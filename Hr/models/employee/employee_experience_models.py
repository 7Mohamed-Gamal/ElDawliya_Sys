"""
Employee Experience Models for HRMS
Handles employee work experience and career history
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings


class EmployeeExperience(models.Model):
    """
    Employee Experience model for storing work history
    Includes previous jobs, roles, and responsibilities
    """
    
    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='experience',
        verbose_name=_("الموظف")
    )
    
    # Company Information
    company_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الشركة")
    )
    
    company_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("موقع الشركة")
    )
    
    company_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("دولة الشركة")
    )
    
    company_industry = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("مجال عمل الشركة")
    )
    
    # Job Information
    job_title = models.CharField(
        max_length=200,
        verbose_name=_("المسمى الوظيفي")
    )
    
    department = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )
    
    # Employment Type
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
        ('consultant', _('استشاري')),
        ('freelance', _('عمل حر')),
        ('volunteer', _('تطوع')),
    ]
    
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        verbose_name=_("نوع التوظيف")
    )
    
    # Duration and Dates
    start_date = models.DateField(
        verbose_name=_("تاريخ البداية")
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء")
    )
    
    is_current = models.BooleanField(
        default=False,
        verbose_name=_("حالي")
    )
    
    duration_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("المدة (بالشهور)")
    )
    
    # Job Details
    responsibilities = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("المسؤوليات")
    )
    
    achievements = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الإنجازات")
    )
    
    skills_used = models.JSONField(
        default=list,
        verbose_name=_("المهارات المستخدمة"),
        help_text=_("قائمة بالمهارات المستخدمة في هذه الوظيفة")
    )
    
    # Compensation
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الراتب")
    )
    
    currency = models.CharField(
        max_length=3,
        default="EGP",
        null=True,
        blank=True,
        verbose_name=_("العملة")
    )
    
    # Reference Information
    reference_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("اسم المرجع")
    )
    
    reference_contact = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("معلومات الاتصال بالمرجع")
    )
    
    reference_position = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("منصب المرجع")
    )
    
    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق")
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_experience',
        verbose_name=_("تم التحقق بواسطة")
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التحقق")
    )
    
    # Reason for Leaving
    reason_for_leaving = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب ترك العمل")
    )
    
    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Supporting Documents
    experience_certificate = models.FileField(
        upload_to='employee_experience/',
        null=True,
        blank=True,
        verbose_name=_("شهادة الخبرة")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employee_experience',
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
        verbose_name = _("خبرة الموظف")
        verbose_name_plural = _("خبرات الموظفين")
        db_table = 'hrms_employee_experience'
        ordering = ['employee', '-is_current', '-end_date', '-start_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['is_current']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.job_title} ({self.company_name})"
    
    def clean(self):
        """Validate experience data"""
        super().clean()
        
        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ الانتهاء"))
        
        # If current, end date should be null
        if self.is_current and self.end_date:
            raise ValidationError(_("إذا كانت الخبرة حالية، يجب أن يكون تاريخ الانتهاء فارغاً"))
        
        # If not current, end date should be provided
        if not self.is_current and not self.end_date:
            raise ValidationError(_("إذا لم تكن الخبرة حالية، يجب تحديد تاريخ الانتهاء"))
    
    def save(self, *args, **kwargs):
        """Override save to calculate duration"""
        # Calculate duration in months if start and end dates are provided
        if self.start_date:
            if self.end_date:
                # Calculate months between dates
                months = (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
                self.duration_months = months if months > 0 else 1
            elif self.is_current:
                # Calculate months until today for current job
                from django.utils import timezone
                today = timezone.now().date()
                months = (today.year - self.start_date.year) * 12 + (today.month - self.start_date.month)
                self.duration_months = months if months > 0 else 1
        
        super().save(*args, **kwargs)
    
    @property
    def duration_display(self):
        """Get formatted duration"""
        if self.duration_months:
            years = self.duration_months // 12
            months = self.duration_months % 12
            
            if years > 0 and months > 0:
                return f"{years} {_('سنة')} {months} {_('شهر')}"
            elif years > 0:
                return f"{years} {_('سنة')}"
            else:
                return f"{months} {_('شهر')}"
        return _("غير محدد")
    
    @property
    def salary_display(self):
        """Get formatted salary"""
        if self.salary:
            return f"{self.salary:,.2f} {self.currency or ''}"
        return _("غير محدد")