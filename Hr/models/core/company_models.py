"""
Company and Branch Models for HRMS
Handles company structure, branches, and organizational hierarchy
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.conf import settings
from django.core.exceptions import ValidationError


class Company(models.Model):
    """
    Company model for managing multiple companies within the system
    Supports multi-tenant architecture with complete company information
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الشركة")
    )
    
    name_english = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الاسم بالإنجليزية")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود الشركة"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]+$',
                message=_("كود الشركة يجب أن يحتوي على أحرف كبيرة وأرقام فقط")
            )
        ]
    )
    
    # Legal Information
    commercial_register = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("رقم السجل التجاري")
    )
    
    tax_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("الرقم الضريبي")
    )
    
    vat_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم ضريبة القيمة المضافة")
    )
    
    # Contact Information
    address = models.TextField(
        verbose_name=_("العنوان")
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name=_("المدينة")
    )
    
    state = models.CharField(
        max_length=100,
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
    
    phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم الهاتف"),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("رقم الهاتف يجب أن يكون صالحاً")
            )
        ]
    )
    
    fax = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الفاكس")
    )
    
    email = models.EmailField(
        verbose_name=_("البريد الإلكتروني"),
        validators=[EmailValidator()]
    )
    
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
    )
    
    # Company Logo and Branding
    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
        verbose_name=_("شعار الشركة")
    )
    
    # Business Information
    BUSINESS_TYPES = [
        ('corporation', _('شركة مساهمة')),
        ('llc', _('شركة ذات مسؤولية محدودة')),
        ('partnership', _('شراكة')),
        ('sole_proprietorship', _('مؤسسة فردية')),
        ('government', _('جهة حكومية')),
        ('ngo', _('منظمة غير ربحية')),
        ('other', _('أخرى')),
    ]
    
    business_type = models.CharField(
        max_length=30,
        choices=BUSINESS_TYPES,
        default='llc',
        verbose_name=_("نوع النشاط التجاري")
    )
    
    industry = models.CharField(
        max_length=100,
        verbose_name=_("القطاع/الصناعة")
    )
    
    established_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )
    
    # Financial Information
    CURRENCIES = [
        ('EGP', _('جنيه مصري')),
        ('SAR', _('ريال سعودي')),
        ('AED', _('درهم إماراتي')),
        ('USD', _('دولار أمريكي')),
        ('EUR', _('يورو')),
    ]
    
    default_currency = models.CharField(
        max_length=3,
        choices=CURRENCIES,
        default='EGP',
        verbose_name=_("العملة الافتراضية")
    )
    
    fiscal_year_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("بداية السنة المالية")
    )
    
    # System Settings
    timezone = models.CharField(
        max_length=50,
        default='Africa/Cairo',
        verbose_name=_("المنطقة الزمنية")
    )
    
    language = models.CharField(
        max_length=10,
        default='ar',
        verbose_name=_("اللغة الافتراضية")
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
            models.Index(fields=['code']),
            models.Index(fields=['commercial_register']),
            models.Index(fields=['tax_number']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate company data"""
        super().clean()
        
        # Ensure code is uppercase
        if self.code:
            self.code = self.code.upper()
    
    def get_total_employees(self):
        """Get total number of active employees across all branches"""
        return sum(branch.get_total_employees() for branch in self.branches.filter(is_active=True))
    
    def get_total_departments(self):
        """Get total number of departments across all branches"""
        return sum(branch.departments.filter(is_active=True).count() for branch in self.branches.filter(is_active=True))
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate code if not provided"""
        if not self.code:
            # Generate code from company name
            name_parts = self.name.split()
            if len(name_parts) >= 2:
                self.code = ''.join([part[:2].upper() for part in name_parts[:3]])
            else:
                self.code = self.name[:4].upper()
            
            # Ensure uniqueness
            counter = 1
            original_code = self.code
            while Company.objects.filter(code=self.code).exists():
                self.code = f"{original_code}{counter:02d}"
                counter += 1
        
        super().save(*args, **kwargs)


