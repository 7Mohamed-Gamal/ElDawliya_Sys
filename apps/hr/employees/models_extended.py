"""
Extended Employee Models for Comprehensive HR Management
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Employee


# =============================================================================
# HEALTH INSURANCE MODELS
# =============================================================================

class ExtendedHealthInsuranceProvider(models.Model):
    """مقدمي خدمات التأمين الصحي - النسخة الموسعة"""
    provider_id = models.AutoField(primary_key=True, db_column='ProviderID')
    provider_name = models.CharField(max_length=200, db_column='ProviderName', verbose_name='اسم مقدم الخدمة')
    provider_code = models.CharField(max_length=20, unique=True, verbose_name='رمز مقدم الخدمة')
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name='الشخص المسؤول')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='الهاتف')
    email = models.EmailField(blank=True, null=True, verbose_name='البريد الإلكتروني')
    address = models.TextField(blank=True, null=True, verbose_name='العنوان')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'ExtendedHealthInsuranceProviders'
        verbose_name = 'مقدم خدمة التأمين الصحي الموسع'
        verbose_name_plural = 'مقدمي خدمات التأمين الصحي الموسعة'

    def __str__(self):
        """__str__ function"""
        return self.provider_name


class ExtendedEmployeeHealthInsurance(models.Model):
    """تأمين الموظفين الصحي - النسخة الموسعة"""
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
        ('family', 'عائلي'),
    ]

    insurance_id = models.AutoField(primary_key=True, db_column='InsuranceID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID',
                           related_name='extended_health_insurance', verbose_name='الموظف')
    provider = models.ForeignKey(ExtendedHealthInsuranceProvider, on_delete=models.PROTECT, verbose_name='مقدم الخدمة')
    insurance_status = models.CharField(max_length=20, choices=INSURANCE_STATUS_CHOICES, default='active', verbose_name='حالة التأمين')
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES, default='basic', verbose_name='نوع التأمين')
    insurance_number = models.CharField(max_length=100, unique=True, verbose_name='رقم التأمين')
    start_date = models.DateField(verbose_name='تاريخ البداية')
    expiry_date = models.DateField(verbose_name='تاريخ الانتهاء')
    num_dependents = models.IntegerField(default=0, verbose_name='عدد المعالين')
    dependent_names = models.TextField(blank=True, null=True, verbose_name='أسماء المعالين')
    coverage_details = models.TextField(blank=True, null=True, verbose_name='تفاصيل التغطية')
    monthly_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='القسط الشهري')
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مساهمة الموظف')
    company_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مساهمة الشركة')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'ExtendedEmployeeHealthInsurance'
        verbose_name = 'تأمين صحي موسع للموظف'
        verbose_name_plural = 'التأمين الصحي الموسع للموظفين'

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.insurance_number}"

    @property
    def is_active(self):
        """is_active function"""
        return self.insurance_status == 'active' and self.expiry_date >= date.today()

    def clean(self):
        """clean function"""
        if self.start_date and self.expiry_date and self.start_date >= self.expiry_date:
            raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')


# =============================================================================
# SOCIAL INSURANCE MODELS
# =============================================================================

class SocialInsuranceJobTitle(models.Model):
    """مسميات الوظائف في نظام التأمينات الاجتماعية"""
    job_title_id = models.AutoField(primary_key=True, db_column='JobTitleID')
    job_code = models.CharField(max_length=20, unique=True, verbose_name='رمز الوظيفة في التأمينات')
    job_title = models.CharField(max_length=200, verbose_name='مسمى الوظيفة في التأمينات')
    insurable_wage_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='مبلغ الأجر الخاضع للتأمين')
    employee_deduction_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة خصم الموظف')
    company_contribution_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة مساهمة الشركة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'SocialInsuranceJobTitles'
        verbose_name = 'مسمى وظيفة في التأمينات الاجتماعية'
        verbose_name_plural = 'مسميات الوظائف في التأمينات الاجتماعية'

    def __str__(self):
        """__str__ function"""
        return f"{self.job_code} - {self.job_title}"


class ExtendedEmployeeSocialInsurance(models.Model):
    """التأمينات الاجتماعية للموظفين - النسخة الموسعة"""
    INSURANCE_STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'معلق'),
        ('pending', 'في الانتظار'),
    ]

    social_insurance_id = models.AutoField(primary_key=True, db_column='SocialInsuranceID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID',
                           related_name='extended_social_insurance', verbose_name='الموظف')
    insurance_status = models.CharField(max_length=20, choices=INSURANCE_STATUS_CHOICES, default='active', verbose_name='حالة التأمين')
    start_date = models.DateField(verbose_name='تاريخ بداية الاشتراك')
    subscription_confirmed = models.BooleanField(default=False, verbose_name='تأكيد الاشتراك')
    job_title = models.ForeignKey(SocialInsuranceJobTitle, on_delete=models.PROTECT, verbose_name='المسمى الوظيفي في التأمينات')
    social_insurance_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='رقم التأمينات الاجتماعية')
    monthly_wage = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='الأجر الشهري')
    deduction_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('9.0'), verbose_name='نسبة الخصم')
    employee_deduction = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='خصم الموظف')
    company_contribution = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='مساهمة الشركة')
    s1_field = models.BooleanField(default=False, verbose_name='حقل S1')
    incoming_document_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='رقم الوثيقة الواردة')
    incoming_document_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الوثيقة الواردة')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'ExtendedEmployeeSocialInsurance'
        verbose_name = 'تأمينات اجتماعية موسعة للموظف'
        verbose_name_plural = 'التأمينات الاجتماعية الموسعة للموظفين'

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.social_insurance_number or 'غير محدد'}"

    def save(self, *args, **kwargs):
        """save function"""
        # Calculate deductions automatically if we have the required data
        if self.monthly_wage and self.deduction_percentage:
            # Calculate employee deduction based on percentage
            self.employee_deduction = self.monthly_wage * (self.deduction_percentage / 100)

            # Calculate company contribution
            if self.job_title_id:
                try:
                    job_title = SocialInsuranceJobTitle.objects.get(id=self.job_title_id)
                    if hasattr(job_title, 'company_contribution_percentage'):
                        self.company_contribution = self.monthly_wage * (job_title.company_contribution_percentage / 100)
                    else:
                        # Default company contribution rate (12% for Saudi)
                        self.company_contribution = self.monthly_wage * Decimal('0.12')
                except SocialInsuranceJobTitle.DoesNotExist:
                    # Default company contribution rate
                    self.company_contribution = self.monthly_wage * Decimal('0.12')
            else:
                # Default company contribution rate
                self.company_contribution = self.monthly_wage * Decimal('0.12')
        super().save(*args, **kwargs)


# =============================================================================
# PAYROLL COMPONENTS MODELS
# =============================================================================

class SalaryComponent(models.Model):
    """مكونات الراتب"""
    COMPONENT_TYPE_CHOICES = [
        ('allowance', 'بدل'),
        ('deduction', 'خصم'),
    ]

    CALCULATION_TYPE_CHOICES = [
        ('fixed', 'مبلغ ثابت'),
        ('percentage', 'نسبة مئوية'),
        ('formula', 'معادلة حسابية'),
    ]

    component_id = models.AutoField(primary_key=True, db_column='ComponentID')
    component_name = models.CharField(max_length=100, verbose_name='اسم المكون')
    component_code = models.CharField(max_length=20, unique=True, verbose_name='رمز المكون')
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES, verbose_name='نوع المكون')
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPE_CHOICES, default='fixed', verbose_name='نوع الحساب')
    default_value = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='القيمة الافتراضية')
    is_taxable = models.BooleanField(default=True, verbose_name='خاضع للضريبة')
    is_social_insurance_applicable = models.BooleanField(default=True, verbose_name='خاضع للتأمينات الاجتماعية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    sort_order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'SalaryComponents'
        verbose_name = 'مكون راتب'
        verbose_name_plural = 'مكونات الراتب'
        ordering = ['sort_order', 'component_name']

    def __str__(self):
        """__str__ function"""
        return f"{self.component_name} ({self.get_component_type_display()})"


class EmployeeSalaryComponent(models.Model):
    """مكونات راتب الموظف"""
    emp_salary_component_id = models.AutoField(primary_key=True, db_column='EmpSalaryComponentID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE, verbose_name='مكون الراتب')
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='المبلغ')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='النسبة المئوية')
    effective_date = models.DateField(verbose_name='تاريخ السريان')
    end_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeSalaryComponents'
        verbose_name = 'مكون راتب الموظف'
        verbose_name_plural = 'مكونات رواتب الموظفين'
        unique_together = ['emp', 'component', 'effective_date']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.component.component_name}"

    def clean(self):
        """clean function"""
        if self.effective_date and self.end_date and self.effective_date >= self.end_date:
            raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان')


# =============================================================================
# LEAVE BALANCE MODELS
# =============================================================================

class EmployeeLeaveBalance(models.Model):
    """أرصدة إجازات الموظفين"""
    balance_id = models.AutoField(primary_key=True, db_column='BalanceID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    leave_type = models.ForeignKey('leaves.LeaveType', on_delete=models.CASCADE, verbose_name='نوع الإجازة')
    year = models.IntegerField(verbose_name='السنة')
    opening_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='الرصيد الافتتاحي')
    accrued_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='الرصيد المستحق')
    used_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='الرصيد المستخدم')
    carried_forward = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='الرصيد المرحل')
    current_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='الرصيد الحالي')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeLeaveBalances'
        verbose_name = 'رصيد إجازة الموظف'
        verbose_name_plural = 'أرصدة إجازات الموظفين'
        unique_together = ['emp', 'leave_type', 'year']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.leave_type.leave_name} ({self.year})"


# =============================================================================
# EMPLOYEE DOCUMENTS MODELS
# =============================================================================

class EmployeeDocumentCategory(models.Model):
    """فئات وثائق الموظفين"""
    category_id = models.AutoField(primary_key=True, db_column='CategoryID')
    category_name = models.CharField(max_length=100, verbose_name='اسم الفئة')
    category_code = models.CharField(max_length=20, unique=True, verbose_name='رمز الفئة')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    is_required = models.BooleanField(default=False, verbose_name='مطلوب')
    max_file_size_mb = models.IntegerField(default=10, verbose_name='الحد الأقصى لحجم الملف (ميجابايت)')
    allowed_extensions = models.CharField(max_length=200, default='pdf,doc,docx,jpg,jpeg,png', verbose_name='الامتدادات المسموحة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    sort_order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeDocumentCategories'
        verbose_name = 'فئة وثائق الموظف'
        verbose_name_plural = 'فئات وثائق الموظفين'
        ordering = ['sort_order', 'category_name']

    def __str__(self):
        """__str__ function"""
        return self.category_name

    def get_allowed_extensions_list(self):
        """إرجاع قائمة بالامتدادات المسموحة"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(',')]


class ExtendedEmployeeDocument(models.Model):
    """وثائق الموظفين"""
    document_id = models.AutoField(primary_key=True, db_column='DocumentID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID',
                           related_name='extended_documents', verbose_name='الموظف')
    category = models.ForeignKey(EmployeeDocumentCategory, on_delete=models.PROTECT,
                                verbose_name='فئة الوثيقة')
    document_name = models.CharField(max_length=200, verbose_name='اسم الوثيقة')
    document_file = models.FileField(upload_to='employee_documents/%Y/%m/', verbose_name='ملف الوثيقة')
    file_size = models.BigIntegerField(verbose_name='حجم الملف (بايت)')
    file_extension = models.CharField(max_length=10, verbose_name='امتداد الملف')
    document_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الوثيقة')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')
    is_verified = models.BooleanField(default=False, verbose_name='تم التحقق')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='verified_documents', verbose_name='تم التحقق بواسطة')
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ التحقق')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='uploaded_documents', verbose_name='رفع بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'ExtendedEmployeeDocuments'
        verbose_name = 'وثيقة الموظف الموسعة'
        verbose_name_plural = 'وثائق الموظفين الموسعة'
        ordering = ['-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.document_name}"

    def save(self, *args, **kwargs):
        """save function"""
        if self.document_file:
            self.file_size = self.document_file.size
            self.file_extension = self.document_file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)

    def get_file_size_mb(self):
        """إرجاع حجم الملف بالميجابايت"""
        return round(self.file_size / (1024 * 1024), 2)

    def is_expired(self):
        """التحقق من انتهاء صلاحية الوثيقة"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    def calculate_current_balance(self):
        """حساب الرصيد الحالي"""
        self.current_balance = self.opening_balance + self.accrued_balance + self.carried_forward - self.used_balance
        return self.current_balance

    def save(self, *args, **kwargs):
        """save function"""
        self.calculate_current_balance()
        super().save(*args, **kwargs)


# =============================================================================
# TRANSPORT MODELS
# =============================================================================

class Vehicle(models.Model):
    """المركبات"""
    VEHICLE_STATUS_CHOICES = [
        ('active', 'نشط'),
        ('maintenance', 'صيانة'),
        ('inactive', 'غير نشط'),
        ('retired', 'متقاعد'),
    ]

    vehicle_id = models.AutoField(primary_key=True, db_column='VehicleID')
    vehicle_number = models.CharField(max_length=20, unique=True, verbose_name='رقم المركبة')
    vehicle_model = models.CharField(max_length=100, verbose_name='موديل المركبة')
    vehicle_year = models.IntegerField(verbose_name='سنة الصنع')
    capacity = models.IntegerField(verbose_name='السعة')
    route_info = models.TextField(blank=True, null=True, verbose_name='معلومات المسار')
    supervisor_name = models.CharField(max_length=100, verbose_name='اسم المشرف')
    supervisor_phone = models.CharField(max_length=20, verbose_name='هاتف المشرف')
    driver_name = models.CharField(max_length=100, verbose_name='اسم السائق')
    driver_phone = models.CharField(max_length=20, verbose_name='هاتف السائق')
    driver_license = models.CharField(max_length=50, blank=True, null=True, verbose_name='رخصة السائق')
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='active', verbose_name='حالة المركبة')
    insurance_expiry = models.DateField(blank=True, null=True, verbose_name='انتهاء التأمين')
    license_expiry = models.DateField(blank=True, null=True, verbose_name='انتهاء الرخصة')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'Vehicles'
        verbose_name = 'مركبة'
        verbose_name_plural = 'المركبات'

    def __str__(self):
        """__str__ function"""
        return f"{self.vehicle_number} - {self.vehicle_model}"

    @property
    def is_available(self):
        """is_available function"""
        return self.vehicle_status == 'active'


class PickupPoint(models.Model):
    """نقاط التجميع"""
    pickup_point_id = models.AutoField(primary_key=True, db_column='PickupPointID')
    point_name = models.CharField(max_length=100, verbose_name='اسم النقطة')
    point_code = models.CharField(max_length=20, unique=True, verbose_name='رمز النقطة')
    address = models.TextField(verbose_name='العنوان')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True, verbose_name='خط العرض')
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True, verbose_name='خط الطول')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'PickupPoints'
        verbose_name = 'نقطة تجميع'
        verbose_name_plural = 'نقاط التجميع'

    def __str__(self):
        """__str__ function"""
        return f"{self.point_code} - {self.point_name}"


class EmployeeTransport(models.Model):
    """نقل الموظفين"""
    transport_id = models.AutoField(primary_key=True, db_column='TransportID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name='المركبة')
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE, verbose_name='نقطة التجميع')
    pickup_time = models.TimeField(verbose_name='وقت التجميع')
    effective_date = models.DateField(verbose_name='تاريخ السريان')
    end_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeTransport'
        verbose_name = 'نقل الموظف'
        verbose_name_plural = 'نقل الموظفين'

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.vehicle.vehicle_number}"

    def clean(self):
        """clean function"""
        if self.effective_date and self.end_date and self.effective_date >= self.end_date:
            raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان')


# =============================================================================
# PERFORMANCE EVALUATION MODELS
# =============================================================================

class EvaluationCriteria(models.Model):
    """معايير التقييم"""
    criteria_id = models.AutoField(primary_key=True, db_column='CriteriaID')
    criteria_name = models.CharField(max_length=100, verbose_name='اسم المعيار')
    criteria_code = models.CharField(max_length=20, unique=True, verbose_name='رمز المعيار')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name='الدرجة القصوى')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name='الوزن النسبي')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    sort_order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'EvaluationCriteria'
        verbose_name = 'معيار تقييم'
        verbose_name_plural = 'معايير التقييم'
        ordering = ['sort_order', 'criteria_name']

    def __str__(self):
        """__str__ function"""
        return self.criteria_name


class EmployeePerformanceEvaluation(models.Model):
    """تقييم أداء الموظفين"""
    EVALUATION_STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('submitted', 'مقدم'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
    ]

    evaluation_id = models.AutoField(primary_key=True, db_column='EvaluationID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    evaluator = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations_given', verbose_name='المقيم')
    evaluation_period_start = models.DateField(verbose_name='بداية فترة التقييم')
    evaluation_period_end = models.DateField(verbose_name='نهاية فترة التقييم')
    evaluation_date = models.DateField(verbose_name='تاريخ التقييم')
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='الدرجة الإجمالية')
    overall_rating = models.CharField(max_length=20, blank=True, null=True, verbose_name='التقدير الإجمالي')
    strengths = models.TextField(blank=True, null=True, verbose_name='نقاط القوة')
    areas_for_improvement = models.TextField(blank=True, null=True, verbose_name='مجالات التحسين')
    goals_next_period = models.TextField(blank=True, null=True, verbose_name='أهداف الفترة القادمة')
    employee_comments = models.TextField(blank=True, null=True, verbose_name='تعليقات الموظف')
    evaluator_comments = models.TextField(blank=True, null=True, verbose_name='تعليقات المقيم')
    status = models.CharField(max_length=20, choices=EVALUATION_STATUS_CHOICES, default='draft', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeePerformanceEvaluations'
        verbose_name = 'تقييم أداء الموظف'
        verbose_name_plural = 'تقييمات أداء الموظفين'

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.evaluation_date}"

    def clean(self):
        """clean function"""
        if self.evaluation_period_start and self.evaluation_period_end and self.evaluation_period_start >= self.evaluation_period_end:
            raise ValidationError('نهاية فترة التقييم يجب أن تكون بعد البداية')


class EvaluationScore(models.Model):
    """درجات التقييم"""
    score_id = models.AutoField(primary_key=True, db_column='ScoreID')
    evaluation = models.ForeignKey(EmployeePerformanceEvaluation, on_delete=models.CASCADE, verbose_name='التقييم')
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE, verbose_name='المعيار')
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='الدرجة')
    comments = models.TextField(blank=True, null=True, verbose_name='التعليقات')

    class Meta:
        """Meta class"""
        db_table = 'EvaluationScores'
        verbose_name = 'درجة تقييم'
        verbose_name_plural = 'درجات التقييم'
        unique_together = ['evaluation', 'criteria']

    def __str__(self):
        """__str__ function"""
        return f"{self.evaluation} - {self.criteria.criteria_name}: {self.score}"


# =============================================================================
# WORK SETUP MODELS
# =============================================================================

class WorkSchedule(models.Model):
    """جداول العمل"""
    schedule_id = models.AutoField(primary_key=True, db_column='ScheduleID')
    schedule_name = models.CharField(max_length=100, verbose_name='اسم الجدول')
    schedule_code = models.CharField(max_length=20, unique=True, verbose_name='رمز الجدول')
    daily_hours = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ساعات العمل اليومية')
    weekly_hours = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ساعات العمل الأسبوعية')
    start_time = models.TimeField(verbose_name='وقت البداية')
    end_time = models.TimeField(verbose_name='وقت النهاية')
    break_duration = models.IntegerField(default=0, verbose_name='مدة الاستراحة (بالدقائق)')
    is_flexible = models.BooleanField(default=False, verbose_name='مرن')
    overtime_applicable = models.BooleanField(default=True, verbose_name='قابل للعمل الإضافي')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'WorkSchedules'
        verbose_name = 'جدول عمل'
        verbose_name_plural = 'جداول العمل'

    def __str__(self):
        """__str__ function"""
        return f"{self.schedule_name} ({self.daily_hours} ساعة)"


class EmployeeWorkSetup(models.Model):
    """إعدادات عمل الموظف"""
    work_setup_id = models.AutoField(primary_key=True, db_column='WorkSetupID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE, verbose_name='جدول العمل')
    effective_date = models.DateField(verbose_name='تاريخ السريان')
    end_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء')
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.5, verbose_name='معدل العمل الإضافي')
    late_deduction_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='معدل خصم التأخير')
    absence_deduction_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name='معدل خصم الغياب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeWorkSetup'
        verbose_name = 'إعدادات عمل الموظف'
        verbose_name_plural = 'إعدادات عمل الموظفين'

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.work_schedule.schedule_name}"

    def clean(self):
        """clean function"""
        if self.effective_date and self.end_date and self.effective_date >= self.end_date:
            raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان')
