"""
خدمة إدارة المخزون الشاملة
Comprehensive Inventory Management Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from decimal import Decimal
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.inventory import (
    Product, Warehouse, InventoryMovement, StockLevel,
    InventoryAdjustment, StockAlert, InventoryCount
)


class InventoryService(BaseService):
    """
    خدمة إدارة المخزون الشاملة
    Comprehensive inventory management with stock tracking
    """

    def record_stock_movement(self, data):
        """
        تسجيل حركة مخزون
        Record inventory movement
        """
        self.check_permission('inventory.add_inventorymovement')

        required_fields = ['product_id', 'warehouse_id', 'movement_type', 'quantity']
        self.validate_required_fields(data, required_fields)

        try:
            product = Product.objects.get(id=data['product_id'])
            warehouse = Warehouse.objects.get(id=data['warehouse_id'])

            with transaction.atomic():
                # Create inventory movement
                movement = InventoryMovement.objects.create(
                    product=product,
                    warehouse=warehouse,
                    movement_type=data['movement_type'],
                    quantity=data['quantity'],
                    unit_cost=data.get('unit_cost', 0),
                    reference_number=data.get('reference_number'),
                    reference_type=data.get('reference_type'),
                    notes=data.get('notes'),
                    movement_date=data.get('movement_date', timezone.now().date()),
                    created_by=self.user,
                    updated_by=self.user
                )

                # Update stock level
                self._update_stock_level(product, warehouse, data['movement_type'], data['quantity'])

                # Check for stock alerts
                self._check_stock_alerts(product, warehouse)

                # Log the action
                self.log_action(
                    action='create',
                    resource='inventory_movement',
                    content_object=movement,
                    new_values=data,
                    message=f'تم تسجيل حركة مخزون: {product.name_ar} - {data["movement_type"]}'
                )

                return self.format_response(
                    data={'movement_id': movement.id},
                    message='تم تسجيل حركة المخزون بنجاح'
                )

        except Product.DoesNotExist:
            return self.format_response(
                success=False,
                message='المنتج غير موجود'
            )
        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'record_stock_movement', 'inventory_movement', data)

    def get_stock_levels(self, warehouse_id=None, product_id=None, low_stock_only=False):
        """
        الحصول على مستويات المخزون
        Get current stock levels
        """
        self.check_permission('inventory.view_stocklevel')

        try:
            queryset = StockLevel.objects.select_related('product', 'warehouse')

            if warehouse_id:
                queryset = queryset.filter(warehouse_id=warehouse_id)

            if product_id:
                queryset = queryset.filter(product_id=product_id)

            if low_stock_only:
                queryset = queryset.filter(
                    Q(current_stock__lte=F('product__min_stock_level')) |
                    Q(current_stock__lte=F('reorder_level'))
                )

            stock_levels = []
            for stock in queryset:
                stock_levels.append({
                    'product_id': stock.product.id,
                    'product_name': stock.product.name_ar,
                    'product_code': stock.product.code,
                    'warehouse_id': stock.warehouse.id,
                    'warehouse_name': stock.warehouse.name_ar,
                    'current_stock': stock.current_stock,
                    'reserved_stock': stock.reserved_stock,
                    'available_stock': stock.available_stock,
                    'reorder_level': stock.reorder_level,
                    'max_stock_level': stock.max_stock_level,
                    'unit_cost': stock.average_cost,
                    'total_value': stock.current_stock * stock.average_cost,
                    'last_updated': stock.updated_at,
                    'is_low_stock': stock.current_stock <= (stock.reorder_level or stock.product.min_stock_level or 0),
                })

            return self.format_response(
                data=stock_levels,
                message='تم الحصول على مستويات المخزون بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_stock_levels', 'stock_levels')

    def perform_stock_adjustment(self, data):
        """
        تنفيذ تسوية مخزون
        Perform stock adjustment
        """
        self.check_permission('inventory.add_inventoryadjustment')

        required_fields = ['product_id', 'warehouse_id', 'adjustment_type', 'quantity', 'reason']
        self.validate_required_fields(data, required_fields)

        try:
            product = Product.objects.get(id=data['product_id'])
            warehouse = Warehouse.objects.get(id=data['warehouse_id'])

            # Get current stock level
            stock_level = StockLevel.objects.filter(
                product=product,
                warehouse=warehouse
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if not stock_level:
                return self.format_response(
                    success=False,
                    message='لا يوجد مخزون لهذا المنتج في هذا المخزن'
                )

            with transaction.atomic():
                # Create adjustment record
                adjustment = InventoryAdjustment.objects.create(
                    product=product,
                    warehouse=warehouse,
                    adjustment_type=data['adjustment_type'],
                    quantity=data['quantity'],
                    reason=data['reason'],
                    reference_number=data.get('reference_number'),
                    notes=data.get('notes'),
                    old_quantity=stock_level.current_stock,
                    created_by=self.user,
                    updated_by=self.user
                )

                # Calculate new quantity
                if data['adjustment_type'] == 'increase':
                    new_quantity = stock_level.current_stock + data['quantity']
                    movement_type = 'adjustment_in'
                else:
                    new_quantity = stock_level.current_stock - data['quantity']
                    movement_type = 'adjustment_out'

                adjustment.new_quantity = new_quantity
                adjustment.save()

                # Create inventory movement
                self.record_stock_movement({
                    'product_id': product.id,
                    'warehouse_id': warehouse.id,
                    'movement_type': movement_type,
                    'quantity': data['quantity'],
                    'reference_number': adjustment.reference_number,
                    'reference_type': 'adjustment',
                    'notes': f"تسوية مخزون: {data['reason']}"
                })

                # Log the action
                self.log_action(
                    action='create',
                    resource='inventory_adjustment',
                    content_object=adjustment,
                    new_values=data,
                    message=f'تم تنفيذ تسوية مخزون: {product.name_ar}'
                )

                return self.format_response(
                    data={
                        'adjustment_id': adjustment.id,
                        'old_quantity': adjustment.old_quantity,
                        'new_quantity': adjustment.new_quantity
                    },
                    message='تم تنفيذ تسوية المخزون بنجاح'
                )

        except Product.DoesNotExist:
            return self.format_response(
                success=False,
                message='المنتج غير موجود'
            )
        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'perform_stock_adjustment', 'inventory_adjustment', data)

    def start_inventory_count(self, warehouse_id, data):
        """
        بدء جرد المخزون
        Start inventory count process
        """
        self.check_permission('inventory.add_inventorycount')

        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)

            # Check if there's an active count for this warehouse
            active_count = InventoryCount.objects.filter(
                warehouse=warehouse,
                status='in_progress'
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

            if active_count:
                return self.format_response(
                    success=False,
                    message='يوجد جرد نشط لهذا المخزن بالفعل'
                )

            with transaction.atomic():
                # Create inventory count
                count = InventoryCount.objects.create(
                    warehouse=warehouse,
                    count_date=data.get('count_date', timezone.now().date()),
                    count_type=data.get('count_type', 'full'),
                    description=data.get('description', ''),
                    status='in_progress',
                    started_by=self.user,
                    created_by=self.user,
                    updated_by=self.user
                )

                # Create count items for all products in warehouse
                stock_levels = StockLevel.objects.filter(
                    warehouse=warehouse,
                    current_stock__gt=0
                ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('product')

                count_items_created = 0
                for stock in stock_levels:
                    from core.models.inventory import InventoryCountItem

                    InventoryCountItem.objects.create(
                        inventory_count=count,
                        product=stock.product,
                        system_quantity=stock.current_stock,
                        counted_quantity=0,
                        variance=0,
                        status='pending',
                        created_by=self.user,
                        updated_by=self.user
                    )
                    count_items_created += 1

                # Log the action
                self.log_action(
                    action='create',
                    resource='inventory_count',
                    content_object=count,
                    details={
                        'warehouse_id': warehouse_id,
                        'count_items': count_items_created
                    },
                    message=f'تم بدء جرد المخزون: {warehouse.name_ar}'
                )

                return self.format_response(
                    data={
                        'count_id': count.id,
                        'items_count': count_items_created
                    },
                    message=f'تم بدء جرد المخزون مع {count_items_created} عنصر'
                )

        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'start_inventory_count', f'inventory_count/{warehouse_id}', data)

    def get_inventory_valuation(self, warehouse_id=None, valuation_date=None):
        """
        الحصول على تقييم المخزون
        Get inventory valuation
        """
        self.check_permission('inventory.view_inventory_valuation')

        try:
            valuation_date = valuation_date or timezone.now().date()

            queryset = StockLevel.objects.select_related('product', 'warehouse')

            if warehouse_id:
                queryset = queryset.filter(warehouse_id=warehouse_id)

            # Calculate valuation
            total_value = Decimal('0')
            total_quantity = 0
            categories_summary = {}

            valuation_items = []
            for stock in queryset:
                item_value = stock.current_stock * stock.average_cost
                total_value += item_value
                total_quantity += stock.current_stock

                # Category summary
                category = stock.product.category.name_ar if stock.product.category else 'غير مصنف'
                if category not in categories_summary:
                    categories_summary[category] = {
                        'quantity': 0,
                        'value': Decimal('0'),
                        'items_count': 0
                    }

                categories_summary[category]['quantity'] += stock.current_stock
                categories_summary[category]['value'] += item_value
                categories_summary[category]['items_count'] += 1

                valuation_items.append({
                    'product_id': stock.product.id,
                    'product_name': stock.product.name_ar,
                    'product_code': stock.product.code,
                    'category': category,
                    'warehouse_name': stock.warehouse.name_ar,
                    'quantity': stock.current_stock,
                    'unit_cost': stock.average_cost,
                    'total_value': item_value,
                })

            valuation_summary = {
                'valuation_date': valuation_date,
                'total_items': len(valuation_items),
                'total_quantity': total_quantity,
                'total_value': total_value,
                'categories_summary': categories_summary,
                'items': valuation_items
            }

            return self.format_response(
                data=valuation_summary,
                message='تم حساب تقييم المخزون بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_inventory_valuation', 'inventory_valuation')

    def get_stock_alerts(self, warehouse_id=None, alert_type=None):
        """
        الحصول على تنبيهات المخزون
        Get stock alerts
        """
        self.check_permission('inventory.view_stockalert')

        try:
            queryset = StockAlert.objects.select_related('product', 'warehouse')

            if warehouse_id:
                queryset = queryset.filter(warehouse_id=warehouse_id)

            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)

            # Also get current low stock items
            low_stock_items = StockLevel.objects.filter(
                current_stock__lte=F('reorder_level').prefetch_related()  # TODO: Add appropriate prefetch_related fields
            ).select_related('product', 'warehouse')

            if warehouse_id:
                low_stock_items = low_stock_items.filter(warehouse_id=warehouse_id)

            alerts = []

            # Add existing alerts
            for alert in queryset.filter(is_resolved=False):
                alerts.append({
                    'id': alert.id,
                    'type': 'alert',
                    'alert_type': alert.alert_type,
                    'product_name': alert.product.name_ar,
                    'warehouse_name': alert.warehouse.name_ar,
                    'message': alert.message,
                    'severity': alert.severity,
                    'created_at': alert.created_at,
                })

            # Add low stock alerts
            for stock in low_stock_items:
                alerts.append({
                    'type': 'low_stock',
                    'alert_type': 'low_stock',
                    'product_name': stock.product.name_ar,
                    'warehouse_name': stock.warehouse.name_ar,
                    'current_stock': stock.current_stock,
                    'reorder_level': stock.reorder_level,
                    'message': f'المخزون منخفض: {stock.current_stock} متبقي',
                    'severity': 'medium' if stock.current_stock > 0 else 'high',
                })

            return self.format_response(
                data=alerts,
                message='تم الحصول على تنبيهات المخزون بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_stock_alerts', 'stock_alerts')

    def generate_inventory_report(self, report_type, filters=None):
        """
        إنشاء تقرير المخزون
        Generate inventory report
        """
        self.check_permission('inventory.view_inventory_reports')

        try:
            if report_type == 'stock_summary':
                return self._generate_stock_summary_report(filters)
            elif report_type == 'movement_history':
                return self._generate_movement_history_report(filters)
            elif report_type == 'valuation':
                return self._generate_valuation_report(filters)
            elif report_type == 'low_stock':
                return self._generate_low_stock_report(filters)
            else:
                return self.format_response(
                    success=False,
                    message='نوع التقرير غير مدعوم'
                )

        except Exception as e:
            return self.handle_exception(e, 'generate_inventory_report', f'report/{report_type}')

    def _update_stock_level(self, product, warehouse, movement_type, quantity):
        """تحديث مستوى المخزون"""
        stock_level, created = StockLevel.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={
                'current_stock': 0,
                'reserved_stock': 0,
                'reorder_level': product.min_stock_level or 0,
                'max_stock_level': product.max_stock_level or 0,
                'average_cost': product.cost_price or 0,
                'created_by': self.user,
                'updated_by': self.user
            }
        )

        # Update stock based on movement type
        if movement_type in ['receipt', 'purchase', 'transfer_in', 'adjustment_in', 'return_in']:
            stock_level.current_stock += quantity
        elif movement_type in ['issue', 'sale', 'transfer_out', 'adjustment_out', 'return_out']:
            stock_level.current_stock -= quantity

        # Ensure stock doesn't go negative
        if stock_level.current_stock < 0:
            stock_level.current_stock = 0

        # Update available stock
        stock_level.available_stock = stock_level.current_stock - stock_level.reserved_stock

        # Update average cost for incoming movements
        if movement_type in ['receipt', 'purchase'] and hasattr(self, '_movement_unit_cost'):
            total_value = (stock_level.current_stock - quantity) * stock_level.average_cost
            total_value += quantity * self._movement_unit_cost
            if stock_level.current_stock > 0:
                stock_level.average_cost = total_value / stock_level.current_stock

        stock_level.updated_by = self.user
        stock_level.save()

    def _check_stock_alerts(self, product, warehouse):
        """فحص تنبيهات المخزون"""
        stock_level = StockLevel.objects.filter(
            product=product,
            warehouse=warehouse
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.first()

        if not stock_level:
            return

        # Check for low stock
        if stock_level.current_stock <= (stock_level.reorder_level or 0):
            StockAlert.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                alert_type='low_stock',
                defaults={
                    'message': f'المخزون منخفض: {stock_level.current_stock} متبقي',
                    'severity': 'medium' if stock_level.current_stock > 0 else 'high',
                    'created_by': self.user,
                    'updated_by': self.user
                }
            )

        # Check for out of stock
        if stock_level.current_stock <= 0:
            StockAlert.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                alert_type='out_of_stock',
                defaults={
                    'message': f'نفد المخزون: {product.name_ar}',
                    'severity': 'high',
                    'created_by': self.user,
                    'updated_by': self.user
                }
            )

    def _generate_stock_summary_report(self, filters):
        """إنشاء تقرير ملخص المخزون"""
        queryset = StockLevel.objects.select_related('product', 'warehouse')

        if filters:
            if filters.get('warehouse_id'):
                queryset = queryset.filter(warehouse_id=filters['warehouse_id'])
            if filters.get('category_id'):
                queryset = queryset.filter(product__category_id=filters['category_id'])

        summary_data = []
        for stock in queryset:
            summary_data.append({
                'product_name': stock.product.name_ar,
                'warehouse_name': stock.warehouse.name_ar,
                'current_stock': stock.current_stock,
                'available_stock': stock.available_stock,
                'unit_cost': stock.average_cost,
                'total_value': stock.current_stock * stock.average_cost,
            })

        return self.format_response(
            data=summary_data,
            message='تم إنشاء تقرير ملخص المخزون بنجاح'
        )

    def _generate_movement_history_report(self, filters):
        """إنشاء تقرير تاريخ الحركات"""
        queryset = InventoryMovement.objects.select_related('product', 'warehouse')

        if filters:
            if filters.get('start_date'):
                queryset = queryset.filter(movement_date__gte=filters['start_date'])
            if filters.get('end_date'):
                queryset = queryset.filter(movement_date__lte=filters['end_date'])
            if filters.get('product_id'):
                queryset = queryset.filter(product_id=filters['product_id'])
            if filters.get('warehouse_id'):
                queryset = queryset.filter(warehouse_id=filters['warehouse_id'])

        movements_data = []
        for movement in queryset.order_by('-movement_date'):
            movements_data.append({
                'date': movement.movement_date,
                'product_name': movement.product.name_ar,
                'warehouse_name': movement.warehouse.name_ar,
                'movement_type': movement.movement_type,
                'quantity': movement.quantity,
                'unit_cost': movement.unit_cost,
                'reference_number': movement.reference_number,
                'notes': movement.notes,
            })

        return self.format_response(
            data=movements_data,
            message='تم إنشاء تقرير تاريخ الحركات بنجاح'
        )

    def _generate_valuation_report(self, filters):
        """إنشاء تقرير التقييم"""
        return self.get_inventory_valuation(
            warehouse_id=filters.get('warehouse_id') if filters else None
        )

    def _generate_low_stock_report(self, filters):
        """إنشاء تقرير المخزون المنخفض"""
        return self.get_stock_levels(
            warehouse_id=filters.get('warehouse_id') if filters else None,
            low_stock_only=True
        )
