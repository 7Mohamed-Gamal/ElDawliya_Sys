"""
نماذج المخزون المحسنة والموحدة
Enhanced and Unified Inventory Models
"""
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from .base import BaseModel, AuditableModel, SoftDeleteModel, AddressModel, ContactModel


class ProductCategory(BaseModel):
    """
    تصنيفات المنتجات
    Product Categories
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم التصنيف'),
        help_text=_('اسم تصنيف المنتج')
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('رمز التصنيف'),
        help_text=_('رمز فريد للتصنيف')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف التصنيف')
    )
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_('التصنيف الأب'),
        help_text=_('التصنيف الرئيسي إن وجد')
    )
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name=_('صورة التصنيف')
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('ترتيب العرض')
    )

    class Meta:
        verbose_name = _('تصنيف المنتج')
        verbose_name_plural = _('تصنيفات المنتجات')
        ordering = ['sort_order', 'name']
        unique_together = ['name', 'parent_category']

    def __str__(self):
        if self.parent_category:
            return f"{self.parent_category.name} - {self.name}"
        return self.name

    @property
    def full_path(self):
        """Get full category path"""
        path = [self.name]
        parent = self.parent_category
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_category
        return ' > '.join(path)

    def get_all_subcategories(self):
        """Get all subcategories recursively"""
        subcategories = list(self.subcategories.filter(is_active=True))
        for subcategory in self.subcategories.filter(is_active=True):
            subcategories.extend(subcategory.get_all_subcategories())
        return subcategories


class Unit(BaseModel):
    """
    وحدات القياس
    Units of Measurement
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('اسم الوحدة'),
        help_text=_('اسم وحدة القياس')
    )
    symbol = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('رمز الوحدة'),
        help_text=_('الرمز المختصر للوحدة')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف')
    )
    is_base_unit = models.BooleanField(
        default=False,
        verbose_name=_('وحدة أساسية'),
        help_text=_('هل هذه وحدة أساسية أم فرعية')
    )
    base_unit = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='derived_units',
        verbose_name=_('الوحدة الأساسية')
    )
    conversion_factor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name=_('معامل التحويل'),
        help_text=_('معامل التحويل إلى الوحدة الأساسية')
    )

    class Meta:
        verbose_name = _('وحدة القياس')
        verbose_name_plural = _('وحدات القياس')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def clean(self):
        if self.is_base_unit and self.base_unit:
            raise ValidationError(_('الوحدة الأساسية لا يمكن أن تحتوي على وحدة أساسية أخرى'))
        if not self.is_base_unit and not self.base_unit:
            raise ValidationError(_('الوحدة الفرعية يجب أن تحتوي على وحدة أساسية'))


class Warehouse(BaseModel, AddressModel):
    """
    المخازن
    Warehouses
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('اسم المخزن'),
        help_text=_('اسم المخزن')
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('رمز المخزن'),
        help_text=_('رمز فريد للمخزن')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف')
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses',
        verbose_name=_('مدير المخزن')
    )
    capacity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('السعة الإجمالية'),
        help_text=_('السعة الإجمالية للمخزن')
    )
    is_main_warehouse = models.BooleanField(
        default=False,
        verbose_name=_('مخزن رئيسي'),
        help_text=_('هل هذا مخزن رئيسي')
    )

    class Meta:
        verbose_name = _('مخزن')
        verbose_name_plural = _('المخازن')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def current_capacity_used(self):
        """Calculate current capacity used"""
        from django.db.models import Sum
        total_stock = self.stock_levels.aggregate(
            total=Sum('quantity_on_hand')
        )['total'] or Decimal('0')
        return total_stock

    @property
    def capacity_utilization_percentage(self):
        """Calculate capacity utilization percentage"""
        if not self.capacity or self.capacity == 0:
            return 0
        return (self.current_capacity_used / self.capacity) * 100


class Supplier(BaseModel, AddressModel, ContactModel):
    """
    الموردين
    Suppliers
    """
    SUPPLIER_TYPES = [
        ('local', _('محلي')),
        ('international', _('دولي')),
        ('manufacturer', _('مصنع')),
        ('distributor', _('موزع')),
        ('wholesaler', _('تاجر جملة')),
    ]

    PAYMENT_TERMS = [
        ('cash', _('نقداً')),
        ('net_30', _('30 يوم')),
        ('net_60', _('60 يوم')),
        ('net_90', _('90 يوم')),
        ('custom', _('مخصص')),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم المورد'),
        help_text=_('اسم المورد أو الشركة')
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('رمز المورد'),
        help_text=_('رمز فريد للمورد')
    )
    supplier_type = models.CharField(
        max_length=20,
        choices=SUPPLIER_TYPES,
        default='local',
        verbose_name=_('نوع المورد')
    )
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('جهة الاتصال')
    )
    tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('الرقم الضريبي')
    )
    commercial_registration = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('السجل التجاري')
    )
    payment_terms = models.CharField(
        max_length=20,
        choices=PAYMENT_TERMS,
        default='net_30',
        verbose_name=_('شروط الدفع')
    )
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('حد الائتمان')
    )
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_('التقييم'),
        help_text=_('تقييم المورد من 1 إلى 10')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('معتمد'),
        help_text=_('هل المورد معتمد للتعامل معه')
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_suppliers',
        verbose_name=_('اعتمد بواسطة')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الاعتماد')
    )

    class Meta:
        verbose_name = _('مورد')
        verbose_name_plural = _('الموردين')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def approve(self, user):
        """Approve supplier"""
        self.is_approved = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=['is_approved', 'approved_by', 'approved_at'])

    @property
    def total_orders_value(self):
        """Calculate total orders value"""
        from django.db.models import Sum
        return self.purchase_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')

    @property
    def orders_count(self):
        """Get total orders count"""
        return self.purchase_orders.count()


class Product(AuditableModel):
    """
    المنتجات
    Products
    """
    PRODUCT_TYPES = [
        ('raw_material', _('مادة خام')),
        ('finished_good', _('منتج تام')),
        ('semi_finished', _('نصف مصنع')),
        ('consumable', _('مستهلك')),
        ('service', _('خدمة')),
    ]

    TRACKING_METHODS = [
        ('none', _('بدون تتبع')),
        ('serial', _('رقم تسلسلي')),
        ('batch', _('دفعة')),
        ('expiry', _('تاريخ انتهاء')),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_('اسم المنتج'),
        help_text=_('اسم المنتج')
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رمز المنتج'),
        help_text=_('رمز فريد للمنتج')
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('الباركود')
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('التصنيف')
    )
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        default='finished_good',
        verbose_name=_('نوع المنتج')
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('وحدة القياس')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف')
    )
    specifications = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('المواصفات'),
        help_text=_('المواصفات التقنية للمنتج')
    )
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        verbose_name=_('صورة المنتج')
    )
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر التكلفة')
    )
    selling_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر البيع')
    )
    
    # Stock Management
    tracking_method = models.CharField(
        max_length=20,
        choices=TRACKING_METHODS,
        default='none',
        verbose_name=_('طريقة التتبع')
    )
    min_stock_level = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الحد الأدنى للمخزون')
    )
    max_stock_level = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الحد الأقصى للمخزون')
    )
    reorder_point = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('نقطة إعادة الطلب')
    )
    reorder_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('كمية إعادة الطلب')
    )
    
    # Quality Control
    requires_inspection = models.BooleanField(
        default=False,
        verbose_name=_('يتطلب فحص'),
        help_text=_('هل المنتج يتطلب فحص جودة')
    )
    shelf_life_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('مدة الصلاحية (أيام)')
    )
    
    # Supplier Information
    preferred_supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_products',
        verbose_name=_('المورد المفضل')
    )
    
    # Status
    is_discontinued = models.BooleanField(
        default=False,
        verbose_name=_('متوقف'),
        help_text=_('هل المنتج متوقف الإنتاج')
    )

    class Meta:
        verbose_name = _('منتج')
        verbose_name_plural = _('المنتجات')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        if self.max_stock_level and self.min_stock_level:
            if self.max_stock_level <= self.min_stock_level:
                raise ValidationError(_('الحد الأقصى يجب أن يكون أكبر من الحد الأدنى'))
        
        if self.reorder_point and self.min_stock_level:
            if self.reorder_point < self.min_stock_level:
                raise ValidationError(_('نقطة إعادة الطلب يجب أن تكون أكبر من أو تساوي الحد الأدنى'))

    @property
    def total_stock_quantity(self):
        """Get total stock quantity across all warehouses"""
        from django.db.models import Sum
        return self.stock_levels.aggregate(
            total=Sum('quantity_on_hand')
        )['total'] or Decimal('0')

    @property
    def available_stock_quantity(self):
        """Get available stock quantity (on hand - reserved)"""
        from django.db.models import Sum, F
        return self.stock_levels.aggregate(
            available=Sum(F('quantity_on_hand') - F('quantity_reserved'))
        )['available'] or Decimal('0')

    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.total_stock_quantity <= self.min_stock_level

    @property
    def needs_reorder(self):
        """Check if product needs reordering"""
        if not self.reorder_point:
            return False
        return self.available_stock_quantity <= self.reorder_point

    def get_stock_in_warehouse(self, warehouse):
        """Get stock quantity in specific warehouse"""
        try:
            stock_level = self.stock_levels.get(warehouse=warehouse)
            return stock_level.quantity_on_hand
        except:
            return Decimal('0')


class StockLevel(BaseModel):
    """
    مستويات المخزون
    Stock Levels per Warehouse
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_levels',
        verbose_name=_('المنتج')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_levels',
        verbose_name=_('المخزن')
    )
    quantity_on_hand = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المتاحة')
    )
    quantity_reserved = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المحجوزة')
    )
    quantity_on_order = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المطلوبة')
    )
    last_movement_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ آخر حركة')
    )
    average_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('متوسط التكلفة')
    )

    class Meta:
        verbose_name = _('مستوى المخزون')
        verbose_name_plural = _('مستويات المخزون')
        unique_together = ['product', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity_on_hand']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity_on_hand}"

    @property
    def available_quantity(self):
        """Get available quantity (on hand - reserved)"""
        return self.quantity_on_hand - self.quantity_reserved

    def update_average_cost(self, new_quantity, new_cost):
        """Update average cost using weighted average method"""
        if self.quantity_on_hand == 0:
            self.average_cost = new_cost
        else:
            total_value = (self.quantity_on_hand * (self.average_cost or Decimal('0'))) + (new_quantity * new_cost)
            total_quantity = self.quantity_on_hand + new_quantity
            self.average_cost = total_value / total_quantity if total_quantity > 0 else Decimal('0')


class StockMovement(AuditableModel):
    """
    حركات المخزون
    Stock Movements
    """
    MOVEMENT_TYPES = [
        ('receipt', _('استلام')),
        ('issue', _('صرف')),
        ('transfer', _('نقل')),
        ('adjustment', _('تسوية')),
        ('return', _('مرتجع')),
        ('damage', _('تالف')),
        ('loss', _('فقدان')),
    ]

    MOVEMENT_REASONS = [
        ('purchase', _('شراء')),
        ('sale', _('بيع')),
        ('production', _('إنتاج')),
        ('consumption', _('استهلاك')),
        ('transfer', _('نقل')),
        ('adjustment', _('تسوية')),
        ('return', _('مرتجع')),
        ('damage', _('تالف')),
        ('expired', _('منتهي الصلاحية')),
        ('theft', _('سرقة')),
        ('other', _('أخرى')),
    ]

    movement_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رقم الحركة'),
        help_text=_('رقم فريد للحركة')
    )
    movement_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('تاريخ الحركة')
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name=_('نوع الحركة')
    )
    movement_reason = models.CharField(
        max_length=20,
        choices=MOVEMENT_REASONS,
        verbose_name=_('سبب الحركة')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name=_('المنتج')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name=_('المخزن')
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('الكمية')
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('تكلفة الوحدة')
    )
    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('إجمالي التكلفة')
    )
    
    # For transfers
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='incoming_transfers',
        verbose_name=_('المخزن المستقبل')
    )
    
    # Reference documents
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('نوع المرجع'),
        help_text=_('نوع المستند المرجعي')
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('معرف المرجع'),
        help_text=_('معرف المستند المرجعي')
    )
    
    # Batch/Serial tracking
    batch_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('رقم الدفعة')
    )
    serial_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('الرقم التسلسلي')
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ انتهاء الصلاحية')
    )
    
    # Balance after movement
    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('الرصيد بعد الحركة')
    )

    class Meta:
        verbose_name = _('حركة مخزون')
        verbose_name_plural = _('حركات المخزون')
        ordering = ['-movement_date', '-created_at']
        indexes = [
            models.Index(fields=['movement_date', 'product']),
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['movement_type', 'movement_date']),
        ]

    def __str__(self):
        return f"{self.movement_number} - {self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculate total cost if not provided
        if self.unit_cost and not self.total_cost:
            self.total_cost = self.quantity * self.unit_cost
        
        # Generate movement number if not provided
        if not self.movement_number:
            self.movement_number = self.generate_movement_number()
        
        super().save(*args, **kwargs)
        
        # Update stock levels after saving
        self.update_stock_levels()

    def generate_movement_number(self):
        """Generate unique movement number"""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m%d')
        count = StockMovement.objects.filter(
            movement_date__date=timezone.now().date()
        ).count() + 1
        return f"MOV-{date_str}-{count:04d}"

    def update_stock_levels(self):
        """Update stock levels based on movement"""
        stock_level, created = StockLevel.objects.get_or_create(
            product=self.product,
            warehouse=self.warehouse,
            defaults={'quantity_on_hand': Decimal('0')}
        )
        
        # Update quantity based on movement type
        if self.movement_type in ['receipt', 'return']:
            stock_level.quantity_on_hand += self.quantity
            if self.unit_cost:
                stock_level.update_average_cost(self.quantity, self.unit_cost)
        elif self.movement_type in ['issue', 'damage', 'loss']:
            stock_level.quantity_on_hand -= self.quantity
        elif self.movement_type == 'transfer':
            # Decrease from source warehouse
            stock_level.quantity_on_hand -= self.quantity
            
            # Increase in destination warehouse
            if self.destination_warehouse:
                dest_stock, created = StockLevel.objects.get_or_create(
                    product=self.product,
                    warehouse=self.destination_warehouse,
                    defaults={'quantity_on_hand': Decimal('0')}
                )
                dest_stock.quantity_on_hand += self.quantity
                if self.unit_cost:
                    dest_stock.update_average_cost(self.quantity, self.unit_cost)
                dest_stock.last_movement_date = self.movement_date
                dest_stock.save()
        elif self.movement_type == 'adjustment':
            # For adjustments, the quantity represents the new balance
            stock_level.quantity_on_hand = self.quantity
        
        # Update last movement date and balance
        stock_level.last_movement_date = self.movement_date
        self.balance_after = stock_level.quantity_on_hand
        stock_level.save()


class StockTake(AuditableModel):
    """
    جرد المخزون
    Stock Take/Physical Inventory
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]

    stock_take_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رقم الجرد')
    )
    stock_take_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ الجرد')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='stock_takes',
        verbose_name=_('المخزن')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('الحالة')
    )
    conducted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='conducted_stock_takes',
        verbose_name=_('أجراه')
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_stock_takes',
        verbose_name=_('اعتمده')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الاعتماد')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف')
    )

    class Meta:
        verbose_name = _('جرد مخزون')
        verbose_name_plural = _('جرد المخزون')
        ordering = ['-stock_take_date']

    def __str__(self):
        return f"{self.stock_take_number} - {self.warehouse.name}"

    def complete_stock_take(self, user):
        """Complete stock take and create adjustments"""
        if self.status != 'in_progress':
            raise ValidationError(_('يمكن إكمال الجرد فقط إذا كان قيد التنفيذ'))
        
        # Create adjustment movements for differences
        for item in self.items.all():
            if item.variance_quantity != 0:
                movement_type = 'adjustment'
                StockMovement.objects.create(
                    movement_type=movement_type,
                    movement_reason='adjustment',
                    product=item.product,
                    warehouse=self.warehouse,
                    quantity=abs(item.variance_quantity),
                    reference_type='stock_take',
                    reference_id=str(self.id),
                    notes=f"تسوية جرد - {self.stock_take_number}",
                    created_by=user
                )
        
        self.status = 'completed'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()


class StockTakeItem(BaseModel):
    """
    عناصر جرد المخزون
    Stock Take Items
    """
    stock_take = models.ForeignKey(
        StockTake,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('الجرد')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('المنتج')
    )
    system_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name=_('الكمية في النظام')
    )
    counted_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('الكمية المعدودة')
    )
    variance_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name=_('فرق الكمية')
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('تكلفة الوحدة')
    )
    variance_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name=_('قيمة الفرق')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )

    class Meta:
        verbose_name = _('عنصر جرد المخزون')
        verbose_name_plural = _('عناصر جرد المخزون')
        unique_together = ['stock_take', 'product']

    def __str__(self):
        return f"{self.stock_take.stock_take_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        # Calculate variance
        if self.counted_quantity is not None:
            self.variance_quantity = self.counted_quantity - self.system_quantity
            if self.unit_cost:
                self.variance_value = self.variance_quantity * self.unit_cost
        
        super().save(*args, **kwargs)