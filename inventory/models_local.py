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

class Product(models.Model):
    product_id = models.CharField(max_length=100, primary_key=True, verbose_name=_("رقم الصنف"))
    name = models.CharField(max_length=100, verbose_name=_("اسم الصنف"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name=_("التصنيف"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الكمية المتوفرة"))
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

class Invoice(models.Model):
    INVOICE_TYPES = (
        ('إضافة', 'إضافة'),
        ('صرف', 'صرف'),
    )
    
    invoice_number = models.CharField(max_length=100, primary_key=True, verbose_name=_("رقم الفاتورة"))
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPES, verbose_name=_("نوع الفاتورة"))
    date = models.DateField(verbose_name=_("تاريخ الفاتورة"))
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices", verbose_name=_("المورد"))
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices", verbose_name=_("العميل"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))
    
    def __str__(self):
        return f"{self.invoice_number} - {self.get_invoice_type_display()}"
    
    class Meta:
        verbose_name = _("فاتورة")
        verbose_name_plural = _("الفواتير")

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items", verbose_name=_("الفاتورة"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="invoice_items", verbose_name=_("الصنف"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الكمية"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر الوحدة"))
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"
    
    class Meta:
        verbose_name = _("عنصر الفاتورة")
        verbose_name_plural = _("عناصر الفاتورة")

class LocalSystemSettings(models.Model):
    company_name = models.CharField(max_length=100, verbose_name=_("اسم الشركة"))
    company_logo = models.ImageField(upload_to="settings/", blank=True, null=True, verbose_name=_("شعار الشركة"))
    company_address = models.TextField(blank=True, null=True, verbose_name=_("عنوان الشركة"))
    company_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم هاتف الشركة"))
    company_email = models.EmailField(blank=True, null=True, verbose_name=_("البريد الإلكتروني للشركة"))
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = _("إعدادات النظام المحلية")
        verbose_name_plural = _("إعدادات النظام المحلية")