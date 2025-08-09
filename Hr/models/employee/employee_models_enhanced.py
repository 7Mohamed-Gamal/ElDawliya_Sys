"""
نماذج الموظفين المحسنة لنظام إدارة الموارد البشرية (HRMS) - النسخة الشاملة
تتعامل مع جميع بيانات الموظفين والمعلومات الحساسة مع التشفير المتقدم والتحقق من صحة البيانات
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import (
    make_password,
    is_password_usable,
    check_password
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import date, timedelta
import re


def validate_birth_date(value):
    """التحقق من صحة تاريخ الميلاد"""
    if value >= date.today():
        raise ValidationError(_('تاريخ الميلاد يجب أن يكون في الماضي'))


class EmployeeEnhanced(models.Model):
    """
    نموذج الموظف المحسن والشامل يحتوي على جميع المعلومات الشخصية والمالية مع تشفير الحقول الحساسة.
    """
    
    # Gender Choices
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    
    GENDER_CHOICES = (
        (MALE, _('ذكر')),
        (FEMALE, _('أنثى')),
        (OTHER, _('أخرى'))
    )
    
    # Marital Status
    SINGLE = 'S'
    MARRIED = 'M'
    DIVORCED = 'D'
    WIDOWED = 'W'
    
    MARITAL_CHOICES = (
        (SINGLE, _('أعزب')), 
        (MARRIED, _('متزوج')),
        (DIVORCED, _('مطلق')),
        (WIDOWED, _('أرمل'))
    )
    
    # Employment Type
    EMPLOYMENT_TYPES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('عقد مؤقت')),
        ('internship', _('تدريب')),
        ('consultant', _('استشاري')),
        ('freelancer', _('عمل حر')),
        ('temporary', _('مؤقت')),
    ]
    
    # Status Options
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    TERMINATED = 'terminated'
    ON_LEAVE = 'on_leave'
    PROBATION = 'probation'
    
    STATUS_CHOICES = (
        (ACTIVE, _('نشط')),
        (SUSPENDED, _('موقوف')),
        (TERMINATED, _('منتهي الخدمة')),
        (ON_LEAVE, _('في إجازة')),
        (PROBATION, _('فترة تجربة')),
    )
    
    # Work Schedule Types
    WORK_SCHEDULE_CHOICES = [
        ('regular', _('نظام عادي')),
        ('shift', _('نظام ورديات')),
        ('flexible', _('مرن')),
        ('remote', _('عن بُعد')),
        ('hybrid', _('مختلط')),
    ]
    
    # Military Service Status
    MILITARY_SERVICE_CHOICES = [
        ('completed', _('مكتملة')),
        ('exempted', _('معفى')),
        ('postponed', _('مؤجلة')),
        ('not_applicable', _('غير مطلوبة')),
        ('in_progress', _('جارية')),
    ]
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Personal Information - Enhanced
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("الاسم الأول"),
        validators=[RegexValidator(
            regex=r'^[a-zA-Zأ-ي\s]+$',
            message=_('الاسم يجب أن يحتوي على حروف فقط')
        )]
    )
    
    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم الأوسط"),
        validators=[RegexValidator(
            regex=r'^[a-zA-Zأ-ي\s]+$',
            message=_('الاسم يجب أن يحتوي على حروف فقط')
        )]
    )
    
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("الاسم الأخير"),
        validators=[RegexValidator(
            regex=r'^[a-zA-Zأ-ي\s]+$',
            message=_('الاسم يجب أن يحتوي على حروف فقط')
        )]
    )
    
    # English Names
    first_name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم الأول بالإنجليزية"),
        validators=[RegexValidator(
            regex=r'^[a-zA-Z\s]+$',
            message=_('الاسم الإنجليزي يجب أن يحتوي على حروف إنجليزية فقط')
        )]
    )
    
    middle_name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم الأوسط بالإنجليزية"),
        validators=[RegexValidator(
            regex=r'^[a-zA-Z\s]+$',
            message=_('الاسم الإنجليزي يجب أن يحتوي على حروف إنجليزية فقط')
        )]
    )
    
    last_name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم الأخير بالإنجليزية"),
        validators=[RegexValidator(
            regex=r'^[a-zA-Z\s]+$',
            message=_('الاسم الإنجليزي يجب أن يحتوي على حروف إنجليزية فقط')
        )]
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name=_("النوع")
    )
    
    date_of_birth = models.DateField(
        verbose_name=_("تاريخ الميلاد"),
        validators=[validate_birth_date]
    )
    
    place_of_birth = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("مكان الميلاد")
    )
    
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_CHOICES,
        default=SINGLE,
        verbose_name=_("الحالة الاجتماعية")
    )
    
    number_of_children = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد الأطفال"),
        validators=[MaxValueValidator(20)]
    )
    
    mother_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("اسم الأم"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    # Contact Information - Enhanced and Encrypted
    private_email = models.CharField(
        max_length=254,
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني الشخصي"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    work_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني للعمل")
    )
    
    mobile_phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم الجوال"),
        help_text=_("يتم تشفير هذه البيانات"),
        validators=[RegexValidator(
            regex=r'^\+?[1-9]\d{1,14}$',
            message=_('رقم الهاتف غير صحيح')
        )]
    )
    
    home_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("هاتف المنزل"),
        help_text=_("يتم تشفير هذه البيانات"),
        validators=[RegexValidator(
            regex=r'^\+?[1-9]\d{1,14}$',
            message=_('رقم الهاتف غير صحيح')
        )]
    )
    
    # Address Information - Enhanced
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المدينة")
    )
    
    state_province = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المنطقة/الولاية")
    )
    
    country = models.CharField(
        max_length=100,
        default='Saudi Arabia',
        verbose_name=_("الدولة")
    )
    
    postal_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الرمز البريدي")
    )
    
    # Personal Details - Enhanced
    nationality = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الجنسية")
    )
    
    religion = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الديانة")
    )
    
    blood_type = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        null=True,
        blank=True,
        verbose_name=_("فصيلة الدم")
    )
    
    # Physical Information
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الطول (سم)"),
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الوزن (كغ)"),
        validators=[MinValueValidator(20), MaxValueValidator(300)]
    )
    
    # Language Skills
    languages_spoken = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("اللغات المتحدث بها"),
        help_text=_("فصل بين اللغات بفاصلة")
    )
    
    # Military Service
    military_service_status = models.CharField(
        max_length=20,
        choices=MILITARY_SERVICE_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("حالة الخدمة العسكرية")
    )
    
    military_service_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الخدمة العسكرية")
    )
    
    # Employment Information - Enhanced
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("الرقم التعريفي للموظف")
    )

    employee_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("رقم الموظف"),
        help_text=_("للاتفاقية القديمة فقط")
    )
    
    join_date = models.DateField(
        verbose_name=_("تاريخ التعيين")
    )
    
    probation_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء فترة التجربة")
    )
    
    contract_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ بداية العقد")
    )
    
    contract_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء العقد")
    )
    
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPES,
        default='full_time',
        verbose_name=_("نوع التوظيف")
    )
    
    # Organizational Structure
    company = models.ForeignKey(
        'Hr.Company',
        on_delete=models.CASCADE,
        related_name='employees_enhanced',
        verbose_name=_("الشركة")
    )

    branch = models.ForeignKey(
        'Hr.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees_enhanced',
        verbose_name=_("الفرع")
    )

    department = models.ForeignKey(
        'Hr.Department', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees_enhanced',
        verbose_name=_("القسم")
    )

    position = models.ForeignKey(
        'Hr.JobPosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees_enhanced',
        verbose_name=_("الوظيفة")
    )
    
    direct_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates_enhanced',
        verbose_name=_("المدير المباشر")
    )
    
    # Salary Information - Enhanced
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الراتب الأساسي"),
        validators=[MinValueValidator(0)]
    )
    
    salary_currency = models.CharField(
        max_length=10,
        default='SAR',
        verbose_name=_("عملة الراتب")
    )
    
    # Work Schedule
    work_schedule = models.CharField(
        max_length=20,
        choices=WORK_SCHEDULE_CHOICES,
        default='regular',
        verbose_name=_("نظام العمل")
    )

    # Financial Information - Enhanced and Encrypted
    bank_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم البنك")
    )
    
    bank_account_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم الحساب البنكي"),
        help_text=_("يتم تشفير هذه البيانات")
    )

    iban = models.CharField(
        max_length=34,  # IBAN max length is 34
        null=True,
        blank=True,
        verbose_name=_("رقم الأيبان"),
        help_text=_("يتم تشفير هذه البيانات")
    )

    # Government Documents - Enhanced and Encrypted
    national_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("رقم الهوية/الرقم القومي"),
        help_text=_("يتم تشفير هذه البيانات")
    )

    passport_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("رقم الجواز"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    passport_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الجواز")
    )
    
    passport_issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ إصدار الجواز")
    )
    
    passport_issue_place = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("مكان إصدار الجواز")
    )
    
    # Visa Information
    visa_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم التأشيرة"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    visa_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء التأشيرة")
    )
    
    # Insurance Information - Enhanced and Encrypted
    social_insurance_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم التأمين الاجتماعي"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    health_insurance_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم التأمين الصحي"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    insurance_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ بداية التأمين")
    )
    
    # Emergency Contact Information - Enhanced and Encrypted
    emergency_contact_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("اسم جهة الاتصال للطوارئ"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("صلة القرابة")
    )
    
    emergency_contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("هاتف جهة الاتصال للطوارئ"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    emergency_contact_address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("عنوان جهة الاتصال للطوارئ"),
        help_text=_("يتم تشفير هذه البيانات")
    )

    # Status Information - Enhanced
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name=_("الحالة الوظيفية")
    )

    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ إنهاء الخدمة")
    )
    
    termination_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب إنهاء الخدمة")
    )
    
    # Performance and Evaluation
    last_evaluation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ آخر تقييم")
    )
    
    next_evaluation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التقييم القادم")
    )
    
    performance_rating = models.CharField(
        max_length=20,
        choices=[
            ('excellent', _('ممتاز')),
            ('very_good', _('جيد جداً')),
            ('good', _('جيد')),
            ('satisfactory', _('مرضي')),
            ('needs_improvement', _('يحتاج تحسين')),
        ],
        null=True,
        blank=True,
        verbose_name=_("تقييم الأداء")
    )

    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Profile Picture
    profile_picture = models.ImageField(
        upload_to='employee_photos/',
        null=True,
        blank=True,
        verbose_name=_("الصورة الشخصية")
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    created_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_employees_enhanced',
        verbose_name=_("تم الإنشاء بواسطة")
    )
    
    updated_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='updated_employees_enhanced',
        verbose_name=_("تم التحديث بواسطة")
    )

    class Meta:
        verbose_name = _("موظف محسن")
        verbose_name_plural = _("الموظفين المحسنين")
        db_table = 'hrms_employee_enhanced'
        ordering = ['company', 'department', 'position', 'employee_id']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['national_id']),
            models.Index(fields=['department']),
            models.Index(fields=['position']),
            models.Index(fields=['join_date']),
            models.Index(fields=['status']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['direct_manager']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_of_birth__lt=models.F('join_date')),
                name='birth_before_join'
            ),
            models.CheckConstraint(
                check=models.Q(base_salary__gte=0),
                name='positive_salary'
            ),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    @property  
    def full_name(self):
        """إرجاع الاسم الكامل للموظف (الاسم الأول + الأوسط + الأخير)"""
        names = [self.first_name]
        if self.middle_name:
            names.append(self.middle_name)
        names.append(self.last_name)
        return ' '.join(names)
    
    @property  
    def full_name_en(self):
        """إرجاع الاسم الكامل بالإنجليزية"""
        if not self.first_name_en:
            return None
        names = [self.first_name_en]
        if self.middle_name_en:
            names.append(self.middle_name_en)
        if self.last_name_en:
            names.append(self.last_name_en)
        return ' '.join(names)

    def save(self, *args, **kwargs):
        """تجاوز الحفظ لتوليد رقم الموظف وتشفير الحقول الحساسة تلقائيًا"""
        if not self.employee_id:
            # Generate employee ID using company code and sequence
            company_code = self.company.name[:3].upper() if self.company else 'EMP'
            last_emp = EmployeeEnhanced.objects.filter(
                company=self.company
            ).order_by('-employee_id').first()
            
            if last_emp and last_emp.employee_id:
                try:
                    last_seq = int(last_emp.employee_id.split('-')[-1])
                except (ValueError, IndexError):
                    last_seq = 0
            else:
                last_seq = 0
                
            self.employee_id = f"{company_code}-{last_seq+1:05d}"
            self.employee_number = self.employee_id  # Set both fields to same value

        # Encrypt sensitive fields before saving
        for field in self._sensitive_fields:
            value = getattr(self, field)
            if value and not str(value).startswith('$pbkdf2-sha256'):
                setattr(self, field, make_password(str(value)))

        # Auto-set probation end date if not set
        if not self.probation_end_date and self.join_date:
            self.probation_end_date = self.join_date + timedelta(days=90)  # 3 months default

        # Auto-set next evaluation date if not set
        if not self.next_evaluation_date and self.join_date:
            if self.last_evaluation_date:
                self.next_evaluation_date = self.last_evaluation_date + timedelta(days=365)  # 1 year
            else:
                self.next_evaluation_date = self.join_date + timedelta(days=180)  # 6 months for new employees

        # Call clean method for validation
        try:
            self.full_clean()
        except ValidationError as e:
            # Log validation errors but don't prevent saving
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Validation errors for employee {self.employee_id}: {e}")
        
        super().save(*args, **kwargs)

    @property
    def _sensitive_fields(self):
        """قائمة الحقول التي يجب تشفيرها تلقائيًا عند الحفظ"""
        return [
            'private_email',
            'mobile_phone',
            'home_phone',
            'address',
            'mother_name',
            'bank_account_number',
            'iban',
            'national_id',
            'passport_number',
            'visa_number',
            'social_insurance_number',
            'health_insurance_number',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_address'
        ]

    def verify_sensitive_data(self, field_name, value):
        """التحقق من صحة البيانات الحساسة المشفرة (مثل البريد أو الهوية)"""
        encrypted = getattr(self, field_name)
        if not encrypted:
            return False
        return check_password(str(value), encrypted)

    def get_age(self):
        """حساب عمر الموظف بناءً على تاريخ الميلاد"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < 
            (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def age(self):
        """خاصية العمر"""
        return self.get_age()
    
    @property
    def years_of_service(self):
        """حساب سنوات الخدمة"""
        if self.status == self.TERMINATED and self.termination_date:
            end_date = self.termination_date
        else:
            end_date = date.today()
        
        years = end_date.year - self.join_date.year
        if (end_date.month, end_date.day) < (self.join_date.month, self.join_date.day):
            years -= 1
        return years
    
    @property
    def months_of_service(self):
        """حساب شهور الخدمة الإجمالية"""
        if self.status == self.TERMINATED and self.termination_date:
            end_date = self.termination_date
        else:
            end_date = date.today()
        
        months = (end_date.year - self.join_date.year) * 12
        months += end_date.month - self.join_date.month
        
        if end_date.day < self.join_date.day:
            months -= 1
            
        return months
    
    @property
    def is_active(self):
        """هل الموظف نشط"""
        return self.status == self.ACTIVE
    
    @property
    def is_in_probation(self):
        """هل الموظف في فترة التجربة"""
        if not self.probation_end_date:
            return False
        return date.today() <= self.probation_end_date
    
    @property
    def contract_remaining_days(self):
        """عدد الأيام المتبقية في العقد"""
        if not self.contract_end_date:
            return None
        if self.contract_end_date < date.today():
            return 0
        return (self.contract_end_date - date.today()).days
    
    @property
    def is_contract_expiring_soon(self, days=30):
        """هل العقد ينتهي قريباً (خلال 30 يوم افتراضياً)"""
        remaining = self.contract_remaining_days
        return remaining is not None and 0 <= remaining <= days
    
    @property
    def passport_expiring_soon(self, days=90):
        """هل الجواز ينتهي قريباً (خلال 90 يوم افتراضياً)"""
        if not self.passport_expiry_date:
            return False
        remaining = (self.passport_expiry_date - date.today()).days
        return 0 <= remaining <= days
    
    @property
    def visa_expiring_soon(self, days=90):
        """هل التأشيرة تنتهي قريباً (خلال 90 يوم افتراضياً)"""
        if not self.visa_expiry_date:
            return False
        remaining = (self.visa_expiry_date - date.today()).days
        return 0 <= remaining <= days
    
    @property
    def full_address(self):
        """العنوان الكامل"""
        if not self.address:
            return None
        
        parts = [self.address]
        if self.city:
            parts.append(self.city)
        if self.state_province:
            parts.append(self.state_province)
        if self.country and self.country != 'Saudi Arabia':
            parts.append(self.country)
        if self.postal_code:
            parts.append(self.postal_code)
        
        return ', '.join(parts)
    
    @property
    def hierarchy_level(self):
        """مستوى الموظف في الهيكل التنظيمي"""
        level = 0
        manager = self.direct_manager
        while manager and level < 10:  # تجنب الحلقة اللانهائية
            level += 1
            manager = manager.direct_manager
        return level
    
    def get_subordinates_count(self):
        """عدد المرؤوسين المباشرين"""
        return self.subordinates_enhanced.filter(status=self.ACTIVE).count()
    
    def get_all_subordinates(self):
        """جميع المرؤوسين (مباشرين وغير مباشرين)"""
        subordinates = []
        direct_subordinates = self.subordinates_enhanced.filter(status=self.ACTIVE)
        
        for subordinate in direct_subordinates:
            subordinates.append(subordinate)
            subordinates.extend(subordinate.get_all_subordinates())
        
        return subordinates
    
    def get_management_chain(self):
        """سلسلة الإدارة من الموظف إلى أعلى مستوى"""
        chain = [self]
        manager = self.direct_manager
        
        while manager and len(chain) < 10:  # تجنب الحلقة اللانهائية
            chain.append(manager)
            manager = manager.direct_manager
        
        return chain
    
    def can_approve_for(self, employee):
        """هل يمكن لهذا الموظف الموافقة على طلبات موظف آخر"""
        if not employee or employee == self:
            return False
        
        # التحقق من كون هذا الموظف في سلسلة الإدارة للموظف الآخر
        management_chain = employee.get_management_chain()
        return self in management_chain[1:]  # استبعاد الموظف نفسه
    
    def get_display_name(self):
        """اسم العرض (الاسم + الوظيفة)"""
        name = self.full_name
        if self.position:
            name += f" - {self.position.title}"
        return name
    
    @property
    def bmi(self):
        """حساب مؤشر كتلة الجسم"""
        if not self.height or not self.weight:
            return None
        height_m = self.height / 100  # تحويل من سم إلى متر
        return round(self.weight / (height_m ** 2), 2)
    
    @property
    def bmi_category(self):
        """تصنيف مؤشر كتلة الجسم"""
        bmi = self.bmi
        if not bmi:
            return None
        
        if bmi < 18.5:
            return _('نحيف')
        elif bmi < 25:
            return _('طبيعي')
        elif bmi < 30:
            return _('زيادة وزن')
        else:
            return _('سمنة')
    
    def get_upcoming_documents_expiry(self, days=90):
        """الحصول على الوثائق التي ستنتهي صلاحيتها قريباً"""
        expiring_docs = []
        today = date.today()
        
        if self.passport_expiry_date:
            remaining = (self.passport_expiry_date - today).days
            if 0 <= remaining <= days:
                expiring_docs.append({
                    'type': _('جواز السفر'),
                    'expiry_date': self.passport_expiry_date,
                    'days_remaining': remaining
                })
        
        if self.visa_expiry_date:
            remaining = (self.visa_expiry_date - today).days
            if 0 <= remaining <= days:
                expiring_docs.append({
                    'type': _('التأشيرة'),
                    'expiry_date': self.visa_expiry_date,
                    'days_remaining': remaining
                })
        
        if self.contract_end_date:
            remaining = (self.contract_end_date - today).days
            if 0 <= remaining <= days:
                expiring_docs.append({
                    'type': _('العقد'),
                    'expiry_date': self.contract_end_date,
                    'days_remaining': remaining
                })
        
        return sorted(expiring_docs, key=lambda x: x['days_remaining'])
    
    def get_service_milestones(self):
        """الحصول على معالم الخدمة (سنوات مهمة)"""
        years = self.years_of_service
        milestones = []
        
        milestone_years = [1, 5, 10, 15, 20, 25, 30]
        for milestone in milestone_years:
            if years >= milestone:
                milestones.append({
                    'years': milestone,
                    'achieved': True,
                    'date': self.join_date.replace(year=self.join_date.year + milestone)
                })
            else:
                milestones.append({
                    'years': milestone,
                    'achieved': False,
                    'date': self.join_date.replace(year=self.join_date.year + milestone)
                })
        
        return milestones
    
    def calculate_detailed_service_period(self):
        """حساب فترة الخدمة بالتفصيل (سنوات، شهور، أيام)"""
        if self.status == self.TERMINATED and self.termination_date:
            end_date = self.termination_date
        else:
            end_date = date.today()
        
        # حساب الفرق
        years = end_date.year - self.join_date.year
        months = end_date.month - self.join_date.month
        days = end_date.day - self.join_date.day
        
        # تعديل الحسابات
        if days < 0:
            months -= 1
            # الحصول على عدد أيام الشهر السابق
            if end_date.month == 1:
                prev_month = 12
                prev_year = end_date.year - 1
            else:
                prev_month = end_date.month - 1
                prev_year = end_date.year
            
            from calendar import monthrange
            days_in_prev_month = monthrange(prev_year, prev_month)[1]
            days += days_in_prev_month
        
        if months < 0:
            years -= 1
            months += 12
        
        return {
            'years': years,
            'months': months,
            'days': days,
            'total_days': (end_date - self.join_date).days,
            'formatted': f"{years} سنة، {months} شهر، {days} يوم"
        }
    
    @property
    def retirement_eligibility(self):
        """التحقق من أهلية التقاعد"""
        age = self.age
        service_years = self.years_of_service
        
        # قواعد التقاعد العامة (يمكن تخصيصها حسب الشركة)
        if age >= 60 or service_years >= 35:
            return {
                'eligible': True,
                'reason': _('بلغ سن التقاعد أو أكمل سنوات الخدمة المطلوبة'),
                'retirement_date': None
            }
        elif age >= 55 and service_years >= 25:
            return {
                'eligible': True,
                'reason': _('التقاعد المبكر'),
                'retirement_date': None
            }
        else:
            # حساب تاريخ التقاعد المتوقع
            years_to_retirement = max(60 - age, 35 - service_years)
            retirement_date = date.today().replace(year=date.today().year + years_to_retirement)
            
            return {
                'eligible': False,
                'reason': f"متبقي {years_to_retirement} سنة للتقاعد",
                'retirement_date': retirement_date
            }
    
    def get_salary_history_summary(self):
        """ملخص تاريخ الرواتب (يتطلب نموذج تاريخ الرواتب)"""
        # هذا مثال - يحتاج لنموذج SalaryHistory منفصل
        return {
            'current_salary': self.base_salary,
            'currency': self.salary_currency,
            'last_increase_date': None,  # يحتاج لنموذج منفصل
            'total_increases': 0,  # يحتاج لنموذج منفصل
            'average_annual_increase': 0  # يحتاج لنموذج منفصل
        }
    
    def clean(self):
        """التحقق من صحة البيانات المتقدم"""
        errors = {}
        
        # التحقق من تاريخ الميلاد
        if self.date_of_birth and self.date_of_birth >= date.today():
            errors['date_of_birth'] = _('تاريخ الميلاد يجب أن يكون في الماضي')
        
        # التحقق من العمر المنطقي
        if self.date_of_birth:
            age = self.get_age()
            if age < 16:
                errors['date_of_birth'] = _('عمر الموظف يجب أن يكون 16 سنة على الأقل')
            elif age > 80:
                errors['date_of_birth'] = _('عمر الموظف يبدو غير منطقي')
        
        # التحقق من تاريخ التعيين
        if self.join_date and self.join_date > date.today():
            errors['join_date'] = _('تاريخ التعيين لا يمكن أن يكون في المستقبل')
        
        # التحقق من فترة التجربة
        if self.probation_end_date and self.probation_end_date <= self.join_date:
            errors['probation_end_date'] = _('تاريخ انتهاء فترة التجربة يجب أن يكون بعد تاريخ التعيين')
        
        # التحقق من تواريخ العقد
        if self.contract_start_date and self.contract_end_date:
            if self.contract_start_date >= self.contract_end_date:
                errors['contract_end_date'] = _('تاريخ بداية العقد يجب أن يكون قبل تاريخ النهاية')
        
        # التحقق من تاريخ إنهاء الخدمة
        if self.termination_date:
            if self.termination_date <= self.join_date:
                errors['termination_date'] = _('تاريخ إنهاء الخدمة يجب أن يكون بعد تاريخ التعيين')
            if self.status != self.TERMINATED:
                errors['status'] = _('يجب تغيير حالة الموظف إلى "منتهي الخدمة" عند تحديد تاريخ إنهاء الخدمة')
        
        # التحقق من المدير المباشر
        if self.direct_manager:
            if self.direct_manager == self:
                errors['direct_manager'] = _('الموظف لا يمكن أن يكون مديراً لنفسه')
            if self.direct_manager.company != self.company:
                errors['direct_manager'] = _('المدير المباشر يجب أن يكون من نفس الشركة')
        
        # التحقق من تواريخ الجواز
        if self.passport_issue_date and self.passport_expiry_date:
            if self.passport_issue_date >= self.passport_expiry_date:
                errors['passport_expiry_date'] = _('تاريخ انتهاء الجواز يجب أن يكون بعد تاريخ الإصدار')
        
        # التحقق من الوزن والطول
        if self.height and self.weight:
            bmi = self.weight / ((self.height / 100) ** 2)
            if bmi < 10 or bmi > 50:
                errors['weight'] = _('نسبة الوزن إلى الطول تبدو غير منطقية')
        
        if errors:
            raise ValidationError(errors)
    
    def get_contact_info(self):
        """معلومات الاتصال (غير مشفرة للعرض)"""
        return {
            'work_email': self.work_email,
            'city': self.city,
            'state_province': self.state_province,
            'country': self.country,
            'postal_code': self.postal_code,
        }
    
    def has_expired_documents(self):
        """هل لدى الموظف وثائق منتهية الصلاحية"""
        today = date.today()
        expired = []
        
        if self.passport_expiry_date and self.passport_expiry_date < today:
            expired.append('passport')
        
        if self.visa_expiry_date and self.visa_expiry_date < today:
            expired.append('visa')
        
        if self.contract_end_date and self.contract_end_date < today:
            expired.append('contract')
        
        return expired
    
    def get_upcoming_expirations(self, days=90):
        """الوثائق التي ستنتهي صلاحيتها قريباً"""
        today = date.today()
        upcoming = []
        
        documents = [
            ('passport', self.passport_expiry_date),
            ('visa', self.visa_expiry_date),
            ('contract', self.contract_end_date),
        ]
        
        for doc_type, expiry_date in documents:
            if expiry_date:
                days_remaining = (expiry_date - today).days
                if 0 <= days_remaining <= days:
                    upcoming.append({
                        'document': doc_type,
                        'expiry_date': expiry_date,
                        'days_remaining': days_remaining
                    })
        
        return upcoming
    
    def calculate_bmi(self):
        """حساب مؤشر كتلة الجسم"""
        if not self.height or not self.weight:
            return None
        return round(self.weight / ((self.height / 100) ** 2), 2)
    
    def get_bmi_category(self):
        """تصنيف مؤشر كتلة الجسم"""
        bmi = self.calculate_bmi()
        if not bmi:
            return None
        
        if bmi < 18.5:
            return _('نحيف')
        elif bmi < 25:
            return _('طبيعي')
        elif bmi < 30:
            return _('زيادة وزن')
        else:
            return _('سمنة')
    
    def needs_evaluation(self):
        """هل يحتاج الموظف لتقييم"""
        if not self.next_evaluation_date:
            return True
        return date.today() >= self.next_evaluation_date
    
    def get_service_duration_text(self):
        """نص مدة الخدمة بالعربية"""
        years = self.years_of_service
        months = self.months_of_service % 12
        
        text_parts = []
        if years > 0:
            if years == 1:
                text_parts.append(_('سنة واحدة'))
            elif years == 2:
                text_parts.append(_('سنتان'))
            elif years <= 10:
                text_parts.append(f'{years} {_("سنوات")}')
            else:
                text_parts.append(f'{years} {_("سنة")}')
        
        if months > 0:
            if months == 1:
                text_parts.append(_('شهر واحد'))
            elif months == 2:
                text_parts.append(_('شهران'))
            elif months <= 10:
                text_parts.append(f'{months} {_("أشهر")}')
            else:
                text_parts.append(f'{months} {_("شهراً")}')
        
        if not text_parts:
            return _('أقل من شهر')
        
        return ' و '.join(text_parts)