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
from core.models.inventory import Supplier, SupplierContact, SupplierEvaluation, SupplierProduct


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

                # Add supplier contacts if provided
                if data.get('contacts'):
                    self._add_supplier_contacts(supplier, data['contacts'])

                # Add supplier products if provided
                if data.get('products'):
                    self._add_supplier_products(supplier, data['products'])

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
                    # Add contacts
                    contacts = []
                    for contact in supplier.contacts.all():
                        contacts.append({
                            'id': contact.id,
                            'name': contact.name,
                            'position': contact.position,
                            'phone': contact.phone,
                            'email': contact.email,
                            'is_primary': contact.is_primary,
                        })
                    supplier_data['contacts'] = contacts

                    # Add evaluation summary
                    evaluations = supplier.evaluations.all()
                    if evaluations:
                        avg_rating = evaluations.aggregate(avg_rating=Avg('overall_rating'))['avg_rating']
                        supplier_data['evaluation_summary'] = {
                            'average_rating': round(avg_rating, 2) if avg_rating else 0,
                            'evaluations_count': evaluations.count(),
                            'last_evaluation': evaluations.order_by('-evaluation_date').first().evaluation_date if evaluations else None
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
            queryset = Supplier.objects.all().select_related()  # TODO: Add appropriate select_related fields

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

                if filters.get('min_rating'):
                    queryset = queryset.filter(
                        evaluations__overall_rating__gte=filters['min_rating']
                    ).distinct()

            # Order by name
            queryset = queryset.order_by('name_ar')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format supplier data
            suppliers = []
            for supplier in paginated_data['results']:
                # Get average rating
                avg_rating = supplier.evaluations.aggregate(
                    avg_rating=Avg('overall_rating')
                )['avg_rating']

                suppliers.append({
                    'id': supplier.id,
                    'name_ar': supplier.name_ar,
                    'name_en': supplier.name_en,
                    'supplier_type': supplier.supplier_type,
                    'city': supplier.city,
                    'country': supplier.country,
                    'phone': supplier.phone,
                    'email': supplier.email,
                    'payment_terms': supplier.payment_terms,
                    'average_rating': round(avg_rating, 2) if avg_rating else 0,
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
        """
        self.check_permission('inventory.add_supplierevaluation')

        required_fields = ['evaluation_period_start', 'evaluation_period_end', 'overall_rating']
        self.validate_required_fields(evaluation_data, required_fields)

        try:
            supplier = Supplier.objects.get(id=supplier_id)

            with transaction.atomic():
                # Create supplier evaluation
                evaluation = SupplierEvaluation.objects.create(
                    supplier=supplier,
                    evaluation_date=evaluation_data.get('evaluation_date', timezone.now().date()),
                    evaluation_period_start=evaluation_data['evaluation_period_start'],
                    evaluation_period_end=evaluation_data['evaluation_period_end'],
                    overall_rating=evaluation_data['overall_rating'],
                    quality_rating=evaluation_data.get('quality_rating', 0),
                    delivery_rating=evaluation_data.get('delivery_rating', 0),
                    service_rating=evaluation_data.get('service_rating', 0),
                    price_rating=evaluation_data.get('price_rating', 0),
                    communication_rating=evaluation_data.get('communication_rating', 0),
                    strengths=evaluation_data.get('strengths', ''),
                    weaknesses=evaluation_data.get('weaknesses', ''),
                    recommendations=evaluation_data.get('recommendations', ''),
                    evaluator_notes=evaluation_data.get('evaluator_notes', ''),
                    created_by=self.user,
                    updated_by=self.user
                )

                # Update supplier's average rating
                self._update_supplier_rating(supplier)

                # Log the action
                self.log_action(
                    action='create',
                    resource='supplier_evaluation',
                    content_object=evaluation,
                    new_values=evaluation_data,
                    message=f'تم تقييم المورد: {supplier.name_ar} - التقييم: {evaluation_data["overall_rating"]}'
                )

                return self.format_response(
                    data={'evaluation_id': evaluation.id},
                    message='تم تقييم المورد بنجاح'
                )

        except Supplier.DoesNotExist:
            return self.format_response(
                success=False,
                message='المورد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'evaluate_supplier', f'supplier_evaluation/{supplier_id}', evaluation_data)

    def get_supplier_evaluations(self, supplier_id, page=1, page_size=20):
        """
        الحصول على تقييمات المورد
        Get supplier evaluations
        """
        self.check_permission('inventory.view_supplierevaluation')

        try:
            supplier = Supplier.objects.get(id=supplier_id)

            queryset = SupplierEvaluation.objects.filter(
                supplier=supplier
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-evaluation_date')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format evaluation data
            evaluations = []
            for evaluation in paginated_data['results']:
                evaluations.append({
                    'id': evaluation.id,
                    'evaluation_date': evaluation.evaluation_date,
                    'period_start': evaluation.evaluation_period_start,
                    'period_end': evaluation.evaluation_period_end,
                    'overall_rating': evaluation.overall_rating,
                    'quality_rating': evaluation.quality_rating,
                    'delivery_rating': evaluation.delivery_rating,
                    'service_rating': evaluation.service_rating,
                    'price_rating': evaluation.price_rating,
                    'communication_rating': evaluation.communication_rating,
                    'strengths': evaluation.strengths,
                    'weaknesses': evaluation.weaknesses,
                    'recommendations': evaluation.recommendations,
                    'evaluator': evaluation.created_by.get_full_name() if evaluation.created_by else '',
                })

            paginated_data['results'] = evaluations

            return self.format_response(
                data=paginated_data,
                message='تم الحصول على تقييمات المورد بنجاح'
            )

        except Supplier.DoesNotExist:
            return self.format_response(
                success=False,
                message='المورد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_supplier_evaluations', f'supplier_evaluations/{supplier_id}')

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
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

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

            # Get evaluation statistics
            evaluations = SupplierEvaluation.objects.filter(
                supplier=supplier,
                evaluation_date__range=[start_date, end_date]
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            eval_stats = evaluations.aggregate(
                avg_overall_rating=Avg('overall_rating'),
                avg_quality_rating=Avg('quality_rating'),
                avg_delivery_rating=Avg('delivery_rating'),
                avg_service_rating=Avg('service_rating'),
                avg_price_rating=Avg('price_rating'),
                evaluations_count=Count('id'),
            )

            # Get top products from this supplier
            top_products = SupplierProduct.objects.filter(
                supplier=supplier
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.select_related('product').order_by('-last_purchase_date')[:10]

            products_list = []
            for sp in top_products:
                products_list.append({
                    'product_name': sp.product.name_ar,
                    'supplier_product_code': sp.supplier_product_code,
                    'unit_price': sp.unit_price,
                    'last_purchase_date': sp.last_purchase_date,
                })

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
        """
        self.check_permission('inventory.view_supplier_reports')

        try:
            suppliers = Supplier.objects.filter(id__in=supplier_ids).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            if not suppliers.exists():
                return self.format_response(
                    success=False,
                    message='لا توجد موردين للمقارنة'
                )

            comparison_data = []

            for supplier in suppliers:
                # Get latest evaluation
                latest_evaluation = SupplierEvaluation.objects.filter(
                    supplier=supplier
                ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('-evaluation_date').first()

                # Get purchase statistics (last 12 months)
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=365)

                from core.models.procurement import PurchaseOrder

                po_stats = PurchaseOrder.objects.filter(
                    supplier=supplier,
                    order_date__range=[start_date, end_date]
                ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(
                    total_orders=Count('id'),
                    total_value=Sum('total_amount'),
                    avg_order_value=Avg('total_amount'),
                )

                supplier_data = {
                    'id': supplier.id,
                    'name': supplier.name_ar,
                    'supplier_type': supplier.supplier_type,
                    'payment_terms': supplier.payment_terms,
                    'latest_evaluation': {
                        'overall_rating': latest_evaluation.overall_rating if latest_evaluation else 0,
                        'quality_rating': latest_evaluation.quality_rating if latest_evaluation else 0,
                        'delivery_rating': latest_evaluation.delivery_rating if latest_evaluation else 0,
                        'service_rating': latest_evaluation.service_rating if latest_evaluation else 0,
                        'price_rating': latest_evaluation.price_rating if latest_evaluation else 0,
                        'evaluation_date': latest_evaluation.evaluation_date if latest_evaluation else None,
                    },
                    'purchase_statistics': {
                        'total_orders': po_stats['total_orders'] or 0,
                        'total_value': po_stats['total_value'] or 0,
                        'average_order_value': po_stats['avg_order_value'] or 0,
                    }
                }

                comparison_data.append(supplier_data)

            return self.format_response(
                data=comparison_data,
                message='تم إنشاء مقارنة الموردين بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_suppliers_comparison', 'suppliers_comparison')

    def _add_supplier_contacts(self, supplier, contacts_data):
        """إضافة جهات اتصال المورد"""
        for contact_data in contacts_data:
            SupplierContact.objects.create(
                supplier=supplier,
                name=contact_data['name'],
                position=contact_data.get('position', ''),
                phone=contact_data.get('phone', ''),
                email=contact_data.get('email', ''),
                is_primary=contact_data.get('is_primary', False),
                created_by=self.user,
                updated_by=self.user
            )

    def _add_supplier_products(self, supplier, products_data):
        """إضافة منتجات المورد"""
        from core.models.inventory import Product

        for product_data in products_data:
            try:
                product = Product.objects.get(id=product_data['product_id'])

                SupplierProduct.objects.create(
                    supplier=supplier,
                    product=product,
                    supplier_product_code=product_data.get('supplier_product_code', ''),
                    unit_price=product_data.get('unit_price', 0),
                    minimum_order_quantity=product_data.get('minimum_order_quantity', 1),
                    lead_time_days=product_data.get('lead_time_days', 0),
                    is_preferred=product_data.get('is_preferred', False),
                    created_by=self.user,
                    updated_by=self.user
                )
            except Product.DoesNotExist:
                self.logger.warning(f"Product {product_data['product_id']} not found for supplier {supplier.id}")

    def _update_supplier_rating(self, supplier):
        """تحديث تقييم المورد المتوسط"""
        avg_rating = SupplierEvaluation.objects.filter(
            supplier=supplier
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.aggregate(avg_rating=Avg('overall_rating'))['avg_rating']

        if avg_rating:
            supplier.average_rating = round(avg_rating, 2)
            supplier.save()
