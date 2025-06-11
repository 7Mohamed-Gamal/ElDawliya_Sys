from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from inventory.models import TblProducts

User = get_user_model()

class Vendor(models.Model):
    """نموذج الموردين"""
    name = models.CharField(max_length=100, verbose_name=_('اسم المورد'))
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('جهة الاتصال'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهاتف'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('مورد')
        verbose_name_plural = _('الموردين')
        ordering = ['name']

class PurchaseRequest(models.Model):
    """نموذج طلبات الشراء"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
        ('completed', 'مكتمل'),
    ]

    request_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الطلب'))
    request_date = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الطلب'))
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_requests', verbose_name=_('مقدم الطلب'))
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_requests', verbose_name=_('المورد'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('حالة الطلب'))
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchase_requests', verbose_name=_('تمت الموافقة بواسطة'))
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الموافقة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))

    def __str__(self):
        return f"طلب شراء #{self.request_number}"

    class Meta:
        verbose_name = _('طلب شراء')
        verbose_name_plural = _('طلبات الشراء')
        ordering = ['-request_date']

class PurchaseRequestItem(models.Model):
    """نموذج عناصر طلب الشراء"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
        ('transferred', 'تم الترحيل'),
    ]

    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items', verbose_name=_('طلب الشراء'))
    product = models.ForeignKey(TblProducts, on_delete=models.CASCADE, verbose_name=_('الصنف'))
    quantity_requested = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('الكمية المطلوبة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('حالة العنصر'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_requested}"

    class Meta:
        verbose_name = _('عنصر طلب الشراء')
        verbose_name_plural = _('عناصر طلبات الشراء')
        ordering = ['purchase_request', 'created_at']
