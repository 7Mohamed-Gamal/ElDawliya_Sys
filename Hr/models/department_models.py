from django.db import models
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    dept_code = models.IntegerField(primary_key=True, verbose_name=_("رمز القسم"))
    dept_name = models.CharField(max_length=250, verbose_name=_("اسم القسم"))
    manager_id = models.IntegerField(null=True, blank=True, verbose_name=_("كود مدير القسم"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    note = models.TextField(null=True, blank=True, verbose_name=_("ملاحظات"))

    def __str__(self):
        return self.dept_name or ''

    class Meta:
        managed = True
        db_table = 'Tbl_Department'
        verbose_name = _("القسم")
        verbose_name_plural = _("الأقسام")
