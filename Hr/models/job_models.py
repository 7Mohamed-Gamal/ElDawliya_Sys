from django.db import models
from django.utils.translation import gettext_lazy as _
from Hr.models.department_models import Department

class Job(models.Model):
    jop_code = models.IntegerField(  # اسم الحقل: jop_code (بالإنجليزية o)
        db_column='Jop_Code', 
        primary_key=True,
        verbose_name=_("رمز الوظيفة")
    )
    jop_name = models.CharField(
        db_column='Jop_Name',
        max_length=50,
        verbose_name=_("اسم الوظيفة")
    )
    department = models.ForeignKey(
        Department,
        db_column='Dept_Code',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )

    def __str__(self):
        return self.jop_name or ''

    class Meta:
        managed = True
        db_table = 'Tbl_Jop'
        verbose_name = _("الوظيفة")
        verbose_name_plural = _("الوظائف")
