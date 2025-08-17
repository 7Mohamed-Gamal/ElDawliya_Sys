"""
Employee Shift Assignment Models for HRMS
Handles assignment of work shifts to employees
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date, timedelta


class EmployeeShiftAssignment(models.Model):
    """
    Employee Shift Assignment model for assigning work shifts to employees
    Supports both permanent and temporary shift assignments
    """
    
    # Unique Identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Employee and Shift
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.CASCADE,
        related_name='shift_assignments',
        verbose_name=_("الموظف")
    )
    
    work_shift = models.ForeignKey(
        'WorkShift',
        on_delete=models.CASCADE,
        related_name='employee_assignments',
        verbose_name=_("وردية العمل")
    )
    
    # Assignment Type
    ASSIGNMENT_TYPES = [
        ('permanent', _('دائم')),
        ('temporary', _('مؤقت')),
        ('rotating', _('متناوب')),
        ('flexible', _('مرن')),
        ('on_call', _('عند الطلب')),
    ]
    
    assignment_type = models.CharField(
        max_length=15,
        choices=ASSIGNMENT_TYPES,
        default='permanent',
        verbose_name=_("نوع التعيين")
    )
    
    # Date Range
    start_date = models.DateField(
        verbose_name=_("تاريخ البداية")
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ النهاية"),
        help_text=_("اتركه فارغاً للتعيين الدائم")
    )
    
    # Specific Days (for flexible assignments)
    specific_dates = models.JSONField(
        default=list,
        verbose_name=_("تواريخ محددة"),
        help_text=_("قائمة بالتواريخ المحددة للتعيين المرن")
    )
    
    # Weekly Pattern (for rotating shifts)
    weekly_pattern = models.JSONField(
        default=dict,
        verbose_name=_("النمط الأسبوعي"),
        help_text=_("نمط الوردية الأسبوعية للتناوب")
    )
    
    # Override Settings
    override_shift_settings = models.BooleanField(
        default=False,
        verbose_name=_("تجاوز إعدادات الوردية"),
        help_text=_("هل تريد تجاوز إعدادات الوردية الافتراضية؟")
    )
    
    custom_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت البداية المخصص")
    )
    
    custom_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت النهاية المخصص")
    )
    
    custom_break_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("مدة الراحة المخصصة (دقائق)")
    )
    
    # Approval and Authorization
    requires_approval = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب موافقة")
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_shift_assignments',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    # Status
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('pending', _('معلق')),
        ('expired', _('منتهي')),
        ('cancelled', _('ملغي')),
    ]
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_("الحالة")
    )
    
    # Priority (for overlapping assignments)
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الأولوية"),
        help_text=_("الأولوية في حالة تداخل التعيينات (الأقل رقماً له الأولوية)")
    )
    
    # Reason and Notes
    reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("سبب التعيين")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Automatic Expiry
    auto_expire = models.BooleanField(
        default=True,
        verbose_name=_("انتهاء تلقائي"),
        help_text=_("هل ينتهي التعيين تلقائياً في تاريخ النهاية؟")
    )
    
    # Notification Settings
    notify_employee = models.BooleanField(
        default=True,
        verbose_name=_("إشعار الموظف")
    )
    
    notify_manager = models.BooleanField(
        default=True,
        verbose_name=_("إشعار المدير")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_shift_assignments_employee',
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
        verbose_name = _("تعيين وردية موظف")
        verbose_name_plural = _("تعيينات ورديات الموظفين")
        db_table = 'hrms_employee_shift_assignment'
        ordering = ['-start_date', 'priority']
        indexes = [
            models.Index(fields=['employee', 'start_date']),
            models.Index(fields=['work_shift']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.work_shift.name} ({self.start_date})"
    
    def clean(self):
        """Validate shift assignment data"""
        super().clean()
        
        # Validate date range
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
        
        # Validate custom times
        if self.override_shift_settings:
            if self.custom_start_time and self.custom_end_time:
                if self.custom_start_time >= self.custom_end_time:
                    # This might be valid for night shifts
                    pass
        
        # Check for overlapping assignments
        overlapping = EmployeeShiftAssignment.objects.filter(
            employee=self.employee,
            status='active'
        ).exclude(pk=self.pk)
        
        if self.end_date:
            overlapping = overlapping.filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            )
        else:
            overlapping = overlapping.filter(
                start_date__lte=self.start_date
            )
        
        if overlapping.exists() and self.priority == overlapping.first().priority:
            raise ValidationError(_("يوجد تعيين وردية متداخل بنفس الأولوية"))
    
    @property
    def is_active(self):
        """Check if assignment is currently active"""
        today = date.today()
        if self.status != 'active':
            return False
        
        if today < self.start_date:
            return False
        
        if self.end_date and today > self.end_date:
            return False
        
        return True
    
    @property
    def is_expired(self):
        """Check if assignment has expired"""
        if self.end_date:
            return date.today() > self.end_date
        return False
    
    @property
    def duration_days(self):
        """Calculate assignment duration in days"""
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    @property
    def effective_start_time(self):
        """Get effective start time (custom or shift default)"""
        if self.override_shift_settings and self.custom_start_time:
            return self.custom_start_time
        return self.work_shift.start_time
    
    @property
    def effective_end_time(self):
        """Get effective end time (custom or shift default)"""
        if self.override_shift_settings and self.custom_end_time:
            return self.custom_end_time
        return self.work_shift.end_time
    
    @property
    def effective_break_duration(self):
        """Get effective break duration (custom or shift default)"""
        if self.override_shift_settings and self.custom_break_duration:
            return self.custom_break_duration
        return self.work_shift.break_duration_minutes
    
    def is_applicable_on_date(self, check_date):
        """Check if assignment is applicable on a specific date"""
        if not self.is_active:
            return False
        
        if check_date < self.start_date:
            return False
        
        if self.end_date and check_date > self.end_date:
            return False
        
        # Check specific dates for flexible assignments
        if self.assignment_type == 'flexible' and self.specific_dates:
            return check_date.isoformat() in self.specific_dates
        
        # Check weekly pattern for rotating assignments
        if self.assignment_type == 'rotating' and self.weekly_pattern:
            weekday = check_date.weekday()
            return self.weekly_pattern.get(str(weekday), False)
        
        # For permanent and temporary assignments, check work shift days
        return self.work_shift.is_working_day(check_date.weekday())
    
    def get_shift_for_date(self, check_date):
        """Get shift details for a specific date"""
        if not self.is_applicable_on_date(check_date):
            return None
        
        return {
            'assignment': self,
            'work_shift': self.work_shift,
            'start_time': self.effective_start_time,
            'end_time': self.effective_end_time,
            'break_duration': self.effective_break_duration,
            'is_custom': self.override_shift_settings,
        }
    
    def extend_assignment(self, new_end_date, reason=None):
        """Extend the assignment to a new end date"""
        if self.end_date and new_end_date <= self.end_date:
            raise ValidationError(_("التاريخ الجديد يجب أن يكون بعد تاريخ النهاية الحالي"))
        
        old_end_date = self.end_date
        self.end_date = new_end_date
        
        if reason:
            self.notes = f"{self.notes or ''}\nتم تمديد التعيين من {old_end_date} إلى {new_end_date}. السبب: {reason}"
        
        self.save()
    
    def terminate_assignment(self, termination_date=None, reason=None):
        """Terminate the assignment"""
        termination_date = termination_date or date.today()
        
        if termination_date < self.start_date:
            raise ValidationError(_("تاريخ الإنهاء لا يمكن أن يكون قبل تاريخ البداية"))
        
        self.end_date = termination_date
        self.status = 'cancelled'
        
        if reason:
            self.notes = f"{self.notes or ''}\nتم إنهاء التعيين في {termination_date}. السبب: {reason}"
        
        self.save()
    
    def approve_assignment(self, approved_by_user):
        """Approve the shift assignment"""
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.requires_approval = False
        self.status = 'active'
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to handle status updates"""
        # Auto-expire if past end date
        if self.auto_expire and self.end_date and date.today() > self.end_date:
            self.status = 'expired'
        
        # Set default weekly pattern for rotating shifts
        if self.assignment_type == 'rotating' and not self.weekly_pattern:
            self.weekly_pattern = {
                '0': True,  # Monday
                '1': True,  # Tuesday
                '2': True,  # Wednesday
                '3': True,  # Thursday
                '4': True,  # Friday
                '5': False, # Saturday
                '6': False, # Sunday
            }
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_assignment_for_employee_date(cls, employee, check_date):
        """Get the active shift assignment for an employee on a specific date"""
        assignments = cls.objects.filter(
            employee=employee,
            status='active',
            start_date__lte=check_date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=check_date)
        ).order_by('priority', '-start_date')
        
        for assignment in assignments:
            if assignment.is_applicable_on_date(check_date):
                return assignment
        
        return None
