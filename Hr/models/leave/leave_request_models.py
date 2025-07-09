"""
Leave Request Models for HRMS
Handles leave requests, approvals, and workflow management
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta


class LeaveRequest(models.Model):
    """
    Leave Request model for managing employee leave applications
    Includes approval workflow, balance tracking, and status management
    """
    
    # Basic Information
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_("الموظف")
    )
    
    leave_type = models.ForeignKey(
        'LeaveType',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_("نوع الإجازة")
    )
    
    leave_policy = models.ForeignKey(
        'LeavePolicy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_requests',
        verbose_name=_("سياسة الإجازة")
    )
    
    # Request Details
    start_date = models.DateField(
        verbose_name=_("تاريخ البداية")
    )
    
    end_date = models.DateField(
        verbose_name=_("تاريخ النهاية")
    )
    
    days_requested = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name=_("عدد الأيام المطلوبة")
    )
    
    is_half_day = models.BooleanField(
        default=False,
        verbose_name=_("نصف يوم")
    )
    
    HALF_DAY_PERIODS = [
        ('morning', _('الفترة الصباحية')),
        ('afternoon', _('الفترة المسائية')),
    ]
    
    half_day_period = models.CharField(
        max_length=10,
        choices=HALF_DAY_PERIODS,
        null=True,
        blank=True,
        verbose_name=_("فترة نصف اليوم")
    )
    
    # Reason and Documentation
    reason = models.TextField(
        verbose_name=_("سبب الإجازة")
    )
    
    emergency_contact_during_leave = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("جهة الاتصال أثناء الإجازة")
    )
    
    emergency_phone_during_leave = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("هاتف الطوارئ أثناء الإجازة")
    )
    
    # Supporting Documents
    medical_certificate = models.FileField(
        upload_to='leave_documents/medical/',
        null=True,
        blank=True,
        verbose_name=_("الشهادة الطبية")
    )
    
    supporting_documents = models.FileField(
        upload_to='leave_documents/supporting/',
        null=True,
        blank=True,
        verbose_name=_("المستندات الداعمة")
    )
    
    # Status and Workflow
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مقدم')),
        ('pending_approval', _('في انتظار الموافقة')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغي')),
        ('in_progress', _('جاري')),
        ('completed', _('مكتمل')),
        ('partially_taken', _('مأخوذ جزئياً')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("الحالة")
    )
    
    current_approval_level = models.PositiveIntegerField(
        default=0,
        verbose_name=_("مستوى الموافقة الحالي")
    )
    
    # Balance Information
    balance_before_request = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("الرصيد قبل الطلب")
    )
    
    balance_after_request = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("الرصيد بعد الطلب")
    )
    
    # Actual Leave Taken
    actual_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ البداية الفعلي")
    )
    
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ النهاية الفعلي")
    )
    
    actual_days_taken = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("الأيام المأخوذة فعلياً")
    )
    
    # Return Information
    expected_return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ العودة المتوقع")
    )
    
    actual_return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ العودة الفعلي")
    )
    
    return_confirmed = models.BooleanField(
        default=False,
        verbose_name=_("تم تأكيد العودة")
    )
    
    return_confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_returns',
        verbose_name=_("تم تأكيد العودة بواسطة")
    )
    
    return_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ تأكيد العودة")
    )
    
    # Handover Information
    handover_to = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_handovers',
        verbose_name=_("تسليم المهام إلى")
    )
    
    handover_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات التسليم")
    )
    
    handover_completed = models.BooleanField(
        default=False,
        verbose_name=_("تم التسليم")
    )
    
    # Comments and Notes
    employee_comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تعليقات الموظف")
    )
    
    manager_comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تعليقات المدير")
    )
    
    hr_comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تعليقات الموارد البشرية")
    )
    
    # System Information
    is_emergency_leave = models.BooleanField(
        default=False,
        verbose_name=_("إجازة طارئة")
    )
    
    is_backdated = models.BooleanField(
        default=False,
        verbose_name=_("طلب بأثر رجعي")
    )
    
    auto_approved = models.BooleanField(
        default=False,
        verbose_name=_("موافقة تلقائية")
    )
    
    # Metadata
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_leave_requests',
        verbose_name=_("قدم بواسطة")
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التقديم")
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
        verbose_name = _("طلب إجازة")
        verbose_name_plural = _("طلبات الإجازات")
        db_table = 'hrms_leave_request'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'start_date']),
            models.Index(fields=['status']),
            models.Index(fields=['leave_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        """Validate leave request data"""
        super().clean()
        
        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية"))
        
        # Validate half day settings
        if self.is_half_day:
            if self.start_date != self.end_date:
                raise ValidationError(_("نصف اليوم يجب أن يكون في نفس اليوم"))
            if not self.half_day_period:
                raise ValidationError(_("يجب تحديد فترة نصف اليوم"))
        
        # Validate actual dates
        if self.actual_start_date and self.actual_end_date:
            if self.actual_start_date > self.actual_end_date:
                raise ValidationError(_("تاريخ البداية الفعلي لا يمكن أن يكون بعد تاريخ النهاية الفعلي"))
    
    @property
    def duration_days(self):
        """Calculate duration in days"""
        if self.start_date and self.end_date:
            if self.is_half_day:
                return 0.5
            return (self.end_date - self.start_date).days + 1
        return 0
    
    @property
    def is_current(self):
        """Check if leave is currently active"""
        today = date.today()
        return (self.status in ['approved', 'in_progress'] and
                self.start_date <= today <= self.end_date)
    
    @property
    def is_future(self):
        """Check if leave is in the future"""
        return self.start_date > date.today()
    
    @property
    def is_past(self):
        """Check if leave is in the past"""
        return self.end_date < date.today()
    
    @property
    def can_be_cancelled(self):
        """Check if leave request can be cancelled"""
        return (self.status in ['submitted', 'pending_approval', 'approved'] and
                self.start_date > date.today())
    
    @property
    def can_be_modified(self):
        """Check if leave request can be modified"""
        return (self.status in ['draft', 'submitted'] and
                self.start_date > date.today())
    
    def calculate_working_days(self):
        """Calculate working days excluding weekends and holidays"""
        if not self.start_date or not self.end_date:
            return 0
        
        # Simple calculation - can be enhanced with company calendar
        total_days = (self.end_date - self.start_date).days + 1
        
        if self.is_half_day:
            return 0.5
        
        # Exclude weekends (assuming Saturday and Sunday)
        working_days = 0
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def submit_request(self, submitted_by_user):
        """Submit the leave request for approval"""
        if self.status != 'draft':
            raise ValidationError(_("يمكن تقديم المسودات فقط"))
        
        self.status = 'submitted'
        self.submitted_by = submitted_by_user
        self.submitted_at = timezone.now()
        self.current_approval_level = 1
        
        # Check if auto-approval is applicable
        if (self.leave_type.auto_approve_threshold and 
            self.days_requested <= self.leave_type.auto_approve_threshold):
            self.status = 'approved'
            self.auto_approved = True
        else:
            self.status = 'pending_approval'
        
        self.save()
    
    def approve_request(self, approved_by_user, comments=None):
        """Approve the leave request"""
        if self.status != 'pending_approval':
            raise ValidationError(_("يمكن الموافقة على الطلبات المعلقة فقط"))
        
        self.status = 'approved'
        if comments:
            self.manager_comments = comments
        
        # Create approval record
        LeaveApproval.objects.create(
            leave_request=self,
            approved_by=approved_by_user,
            approval_level=self.current_approval_level,
            status='approved',
            comments=comments
        )
        
        self.save()
    
    def reject_request(self, rejected_by_user, reason):
        """Reject the leave request"""
        if self.status not in ['submitted', 'pending_approval']:
            raise ValidationError(_("يمكن رفض الطلبات المقدمة أو المعلقة فقط"))
        
        self.status = 'rejected'
        self.manager_comments = reason
        
        # Create approval record
        LeaveApproval.objects.create(
            leave_request=self,
            approved_by=rejected_by_user,
            approval_level=self.current_approval_level,
            status='rejected',
            comments=reason
        )
        
        self.save()
    
    def cancel_request(self, cancelled_by_user, reason=None):
        """Cancel the leave request"""
        if not self.can_be_cancelled:
            raise ValidationError(_("لا يمكن إلغاء هذا الطلب"))
        
        self.status = 'cancelled'
        if reason:
            self.employee_comments = reason
        
        self.save()
    
    def mark_as_taken(self, actual_start_date=None, actual_end_date=None):
        """Mark leave as taken/in progress"""
        if self.status != 'approved':
            raise ValidationError(_("يمكن تنفيذ الإجازات الموافق عليها فقط"))
        
        self.status = 'in_progress'
        self.actual_start_date = actual_start_date or self.start_date
        self.actual_end_date = actual_end_date or self.end_date
        self.actual_days_taken = self.calculate_working_days()
        
        self.save()
    
    def complete_leave(self, return_date=None, confirmed_by_user=None):
        """Complete the leave and mark employee as returned"""
        if self.status not in ['approved', 'in_progress']:
            raise ValidationError(_("يمكن إكمال الإجازات الجارية فقط"))
        
        self.status = 'completed'
        self.actual_return_date = return_date or date.today()
        self.return_confirmed = True
        self.return_confirmed_by = confirmed_by_user
        self.return_confirmed_at = timezone.now()
        
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to calculate fields"""
        # Calculate days requested if not set
        if not self.days_requested:
            self.days_requested = self.calculate_working_days()
        
        # Set expected return date
        if not self.expected_return_date and self.end_date:
            self.expected_return_date = self.end_date + timedelta(days=1)
        
        # Check if request is backdated
        if self.start_date and self.start_date < date.today():
            self.is_backdated = True
        
        super().save(*args, **kwargs)


class LeaveApproval(models.Model):
    """
    Leave Approval model for tracking approval workflow
    """
    
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name=_("طلب الإجازة")
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_approvals',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    approval_level = models.PositiveIntegerField(
        verbose_name=_("مستوى الموافقة")
    )
    
    STATUS_CHOICES = [
        ('pending', _('معلق')),
        ('approved', _('موافق')),
        ('rejected', _('مرفوض')),
    ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name=_("حالة الموافقة")
    )
    
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تعليقات")
    )
    
    approved_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    class Meta:
        verbose_name = _("موافقة إجازة")
        verbose_name_plural = _("موافقات الإجازات")
        db_table = 'hrms_leave_approval'
        ordering = ['approval_level']
    
    def __str__(self):
        return f"{self.leave_request} - Level {self.approval_level} - {self.status}"
