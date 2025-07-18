"""
Branch Models for HRMS
Handles branch/location information for multi-location companies
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings


class Branch(models.Model):
    """
    Branch model for managing company locations/branches
    Each branch can have its own departments and employees
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationship to Company
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name=_("الشركة")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الفرع"),
        help_text=_("اسم الفرع أو الموقع")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود الفرع"),
        help_text=_("كود فريد للفرع"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]+$',
                message=_("كود الفرع يجب أن يحتوي على أحرف كبيرة وأرقام فقط")
            )
        ]
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف الفرع")
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
    
    fax = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الفاكس")
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
    
    # Geographic Information
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name=_("خط العرض"),
        help_text=_("خط العرض للموقع الجغرافي")
    )
    
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name=_("خط الطول"),
        help_text=_("خط الطول للموقع الجغرافي")
    )
    
    # Management
    manager = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_branches',
        verbose_name=_("مدير الفرع")
    )
    
    # Operational Information
    opening_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت بداية العمل")
    )
    
    closing_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت نهاية العمل")
    )
    
    timezone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("المنطقة الزمنية"),
        help_text=_("المنطقة الزمنية للفرع إذا كانت مختلفة عن الشركة")
    )
    
    # Capacity and Resources
    employee_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("السعة القصوى للموظفين")
    )
    
    floor_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("المساحة (متر مربع)")
    )
    
    parking_spaces = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("عدد أماكن الانتظار")
    )
    
    # Financial Information
    monthly_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الإيجار الشهري")
    )
    
    monthly_utilities = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("المرافق الشهرية")
    )
    
    # Branch Settings
    branch_settings = models.JSONField(
        default=dict,
        verbose_name=_("إعدادات الفرع"),
        help_text=_("إعدادات خاصة بالفرع")
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_headquarters = models.BooleanField(
        default=False,
        verbose_name=_("المقر الرئيسي"),
        help_text=_("هل هذا الفرع هو المقر الرئيسي للشركة؟")
    )
    
    established_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التأسيس")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_branches',
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
        verbose_name = _("فرع")
        verbose_name_plural = _("الفروع")
        db_table = 'hrms_branch'
        ordering = ['company', 'name']
        unique_together = [['company', 'code']]
        indexes = [
            models.Index(fields=['company', 'name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    def get_active_employees_count(self):
        """Get count of active employees in this branch"""
        return self.employees.filter(status='active').count()
    
    def get_departments_count(self):
        """Get count of departments in this branch"""
        return self.departments.filter(is_active=True).count()
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.country:
            address_parts.append(self.country)
        if self.postal_code:
            address_parts.append(self.postal_code)
        return ", ".join(address_parts)
    
    @property
    def coordinates(self):
        """Get coordinates as tuple"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
    
    def save(self, *args, **kwargs):
        """Override save to set default settings and validate"""
        # Set default branch settings
        if not self.branch_settings:
            self.branch_settings = {
                'allow_remote_work': False,
                'require_attendance_machine': True,
                'overtime_approval_required': True,
                'leave_approval_levels': 2,
                'working_hours_per_day': 8,
                'break_duration_minutes': 60,
            }
        
        # Ensure only one headquarters per company
        if self.is_headquarters:
            Branch.objects.filter(
                company=self.company,
                is_headquarters=True
            ).exclude(pk=self.pk).update(is_headquarters=False)
        
        # Auto-generate code if not provided
        if not self.code:
            company_code = self.company.name[:3].upper()
            branch_count = Branch.objects.filter(company=self.company).count()
            self.code = f"{company_code}-BR{branch_count + 1:03d}"
        
        super().save(*args, **kwargs)
