from django.db import models
from django.utils.translation import gettext_lazy as _

class Car(models.Model):
    SHIFT_TYPE_CHOICES = [
        ('حضور فقط', 'حضور فقط'),
        ('انصراف فقط', 'انصراف فقط'),
    ]

    car_id = models.IntegerField(primary_key=True, verbose_name=_("رقم السيارة"))
    car_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("اسم السيارة"))
    car_type = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("نوع السيارة"))
    car_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("تكلفة السيارة"))
    car_salary_farda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("تكلفة السيارة (فردة)"))
    supplier = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("المورد"))
    contract_type = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("نوع العقد"))
    car_number = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("رقم السيارة"))
    car_license_expiration_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ انتهاء رخصة السيارة"))
    driver_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("اسم السائق"))
    driver_phone = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("رقم هاتف السائق"))
    driver_license_expiration_date = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ انتهاء رخصة السائق"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    shift_type = models.CharField(max_length=50, choices=SHIFT_TYPE_CHOICES, null=True, blank=True, verbose_name=_("نوع الوردية"))
    contract_type_farada = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("نوع العقد (فردة)"))

    def __str__(self):
        return f"{self.car_name or 'سيارة'} - {self.car_number or self.car_id}"

    class Meta:
        verbose_name = _("السيارة")
        verbose_name_plural = _("السيارات")
        managed = True
        db_table = 'Tbl_Car'
