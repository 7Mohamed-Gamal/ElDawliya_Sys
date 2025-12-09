"""
أمر إدارة لترحيل نماذج المخزون والمشتريات إلى الهيكل الجديد
Management command to migrate inventory and procurement models to new structure
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class"""
    help = 'ترحيل نماذج المخزون والمشتريات إلى الهيكل الجديد الموحد'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حفظ التغييرات',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='عرض تفاصيل أكثر',
        )

    def handle(self, *args, **options):
        """handle function"""
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('تشغيل تجريبي - لن يتم حفظ أي تغييرات')
            )

        try:
            with transaction.atomic():
                self.migrate_categories()
                self.migrate_units()
                self.migrate_suppliers()
                self.migrate_warehouses()
                self.migrate_products()
                self.migrate_purchase_orders()

                if self.dry_run:
                    raise Exception("Dry run - rolling back changes")

        except Exception as e:
            if "Dry run" in str(e):
                self.stdout.write(
                    self.style.SUCCESS('تم الانتهاء من التشغيل التجريبي بنجاح')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'خطأ في الترحيل: {str(e)}')
                )
                raise

        self.stdout.write(
            self.style.SUCCESS('تم ترحيل نماذج المخزون والمشتريات بنجاح')
        )

    def migrate_categories(self):
        """ترحيل تصنيفات المنتجات"""
        self.stdout.write('ترحيل تصنيفات المنتجات...')

        try:
            from apps.inventory.models import TblCategories
            from core.models.inventory import ProductCategory

            categories_migrated = 0

            for old_category in TblCategories.objects.all():
                category, created = ProductCategory.objects.get_or_create(
                    code=f"CAT-{old_category.cat_id:04d}",
                    defaults={
                        'name': old_category.cat_name or f'تصنيف {old_category.cat_id}',
                        'description': f'تصنيف مرحل من النظام القديم - ID: {old_category.cat_id}',
                        'sort_order': old_category.cat_id,
                        'is_active': True,
                    }
                )

                if created:
                    categories_migrated += 1
                    if self.verbose:
                        self.stdout.write(f'  - تم إنشاء تصنيف: {category.name}')

            self.stdout.write(
                self.style.SUCCESS(f'تم ترحيل {categories_migrated} تصنيف')
            )

        except ImportError:
            self.stdout.write(
                self.style.WARNING('لم يتم العثور على نماذج التصنيفات القديمة')
            )

    def migrate_units(self):
        """ترحيل وحدات القياس"""
        self.stdout.write('ترحيل وحدات القياس...')

        try:
            from apps.inventory.models import TblUnitsSpareparts
            from core.models.inventory import Unit

            units_migrated = 0

            for old_unit in TblUnitsSpareparts.objects.all():
                unit, created = Unit.objects.get_or_create(
                    symbol=f"U{old_unit.unit_id:03d}",
                    defaults={
                        'name': old_unit.unit_name or f'وحدة {old_unit.unit_id}',
                        'description': f'وحدة مرحلة من النظام القديم - ID: {old_unit.unit_id}',
                        'is_base_unit': True,
                        'conversion_factor': Decimal('1.0'),
                        'is_active': True,
                    }
                )

                if created:
                    units_migrated += 1
                    if self.verbose:
                        self.stdout.write(f'  - تم إنشاء وحدة: {unit.name}')

            self.stdout.write(
                self.style.SUCCESS(f'تم ترحيل {units_migrated} وحدة قياس')
            )

        except ImportError:
            self.stdout.write(
                self.style.WARNING('لم يتم العثور على نماذج الوحدات القديمة')
            )

    def migrate_suppliers(self):
        """ترحيل الموردين"""
        self.stdout.write('ترحيل الموردين...')

        try:
            from apps.inventory.models import TblSuppliers
            from apps.procurement.purchase_orders.models import Vendor
            from core.models.inventory import Supplier

            suppliers_migrated = 0

            # ترحيل من TblSuppliers
            for old_supplier in TblSuppliers.objects.all():
                supplier, created = Supplier.objects.get_or_create(
                    code=f"SUP-{old_supplier.supplier_id:04d}",
                    defaults={
                        'name': old_supplier.supplier_name or f'مورد {old_supplier.supplier_id}',
                        'supplier_type': 'local',
                        'payment_terms': 'net_30',
                        'rating': 5,
                        'is_approved': True,
                        'is_active': True,
                    }
                )

                if created:
                    suppliers_migrated += 1
                    if self.verbose:
                        self.stdout.write(f'  - تم إنشاء مورد: {supplier.name}')

            # ترحيل من Vendor
            for old_vendor in Vendor.objects.all():
                supplier, created = Supplier.objects.get_or_create(
                    name=old_vendor.name,
                    defaults={
                        'code': f"VEN-{old_vendor.id:04d}",
                        'contact_person': old_vendor.contact_person,
                        'phone': old_vendor.phone,
                        'email': old_vendor.email,
                        'address': old_vendor.address,
                        'supplier_type': 'local',
                        'payment_terms': 'net_30',
                        'rating': 5,
                        'is_approved': True,
                        'is_active': True,
                    }
                )

                if created:
                    suppliers_migrated += 1
                    if self.verbose:
                        self.stdout.write(f'  - تم إنشاء مورد: {supplier.name}')

            self.stdout.write(
                self.style.SUCCESS(f'تم ترحيل {suppliers_migrated} مورد')
            )

        except ImportError:
            self.stdout.write(
                self.style.WARNING('لم يتم العثور على نماذج الموردين القديمة')
            )

    def migrate_warehouses(self):
        """إنشاء مخزن افتراضي"""
        self.stdout.write('إنشاء المخازن الافتراضية...')

        from core.models.inventory import Warehouse

        # إنشاء مخزن رئيسي افتراضي
        main_warehouse, created = Warehouse.objects.get_or_create(
            code='MAIN-001',
            defaults={
                'name': 'المخزن الرئيسي',
                'description': 'المخزن الرئيسي للشركة',
                'is_main_warehouse': True,
                'capacity': Decimal('10000.00'),
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(f'  - تم إنشاء المخزن الرئيسي: {main_warehouse.name}')

        self.stdout.write(
            self.style.SUCCESS('تم إنشاء المخازن الافتراضية')
        )

    def migrate_products(self):
        """ترحيل المنتجات"""
        self.stdout.write('ترحيل المنتجات...')

        try:
            from apps.inventory.models import TblProducts
            from core.models.inventory import Product, ProductCategory, Unit, Warehouse, StockLevel

            products_migrated = 0
            main_warehouse = Warehouse.objects.filter(is_main_warehouse=True).first()
            default_category = ProductCategory.objects.first()
            default_unit = Unit.objects.first()

            if not main_warehouse or not default_category or not default_unit:
                self.stdout.write(
                    self.style.ERROR('يجب إنشاء المخازن والتصنيفات والوحدات أولاً')
                )
                return

            for old_product in TblProducts.objects.all():
                # البحث عن التصنيف المناسب
                category = default_category
                if old_product.cat_id:
                    try:
                        category = ProductCategory.objects.get(
                            code=f"CAT-{old_product.cat_id:04d}"
                        )
                    except ProductCategory.DoesNotExist:
                        pass

                # البحث عن الوحدة المناسبة
                unit = default_unit
                if old_product.unit_id:
                    try:
                        unit = Unit.objects.get(
                            symbol=f"U{old_product.unit_id:03d}"
                        )
                    except Unit.DoesNotExist:
                        pass

                product, created = Product.objects.get_or_create(
                    code=old_product.product_id,
                    defaults={
                        'name': old_product.product_name or f'منتج {old_product.product_id}',
                        'category': category,
                        'unit': unit,
                        'product_type': 'finished_good',
                        'cost_price': old_product.unit_price or Decimal('0'),
                        'selling_price': old_product.unit_price or Decimal('0'),
                        'min_stock_level': old_product.minimum_threshold or Decimal('0'),
                        'max_stock_level': old_product.maximum_threshold,
                        'tracking_method': 'none',
                        'is_active': True,
                    }
                )

                if created:
                    products_migrated += 1

                    # إنشاء مستوى المخزون
                    stock_level, stock_created = StockLevel.objects.get_or_create(
                        product=product,
                        warehouse=main_warehouse,
                        defaults={
                            'quantity_on_hand': old_product.qte_in_stock or Decimal('0'),
                            'quantity_reserved': Decimal('0'),
                            'quantity_on_order': Decimal('0'),
                            'average_cost': old_product.unit_price or Decimal('0'),
                        }
                    )

                    if self.verbose:
                        self.stdout.write(f'  - تم إنشاء منتج: {product.name}')

            self.stdout.write(
                self.style.SUCCESS(f'تم ترحيل {products_migrated} منتج')
            )

        except ImportError:
            self.stdout.write(
                self.style.WARNING('لم يتم العثور على نماذج المنتجات القديمة')
            )

    def migrate_purchase_orders(self):
        """ترحيل أوامر الشراء"""
        self.stdout.write('ترحيل أوامر الشراء...')

        try:
            from apps.procurement.purchase_orders.models import PurchaseRequest as OldPurchaseRequest
            from apps.procurement.purchase_orders.models import PurchaseRequestItem as OldPurchaseRequestItem
            from core.models.procurement import PurchaseRequest, PurchaseRequestLineItem
            from core.models.inventory import Product, Supplier, Warehouse

            requests_migrated = 0
            main_warehouse = Warehouse.objects.filter(is_main_warehouse=True).first()

            if not main_warehouse:
                self.stdout.write(
                    self.style.ERROR('يجب إنشاء المخازن أولاً')
                )
                return

            for old_request in OldPurchaseRequest.objects.all():
                # البحث عن المورد
                supplier = None
                if old_request.vendor:
                    try:
                        supplier = Supplier.objects.get(name=old_request.vendor.name)
                    except Supplier.DoesNotExist:
                        pass

                purchase_request, created = PurchaseRequest.objects.get_or_create(
                    pr_number=old_request.request_number,
                    defaults={
                        'pr_date': old_request.request_date.date() if old_request.request_date else timezone.now().date(),
                        'requested_by': old_request.requested_by,
                        'status': self.map_old_status_to_new(old_request.status),
                        'urgency': 'normal',
                        'justification': old_request.notes or 'طلب مرحل من النظام القديم',
                        'approved_by': old_request.approved_by,
                        'approved_at': old_request.approval_date,
                    }
                )

                if created:
                    requests_migrated += 1

                    # ترحيل عناصر الطلب
                    for old_item in old_request.items.all():
                        try:
                            product = Product.objects.get(code=old_item.product.product_id)

                            PurchaseRequestLineItem.objects.get_or_create(
                                purchase_request=purchase_request,
                                product=product,
                                defaults={
                                    'quantity_requested': old_item.quantity_requested,
                                    'preferred_supplier': supplier,
                                    'specifications': old_item.notes or '',
                                }
                            )
                        except Product.DoesNotExist:
                            # إنشاء عنصر بوصف نصي
                            PurchaseRequestLineItem.objects.get_or_create(
                                purchase_request=purchase_request,
                                item_description=old_item.product.product_name,
                                defaults={
                                    'quantity_requested': old_item.quantity_requested,
                                    'preferred_supplier': supplier,
                                    'specifications': old_item.notes or '',
                                }
                            )

                    if self.verbose:
                        self.stdout.write(f'  - تم إنشاء طلب شراء: {purchase_request.pr_number}')

            self.stdout.write(
                self.style.SUCCESS(f'تم ترحيل {requests_migrated} طلب شراء')
            )

        except ImportError:
            self.stdout.write(
                self.style.WARNING('لم يتم العثور على نماذج طلبات الشراء القديمة')
            )

    def map_old_status_to_new(self, old_status):
        """تحويل حالات النظام القديم إلى الجديد"""
        status_mapping = {
            'pending': 'submitted',
            'approved': 'approved',
            'rejected': 'rejected',
            'completed': 'fully_ordered',
        }
        return status_mapping.get(old_status, 'draft')
