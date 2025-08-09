# -*- coding: utf-8 -*-
"""
نماذج الورديات المتقدمة لنظام إدارة الموارد البشرية (HRMS)
Enhanced Work Shift Models with Advanced Features
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.conf import settings
from decimal import Decimal
import json

User = get_user_model()


# Legacy model for backward compatibility
class WorkShift(models.Model):
    """نموذج الوردية الأساسي للتوافق مع النظام القديم"""
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الوردية")
    )
    
    start_time = models.TimeField(verbose_name=_("وقت البداية"))
    end_time = models.TimeField(verbose_name=_("وقت النهاية"))
    
    is_overnight = models.BooleanField(
        default=False,
        verbose_name=_("وردية ليلية")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    class Meta:
        verbose_name = _("وردية")
        verbose_name_plural = _("الورديات")
        db_table = 'hrms_work_shift'
    
    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    @property
    def total_hours(self):
        """إجمالي ساعات العمل"""
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        
        # للورديات الليلية
        if self.is_overnight and self.end_time < self.start_time:
            end_dt += timedelta(days=1)
        
        total_time = end_dt - start_dt
        return Decimal(str(total_time.total_seconds() / 3600))
    
    def calculate_late_minutes(self, actual_check_in_time):
        """حساب دقائق التأخير"""
        if not actual_check_in_time:
            return 0
        
        expected_time = datetime.combine(date.today(), self.start_time)
        actual_time = datetime.combine(date.today(), actual_check_in_time)
        
        if actual_time > expected_time:
            late_time = actual_time - expected_time
            return int(late_time.total_seconds() / 60)
        
        return 0


class ShiftAssignment(models.Model):
    """تعيين الوردية للموظف - للتوافق مع النظام القديم"""
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        verbose_name=_("الموظف")
    )
    
    shift = models.ForeignKey(
        WorkShift,
        on_delete=models.CASCADE,
        verbose_name=_("الوردية")
    )
    
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ النهاية")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    class Meta:
        verbose_name = _("تعيين وردية")
        verbose_name_plural = _("تعيينات الورديات")
        db_table = 'hrms_shift_assignment'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.shift.name}"


class WorkShiftEnhanced(models.Model):
    """نموذج الوردية المحسن مع ميزات متقدمة"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الوردية")
    )
    
    name_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم بالإنجليزية")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("رمز الوردية")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )
    
    # Time Configuration
    start_time = models.TimeField(verbose_name=_("وقت البداية"))
    end_time = models.TimeField(verbose_name=_("وقت النهاية"))
    
    # Break Configuration
    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("بداية الاستراحة")
    )
    
    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("نهاية الاستراحة")
    )
    
    break_duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name=_("مدة الاستراحة (دقيقة)")
    )
    
    # Flexibility Settings
    grace_period_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_("فترة السماح (دقيقة)"),
        help_text=_("الوقت المسموح للتأخير بدون احتساب")
    )
    
    early_departure_grace_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_("فترة السماح للانصراف المبكر (دقيقة)")
    )
    
    overtime_threshold_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name=_("حد الوقت الإضافي (دقيقة)"),
        help_text=_("الحد الأدنى لاحتساب الوقت الإضافي")
    )
    
    # Shift Type and Properties
    SHIFT_TYPES = [
        ('regular', _('عادية')),
        ('night', _('ليلية')),
        ('split', _('منقسمة')),
        ('flexible', _('مرنة')),
        ('rotating', _('متناوبة')),
        ('on_call', _('استدعاء')),
        ('remote', _('عن بُعد')),
    ]
    
    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPES,
        default='regular',
        verbose_name=_("نوع الوردية")
    )
    
    is_overnight = models.BooleanField(
        default=False,
        verbose_name=_("وردية ليلية"),
        help_text=_("هل تمتد الوردية لليوم التالي؟")
    )
    
    is_flexible = models.BooleanField(
        default=False,
        verbose_name=_("وردية مرنة"),
        help_text=_("هل يمكن للموظف اختيار أوقات العمل؟")
    )
    
    flexible_hours_range = models.PositiveIntegerField(
        default=0,
        verbose_name=_("نطاق الساعات المرنة"),
        help_text=_("عدد الساعات المرنة المسموحة")
    )
    
    # Working Days Configuration
    working_days = models.JSONField(
        default=list,
        verbose_name=_("أيام العمل"),
        help_text=_("أيام الأسبوع [0=الاثنين, 6=الأحد]")
    )
    
    # Department and Location
    department = models.ForeignKey(
        'Hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_shifts',
        verbose_name=_("القسم")
    )
    
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("الموقع")
    )
    
    allowed_locations = models.JSONField(
        default=list,
        verbose_name=_("المواقع المسموحة"),
        help_text=_("قائمة بالمواقع المسموح بها للحضور")
    )
    
    # Overtime Configuration
    overtime_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('1.5'),
        verbose_name=_("معامل الوقت الإضافي")
    )
    
    weekend_overtime_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('2.0'),
        verbose_name=_("معامل الوقت الإضافي في العطل")
    )
    
    max_overtime_hours_daily = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('4.0'),
        verbose_name=_("الحد الأقصى للوقت الإضافي اليومي")
    )
    
    max_overtime_hours_weekly = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('20.0'),
        verbose_name=_("الحد الأقصى للوقت الإضافي الأسبوعي")
    )
    
    # Attendance Rules
    require_check_in = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب تسجيل دخول")
    )
    
    require_check_out = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب تسجيل خروج")
    )
    
    auto_check_out = models.BooleanField(
        default=False,
        verbose_name=_("تسجيل خروج تلقائي")
    )
    
    auto_check_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت التسجيل التلقائي للخروج")
    )
    
    # Notification Settings
    late_notification_threshold = models.PositiveIntegerField(
        default=30,
        verbose_name=_("حد إشعار التأخير (دقيقة)")
    )
    
    absence_notification_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت إشعار الغياب")
    )
    
    # Status and Activation
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    effective_from = models.DateField(
        default=timezone.now,
        verbose_name=_("ساري من")
    )
    
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("ساري حتى")
    )
    
    # Color and Display
    color_code = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_("رمز اللون"),
        help_text=_("لون الوردية في التقويم")
    )
    
    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("الأيقونة")
    )
    
    # Priority and Sorting
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الأولوية")
    )
    
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ترتيب العرض")
    )
    
    # System Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        verbose_name=_("بيانات إضافية")
    )
    
    class Meta:
        verbose_name = _("وردية محسنة")
        verbose_name_plural = _("الورديات المحسنة")
        db_table = 'hrms_work_shift_enhanced'
        ordering = ['sort_order', 'start_time']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['shift_type']),
            models.Index(fields=['department']),
            models.Index(fields=['effective_from', 'effective_to']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()
        
        # التحقق من أوقات الاستراحة
        if self.break_start_time and self.break_end_time:
            if self.break_end_time <= self.break_start_time:
                raise ValidationError(_("وقت نهاية الاستراحة يجب أن يكون بعد وقت البداية"))
            
            # التحقق من أن الاستراحة ضمن وقت العمل
            if not self.is_overnight:
                if (self.break_start_time < self.start_time or 
                    self.break_end_time > self.end_time):
                    raise ValidationError(_("وقت الاستراحة يجب أن يكون ضمن وقت العمل"))
        
        # التحقق من التواريخ الفعالة
        if self.effective_from and self.effective_to:
            if self.effective_from >= self.effective_to:
                raise ValidationError(_("تاريخ البداية يجب أن يكون قبل تاريخ النهاية"))
    
    def save(self, *args, **kwargs):
        """حفظ الوردية مع حساب القيم التلقائية"""
        # تحديد نوع الوردية تلقائياً
        self._auto_determine_shift_type()
        
        # تحديد أيام العمل الافتراضية
        if not self.working_days:
            self.working_days = [0, 1, 2, 3, 4]  # الاثنين إلى الجمعة
        
        super().save(*args, **kwargs)
    
    def _auto_determine_shift_type(self):
        """تحديد نوع الوردية تلقائياً"""
        if self.is_overnight or (self.start_time > time(18, 0) or self.end_time < time(6, 0)):
            if self.shift_type == 'regular':
                self.shift_type = 'night'
        
        if self.is_flexible:
            self.shift_type = 'flexible'
    
    # Properties
    @property
    def total_hours(self):
        """إجمالي ساعات العمل"""
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        
        # للورديات الليلية
        if self.is_overnight and self.end_time < self.start_time:
            end_dt += timedelta(days=1)
        
        total_time = end_dt - start_dt
        
        # خصم وقت الاستراحة
        if self.break_start_time and self.break_end_time:
            break_start_dt = datetime.combine(date.today(), self.break_start_time)
            break_end_dt = datetime.combine(date.today(), self.break_end_time)
            break_time = break_end_dt - break_start_dt
            total_time -= break_time
        
        return Decimal(str(total_time.total_seconds() / 3600))
    
    @property
    def is_current_active(self):
        """هل الوردية نشطة حالياً؟"""
        if not self.is_active:
            return False
        
        today = timezone.now().date()
        
        if self.effective_from > today:
            return False
        
        if self.effective_to and self.effective_to < today:
            return False
        
        return True
    
    @property
    def break_duration_hours(self):
        """مدة الاستراحة بالساعات"""
        if self.break_start_time and self.break_end_time:
            break_start_dt = datetime.combine(date.today(), self.break_start_time)
            break_end_dt = datetime.combine(date.today(), self.break_end_time)
            break_time = break_end_dt - break_start_dt
            return Decimal(str(break_time.total_seconds() / 3600))
        return Decimal('0')
    
    @property
    def working_days_display(self):
        """عرض أيام العمل"""
        days_names = {
            0: _('الاثنين'),
            1: _('الثلاثاء'),
            2: _('الأربعاء'),
            3: _('الخميس'),
            4: _('الجمعة'),
            5: _('السبت'),
            6: _('الأحد'),
        }
        
        return [days_names.get(day, str(day)) for day in self.working_days]
    
    # Methods
    def calculate_late_minutes(self, actual_check_in_time):
        """حساب دقائق التأخير"""
        if not actual_check_in_time:
            return 0
        
        # تحويل الأوقات إلى datetime للمقارنة
        expected_time = datetime.combine(date.today(), self.start_time)
        actual_time = datetime.combine(date.today(), actual_check_in_time)
        
        # إضافة فترة السماح
        grace_time = expected_time + timedelta(minutes=self.grace_period_minutes)
        
        if actual_time > grace_time:
            late_time = actual_time - expected_time
            return int(late_time.total_seconds() / 60)
        
        return 0
    
    def calculate_early_departure_minutes(self, actual_check_out_time):
        """حساب دقائق الانصراف المبكر"""
        if not actual_check_out_time:
            return 0
        
        expected_time = datetime.combine(date.today(), self.end_time)
        actual_time = datetime.combine(date.today(), actual_check_out_time)
        
        # إضافة فترة السماح
        grace_time = expected_time - timedelta(minutes=self.early_departure_grace_minutes)
        
        if actual_time < grace_time:
            early_time = expected_time - actual_time
            return int(early_time.total_seconds() / 60)
        
        return 0
    
    def calculate_overtime_hours(self, actual_check_out_time):
        """حساب ساعات الوقت الإضافي"""
        if not actual_check_out_time:
            return Decimal('0')
        
        expected_time = datetime.combine(date.today(), self.end_time)
        actual_time = datetime.combine(date.today(), actual_check_out_time)
        
        # للورديات الليلية
        if self.is_overnight and actual_check_out_time < self.end_time:
            actual_time += timedelta(days=1)
        
        # إضافة حد الوقت الإضافي
        threshold_time = expected_time + timedelta(minutes=self.overtime_threshold_minutes)
        
        if actual_time > threshold_time:
            overtime_time = actual_time - expected_time
            overtime_hours = Decimal(str(overtime_time.total_seconds() / 3600))
            
            # تطبيق الحد الأقصى اليومي
            if overtime_hours > self.max_overtime_hours_daily:
                overtime_hours = self.max_overtime_hours_daily
            
            return overtime_hours
        
        return Decimal('0')
    
    def is_working_day(self, date_obj):
        """هل هذا اليوم يوم عمل؟"""
        weekday = date_obj.weekday()  # 0 = الاثنين
        return weekday in self.working_days
    
    def get_shift_times_for_date(self, date_obj):
        """الحصول على أوقات الوردية لتاريخ محدد"""
        if not self.is_working_day(date_obj):
            return None
        
        start_datetime = datetime.combine(date_obj, self.start_time)
        end_datetime = datetime.combine(date_obj, self.end_time)
        
        # للورديات الليلية
        if self.is_overnight and self.end_time < self.start_time:
            end_datetime += timedelta(days=1)
        
        return {
            'start': start_datetime,
            'end': end_datetime,
            'break_start': datetime.combine(date_obj, self.break_start_time) if self.break_start_time else None,
            'break_end': datetime.combine(date_obj, self.break_end_time) if self.break_end_time else None,
        }
    
    def get_employees_count(self):
        """عدد الموظفين المعينين لهذه الوردية"""
        from Hr.models.attendance.attendance_models import EmployeeShiftAssignmentEnhanced
        
        return EmployeeShiftAssignmentEnhanced.objects.filter(
            shift=self,
            is_active=True,
            status='approved'
        ).count()
    
    def get_current_employees(self):
        """الموظفين المعينين حالياً لهذه الوردية"""
        from Hr.models.attendance.attendance_models import EmployeeShiftAssignmentEnhanced
        
        today = timezone.now().date()
        
        return EmployeeShiftAssignmentEnhanced.objects.filter(
            shift=self,
            is_active=True,
            status='approved',
            start_date__lte=today
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
        )
    
    def clone_shift(self, new_name, new_code):
        """نسخ الوردية"""
        new_shift = WorkShiftEnhanced.objects.create(
            name=new_name,
            name_en=f"{self.name_en}_copy" if self.name_en else None,
            code=new_code,
            description=f"نسخة من {self.name}",
            start_time=self.start_time,
            end_time=self.end_time,
            break_start_time=self.break_start_time,
            break_end_time=self.break_end_time,
            break_duration_minutes=self.break_duration_minutes,
            grace_period_minutes=self.grace_period_minutes,
            early_departure_grace_minutes=self.early_departure_grace_minutes,
            overtime_threshold_minutes=self.overtime_threshold_minutes,
            shift_type=self.shift_type,
            is_overnight=self.is_overnight,
            is_flexible=self.is_flexible,
            flexible_hours_range=self.flexible_hours_range,
            working_days=self.working_days.copy(),
            department=self.department,
            location=self.location,
            allowed_locations=self.allowed_locations.copy(),
            overtime_multiplier=self.overtime_multiplier,
            weekend_overtime_multiplier=self.weekend_overtime_multiplier,
            max_overtime_hours_daily=self.max_overtime_hours_daily,
            max_overtime_hours_weekly=self.max_overtime_hours_weekly,
            require_check_in=self.require_check_in,
            require_check_out=self.require_check_out,
            auto_check_out=self.auto_check_out,
            auto_check_out_time=self.auto_check_out_time,
            late_notification_threshold=self.late_notification_threshold,
            absence_notification_time=self.absence_notification_time,
            color_code=self.color_code,
            icon=self.icon,
            priority=self.priority,
            metadata=self.metadata.copy(),
        )
        
        return new_shift
    
    @classmethod
    def get_active_shifts(cls, department=None):
        """الحصول على الورديات النشطة"""
        queryset = cls.objects.filter(is_active=True)
        
        today = timezone.now().date()
        queryset = queryset.filter(
            effective_from__lte=today
        ).filter(
            models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today)
        )
        
        if department:
            queryset = queryset.filter(department=department)
        
        return queryset.order_by('sort_order', 'start_time')
    
    @classmethod
    def get_shifts_by_type(cls, shift_type):
        """الحصول على الورديات حسب النوع"""
        return cls.objects.filter(
            shift_type=shift_type,
            is_active=True
        ).order_by('start_time')
    
    @classmethod
    def get_overlapping_shifts(cls, start_time, end_time, exclude_id=None):
        """الحصول على الورديات المتداخلة"""
        queryset = cls.objects.filter(is_active=True)
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        
        # فحص التداخل
        overlapping = []
        for shift in queryset:
            if cls._check_time_overlap(start_time, end_time, shift.start_time, shift.end_time, shift.is_overnight):
                overlapping.append(shift)
        
        return overlapping
    
    @staticmethod
    def _check_time_overlap(start1, end1, start2, end2, is_overnight2=False):
        """فحص تداخل الأوقات"""
        # تحويل الأوقات إلى دقائق من بداية اليوم
        def time_to_minutes(t):
            return t.hour * 60 + t.minute
        
        start1_min = time_to_minutes(start1)
        end1_min = time_to_minutes(end1)
        start2_min = time_to_minutes(start2)
        end2_min = time_to_minutes(end2)
        
        # للورديات الليلية
        if is_overnight2 and end2 < start2:
            end2_min += 24 * 60  # إضافة 24 ساعة
        
        # فحص التداخل
        return not (end1_min <= start2_min or start1_min >= end2_min)


class ShiftPatternEnhanced(models.Model):
    """نموذج نمط الورديات المتقدم"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم النمط")
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )
    
    # Pattern Configuration
    PATTERN_TYPES = [
        ('weekly', _('أسبوعي')),
        ('monthly', _('شهري')),
        ('custom', _('مخصص')),
        ('rotating', _('متناوب')),
    ]
    
    pattern_type = models.CharField(
        max_length=20,
        choices=PATTERN_TYPES,
        default='weekly',
        verbose_name=_("نوع النمط")
    )
    
    # Shifts in Pattern
    shifts = models.ManyToManyField(
        WorkShiftEnhanced,
        through='ShiftPatternAssignment',
        verbose_name=_("الورديات")
    )
    
    # Rotation Settings
    rotation_days = models.PositiveIntegerField(
        default=7,
        verbose_name=_("أيام الدوران")
    )
    
    rotation_order = models.JSONField(
        default=list,
        verbose_name=_("ترتيب الدوران"),
        help_text=_("ترتيب الورديات في الدوران")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    # System Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        verbose_name = _("نمط وردية محسن")
        verbose_name_plural = _("أنماط الورديات المحسنة")
        db_table = 'hrms_shift_pattern_enhanced'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_shift_for_date(self, start_date, target_date):
        """الحصول على الوردية لتاريخ محدد"""
        if self.pattern_type == 'weekly':
            weekday = target_date.weekday()
            assignments = self.pattern_assignments.filter(day_of_week=weekday)
            if assignments.exists():
                return assignments.first().shift
        
        elif self.pattern_type == 'rotating':
            days_diff = (target_date - start_date).days
            rotation_position = days_diff % self.rotation_days
            
            if rotation_position < len(self.rotation_order):
                shift_id = self.rotation_order[rotation_position]
                try:
                    return WorkShiftEnhanced.objects.get(id=shift_id)
                except WorkShiftEnhanced.DoesNotExist:
                    pass
        
        return None


class ShiftPatternAssignment(models.Model):
    """تعيين الورديات في النمط"""
    
    pattern = models.ForeignKey(
        ShiftPatternEnhanced,
        on_delete=models.CASCADE,
        related_name='pattern_assignments',
        verbose_name=_("النمط")
    )
    
    shift = models.ForeignKey(
        WorkShiftEnhanced,
        on_delete=models.CASCADE,
        verbose_name=_("الوردية")
    )
    
    day_of_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        verbose_name=_("يوم الأسبوع"),
        help_text=_("0=الاثنين, 6=الأحد")
    )
    
    sequence_order = models.PositiveIntegerField(
        default=1,
        verbose_name=_("ترتيب التسلسل")
    )
    
    class Meta:
        verbose_name = _("تعيين نمط وردية")
        verbose_name_plural = _("تعيينات أنماط الورديات")
        db_table = 'hrms_shift_pattern_assignment'
        unique_together = [['pattern', 'day_of_week'], ['pattern', 'sequence_order']]
        ordering = ['sequence_order']
    
    def __str__(self):
        return f"{self.pattern.name} - {self.shift.name}"