"""
Company Models for HRMS
Handles company-level information and settings
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings


class Company(models.Model):
    """
    Company model for multi-company HRMS support
    Stores company information, branding, and configuration
    """
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الشركة"),
        help_text=_("الاسم التجاري للشركة")
    )
    
    legal_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الاسم القانوني"),
        help_text=_("الاسم القانوني المسجل للشركة")
    )
    
    # Registration Information
    tax_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("الرقم الضريبي"),
        validators=[
            RegexValidator(
                regex=r'^[0-9A-Za-z\-]+$',
                message=_("الرقم الضريبي يجب أن يحتوي على أرقام وحروف فقط")
            )
        ]
    )
    
    registration_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم السجل التجاري"),
        help_text=_("رقم السجل التجاري للشركة")
    )
    
    # Contact Information
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )
    
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
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
    
    # Branding
    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار الشركة")
    )
    
    primary_color = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name=_("اللون الأساسي"),
        help_text=_("اللون الأساسي لواجهة النظام (Hex Color)")
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default="#6c757d",
        verbose_name=_("اللون الثانوي"),
        help_text=_("اللون الثانوي لواجهة النظام (Hex Color)")
    )
    
    # Business Information
    industry = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("نوع النشاط")
    )
    
    established_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )
    
    employee_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد الموظفين"),
        help_text=_("العدد التقريبي للموظفين")
    )
    
    # System Configuration
    timezone = models.CharField(
        max_length=50,
        default="Africa/Cairo",
        verbose_name=_("المنطقة الزمنية")
    )
    
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة"),
        help_text=_("رمز العملة (ISO 4217)")
    )
    
    fiscal_year_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("بداية السنة المالية")
    )
    
    # HR Settings (stored as JSON)
    hr_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الموارد البشرية"),
        help_text=_("إعدادات خاصة بنظام الموارد البشرية")
    )
    
    # Payroll Settings
    payroll_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الرواتب"),
        help_text=_("إعدادات خاصة بنظام الرواتب")
    )
    
    # Leave Settings
    leave_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الإجازات"),
        help_text=_("إعدادات خاصة بنظام الإجازات")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_companies',
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
        verbose_name = _("شركة")
        verbose_name_plural = _("الشركات")
        db_table = 'hrms_company'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['tax_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_active_employees_count(self):
        """Get count of active employees in this company"""
        return self.employees.filter(status='active').count()
    
    def get_departments_count(self):
        """Get count of departments in this company"""
        return self.departments.filter(is_active=True).count()
    
    def get_branches_count(self):
        """Get count of branches in this company"""
        return self.branches.filter(is_active=True).count()
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.country:
            address_parts.append(self.country)
        if self.postal_code:
            address_parts.append(self.postal_code)
        return ", ".join(address_parts)
    
    def save(self, *args, **kwargs):
        """Override save to set default settings"""
        if not self.hr_settings:
            self.hr_settings = {
                'working_hours_per_day': 8,
                'working_days_per_week': 5,
                'probation_period_days': 90,
                'notice_period_days': 30,
                'overtime_rate': 1.5,
                'weekend_days': [5, 6],  # Friday and Saturday
            }
        
        if not self.payroll_settings:
            self.payroll_settings = {
                'pay_frequency': 'monthly',
                'pay_day': 1,  # 1st of each month
                'tax_calculation_method': 'progressive',
                'social_insurance_rate': 0.14,
                'health_insurance_rate': 0.01,
            }
        
        if not self.leave_settings:
            self.leave_settings = {
                'annual_leave_days': 21,
                'sick_leave_days': 30,
                'maternity_leave_days': 90,
                'paternity_leave_days': 3,
                'carry_forward_limit': 7,
            }
        
        super().save(*args, **kwargs)
