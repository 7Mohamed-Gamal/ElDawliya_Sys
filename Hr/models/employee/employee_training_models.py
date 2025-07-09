"""
Employee Training Models for HRMS
Handles employee training records and certifications
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


class EmployeeTraining(models.Model):
    """
    Employee Training model for tracking training and development activities
    """
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='trainings',
        verbose_name=_("الموظف")
    )
    
    # Training Information
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان التدريب")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف التدريب")
    )
    
    # Training Provider
    provider = models.CharField(
        max_length=200,
        verbose_name=_("مقدم التدريب")
    )
    
    instructor = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("المدرب")
    )
    
    # Training Type
    TRAINING_TYPES = [
        ('internal', _('تدريب داخلي')),
        ('external', _('تدريب خارجي')),
        ('online', _('تدريب إلكتروني')),
        ('workshop', _('ورشة عمل')),
        ('seminar', _('ندوة')),
        ('conference', _('مؤتمر')),
        ('certification', _('شهادة مهنية')),
        ('orientation', _('تدريب تعريفي')),
        ('safety', _('تدريب سلامة')),
        ('technical', _('تدريب تقني')),
        ('soft_skills', _('مهارات شخصية')),
        ('leadership', _('تدريب قيادي')),
    ]
    
    training_type = models.CharField(
        max_length=20,
        choices=TRAINING_TYPES,
        verbose_name=_("نوع التدريب")
    )
    
    # Dates and Duration
    start_date = models.DateField(
        verbose_name=_("تاريخ البداية")
    )
    
    end_date = models.DateField(
        verbose_name=_("تاريخ النهاية")
    )
    
    duration_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("مدة التدريب (ساعات)")
    )
    
    # Status and Completion
    STATUS_CHOICES = [
        ('planned', _('مخطط')),
        ('in_progress', _('جاري')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
        ('postponed', _('مؤجل')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name=_("الحالة")
    )
    
    completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الإكمال")
    )
    
    # Results and Evaluation
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("النتيجة")
    )
    
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("النتيجة العظمى")
    )
    
    grade = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_("التقدير")
    )
    
    passed = models.BooleanField(
        default=False,
        verbose_name=_("نجح")
    )
    
    # Certificate Information
    certificate_issued = models.BooleanField(
        default=False,
        verbose_name=_("تم إصدار شهادة")
    )
    
    certificate_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم الشهادة")
    )
    
    certificate_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء الشهادة")
    )
    
    certificate_file = models.FileField(
        upload_to='training_certificates/',
        null=True,
        blank=True,
        verbose_name=_("ملف الشهادة")
    )
    
    # Cost Information
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("التكلفة")
    )
    
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة")
    )
    
    # Approval and Authorization
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_trainings',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    # Additional Information
    skills_gained = models.JSONField(
        default=list,
        verbose_name=_("المهارات المكتسبة"),
        help_text=_("قائمة بالمهارات التي تم اكتسابها")
    )
    
    feedback = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("التقييم والملاحظات")
    )
    
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
        related_name='created_trainings',
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
        verbose_name = _("تدريب موظف")
        verbose_name_plural = _("تدريبات الموظفين")
        db_table = 'hrms_employee_training'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'start_date']),
            models.Index(fields=['status']),
            models.Index(fields=['training_type']),
            models.Index(fields=['certificate_expiry']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    def clean(self):
        """Validate training data"""
        super().clean()
        
        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
        
        if self.completion_date and self.start_date:
            if self.completion_date < self.start_date:
                raise ValidationError(_("تاريخ الإكمال لا يمكن أن يكون قبل تاريخ البداية"))
        
        # Validate score
        if self.score and self.max_score:
            if self.score > self.max_score:
                raise ValidationError(_("النتيجة لا يمكن أن تكون أكبر من النتيجة العظمى"))
    
    @property
    def duration_days(self):
        """Calculate training duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    @property
    def is_completed(self):
        """Check if training is completed"""
        return self.status == 'completed'
    
    @property
    def is_certificate_valid(self):
        """Check if certificate is still valid"""
        if self.certificate_issued and self.certificate_expiry:
            from django.utils import timezone
            return timezone.now().date() <= self.certificate_expiry
        return self.certificate_issued
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.score and self.max_score and self.max_score > 0:
            return round((self.score / self.max_score) * 100, 2)
        return None
    
    def mark_completed(self, completion_date=None, score=None, passed=False):
        """Mark training as completed"""
        from django.utils import timezone
        
        self.status = 'completed'
        self.completion_date = completion_date or timezone.now().date()
        if score is not None:
            self.score = score
        self.passed = passed
        self.save()
    
    def issue_certificate(self, certificate_number, expiry_date=None):
        """Issue certificate for completed training"""
        if self.status == 'completed' and self.passed:
            self.certificate_issued = True
            self.certificate_number = certificate_number
            self.certificate_expiry = expiry_date
            self.save()
        else:
            raise ValidationError(_("لا يمكن إصدار شهادة للتدريب غير المكتمل أو غير الناجح"))
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate fields"""
        # Auto-set completion date if status is completed
        if self.status == 'completed' and not self.completion_date:
            from django.utils import timezone
            self.completion_date = timezone.now().date()
        
        # Auto-calculate duration hours if not set
        if not self.duration_hours and self.duration_days:
            # Assume 8 hours per day for multi-day trainings
            if self.duration_days == 1:
                self.duration_hours = 8
            else:
                self.duration_hours = self.duration_days * 8
        
        super().save(*args, **kwargs)
