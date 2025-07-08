"""
Work Shift Models for HRMS
Handles work shift definitions and scheduling
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time, timedelta


class WorkShift(models.Model):
    """
    Work Shift model for defining work schedules and shift patterns
    """
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الوردية")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("كود الوردية")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("وصف الوردية")
    )
    
    # Shift Type
    SHIFT_TYPES = [
        ('morning', _('صباحي')),
        ('afternoon', _('مسائي')),
        ('evening', _('ليلي')),
        ('night', _('ليلي متأخر')),
        ('rotating', _('متناوب')),
        ('flexible', _('مرن')),
        ('split', _('منقسم')),
    ]
    
    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPES,
        verbose_name=_("نوع الوردية")
    )
    
    # Time Settings
    start_time = models.TimeField(
        verbose_name=_("وقت البداية")
    )
    
    end_time = models.TimeField(
        verbose_name=_("وقت النهاية")
    )
    
    # Break Times
    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("بداية فترة الراحة")
    )
    
    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("نهاية فترة الراحة")
    )
    
    break_duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name=_("مدة الراحة (دقائق)")
    )
    
    # Working Hours
    total_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("إجمالي ساعات العمل")
    )
    
    working_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("ساعات العمل الفعلية"),
        help_text=_("ساعات العمل بعد خصم فترات الراحة")
    )
    
    # Grace Periods
    late_grace_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_("فترة سماح التأخير (دقائق)")
    )
    
    early_leave_grace_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_("فترة سماح الانصراف المبكر (دقائق)")
    )
    
    # Overtime Settings
    overtime_threshold_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name=_("حد العمل الإضافي (دقائق)"),
        help_text=_("الحد الأدنى للدقائق الإضافية لاحتسابها كعمل إضافي")
    )
    
    max_overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=4.0,
        verbose_name=_("الحد الأقصى للعمل الإضافي (ساعات)")
    )
    
    # Weekly Schedule
    monday = models.BooleanField(default=True, verbose_name=_("الاثنين"))
    tuesday = models.BooleanField(default=True, verbose_name=_("الثلاثاء"))
    wednesday = models.BooleanField(default=True, verbose_name=_("الأربعاء"))
    thursday = models.BooleanField(default=True, verbose_name=_("الخميس"))
    friday = models.BooleanField(default=True, verbose_name=_("الجمعة"))
    saturday = models.BooleanField(default=False, verbose_name=_("السبت"))
    sunday = models.BooleanField(default=False, verbose_name=_("الأحد"))
    
    # Shift Settings
    is_night_shift = models.BooleanField(
        default=False,
        verbose_name=_("وردية ليلية"),
        help_text=_("هل هذه وردية ليلية تمتد لليوم التالي؟")
    )
    
    requires_check_in = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب تسجيل حضور")
    )
    
    requires_check_out = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب تسجيل انصراف")
    )
    
    auto_check_out = models.BooleanField(
        default=False,
        verbose_name=_("تسجيل انصراف تلقائي"),
        help_text=_("تسجيل انصراف تلقائي في نهاية الوردية")
    )
    
    # Attendance Rules
    minimum_hours_for_full_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=6.0,
        verbose_name=_("الحد الأدنى للساعات ليوم كامل")
    )
    
    minimum_hours_for_half_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=4.0,
        verbose_name=_("الحد الأدنى للساعات لنصف يوم")
    )
    
    # Color Coding for UI
    color_code = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name=_("رمز اللون"),
        help_text=_("لون الوردية في التقويم والجداول")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("افتراضي"),
        help_text=_("هل هذه الوردية الافتراضية للموظفين الجدد؟")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_work_shifts',
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
        verbose_name = _("وردية عمل")
        verbose_name_plural = _("ورديات العمل")
        db_table = 'hrms_work_shift'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['shift_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    def clean(self):
        """Validate work shift data"""
        super().clean()
        
        # Validate break times
        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                raise ValidationError(_("وقت بداية الراحة يجب أن يكون قبل وقت النهاية"))
            
            # Check if break times are within shift hours
            if not self.is_night_shift:
                if (self.break_start_time < self.start_time or 
                    self.break_end_time > self.end_time):
                    raise ValidationError(_("أوقات الراحة يجب أن تكون ضمن أوقات الوردية"))
        
        # Validate working hours
        if self.working_hours > self.total_hours:
            raise ValidationError(_("ساعات العمل الفعلية لا يمكن أن تكون أكثر من إجمالي الساعات"))
    
    @property
    def working_days(self):
        """Get list of working days"""
        days = []
        if self.monday: days.append(0)  # Monday
        if self.tuesday: days.append(1)  # Tuesday
        if self.wednesday: days.append(2)  # Wednesday
        if self.thursday: days.append(3)  # Thursday
        if self.friday: days.append(4)  # Friday
        if self.saturday: days.append(5)  # Saturday
        if self.sunday: days.append(6)  # Sunday
        return days
    
    @property
    def working_days_count(self):
        """Get number of working days per week"""
        return len(self.working_days)
    
    @property
    def weekly_hours(self):
        """Calculate total weekly working hours"""
        return self.working_hours * self.working_days_count
    
    def calculate_total_hours(self):
        """Calculate total hours between start and end time"""
        if self.is_night_shift:
            # For night shifts that cross midnight
            end_datetime = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
            start_datetime = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)
            total_minutes = (end_datetime - start_datetime).total_seconds() / 60
        else:
            # For regular shifts
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            total_minutes = end_minutes - start_minutes
        
        return round(total_minutes / 60, 2)
    
    def calculate_working_hours(self):
        """Calculate working hours after deducting break time"""
        total_hours = self.calculate_total_hours()
        break_hours = self.break_duration_minutes / 60
        return round(total_hours - break_hours, 2)
    
    def is_working_day(self, weekday):
        """Check if given weekday is a working day (0=Monday, 6=Sunday)"""
        working_days_map = {
            0: self.monday,
            1: self.tuesday,
            2: self.wednesday,
            3: self.thursday,
            4: self.friday,
            5: self.saturday,
            6: self.sunday,
        }
        return working_days_map.get(weekday, False)
    
    def get_expected_check_in_time(self):
        """Get expected check-in time with grace period"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        grace_minutes = start_minutes + self.late_grace_minutes
        hours = grace_minutes // 60
        minutes = grace_minutes % 60
        return time(hours, minutes)
    
    def get_expected_check_out_time(self):
        """Get expected check-out time with grace period"""
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        grace_minutes = end_minutes - self.early_leave_grace_minutes
        hours = grace_minutes // 60
        minutes = grace_minutes % 60
        return time(hours, minutes)
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate hours"""
        # Auto-calculate total hours if not set
        if not self.total_hours:
            self.total_hours = self.calculate_total_hours()
        
        # Auto-calculate working hours if not set
        if not self.working_hours:
            self.working_hours = self.calculate_working_hours()
        
        # Ensure only one default shift
        if self.is_default:
            WorkShift.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        # Auto-generate code if not provided
        if not self.code:
            shift_count = WorkShift.objects.count()
            self.code = f"SHIFT{shift_count + 1:03d}"
        
        super().save(*args, **kwargs)
