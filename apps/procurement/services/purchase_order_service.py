"""
خدمة سير عمل أوامر الشراء
Purchase Order Workflow Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from decimal import Decimal
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.procurement import (
    PurchaseOrder, PurchaseOrderItem, PurchaseOrderApproval,
    Quotation, QuotationItem, PurchaseRequest
)


class PurchaseOrderService(BaseService):
    """
    خدمة سير عمل أوامر الشراء
    Comprehensive purchase order workflow service
    """
    
    def create_purchase_order(self, data):
        """
        إنشاء أمر شراء جديد
        Create new purchase order
        """
        self.check_permission('procurement.add_purchaseorder')
        
        required_fields = ['supplier_id', 'order_items']
        self.validate_required_fields(data, required_fields)
        
        try:
            from core.models.inventory import Supplier
            
            supplier = Supplier.objects.get(id=data['supplier_id'])
            
            with transaction.atomic():
                # Generate PO number
                po_number = self._generate_po_number()
                
                # Create purchase order
                purchase_order = PurchaseOrder.objects.create(
                    po_number=po_number,
                    supplier=supplier,
                    order_date=data.get('order_date', timezone.now().date()),
                    expected_delivery_date=data.get('expected_delivery_date'),
                    payment_terms=data.get('payment_terms', supplier.payment_terms),
                    currency=data.get('currency', supplier.currency or 'SAR'),
                    tax_rate=data.get('tax_rate', 15),  # Default VAT rate
                    discount_percentage=data.get('discount_percentage', 0),
                    shipping_cost=data.get('shipping_cost', 0),
                    notes=data.get('notes', ''),
                    status='draft',
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Add order items
                total_amount = Decimal('0')
                items_count = 0
                
                for item_data in data['order_items']:
                    from core.models.inventory import Product
                    
                    product = Product.objects.get(id=item_data['product_id'])
                    
                    unit_price = Decimal(str(item_data['unit_price']))
                    quantity = Decimal(str(item_data['quantity']))
                    line_total = unit_price * quantity
                    
                    PurchaseOrderItem.objects.create(
                        purchase_order=purchase_order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        line_total=line_total,
                        notes=item_data.get('notes', ''),
                        created_by=self.user,
                        updated_by=self.user
                    )
                    
                    total_amount += line_total
                    items_count += 1
                
                # Calculate totals
                discount_amount = total_amount * (purchase_order.discount_percentage / 100)
                subtotal = total_amount - discount_amount
                tax_amount = subtotal * (purchase_order.tax_rate / 100)
                final_total = subtotal + tax_amount + purchase_order.shipping_cost
                
                # Update purchase order totals
                purchase_order.subtotal = total_amount
                purchase_order.discount_amount = discount_amount
                purchase_order.tax_amount = tax_amount
                purchase_order.total_amount = final_total
                purchase_order.save()
                
                # Start approval workflow if required
                if self._requires_approval(purchase_order):
                    self._initiate_approval_workflow(purchase_order)
                else:
                    purchase_order.status = 'approved'
                    purchase_order.approved_by = self.user
                    purchase_order.approved_at = timezone.now()
                    purchase_order.save()
                
                # Log the action
                self.log_action(
                    action='create',
                    resource='purchase_order',
                    content_object=purchase_order,
                    details={
                        'po_number': po_number,
                        'supplier_id': supplier.id,
                        'items_count': items_count,
                        'total_amount': float(final_total)
                    },
                    message=f'تم إنشاء أمر شراء جديد: {po_number}'
                )
                
                return self.format_response(
                    data={
                        'purchase_order_id': purchase_order.id,
                        'po_number': po_number,
                        'total_amount': final_total,
                        'status': purchase_order.status
                    },
                    message='تم إنشاء أمر الشراء بنجاح'
                )
                
        except Supplier.DoesNotExist:
            return self.format_response(
                success=False,
                message='المورد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_purchase_order', 'purchase_order', data)
    
    def approve_purchase_order(self, po_id, action, comments=None):
        """
        اعتماد أو رفض أمر الشراء
        Approve or reject purchase order
        """
        self.check_permission('procurement.change_purchaseorder')
        
        if action not in ['approve', 'reject']:
            return self.format_response(
                success=False,
                message='الإجراء غير صحيح'
            )
        
        try:
            purchase_order = PurchaseOrder.objects.select_related('supplier').get(id=po_id)
            
            # Check if user can approve this order
            if not self._can_approve_order(purchase_order, self.user):
                return self.format_response(
                    success=False,
                    message='ليس لديك صلاحية اعتماد هذا الأمر'
                )
            
            if purchase_order.status not in ['pending_approval', 'draft']:
                return self.format_response(
                    success=False,
                    message='لا يمكن تعديل أمر شراء غير معلق'
                )
            
            with transaction.atomic():
                # Create approval record
                approval = PurchaseOrderApproval.objects.create(
                    purchase_order=purchase_order,
                    approver=self.user,
                    action=action,
                    comments=comments,
                    approval_date=timezone.now(),
                    created_by=self.user,
                    updated_by=self.user
                )
                
                if action == 'approve':
                    # Check if this is the final approval
                    if self._is_final_approval(purchase_order, approval):
                        purchase_order.status = 'approved'
                        purchase_order.approved_by = self.user
                        purchase_order.approved_at = timezone.now()
                        
                        # Send to supplier
                        self._send_po_to_supplier(purchase_order)
                    else:
                        # Move to next approval level
                        purchase_order.status = 'pending_approval'
                        self._notify_next_approver(purchase_order)
                else:
                    # Reject the order
                    purchase_order.status = 'rejected'
                    purchase_order.rejected_by = self.user
                    purchase_order.rejected_at = timezone.now()
                
                purchase_order.updated_by = self.user
                purchase_order.save()
                
                # Log the action
                self.log_action(
                    action=action,
                    resource='purchase_order_approval',
                    content_object=purchase_order,
                    details={
                        'action': action,
                        'comments': comments,
                        'approver_id': self.user.id
                    },
                    message=f'تم {action} أمر الشراء: {purchase_order.po_number}'
                )
                
                # Send notification
                self._send_approval_notification(purchase_order, action)
                
                return self.format_response(
                    data={
                        'purchase_order_id': purchase_order.id,
                        'new_status': purchase_order.status
                    },
                    message=f'تم {action} أمر الشراء بنجاح'
                )
                
        except PurchaseOrder.DoesNotExist:
            return self.format_response(
                success=False,
                message='أمر الشراء غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'approve_purchase_order', f'po_approval/{po_id}')
    
    def receive_purchase_order(self, po_id, received_items):
        """
        استلام أمر الشراء
        Receive purchase order items
        """
        self.check_permission('procurement.change_purchaseorder')
        
        try:
            purchase_order = PurchaseOrder.objects.select_related('supplier').get(id=po_id)
            
            if purchase_order.status != 'approved':
                return self.format_response(
                    success=False,
                    message='لا يمكن استلام أمر شراء غير معتمد'
                )
            
            with transaction.atomic():
                total_received = 0
                
                for received_item in received_items:
                    po_item = PurchaseOrderItem.objects.get(
                        id=received_item['item_id'],
                        purchase_order=purchase_order
                    )
                    
                    received_quantity = Decimal(str(received_item['received_quantity']))
                    
                    # Update received quantity
                    po_item.received_quantity += received_quantity
                    po_item.save()
                    
                    # Create inventory movement
                    from apps.inventory.services.inventory_service import InventoryService
                    
                    inventory_service = InventoryService(user=self.user)
                    inventory_service.record_stock_movement({
                        'product_id': po_item.product.id,
                        'warehouse_id': received_item['warehouse_id'],
                        'movement_type': 'purchase',
                        'quantity': received_quantity,
                        'unit_cost': po_item.unit_price,
                        'reference_number': purchase_order.po_number,
                        'reference_type': 'purchase_order',
                        'notes': f'استلام من أمر الشراء: {purchase_order.po_number}'
                    })
                    
                    total_received += received_quantity
                
                # Update purchase order status
                all_items_received = all(
                    item.received_quantity >= item.quantity
                    for item in purchase_order.items.all()
                )
                
                if all_items_received:
                    purchase_order.status = 'completed'
                    purchase_order.completed_at = timezone.now()
                else:
                    purchase_order.status = 'partially_received'
                
                purchase_order.updated_by = self.user
                purchase_order.save()
                
                # Log the action
                self.log_action(
                    action='receive',
                    resource='purchase_order_receipt',
                    content_object=purchase_order,
                    details={
                        'items_received': len(received_items),
                        'total_quantity': float(total_received)
                    },
                    message=f'تم استلام أمر الشراء: {purchase_order.po_number}'
                )
                
                return self.format_response(
                    data={
                        'purchase_order_id': purchase_order.id,
                        'new_status': purchase_order.status,
                        'items_received': len(received_items)
                    },
                    message='تم استلام أمر الشراء بنجاح'
                )
                
        except PurchaseOrder.DoesNotExist:
            return self.format_response(
                success=False,
                message='أمر الشراء غير موجود'
            )
        except PurchaseOrderItem.DoesNotExist:
            return self.format_response(
                success=False,
                message='عنصر أمر الشراء غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'receive_purchase_order', f'po_receipt/{po_id}')
    
    def get_purchase_orders(self, filters=None, page=1, page_size=20):
        """
        الحصول على أوامر الشراء
        Get purchase orders with filters
        """
        self.check_permission('procurement.view_purchaseorder')
        
        try:
            queryset = PurchaseOrder.objects.select_related('supplier', 'created_by', 'approved_by')
            
            # Apply filters
            if filters:
                if filters.get('supplier_id'):
                    queryset = queryset.filter(supplier_id=filters['supplier_id'])
                
                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])
                
                if filters.get('start_date'):
                    queryset = queryset.filter(order_date__gte=filters['start_date'])
                
                if filters.get('end_date'):
                    queryset = queryset.filter(order_date__lte=filters['end_date'])
                
                if filters.get('po_number'):
                    queryset = queryset.filter(po_number__icontains=filters['po_number'])
                
                if filters.get('min_amount'):
                    queryset = queryset.filter(total_amount__gte=filters['min_amount'])
                
                if filters.get('max_amount'):
                    queryset = queryset.filter(total_amount__lte=filters['max_amount'])
            
            # Apply user-level filtering if not admin
            if not self.user.is_superuser and not self.user.has_perm('procurement.view_all_orders'):
                # Show only orders created by user or in their department
                queryset = queryset.filter(created_by=self.user)
            
            queryset = queryset.order_by('-order_date', '-created_at')
            
            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)
            
            # Format purchase order data
            purchase_orders = []
            for po in paginated_data['results']:
                purchase_orders.append({
                    'id': po.id,
                    'po_number': po.po_number,
                    'supplier_name': po.supplier.name_ar,
                    'order_date': po.order_date,
                    'expected_delivery_date': po.expected_delivery_date,
                    'total_amount': po.total_amount,
                    'currency': po.currency,
                    'status': po.status,
                    'created_by': po.created_by.get_full_name() if po.created_by else '',
                    'approved_by': po.approved_by.get_full_name() if po.approved_by else '',
                    'approved_at': po.approved_at,
                    'items_count': po.items.count(),
                })
            
            paginated_data['results'] = purchase_orders
            
            return self.format_response(
                data=paginated_data,
                message='تم الحصول على أوامر الشراء بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'get_purchase_orders', 'purchase_orders', filters)
    
    def get_purchase_order_details(self, po_id):
        """
        الحصول على تفاصيل أمر الشراء
        Get purchase order details
        """
        self.check_permission('procurement.view_purchaseorder')
        
        try:
            purchase_order = PurchaseOrder.objects.select_related(
                'supplier', 'created_by', 'approved_by'
            ).prefetch_related(
                'items__product', 'approvals__approver'
            ).get(id=po_id)
            
            # Check object-level permission
            self.check_object_permission('procurement.view_purchaseorder', purchase_order)
            
            # Format purchase order details
            po_details = {
                'id': purchase_order.id,
                'po_number': purchase_order.po_number,
                'supplier': {
                    'id': purchase_order.supplier.id,
                    'name_ar': purchase_order.supplier.name_ar,
                    'name_en': purchase_order.supplier.name_en,
                    'phone': purchase_order.supplier.phone,
                    'email': purchase_order.supplier.email,
                },
                'order_date': purchase_order.order_date,
                'expected_delivery_date': purchase_order.expected_delivery_date,
                'payment_terms': purchase_order.payment_terms,
                'currency': purchase_order.currency,
                'subtotal': purchase_order.subtotal,
                'discount_percentage': purchase_order.discount_percentage,
                'discount_amount': purchase_order.discount_amount,
                'tax_rate': purchase_order.tax_rate,
                'tax_amount': purchase_order.tax_amount,
                'shipping_cost': purchase_order.shipping_cost,
                'total_amount': purchase_order.total_amount,
                'status': purchase_order.status,
                'notes': purchase_order.notes,
                'created_by': purchase_order.created_by.get_full_name() if purchase_order.created_by else '',
                'created_at': purchase_order.created_at,
                'approved_by': purchase_order.approved_by.get_full_name() if purchase_order.approved_by else '',
                'approved_at': purchase_order.approved_at,
            }
            
            # Add items
            items = []
            for item in purchase_order.items.all():
                items.append({
                    'id': item.id,
                    'product_name': item.product.name_ar,
                    'product_code': item.product.code,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'line_total': item.line_total,
                    'received_quantity': item.received_quantity,
                    'remaining_quantity': item.quantity - item.received_quantity,
                    'notes': item.notes,
                })
            
            po_details['items'] = items
            
            # Add approval history
            approvals = []
            for approval in purchase_order.approvals.all():
                approvals.append({
                    'id': approval.id,
                    'approver_name': approval.approver.get_full_name(),
                    'action': approval.action,
                    'comments': approval.comments,
                    'approval_date': approval.approval_date,
                })
            
            po_details['approval_history'] = approvals
            
            return self.format_response(
                data=po_details,
                message='تم الحصول على تفاصيل أمر الشراء بنجاح'
            )
            
        except PurchaseOrder.DoesNotExist:
            return self.format_response(
                success=False,
                message='أمر الشراء غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_purchase_order_details', f'po_details/{po_id}')
    
    def get_procurement_analytics(self, start_date=None, end_date=None):
        """
        الحصول على تحليلات المشتريات
        Get procurement analytics
        """
        self.check_permission('procurement.view_procurement_analytics')
        
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = timezone.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year
            
            queryset = PurchaseOrder.objects.filter(
                order_date__range=[start_date, end_date]
            )
            
            # Calculate analytics
            analytics = queryset.aggregate(
                total_orders=Count('id'),
                total_value=Sum('total_amount'),
                avg_order_value=Avg('total_amount'),
                approved_orders=Count('id', filter=Q(status='approved')),
                completed_orders=Count('id', filter=Q(status='completed')),
                pending_orders=Count('id', filter=Q(status__in=['draft', 'pending_approval'])),
            )
            
            # Calculate percentages
            total = analytics['total_orders'] or 1
            analytics.update({
                'approval_rate': round((analytics['approved_orders'] / total) * 100, 2),
                'completion_rate': round((analytics['completed_orders'] / total) * 100, 2),
            })
            
            # Get supplier breakdown
            supplier_breakdown = queryset.values(
                'supplier__name_ar'
            ).annotate(
                orders_count=Count('id'),
                total_value=Sum('total_amount')
            ).order_by('-total_value')[:10]
            
            # Get monthly trends
            monthly_trends = queryset.extra(
                select={'month': "strftime('%%Y-%%m', order_date)"}
            ).values('month').annotate(
                orders_count=Count('id'),
                total_value=Sum('total_amount')
            ).order_by('month')
            
            analytics.update({
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                },
                'supplier_breakdown': list(supplier_breakdown),
                'monthly_trends': list(monthly_trends),
            })
            
            return self.format_response(
                data=analytics,
                message='تم الحصول على تحليلات المشتريات بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'get_procurement_analytics', 'procurement_analytics')
    
    def _generate_po_number(self):
        """إنشاء رقم أمر الشراء"""
        from django.utils import timezone
        
        today = timezone.now().date()
        year = today.year
        month = today.month
        
        # Get the last PO number for this month
        last_po = PurchaseOrder.objects.filter(
            order_date__year=year,
            order_date__month=month
        ).order_by('-id').first()
        
        if last_po and last_po.po_number:
            # Extract sequence number from last PO
            try:
                last_sequence = int(last_po.po_number.split('-')[-1])
                sequence = last_sequence + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        
        return f"PO-{year}{month:02d}-{sequence:04d}"
    
    def _requires_approval(self, purchase_order):
        """فحص إذا كان أمر الشراء يحتاج اعتماد"""
        # Simple approval logic - orders above certain amount need approval
        approval_threshold = Decimal('10000')  # 10,000 SAR
        return purchase_order.total_amount >= approval_threshold
    
    def _initiate_approval_workflow(self, purchase_order):
        """بدء سير عمل الاعتماد"""
        purchase_order.status = 'pending_approval'
        purchase_order.save()
        
        # Notify approvers
        self._notify_approvers(purchase_order)
    
    def _can_approve_order(self, purchase_order, user):
        """فحص إمكانية اعتماد الأمر"""
        # Check if user has approval permission
        if user.has_perm('procurement.approve_purchaseorder'):
            return True
        
        # Check if user is department manager
        # This would be implemented based on organizational structure
        return False
    
    def _is_final_approval(self, purchase_order, approval):
        """فحص إذا كان هذا الاعتماد الأخير"""
        # For now, assume single-level approval
        return True
    
    def _send_po_to_supplier(self, purchase_order):
        """إرسال أمر الشراء للمورد"""
        try:
            self.send_notification(
                recipient=purchase_order.supplier,  # This would need email handling
                template_name='purchase_order_sent',
                context={'purchase_order': purchase_order},
                channels=['email']
            )
        except Exception as e:
            self.logger.warning(f"Failed to send PO to supplier: {e}")
    
    def _notify_approvers(self, purchase_order):
        """إشعار المعتمدين"""
        # This would notify users with approval permissions
        pass
    
    def _notify_next_approver(self, purchase_order):
        """إشعار المعتمد التالي"""
        # This would implement multi-level approval notifications
        pass
    
    def _send_approval_notification(self, purchase_order, action):
        """إرسال إشعار الاعتماد أو الرفض"""
        try:
            template_name = f'purchase_order_{action}'
            recipient = purchase_order.created_by
            
            self.send_notification(
                recipient=recipient,
                template_name=template_name,
                context={'purchase_order': purchase_order},
                channels=['in_app', 'email']
            )
        except Exception as e:
            self.logger.warning(f"Failed to send approval notification: {e}")