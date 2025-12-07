"""
نماذج المشتريات المحسنة والموحدة
Enhanced and Unified Procurement Models
"""
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from .base import BaseModel, AuditableModel, SoftDeleteModel
from .inventory import Product, Supplier, Warehouse


class PurchaseOrder(AuditableModel):
    """
    أوامر الشراء
    Purchase Orders
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('pending_approval', _('في انتظار الموافقة')),
        ('approved', _('معتمد')),
        ('sent_to_supplier', _('مرسل للمورد')),
        ('partially_received', _('مستلم جزئياً')),
        ('fully_received', _('مستلم بالكامل')),
        ('cancelled', _('ملغي')),
        ('closed', _('مغلق')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('normal', _('عادية')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]

    po_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رقم أمر الشراء'),
        help_text=_('رقم فريد لأمر الشراء')
    )
    po_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ أمر الشراء')
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name=_('المورد')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name=_('المخزن المستقبل')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('الحالة')
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name=_('الأولوية')
    )

    # Dates
    expected_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ التسليم المتوقع')
    )
    actual_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ التسليم الفعلي')
    )

    # Financial
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('المجموع الفرعي')
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name=_('معدل الضريبة (%)')
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('مبلغ الضريبة')
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('مبلغ الخصم')
    )
    shipping_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('تكلفة الشحن')
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('المبلغ الإجمالي')
    )

    # Approval workflow
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='requested_purchase_orders',
        verbose_name=_('طلب بواسطة')
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_orders',
        verbose_name=_('اعتمد بواسطة')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الاعتماد')
    )

    # Additional information
    terms_and_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الشروط والأحكام')
    )
    delivery_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('تعليمات التسليم')
    )
    internal_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات داخلية')
    )

    # Reference to purchase request
    purchase_request = models.ForeignKey(
        'PurchaseRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders',
        verbose_name=_('طلب الشراء المرجعي')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('أمر شراء')
        verbose_name_plural = _('أوامر الشراء')
        ordering = ['-po_date', '-created_at']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['supplier', 'status']),
            models.Index(fields=['po_date', 'status']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.po_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        """save function"""
        # Generate PO number if not provided
        if not self.po_number:
            self.po_number = self.generate_po_number()

        # Calculate totals
        self.calculate_totals()

        super().save(*args, **kwargs)

    def generate_po_number(self):
        """Generate unique PO number"""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m')
        count = PurchaseOrder.objects.filter(
            po_date__year=timezone.now().year,
            po_date__month=timezone.now().month
        ).count() + 1
        return f"PO-{date_str}-{count:04d}"

    def calculate_totals(self):
        """Calculate order totals"""
        # Calculate subtotal from line items
        self.subtotal = sum(item.line_total for item in self.line_items.all())

        # Calculate tax
        self.tax_amount = (self.subtotal * self.tax_rate) / 100

        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount

    def approve(self, user):
        """Approve purchase order"""
        if self.status != 'pending_approval':
            raise ValidationError(_('يمكن اعتماد أمر الشراء فقط إذا كان في انتظار الموافقة'))

        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def send_to_supplier(self, user):
        """Send PO to supplier"""
        if self.status != 'approved':
            raise ValidationError(_('يمكن إرسال أمر الشراء فقط بعد اعتماده'))

        self.status = 'sent_to_supplier'
        self.save()

    def cancel(self, user, reason=None):
        """Cancel purchase order"""
        if self.status in ['fully_received', 'closed', 'cancelled']:
            raise ValidationError(_('لا يمكن إلغاء أمر الشراء في هذه الحالة'))

        self.status = 'cancelled'
        if reason:
            self.internal_notes = f"{self.internal_notes or ''}\nألغي بواسطة {user.username}: {reason}"
        self.save()

    @property
    def is_overdue(self):
        """Check if PO is overdue"""
        if not self.expected_delivery_date:
            return False
        return timezone.now().date() > self.expected_delivery_date and self.status not in ['fully_received', 'closed', 'cancelled']

    @property
    def received_percentage(self):
        """Calculate received percentage"""
        total_ordered = sum(item.quantity_ordered for item in self.line_items.all())
        total_received = sum(item.quantity_received for item in self.line_items.all())

        if total_ordered == 0:
            return 0
        return (total_received / total_ordered) * 100

    def update_status_based_on_receipts(self):
        """Update PO status based on receipt status"""
        received_percentage = self.received_percentage

        if received_percentage == 0:
            # No items received yet
            if self.status == 'partially_received':
                self.status = 'sent_to_supplier'
        elif received_percentage == 100:
            # All items received
            self.status = 'fully_received'
            self.actual_delivery_date = timezone.now().date()
        else:
            # Partially received
            self.status = 'partially_received'

        self.save()


class PurchaseOrderLineItem(BaseModel):
    """
    عناصر أمر الشراء
    Purchase Order Line Items
    """
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='line_items',
        verbose_name=_('أمر الشراء')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_order_items',
        verbose_name=_('المنتج')
    )
    quantity_ordered = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('الكمية المطلوبة')
    )
    quantity_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المستلمة')
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر الوحدة')
    )
    line_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('إجمالي السطر')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('الوصف')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('عنصر أمر الشراء')
        verbose_name_plural = _('عناصر أوامر الشراء')
        unique_together = ['purchase_order', 'product']

    def __str__(self):
        """__str__ function"""
        return f"{self.purchase_order.po_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        """save function"""
        # Calculate line total
        self.line_total = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)

        # Update PO totals
        self.purchase_order.calculate_totals()
        self.purchase_order.save()

    @property
    def quantity_pending(self):
        """Get pending quantity"""
        return self.quantity_ordered - self.quantity_received

    @property
    def is_fully_received(self):
        """Check if line item is fully received"""
        return self.quantity_received >= self.quantity_ordered


class PurchaseRequest(AuditableModel):
    """
    طلبات الشراء
    Purchase Requests
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مقدم')),
        ('under_review', _('قيد المراجعة')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
        ('partially_ordered', _('مطلوب جزئياً')),
        ('fully_ordered', _('مطلوب بالكامل')),
        ('cancelled', _('ملغي')),
    ]

    URGENCY_CHOICES = [
        ('low', _('منخفضة')),
        ('normal', _('عادية')),
        ('high', _('عالية')),
        ('critical', _('حرجة')),
    ]

    pr_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رقم طلب الشراء')
    )
    pr_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ الطلب')
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='purchase_requests',
        verbose_name=_('طلب بواسطة')
    )
    # Temporarily disabled until HR app is restored
    # department = models.ForeignKey(
    #     'hr.Department',
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name='purchase_requests',
    #     verbose_name=_('القسم')
    # )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('الحالة')
    )
    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
        default='normal',
        verbose_name=_('درجة الإلحاح')
    )
    required_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('التاريخ المطلوب')
    )
    justification = models.TextField(
        verbose_name=_('المبرر'),
        help_text=_('مبرر طلب الشراء')
    )

    # Approval workflow
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_purchase_requests',
        verbose_name=_('راجعه')
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ المراجعة')
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_requests',
        verbose_name=_('اعتمده')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الاعتماد')
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('سبب الرفض')
    )

    # Budget information
    estimated_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('إجمالي تقديري')
    )
    budget_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('رمز الميزانية')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('طلب شراء')
        verbose_name_plural = _('طلبات الشراء')
        ordering = ['-pr_date', '-created_at']
        indexes = [
            models.Index(fields=['pr_number']),
            models.Index(fields=['status', 'pr_date']),
            models.Index(fields=['requested_by', 'status']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.pr_number} - {self.requested_by.get_full_name()}"

    def save(self, *args, **kwargs):
        """save function"""
        # Generate PR number if not provided
        if not self.pr_number:
            self.pr_number = self.generate_pr_number()

        super().save(*args, **kwargs)

    def generate_pr_number(self):
        """Generate unique PR number"""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m')
        count = PurchaseRequest.objects.filter(
            pr_date__year=timezone.now().year,
            pr_date__month=timezone.now().month
        ).count() + 1
        return f"PR-{date_str}-{count:04d}"

    def submit(self):
        """Submit purchase request for review"""
        if self.status != 'draft':
            raise ValidationError(_('يمكن تقديم طلب الشراء فقط إذا كان مسودة'))

        self.status = 'submitted'
        self.save()

    def approve(self, user):
        """Approve purchase request"""
        if self.status not in ['submitted', 'under_review']:
            raise ValidationError(_('يمكن اعتماد طلب الشراء فقط إذا كان مقدماً أو قيد المراجعة'))

        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def reject(self, user, reason):
        """Reject purchase request"""
        if self.status not in ['submitted', 'under_review']:
            raise ValidationError(_('يمكن رفض طلب الشراء فقط إذا كان مقدماً أو قيد المراجعة'))

        self.status = 'rejected'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save()

    @property
    def is_overdue(self):
        """Check if request is overdue"""
        if not self.required_date:
            return False
        return timezone.now().date() > self.required_date and self.status not in ['fully_ordered', 'cancelled', 'rejected']


class PurchaseRequestLineItem(BaseModel):
    """
    عناصر طلب الشراء
    Purchase Request Line Items
    """
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='line_items',
        verbose_name=_('طلب الشراء')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='purchase_request_items',
        verbose_name=_('المنتج')
    )
    # For non-catalog items
    item_description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('وصف الصنف'),
        help_text=_('للأصناف غير المدرجة في الكتالوج')
    )
    quantity_requested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('الكمية المطلوبة')
    )
    quantity_ordered = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المطلوبة')
    )
    estimated_unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('السعر التقديري للوحدة')
    )
    estimated_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الإجمالي التقديري')
    )
    preferred_supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_request_items',
        verbose_name=_('المورد المفضل')
    )
    urgency_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('سبب الإلحاح')
    )
    specifications = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('المواصفات المطلوبة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('عنصر طلب الشراء')
        verbose_name_plural = _('عناصر طلبات الشراء')

    def __str__(self):
        """__str__ function"""
        item_name = self.product.name if self.product else self.item_description
        return f"{self.purchase_request.pr_number} - {item_name}"

    def save(self, *args, **kwargs):
        """save function"""
        # Calculate estimated total
        if self.estimated_unit_price:
            self.estimated_total = self.quantity_requested * self.estimated_unit_price

        super().save(*args, **kwargs)

    @property
    def item_name(self):
        """Get item name (product name or description)"""
        return self.product.name if self.product else self.item_description

    @property
    def quantity_pending(self):
        """Get pending quantity"""
        return self.quantity_requested - self.quantity_ordered


class GoodsReceipt(AuditableModel):
    """
    إيصالات استلام البضائع
    Goods Receipt Notes
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]

    grn_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رقم إيصال الاستلام')
    )
    grn_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ الاستلام')
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.PROTECT,
        related_name='goods_receipts',
        verbose_name=_('أمر الشراء')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='goods_receipts',
        verbose_name=_('المخزن')
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='received_goods_receipts',
        verbose_name=_('استلم بواسطة')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('الحالة')
    )
    supplier_invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('رقم فاتورة المورد')
    )
    supplier_invoice_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ فاتورة المورد')
    )
    delivery_note_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('رقم إشعار التسليم')
    )
    vehicle_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('رقم المركبة')
    )
    driver_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('اسم السائق')
    )
    quality_check_passed = models.BooleanField(
        default=True,
        verbose_name=_('اجتاز فحص الجودة')
    )
    quality_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات الجودة')
    )
    general_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات عامة')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('إيصال استلام البضائع')
        verbose_name_plural = _('إيصالات استلام البضائع')
        ordering = ['-grn_date', '-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.grn_number} - {self.purchase_order.po_number}"

    def save(self, *args, **kwargs):
        """save function"""
        # Generate GRN number if not provided
        if not self.grn_number:
            self.grn_number = self.generate_grn_number()

        super().save(*args, **kwargs)

    def generate_grn_number(self):
        """Generate unique GRN number"""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m')
        count = GoodsReceipt.objects.filter(
            grn_date__year=timezone.now().year,
            grn_date__month=timezone.now().month
        ).count() + 1
        return f"GRN-{date_str}-{count:04d}"

    def complete_receipt(self, user):
        """Complete goods receipt and update stock"""
        if self.status != 'draft':
            raise ValidationError(_('يمكن إكمال الاستلام فقط إذا كان مسودة'))

        from .inventory import StockMovement

        # Create stock movements for received items
        for item in self.line_items.all():
            if item.quantity_received > 0:
                StockMovement.objects.create(
                    movement_type='receipt',
                    movement_reason='purchase',
                    product=item.product,
                    warehouse=self.warehouse,
                    quantity=item.quantity_received,
                    unit_cost=item.unit_cost,
                    reference_type='goods_receipt',
                    reference_id=str(self.id),
                    batch_number=item.batch_number,
                    serial_number=item.serial_number,
                    expiry_date=item.expiry_date,
                    created_by=user
                )

                # Update PO line item received quantity
                po_item = item.purchase_order_line_item
                po_item.quantity_received += item.quantity_received
                po_item.save()

        # Update PO status
        self.purchase_order.update_status_based_on_receipts()

        self.status = 'completed'
        self.save()


class GoodsReceiptLineItem(BaseModel):
    """
    عناصر إيصال استلام البضائع
    Goods Receipt Line Items
    """
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name='line_items',
        verbose_name=_('إيصال الاستلام')
    )
    purchase_order_line_item = models.ForeignKey(
        PurchaseOrderLineItem,
        on_delete=models.PROTECT,
        related_name='receipt_items',
        verbose_name=_('عنصر أمر الشراء')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('المنتج')
    )
    quantity_ordered = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_('الكمية المطلوبة')
    )
    quantity_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المستلمة')
    )
    quantity_rejected = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المرفوضة')
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('تكلفة الوحدة')
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

    # Quality control
    quality_status = models.CharField(
        max_length=20,
        choices=[
            ('passed', _('مقبول')),
            ('failed', _('مرفوض')),
            ('pending', _('قيد الفحص')),
        ],
        default='passed',
        verbose_name=_('حالة الجودة')
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('سبب الرفض')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('عنصر إيصال استلام البضائع')
        verbose_name_plural = _('عناصر إيصالات استلام البضائع')

    def __str__(self):
        """__str__ function"""
        return f"{self.goods_receipt.grn_number} - {self.product.name}"

    def clean(self):
        """clean function"""
        if self.quantity_received + self.quantity_rejected > self.quantity_ordered:
            raise ValidationError(_('مجموع الكمية المستلمة والمرفوضة لا يمكن أن يتجاوز الكمية المطلوبة'))


class SupplierQuotation(AuditableModel):
    """
    عروض أسعار الموردين
    Supplier Quotations
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مقدم')),
        ('under_review', _('قيد المراجعة')),
        ('accepted', _('مقبول')),
        ('rejected', _('مرفوض')),
        ('expired', _('منتهي الصلاحية')),
    ]

    quotation_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('رقم عرض السعر')
    )
    quotation_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ العرض')
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='quotations',
        verbose_name=_('المورد')
    )
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='quotations',
        verbose_name=_('طلب الشراء')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('الحالة')
    )
    valid_until = models.DateField(
        verbose_name=_('صالح حتى')
    )
    currency = models.CharField(
        max_length=3,
        default='SAR',
        verbose_name=_('العملة')
    )
    payment_terms = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('شروط الدفع')
    )
    delivery_terms = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('شروط التسليم')
    )
    delivery_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('مدة التسليم (أيام)')
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('المبلغ الإجمالي')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )

    # Evaluation
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluated_quotations',
        verbose_name=_('قيم بواسطة')
    )
    evaluation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name=_('نقاط التقييم')
    )
    evaluation_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات التقييم')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('عرض سعر المورد')
        verbose_name_plural = _('عروض أسعار الموردين')
        ordering = ['-quotation_date']

    def __str__(self):
        """__str__ function"""
        return f"{self.quotation_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        """save function"""
        # Generate quotation number if not provided
        if not self.quotation_number:
            self.quotation_number = self.generate_quotation_number()

        super().save(*args, **kwargs)

    def generate_quotation_number(self):
        """Generate unique quotation number"""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m')
        count = SupplierQuotation.objects.filter(
            quotation_date__year=timezone.now().year,
            quotation_date__month=timezone.now().month
        ).count() + 1
        return f"QUO-{date_str}-{count:04d}"

    @property
    def is_expired(self):
        """Check if quotation is expired"""
        return timezone.now().date() > self.valid_until

    def accept(self, user):
        """Accept quotation"""
        if self.status != 'under_review':
            raise ValidationError(_('يمكن قبول عرض السعر فقط إذا كان قيد المراجعة'))

        self.status = 'accepted'
        self.evaluated_by = user
        self.save()

    def reject(self, user, reason=None):
        """Reject quotation"""
        if self.status not in ['submitted', 'under_review']:
            raise ValidationError(_('يمكن رفض عرض السعر فقط إذا كان مقدماً أو قيد المراجعة'))

        self.status = 'rejected'
        self.evaluated_by = user
        if reason:
            self.evaluation_notes = reason
        self.save()


class SupplierQuotationLineItem(BaseModel):
    """
    عناصر عرض سعر المورد
    Supplier Quotation Line Items
    """
    quotation = models.ForeignKey(
        SupplierQuotation,
        on_delete=models.CASCADE,
        related_name='line_items',
        verbose_name=_('عرض السعر')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('المنتج')
    )
    item_description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('وصف الصنف')
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('الكمية')
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر الوحدة')
    )
    line_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('إجمالي السطر')
    )
    specifications = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('المواصفات')
    )
    delivery_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('مدة التسليم (أيام)')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )

    class Meta:
        """Meta class"""
        verbose_name = _('عنصر عرض سعر المورد')
        verbose_name_plural = _('عناصر عروض أسعار الموردين')

    def __str__(self):
        """__str__ function"""
        item_name = self.product.name if self.product else self.item_description
        return f"{self.quotation.quotation_number} - {item_name}"

    def save(self, *args, **kwargs):
        """save function"""
        # Calculate line total
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def item_name(self):
        """Get item name (product name or description)"""
        return self.product.name if self.product else self.item_description
