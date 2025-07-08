"""
Attendance Record Models for HRMS
Handles individual attendance records and punch data
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta


class AttendanceRecord(models.Model):
    """
    Attendance Record model for storing individual punch records
    Captures all attendance events from various sources
    """
    
    # Employee Information
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("الموظف")
    )
    
    # Date and Time Information
    record_date = models.DateField(
        verbose_name=_("تاريخ التسجيل")
    )
    
    record_time = models.TimeField(
        verbose_name=_("وقت التسجيل")
    )
    
    record_datetime = models.DateTimeField(
        verbose_name=_("تاريخ ووقت التسجيل")
    )
    
    # Record Type
    RECORD_TYPES = [
        ('in', _('دخول')),
        ('out', _('خروج')),
        ('break_out', _('خروج للراحة')),
        ('break_in', _('عودة من الراحة')),
        ('overtime_in', _('دخول عمل إضافي')),
        ('overtime_out', _('خروج عمل إضافي')),
    ]
    
    record_type = models.CharField(
        max_length=15,
        choices=RECORD_TYPES,
        verbose_name=_("نوع التسجيل")
    )
    
    # Source Information
    SOURCE_CHOICES = [
        ('machine', _('جهاز حضور')),
        ('manual', _('يدوي')),
        ('mobile', _('تطبيق جوال')),
        ('web', _('موقع ويب')),
        ('import', _('استيراد')),
        ('system', _('نظام')),
    ]
    
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='machine',
        verbose_name=_("مصدر التسجيل")
    )
    
    # Device Information
    machine = models.ForeignKey(
        'AttendanceMachine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
        verbose_name=_("جهاز الحضور")
    )
    
    device_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("معرف المستخدم في الجهاز")
    )
    
    # Verification Method
    VERIFICATION_METHODS = [
        ('fingerprint', _('بصمة الإصبع')),
        ('face', _('التعرف على الوجه')),
        ('card', _('بطاقة')),
        ('password', _('كلمة مرور')),
        ('manual', _('يدوي')),
        ('unknown', _('غير معروف')),
    ]
    
    verification_method = models.CharField(
        max_length=15,
        choices=VERIFICATION_METHODS,
        default='fingerprint',
        verbose_name=_("طريقة التحقق")
    )
    
    # Location Information
    location_description = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("وصف الموقع")
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("عنوان IP")
    )
    
    # Work Shift Information
    work_shift = models.ForeignKey(
        'WorkShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
        verbose_name=_("وردية العمل")
    )
    
    # Status and Validation
    STATUS_CHOICES = [
        ('valid', _('صحيح')),
        ('invalid', _('غير صحيح')),
        ('duplicate', _('مكرر')),
        ('late', _('متأخر')),
        ('early', _('مبكر')),
        ('pending', _('معلق')),
        ('processed', _('تم معالجته')),
    ]
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='valid',
        verbose_name=_("حالة التسجيل")
    )
    
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_("تم المعالجة")
    )
    
    is_manual_entry = models.BooleanField(
        default=False,
        verbose_name=_("إدخال يدوي")
    )
    
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_("تم التعديل")
    )
    
    # Timing Analysis
    is_late = models.BooleanField(
        default=False,
        verbose_name=_("متأخر")
    )
    
    is_early = models.BooleanField(
        default=False,
        verbose_name=_("مبكر")
    )
    
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق التأخير")
    )
    
    early_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق التبكير")
    )
    
    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    raw_data = models.JSONField(
        default=dict,
        verbose_name=_("البيانات الخام"),
        help_text=_("البيانات الأصلية من الجهاز")
    )
    
    # Approval Information
    requires_approval = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب موافقة")
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance_records',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_attendance_records',
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
        verbose_name = _("سجل حضور")
        verbose_name_plural = _("سجلات الحضور")
        db_table = 'hrms_attendance_record'
        ordering = ['-record_datetime']
        indexes = [
            models.Index(fields=['employee', 'record_date']),
            models.Index(fields=['record_date', 'record_time']),
            models.Index(fields=['status']),
            models.Index(fields=['record_type']),
            models.Index(fields=['machine']),
        ]
        unique_together = [
            ['employee', 'record_datetime', 'record_type', 'machine']
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.record_date} {self.record_time} - {self.get_record_type_display()}"
    
    def clean(self):
        """Validate attendance record data"""
        super().clean()
        
        # Validate record datetime consistency
        if self.record_date and self.record_time:
            expected_datetime = datetime.combine(self.record_date, self.record_time)
            if self.record_datetime and self.record_datetime.date() != self.record_date:
                raise ValidationError(_("تاريخ التسجيل غير متطابق"))
    
    @property
    def is_check_in(self):
        """Check if this is a check-in record"""
        return self.record_type in ['in', 'break_in', 'overtime_in']
    
    @property
    def is_check_out(self):
        """Check if this is a check-out record"""
        return self.record_type in ['out', 'break_out', 'overtime_out']
    
    @property
    def formatted_time(self):
        """Get formatted time string"""
        return self.record_time.strftime('%H:%M')
    
    @property
    def is_weekend(self):
        """Check if record is on weekend"""
        # Assuming Friday and Saturday are weekends
        return self.record_date.weekday() in [4, 5]
    
    def calculate_timing_status(self):
        """Calculate if record is late or early based on work shift"""
        if not self.work_shift:
            return
        
        if self.record_type == 'in':
            # Check if late for check-in
            expected_time = self.work_shift.start_time
            grace_minutes = self.work_shift.late_grace_minutes
            
            # Convert times to minutes for comparison
            record_minutes = self.record_time.hour * 60 + self.record_time.minute
            expected_minutes = expected_time.hour * 60 + expected_time.minute
            grace_limit = expected_minutes + grace_minutes
            
            if record_minutes > grace_limit:
                self.is_late = True
                self.late_minutes = record_minutes - expected_minutes
            else:
                self.is_late = False
                self.late_minutes = 0
        
        elif self.record_type == 'out':
            # Check if early for check-out
            expected_time = self.work_shift.end_time
            grace_minutes = self.work_shift.early_leave_grace_minutes
            
            # Convert times to minutes for comparison
            record_minutes = self.record_time.hour * 60 + self.record_time.minute
            expected_minutes = expected_time.hour * 60 + expected_time.minute
            grace_limit = expected_minutes - grace_minutes
            
            if record_minutes < grace_limit:
                self.is_early = True
                self.early_minutes = expected_minutes - record_minutes
            else:
                self.is_early = False
                self.early_minutes = 0
    
    def get_paired_record(self):
        """Get the paired record (in/out)"""
        if self.record_type == 'in':
            # Find the next out record
            return AttendanceRecord.objects.filter(
                employee=self.employee,
                record_date=self.record_date,
                record_type='out',
                record_time__gt=self.record_time
            ).first()
        elif self.record_type == 'out':
            # Find the previous in record
            return AttendanceRecord.objects.filter(
                employee=self.employee,
                record_date=self.record_date,
                record_type='in',
                record_time__lt=self.record_time
            ).last()
        return None
    
    def calculate_work_duration(self):
        """Calculate work duration with paired record"""
        paired_record = self.get_paired_record()
        if not paired_record:
            return None
        
        if self.record_type == 'in' and paired_record.record_type == 'out':
            # Calculate duration from in to out
            in_datetime = datetime.combine(self.record_date, self.record_time)
            out_datetime = datetime.combine(paired_record.record_date, paired_record.record_time)
            return out_datetime - in_datetime
        elif self.record_type == 'out' and paired_record.record_type == 'in':
            # Calculate duration from paired in to this out
            in_datetime = datetime.combine(paired_record.record_date, paired_record.record_time)
            out_datetime = datetime.combine(self.record_date, self.record_time)
            return out_datetime - in_datetime
        
        return None
    
    def mark_as_duplicate(self):
        """Mark record as duplicate"""
        self.status = 'duplicate'
        self.save()
    
    def approve_record(self, approved_by_user):
        """Approve the attendance record"""
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.requires_approval = False
        self.status = 'valid'
        self.save()
    
    def edit_record(self, new_time, edited_by_user, reason=None):
        """Edit the attendance record time"""
        old_time = self.record_time
        self.record_time = new_time
        self.record_datetime = datetime.combine(self.record_date, new_time)
        self.is_edited = True
        self.is_manual_entry = True
        
        if reason:
            self.notes = f"{self.notes or ''}\nتم التعديل من {old_time} إلى {new_time}. السبب: {reason}"
        
        # Recalculate timing status
        self.calculate_timing_status()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate fields"""
        # Set record_datetime if not provided
        if not self.record_datetime and self.record_date and self.record_time:
            self.record_datetime = datetime.combine(self.record_date, self.record_time)
        
        # Extract date and time from datetime if provided
        if self.record_datetime:
            self.record_date = self.record_datetime.date()
            self.record_time = self.record_datetime.time()
        
        # Calculate timing status if work shift is available
        if self.work_shift:
            self.calculate_timing_status()
        
        # Set status based on timing
        if self.is_late or self.is_early:
            if self.status == 'valid':
                self.status = 'late' if self.is_late else 'early'
        
        super().save(*args, **kwargs)
