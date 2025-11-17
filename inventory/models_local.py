"""
Local models for inventory application.
These models are used for the new inventory system.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """نموذج التصنيفات"""
    name = models.CharField(max_length=100, verbose_name=_('اسم التصنيف'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))

    class Meta:
        verbose_name = _('تصنيف')
        verbose_name_plural = _('التصنيفات')

    def __str__(self):
        return self.name


class Unit(models.Model):
    """نموذج وحدات القياس"""
    name = models.CharField(max_length=50, verbose_name=_('اسم الوحدة'))
    symbol = models.CharField(max_length=10, verbose_name=_('الرمز'))

    class Meta:
        verbose_name = _('وحدة قياس')
        verbose_name_plural = _('وحدات القياس')

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Product(models.Model):
    """نموذج المنتجات"""
    product_id = models.CharField(max_length=100, primary_key=True, verbose_name=_('رقم الصنف'))
    name = models.CharField(max_length=200, verbose_name=_('اسم الصنف'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='products', verbose_name=_('التصنيف'))
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='products', verbose_name=_('الوحدة'))
    initial_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                          verbose_name=_('الرصيد الافتتاحي'))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                   verbose_name=_('الكمية الحالية'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                     verbose_name=_('سعر الوحدة'))
    minimum_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                           verbose_name=_('الحد الأدنى'))
    maximum_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                           verbose_name=_('الحد الأقصى'))
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الموقع'))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_('الصورة'))

    class Meta:
        verbose_name = _('صنف')
        verbose_name_plural = _('الأصناف')
        ordering = ['name']

    def __str__(self):
        return f"{self.product_id} - {self.name}"


class Supplier(models.Model):
    """نموذج الموردين"""
    name = models.CharField(max_length=100, verbose_name=_('اسم المورد'))
    contact_person = models.CharField(max_length=100, blank=True, null=True, 
                                     verbose_name=_('الشخص المسؤول'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهاتف'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))

    class Meta:
        verbose_name = _('مورد')
        verbose_name_plural = _('الموردين')

    def __str__(self):
        return self.name


class Customer(models.Model):
    """نموذج العملاء"""
    name = models.CharField(max_length=100, verbose_name=_('اسم العميل'))
    contact_person = models.CharField(max_length=100, blank=True, null=True, 
                                     verbose_name=_('الشخص المسؤول'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهاتف'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))

    class Meta:
        verbose_name = _('عميل')
        verbose_name_plural = _('العملاء')

    def __str__(self):
        return self.name


class Department(models.Model):
    """نموذج الأقسام"""
    name = models.CharField(max_length=100, verbose_name=_('اسم القسم'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))

    class Meta:
        verbose_name = _('قسم')
        verbose_name_plural = _('الأقسام')

    def __str__(self):
        return self.name


class PurchaseRequest(models.Model):
    """نموذج طلبات الشراء"""
    STATUS_CHOICES = (
        ('pending', _('قيد الانتظار')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('completed', _('مكتمل')),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='purchase_requests', verbose_name=_('الصنف'))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('الكمية'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('الحالة'))
    requested_date = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الطلب'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))

    class Meta:
        verbose_name = _('طلب شراء')
        verbose_name_plural = _('طلبات الشراء')

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class LocalSystemSettings(models.Model):
    """نموذج إعدادات النظام المحلية"""
    company_name = models.CharField(max_length=100, verbose_name=_('اسم الشركة'))
    company_logo = models.ImageField(upload_to='settings/', blank=True, null=True,
                                     verbose_name=_('شعار الشركة'))
    company_address = models.TextField(blank=True, null=True, verbose_name=_('عنوان الشركة'))
    company_phone = models.CharField(max_length=20, blank=True, null=True,
                                     verbose_name=_('رقم هاتف الشركة'))
    company_email = models.EmailField(blank=True, null=True,
                                      verbose_name=_('البريد الإلكتروني للشركة'))
    primary_color = models.CharField(max_length=7, default='#007bff',
                                    verbose_name=_('اللون الأساسي'))
    secondary_color = models.CharField(max_length=7, default='#6c757d',
                                      verbose_name=_('اللون الثانوي'))
    items_per_page = models.IntegerField(default=10, verbose_name=_('عدد العناصر في الصفحة'))
    compact_tables = models.BooleanField(default=False, verbose_name=_('جداول مضغوطة'))
    currency = models.CharField(max_length=10, default='EGP', verbose_name=_('العملة'))
    enable_stock_alerts = models.BooleanField(default=True,
                                             verbose_name=_('تفعيل تنبيهات المخزون'))
    default_min_stock_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20,
                                                       verbose_name=_('نسبة الحد الأدنى الافتراضية'))
    invoice_in_prefix = models.CharField(max_length=10, default='IN',
                                        verbose_name=_('بادئة فاتورة الوارد'))
    invoice_out_prefix = models.CharField(max_length=10, default='OUT',
                                         verbose_name=_('بادئة فاتورة الصادر'))
    prevent_editing_completed_invoices = models.BooleanField(default=True,
                                                            verbose_name=_('منع تعديل الفواتير المكتملة'))

    class Meta:
        verbose_name = _('إعدادات النظام المحلية')
        verbose_name_plural = _('إعدادات النظام المحلية')

    def __str__(self):
        return self.company_name


# Import Voucher and VoucherItem from voucher_models
from .voucher_models import Voucher, VoucherItem

__all__ = [
    'Category', 'Unit', 'Product', 'Supplier', 'Customer',
    'Department', 'PurchaseRequest', 'LocalSystemSettings',
    'Voucher', 'VoucherItem'
]

