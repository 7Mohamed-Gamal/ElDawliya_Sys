"""
Company Models for HRMS
Handles core company information and settings
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings


class Company(models.Model):
    """
    Company model representing the organization
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
        unique=True,
        verbose_name=_("اسم الشركة")
    )
    
    legal_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الاسم القانوني")
    )
    
    tax_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الرقم الضريبي")
    )
    
    registration_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("رقم السجل التجاري")
    )
    
    # Contact Information
    email = models.EmailField(
        verbose_name=_("البريد الإلكتروني")
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم الهاتف")
    )
    
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
    )
    
    # Address Information
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
    
    # Company Details
    industry = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المجال")
    )
    
    founded_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )
    
    fiscal_year_start = models.DateField(
        verbose_name=_("بداية السنة المالية")
    )
    
    fiscal_year_end = models.DateField(
        verbose_name=_("نهاية السنة المالية")
    )
    
    # Financial Information
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة")
    )
    
    # Company Settings
    company_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الشركة")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
        verbose_name=_("الشعار")
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
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save to set default settings"""
        if not self.company_settings:
            self.company_settings = {
                'leave_approval_required': True,
                'attendance_required': True,
                'default_working_hours': 8,
                'overtime_enabled': True,
                'probation_period_days': 90,
                'notice_period_days': 30
            }
        super().save(*args, **kwargs)
