"""
نماذج الحضور والانصراف المحسنة
Enhanced Attendance Models
"""
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .base import BaseModel, AuditableModel
from .hr import Employee


class AttendanceRule(BaseModel):
    """قواعد الحضور المحسنة"""
    name = models.CharField(max_length=100, verbose_name=_('اسم القاعدة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))

    # Working Hours
    shift_start_time = models.TimeField(verbose_name=_('وقت بداية الوردية'))
    shift_end_time = models.TimeField(verbose_name=_('وقت نهاية الوردية'))
    break_start_time = models.TimeField(blank=True, null=True, verbose_name=_('وقت بداية الاستراحة'))
    break_end_time = models.TimeField(blank=True, null=True, verbose_name=_('وقت نهاية الاستراحة'))
    break_duration_minutes = models.PositiveIntegerField(default=60, verbose_name=_('مدة الاستراحة بالدقائق'))

    # Tolerance Settings
    late_tolerance_minutes = models.PositiveIntegerField(default=15, verbose_name=_('تسامح التأخير بالدقائق'))
    early_leave_tolerance_minutes = models.PositiveIntegerField(default=15, verbose_name=_('تسامح المغادرة المبكرة بالدقائق'))

    # Overtime Settings
    overtime_start_after_minutes = models.PositiveIntegerField(default=0, verbose_name=_('بداية الوقت الإضافي بعد (دقائق)'))
    max_overtime_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=4, verbose_name=_('الحد الأقصى للوقت الإضافي يومياً'))
    max_overtime_hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name=_('الحد الأقصى للوقت الإضافي أسبوعياً'))

    # Working Days
    work_days = models.CharField(max_length=20, default='0,1,2,3,4', verbose_name=_('أيام العمل'),
                                help_text=_('أرقام أيام الأسبوع مفصولة بفواصل (0=الاثنين, 6=الأحد)'))

    # Flexible Settings
    is_flexible_time = models.BooleanField(default=False, verbose_name=_('وقت مرن'))
    flexible_start_time = models.TimeField(blank=True, null=True, verbose_name=_('أقرب وقت دخول مرن'))
    flexible_end_time = models.TimeField(blank=True, null=True, verbose_name=_('أبعد وقت خروج مرن'))
    minimum_work_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8, verbose_name=_('الحد الأدنى لساعات العمل'))

    # Automatic Calculations
    auto_deduct_break = models.BooleanField(default=True, verbose_name=_('خصم الاستراحة تلقائياً'))
    auto_calculate_overtime = models.BooleanField(default=True, verbose_name=_('حساب الوقت الإضافي تلقائياً'))

    class Meta:
        """Meta class"""
        verbose_name = _('قاعدة حضور')
        verbose_name_plural = _('قواعد الحضور')
        ordering = ['name']

    def __str__(self):
        """__str__ function"""
        return self.name

    def get_work_days_list(self):
        """الحصول على قائمة أيام العمل"""
        return [int(day) for day in self.work_days.split(',') if day.strip()]

    def is_work_day(self, date_obj):
        """فحص إذا كان التاريخ يوم عمل"""
        weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
        return weekday in self.get_work_days_list()

    def calculate_expected_work_hours(self):
        """حساب ساعات العمل المتوقعة"""
        shift_duration = datetime.combine(date.today(), self.shift_end_time) - datetime.combine(date.today(), self.shift_start_time)
        total_minutes = shift_duration.total_seconds() / 60

        if self.auto_deduct_break:
            total_minutes -= self.break_duration_minutes

        return total_minutes / 60

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}

        if self.shift_start_time >= self.shift_end_time:
            errors['shift_end_time'] = _('وقت نهاية الوردية يجب أن يكون بعد وقت البداية')

        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                errors['break_end_time'] = _('وقت نهاية الاستراحة يجب أن يكون بعد وقت البداية')

        if self.is_flexible_time:
            if not self.flexible_start_time or not self.flexible_end_time:
                errors['flexible_start_time'] = _('يجب تحديد أوقات الدوام المرن')

        if errors:
            raise ValidationError(errors)


class EmployeeAttendanceProfile(BaseModel):
    """ملف حضور الموظف"""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='attendance_profile', verbose_name=_('الموظف'))
    attendance_rule = models.ForeignKey(AttendanceRule, on_delete=models.PROTECT, verbose_name=_('قاعدة الحضور'))

    # Custom Settings
    custom_shift_start = models.TimeField(blank=True, null=True, verbose_name=_('وقت دخول مخصص'))
    custom_shift_end = models.TimeField(blank=True, null=True, verbose_name=_('وقت خروج مخصص'))
    custom_work_days = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('أيام عمل مخصصة'))

    # Status
    is_attendance_tracked = models.BooleanField(default=True, verbose_name=_('تتبع الحضور'))
    is_overtime_eligible = models.BooleanField(default=True, verbose_name=_('مؤهل للوقت الإضافي'))

    # Device Integration
    device_user_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('معرف المستخدم في الجهاز'))
    fingerprint_enrolled = models.BooleanField(default=False, verbose_name=_('تم تسجيل البصمة'))
    face_enrolled = models.BooleanField(default=False, verbose_name=_('تم تسجيل الوجه'))

    class Meta:
        """Meta class"""
        verbose_name = _('ملف حضور موظف')
        verbose_name_plural = _('ملفات حضور الموظفين')

    def __str__(self):
        """__str__ function"""
        return f"{self.employee.get_full_name()} - {self.attendance_rule.name}"

    def get_effective_shift_start(self):
        """الحصول على وقت الدخول الفعلي"""
        return self.custom_shift_start or self.attendance_rule.shift_start_time

    def get_effective_shift_end(self):
        """الحصول على وقت الخروج الفعلي"""
        return self.custom_shift_end or self.attendance_rule.shift_end_time

    def get_effective_work_days(self):
        """الحصول على أيام العمل الفعلية"""
        if self.custom_work_days:
            return [int(day) for day in self.custom_work_days.split(',') if day.strip()]
        return self.attendance_rule.get_work_days_list()


class AttendanceRecord(AuditableModel):
    """سجل الحضور المحسن"""
    RECORD_TYPES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('early_leave', _('مغادرة مبكرة')),
        ('holiday', _('عطلة')),
        ('leave', _('إجازة')),
        ('sick_leave', _('إجازة مرضية')),
        ('business_trip', _('مهمة عمل')),
        ('training', _('تدريب')),
        ('overtime', _('وقت إضافي')),
    ]

    ATTENDANCE_STATUS = [
        ('on_time', _('في الوقت')),
        ('late', _('متأخر')),
        ('very_late', _('متأخر جداً')),
        ('absent', _('غائب')),
        ('partial', _('حضور جزئي')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records', verbose_name=_('الموظف'))
    attendance_date = models.DateField(verbose_name=_('تاريخ الحضور'))

    # Time Records
    check_in_time = models.DateTimeField(blank=True, null=True, verbose_name=_('وقت الدخول'))
    check_out_time = models.DateTimeField(blank=True, null=True, verbose_name=_('وقت الخروج'))
    break_out_time = models.DateTimeField(blank=True, null=True, verbose_name=_('وقت خروج الاستراحة'))
    break_in_time = models.DateTimeField(blank=True, null=True, verbose_name=_('وقت عودة الاستراحة'))

    # Calculated Fields
    total_work_minutes = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي دقائق العمل'))
    break_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق الاستراحة'))
    late_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق التأخير'))
    early_leave_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق المغادرة المبكرة'))
    overtime_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق الوقت الإضافي'))

    # Status and Classification
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='present', verbose_name=_('نوع السجل'))
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='on_time', verbose_name=_('حالة الحضور'))

    # Additional Information
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الموقع'))
    device_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم الجهاز'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('عنوان IP'))

    # Manual Adjustments
    is_manual_entry = models.BooleanField(default=False, verbose_name=_('إدخال يدوي'))
    manual_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب الإدخال اليدوي'))
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_attendance', verbose_name=_('معتمد بواسطة'))

    # Comments and Notes
    employee_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات الموظف'))
    manager_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات المدير'))

    class Meta:
        """Meta class"""
        verbose_name = _('سجل حضور')
        verbose_name_plural = _('سجلات الحضور')
        unique_together = ['employee', 'attendance_date']
        ordering = ['-attendance_date', 'employee__emp_code']
        indexes = [
            models.Index(fields=['employee', 'attendance_date']),
            models.Index(fields=['attendance_date']),
            models.Index(fields=['record_type']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.employee.get_full_name()} - {self.attendance_date}"

    @property
    def work_hours(self):
        """ساعات العمل"""
        return self.total_work_minutes / 60

    @property
    def break_hours(self):
        """ساعات الاستراحة"""
        return self.break_minutes / 60

    @property
    def late_hours(self):
        """ساعات التأخير"""
        return self.late_minutes / 60

    @property
    def overtime_hours(self):
        """ساعات الوقت الإضافي"""
        return self.overtime_minutes / 60

    @property
    def net_work_minutes(self):
        """صافي دقائق العمل (بعد خصم الاستراحة)"""
        return max(0, self.total_work_minutes - self.break_minutes)

    @property
    def is_full_day_present(self):
        """فحص إذا كان حاضراً طوال اليوم"""
        return self.check_in_time and self.check_out_time and self.record_type == 'present'

    def calculate_work_duration(self):
        """حساب مدة العمل الإجمالية"""
        if not self.check_in_time or not self.check_out_time:
            return 0

        total_duration = self.check_out_time - self.check_in_time
        total_minutes = int(total_duration.total_seconds() / 60)

        # خصم فترة الاستراحة إذا كانت محددة
        if self.break_out_time and self.break_in_time:
            break_duration = self.break_in_time - self.break_out_time
            break_minutes = int(break_duration.total_seconds() / 60)
            self.break_minutes = break_minutes
            total_minutes -= break_minutes

        return max(0, total_minutes)

    def calculate_attendance_metrics(self):
        """حساب مقاييس الحضور"""
        if not self.employee.attendance_profile:
            return

        profile = self.employee.attendance_profile
        rule = profile.attendance_rule

        # حساب مدة العمل
        self.total_work_minutes = self.calculate_work_duration()

        # حساب التأخير
        if self.check_in_time:
            expected_start = datetime.combine(self.attendance_date, profile.get_effective_shift_start())
            if self.check_in_time > expected_start:
                late_duration = self.check_in_time - expected_start
                self.late_minutes = max(0, int(late_duration.total_seconds() / 60) - rule.late_tolerance_minutes)

        # حساب المغادرة المبكرة
        if self.check_out_time:
            expected_end = datetime.combine(self.attendance_date, profile.get_effective_shift_end())
            if self.check_out_time < expected_end:
                early_duration = expected_end - self.check_out_time
                self.early_leave_minutes = max(0, int(early_duration.total_seconds() / 60) - rule.early_leave_tolerance_minutes)

        # حساب الوقت الإضافي
        if self.check_out_time and profile.is_overtime_eligible:
            expected_end = datetime.combine(self.attendance_date, profile.get_effective_shift_end())
            overtime_start = expected_end + timedelta(minutes=rule.overtime_start_after_minutes)
            if self.check_out_time > overtime_start:
                overtime_duration = self.check_out_time - overtime_start
                self.overtime_minutes = int(overtime_duration.total_seconds() / 60)

        # تحديد حالة الحضور
        self._determine_attendance_status()

    def _determine_attendance_status(self):
        """تحديد حالة الحضور"""
        if not self.check_in_time:
            self.attendance_status = 'absent'
            self.record_type = 'absent'
        elif self.late_minutes > 60:  # متأخر أكثر من ساعة
            self.attendance_status = 'very_late'
            self.record_type = 'late'
        elif self.late_minutes > 0:
            self.attendance_status = 'late'
            self.record_type = 'late'
        elif not self.check_out_time:
            self.attendance_status = 'partial'
            self.record_type = 'present'
        else:
            self.attendance_status = 'on_time'
            self.record_type = 'present'

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}

        if self.check_in_time and self.check_out_time:
            if self.check_in_time >= self.check_out_time:
                errors['check_out_time'] = _('وقت الخروج يجب أن يكون بعد وقت الدخول')

        if self.break_out_time and self.break_in_time:
            if self.break_out_time >= self.break_in_time:
                errors['break_in_time'] = _('وقت عودة الاستراحة يجب أن يكون بعد وقت الخروج للاستراحة')

        if self.attendance_date > date.today():
            errors['attendance_date'] = _('لا يمكن تسجيل حضور لتاريخ مستقبلي')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """حفظ محسن مع حساب المقاييس"""
        if self.check_in_time or self.check_out_time:
            self.calculate_attendance_metrics()
        super().save(*args, **kwargs)


class AttendanceSummary(BaseModel):
    """ملخص الحضور الشهري المحسن"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_summaries', verbose_name=_('الموظف'))
    year = models.PositiveIntegerField(verbose_name=_('السنة'))
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name=_('الشهر'))

    # Working Days
    total_working_days = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي أيام العمل'))
    present_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الحضور'))
    absent_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الغياب'))
    late_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام التأخير'))
    early_leave_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام المغادرة المبكرة'))

    # Leave Days
    annual_leave_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name=_('أيام الإجازة السنوية'))
    sick_leave_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name=_('أيام الإجازة المرضية'))
    other_leave_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name=_('أيام إجازات أخرى'))

    # Time Calculations
    total_work_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('إجمالي ساعات العمل'))
    regular_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('الساعات العادية'))
    overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('ساعات إضافية'))
    total_late_minutes = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي دقائق التأخير'))
    total_early_leave_minutes = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي دقائق المغادرة المبكرة'))

    # Performance Metrics
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('معدل الحضور'))
    punctuality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('معدل الالتزام بالوقت'))

    # Calculation Metadata
    last_calculated = models.DateTimeField(auto_now=True, verbose_name=_('آخر حساب'))
    is_finalized = models.BooleanField(default=False, verbose_name=_('مؤكد'))
    finalized_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='finalized_summaries', verbose_name=_('أكد بواسطة'))
    finalized_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التأكيد'))

    class Meta:
        """Meta class"""
        verbose_name = _('ملخص حضور')
        verbose_name_plural = _('ملخصات الحضور')
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month', 'employee__emp_code']

    def __str__(self):
        """__str__ function"""
        return f"{self.employee.get_full_name()} - {self.year}/{self.month:02d}"

    @property
    def total_leave_days(self):
        """إجمالي أيام الإجازات"""
        return self.annual_leave_days + self.sick_leave_days + self.other_leave_days

    @property
    def effective_working_days(self):
        """أيام العمل الفعلية (بعد خصم الإجازات)"""
        return self.total_working_days - float(self.total_leave_days)

    def calculate_rates(self):
        """حساب المعدلات"""
        # معدل الحضور
        if self.effective_working_days > 0:
            self.attendance_rate = (self.present_days / self.effective_working_days) * 100
        else:
            self.attendance_rate = 0

        # معدل الالتزام بالوقت
        if self.present_days > 0:
            self.punctuality_rate = ((self.present_days - self.late_days) / self.present_days) * 100
        else:
            self.punctuality_rate = 0

    def finalize(self, finalized_by=None):
        """تأكيد الملخص"""
        self.is_finalized = True
        self.finalized_by = finalized_by
        self.finalized_at = timezone.now()
        self.save()

    @classmethod
    def calculate_for_employee_month(cls, employee, year, month):
        """حساب ملخص الحضور لموظف وشهر محدد"""
        from calendar import monthrange

        # الحصول على أو إنشاء الملخص
        summary, created = cls.objects.get_or_create(
            employee=employee,
            year=year,
            month=month,
            defaults={'created_by': employee.user_account}
        )

        # تاريخ بداية ونهاية الشهر
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        # الحصول على سجلات الحضور للشهر
        attendance_records = AttendanceRecord.objects.filter(
            employee=employee,
            attendance_date__range=[start_date, end_date]
        )

        # حساب الإحصائيات
        summary.present_days = attendance_records.filter(record_type='present').count()
        summary.absent_days = attendance_records.filter(record_type='absent').count()
        summary.late_days = attendance_records.filter(late_minutes__gt=0).count()
        summary.early_leave_days = attendance_records.filter(early_leave_minutes__gt=0).count()

        # حساب الساعات
        summary.total_work_hours = sum(record.work_hours for record in attendance_records)
        summary.overtime_hours = sum(record.overtime_hours for record in attendance_records)
        summary.regular_hours = summary.total_work_hours - summary.overtime_hours

        # حساب دقائق التأخير والمغادرة المبكرة
        summary.total_late_minutes = sum(record.late_minutes for record in attendance_records)
        summary.total_early_leave_minutes = sum(record.early_leave_minutes for record in attendance_records)

        # حساب أيام العمل الإجمالية (بناءً على قاعدة الحضور)
        if employee.attendance_profile:
            work_days = employee.attendance_profile.get_effective_work_days()
            total_days = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() in work_days:
                    total_days += 1
                current_date += timedelta(days=1)
            summary.total_working_days = total_days

        # حساب المعدلات
        summary.calculate_rates()

        summary.save()
        return summary
