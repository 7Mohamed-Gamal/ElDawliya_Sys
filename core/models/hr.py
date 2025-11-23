"""
نماذج الموارد البشرية المحسنة والموحدة
Enhanced and Unified HR Models
"""
import uuid
from decimal import Decimal
from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .base import BaseModel, AuditableModel, SoftDeleteModel, AddressModel, ContactModel


class Department(BaseModel):
    """الأقسام المحسنة"""
    name = models.CharField(max_length=100, verbose_name=_('اسم القسم'))
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('رمز القسم'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    parent_department = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='sub_departments', verbose_name=_('القسم الأب'))
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_departments', verbose_name=_('مدير القسم'))
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_('الميزانية'))
    cost_center = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('مركز التكلفة'))
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الموقع'))
    
    class Meta:
        verbose_name = _('قسم')
        verbose_name_plural = _('الأقسام')
        ordering = ['name']
        
    def __str__(self):
        return self.name


class JobPosition(BaseModel):
    """المناصب الوظيفية المحسنة"""
    title = models.CharField(max_length=100, verbose_name=_('المسمى الوظيفي'))
    title_en = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المسمى بالإنجليزية'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('رمز المنصب'))
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='positions', verbose_name=_('القسم'))
    level = models.PositiveIntegerField(default=1, verbose_name=_('المستوى الوظيفي'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف الوظيفي'))
    requirements = models.TextField(blank=True, null=True, verbose_name=_('المتطلبات'))
    responsibilities = models.TextField(blank=True, null=True, verbose_name=_('المسؤوليات'))
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('الحد الأدنى للراتب'))
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('الحد الأقصى للراتب'))
    
    class Meta:
        verbose_name = _('منصب وظيفي')
        verbose_name_plural = _('المناصب الوظيفية')
        ordering = ['department', 'level', 'title']
        
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Employee(AuditableModel, AddressModel, ContactModel):
    """نموذج الموظف المحسن والشامل"""
    GENDER_CHOICES = [
        ('M', _('ذكر')),
        ('F', _('أنثى')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('terminated', _('منتهي الخدمة')),
        ('suspended', _('معلق')),
        ('on_leave', _('في إجازة')),
        ('probation', _('فترة تجربة')),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
    ]
    
    # Basic Information
    emp_code = models.CharField(max_length=20, unique=True, verbose_name=_('رقم الموظف'))
    first_name = models.CharField(max_length=100, verbose_name=_('الاسم الأول'))
    second_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم الثاني'))
    third_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم الثالث'))
    last_name = models.CharField(max_length=100, verbose_name=_('اسم العائلة'))
    first_name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم الأول بالإنجليزية'))
    last_name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم العائلة بالإنجليزية'))
    
    # Personal Information
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('الجنس'))
    birth_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الميلاد'))
    birth_place = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('مكان الميلاد'))
    nationality = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الجنسية'))
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, null=True, verbose_name=_('الحالة الاجتماعية'))
    dependents_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد المعالين'))
    
    # Identification
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهوية الوطنية'))
    passport_no = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم جواز السفر'))
    passport_expiry = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء جواز السفر'))
    iqama_no = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الإقامة'))
    iqama_expiry = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الإقامة'))
    
    # Employment Information
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', verbose_name=_('القسم'))
    job_position = models.ForeignKey(JobPosition, on_delete=models.PROTECT, related_name='employees', verbose_name=_('المنصب'))
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='subordinates', verbose_name=_('المدير المباشر'))
    hire_date = models.DateField(verbose_name=_('تاريخ التوظيف'))
    join_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الالتحاق'))
    probation_end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء فترة التجربة'))
    confirmation_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التثبيت'))
    termination_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ إنهاء الخدمة'))
    termination_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب إنهاء الخدمة'))
    
    # Status and Classification
    emp_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('حالة الموظف'))
    employment_type = models.CharField(max_length=20, choices=[
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
    ], default='full_time', verbose_name=_('نوع التوظيف'))
    
    # Additional Information
    photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True, verbose_name=_('الصورة الشخصية'))
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم جهة الاتصال للطوارئ'))
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('هاتف جهة الاتصال للطوارئ'))
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('صلة القرابة'))
    
    # System Integration
    user_account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='employee_profile', verbose_name=_('حساب المستخدم'))
    
    class Meta:
        verbose_name = _('موظف')
        verbose_name_plural = _('الموظفون')
        ordering = ['emp_code']
        indexes = [
            models.Index(fields=['emp_code']),
            models.Index(fields=['department', 'emp_status']),
            models.Index(fields=['manager']),
            models.Index(fields=['hire_date']),
            models.Index(fields=['emp_status']),
        ]
        
    def __str__(self):
        return f"{self.emp_code} - {self.get_full_name()}"
    
    def get_full_name(self):
        """الحصول على الاسم الكامل"""
        names = [self.first_name, self.second_name, self.third_name, self.last_name]
        return ' '.join([name for name in names if name])
    
    def get_full_name_en(self):
        """الحصول على الاسم الكامل بالإنجليزية"""
        if self.first_name_en and self.last_name_en:
            return f"{self.first_name_en} {self.last_name_en}"
        return self.get_full_name()
    
    @property
    def full_name(self):
        return self.get_full_name()
    
    @property
    def age(self):
        """حساب العمر"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    @property
    def years_of_service(self):
        """حساب سنوات الخدمة"""
        if self.hire_date:
            end_date = self.termination_date or date.today()
            return (end_date - self.hire_date).days / 365.25
        return 0
    
    @property
    def months_of_service(self):
        """حساب شهور الخدمة"""
        return int(self.years_of_service * 12)
    
    @property
    def is_on_probation(self):
        """فحص إذا كان الموظف في فترة تجربة"""
        if self.probation_end_date:
            return date.today() <= self.probation_end_date
        return False
    
    @property
    def is_document_expiring_soon(self):
        """فحص إذا كانت وثائق الموظف ستنتهي قريباً"""
        warning_days = 30
        today = date.today()
        warning_date = today + timedelta(days=warning_days)
        
        expiring_docs = []
        if self.passport_expiry and self.passport_expiry <= warning_date:
            expiring_docs.append('passport')
        if self.iqama_expiry and self.iqama_expiry <= warning_date:
            expiring_docs.append('iqama')
            
        return expiring_docs
    
    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}
        
        # التحقق من التواريخ
        if self.birth_date and self.birth_date > date.today():
            errors['birth_date'] = _('تاريخ الميلاد لا يمكن أن يكون في المستقبل')
            
        if self.hire_date and self.hire_date > date.today():
            errors['hire_date'] = _('تاريخ التوظيف لا يمكن أن يكون في المستقبل')
            
        if self.join_date and self.hire_date and self.join_date < self.hire_date:
            errors['join_date'] = _('تاريخ الالتحاق لا يمكن أن يكون قبل تاريخ التوظيف')
            
        if self.probation_end_date and self.hire_date and self.probation_end_date < self.hire_date:
            errors['probation_end_date'] = _('تاريخ انتهاء فترة التجربة لا يمكن أن يكون قبل تاريخ التوظيف')
            
        if self.termination_date and self.hire_date and self.termination_date < self.hire_date:
            errors['termination_date'] = _('تاريخ إنهاء الخدمة لا يمكن أن يكون قبل تاريخ التوظيف')
        
        # التحقق من المدير
        if self.manager == self:
            errors['manager'] = _('لا يمكن للموظف أن يكون مديراً لنفسه')
            
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """حفظ محسن مع التحقق"""
        self.full_clean()
        super().save(*args, **kwargs)

clas
s EmployeeQualification(BaseModel):
    """مؤهلات الموظف"""
    QUALIFICATION_TYPES = [
        ('education', _('تعليمي')),
        ('certification', _('شهادة مهنية')),
        ('training', _('دورة تدريبية')),
        ('experience', _('خبرة عملية')),
        ('skill', _('مهارة')),
    ]
    
    EDUCATION_LEVELS = [
        ('high_school', _('ثانوية عامة')),
        ('diploma', _('دبلوم')),
        ('bachelor', _('بكالوريوس')),
        ('master', _('ماجستير')),
        ('phd', _('دكتوراه')),
        ('other', _('أخرى')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='qualifications', verbose_name=_('الموظف'))
    qualification_type = models.CharField(max_length=20, choices=QUALIFICATION_TYPES, verbose_name=_('نوع المؤهل'))
    title = models.CharField(max_length=200, verbose_name=_('عنوان المؤهل'))
    institution = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('المؤسسة'))
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVELS, blank=True, null=True, verbose_name=_('المستوى التعليمي'))
    field_of_study = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('مجال الدراسة'))
    start_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ النهاية'))
    grade = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الدرجة/التقدير'))
    certificate_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('رقم الشهادة'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الصلاحية'))
    attachment = models.FileField(upload_to='employees/qualifications/', blank=True, null=True, verbose_name=_('المرفق'))
    verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('تم التحقق بواسطة'))
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    
    class Meta:
        verbose_name = _('مؤهل موظف')
        verbose_name_plural = _('مؤهلات الموظفين')
        ordering = ['-end_date', 'qualification_type']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.title}"
    
    @property
    def is_expired(self):
        """فحص إذا كان المؤهل منتهي الصلاحية"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False


class EmployeeBankAccount(BaseModel):
    """حسابات الموظف البنكية"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bank_accounts', verbose_name=_('الموظف'))
    bank_name = models.CharField(max_length=100, verbose_name=_('اسم البنك'))
    account_number = models.CharField(max_length=50, verbose_name=_('رقم الحساب'))
    iban = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('رقم الآيبان'))
    account_holder_name = models.CharField(max_length=200, verbose_name=_('اسم صاحب الحساب'))
    is_primary = models.BooleanField(default=False, verbose_name=_('الحساب الأساسي'))
    is_salary_account = models.BooleanField(default=False, verbose_name=_('حساب الراتب'))
    
    class Meta:
        verbose_name = _('حساب بنكي')
        verbose_name_plural = _('الحسابات البنكية')
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.bank_name}"
    
    def clean(self):
        """التحقق من وجود حساب أساسي واحد فقط"""
        if self.is_primary:
            existing_primary = EmployeeBankAccount.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(pk=self.pk)
            
            if existing_primary.exists():
                raise ValidationError(_('يمكن أن يكون هناك حساب أساسي واحد فقط لكل موظف'))


class EmployeeDocument(BaseModel):
    """وثائق الموظف"""
    DOCUMENT_TYPES = [
        ('id_card', _('بطاقة الهوية')),
        ('passport', _('جواز السفر')),
        ('iqama', _('الإقامة')),
        ('contract', _('عقد العمل')),
        ('cv', _('السيرة الذاتية')),
        ('certificate', _('شهادة')),
        ('medical_report', _('تقرير طبي')),
        ('photo', _('صورة شخصية')),
        ('other', _('أخرى')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents', verbose_name=_('الموظف'))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name=_('نوع الوثيقة'))
    title = models.CharField(max_length=200, verbose_name=_('عنوان الوثيقة'))
    document_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('رقم الوثيقة'))
    issue_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الإصدار'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الصلاحية'))
    issuing_authority = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('جهة الإصدار'))
    file = models.FileField(upload_to='employees/documents/', verbose_name=_('الملف'))
    file_size = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('حجم الملف'))
    file_type = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('نوع الملف'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    
    class Meta:
        verbose_name = _('وثيقة موظف')
        verbose_name_plural = _('وثائق الموظفين')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.title}"
    
    @property
    def is_expired(self):
        """فحص إذا كانت الوثيقة منتهية الصلاحية"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False
    
    @property
    def days_until_expiry(self):
        """حساب الأيام المتبقية حتى انتهاء الصلاحية"""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days if delta.days > 0 else 0
        return None
    
    def save(self, *args, **kwargs):
        """حفظ محسن مع معلومات الملف"""
        if self.file:
            self.file_size = self.file.size
            self.file_type = self.file.name.split('.')[-1].lower() if '.' in self.file.name else ''
        super().save(*args, **kwargs)


class EmployeeSalary(AuditableModel):
    """رواتب الموظفين المحسنة"""
    SALARY_TYPES = [
        ('monthly', _('شهري')),
        ('hourly', _('بالساعة')),
        ('daily', _('يومي')),
        ('project', _('مشروع')),
        ('commission', _('عمولة')),
    ]
    
    CURRENCY_CHOICES = [
        ('SAR', _('ريال سعودي')),
        ('USD', _('دولار أمريكي')),
        ('EUR', _('يورو')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries', verbose_name=_('الموظف'))
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPES, default='monthly', verbose_name=_('نوع الراتب'))
    
    # Basic Salary Components
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('الراتب الأساسي'))
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل السكن'))
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل المواصلات'))
    food_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل الطعام'))
    mobile_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل الهاتف'))
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدلات أخرى'))
    
    # Deductions
    gosi_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('تأمينات الموظف'))
    gosi_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('تأمينات صاحب العمل'))
    income_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('ضريبة الدخل'))
    medical_insurance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('التأمين الطبي'))
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('خصومات أخرى'))
    
    # Overtime Settings
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.5'), verbose_name=_('معدل الوقت الإضافي'))
    weekend_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.0'), verbose_name=_('معدل عمل نهاية الأسبوع'))
    holiday_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.5'), verbose_name=_('معدل عمل العطل'))
    
    # Validity
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='SAR', verbose_name=_('العملة'))
    effective_date = models.DateField(verbose_name=_('تاريخ السريان'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الانتهاء'))
    is_current = models.BooleanField(default=True, verbose_name=_('ساري حالياً'))
    
    class Meta:
        verbose_name = _('راتب موظف')
        verbose_name_plural = _('رواتب الموظفين')
        ordering = ['-effective_date']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.basic_salary} {self.currency}"
    
    @property
    def total_allowances(self):
        """إجمالي البدلات"""
        return (
            self.housing_allowance + self.transport_allowance + 
            self.food_allowance + self.mobile_allowance + self.other_allowances
        )
    
    @property
    def total_deductions(self):
        """إجمالي الخصومات"""
        return (
            self.gosi_employee + self.income_tax + 
            self.medical_insurance + self.other_deductions
        )
    
    @property
    def gross_salary(self):
        """إجمالي الراتب قبل الخصومات"""
        return self.basic_salary + self.total_allowances
    
    @property
    def net_salary(self):
        """صافي الراتب"""
        return self.gross_salary - self.total_deductions
    
    @property
    def total_cost_to_employer(self):
        """إجمالي التكلفة على صاحب العمل"""
        return self.gross_salary + self.gosi_employer
    
    def calculate_hourly_rate(self):
        """حساب الأجر بالساعة"""
        if self.salary_type == 'hourly':
            return self.basic_salary
        elif self.salary_type == 'monthly':
            # افتراض 8 ساعات يومياً × 22 يوم عمل شهرياً
            return self.basic_salary / Decimal('176')
        elif self.salary_type == 'daily':
            return self.basic_salary / Decimal('8')
        return Decimal('0')
    
    def calculate_daily_rate(self):
        """حساب الأجر اليومي"""
        if self.salary_type == 'daily':
            return self.basic_salary
        elif self.salary_type == 'monthly':
            return self.basic_salary / Decimal('22')  # 22 يوم عمل في الشهر
        elif self.salary_type == 'hourly':
            return self.basic_salary * Decimal('8')
        return Decimal('0')
    
    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}
        
        if self.basic_salary < 0:
            errors['basic_salary'] = _('الراتب الأساسي لا يمكن أن يكون سالباً')
        
        if self.end_date and self.effective_date and self.end_date <= self.effective_date:
            errors['end_date'] = _('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان')
        
        # التأكد من وجود راتب واحد فقط ساري لكل موظف
        if self.is_current:
            existing_current = EmployeeSalary.objects.filter(
                employee=self.employee,
                is_current=True
            ).exclude(pk=self.pk)
            
            if existing_current.exists():
                errors['is_current'] = _('يوجد راتب ساري بالفعل لهذا الموظف')
        
        if errors:
            raise ValidationError(errors)


class EmployeeInsurance(BaseModel):
    """تأمينات الموظف"""
    INSURANCE_TYPES = [
        ('health', _('تأمين صحي')),
        ('social', _('تأمينات اجتماعية')),
        ('life', _('تأمين على الحياة')),
        ('disability', _('تأمين ضد العجز')),
        ('unemployment', _('تأمين ضد البطالة')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('suspended', _('معلق')),
        ('expired', _('منتهي الصلاحية')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='insurances', verbose_name=_('الموظف'))
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPES, verbose_name=_('نوع التأمين'))
    provider_name = models.CharField(max_length=200, verbose_name=_('اسم مقدم الخدمة'))
    policy_number = models.CharField(max_length=100, verbose_name=_('رقم البوليصة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('الحالة'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ النهاية'))
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_('قسط التأمين'))
    coverage_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name=_('مبلغ التغطية'))
    employee_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('مساهمة الموظف'))
    employer_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('مساهمة صاحب العمل'))
    dependents_covered = models.PositiveIntegerField(default=0, verbose_name=_('عدد المعالين المشمولين'))
    
    class Meta:
        verbose_name = _('تأمين موظف')
        verbose_name_plural = _('تأمينات الموظفين')
        unique_together = ['employee', 'insurance_type', 'policy_number']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_insurance_type_display()}"
    
    @property
    def is_active(self):
        """فحص إذا كان التأمين نشطاً"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < date.today():
            return False
        return True
    
    @property
    def days_until_expiry(self):
        """حساب الأيام المتبقية حتى انتهاء الصلاحية"""
        if self.end_date:
            delta = self.end_date - date.today()
            return delta.days if delta.days > 0 else 0
        return None
    
    @property
    def total_contribution(self):
        """إجمالي المساهمة الشهرية"""
        return self.employee_contribution + self.employer_contribution