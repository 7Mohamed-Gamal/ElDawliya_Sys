"""
Attendance Summary Models for HRMS
Handles daily attendance summaries and calculations
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal


class AttendanceSummary(models.Model):
    """
    Attendance Summary model for daily attendance calculations
    Aggregates attendance records into daily summaries with work hours calculation
    """
    
    # Employee and Date
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
        verbose_name=_("الموظف")
    )
    
    date = models.DateField(
        verbose_name=_("التاريخ")
    )
    
    # Work Shift Information
    work_shift = models.ForeignKey(
        'WorkShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_summaries',
        verbose_name=_("وردية العمل")
    )
    
    # Attendance Status
    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('early_leave', _('انصراف مبكر')),
        ('half_day', _('نصف يوم')),
        ('on_leave', _('في إجازة')),
        ('holiday', _('عطلة رسمية')),
        ('weekend', _('عطلة أسبوعية')),
        ('sick', _('مريض')),
        ('training', _('تدريب')),
        ('business_trip', _('مهمة عمل')),
        ('no_show', _('لم يحضر')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name=_("حالة الحضور")
    )
    
    # Time Records
    first_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("أول وقت دخول")
    )
    
    last_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر وقت خروج")
    )
    
    scheduled_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت الدخول المجدول")
    )
    
    scheduled_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت الخروج المجدول")
    )
    
    # Work Hours Calculation
    total_work_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي ساعات العمل")
    )
    
    regular_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("الساعات العادية")
    )
    
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات العمل الإضافي")
    )
    
    break_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات الراحة")
    )
    
    # Timing Analysis
    late_arrival_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق التأخير")
    )
    
    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق الانصراف المبكر")
    )
    
    # Attendance Counts
    total_punches = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي التسجيلات")
    )
    
    in_punches = models.PositiveIntegerField(
        default=0,
        verbose_name=_("تسجيلات الدخول")
    )
    
    out_punches = models.PositiveIntegerField(
        default=0,
        verbose_name=_("تسجيلات الخروج")
    )
    
    # Leave Information
    leave_request = models.ForeignKey(
        'leave.LeaveRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_summaries',
        verbose_name=_("طلب الإجازة")
    )
    
    leave_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات الإجازة")
    )
    
    # Flags
    is_holiday = models.BooleanField(
        default=False,
        verbose_name=_("عطلة رسمية")
    )
    
    is_weekend = models.BooleanField(
        default=False,
        verbose_name=_("عطلة أسبوعية")
    )
    
    is_working_day = models.BooleanField(
        default=True,
        verbose_name=_("يوم عمل")
    )
    
    has_incomplete_punches = models.BooleanField(
        default=False,
        verbose_name=_("تسجيلات ناقصة")
    )
    
    requires_approval = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب موافقة")
    )
    
    # Calculation Details
    calculation_details = models.JSONField(
        default=dict,
        verbose_name=_("تفاصيل الحساب"),
        help_text=_("تفاصيل حساب ساعات العمل")
    )
    
    # Exceptions and Notes
    exceptions = models.JSONField(
        default=list,
        verbose_name=_("الاستثناءات"),
        help_text=_("قائمة بالاستثناءات والمشاكل")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Approval Information
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance_summaries',
        verbose_name=_("تمت الموافقة بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الموافقة")
    )
    
    # Processing Information
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_("تم المعالجة")
    )
    
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المعالجة")
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("ملخص حضور")
        verbose_name_plural = _("ملخصات الحضور")
        db_table = 'hrms_attendance_summary'
        unique_together = [['employee', 'date']]
        ordering = ['-date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        """Validate attendance summary data"""
        super().clean()
        
        # Validate time consistency
        if (self.first_in_time and self.last_out_time and 
            self.first_in_time > self.last_out_time):
            # This might be valid for night shifts
            pass
    
    @property
    def is_present(self):
        """Check if employee was present"""
        return self.status in ['present', 'late', 'early_leave', 'half_day']
    
    @property
    def is_absent(self):
        """Check if employee was absent"""
        return self.status in ['absent', 'no_show']
    
    @property
    def work_duration(self):
        """Calculate total work duration"""
        if self.first_in_time and self.last_out_time:
            # Handle night shifts
            if self.first_in_time <= self.last_out_time:
                # Same day
                in_datetime = datetime.combine(self.date, self.first_in_time)
                out_datetime = datetime.combine(self.date, self.last_out_time)
            else:
                # Night shift - spans to next day
                in_datetime = datetime.combine(self.date, self.first_in_time)
                out_datetime = datetime.combine(self.date + timedelta(days=1), self.last_out_time)
            
            return out_datetime - in_datetime
        return timedelta(0)
    
    @property
    def effective_work_hours(self):
        """Calculate effective work hours (excluding breaks)"""
        total_hours = float(self.total_work_hours)
        break_hours = float(self.break_hours)
        return total_hours - break_hours
    
    def calculate_work_hours(self):
        """Calculate work hours from attendance records"""
        from .attendance_record_models import AttendanceRecord
        
        # Get all records for this employee and date
        records = AttendanceRecord.objects.filter(
            employee=self.employee,
            record_date=self.date,
            status='valid'
        ).order_by('record_time')
        
        if not records.exists():
            self.total_work_hours = 0
            self.regular_hours = 0
            self.overtime_hours = 0
            return
        
        # Find first in and last out
        in_records = records.filter(record_type='in')
        out_records = records.filter(record_type='out')
        
        if in_records.exists():
            self.first_in_time = in_records.first().record_time
        
        if out_records.exists():
            self.last_out_time = out_records.last().record_time
        
        # Calculate total work duration
        work_duration = self.work_duration
        if work_duration:
            total_hours = work_duration.total_seconds() / 3600
            
            # Subtract break time if configured
            if self.work_shift and self.work_shift.break_duration_minutes:
                break_hours = self.work_shift.break_duration_minutes / 60
                total_hours -= break_hours
                self.break_hours = Decimal(str(break_hours))
            
            self.total_work_hours = Decimal(str(round(total_hours, 2)))
            
            # Calculate regular vs overtime hours
            if self.work_shift:
                regular_limit = float(self.work_shift.working_hours)
                if total_hours <= regular_limit:
                    self.regular_hours = self.total_work_hours
                    self.overtime_hours = 0
                else:
                    self.regular_hours = Decimal(str(regular_limit))
                    self.overtime_hours = Decimal(str(round(total_hours - regular_limit, 2)))
            else:
                self.regular_hours = self.total_work_hours
                self.overtime_hours = 0
        
        # Update punch counts
        self.total_punches = records.count()
        self.in_punches = in_records.count()
        self.out_punches = out_records.count()
        
        # Check for incomplete punches
        self.has_incomplete_punches = (self.in_punches != self.out_punches)
    
    def calculate_timing_analysis(self):
        """Calculate late arrival and early departure"""
        if not self.work_shift:
            return
        
        # Calculate late arrival
        if self.first_in_time and self.work_shift.start_time:
            scheduled_minutes = (self.work_shift.start_time.hour * 60 + 
                               self.work_shift.start_time.minute)
            actual_minutes = (self.first_in_time.hour * 60 + 
                            self.first_in_time.minute)
            
            if actual_minutes > scheduled_minutes + self.work_shift.late_grace_minutes:
                self.late_arrival_minutes = actual_minutes - scheduled_minutes
            else:
                self.late_arrival_minutes = 0
        
        # Calculate early departure
        if self.last_out_time and self.work_shift.end_time:
            scheduled_minutes = (self.work_shift.end_time.hour * 60 + 
                               self.work_shift.end_time.minute)
            actual_minutes = (self.last_out_time.hour * 60 + 
                            self.last_out_time.minute)
            
            if actual_minutes < scheduled_minutes - self.work_shift.early_leave_grace_minutes:
                self.early_departure_minutes = scheduled_minutes - actual_minutes
            else:
                self.early_departure_minutes = 0
    
    def determine_status(self):
        """Determine attendance status based on records and timing"""
        # Check if it's a weekend or holiday
        if self.is_weekend:
            self.status = 'weekend'
            return
        
        if self.is_holiday:
            self.status = 'holiday'
            return
        
        # Check if on leave
        if self.leave_request:
            self.status = 'on_leave'
            return
        
        # Check if present
        if self.first_in_time:
            if self.late_arrival_minutes > 0 and self.early_departure_minutes > 0:
                self.status = 'late'  # Both late and early
            elif self.late_arrival_minutes > 0:
                self.status = 'late'
            elif self.early_departure_minutes > 0:
                self.status = 'early_leave'
            elif float(self.total_work_hours) < 4:  # Less than half day
                self.status = 'half_day'
            else:
                self.status = 'present'
        else:
            self.status = 'absent'
    
    def add_exception(self, exception_type, description):
        """Add an exception to the summary"""
        exception = {
            'type': exception_type,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        self.exceptions.append(exception)
    
    def process_summary(self):
        """Process the attendance summary"""
        self.calculate_work_hours()
        self.calculate_timing_analysis()
        self.determine_status()
        
        # Set calculation details
        self.calculation_details = {
            'work_duration_minutes': self.work_duration.total_seconds() / 60 if self.work_duration else 0,
            'break_deducted': float(self.break_hours),
            'grace_period_applied': True,
            'overtime_threshold': float(self.work_shift.working_hours) if self.work_shift else 8,
            'processed_at': datetime.now().isoformat()
        }
        
        self.is_processed = True
        self.processed_at = datetime.now()
        self.save()
    
    def approve_summary(self, approved_by_user):
        """Approve the attendance summary"""
        self.approved_by = approved_by_user
        self.approved_at = datetime.now()
        self.requires_approval = False
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to set calculated fields"""
        # Set weekend flag
        self.is_weekend = self.date.weekday() in [4, 5]  # Friday and Saturday
        
        # Set working day flag
        self.is_working_day = not (self.is_weekend or self.is_holiday)
        
        # Set scheduled times from work shift
        if self.work_shift:
            self.scheduled_in_time = self.work_shift.start_time
            self.scheduled_out_time = self.work_shift.end_time
        
        super().save(*args, **kwargs)
