from django.db import models
from employees.models import Employee


class HealthInsuranceProvider(models.Model):
    provider_id = models.AutoField(primary_key=True, db_column='ProviderID')
    provider_name = models.CharField(max_length=150, db_column='ProviderName')
    contact_no = models.CharField(max_length=50, db_column='ContactNo', blank=True, null=True)

    class Meta:
        db_table = 'HealthInsuranceProviders'
        verbose_name = 'مزود تأمين صحي'
        verbose_name_plural = 'مزودو التأمين الصحي'

    def __str__(self):
        return self.provider_name


class EmployeeHealthInsurance(models.Model):
    ins_id = models.AutoField(primary_key=True, db_column='InsID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    provider = models.ForeignKey(HealthInsuranceProvider, on_delete=models.PROTECT, db_column='ProviderID', blank=True, null=True)
    policy_no = models.CharField(max_length=100, db_column='PolicyNo', blank=True, null=True)
    start_date = models.DateField(db_column='StartDate', blank=True, null=True)
    end_date = models.DateField(db_column='EndDate', blank=True, null=True)
    premium = models.DecimalField(max_digits=18, decimal_places=2, db_column='Premium', blank=True, null=True)
    dependents = models.IntegerField(db_column='Dependents', default=0)

    class Meta:
        db_table = 'EmployeeHealthInsurance'
        verbose_name = 'تأمين صحي للموظف'
        verbose_name_plural = 'تأمينات صحية للموظفين'


class EmployeeSocialInsurance(models.Model):
    social_id = models.AutoField(primary_key=True, db_column='SocialID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    gosi_no = models.CharField(max_length=50, db_column='GosiNo', blank=True, null=True)
    start_date = models.DateField(db_column='StartDate', blank=True, null=True)
    end_date = models.DateField(db_column='EndDate', blank=True, null=True)
    contribution = models.DecimalField(max_digits=18, decimal_places=2, db_column='Contribution', blank=True, null=True)

    class Meta:
        db_table = 'EmployeeSocialInsurance'
        verbose_name = 'تأمين اجتماعي (GOSI)'
        verbose_name_plural = 'تأمينات اجتماعية للموظفين'

# Create your models here.
