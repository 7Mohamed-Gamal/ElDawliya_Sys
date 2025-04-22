from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.car_models import Car

class PickupPoint(models.Model):
    """
    Modelo para puntos de recogida de empleados por vehículos de transporte
    """
    name = models.CharField(max_length=100, verbose_name=_('اسم النقطة'))
    address = models.CharField(max_length=255, verbose_name=_('العنوان'))
    coordinates = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الإحداثيات'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='pickup_points', verbose_name=_('السيارة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    def __str__(self):
        return f"{self.name} - {self.car}"

    class Meta:
        verbose_name = _('نقطة تجمع')
        verbose_name_plural = _('نقاط التجمع')
        db_table = 'Hr_PickupPoint'
        managed = True
