"""
Employee Models for HRMS
Handles all employee information and sensitive data
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import (
    make_password,
    is_password_usable,
    check_password
)
from django.conf import settings
import uuid
from datetime import date


class Employee(models.Model):
    """
    Main employee model containing sensitive and personal information
    with proper encryption for sensitive fields
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
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
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
        verbose_name=_("الاسم الأخير")
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name=_("النوع")
    )
    
    date_of_birth = models.DateField(
        verbose_name=_("تاريخ الميلاد")
    )
    
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_CHOICES,
        default=SINGLE,
        verbose_name=_("الحالة الاجتماعية")
    )
    
    # Contact Information - Encrypted
    private_email = models.CharField(
        max_length=254,
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني الشخصي"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    mobile_phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم الجوال"),
        help_text=_("يتم تشفير هذه البيانات")
    )
    
    # Employment Information
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
    
    company = models.ForeignKey(
        'Hr.Company',
        on_delete=models.CASCADE,
        verbose_name=_("الشركة")
    )

    department = models.ForeignKey(
        'Hr.Department', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )

    position = models.ForeignKey(
        'Hr.JobPosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("الوظيفة")
    )

    # Financial Information - Encrypted
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

    # Government Documents - Encrypted
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

    # Status Options
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    TERMINATED = 'terminated'
    
    STATUS_CHOICES = (
        (ACTIVE, _('نشط')),
        (SUSPENDED, _('موقوف')),
        (TERMINATED, _('منتهي الخدمة')),
    )
    
    # Status Information
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

    # Timestamps
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
        verbose_name_plural = _("الموظفين")
        db_table = 'hrms_employee'
        ordering = ['company', 'department', 'position', 'employee_id']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['national_id']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    @property  
    def full_name(self):
        """Returns the employee's full name"""
        names = [self.first_name]
        if self.middle_name:
            names.append(self.middle_name)
        names.append(self.last_name)
        return ' '.join(names)

    def save(self, *args, **kwargs):
        """Override save to encrypt sensitive fields and generate IDs"""
        if not self.employee_id:
            # Generate employee ID using company code and sequence
            company_code = self.company.name[:3].upper()
            last_emp = Employee.objects.filter(
                company=self.company
            ).order_by('-employee_id').first()
            last_seq = int(last_emp.employee_id[-5:]) if last_emp else 0
            self.employee_id = f"{company_code}-{last_seq+1:05d}"
            self.employee_number = self.employee_id  # Set both fields to same value

        # Encrypt sensitive fields before saving
        if hasattr(self, '_sensitive_fields'):
            for field in self._sensitive_fields:
                value = getattr(self, field)
                if value and not value.startswith('$pbkdf2-sha256$'):
                    setattr(self, field, make_password(value))

        super().save(*args, **kwargs)

    @property
    def _sensitive_fields(self):
        """List of fields that should be encrypted"""
        return [
            'private_email',
            'mobile_phone',
            'bank_account_number',
            'iban',
            'national_id',
            'passport_number'
        ]

    def verify_sensitive_data(self, field_name, value):
        """Verify encrypted sensitive data"""
        encrypted = getattr(self, field_name)
        return check_password(value, encrypted)

    def get_age(self):
        """Calculate employee age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < 
            (self.date_of_birth.month, self.date_of_birth.day)
        )
