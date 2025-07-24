"""
نماذج نظام الحضور والانصراف

هذا الملف يحتوي على نماذج نظام الحضور والانصراف، بما في ذلك
الورديات وأجهزة البصمة وسجلات الحضور
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from Hr.models.core.base_model import HrBaseModel

class AttendanceMachine(HrBaseModel):
    """
    نموذج جهاز الحضور (البصمة)

    يمثل أجهزة البصمة وأنظمة تسجيل الحضور والانصراف
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الجهاز")
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الجهاز")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='attendance_machines',
        verbose_name=_("الشركة")
    )

    location = models.ForeignKey(
        'core.Location',
        on_delete=models.CASCADE,
        related_name='attendance_machines',
        verbose_name=_("الموقع")
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("عنوان IP")
    )

    model = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الطراز")
    )

    serial_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الرقم التسلسلي")
    )

    machine_type = models.CharField(
        max_length=20,
        choices=[
            ('fingerprint', _("بصمة الإصبع")),
            ('face', _("بصمة الوجه")),
            ('card', _("بطاقة")),
            ('pin', _("رقم سري")),
            ('mobile', _("تطبيق جوال")),
            ('multi', _("متعدد"))
        ],
        default='fingerprint',
        verbose_name=_("نوع الجهاز")
    )

    is_connected = models.BooleanField(
        default=True,
        verbose_name=_("متصل")
    )

    last_sync_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر مزامنة")
    )

    timezone_offset = models.SmallIntegerField(
        default=3,  # AST (Arabia Standard Time)
        verbose_name=_("فرق التوقيت")
    )

    sync_interval = models.PositiveSmallIntegerField(
        default=30,
        verbose_name=_("فترة المزامنة (دقائق)")
    )

    api_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("مفتاح API")
    )

    username = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم المستخدم")
    )

    password = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("كلمة المرور")
    )

    class Meta:
        verbose_name = _("جهاز حضور")
        verbose_name_plural = _("أجهزة الحضور")
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.location.name})"

    def sync_attendance_data(self):
        """
        مزامنة بيانات الحضور من الجهاز
        """
        # هذه الوظيفة تعتمد على نوع الجهاز وبروتوكول الاتصال
        # وتختلف حسب الشركة المصنعة للجهاز
        pass

    def test_connection(self):
        """
        اختبار الاتصال بالجهاز
        """
        # اختبار الاتصال بالجهاز حسب نوعه
        # وتحديث حالة الاتصال
        pass


class ShiftType(models.TextChoices):
    """
    أنواع الورديات
    """
    REGULAR = 'regular', _('دوام منتظم')
    FLEXIBLE = 'flexible', _('دوام مرن')
    NIGHT = 'night', _('دوام ليلي')
    ROTATION = 'rotation', _('دوام متناوب')
    SPLIT = 'split', _('دوام مقسم')
    CUSTOM = 'custom', _('مخصص')


class Shift(HrBaseModel):
    """
    نموذج الوردية

    يمثل وردية العمل وأوقات الدوام والمناوبة
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الوردية")
    )

    code = models.CharField(
        max_length=20,
        verbose_name=_("كود الوردية")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='shifts',
        verbose_name=_("الشركة")
    )

    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shifts',
        verbose_name=_("القسم")
    )

    type = models.CharField(
        max_length=20,
        choices=ShiftType.choices,
        default=ShiftType.REGULAR,
        verbose_name=_("نوع الوردية")
    )

    start_time = models.TimeField(
        verbose_name=_("وقت البدء")
    )

    end_time = models.TimeField(
        verbose_name=_("وقت الانتهاء")
    )

    late_grace_minutes = models.PositiveSmallIntegerField(
        default=10,
        verbose_name=_("فترة السماح للتأخير (دقائق)")
    )

    early_leave_grace_minutes = models.PositiveSmallIntegerField(
        default=10,
        verbose_name=_("فترة السماح للمغادرة المبكرة (دقائق)")
    )

    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت بدء الاستراحة")
    )

    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت انتهاء الاستراحة")
    )

    break_duration_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("مدة الاستراحة (دقائق)")
    )

    work_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("ساعات العمل")
    )

    is_night_shift = models.BooleanField(
        default=False,
        verbose_name=_("وردية ليلية")
    )

    is_next_day = models.BooleanField(
        default=False,
        verbose_name=_("تنتهي في اليوم التالي")
    )

    is_flex_time = models.BooleanField(
        default=False,
        verbose_name=_("دوام مرن")
    )

    flex_time_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("بداية الدوام المرن")
    )

    flex_time_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("نهاية الدوام المرن")
    )

    weekly_off_days = models.CharField(
        max_length=20,
        default='5,6',  # الجمعة والسبت
        verbose_name=_("أيام الإجازة الأسبوعية"),
        help_text=_("أرقام الأيام مفصولة بفواصل (0=الاثنين، 6=الأحد)")
    )

    class Meta:
        verbose_name = _("وردية")
        verbose_name_plural = _("الورديات")
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def get_work_hours_display(self):
        """
        عرض ساعات العمل بتنسيق مناسب
        """
        hours = int(self.work_hours)
        minutes = int((self.work_hours - hours) * 60)
        return f"{hours} ساعة و {minutes} دقيقة"

    @property
    def time_range_display(self):
        """
        عرض نطاق الوقت بتنسيق مناسب
        """
        start_format = self.start_time.strftime("%I:%M %p")
        end_format = self.end_time.strftime("%I:%M %p")
        if self.is_next_day:
            return f"{start_format} - {end_format} (اليوم التالي)"
        return f"{start_format} - {end_format}"

    def get_weekly_off_days_list(self):
        """
        الحصول على قائمة أيام الإجازة الأسبوعية
        """
        return [int(day) for day in self.weekly_off_days.split(',') if day.strip()]

    def is_day_off(self, date_obj):
        """
        التحقق مما إذا كان اليوم المحدد يوم إجازة
        """
        weekday = date_obj.weekday()
        return weekday in self.get_weekly_off_days_list()

    def clean(self):
        """
        التحقق من صحة البيانات قبل الحفظ
        """
        # التحقق من وقت البدء والانتهاء
        if self.start_time and self.end_time:
            # تحويل الوقت إلى دقائق لسهولة المقارنة
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute

            # إذا كان ينتهي في اليوم التالي
            if self.is_next_day:
                end_minutes += 24 * 60  # إضافة 24 ساعة

            # التحقق من أن وقت الانتهاء بعد وقت البدء
            if end_minutes <= start_minutes:
                if not self.is_next_day:
                    raise ValidationError({
                        'end_time': _("وقت الانتهاء يجب أن يكون بعد وقت البدء")
                    })

            # حساب ساعات العمل
            work_minutes = end_minutes - start_minutes

            # طرح وقت الاستراحة إن وجد
            if self.break_duration_minutes:
                work_minutes -= self.break_duration_minutes

            # التحقق من ساعات العمل
            calculated_work_hours = round(work_minutes / 60, 2)
            if abs(calculated_work_hours - float(self.work_hours)) > 0.01:
                raise ValidationError({
                    'work_hours': _("ساعات العمل المحسوبة ({}) لا تتطابق مع القيمة المدخلة").format(calculated_work_hours)
                })

        # التحقق من أوقات الاستراحة
        if self.break_start_time and self.break_end_time:
            break_start_minutes = self.break_start_time.hour * 60 + self.break_start_time.minute
            break_end_minutes = self.break_end_time.hour * 60 + self.break_end_time.minute

            # التحقق من أن وقت انتهاء الاستراحة بعد وقت بدء الاستراحة
            if break_end_minutes <= break_start_minutes:
                raise ValidationError({
                    'break_end_time': _("وقت انتهاء الاستراحة يجب أن يكون بعد وقت بدء الاستراحة")
                })

            # حساب مدة الاستراحة
            calculated_break_duration = break_end_minutes - break_start_minutes
            if calculated_break_duration != self.break_duration_minutes:
                raise ValidationError({
                    'break_duration_minutes': _("مدة الاستراحة المحسوبة ({}) لا تتطابق مع القيمة المدخلة").format(calculated_break_duration)
                })

class WorkSchedule(HrBaseModel):
    """
    نموذج جدول العمل

    يمثل جدول العمل للموظف أو مجموعة من الموظفين
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("اسم الجدول")
    )

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='work_schedules',
        verbose_name=_("الشركة")
    )

    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_schedules',
        verbose_name=_("القسم")
    )

    effective_from = models.DateField(
        default=date.today,
        verbose_name=_("تاريخ البدء")
    )

    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء")
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("الوصف")
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name=_("افتراضي")
    )

    class Meta:
        verbose_name = _("جدول عمل")
        verbose_name_plural = _("جداول العمل")
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    def is_active(self):
        """
        التحقق مما إذا كان الجدول نشطًا في التاريخ الحالي
        """
        today = date.today()
        if self.effective_to:
            return self.effective_from <= today <= self.effective_to
        return self.effective_from <= today


class WorkScheduleShift(HrBaseModel):
    """
    نموذج وردية جدول العمل

    يربط بين جدول العمل والوردية ليوم محدد من الأسبوع
    """
    schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        related_name='shifts',
        verbose_name=_("جدول العمل")
    )

    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        related_name='schedule_assignments',
        verbose_name=_("الوردية")
    )

    weekday = models.PositiveSmallIntegerField(
        choices=[
            (0, _("الاثنين")),
            (1, _("الثلاثاء")),
            (2, _("الأربعاء")),
            (3, _("الخميس")),
            (4, _("الجمعة")),
            (5, _("السبت")),
            (6, _("الأحد"))
        ],
        verbose_name=_("يوم الأسبوع")
    )

    is_workday = models.BooleanField(
        default=True,
        verbose_name=_("يوم عمل")
    )

    class Meta:
        verbose_name = _("وردية جدول العمل")
        verbose_name_plural = _("ورديات جدول العمل")
        unique_together = ['schedule', 'weekday']
        ordering = ['schedule', 'weekday']

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.shift.name}"


class EmployeeWorkSchedule(HrBaseModel):
    """
    نموذج جدول عمل الموظف

    يربط الموظف بجدول عمل معين
    """
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='work_schedules',
        verbose_name=_("الموظف")
    )

    schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        related_name='employee_assignments',
        verbose_name=_("جدول العمل")
    )

    effective_from = models.DateField(
        default=date.today,
        verbose_name=_("تاريخ البدء")
    )

    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء")
    )

    class Meta:
        verbose_name = _("جدول عمل الموظف")
        verbose_name_plural = _("جداول عمل الموظفين")
        ordering = ['employee', '-effective_from']

    def __str__(self):
        return f"{self.employee} - {self.schedule.name}"

    def is_active(self):
        """
        التحقق مما إذا كان الجدول نشطًا في التاريخ الحالي
        """
        today = date.today()
        if self.effective_to:
            return self.effective_from <= today <= self.effective_to
        return self.effective_from <= today


class AttendanceStatus(models.TextChoices):
    """
    حالات الحضور
    """
    PRESENT = 'present', _('حاضر')
    ABSENT = 'absent', _('غائب')
    HALF_DAY = 'half_day', _('نصف يوم')
    LATE = 'late', _('متأخر')
    EARLY_LEAVE = 'early_leave', _('مغادرة مبكرة')
    LATE_AND_EARLY_LEAVE = 'late_and_early', _('متأخر ومغادرة مبكرة')
    ON_LEAVE = 'on_leave', _('في إجازة')
    HOLIDAY = 'holiday', _('عطلة رسمية')
    WEEKEND = 'weekend', _('عطلة نهاية الأسبوع')
    BUSINESS_TRIP = 'business_trip', _('مهمة عمل')
    WORK_FROM_HOME = 'work_from_home', _('عمل من المنزل')
    UNPLANNED_LEAVE = 'unplanned_leave', _('إجازة غير مخططة')


class AttendanceRecord(HrBaseModel):
    """
    نموذج سجل الحضور

    يمثل سجل حضور وانصراف الموظف ليوم معين
    """
    employee = models.ForeignKey(
        'employee.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("الموظف")
    )

    date = models.DateField(
        verbose_name=_("التاريخ")
    )

    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
        verbose_name=_("الوردية")
    )

    check_in = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت الحضور")
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت الانصراف")
    )

    check_in_device = models.ForeignKey(
        AttendanceMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='check_ins',
        verbose_name=_("جهاز تسجيل الحضور")
    )

    check_out_device = models.ForeignKey(
        AttendanceMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='check_outs',
        verbose_name=_("جهاز تسجيل الانصراف")
    )

    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.ABSENT,
        verbose_name=_("الحالة")
    )

    late_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("دقائق التأخير")
    )

    early_leave_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("دقائق المغادرة المبكرة")
    )

    overtime_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("دقائق العمل الإضافي")
    )

    worked_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات العمل")
    )

    leave = models.ForeignKey(
        'leave.LeaveRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
        verbose_name=_("الإجازة المرتبطة")
    )

    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )

    is_processed = models.BooleanField(
        default=False,
        verbose_name=_("تمت المعالجة")
    )

    is_manual_entry = models.BooleanField(
        default=False,
        verbose_name=_("إدخال يدوي")
    )

    approved_by = models.ForeignKey(
        'employee.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance_records',
        verbose_name=_("معتمد من")
    )

    class Meta:
        verbose_name = _("سجل حضور")
        verbose_name_plural = _("سجلات الحضور")
        unique_together = ['employee', 'date']
        ordering = ['date', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """
        تخصيص عملية الحفظ لحساب القيم التلقائية
        """
        self.calculate_status()
        self.calculate_worked_hours()
        super().save(*args, **kwargs)

    def calculate_status(self):
        """
        حساب حالة الحضور
        """
        if self.leave:
            self.status = AttendanceStatus.ON_LEAVE
            return

        if not self.shift:
            return

        if self.shift.is_day_off(self.date):
            self.status = AttendanceStatus.WEEKEND
            return

        if not self.check_in and not self.check_out:
            self.status = AttendanceStatus.ABSENT
            return

        if not self.check_out:
            self.status = AttendanceStatus.PRESENT  # يمكن تعديلها لاحقًا عند تسجيل الانصراف
            return

        # حساب دقائق التأخير والمغادرة المبكرة
        if self.check_in and self.shift:
            expected_check_in = datetime.combine(self.date, self.shift.start_time)
            if self.check_in > expected_check_in + timedelta(minutes=self.shift.late_grace_minutes):
                self.late_minutes = int((self.check_in - expected_check_in).total_seconds() / 60)

        if self.check_out and self.shift:
            expected_check_out = datetime.combine(self.date, self.shift.end_time)
            if self.shift.is_next_day:
                expected_check_out += timedelta(days=1)
            if self.check_out < expected_check_out - timedelta(minutes=self.shift.early_leave_grace_minutes):
                self.early_leave_minutes = int((expected_check_out - self.check_out).total_seconds() / 60)

        # تحديد الحالة النهائية
        if self.late_minutes > 0 and self.early_leave_minutes > 0:
            self.status = AttendanceStatus.LATE_AND_EARLY_LEAVE
        elif self.late_minutes > 0:
            self.status = AttendanceStatus.LATE
        elif self.early_leave_minutes > 0:
            self.status = AttendanceStatus.EARLY_LEAVE
        else:
            self.status = AttendanceStatus.PRESENT

    def calculate_worked_hours(self):
        """
        حساب ساعات العمل والعمل الإضافي
        """
        if not self.check_in or not self.check_out:
            self.worked_hours = 0
            return

        # حساب مدة العمل بالساعات
        worked_seconds = (self.check_out - self.check_in).total_seconds()

        # طرح وقت الاستراحة إذا كان مسجلاً
        if self.shift and self.shift.break_duration_minutes > 0:
            worked_seconds -= self.shift.break_duration_minutes * 60

        self.worked_hours = round(worked_seconds / 3600, 2)

        # حساب العمل الإضافي
        if self.shift:
            expected_hours = float(self.shift.work_hours)
            if self.worked_hours > expected_hours:
                self.overtime_minutes = int((self.worked_hours - expected_hours) * 60)
