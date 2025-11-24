"""
خدمة إدارة المخازن والحركات
Warehouse Management Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from decimal import Decimal
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.inventory import Warehouse, StockLevel, StockMovement


class WarehouseService(BaseService):
    """
    خدمة إدارة المخازن والحركات
    Comprehensive warehouse management service
    """

    def create_warehouse(self, data):
        """
        إنشاء مخزن جديد
        Create new warehouse
        """
        self.check_permission('inventory.add_warehouse')

        required_fields = ['name_ar', 'name_en', 'warehouse_type']
        self.validate_required_fields(data, required_fields)

        try:
            with transaction.atomic():
                # Create warehouse
                warehouse_data = self.clean_data(data, [
                    'name_ar', 'name_en', 'warehouse_type', 'code', 'description_ar',
                    'description_en', 'address_ar', 'address_en', 'city', 'country',
                    'postal_code', 'phone', 'email', 'manager_name', 'capacity',
                    'is_active', 'allow_negative_stock', 'auto_reorder'
                ])

                warehouse = Warehouse.objects.create(
                    **warehouse_data,
                    created_by=self.user,
                    updated_by=self.user
                )

                # Note: Warehouse zones functionality would require WarehouseZone model

                # Log the action
                self.log_action(
                    action='create',
                    resource='warehouse',
                    content_object=warehouse,
                    new_values=warehouse_data,
                    message=f'تم إنشاء مخزن جديد: {warehouse.name_ar}'
                )

                return self.format_response(
                    data={
                        'warehouse_id': warehouse.id,
                        'name': warehouse.name_ar,
                        'code': warehouse.code
                    },
                    message='تم إنشاء المخزن بنجاح'
                )

        except Exception as e:
            return self.handle_exception(e, 'create_warehouse', 'warehouse', data)

    def update_warehouse(self, warehouse_id, data):
        """
        تحديث بيانات المخزن
        Update warehouse information
        """
        self.check_permission('inventory.change_warehouse')

        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)

            # Check object-level permission
            self.check_object_permission('inventory.change_warehouse', warehouse)

            # Get old values for audit
            old_values, new_values = self.get_model_changes(warehouse, data)

            # Update warehouse data
            allowed_fields = [
                'name_ar', 'name_en', 'warehouse_type', 'code', 'description_ar',
                'description_en', 'address_ar', 'address_en', 'city', 'country',
                'postal_code', 'phone', 'email', 'manager_name', 'capacity',
                'is_active', 'allow_negative_stock', 'auto_reorder'
            ]

            for field, value in data.items():
                if field in allowed_fields and hasattr(warehouse, field):
                    setattr(warehouse, field, value)

            warehouse.updated_by = self.user
            warehouse.save()

            # Log the action
            self.log_action(
                action='update',
                resource='warehouse',
                content_object=warehouse,
                old_values=old_values,
                new_values=new_values,
                message=f'تم تحديث بيانات المخزن: {warehouse.name_ar}'
            )

            # Invalidate cache
            self.invalidate_cache(f'warehouse_{warehouse_id}_*')

            return self.format_response(
                data={
                    'warehouse_id': warehouse.id,
                    'updated_fields': list(new_values.keys())
                },
                message='تم تحديث بيانات المخزن بنجاح'
            )

        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_warehouse', f'warehouse/{warehouse_id}', data)

    def get_warehouse(self, warehouse_id, include_stock=True):
        """
        الحصول على بيانات المخزن
        Get warehouse details
        """
        self.check_permission('inventory.view_warehouse')

        try:
            cache_key = self.cache_key('warehouse', warehouse_id, 'details', include_stock)

            def get_warehouse_data():
                """get_warehouse_data function"""
                queryset = Warehouse.objects

                if include_stock:
                    queryset = queryset.prefetch_related('stock_levels', 'zones')

                warehouse = queryset.get(id=warehouse_id)

                # Check object-level permission
                self.check_object_permission('inventory.view_warehouse', warehouse)

                warehouse_data = {
                    'id': warehouse.id,
                    'name_ar': warehouse.name_ar,
                    'name_en': warehouse.name_en,
                    'warehouse_type': warehouse.warehouse_type,
                    'code': warehouse.code,
                    'description_ar': warehouse.description_ar,
                    'address_ar': warehouse.address_ar,
                    'city': warehouse.city,
                    'country': warehouse.country,
                    'phone': warehouse.phone,
                    'email': warehouse.email,
                    'manager_name': warehouse.manager_name,
                    'capacity': warehouse.capacity,
                    'is_active': warehouse.is_active,
                    'allow_negative_stock': warehouse.allow_negative_stock,
                    'auto_reorder': warehouse.auto_reorder,
                    'created_at': warehouse.created_at,
                }

                if include_stock:
                    # Add stock summary
                    stock_levels = warehouse.stock_levels.all()
                    total_products = stock_levels.count()
                    total_value = sum(
                        stock.current_stock * stock.average_cost
                        for stock in stock_levels
                    )

                    warehouse_data['stock_summary'] = {
                        'total_products': total_products,
                        'total_stock_value': total_value,
                        'low_stock_items': stock_levels.filter(
                            current_stock__lte=F('reorder_level')
                        ).count(),
                    }

                    # Add zones
                    zones = []
                    for zone in warehouse.zones.all():
                        zones.append({
                            'id': zone.id,
                            'name': zone.name,
                            'zone_type': zone.zone_type,
                            'capacity': zone.capacity,
                            'is_active': zone.is_active,
                        })
                    warehouse_data['zones'] = zones

                return warehouse_data

            warehouse_data = self.get_from_cache(cache_key)
            if not warehouse_data:
                warehouse_data = get_warehouse_data()
                self.set_cache(cache_key, warehouse_data, 300)  # 5 minutes

            return self.format_response(
                data=warehouse_data,
                message='تم الحصول على بيانات المخزن بنجاح'
            )

        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_warehouse', f'warehouse/{warehouse_id}')

    def get_warehouses_list(self, filters=None):
        """
        الحصول على قائمة المخازن
        Get warehouses list
        """
        self.check_permission('inventory.view_warehouse')

        try:
            queryset = Warehouse.objects.all()

            # Apply filters
            if filters:
                if filters.get('warehouse_type'):
                    queryset = queryset.filter(warehouse_type=filters['warehouse_type'])

                if filters.get('is_active') is not None:
                    queryset = queryset.filter(is_active=filters['is_active'])

                if filters.get('city'):
                    queryset = queryset.filter(city__icontains=filters['city'])

                if filters.get('search_term'):
                    term = filters['search_term']
                    queryset = queryset.filter(
                        Q(name_ar__icontains=term) |
                        Q(name_en__icontains=term) |
                        Q(code__icontains=term)
                    )

            warehouses = []
            for warehouse in queryset.order_by('name_ar'):
                # Get stock summary
                stock_count = warehouse.stock_levels.count()
                total_value = warehouse.stock_levels.aggregate(
                    total_value=Sum(F('current_stock') * F('average_cost'))
                )['total_value'] or 0

                warehouses.append({
                    'id': warehouse.id,
                    'name_ar': warehouse.name_ar,
                    'name_en': warehouse.name_en,
                    'warehouse_type': warehouse.warehouse_type,
                    'code': warehouse.code,
                    'city': warehouse.city,
                    'manager_name': warehouse.manager_name,
                    'stock_items_count': stock_count,
                    'total_stock_value': total_value,
                    'is_active': warehouse.is_active,
                })

            return self.format_response(
                data=warehouses,
                message='تم الحصول على قائمة المخازن بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_warehouses_list', 'warehouses_list')

    def create_stock_transfer(self, data):
        """
        إنشاء تحويل مخزون
        Create stock transfer between warehouses
        Note: This would require StockTransfer model to be implemented
        """
        return self.format_response(
            success=False,
            message='وظيفة تحويل المخزون تتطلب نموذج StockTransfer'
        )

    def approve_stock_transfer(self, transfer_id, action='approve'):
        """
        اعتماد تحويل المخزون
        Approve or reject stock transfer
        Note: This would require StockTransfer model to be implemented
        """
        return self.format_response(
            success=False,
            message='وظيفة اعتماد تحويل المخزون تتطلب نموذج StockTransfer'
        )

    def get_warehouse_movements(self, warehouse_id, start_date=None, end_date=None,
                               movement_type=None, page=1, page_size=20):
        """
        الحصول على حركات المخزن
        Get warehouse movements history
        """
        self.check_permission('inventory.view_inventorymovement')

        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)

            queryset = StockMovement.objects.filter(
                warehouse=warehouse
            ).select_related('product')

            # Apply filters
            if start_date:
                queryset = queryset.filter(movement_date__gte=start_date)

            if end_date:
                queryset = queryset.filter(movement_date__lte=end_date)

            if movement_type:
                queryset = queryset.filter(movement_type=movement_type)

            queryset = queryset.order_by('-movement_date', '-created_at')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format movement data
            movements = []
            for movement in paginated_data['results']:
                movements.append({
                    'id': movement.id,
                    'movement_date': movement.movement_date,
                    'product_name': movement.product.name_ar,
                    'product_code': movement.product.code,
                    'movement_type': movement.movement_type,
                    'quantity': movement.quantity,
                    'unit_cost': movement.unit_cost,
                    'total_cost': movement.quantity * movement.unit_cost,
                    'reference_number': movement.reference_number,
                    'reference_type': movement.reference_type,
                    'notes': movement.notes,
                    'created_at': movement.created_at,
                })

            paginated_data['results'] = movements

            return self.format_response(
                data=paginated_data,
                message='تم الحصول على حركات المخزن بنجاح'
            )

        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_warehouse_movements', f'warehouse_movements/{warehouse_id}')

    def get_warehouse_utilization_report(self, warehouse_id):
        """
        تقرير استخدام المخزن
        Get warehouse utilization report
        """
        self.check_permission('inventory.view_warehouse_reports')

        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)

            # Get stock levels
            stock_levels = warehouse.stock_levels.select_related('product')

            # Calculate utilization metrics
            total_products = stock_levels.count()
            total_stock_value = sum(
                stock.current_stock * stock.average_cost
                for stock in stock_levels
            )

            # Get movement statistics (last 30 days)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            movements = StockMovement.objects.filter(
                warehouse=warehouse,
                movement_date__range=[start_date, end_date]
            )

            movement_stats = {
                'total_movements': movements.count(),
                'inbound_movements': movements.filter(
                    movement_type__in=['receipt', 'purchase', 'transfer_in', 'adjustment_in']
                ).count(),
                'outbound_movements': movements.filter(
                    movement_type__in=['issue', 'sale', 'transfer_out', 'adjustment_out']
                ).count(),
            }

            # Get top products by value
            top_products = []
            for stock in stock_levels.order_by('-current_stock')[:10]:
                top_products.append({
                    'product_name': stock.product.name_ar,
                    'current_stock': stock.current_stock,
                    'unit_cost': stock.average_cost,
                    'total_value': stock.current_stock * stock.average_cost,
                })

            # Calculate capacity utilization if capacity is set
            capacity_utilization = None
            if warehouse.capacity:
                used_capacity = total_products  # Simplified calculation
                capacity_utilization = (used_capacity / warehouse.capacity) * 100

            utilization_report = {
                'warehouse': {
                    'id': warehouse.id,
                    'name': warehouse.name_ar,
                    'capacity': warehouse.capacity,
                },
                'stock_summary': {
                    'total_products': total_products,
                    'total_stock_value': total_stock_value,
                    'capacity_utilization_percentage': capacity_utilization,
                },
                'movement_statistics': movement_stats,
                'top_products_by_value': top_products,
                'report_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                }
            }

            return self.format_response(
                data=utilization_report,
                message='تم إنشاء تقرير استخدام المخزن بنجاح'
            )

        except Warehouse.DoesNotExist:
            return self.format_response(
                success=False,
                message='المخزن غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_warehouse_utilization_report', f'warehouse_utilization/{warehouse_id}')


