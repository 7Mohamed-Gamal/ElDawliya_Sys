"""
Employee Education Models for HRMS
Handles employee education history and qualifications
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings


class EmployeeEducation(models.Model):
    """
    Employee Education model for storing educational qualifications
    Includes degrees, certifications, and training courses
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
        'Employee',
        on_delete=models.CASCADE,
        related_name='education',
        verbose_name=_("الموظف")
    )
    
    # Education Type
    EDUCATION_TYPE_CHOICES = [
        ('school', _('تعليم مدرسي')),
        ('diploma', _('دبلوم')),
        ('bachelor', _('بكالوريوس')),
        ('master', _('ماجستير')),
        ('phd', _('دكتوراه')),
        ('certification', _('شهادة مهنية')),
        ('course', _('دورة تدريبية')),
        ('other', _('أخرى')),
    ]
    
    education_type = models.CharField(
        max_length=20,
        choices=EDUCATION_TYPE_CHOICES,
        verbose_name=_("نوع التعليم")
    )
    
    # Institution Information
    institution_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم المؤسسة التعليمية")
    )
    
    institution_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("موقع المؤسسة")
    )
    
    institution_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("دولة المؤسسة")
    )
    
    # Degree/Qualification Information
    degree_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الدرجة/المؤهل")
    )
    
    field_of_study = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("مجال الدراسة")
    )
    
    specialization = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("التخصص")
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
    
    # Performance and Results
    grade = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الدرجة/التقدير")
    )
    
    score = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الدرجة/المعدل")
    )
    
    score_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("نوع الدرجة"),
        help_text=_("مثل: GPA، النسبة المئوية، إلخ")
    )
    
    # Certificate Information
    certificate_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم الشهادة")
    )
    
    certificate_file = models.FileField(
        upload_to='employee_certificates/',
        null=True,
        blank=True,
        verbose_name=_("ملف الشهادة")
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
        related_name='verified_education',
        verbose_name=_("تم التحقق بواسطة")
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التحقق")
    )
    
    # Additional Information
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف")
    )
    
    achievements = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الإنجازات")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employee_education',
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
        verbose_name = _("تعليم الموظف")
        verbose_name_plural = _("تعليم الموظفين")
        db_table = 'hrms_employee_education'
        ordering = ['employee', '-end_date', '-start_date']
        indexes = [
            models.Index(fields=['employee', 'education_type']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.degree_name} ({self.institution_name})"
    
    def clean(self):
        """Validate education data"""
        super().clean()
        
        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ الانتهاء"))
        
        # If current, end date should be null
        if self.is_current and self.end_date:
            raise ValidationError(_("إذا كان التعليم حالياً، يجب أن يكون تاريخ الانتهاء فارغاً"))
        
        # If not current, end date should be provided
        if not self.is_current and not self.end_date:
            raise ValidationError(_("إذا لم يكن التعليم حالياً، يجب تحديد تاريخ الانتهاء"))
    
    def save(self, *args, **kwargs):
        """Override save to calculate duration"""
        # Calculate duration in months if start and end dates are provided
        if self.start_date and self.end_date:
            # Calculate months between dates
            months = (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
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