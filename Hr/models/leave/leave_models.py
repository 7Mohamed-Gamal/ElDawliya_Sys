"""
Leave Models for HRMS
Handles employee leave requests and balances
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class LeaveType(models.Model):
    """
    Leave Type model defining different types of leave 
    (annual, sick, unpaid, etc.)
    """
    
    # Leave Categories
    ANNUAL = 'AN'
    SICK = 'SK'
    MATERNITY = 'MT'
    PATERNITY = 'PT'
    UNPAID = 'UP'
    OTHER = 'OT'
    
    CATEGORY_CHOICES = (
        (ANNUAL, _('سنوي')),
        (SICK, _('مرضى')),
        (MATERNITY, _('وضع')),
        (PATERNITY, _('أبوة')), 
        (UNPAID, _('غير مدفوع')),
        (OTHER, _('أخرى'))
    )
    
    # Unit Types
    DAYS = 'D'
    HOURS = 'H'
    
    UNIT_CHOICES = (
        (DAYS, _('أيام')),
        (HOURS, _('ساعات'))
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("نوع الإجازة")
    )
    
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_("الكود")
    )
    
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        verbose_name=_("الفئة")
    )
    
    is_paid = models.BooleanField(
        default=True,
        verbose_name=_("مدفوعة")
    )
    
    entitlement = models.PositiveSmallIntegerField(
        default=21,
        verbose_name=_("العدد المسموح سنوياً")
    )
    
    unit = models.CharField(
        max_length=1,
        choices=UNIT_CHOICES,
        default=DAYS,
        verbose_name=_("وحدة القياس")
    )
    
    is_carry_forward = models.BooleanField(
        default=True,
        verbose_name=_("يمكن تجميعها")
    )
    
    max_carry_forward = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("أقصى حد للتجميع")
    )
    
    requires_approval = models.BooleanField(
        default=True,
        verbose_name=_("تتطلب موافقة")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
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
        verbose_name = _("نوع إجازة")
        verbose_name_plural = _("أنواع الإجازات")
        db_table = 'hrms_leavetype'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class LeaveRequest(models.Model):
    """
    Employee leave requests with workflow status
    """
    
    # Status Choices
    PENDING = 'P'
    APPROVED = 'A'
    REJECTED = 'R'
    CANCELLED = 'C'
    
    STATUS_CHOICES = (
        (PENDING, _('قيد الانتظار')),
        (APPROVED, _('موافق')),
        (REJECTED, _('مرفوض')),
        (CANCELLED, _('ملغي'))
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_("الموظف")
    )
    
    leave_type = models.ForeignKey(
        'LeaveType',
        on_delete=models.CASCADE,
        verbose_name=_("نوع الإجازة")
    )
    
    start_date = models.DateField(
        verbose_name=_("تاريخ البدء")
    )
    
    end_date = models.DateField(
        verbose_name=_("تاريخ الانتهاء")
    )
    
    days_requested = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("عدد الأيام المطلوبة")
    )
    
    reason = models.TextField(
        verbose_name=_("السبب")
    )
    
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name=_("الحالة")
    )
    
    approved_by = models.ForeignKey(
        'employee.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name=_("وافق عليه")
    )
    
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب الرفض")
    )
    
    is_half_day = models.BooleanField(
        default=False,
        verbose_name=_("نصف يوم")
    )
    
    half_day_part = models.CharField(
        max_length=1,
        choices=[('M', _('الصباح')), ('A', _('المساء'))],
        null=True,
        blank=True,
        verbose_name=_("جزء اليوم")
    )
    
    documents = models.FileField(
        upload_to='leave_documents/',
        null=True,
        blank=True,
        verbose_name=_("المستندات")
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
        db_table = 'hrms_leaverequest'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        """Set approved_date when status changes to approved"""
        if self.status == self.APPROVED and not self.approved_date:
            self.approved_date = timezone.now()
        super().save(*args, **kwargs)


class LeaveBalance(models.Model):
    """
    Tracks remaining leave balances for employees
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name=_("الموظف")
    )
    
    leave_type = models.ForeignKey(
        'LeaveType',
        on_delete=models.CASCADE,
        verbose_name=_("نوع الإجازة")
    )
    
    year = models.PositiveSmallIntegerField(
        verbose_name=_("السنة")
    )
    
    entitlement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("الرصيد الممنوح")
    )
    
    carried_forward = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("المحمول من السنة السابقة")
    )
    
    taken = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("المستهلك")
    )
    
    remaining = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("المتبقي")
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
        verbose_name = _("رصيد إجازة")
        verbose_name_plural = _("أرصدة الإجازات")
        db_table = 'hrms_leavebalance'
        unique_together = ['employee', 'leave_type', 'year']
        indexes = [
            models.Index(fields=['employee', 'year']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.year})"
    
    def save(self, *args, **kwargs):
        """Calculate remaining balance before saving"""
        self.remaining = (self.entitlement + self.carried_forward) - self.taken
        super().save(*args, **kwargs)
