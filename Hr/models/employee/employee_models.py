"""
Employee Models for HRMS
Comprehensive employee management with personal and professional information
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from cryptography.fernet import Fernet


class EncryptedField(models.CharField):
    """
    Custom field for encrypting sensitive data
    """
    def __init__(self, *args, **kwargs):
        # Get encryption key from settings or generate one
        try:
            from django.conf import settings
            if hasattr(settings, 'ENCRYPTION_KEY'):
                self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
            else:
                # Generate a key for development (should be in settings for production)
                key = Fernet.generate_key()
                self.cipher = Fernet(key)
        except Exception:
            # Fallback - no encryption in case of issues
            self.cipher = None
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if decryption fails
    
    def to_python(self, value):
        return value
    
    def get_prep_value(self, value):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if encryption fails


class Employee(models.Model):
    """
    Comprehensive Employee model for HRMS
    Stores all employee information including personal, professional, and employment details
    """
    
    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Unique Identifier
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("رقم الموظف"),
        help_text=_("رقم فريد للموظف"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]+$',
                message=_("رقم الموظف يجب أن يحتوي على أحرف كبيرة وأرقام فقط")
            )
        ]
    )
    
    # Organizational Relationships
    company = models.ForeignKey(
        'Hr.Company',
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name=_("الشركة")
    )

    branch = models.ForeignKey(
        'Hr.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("الفرع")
    )

    department = models.ForeignKey(
        'Hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("القسم")
    )

    job_position = models.ForeignKey(
        'Hr.JobPosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("الوظيفة")
    )
    
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("المدير المباشر")
    )
    
    # Personal Information
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("الاسم الأول")
    )
    
    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم الأوسط")
    )
    
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("اسم العائلة")
    )
    
    full_name = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name=_("الاسم الكامل")
    )
    
    full_name_english = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name=_("الاسم الكامل بالإنجليزية")
    )
    
    # Contact Information
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني"),
        validators=[EmailValidator()]
    )
    
    personal_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني الشخصي")
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )
    
    mobile = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الجوال")
    )
    
    # Identification Information (Encrypted)
    national_id = EncryptedField(
        max_length=200,  # Increased for encrypted data
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("رقم الهوية الوطنية")
    )
    
    passport_number = EncryptedField(
        max_length=200,  # Increased for encrypted data
        null=True,
        blank=True,
        verbose_name=_("رقم جواز السفر")
    )
    
    passport_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء جواز السفر")
    )
    
    # Personal Details
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الميلاد")
    )
    
    GENDER_CHOICES = [
        ('male', _('ذكر')),
        ('female', _('أنثى')),
    ]
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("الجنس")
    )
    
    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
    ]
    
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("الحالة الاجتماعية")
    )
    
    nationality = models.CharField(
        max_length=50,
        default="مصري",
        verbose_name=_("الجنسية")
    )
    
    religion = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الديانة")
    )
    
    # Address Information
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان")
    )
    
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المدينة")
    )
    
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المحافظة/الولاية")
    )
    
    country = models.CharField(
        max_length=100,
        default="مصر",
        verbose_name=_("الدولة")
    )
    
    postal_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الرمز البريدي")
    )
    
    # Employment Information
    hire_date = models.DateField(
        verbose_name=_("تاريخ التوظيف")
    )
    
    probation_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء فترة التجربة")
    )
    
    confirmation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التثبيت")
    )
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
        ('consultant', _('استشاري')),
    ]
    
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        verbose_name=_("نوع التوظيف")
    )
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('on_leave', _('في إجازة')),
        ('suspended', _('موقوف')),
        ('terminated', _('منتهي الخدمة')),
        ('resigned', _('مستقيل')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_("حالة الموظف")
    )
    
    # Salary Information
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الراتب الأساسي")
    )
    
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة")
    )
    
    # Banking Information (Encrypted)
    bank_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم البنك")
    )
    
    bank_account_number = EncryptedField(
        max_length=200,  # Increased for encrypted data
        null=True,
        blank=True,
        verbose_name=_("رقم الحساب البنكي")
    )
    
    iban = EncryptedField(
        max_length=200,  # Increased for encrypted data
        null=True,
        blank=True,
        verbose_name=_("رقم الآيبان")
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("اسم جهة الاتصال في حالات الطوارئ")
    )
    
    emergency_contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("هاتف جهة الاتصال في حالات الطوارئ")
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("صلة القرابة")
    )
    
    # Profile and System
    profile_picture = models.ImageField(
        upload_to='employee_profiles/',
        null=True,
        blank=True,
        verbose_name=_("صورة شخصية")
    )
    
    user_account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name=_("حساب المستخدم")
    )
    
    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees',
        verbose_name=_("أنشئ بواسطة")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفون")
        db_table = 'hrms_employee'
        ordering = ['employee_number']
        indexes = [
            models.Index(fields=['employee_number']),
            models.Index(fields=['email']),
            models.Index(fields=['national_id']),
            models.Index(fields=['status']),
            models.Index(fields=['company', 'department']),
            models.Index(fields=['hire_date']),
        ]
    
    def __str__(self):
        return f"{self.full_name or self.first_name} ({self.employee_number})"
    
    def clean(self):
        """Validate employee data"""
        super().clean()
        
        # Validate birth date
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError(_("تاريخ الميلاد لا يمكن أن يكون في المستقبل"))
        
        # Validate hire date
        if self.hire_date and self.hire_date > date.today():
            raise ValidationError(_("تاريخ التوظيف لا يمكن أن يكون في المستقبل"))
        
        # Validate probation end date
        if self.probation_end_date and self.hire_date:
            if self.probation_end_date <= self.hire_date:
                raise ValidationError(_("تاريخ انتهاء فترة التجربة يجب أن يكون بعد تاريخ التوظيف"))
        
        # Validate organizational relationships
        if self.department and self.company:
            if self.department.company != self.company:
                raise ValidationError(_("القسم يجب أن ينتمي لنفس الشركة"))
        
        if self.branch and self.company:
            if self.branch.company != self.company:
                raise ValidationError(_("الفرع يجب أن ينتمي لنفس الشركة"))
    
    @property
    def age(self):
        """Calculate employee age"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    @property
    def years_of_service(self):
        """Calculate years of service"""
        if self.hire_date:
            today = date.today()
            return today.year - self.hire_date.year - (
                (today.month, today.day) < (self.hire_date.month, self.hire_date.day)
            )
        return None
    
    @property
    def is_on_probation(self):
        """Check if employee is still on probation"""
        if self.probation_end_date:
            return date.today() <= self.probation_end_date
        return False
    
    def get_direct_reports(self):
        """Get employees who report directly to this employee"""
        return Employee.objects.filter(manager=self, status='active')
    
    def get_all_subordinates(self):
        """Get all subordinates recursively"""
        subordinates = []
        for direct_report in self.get_direct_reports():
            subordinates.append(direct_report)
            subordinates.extend(direct_report.get_all_subordinates())
        return subordinates
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate fields"""
        # Auto-generate full name
        if not self.full_name:
            name_parts = [self.first_name]
            if self.middle_name:
                name_parts.append(self.middle_name)
            name_parts.append(self.last_name)
            self.full_name = ' '.join(name_parts)
        
        # Auto-generate employee number if not provided
        if not self.employee_number:
            company_code = self.company.name[:3].upper()
            year = timezone.now().year
            emp_count = Employee.objects.filter(company=self.company).count()
            self.employee_number = f"{company_code}{year}{emp_count + 1:04d}"
        
        # Set probation end date if not set
        if not self.probation_end_date and self.hire_date:
            probation_days = 90  # Default probation period
            if self.job_position and self.job_position.job_settings.get('probation_period_days'):
                probation_days = self.job_position.job_settings['probation_period_days']
            self.probation_end_date = self.hire_date + timedelta(days=probation_days)
        
        super().save(*args, **kwargs)
