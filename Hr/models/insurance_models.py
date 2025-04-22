from django.db import models
from django.utils.translation import gettext_lazy as _

class JobInsurance(models.Model):
    job_code_insurance = models.IntegerField(
        db_column='job_code_insurance',
        primary_key=True,
        verbose_name=_("رمز وظيفة التأمين")
    )
    job_name_insurance = models.CharField(
        db_column='job_name_insurance',
        max_length=200,
        db_collation='Arabic_CI_AS',
        verbose_name=_("اسم وظيفة التأمين")
    )

    def __str__(self):
        return self.job_name_insurance or ''

    class Meta:
        managed = True
        db_table = 'Tbl_Jop_Name_insurance'
        verbose_name = _("وظيفة التأمين")
        verbose_name_plural = _("وظائف التأمين")
