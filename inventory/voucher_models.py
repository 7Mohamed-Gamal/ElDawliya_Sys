from django.db import models
from django.utils.translation import gettext_lazy as _

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
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers", verbose_name=_("المورد"))
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers", verbose_name=_("القسم"))
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers", verbose_name=_("العميل"))
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
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="voucher_items", verbose_name=_("الصنف"))
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