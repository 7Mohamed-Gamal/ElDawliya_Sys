"""
خدمة إدارة الموردين والتقييمات
Supplier Management and Evaluation Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Q
from decimal import Decimal
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.inventory import Supplier


class SupplierService(BaseService):
    """
    خدمة إدارة الموردين والتقييمات
    Comprehensive supplier management with evaluation system
    """

    def create_supplier(self, data):
        """
        إنشاء مورد جديد
        Create new supplier
        """
        self.check_permission('inventory.add_supplier')

        required_fields = ['name_ar', 'name_en', 'supplier_type']
        self.validate_required_fields(data, required_fields)

        try:
            with transaction.atomic():
                # Create supplier
                supplier_data = self.clean_data(data, [
                    'name_ar', 'name_en', 'supplier_type', 'tax_number', 'commercial_register',
                    'address_ar', 'address_en', 'city', 'country', 'postal_code',
                    'phone', 'fax', 'email', 'website', 'contact_person',
                    'payment_terms', 'credit_limit', 'currency', 'is_active'
                ])

                supplier = Supplier.objects.create(
                    **supplier_data,
                    created_by=self.user,
                    updated_by=self.user
                )

                # Note: Supplier contacts and products functionality 
                # would require additional models to be implemented

                # Log the action
                self.log_action(
                    action='create',
                    resource='supplier',
                    content_object=supplier,
                    new_values=supplier_data,
                    message=f'تم إنشاء مورد جديد: {supplier.name_ar}'
                )

                return self.format_response(
                    data={
                        'supplier_id': supplier.id,
                        'name': supplier.name_ar
                    },
                    message='تم إنشاء المورد بنجاح'
                )

        except Exception as e:
            return self.handle_exception(e, 'create_supplier', 'supplier', data)

    def update_supplier(self, supplier_id, data):
        """
        تحديث بيانات المورد
        Update supplier information
        """
        self.check_permission('inventory.change_supplier')

        try:
            supplier = Supplier.objects.get(id=supplier_id)

            # Check object-level permission
            self.check_object_permission('inventory.change_supplier', supplier)

            # Get old values for audit
            old_values, new_values = self.get_model_changes(supplier, data)

            # Update supplier data
            allowed_fields = [
                'name_ar', 'name_en', 'supplier_type', 'tax_number', 'commercial_register',
                'address_ar', 'address_en', 'city', 'country', 'postal_code',
                'phone', 'fax', 'email', 'website', 'contact_person',
                'payment_terms', 'credit_limit', 'currency', 'is_active'
            ]

            for field, value in data.items():
                if field in allowed_fields and hasattr(supplier, field):
                    setattr(supplier, field, value)

            supplier.updated_by = self.user
            supplier.save()

            # Log the action
            self.log_action(
                action='update',
                resource='supplier',
                content_object=supplier,
                old_values=old_values,
                new_values=new_values,
                message=f'تم تحديث بيانات المورد: {supplier.name_ar}'
            )

            # Invalidate cache
            self.invalidate_cache(f'supplier_{supplier_id}_*')

            return self.format_response(
                data={
                    'supplier_id': supplier.id,
                    'updated_fields': list(new_values.keys())
                },
                message='تم تحديث بيانات المورد بنجاح'
            )

        except Supplier.DoesNotExist:
            return self.format_response(
                success=False,
                message='المورد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_supplier', f'supplier/{supplier_id}', data)

    def get_supplier(self, supplier_id, include_relations=True):
        """
        الحصول على بيانات المورد
        Get supplier details
        """
        self.check_permission('inventory.view_supplier')

        try:
            cache_key = self.cache_key('supplier', supplier_id, 'details', include_relations)

            def get_supplier_data():
                """get_supplier_data function"""
                queryset = Supplier.objects

                if include_relations:
                    queryset = queryset.prefetch_related(
                        'contacts', 'products', 'evaluations', 'purchase_orders'
                    )

                supplier = queryset.get(id=supplier_id)

                # Check object-level permission
                self.check_object_permission('inventory.view_supplier', supplier)

                supplier_data = {
                    'id': supplier.id,
                    'name_ar': supplier.name_ar,
                    'name_en': supplier.name_en,
                    'supplier_type': supplier.supplier_type,
                    'tax_number': supplier.tax_number,
                    'commercial_register': supplier.commercial_register,
                    'address_ar': supplier.address_ar,
                    'city': supplier.city,
                    'country': supplier.country,
                    'phone': supplier.phone,
                    'email': supplier.email,
                    'website': supplier.website,
                    'contact_person': supplier.contact_person,
                    'payment_terms': supplier.payment_terms,
                    'credit_limit': supplier.credit_limit,
                    'currency': supplier.currency,
                    'is_active': supplier.is_active,
                    'created_at': supplier.created_at,
                }

                if include_relations:
                    # Note: Contacts and evaluations would require additional models
                    supplier_data['contacts'] = []
                    supplier_data['evaluation_summary'] = {
                        'average_rating': 0,
                        'evaluations_count': 0,
                        'last_evaluation': None
                    }

                return supplier_data

            supplier_data = self.get_from_cache(cache_key)
            if not supplier_data:
                supplier_data = get_supplier_data()
                self.set_cache(cache_key, supplier_data, 300)  # 5 minutes

            return self.format_response(
                data=supplier_data,
                message='تم الحصول على بيانات المورد بنجاح'
            )

        except Supplier.DoesNotExist:
            return self.format_response(
                success=False,
                message='المورد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_supplier', f'supplier/{supplier_id}')

    def search_suppliers(self, filters=None, page=1, page_size=20):
        """
        البحث في الموردين
        Search suppliers with filters
        """
        self.check_permission('inventory.view_supplier')

        try:
            queryset = Supplier.objects.all()

            # Apply filters
            if filters:
                if filters.get('supplier_type'):
                    queryset = queryset.filter(supplier_type=filters['supplier_type'])

                if filters.get('is_active') is not None:
                    queryset = queryset.filter(is_active=filters['is_active'])

                if filters.get('search_term'):
                    term = filters['search_term']
                    queryset = queryset.filter(
                        Q(name_ar__icontains=term) |
                        Q(name_en__icontains=term) |
                        Q(tax_number__icontains=term) |
                        Q(email__icontains=term) |
                        Q(phone__icontains=term)
                    )

                if filters.get('city'):
                    queryset = queryset.filter(city__icontains=filters['city'])

                if filters.get('country'):
                    queryset = queryset.filter(country__icontains=filters['country'])

                # Note: Rating filter would require SupplierEvaluation model

            # Order by name
            queryset = queryset.order_by('name_ar')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format supplier data
            suppliers = []
            for supplier in paginated_data['results']:
                suppliers.append({
                    'id': supplier.id,
                    'name_ar': supplier.name,
                    'name_en': supplier.name,
                    'supplier_type': supplier.supplier_type,
                    'city': supplier.city,
                    'country': supplier.country,
                    'phone': supplier.phone,
                    'email': supplier.email,
                    'payment_terms': supplier.payment_terms,
                    'average_rating': supplier.rating,
                    'is_active': supplier.is_active,
                })

            paginated_data['results'] = suppliers

            return self.format_response(
                data=paginated_data,
                message='تم البحث في الموردين بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'search_suppliers', 'suppliers', filters)

    def evaluate_supplier(self, supplier_id, evaluation_data):
        """
        تقييم المورد
        Evaluate supplier performance
        Note: This would require SupplierEvaluation model to be implemented
        """
        return self.format_response(
            success=False,
            message='وظيفة تقييم الموردين تتطلب نموذج SupplierEvaluation'
        )

    def get_supplier_evaluations(self, supplier_id, page=1, page_size=20):
        """
        الحصول على تقييمات المورد
        Get supplier evaluations
        Note: This would require SupplierEvaluation model to be implemented
        """
        return self.format_response(
            success=False,
            message='وظيفة تقييمات الموردين تتطلب نموذج SupplierEvaluation'
        )

    def get_supplier_performance_report(self, supplier_id, start_date=None, end_date=None):
        """
        تقرير أداء المورد
        Get supplier performance report
        """
        self.check_permission('inventory.view_supplier_reports')

        try:
            supplier = Supplier.objects.get(id=supplier_id)

            # Set default date range if not provided
            if not end_date:
                end_date = timezone.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get purchase orders statistics
            from core.models.procurement import PurchaseOrder

            purchase_orders = PurchaseOrder.objects.filter(
                supplier=supplier,
                order_date__range=[start_date, end_date]
            )

            po_stats = purchase_orders.aggregate(
                total_orders=Count('id'),
                total_value=Sum('total_amount'),
                avg_order_value=Avg('total_amount'),
                on_time_deliveries=Count('id', filter=Q(delivery_status='on_time')),
                late_deliveries=Count('id', filter=Q(delivery_status='late')),
            )

            # Calculate delivery performance
            total_deliveries = po_stats['on_time_deliveries'] + po_stats['late_deliveries']
            on_time_percentage = (
                (po_stats['on_time_deliveries'] / total_deliveries * 100)
                if total_deliveries > 0 else 0
            )

            # Note: Evaluation statistics would require SupplierEvaluation model
            eval_stats = {
                'avg_overall_rating': 0,
                'avg_quality_rating': 0,
                'avg_delivery_rating': 0,
                'avg_service_rating': 0,
                'avg_price_rating': 0,
                'evaluations_count': 0,
            }

            # Note: Top products would require SupplierProduct model
            products_list = []

            performance_report = {
                'supplier': {
                    'id': supplier.id,
                    'name': supplier.name_ar,
                    'supplier_type': supplier.supplier_type,
                },
                'report_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                },
                'purchase_statistics': {
                    'total_orders': po_stats['total_orders'] or 0,
                    'total_value': po_stats['total_value'] or 0,
                    'average_order_value': po_stats['avg_order_value'] or 0,
                    'on_time_delivery_percentage': round(on_time_percentage, 2),
                },
                'evaluation_statistics': {
                    'evaluations_count': eval_stats['evaluations_count'] or 0,
                    'average_overall_rating': round(eval_stats['avg_overall_rating'] or 0, 2),
                    'average_quality_rating': round(eval_stats['avg_quality_rating'] or 0, 2),
                    'average_delivery_rating': round(eval_stats['avg_delivery_rating'] or 0, 2),
                    'average_service_rating': round(eval_stats['avg_service_rating'] or 0, 2),
                    'average_price_rating': round(eval_stats['avg_price_rating'] or 0, 2),
                },
                'top_products': products_list,
            }

            return self.format_response(
                data=performance_report,
                message='تم إنشاء تقرير أداء المورد بنجاح'
            )

        except Supplier.DoesNotExist:
            return self.format_response(
                success=False,
                message='المورد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_supplier_performance_report', f'supplier_performance/{supplier_id}')

    def get_suppliers_comparison(self, supplier_ids, criteria=None):
        """
        مقارنة الموردين
        Compare suppliers
        Note: This would require SupplierEvaluation and PurchaseOrder models to be implemented
        """
        return self.format_response(
            success=False,
            message='وظيفة مقارنة الموردين تتطلب نماذج إضافية'
        )
