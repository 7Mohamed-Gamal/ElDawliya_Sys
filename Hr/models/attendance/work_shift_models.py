"""
Work Shift Models for HRMS
Handles work shifts and scheduling
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import datetime, time, timedelta


class WorkShift(models.Model):
    """
    نموذج الوردية - يحدد أوقات العمل والورديات
    """
    SHIFT_TYPES = [
        ('regular', _('عادية')),
        ('night', _('ليلية')),
        ('split', _('مقسمة')),
        ('flexible', _('مرنة')),
        ('rotating', _('متناوبة')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('suspended', _('معلق')),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('المعرف')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم الوردية'),
        help_text=_('مثال: الوردية الصباحية')
    )
    
    name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('الاسم بالإنجليزية'),
        help_text=_('Morning Shift')
    )
    
    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPES,
        default='regular',
        verbose_name=_('نوع الوردية')
    )
    
    start_time = models.TimeField(
        verbose_name=_('وقت البداية'),
        help_text=_('وقت بداية الوردية')
    )
    
    end_time = models.TimeField(
        verbose_name=_('وقت النهاية'),
        help_text=_('وقت نهاية الوردية')
    )
    
    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('بداية الاستراحة'),
        help_text=_('وقت بداية استراحة الغداء')
    )
    
    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('نهاية الاستراحة'),
        help_text=_('وقت نهاية استراحة الغداء')
    )
    
    total_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_('إجمالي الساعات'),
        help_text=_('إجمالي ساعات العمل في الوردية')
    )
    
    grace_period_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_('فترة السماح (دقيقة)'),
        help_text=_('فترة السماح للتأخير بالدقائق')
    )
    
    overtime_threshold_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name=_('حد الوقت الإضافي (دقيقة)'),
        help_text=_('الحد الأدنى للوقت الإضافي بالدقائق')
    )
    
    is_overnight = models.BooleanField(
        default=False,
        verbose_name=_('وردية ليلية'),
        help_text=_('هل تمتد الوردية لليوم التالي؟')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('الحالة')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف إضافي للوردية')
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
        verbose_name = _('وردية عمل')
        verbose_name_plural = _('ورديات العمل')
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['shift_type']),
            models.Index(fields=['status']),
            models.Index(fields=['start_time', 'end_time']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.start_time and self.end_time:
            # للورديات العادية، وقت النهاية يجب أن يكون بعد وقت البداية
            if not self.is_overnight and self.start_time >= self.end_time:
                raise ValidationError(_('وقت النهاية يجب أن يكون بعد وقت البداية'))
        
        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                raise ValidationError(_('وقت نهاية الاستراحة يجب أن يكون بعد وقت البداية'))
            
            # التحقق من أن الاستراحة ضمن وقت العمل
            if not self.is_overnight:
                if (self.break_start_time < self.start_time or 
                    self.break_end_time > self.end_time):
                    raise ValidationError(_('وقت الاستراحة يجب أن يكون ضمن وقت العمل'))

    def save(self, *args, **kwargs):
        # حساب إجمالي الساعات تلقائياً
        if self.start_time and self.end_time:
            self.total_hours = self.calculate_total_hours()
        self.full_clean()
        super().save(*args, **kwargs)

    def calculate_total_hours(self):
        """حساب إجمالي ساعات العمل"""
        if not self.start_time or not self.end_time:
            return 0
        
        # تحويل الأوقات إلى datetime للحساب
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        
        # إذا كانت وردية ليلية
        if self.is_overnight:
            end_dt += timedelta(days=1)
        
        # حساب إجمالي الوقت
        total_time = end_dt - start_dt
        total_hours = total_time.total_seconds() / 3600
        
        # خصم وقت الاستراحة
        if self.break_start_time and self.break_end_time:
            break_start_dt = datetime.combine(datetime.today(), self.break_start_time)
            break_end_dt = datetime.combine(datetime.today(), self.break_end_time)
            break_time = break_end_dt - break_start_dt
            break_hours = break_time.total_seconds() / 3600
            total_hours -= break_hours
        
        return round(total_hours, 2)

    @property
    def break_duration_minutes(self):
        """مدة الاستراحة بالدقائق"""
        if self.break_start_time and self.break_end_time:
            break_start_dt = datetime.combine(datetime.today(), self.break_start_time)
            break_end_dt = datetime.combine(datetime.today(), self.break_end_time)
            break_time = break_end_dt - break_start_dt
            return int(break_time.total_seconds() / 60)
        return 0

    def is_time_within_shift(self, check_time):
        """التحقق من أن الوقت ضمن الوردية"""
        if not isinstance(check_time, time):
            return False
        
        if self.is_overnight:
            # للورديات الليلية
            return check_time >= self.start_time or check_time <= self.end_time
        else:
            # للورديات العادية
            return self.start_time <= check_time <= self.end_time

    def calculate_late_minutes(self, arrival_time):
        """حساب دقائق التأخير"""
        if not isinstance(arrival_time, time):
            return 0
        
        # تحويل إلى datetime للحساب
        shift_start = datetime.combine(datetime.today(), self.start_time)
        arrival_dt = datetime.combine(datetime.today(), arrival_time)
        
        # إذا وصل قبل وقت البداية، لا يوجد تأخير
        if arrival_dt <= shift_start:
            return 0
        
        # حساب التأخير
        late_time = arrival_dt - shift_start
        late_minutes = int(late_time.total_seconds() / 60)
        
        # إذا كان التأخير ضمن فترة السماح
        if late_minutes <= self.grace_period_minutes:
            return 0
        
        return late_minutes

    def calculate_overtime_minutes(self, departure_time):
        """حساب دقائق الوقت الإضافي"""
        if not isinstance(departure_time, time):
            return 0
        
        # تحويل إلى datetime للحساب
        shift_end = datetime.combine(datetime.today(), self.end_time)
        departure_dt = datetime.combine(datetime.today(), departure_time)
        
        # للورديات الليلية
        if self.is_overnight and departure_time < self.end_time:
            departure_dt += timedelta(days=1)
        
        # إذا غادر قبل وقت النهاية، لا يوجد وقت إضافي
        if departure_dt <= shift_end:
            return 0
        
        # حساب الوقت الإضافي
        overtime = departure_dt - shift_end
        overtime_minutes = int(overtime.total_seconds() / 60)
        
        # إذا كان الوقت الإضافي أقل من الحد الأدنى
        if overtime_minutes < self.overtime_threshold_minutes:
            return 0
        
        return overtime_minutes

    @classmethod
    def get_active_shifts(cls):
        """الحصول على الورديات النشطة"""
        return cls.objects.filter(status='active')

    @classmethod
    def get_shift_for_time(cls, check_time):
        """الحصول على الوردية المناسبة لوقت معين"""
        active_shifts = cls.get_active_shifts()
        for shift in active_shifts:
            if shift.is_time_within_shift(check_time):
                return shift
        return None


class ShiftAssignment(models.Model):
    """
    نموذج تعيين الوردية - ربط الموظفين بالورديات
    """
    ASSIGNMENT_TYPES = [
        ('permanent', _('دائم')),
        ('temporary', _('مؤقت')),
        ('rotating', _('متناوب')),
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
        related_name='shift_assignments',
        verbose_name=_('الموظف')
    )
    
    shift = models.ForeignKey(
        WorkShift,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('الوردية')
    )
    
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default='permanent',
        verbose_name=_('نوع التعيين')
    )
    
    start_date = models.DateField(
        verbose_name=_('تاريخ البداية'),
        help_text=_('تاريخ بداية تعيين الوردية')
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ النهاية'),
        help_text=_('تاريخ نهاية تعيين الوردية (اختياري للتعيين الدائم)')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل هذا التعيين نشط؟')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات'),
        help_text=_('ملاحظات إضافية حول تعيين الوردية')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_shift_assignments_basic',
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
        verbose_name = _('تعيين وردية')
        verbose_name_plural = _('تعيينات الورديات')
        ordering = ['-start_date']
        unique_together = ['employee', 'shift', 'start_date']
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['shift', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.shift} ({self.start_date})"

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
        
        # التحقق من عدم تداخل التعيينات النشطة للموظف نفسه
        if self.is_active and self.employee:
            overlapping = ShiftAssignment.objects.filter(
                employee=self.employee,
                is_active=True
            ).exclude(id=self.id)
            
            for assignment in overlapping:
                # التحقق من التداخل
                if self.start_date <= (assignment.end_date or timezone.now().date()):
                    if not self.end_date or self.end_date >= assignment.start_date:
                        raise ValidationError(
                            _('يوجد تعيين وردية نشط متداخل لهذا الموظف')
                        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_current(self):
        """هل هذا التعيين حالي؟"""
        today = timezone.now().date()
        if not self.is_active:
            return False
        
        if self.start_date > today:
            return False
        
        if self.end_date and self.end_date < today:
            return False
        
        return True

    @classmethod
    def get_employee_current_shift(cls, employee, date=None):
        """الحصول على الوردية الحالية للموظف"""
        if date is None:
            date = timezone.now().date()
        
        return cls.objects.filter(
            employee=employee,
            is_active=True,
            start_date__lte=date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=date)
        ).select_related('shift').first()