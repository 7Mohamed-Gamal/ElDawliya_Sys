from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("اسم التصنيف"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("تصنيف")
        verbose_name_plural = _("التصنيفات")

class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("اسم الوحدة"))
    symbol = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("رمز الوحدة"))

    def __str__(self):
        if self.symbol:
            return f"{self.name} ({self.symbol})"
        return self.name

    class Meta:
        verbose_name = _("وحدة قياس")
        verbose_name_plural = _("وحدات القياس")

class Product(models.Model):
    product_id = models.CharField(max_length=100, primary_key=True, verbose_name=_("رقم الصنف"))
    name = models.CharField(max_length=100, verbose_name=_("اسم الصنف"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name=_("التصنيف"))
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name=_("وحدة القياس"))
    initial_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الرصيد الافتتاحي"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الرصيد الحالي"))
    minimum_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الحد الأدنى"))
    maximum_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الحد الأقصى"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("سعر الوحدة"))
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("الموقع"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name=_("الصورة"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    def __str__(self):
        return f"{self.product_id} - {self.name}"

    class Meta:
        verbose_name = _("صنف")
        verbose_name_plural = _("الأصناف")
        permissions = [
            ("view_dashboard", "Can view inventory dashboard"),
            ("view_stockreport", "Can view stock reports"),
            ("export_stockreport", "Can export stock reports"),
            ("view_settings", "Can view inventory settings"),
            ("view_department", "Can view inventory departments"),
            ("view_purchaserequest", "Can view purchase requests"),
            ("view_voucher", "Can view vouchers"),
        ]

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("اسم المورد"))
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("الشخص المسؤول"))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهاتف"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("البريد الإلكتروني"))
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("مورد")
        verbose_name_plural = _("الموردين")

class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("اسم العميل"))
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("الشخص المسؤول"))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهاتف"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("البريد الإلكتروني"))
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("عميل")
        verbose_name_plural = _("العملاء")

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("اسم القسم"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    # حقول افتراضية للعرض فقط (لن يتم تخزينها في قاعدة البيانات)
    _code = None
    _manager = None
    _location = None
    _notes = None

    def __str__(self):
        return self.name

    @property
    def code(self):
        if not self._code:
            # إنشاء كود افتراضي للقسم
            self._code = f'DEPT-{self.id or 0:04d}'
        return self._code

    @property
    def manager(self):
        return self._manager or ''

    @property
    def location(self):
        return self._location or ''

    @property
    def notes(self):
        return self._notes or ''

    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")

class Voucher(models.Model):
    VOUCHER_TYPES = (
        ('إذن اضافة', 'إذن اضافة'),
        ('إذن صرف', 'إذن صرف'),
        ('اذن مرتجع عميل', 'اذن مرتجع عميل'),
        ('إذن مرتجع مورد', 'إذن مرتجع مورد'),
    )

    voucher_number = models.CharField(max_length=100, primary_key=True, verbose_name=_("رقم الإذن"))
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPES, verbose_name=_("نوع الإذن"))
    date = models.DateField(verbose_name=_("تاريخ الإذن"))
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers", verbose_name=_("المورد"))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers", verbose_name=_("القسم"))
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers", verbose_name=_("العميل"))
    supplier_voucher_number = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("رقم إذن المورد"))
    recipient = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("المستلم"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    def __str__(self):
        return f"{self.voucher_number} - {self.get_voucher_type_display()}"

    @property
    def items_count(self):
        return self.items.count()

    class Meta:
        verbose_name = _("إذن")
        verbose_name_plural = _("الأذونات")

class VoucherItem(models.Model):
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name="items", verbose_name=_("الإذن"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="voucher_items", verbose_name=_("الصنف"))
    quantity_added = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("الكمية المضافة"))
    quantity_disbursed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("الكمية المنصرفة"))
    machine = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("الماكينة"))
    machine_unit = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("وحدة الماكينة"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("سعر الوحدة"))

    @property
    def total_price(self):
        if self.quantity_added:
            return self.quantity_added * self.unit_price
        elif self.quantity_disbursed:
            return self.quantity_disbursed * self.unit_price
        return 0

    def __str__(self):
        return f"{self.voucher.voucher_number} - {self.product.name}"

    class Meta:
        verbose_name = _("عنصر الإذن")
        verbose_name_plural = _("عناصر الإذن")

class PurchaseRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchase_requests", verbose_name=_("الصنف"))
    requested_date = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الطلب"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name=_("الحالة"))
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الموافقة"))
    approved_by = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("تمت الموافقة بواسطة"))

    class Meta:
        verbose_name = _("طلب شراء")
        verbose_name_plural = _("طلبات الشراء")

class LocalSystemSettings(models.Model):
    # معلومات الشركة
    company_name = models.CharField(max_length=100, verbose_name=_("اسم الشركة"))
    company_logo = models.ImageField(upload_to="settings/", blank=True, null=True, verbose_name=_("شعار الشركة"))
    company_address = models.TextField(blank=True, null=True, verbose_name=_("عنوان الشركة"))
    company_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم هاتف الشركة"))
    company_email = models.EmailField(blank=True, null=True, verbose_name=_("البريد الإلكتروني للشركة"))

    # إعدادات واجهة المستخدم
    primary_color = models.CharField(max_length=20, default='#3f51b5', verbose_name=_("اللون الأساسي"))
    secondary_color = models.CharField(max_length=20, default='#ff4081', verbose_name=_("اللون الثانوي"))
    items_per_page = models.IntegerField(default=25, verbose_name=_("عدد العناصر في الصفحة"))
    compact_tables = models.BooleanField(default=False, verbose_name=_("وضع العرض المضغوط"))
    currency = models.CharField(max_length=10, default='EGP', verbose_name=_("العملة"))

    # إعدادات المخزون
    enable_stock_alerts = models.BooleanField(default=True, verbose_name=_("تفعيل تنبيهات المخزون"))
    default_min_stock_percentage = models.IntegerField(default=20, verbose_name=_("نسبة الحد الأدنى الافتراضية"))

    # إعدادات الفواتير
    invoice_in_prefix = models.CharField(max_length=10, default='IN-', verbose_name=_("بادئة أرقام فواتير التوريد"))
    invoice_out_prefix = models.CharField(max_length=10, default='OUT-', verbose_name=_("بادئة أرقام فواتير الصرف"))
    prevent_editing_completed_invoices = models.BooleanField(default=True, verbose_name=_("منع تعديل الفواتير المكتملة"))

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = _("إعدادات النظام المحلية")
        verbose_name_plural = _("إعدادات النظام المحلية")
