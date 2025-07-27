# =============================================================================
# ElDawliya HR Management System - Enhanced Models
# =============================================================================
# Comprehensive HR management system with modern Django architecture
# Supports RTL Arabic interface and enterprise-level functionality
# =============================================================================

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.db.models import Q
from cryptography.fernet import Fernet
from django.conf import settings


# =============================================================================
# ENCRYPTED FIELD FOR SENSITIVE DATA
# =============================================================================

class EncryptedField(models.CharField):
    """حقل مشفر للبيانات الحساسة"""
    
    def __init__(self, *args, **kwargs):
        if hasattr(settings, 'FIELD_ENCRYPTION_KEY') and settings.FIELD_ENCRYPTION_KEY:
            self.cipher = Fernet(settings.FIELD_ENCRYPTION_KEY.encode())
        else:
            self.cipher = None
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except:
            return value  # Return as-is if decryption fails
    
    def get_prep_value(self, value):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except:
            return value


# =============================================================================
# CORE MODELS - Company Structure Enhanced
# =============================================================================

class Company(models.Model):
    """نموذج الشركة المحسن"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name=_('اسم الشركة'))
    name_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('كود الشركة'))
    
    # Legal Information
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الرقم الضريبي'))
    commercial_register = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('السجل التجاري'))
    license_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('رقم الترخيص'))
    
    # Contact Information
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المدينة'))
    country = models.CharField(max_length=100, default='Saudi Arabia', verbose_name=_('الدولة'))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الرمز البريدي'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف'))
    fax = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الفاكس'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    website = models.URLField(blank=True, null=True, verbose_name=_('الموقع الإلكتروني'))
    
    # Media and Branding
    logo = models.ImageField(upload_to='company/logos/', blank=True, null=True, verbose_name=_('الشعار'))
    
    # Settings
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_('العملة'))
    fiscal_year_start = models.DateField(default='2024-01-01', verbose_name=_('بداية السنة المالية'))
    working_days_per_week = models.PositiveIntegerField(default=5, verbose_name=_('أيام العمل في الأسبوع'))
    working_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8.00, verbose_name=_('ساعات العمل في اليوم'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('شركة')
        verbose_name_plural = _('الشركات')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.working_days_per_week > 7:
            raise ValidationError(_('أيام العمل لا يمكن أن تزيد عن 7 أيام'))
        if self.working_hours_per_day > 24:
            raise ValidationError(_('ساعات العمل لا يمكن أن تزيد عن 24 ساعة'))

class 
Branch(models.Model):
    """نموذج الفرع المحسن"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches', verbose_name=_('الشركة'))
    name = models.CharField(max_length=200, verbose_name=_('اسم الفرع'))
    name_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, verbose_name=_('كود الفرع'))
    
    # Location Information
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المدينة'))
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المنطقة'))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الرمز البريدي'))
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف'))
    fax = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الفاكس'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    
    # Management
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_branches', verbose_name=_('مدير الفرع'))
    
    # Settings
    timezone = models.CharField(max_length=50, default='Asia/Riyadh', verbose_name=_('المنطقة الزمنية'))
    cost_center = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('مركز التكلفة'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    opening_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الافتتاح'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('فرع')
        verbose_name_plural = _('الفروع')
        unique_together = ['company', 'code']
        ordering = ['company', 'name']
        indexes = [
            models.Index(fields=['company', 'code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Department(models.Model):
    """نموذج القسم المحسن مع الهيكل الهرمي"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name=_('الشركة'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments', verbose_name=_('الفرع'))
    name = models.CharField(max_length=200, verbose_name=_('اسم القسم'))
    name_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, verbose_name=_('كود القسم'))
    
    # Hierarchical Structure
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='sub_departments', verbose_name=_('القسم الرئيسي'))
    level = models.PositiveIntegerField(default=1, verbose_name=_('المستوى'))
    
    # Management
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_departments', verbose_name=_('مدير القسم'))
    
    # Department Information
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    function = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الوظيفة'))
    
    # Financial Information
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_('الميزانية'))
    cost_center = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('مركز التكلفة'))
    
    # Settings
    max_employees = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('الحد الأقصى للموظفين'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    established_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التأسيس'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('قسم')
        verbose_name_plural = _('الأقسام')
        unique_together = ['company', 'code']
        ordering = ['company', 'level', 'name']
        indexes = [
            models.Index(fields=['company', 'code']),
            models.Index(fields=['parent_department']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Auto-calculate level based on parent
        if self.parent_department:
            self.level = self.parent_department.level + 1
        else:
            self.level = 1
        super().save(*args, **kwargs)

    def get_full_path(self):
        """الحصول على المسار الكامل للقسم"""
        path = [self.name]
        parent = self.parent_department
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_department
        return ' > '.join(path)

    def get_all_children(self):
        """الحصول على جميع الأقسام الفرعية"""
        children = []
        for child in self.sub_departments.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children

class JobPosition(models.Model):
    """نموذج المنصب الوظيفي المحسن"""
    
    LEVEL_CHOICES = [
        ('entry', _('مبتدئ')),
        ('junior', _('مبتدئ متقدم')),
        ('mid', _('متوسط')),
        ('senior', _('كبير')),
        ('lead', _('قائد فريق')),
        ('supervisor', _('مشرف')),
        ('manager', _('مدير')),
        ('senior_manager', _('مدير أول')),
        ('director', _('مدير عام')),
        ('vice_president', _('نائب رئيس')),
        ('president', _('رئيس')),
        ('ceo', _('الرئيس التنفيذي')),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
        ('consultant', _('استشاري')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_positions', verbose_name=_('الشركة'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='job_positions', verbose_name=_('القسم'))
    
    # Position Information
    title = models.CharField(max_length=200, verbose_name=_('المسمى الوظيفي'))
    title_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('المسمى بالإنجليزية'))
    code = models.CharField(max_length=20, verbose_name=_('كود المنصب'))
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='entry', verbose_name=_('المستوى'))
    grade = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('الدرجة'))
    
    # Job Details
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف الوظيفي'))
    responsibilities = models.TextField(blank=True, null=True, verbose_name=_('المسؤوليات'))
    requirements = models.TextField(blank=True, null=True, verbose_name=_('المتطلبات'))
    qualifications = models.TextField(blank=True, null=True, verbose_name=_('المؤهلات المطلوبة'))
    skills = models.TextField(blank=True, null=True, verbose_name=_('المهارات المطلوبة'))
    
    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time', verbose_name=_('نوع التوظيف'))
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='subordinate_positions', verbose_name=_('يرفع تقاريره إلى'))
    
    # Salary Information
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('الحد الأدنى للراتب'))
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('الحد الأقصى للراتب'))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_('العملة'))
    
    # Capacity and Planning
    max_positions = models.PositiveIntegerField(default=1, verbose_name=_('العدد الأقصى للمناصب'))
    current_positions = models.PositiveIntegerField(default=0, verbose_name=_('العدد الحالي'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    is_vacant = models.BooleanField(default=True, verbose_name=_('شاغر'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('منصب وظيفي')
        verbose_name_plural = _('المناصب الوظيفية')
        unique_together = ['company', 'code']
        ordering = ['company', 'department', 'level', 'title']
        indexes = [
            models.Index(fields=['company', 'code']),
            models.Index(fields=['department']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active', 'is_vacant']),
        ]

    def __str__(self):
        return f"{self.department.name} - {self.title}"

    def clean(self):
        if self.min_salary and self.max_salary and self.min_salary > self.max_salary:
            raise ValidationError(_('الحد الأدنى للراتب لا يمكن أن يكون أكبر من الحد الأقصى'))
        if self.current_positions > self.max_positions:
            raise ValidationError(_('العدد الحالي لا يمكن أن يزيد عن العدد الأقصى'))

    @property
    def available_positions(self):
        """عدد المناصب المتاحة"""
        return self.max_positions - self.current_positions

    @property
    def is_available(self):
        """هل المنصب متاح للتوظيف"""
        return self.is_active and self.available_positions > 0

    def update_current_positions(self):
        """تحديث العدد الحالي للمناصب"""
        self.current_positions = self.employees.filter(is_active=True).count()
        self.is_vacant = self.available_positions > 0
        self.save(update_fields=['current_positions', 'is_vacant'])
# =======
======================================================================
# EMPLOYEE MANAGEMENT - Enhanced Employee Model
# =============================================================================

class Employee(models.Model):
    """نموذج الموظف الشامل المحسن"""

    # Status Choices
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('on_leave', _('في إجازة')),
        ('suspended', _('موقوف')),
        ('terminated', _('منتهي الخدمة')),
        ('retired', _('متقاعد')),
        ('probation', _('فترة تجربة')),
    ]

    GENDER_CHOICES = [
        ('male', _('ذكر')),
        ('female', _('أنثى')),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
        ('separated', _('منفصل')),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
        ('consultant', _('استشاري')),
    ]

    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    # Primary Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=20, unique=True, verbose_name=_('رقم الموظف'))

    # Personal Information
    first_name = models.CharField(max_length=100, verbose_name=_('الاسم الأول'))
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم الأوسط'))
    last_name = models.CharField(max_length=100, verbose_name=_('اسم العائلة'))
    full_name = models.CharField(max_length=300, blank=True, verbose_name=_('الاسم الكامل'))
    name_english = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اللقب'))

    # Contact Information
    email = models.EmailField(unique=True, verbose_name=_('البريد الإلكتروني'))
    personal_email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الشخصي'))
    phone_primary = models.CharField(max_length=20, verbose_name=_('الهاتف الأساسي'))
    phone_secondary = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف الثانوي'))
    phone_emergency = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('هاتف الطوارئ'))
    
    # Address Information
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المدينة'))
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المنطقة'))
    country = models.CharField(max_length=100, default='Saudi Arabia', verbose_name=_('الدولة'))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الرمز البريدي'))

    # Personal Details
    national_id = EncryptedField(max_length=255, unique=True, verbose_name=_('رقم الهوية'))
    passport_number = EncryptedField(max_length=255, blank=True, null=True, verbose_name=_('رقم جواز السفر'))
    passport_expiry = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء جواز السفر'))
    date_of_birth = models.DateField(verbose_name=_('تاريخ الميلاد'))
    place_of_birth = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('مكان الميلاد'))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name=_('الجنس'))
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, verbose_name=_('الحالة الاجتماعية'))
    nationality = models.CharField(max_length=50, verbose_name=_('الجنسية'))
    religion = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الديانة'))
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True, verbose_name=_('فصيلة الدم'))

    # Employment Information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', verbose_name=_('الشركة'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='employees', verbose_name=_('الفرع'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees', verbose_name=_('القسم'))
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='employees', verbose_name=_('المنصب'))
    direct_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='subordinates', verbose_name=_('المدير المباشر'))

    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, verbose_name=_('نوع التوظيف'))
    hire_date = models.DateField(verbose_name=_('تاريخ التوظيف'))
    probation_start_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ بداية فترة التجربة'))
    probation_end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء فترة التجربة'))
    confirmation_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التثبيت'))
    contract_start_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ بداية العقد'))
    contract_end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء العقد'))
    termination_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الخدمة'))
    termination_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب انتهاء الخدمة'))

    # Salary Information
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('الراتب الأساسي'))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_('العملة'))
    
    # Status and Settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('الحالة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    is_manager = models.BooleanField(default=False, verbose_name=_('مدير'))
    
    # Media
    photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True, verbose_name=_('الصورة الشخصية'))

    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    
    # System Fields
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT,
                                  related_name='created_employees', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('موظف')
        verbose_name_plural = _('الموظفون')
        ordering = ['employee_number']
        indexes = [
            models.Index(fields=['employee_number']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['company', 'department']),
            models.Index(fields=['hire_date']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate full name
        if not self.full_name:
            name_parts = [self.first_name]
            if self.middle_name:
                name_parts.append(self.middle_name)
            name_parts.append(self.last_name)
            self.full_name = ' '.join(name_parts)
        
        # Auto-generate employee number if not provided
        if not self.employee_number:
            self.employee_number = self.generate_employee_number()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_number} - {self.full_name}"

    @property
    def age(self):
        """حساب العمر"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def years_of_service(self):
        """حساب سنوات الخدمة"""
        from datetime import date
        today = date.today()
        return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))

    @property
    def is_on_probation(self):
        """هل الموظف في فترة تجربة"""
        if not self.probation_end_date:
            return False
        return timezone.now().date() <= self.probation_end_date

    def generate_employee_number(self):
        """توليد رقم موظف تلقائي"""
        prefix = getattr(settings, 'HR_SETTINGS', {}).get('EMPLOYEE_NUMBER_PREFIX', 'EMP')
        length = getattr(settings, 'HR_SETTINGS', {}).get('EMPLOYEE_NUMBER_LENGTH', 6)
        
        # Get the last employee number
        last_employee = Employee.objects.filter(
            employee_number__startswith=prefix
        ).order_by('-employee_number').first()
        
        if last_employee:
            try:
                last_number = int(last_employee.employee_number[len(prefix):])
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{str(new_number).zfill(length)}"# ===
==========================================================================
# EXTENDED EMPLOYEE MODELS - Education, Insurance, Vehicles, Files
# =============================================================================

class EmployeeEducation(models.Model):
    """نموذج المؤهلات الدراسية للموظف"""
    
    DEGREE_CHOICES = [
        ('elementary', _('ابتدائية')),
        ('intermediate', _('متوسطة')),
        ('high_school', _('ثانوية عامة')),
        ('diploma', _('دبلوم')),
        ('bachelor', _('بكالوريوس')),
        ('master', _('ماجستير')),
        ('phd', _('دكتوراه')),
        ('certificate', _('شهادة مهنية')),
        ('training', _('دورة تدريبية')),
    ]
    
    GRADE_SYSTEM_CHOICES = [
        ('percentage', _('نسبة مئوية')),
        ('gpa_4', _('GPA من 4')),
        ('gpa_5', _('GPA من 5')),
        ('letter', _('حروف')),
        ('pass_fail', _('نجح/راسب')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='education_records', verbose_name=_('الموظف'))
    
    # Education Details
    degree_type = models.CharField(max_length=20, choices=DEGREE_CHOICES, verbose_name=_('نوع الشهادة'))
    major = models.CharField(max_length=200, verbose_name=_('التخصص'))
    minor = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('التخصص الفرعي'))
    institution = models.CharField(max_length=200, verbose_name=_('الجامعة/المؤسسة'))
    institution_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('اسم المؤسسة بالإنجليزية'))
    
    # Academic Information
    graduation_year = models.PositiveIntegerField(verbose_name=_('سنة التخرج'))
    start_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('سنة البداية'))
    grade_system = models.CharField(max_length=20, choices=GRADE_SYSTEM_CHOICES, default='percentage', verbose_name=_('نظام الدرجات'))
    grade = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('المعدل/الدرجة'))
    
    # Location
    country = models.CharField(max_length=100, verbose_name=_('الدولة'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المدينة'))
    
    # Verification
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verification_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    verification_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات التحقق'))
    
    # Files
    certificate_file = models.FileField(upload_to='education/certificates/', blank=True, null=True, verbose_name=_('ملف الشهادة'))
    transcript_file = models.FileField(upload_to='education/transcripts/', blank=True, null=True, verbose_name=_('كشف الدرجات'))
    
    # Additional Information
    honors = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('مرتبة الشرف'))
    thesis_title = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('عنوان الرسالة'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('مؤهل دراسي')
        verbose_name_plural = _('المؤهلات الدراسية')
        ordering = ['-graduation_year', 'degree_type']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['degree_type']),
            models.Index(fields=['graduation_year']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_degree_type_display()} - {self.major}"

    def clean(self):
        if self.start_year and self.graduation_year and self.start_year > self.graduation_year:
            raise ValidationError(_('سنة البداية لا يمكن أن تكون أكبر من سنة التخرج'))


class EmployeeInsurance(models.Model):
    """نموذج تأمينات الموظف"""
    
    INSURANCE_TYPE_CHOICES = [
        ('social', _('تأمين اجتماعي')),
        ('medical', _('تأمين صحي')),
        ('life', _('تأمين على الحياة')),
        ('disability', _('تأمين ضد العجز')),
        ('unemployment', _('تأمين ضد البطالة')),
        ('professional', _('تأمين مهني')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('suspended', _('موقوف')),
        ('expired', _('منتهي')),
        ('cancelled', _('ملغى')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='insurance_records', verbose_name=_('الموظف'))
    
    # Insurance Details
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES, verbose_name=_('نوع التأمين'))
    policy_number = models.CharField(max_length=100, verbose_name=_('رقم البوليصة'))
    provider = models.CharField(max_length=200, verbose_name=_('مقدم التأمين'))
    provider_contact = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('جهة الاتصال'))
    
    # Dates
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ النهاية'))
    renewal_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التجديد'))
    
    # Financial Information
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('قسط التأمين'))
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('مبلغ التغطية'))
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('مساهمة الموظف'))
    employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('مساهمة صاحب العمل'))
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('المبلغ المقتطع'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('الحالة'))
    
    # Beneficiaries
    beneficiaries = models.TextField(blank=True, null=True, verbose_name=_('المستفيدون'))
    
    # Files
    policy_document = models.FileField(upload_to='insurance/policies/', blank=True, null=True, verbose_name=_('وثيقة التأمين'))
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تأمين موظف')
        verbose_name_plural = _('تأمينات الموظفين')
        ordering = ['employee', 'insurance_type', '-start_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['insurance_type']),
            models.Index(fields=['policy_number']),
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_insurance_type_display()}"

    @property
    def is_active(self):
        """هل التأمين نشط"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return True

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء التأمين"""
        if not self.end_date:
            return None
        return (self.end_date - timezone.now().date()).days

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_('تاريخ البداية لا يمكن أن يكون أكبر من تاريخ النهاية'))
        if self.employee_contribution + self.employer_contribution != self.premium_amount:
            raise ValidationError(_('مجموع مساهمة الموظف وصاحب العمل يجب أن يساوي قسط التأمين'))c
lass EmployeeVehicle(models.Model):
    """نموذج سيارات الموظفين"""
    
    VEHICLE_TYPE_CHOICES = [
        ('company', _('سيارة الشركة')),
        ('personal', _('سيارة شخصية')),
        ('allowance', _('بدل سيارة')),
        ('rental', _('سيارة مستأجرة')),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('gasoline', _('بنزين')),
        ('diesel', _('ديزل')),
        ('hybrid', _('هجين')),
        ('electric', _('كهربائي')),
        ('lpg', _('غاز')),
    ]
    
    STATUS_CHOICES = [
        ('assigned', _('مخصصة')),
        ('available', _('متاحة')),
        ('maintenance', _('في الصيانة')),
        ('retired', _('خارج الخدمة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='vehicle_records', verbose_name=_('الموظف'))
    
    # Vehicle Information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, verbose_name=_('نوع السيارة'))
    make = models.CharField(max_length=100, verbose_name=_('الماركة'))
    model = models.CharField(max_length=100, verbose_name=_('الموديل'))
    year = models.PositiveIntegerField(verbose_name=_('سنة الصنع'))
    license_plate = models.CharField(max_length=20, unique=True, verbose_name=_('رقم اللوحة'))
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('اللون'))
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, verbose_name=_('نوع الوقود'))
    engine_size = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('حجم المحرك'))
    
    # Assignment Information
    assigned_date = models.DateField(verbose_name=_('تاريخ التخصيص'))
    return_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الإرجاع'))
    
    # Financial Information
    monthly_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('البدل الشهري'))
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_('سعر الشراء'))
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_('القيمة الحالية'))
    
    # Legal Information
    insurance_company = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('شركة التأمين'))
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('رقم بوليصة التأمين'))
    insurance_expiry = models.DateField(verbose_name=_('تاريخ انتهاء التأمين'))
    registration_expiry = models.DateField(verbose_name=_('تاريخ انتهاء الاستمارة'))
    license_expiry = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الرخصة'))
    
    # Maintenance Information
    last_maintenance_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ آخر صيانة'))
    next_maintenance_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الصيانة القادمة'))
    mileage = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('عدد الكيلومترات'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned', verbose_name=_('الحالة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('سيارة موظف')
        verbose_name_plural = _('سيارات الموظفين')
        ordering = ['employee', '-assigned_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['license_plate']),
            models.Index(fields=['vehicle_type']),
            models.Index(fields=['status']),
            models.Index(fields=['insurance_expiry']),
            models.Index(fields=['registration_expiry']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.make} {self.model} ({self.license_plate})"

    @property
    def insurance_days_remaining(self):
        """عدد الأيام المتبقية على انتهاء التأمين"""
        return (self.insurance_expiry - timezone.now().date()).days

    @property
    def registration_days_remaining(self):
        """عدد الأيام المتبقية على انتهاء الاستمارة"""
        return (self.registration_expiry - timezone.now().date()).days

    @property
    def needs_maintenance(self):
        """هل تحتاج السيارة لصيانة"""
        if not self.next_maintenance_date:
            return False
        return timezone.now().date() >= self.next_maintenance_date

    def clean(self):
        if self.return_date and self.assigned_date > self.return_date:
            raise ValidationError(_('تاريخ التخصيص لا يمكن أن يكون أكبر من تاريخ الإرجاع'))


class EmployeeFile(models.Model):
    """نموذج ملفات ووثائق الموظف"""
    
    FILE_TYPE_CHOICES = [
        ('id_copy', _('صورة الهوية')),
        ('passport', _('جواز السفر')),
        ('contract', _('عقد العمل')),
        ('job_offer', _('عرض العمل')),
        ('certificate', _('شهادة دراسية')),
        ('transcript', _('كشف درجات')),
        ('medical', _('تقرير طبي')),
        ('photo', _('صورة شخصية')),
        ('cv', _('السيرة الذاتية')),
        ('reference', _('خطاب توصية')),
        ('bank_letter', _('خطاب بنكي')),
        ('insurance', _('وثيقة تأمين')),
        ('training', _('شهادة تدريب')),
        ('performance', _('تقييم أداء')),
        ('disciplinary', _('إجراء تأديبي')),
        ('resignation', _('استقالة')),
        ('termination', _('إنهاء خدمة')),
        ('other', _('أخرى')),
    ]
    
    CONFIDENTIALITY_LEVEL_CHOICES = [
        ('public', _('عام')),
        ('internal', _('داخلي')),
        ('confidential', _('سري')),
        ('highly_confidential', _('سري للغاية')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files', verbose_name=_('الموظف'))
    
    # File Information
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, verbose_name=_('نوع الملف'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    
    # File Storage
    file = models.FileField(upload_to='employee_files/', verbose_name=_('الملف'))
    file_size = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('حجم الملف'))
    mime_type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('نوع الملف'))
    
    # Dates
    document_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الوثيقة'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الانتهاء'))
    
    # Security
    confidentiality_level = models.CharField(max_length=20, choices=CONFIDENTIALITY_LEVEL_CHOICES, 
                                           default='internal', verbose_name=_('مستوى السرية'))
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verification_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    verified_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='verified_files', verbose_name=_('تم التحقق بواسطة'))
    
    # Access Control
    can_be_downloaded = models.BooleanField(default=True, verbose_name=_('قابل للتحميل'))
    download_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد مرات التحميل'))
    
    # System Information
    uploaded_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الرفع بواسطة'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الرفع'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('ملف موظف')
        verbose_name_plural = _('ملفات الموظفين')
        ordering = ['employee', '-uploaded_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['file_type']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['confidentiality_level']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء الوثيقة"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expired(self):
        """هل انتهت صلاحية الوثيقة"""
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date

    @property
    def is_expiring_soon(self):
        """هل ستنتهي صلاحية الوثيقة قريباً"""
        if not self.expiry_date:
            return False
        warning_days = getattr(settings, 'HR_SETTINGS', {}).get('DOCUMENT_EXPIRY_WARNING_DAYS', 30)
        return 0 <= self.days_until_expiry <= warning_days

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # You can add mime type detection here
        super().save(*args, **kwargs)

    def increment_download_count(self):
        """زيادة عداد التحميل"""
        self.download_count += 1
        self.save(update_fields=['download_count'])