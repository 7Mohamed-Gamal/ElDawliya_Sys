"""
خدمة إدارة المنتجات والتصنيفات
Product and Category Management Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from core.services.base import BaseService
from core.models.inventory import Product, ProductCategory, ProductUnit, ProductImage, ProductVariant


class ProductService(BaseService):
    """
    خدمة إدارة المنتجات والتصنيفات
    Comprehensive product and category management service
    """

    def create_product(self, data):
        """
        إنشاء منتج جديد
        Create new product
        """
        self.check_permission('inventory.add_product')

        required_fields = ['name_ar', 'name_en', 'code', 'category_id', 'unit_id']
        self.validate_required_fields(data, required_fields)

        try:
            # Check if product code already exists
            if Product.objects.filter(code=data['code']).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
                return self.format_response(
                    success=False,
                    message=f"كود المنتج {data['code']} موجود بالفعل"
                )

            category = ProductCategory.objects.get(id=data['category_id'])
            unit = ProductUnit.objects.get(id=data['unit_id'])

            with transaction.atomic():
                # Create product
                product_data = self.clean_data(data, [
                    'name_ar', 'name_en', 'code', 'description_ar', 'description_en',
                    'cost_price', 'selling_price', 'min_stock_level', 'max_stock_level',
                    'reorder_level', 'barcode', 'sku', 'brand', 'model', 'weight',
                    'dimensions', 'color', 'size', 'material', 'warranty_period',
                    'is_active', 'is_serialized', 'track_expiry', 'tax_rate'
                ])

                product = Product.objects.create(
                    category=category,
                    unit=unit,
                    **product_data,
                    created_by=self.user,
                    updated_by=self.user
                )

                # Add product images if provided
                if data.get('images'):
                    self._add_product_images(product, data['images'])

                # Add product variants if provided
                if data.get('variants'):
                    self._add_product_variants(product, data['variants'])

                # Log the action
                self.log_action(
                    action='create',
                    resource='product',
                    content_object=product,
                    new_values=product_data,
                    message=f'تم إنشاء منتج جديد: {product.name_ar}'
                )

                return self.format_response(
                    data={
                        'product_id': product.id,
                        'code': product.code,
                        'name': product.name_ar
                    },
                    message='تم إنشاء المنتج بنجاح'
                )

        except ProductCategory.DoesNotExist:
            return self.format_response(
                success=False,
                message='التصنيف المحدد غير موجود'
            )
        except ProductUnit.DoesNotExist:
            return self.format_response(
                success=False,
                message='الوحدة المحددة غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_product', 'product', data)

    def update_product(self, product_id, data):
        """
        تحديث بيانات المنتج
        Update product information
        """
        self.check_permission('inventory.change_product')

        try:
            product = Product.objects.get(id=product_id)

            # Check object-level permission
            self.check_object_permission('inventory.change_product', product)

            # Get old values for audit
            old_values, new_values = self.get_model_changes(product, data)

            # Update product data
            allowed_fields = [
                'name_ar', 'name_en', 'description_ar', 'description_en',
                'cost_price', 'selling_price', 'min_stock_level', 'max_stock_level',
                'reorder_level', 'barcode', 'sku', 'brand', 'model', 'weight',
                'dimensions', 'color', 'size', 'material', 'warranty_period',
                'is_active', 'is_serialized', 'track_expiry', 'tax_rate',
                'category_id', 'unit_id'
            ]

            for field, value in data.items():
                if field in allowed_fields and hasattr(product, field):
                    setattr(product, field, value)

            product.updated_by = self.user
            product.save()

            # Log the action
            self.log_action(
                action='update',
                resource='product',
                content_object=product,
                old_values=old_values,
                new_values=new_values,
                message=f'تم تحديث بيانات المنتج: {product.name_ar}'
            )

            # Invalidate cache
            self.invalidate_cache(f'product_{product_id}_*')

            return self.format_response(
                data={
                    'product_id': product.id,
                    'updated_fields': list(new_values.keys())
                },
                message='تم تحديث بيانات المنتج بنجاح'
            )

        except Product.DoesNotExist:
            return self.format_response(
                success=False,
                message='المنتج غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_product', f'product/{product_id}', data)

    def get_product(self, product_id, include_stock=True):
        """
        الحصول على بيانات المنتج
        Get product details
        """
        self.check_permission('inventory.view_product')

        try:
            cache_key = self.cache_key('product', product_id, 'details', include_stock)

            def get_product_data():
                """get_product_data function"""
                queryset = Product.objects.select_related('category', 'unit')

                if include_stock:
                    queryset = queryset.prefetch_related('stock_levels', 'images', 'variants')

                product = queryset.get(id=product_id)

                # Check object-level permission
                self.check_object_permission('inventory.view_product', product)

                product_data = {
                    'id': product.id,
                    'code': product.code,
                    'name_ar': product.name_ar,
                    'name_en': product.name_en,
                    'description_ar': product.description_ar,
                    'description_en': product.description_en,
                    'category': {
                        'id': product.category.id,
                        'name_ar': product.category.name_ar,
                        'name_en': product.category.name_en,
                    } if product.category else None,
                    'unit': {
                        'id': product.unit.id,
                        'name_ar': product.unit.name_ar,
                        'name_en': product.unit.name_en,
                        'symbol': product.unit.symbol,
                    } if product.unit else None,
                    'cost_price': product.cost_price,
                    'selling_price': product.selling_price,
                    'min_stock_level': product.min_stock_level,
                    'max_stock_level': product.max_stock_level,
                    'reorder_level': product.reorder_level,
                    'barcode': product.barcode,
                    'sku': product.sku,
                    'brand': product.brand,
                    'model': product.model,
                    'is_active': product.is_active,
                    'is_serialized': product.is_serialized,
                    'track_expiry': product.track_expiry,
                    'created_at': product.created_at,
                }

                if include_stock:
                    # Add stock information
                    stock_levels = []
                    for stock in product.stock_levels.all():
                        stock_levels.append({
                            'warehouse_id': stock.warehouse.id,
                            'warehouse_name': stock.warehouse.name_ar,
                            'current_stock': stock.current_stock,
                            'available_stock': stock.available_stock,
                            'reserved_stock': stock.reserved_stock,
                        })

                    product_data['stock_levels'] = stock_levels
                    product_data['total_stock'] = sum(s['current_stock'] for s in stock_levels)

                return product_data

            product_data = self.get_from_cache(cache_key)
            if not product_data:
                product_data = get_product_data()
                self.set_cache(cache_key, product_data, 300)  # 5 minutes

            return self.format_response(
                data=product_data,
                message='تم الحصول على بيانات المنتج بنجاح'
            )

        except Product.DoesNotExist:
            return self.format_response(
                success=False,
                message='المنتج غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_product', f'product/{product_id}')

    def search_products(self, filters=None, page=1, page_size=20):
        """
        البحث في المنتجات
        Search products with filters
        """
        self.check_permission('inventory.view_product')

        try:
            queryset = Product.objects.select_related('category', 'unit')

            # Apply filters
            if filters:
                if filters.get('category_id'):
                    queryset = queryset.filter(category_id=filters['category_id'])

                if filters.get('is_active') is not None:
                    queryset = queryset.filter(is_active=filters['is_active'])

                if filters.get('search_term'):
                    term = filters['search_term']
                    queryset = queryset.filter(
                        Q(name_ar__icontains=term) |
                        Q(name_en__icontains=term) |
                        Q(code__icontains=term) |
                        Q(barcode__icontains=term) |
                        Q(sku__icontains=term)
                    )

                if filters.get('brand'):
                    queryset = queryset.filter(brand__icontains=filters['brand'])

                if filters.get('min_price'):
                    queryset = queryset.filter(selling_price__gte=filters['min_price'])

                if filters.get('max_price'):
                    queryset = queryset.filter(selling_price__lte=filters['max_price'])

                if filters.get('low_stock_only'):
                    from django.db.models import F
                    queryset = queryset.filter(
                        stock_levels__current_stock__lte=F('min_stock_level')
                    ).distinct()

            # Order by name
            queryset = queryset.order_by('name_ar')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format product data
            products = []
            for product in paginated_data['results']:
                products.append({
                    'id': product.id,
                    'code': product.code,
                    'name_ar': product.name_ar,
                    'name_en': product.name_en,
                    'category': product.category.name_ar if product.category else '',
                    'unit': product.unit.name_ar if product.unit else '',
                    'cost_price': product.cost_price,
                    'selling_price': product.selling_price,
                    'barcode': product.barcode,
                    'brand': product.brand,
                    'is_active': product.is_active,
                })

            paginated_data['results'] = products

            return self.format_response(
                data=paginated_data,
                message='تم البحث في المنتجات بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'search_products', 'products', filters)

    def create_category(self, data):
        """
        إنشاء تصنيف جديد
        Create new product category
        """
        self.check_permission('inventory.add_productcategory')

        required_fields = ['name_ar', 'name_en']
        self.validate_required_fields(data, required_fields)

        try:
            with transaction.atomic():
                category = ProductCategory.objects.create(
                    name_ar=data['name_ar'],
                    name_en=data['name_en'],
                    description_ar=data.get('description_ar', ''),
                    description_en=data.get('description_en', ''),
                    parent_category_id=data.get('parent_category_id'),
                    is_active=data.get('is_active', True),
                    created_by=self.user,
                    updated_by=self.user
                )

                # Log the action
                self.log_action(
                    action='create',
                    resource='product_category',
                    content_object=category,
                    new_values=data,
                    message=f'تم إنشاء تصنيف جديد: {category.name_ar}'
                )

                return self.format_response(
                    data={'category_id': category.id},
                    message='تم إنشاء التصنيف بنجاح'
                )

        except Exception as e:
            return self.handle_exception(e, 'create_category', 'product_category', data)

    def get_categories_tree(self):
        """
        الحصول على شجرة التصنيفات
        Get categories tree structure
        """
        self.check_permission('inventory.view_productcategory')

        try:
            cache_key = self.cache_key('categories', 'tree')

            def build_categories_tree():
                """build_categories_tree function"""
                categories = ProductCategory.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields.order_by('name_ar')

                # Build tree structure
                categories_dict = {}
                root_categories = []

                for category in categories:
                    category_data = {
                        'id': category.id,
                        'name_ar': category.name_ar,
                        'name_en': category.name_en,
                        'description_ar': category.description_ar,
                        'parent_id': category.parent_category_id,
                        'children': [],
                        'products_count': category.products.filter(is_active=True).count()
                    }

                    categories_dict[category.id] = category_data

                    if not category.parent_category_id:
                        root_categories.append(category_data)

                # Build children relationships
                for category_data in categories_dict.values():
                    if category_data['parent_id']:
                        parent = categories_dict.get(category_data['parent_id'])
                        if parent:
                            parent['children'].append(category_data)

                return root_categories

            categories_tree = self.get_from_cache(cache_key)
            if not categories_tree:
                categories_tree = build_categories_tree()
                self.set_cache(cache_key, categories_tree, 1800)  # 30 minutes

            return self.format_response(
                data=categories_tree,
                message='تم الحصول على شجرة التصنيفات بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_categories_tree', 'categories_tree')

    def get_product_analytics(self, category_id=None):
        """
        الحصول على تحليلات المنتجات
        Get product analytics
        """
        self.check_permission('inventory.view_product_analytics')

        try:
            queryset = Product.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            if category_id:
                queryset = queryset.filter(category_id=category_id)

            # Calculate analytics
            analytics = queryset.aggregate(
                total_products=Count('id'),
                avg_cost_price=Avg('cost_price'),
                avg_selling_price=Avg('selling_price'),
                total_value=Sum('cost_price'),
            )

            # Get category breakdown
            category_breakdown = queryset.values(
                'category__name_ar'
            ).annotate(
                count=Count('id'),
                avg_price=Avg('selling_price')
            ).order_by('category__name_ar')

            # Get brand breakdown
            brand_breakdown = queryset.exclude(
                brand__isnull=True
            ).exclude(
                brand=''
            ).values('brand').annotate(
                count=Count('id')
            ).order_by('-count')[:10]

            # Get low stock products count
            low_stock_count = queryset.filter(
                stock_levels__current_stock__lte=F('min_stock_level')
            ).distinct().count()

            analytics.update({
                'category_breakdown': list(category_breakdown),
                'brand_breakdown': list(brand_breakdown),
                'low_stock_count': low_stock_count,
            })

            return self.format_response(
                data=analytics,
                message='تم الحصول على تحليلات المنتجات بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_product_analytics', 'product_analytics')

    def bulk_update_prices(self, updates_data):
        """
        تحديث الأسعار بالجملة
        Bulk update product prices
        """
        self.check_permission('inventory.change_product')

        try:
            updated_count = 0
            errors = []

            with transaction.atomic():
                for update_data in updates_data:
                    try:
                        product = Product.objects.get(id=update_data['product_id'])

                        old_cost_price = product.cost_price
                        old_selling_price = product.selling_price

                        if 'cost_price' in update_data:
                            product.cost_price = update_data['cost_price']

                        if 'selling_price' in update_data:
                            product.selling_price = update_data['selling_price']

                        product.updated_by = self.user
                        product.save()

                        # Log individual update
                        self.log_action(
                            action='update',
                            resource='product_price',
                            content_object=product,
                            old_values={
                                'cost_price': old_cost_price,
                                'selling_price': old_selling_price
                            },
                            new_values={
                                'cost_price': product.cost_price,
                                'selling_price': product.selling_price
                            },
                            message=f'تم تحديث أسعار المنتج: {product.name_ar}'
                        )

                        updated_count += 1

                    except Product.DoesNotExist:
                        errors.append(f'المنتج {update_data["product_id"]} غير موجود')
                    except Exception as e:
                        errors.append(f'خطأ في تحديث المنتج {update_data["product_id"]}: {str(e)}')

            return self.format_response(
                data={
                    'updated_count': updated_count,
                    'errors_count': len(errors),
                    'errors': errors
                },
                message=f'تم تحديث {updated_count} منتج بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'bulk_update_prices', 'bulk_price_update')

    def _add_product_images(self, product, images_data):
        """إضافة صور المنتج"""
        for image_data in images_data:
            ProductImage.objects.create(
                product=product,
                image_path=image_data['image_path'],
                alt_text=image_data.get('alt_text', ''),
                is_primary=image_data.get('is_primary', False),
                display_order=image_data.get('display_order', 0),
                created_by=self.user,
                updated_by=self.user
            )

    def _add_product_variants(self, product, variants_data):
        """إضافة متغيرات المنتج"""
        for variant_data in variants_data:
            ProductVariant.objects.create(
                product=product,
                variant_name=variant_data['variant_name'],
                variant_value=variant_data['variant_value'],
                additional_cost=variant_data.get('additional_cost', 0),
                sku_suffix=variant_data.get('sku_suffix', ''),
                is_active=variant_data.get('is_active', True),
                created_by=self.user,
                updated_by=self.user
            )
