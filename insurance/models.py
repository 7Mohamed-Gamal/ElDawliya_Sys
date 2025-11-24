from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from employees.models import Employee


class HealthInsuranceProvider(models.Model):
    """مقدمي خدمات التأمين الصحي المحسن"""
    provider_id = models.AutoField(primary_key=True, db_column='ProviderID')
    provider_name = models.CharField(max_length=200, db_column='ProviderName', verbose_name='اسم مقدم الخدمة')
    provider_code = models.CharField(max_length=20, unique=True, verbose_name='رمز مقدم الخدمة', null=True, blank=True)
    contact_no = models.CharField(max_length=50, db_column='ContactNo', blank=True, null=True, verbose_name='رقم الاتصال')
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name='الشخص المسؤول')
    email = models.EmailField(blank=True, null=True, verbose_name='البريد الإلكتروني')
    address = models.TextField(blank=True, null=True, verbose_name='العنوان')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'HealthInsuranceProviders'
        verbose_name = 'مزود تأمين صحي'
        verbose_name_plural = 'مزودو التأمين الصحي'
        ordering = ['provider_name']

    def __str__(self):
        """__str__ function"""
        return self.provider_name

    def clean(self):
        """clean function"""
        if self.provider_code:
            self.provider_code = self.provider_code.upper()


class EmployeeHealthInsurance(models.Model):
    """تأمين الموظفين الصحي المحسن"""
    INSURANCE_STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'معلق'),
        ('expired', 'منتهي الصلاحية'),
    ]

    INSURANCE_TYPE_CHOICES = [
        ('basic', 'أساسي'),
        ('comprehensive', 'شامل'),
        ('premium', 'مميز'),
    ]

    ins_id = models.AutoField(primary_key=True, db_column='InsID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    provider = models.ForeignKey(HealthInsuranceProvider, on_delete=models.PROTECT, db_column='ProviderID',
                                blank=True, null=True, verbose_name='مقدم الخدمة')
    policy_no = models.CharField(max_length=100, db_column='PolicyNo', blank=True, null=True, verbose_name='رقم البوليصة')
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES, default='basic', verbose_name='نوع التأمين')
    status = models.CharField(max_length=20, choices=INSURANCE_STATUS_CHOICES, default='active', verbose_name='الحالة')
    start_date = models.DateField(db_column='StartDate', blank=True, null=True, verbose_name='تاريخ البداية')
    end_date = models.DateField(db_column='EndDate', blank=True, null=True, verbose_name='تاريخ النهاية')
    premium = models.DecimalField(max_digits=18, decimal_places=2, db_column='Premium', blank=True, null=True, verbose_name='القسط')
    dependents = models.IntegerField(db_column='Dependents', default=0, verbose_name='عدد المعالين')
    coverage_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name='مبلغ التغطية')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeHealthInsurance'
        verbose_name = 'تأمين صحي للموظف'
        verbose_name_plural = 'تأمينات صحية للموظفين'
        ordering = ['-start_date']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp} - {self.provider} - {self.policy_no}"

    def clean(self):
        """clean function"""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('تاريخ البداية يجب أن يكون قبل تاريخ النهاية')

    @property
    def is_active(self):
        """Check if insurance is currently active"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return True

    @property
    def days_until_expiry(self):
        """Calculate days until insurance expires"""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None


class EmployeeSocialInsurance(models.Model):
    """تأمين الموظفين الاجتماعي المحسن (GOSI)"""
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'معلق'),
        ('terminated', 'منتهي'),
    ]

    social_id = models.AutoField(primary_key=True, db_column='SocialID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    gosi_no = models.CharField(max_length=50, db_column='GosiNo', blank=True, null=True, verbose_name='رقم التأمينات الاجتماعية')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    start_date = models.DateField(db_column='StartDate', blank=True, null=True, verbose_name='تاريخ البداية')
    end_date = models.DateField(db_column='EndDate', blank=True, null=True, verbose_name='تاريخ النهاية')
    contribution = models.DecimalField(max_digits=18, decimal_places=2, db_column='Contribution',
                                     blank=True, null=True, verbose_name='المساهمة الشهرية')
    employer_contribution = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True,
                                              verbose_name='مساهمة صاحب العمل')
    employee_contribution = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True,
                                              verbose_name='مساهمة الموظف')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeSocialInsurance'
        verbose_name = 'تأمين اجتماعي (GOSI)'
        verbose_name_plural = 'تأمينات اجتماعية للموظفين'
        ordering = ['-start_date']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp} - GOSI: {self.gosi_no}"

    def clean(self):
        """clean function"""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('تاريخ البداية يجب أن يكون قبل تاريخ النهاية')

    @property
    def is_active(self):
        """Check if social insurance is currently active"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return True

    @property
    def total_contribution(self):
        """Calculate total monthly contribution"""
        employer = self.employer_contribution or 0
        employee = self.employee_contribution or 0
        return employer + employee

# Create your models here.
