"""
Attendance Record Models for HRMS
Handles attendance records and time tracking
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import datetime, date, time, timedelta


class AttendanceRecord(models.Model):
    """
    نموذج سجل الحضور - تسجيل دخول وخروج الموظفين
    """
    RECORD_TYPES = [
        ('check_in', _('دخول')),
        ('check_out', _('خروج')),
        ('break_out', _('خروج استراحة')),
        ('break_in', _('عودة من الاستراحة')),
        ('overtime_in', _('دخول وقت إضافي')),
        ('overtime_out', _('خروج وقت إضافي')),
    ]
    
    VERIFICATION_METHODS = [
        ('fingerprint', _('بصمة الإصبع')),
        ('face', _('التعرف على الوجه')),
        ('card', _('البطاقة')),
        ('pin', _('رمز PIN')),
        ('manual', _('يدوي')),
        ('web', _('عبر الويب')),
        ('mobile', _('عبر الجوال')),
    ]
    
    STATUS_CHOICES = [
        ('valid', _('صحيح')),
        ('invalid', _('غير صحيح')),
        ('duplicate', _('مكرر')),
        ('suspicious', _('مشكوك فيه')),
        ('corrected', _('مصحح')),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('المعرف')
    )
    
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_('الموظف')
    )
    
    machine = models.ForeignKey(
        'Hr.AttendanceMachine',
        on_delete=models.SET_NULL,
        related_name='attendance_records',
        null=True,
        blank=True,
        verbose_name=_('جهاز الحضور')
    )
    
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPES,
        verbose_name=_('نوع السجل')
    )
    
    timestamp = models.DateTimeField(
        verbose_name=_('الوقت والتاريخ'),
        help_text=_('وقت وتاريخ تسجيل الحضور')
    )
    
    date = models.DateField(
        auto_now_add=True,
        verbose_name=_('التاريخ'),
        help_text=_('تاريخ الحضور (يتم حسابه تلقائياً)')
    )
    
    time = models.TimeField(
        auto_now_add=True,
        verbose_name=_('الوقت'),
        help_text=_('وقت الحضور (يتم حسابه تلقائياً)')
    )
    
    verification_method = models.CharField(
        max_length=20,
        choices=VERIFICATION_METHODS,
        default='fingerprint',
        verbose_name=_('طريقة التحقق')
    )
    
    device_user_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('معرف المستخدم في الجهاز'),
        help_text=_('معرف الموظف في جهاز الحضور')
    )
    
    raw_data = models.TextField(
        blank=True,
        verbose_name=_('البيانات الخام'),
        help_text=_('البيانات الخام من الجهاز')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='valid',
        verbose_name=_('الحالة')
    )
    
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_('تم المعالجة'),
        help_text=_('هل تم معالجة هذا السجل؟')
    )
    
    is_manual = models.BooleanField(
        default=False,
        verbose_name=_('يدوي'),
        help_text=_('هل تم إدخال هذا السجل يدوياً؟')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات'),
        help_text=_('ملاحظات إضافية حول السجل')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_attendance_records',
        null=True,
        blank=True,
        verbose_name=_('أنشئ بواسطة')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('سجل حضور')
        verbose_name_plural = _('سجلات الحضور')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'record_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['machine']),
            models.Index(fields=['status']),
            models.Index(fields=['is_processed']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.get_record_type_display()} - {self.timestamp}"

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.timestamp:
            # التحقق من أن الوقت ليس في المستقبل
            if self.timestamp > timezone.now():
                raise ValidationError(_('لا يمكن أن يكون وقت الحضور في المستقبل'))
        
        # التحقق من عدم وجود سجلات مكررة
        if self.employee and self.timestamp:
            duplicate_records = AttendanceRecord.objects.filter(
                employee=self.employee,
                timestamp=self.timestamp,
                record_type=self.record_type
            ).exclude(id=self.id)
            
            if duplicate_records.exists():
                self.status = 'duplicate'

    def save(self, *args, **kwargs):
        # حساب التاريخ والوقت تلقائياً
        if self.timestamp:
            self.date = self.timestamp.date()
            self.time = self.timestamp.time()
        
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_late(self):
        """هل هذا السجل متأخر؟"""
        if self.record_type != 'check_in':
            return False
        
        # الحصول على الوردية المخصصة للموظف
        from .work_shift_models import ShiftAssignment
        shift_assignment = ShiftAssignment.get_employee_current_shift(
            self.employee, self.date
        )
        
        if not shift_assignment:
            return False
        
        shift = shift_assignment.shift
        late_minutes = shift.calculate_late_minutes(self.time)
        return late_minutes > 0

    @property
    def late_minutes(self):
        """عدد دقائق التأخير"""
        if self.record_type != 'check_in':
            return 0
        
        from .work_shift_models import ShiftAssignment
        shift_assignment = ShiftAssignment.get_employee_current_shift(
            self.employee, self.date
        )
        
        if not shift_assignment:
            return 0
        
        shift = shift_assignment.shift
        return shift.calculate_late_minutes(self.time)

    @property
    def is_overtime(self):
        """هل هذا السجل وقت إضافي؟"""
        if self.record_type != 'check_out':
            return False
        
        from .work_shift_models import ShiftAssignment
        shift_assignment = ShiftAssignment.get_employee_current_shift(
            self.employee, self.date
        )
        
        if not shift_assignment:
            return False
        
        shift = shift_assignment.shift
        overtime_minutes = shift.calculate_overtime_minutes(self.time)
        return overtime_minutes > 0

    @property
    def overtime_minutes(self):
        """عدد دقائق الوقت الإضافي"""
        if self.record_type != 'check_out':
            return 0
        
        from .work_shift_models import ShiftAssignment
        shift_assignment = ShiftAssignment.get_employee_current_shift(
            self.employee, self.date
        )
        
        if not shift_assignment:
            return 0
        
        shift = shift_assignment.shift
        return shift.calculate_overtime_minutes(self.time)

    def mark_as_processed(self):
        """تسجيل السجل كمعالج"""
        self.is_processed = True
        self.save(update_fields=['is_processed'])

    @classmethod
    def get_employee_records_for_date(cls, employee, date):
        """الحصول على سجلات موظف لتاريخ معين"""
        return cls.objects.filter(
            employee=employee,
            date=date,
            status='valid'
        ).order_by('timestamp')

    @classmethod
    def get_employee_records_for_period(cls, employee, start_date, end_date):
        """الحصول على سجلات موظف لفترة معينة"""
        return cls.objects.filter(
            employee=employee,
            date__range=[start_date, end_date],
            status='valid'
        ).order_by('date', 'timestamp')

    @classmethod
    def create_manual_record(cls, employee, record_type, timestamp, created_by, notes=''):
        """إنشاء سجل حضور يدوي"""
        return cls.objects.create(
            employee=employee,
            record_type=record_type,
            timestamp=timestamp,
            verification_method='manual',
            is_manual=True,
            notes=notes,
            created_by=created_by
        )


class AttendanceSummary(models.Model):
    """
    نموذج ملخص الحضور اليومي - ملخص حضور الموظف لكل يوم
    """
    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('half_day', _('نصف يوم')),
        ('holiday', _('عطلة')),
        ('leave', _('إجازة')),
        ('weekend', _('نهاية أسبوع')),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('المعرف')
    )
    
    employee = models.ForeignKey(
        'Hr.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
        verbose_name=_('الموظف')
    )
    
    date = models.DateField(
        verbose_name=_('التاريخ')
    )
    
    shift = models.ForeignKey(
        'Hr.WorkShift',
        on_delete=models.SET_NULL,
        related_name='attendance_summaries',
        null=True,
        blank=True,
        verbose_name=_('الوردية')
    )
    
    check_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('وقت الدخول')
    )
    
    check_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('وقت الخروج')
    )
    
    total_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        verbose_name=_('إجمالي الساعات')
    )
    
    regular_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        verbose_name=_('الساعات العادية')
    )
    
    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        verbose_name=_('ساعات الوقت الإضافي')
    )
    
    break_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        verbose_name=_('ساعات الاستراحة')
    )
    
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('دقائق التأخير')
    )
    
    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('دقائق المغادرة المبكرة')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name=_('الحالة')
    )
    
    is_holiday = models.BooleanField(
        default=False,
        verbose_name=_('عطلة'),
        help_text=_('هل هذا اليوم عطلة رسمية؟')
    )
    
    is_weekend = models.BooleanField(
        default=False,
        verbose_name=_('نهاية أسبوع'),
        help_text=_('هل هذا اليوم نهاية أسبوع؟')
    )
    
    is_leave = models.BooleanField(
        default=False,
        verbose_name=_('إجازة'),
        help_text=_('هل الموظف في إجازة؟')
    )
    
    leave_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('نوع الإجازة'),
        help_text=_('نوع الإجازة إذا كان في إجازة')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('ملخص حضور يومي')
        verbose_name_plural = _('ملخصات الحضور اليومية')
        unique_together = ['employee', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_holiday']),
            models.Index(fields=['is_weekend']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.get_status_display()}"

    @property
    def worked_hours(self):
        """الساعات المعملة فعلياً (بدون الاستراحة)"""
        return self.total_hours - self.break_hours

    @property
    def is_full_day(self):
        """هل عمل يوم كامل؟"""
        if not self.shift:
            return False
        return self.worked_hours >= (self.shift.total_hours * 0.8)  # 80% من ساعات الوردية

    @property
    def attendance_percentage(self):
        """نسبة الحضور"""
        if not self.shift or self.shift.total_hours == 0:
            return 0
        return min(100, (float(self.worked_hours) / float(self.shift.total_hours)) * 100)

    def calculate_summary(self):
        """حساب ملخص الحضور من السجلات"""
        records = AttendanceRecord.get_employee_records_for_date(
            self.employee, self.date
        )
        
        if not records.exists():
            self.status = 'absent'
            return
        
        # البحث عن سجلات الدخول والخروج
        check_in_record = records.filter(record_type='check_in').first()
        check_out_record = records.filter(record_type='check_out').last()
        
        if check_in_record:
            self.check_in_time = check_in_record.time
            self.late_minutes = check_in_record.late_minutes
        
        if check_out_record:
            self.check_out_time = check_out_record.time
        
        # حساب إجمالي الساعات
        if self.check_in_time and self.check_out_time:
            check_in_dt = datetime.combine(self.date, self.check_in_time)
            check_out_dt = datetime.combine(self.date, self.check_out_time)
            
            # إذا كان وقت الخروج قبل وقت الدخول، فهذا يعني أن الخروج في اليوم التالي
            if check_out_dt < check_in_dt:
                check_out_dt += timedelta(days=1)
            
            total_time = check_out_dt - check_in_dt
            self.total_hours = round(total_time.total_seconds() / 3600, 2)
            
            # خصم وقت الاستراحة
            if self.shift and self.shift.break_duration_minutes > 0:
                self.break_hours = round(self.shift.break_duration_minutes / 60, 2)
            
            # حساب الساعات العادية والإضافية
            if self.shift:
                if self.worked_hours <= self.shift.total_hours:
                    self.regular_hours = self.worked_hours
                    self.overtime_hours = 0
                else:
                    self.regular_hours = self.shift.total_hours
                    self.overtime_hours = self.worked_hours - self.shift.total_hours
        
        # تحديد الحالة
        if self.late_minutes > 0:
            self.status = 'late'
        elif self.is_full_day:
            self.status = 'present'
        elif self.worked_hours > 0:
            self.status = 'half_day'
        else:
            self.status = 'absent'

    @classmethod
    def generate_summary_for_employee(cls, employee, date):
        """إنشاء أو تحديث ملخص الحضور لموظف في تاريخ معين"""
        from .work_shift_models import ShiftAssignment
        
        # الحصول على الوردية المخصصة للموظف
        shift_assignment = ShiftAssignment.get_employee_current_shift(employee, date)
        shift = shift_assignment.shift if shift_assignment else None
        
        # إنشاء أو الحصول على الملخص
        summary, created = cls.objects.get_or_create(
            employee=employee,
            date=date,
            defaults={'shift': shift}
        )
        
        # تحديث الوردية إذا تغيرت
        if summary.shift != shift:
            summary.shift = shift
        
        # حساب الملخص
        summary.calculate_summary()
        summary.save()
        
        return summary

    @classmethod
    def generate_summaries_for_period(cls, employee, start_date, end_date):
        """إنشاء ملخصات الحضور لفترة معينة"""
        current_date = start_date
        summaries = []
        
        while current_date <= end_date:
            summary = cls.generate_summary_for_employee(employee, current_date)
            summaries.append(summary)
            current_date += timedelta(days=1)
        
        return summaries