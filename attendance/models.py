from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Count, Q, Sum
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, time, date, timedelta
# Use the new Employees app model
from employees.models import Employee


class AttendanceRule(models.Model):
    """Model for different attendance rules (e.g., Workers Rule, Management Rule)"""
    name = models.CharField(_('Rule Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    late_grace_period = models.IntegerField(
        _('Late Grace Period (minutes)'),
        default=15,
        validators=[MinValueValidator(0)]
    )
    early_leave_grace_period = models.IntegerField(
        _('Early Leave Grace Period (minutes)'),
        default=15,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Rule')
        verbose_name_plural = _('Attendance Rules')

    def __str__(self):
        return self.name


class WorkSchedule(models.Model):
    """Model for work schedules within attendance rules"""
    DAYS_OF_WEEK = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]

    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('Attendance Rule')
    )
    day_of_week = models.IntegerField(
        _('Day of Week'),
        choices=DAYS_OF_WEEK
    )
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    break_start = models.TimeField(_('Break Start Time'), null=True, blank=True)
    break_end = models.TimeField(_('Break End Time'), null=True, blank=True)

    class Meta:
        verbose_name = _('Work Schedule')
        verbose_name_plural = _('Work Schedules')
        unique_together = ['rule', 'day_of_week']

    def __str__(self):
        return f"{self.rule.name} - {self.get_day_of_week_display()}"


class WeeklyHoliday(models.Model):
    """Model for weekly holidays configuration"""
    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE,
        related_name='holidays',
        verbose_name=_('Attendance Rule')
    )
    day = models.IntegerField(
        _('Holiday Day'),
        choices=WorkSchedule.DAYS_OF_WEEK
    )

    class Meta:
        verbose_name = _('Weekly Holiday')
        verbose_name_plural = _('Weekly Holidays')
        unique_together = ['rule', 'day']

    def __str__(self):
        return f"{self.rule.name} - {self.get_day_display()}"


class LeaveType(models.Model):
    """Model for different types of leaves"""
    name = models.CharField(_('Leave Type'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_paid = models.BooleanField(_('Is Paid Leave'), default=True)
    max_days_per_year = models.PositiveIntegerField(
        _('Maximum Days Per Year'),
        validators=[MinValueValidator(0)]
    )
    requires_approval = models.BooleanField(_('Requires Approval'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')

    def __str__(self):
        return self.name


class EmployeeAttendanceProfile(models.Model):
    """Model for employee-specific attendance settings"""
    SALARY_STATUS = [
        ('active', _('Active')),
        ('suspended', _('Suspended')),
    ]
    ATTENDANCE_STATUS = [
        ('active', _('Active')),
        ('suspended', _('Suspended')),
    ]

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_profile',
        verbose_name=_('Employee')
    )
    attendance_rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.PROTECT,
        related_name='employee_profiles',
        verbose_name=_('Attendance Rule')
    )
    work_hours_per_day = models.DecimalField(
        _('Work Hours Per Day'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(24)]
    )
    salary_status = models.CharField(
        _('Salary Status'),
        max_length=20,
        choices=SALARY_STATUS,
        default='active'
    )
    attendance_status = models.CharField(
        _('Attendance Status'),
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='active'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Attendance Profile')
        verbose_name_plural = _('Employee Attendance Profiles')

    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_rule.name}"


class LeaveBalance(models.Model):
    """Model for tracking employee leave balances"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_leave_balances',
        verbose_name=_('Employee')
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='employee_balances',
        verbose_name=_('Leave Type')
    )
    year = models.PositiveIntegerField(_('Year'))
    allocated_days = models.DecimalField(
        _('Allocated Days'),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    used_days = models.DecimalField(
        _('Used Days'),
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Balance')
        verbose_name_plural = _('Leave Balances')
        unique_together = ['employee', 'leave_type', 'year']

    def __str__(self):
        return f"{self.employee.emp_full_name} - {self.leave_type.name} ({self.year})"

    @property
    def remaining_days(self):
        """Calculate remaining leave days"""
        return self.allocated_days - self.used_days


class AttendanceRecord(models.Model):
    """Model for daily attendance records"""
    RECORD_TYPE_CHOICES = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('leave', _('Leave')),
        ('holiday', _('Holiday')),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='new_attendance_records',
        verbose_name=_('Employee')
    )
    date = models.DateField(_('Date'))
    check_in = models.DateTimeField(_('Check In Time'), null=True, blank=True)
    check_out = models.DateTimeField(_('Check Out Time'), null=True, blank=True)
    record_type = models.CharField(
        _('Record Type'),
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='present'
    )
    late_minutes = models.IntegerField(_('Late Minutes'), default=0)
    early_leave_minutes = models.IntegerField(_('Early Leave Minutes'), default=0)
    overtime_minutes = models.IntegerField(_('Overtime Minutes'), default=0)
    break_minutes = models.IntegerField(_('Break Minutes'), default=0)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.emp_full_name} - {self.date}"

    def calculate_work_duration(self):
        """Calculate total work duration in minutes"""
        if self.check_in and self.check_out:
            total_minutes = (self.check_out - self.check_in).total_seconds() / 60
            return total_minutes - self.break_minutes
        return 0


# Schema-specific models to match provided SQL tables
class AttendanceRules(models.Model):
    """نموذج قواعد الحضور حسب مخطط قاعدة البيانات"""
    rule_id = models.AutoField(primary_key=True, db_column='RuleID')
    rule_name = models.CharField(max_length=100, db_column='RuleName', blank=True, null=True, verbose_name='اسم القاعدة')
    shift_start = models.TimeField(db_column='ShiftStart', blank=True, null=True, verbose_name='بداية الوردية')
    shift_end = models.TimeField(db_column='ShiftEnd', blank=True, null=True, verbose_name='نهاية الوردية')
    late_threshold = models.IntegerField(db_column='LateThreshold', blank=True, null=True, verbose_name='حد التأخير (دقائق)')
    early_threshold = models.IntegerField(db_column='EarlyThreshold', blank=True, null=True, verbose_name='حد المغادرة المبكرة (دقائق)')
    overtime_start_after = models.TimeField(db_column='OvertimeStartAfter', blank=True, null=True, verbose_name='بداية الوقت الإضافي')
    week_end_days = models.CharField(max_length=20, db_column='WeekEndDays', blank=True, null=True, verbose_name='أيام نهاية الأسبوع')
    is_default = models.BooleanField(db_column='IsDefault', default=False, verbose_name='افتراضية')

    class Meta:
        db_table = 'AttendanceRules'
        verbose_name = 'قاعدة حضور'
        verbose_name_plural = 'قواعد الحضور'

    def __str__(self):
        return self.rule_name or f'قاعدة {self.rule_id}'

    def clean(self):
        """التحقق من صحة البيانات"""
        from django.core.exceptions import ValidationError
        
        if self.shift_start and self.shift_end:
            if self.shift_start >= self.shift_end:
                raise ValidationError('وقت بداية الوردية يجب أن يكون قبل وقت النهاية')
        
        if self.late_threshold and self.late_threshold < 0:
            raise ValidationError('حد التأخير يجب أن يكون رقماً موجباً')
        
        if self.early_threshold and self.early_threshold < 0:
            raise ValidationError('حد المغادرة المبكرة يجب أن يكون رقماً موجباً')


class EmployeeAttendance(models.Model):
    """نموذج سجلات حضور الموظفين حسب مخطط قاعدة البيانات"""
    att_id = models.BigAutoField(primary_key=True, db_column='AttID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    att_date = models.DateField(db_column='AttDate', blank=True, null=True, verbose_name='التاريخ')
    check_in = models.DateTimeField(db_column='CheckIn', blank=True, null=True, verbose_name='وقت الدخول')
    check_out = models.DateTimeField(db_column='CheckOut', blank=True, null=True, verbose_name='وقت الخروج')
    # WorkMinutes computed via RunSQL migration
    status = models.CharField(max_length=20, db_column='Status', blank=True, null=True, verbose_name='الحالة')
    rule = models.ForeignKey(AttendanceRules, on_delete=models.SET_NULL, db_column='RuleID', blank=True, null=True, verbose_name='قاعدة الحضور')

    class Meta:
        db_table = 'EmployeeAttendance'
        verbose_name = 'سجل حضور'
        verbose_name_plural = 'سجلات الحضور'
        unique_together = ['emp', 'att_date']

    def __str__(self):
        return f'{self.emp} - {self.att_date}'

    def calculate_work_minutes(self):
        """حساب دقائق العمل"""
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            return int(duration.total_seconds() / 60)
        return 0

    def calculate_late_minutes(self):
        """حساب دقائق التأخير"""
        if not self.check_in or not self.rule or not self.rule.shift_start:
            return 0
        
        from datetime import datetime, time
        shift_start_datetime = datetime.combine(self.att_date, self.rule.shift_start)
        
        if self.check_in > shift_start_datetime:
            late_duration = self.check_in - shift_start_datetime
            return int(late_duration.total_seconds() / 60)
        return 0

    def calculate_early_leave_minutes(self):
        """حساب دقائق المغادرة المبكرة"""
        if not self.check_out or not self.rule or not self.rule.shift_end:
            return 0
        
        from datetime import datetime
        shift_end_datetime = datetime.combine(self.att_date, self.rule.shift_end)
        
        if self.check_out < shift_end_datetime:
            early_duration = shift_end_datetime - self.check_out
            return int(early_duration.total_seconds() / 60)
        return 0

    def calculate_overtime_minutes(self):
        """حساب دقائق الوقت الإضافي"""
        if not self.check_out or not self.rule or not self.rule.overtime_start_after:
            return 0
        
        from datetime import datetime
        overtime_start_datetime = datetime.combine(self.att_date, self.rule.overtime_start_after)
        
        if self.check_out > overtime_start_datetime:
            overtime_duration = self.check_out - overtime_start_datetime
            return int(overtime_duration.total_seconds() / 60)
        return 0

    def get_status_display_arabic(self):
        """عرض الحالة باللغة العربية"""
        status_map = {
            'Present': 'حاضر',
            'Absent': 'غائب',
            'Late': 'متأخر',
            'EarlyLeave': 'مغادرة مبكرة',
            'Holiday': 'عطلة',
            'Leave': 'إجازة'
        }
        return status_map.get(self.status, self.status or 'غير محدد')

    def clean(self):
        """التحقق من صحة البيانات"""
        from django.core.exceptions import ValidationError
        
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError('وقت الدخول يجب أن يكون قبل وقت الخروج')
        
        if self.att_date:
            from datetime import date
            if self.att_date > date.today():
                raise ValidationError('لا يمكن تسجيل حضور لتاريخ مستقبلي')


class ZKDevice(models.Model):
    """نموذج أجهزة ZK للحضور والانصراف"""
    DEVICE_STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('maintenance', 'صيانة'),
    ]
    
    device_id = models.AutoField(primary_key=True, verbose_name='معرف الجهاز')
    device_name = models.CharField(max_length=100, verbose_name='اسم الجهاز')
    device_serial = models.CharField(max_length=50, unique=True, verbose_name='الرقم التسلسلي')
    ip_address = models.GenericIPAddressField(verbose_name='عنوان IP')
    port = models.PositiveIntegerField(default=4370, verbose_name='المنفذ')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='الموقع')
    status = models.CharField(max_length=20, choices=DEVICE_STATUS_CHOICES, default='active', verbose_name='الحالة')
    timezone = models.CharField(max_length=50, default='Asia/Riyadh', verbose_name='المنطقة الزمنية')
    last_sync = models.DateTimeField(blank=True, null=True, verbose_name='آخر مزامنة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'جهاز ZK'
        verbose_name_plural = 'أجهزة ZK'
        
    def __str__(self):
        return f'{self.device_name} ({self.ip_address})'
    
    def is_online(self):
        """فحص حالة الاتصال بالجهاز"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.ip_address, self.port))
            sock.close()
            return result == 0
        except:
            return False


class ZKAttendanceRaw(models.Model):
    """نموذج البيانات الخام من أجهزة ZK"""
    PUNCH_TYPE_CHOICES = [
        ('0', 'Check In'),
        ('1', 'Check Out'),
        ('2', 'Break Out'),
        ('3', 'Break In'),
        ('4', 'Overtime In'),
        ('5', 'Overtime Out'),
    ]
    
    raw_id = models.BigAutoField(primary_key=True, verbose_name='معرف السجل')
    device = models.ForeignKey(ZKDevice, on_delete=models.CASCADE, verbose_name='الجهاز')
    user_id = models.CharField(max_length=20, verbose_name='معرف المستخدم في الجهاز')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, verbose_name='الموظف')
    timestamp = models.DateTimeField(verbose_name='الوقت والتاريخ')
    punch_type = models.CharField(max_length=2, choices=PUNCH_TYPE_CHOICES, default='0', verbose_name='نوع البصمة')
    verification_type = models.CharField(max_length=10, blank=True, null=True, verbose_name='نوع التحقق')
    work_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='كود العمل')
    is_processed = models.BooleanField(default=False, verbose_name='تم المعالجة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'بيانات ZK خام'
        verbose_name_plural = 'البيانات الخام من ZK'
        unique_together = ['device', 'user_id', 'timestamp', 'punch_type']
        ordering = ['-timestamp']
        
    def __str__(self):
        emp_name = self.employee.emp_code if self.employee else self.user_id
        return f'{emp_name} - {self.timestamp} ({self.get_punch_type_display()})'
    
    def get_punch_type_display_arabic(self):
        """عرض نوع البصمة باللغة العربية"""
        type_map = {
            '0': 'دخول',
            '1': 'خروج',
            '2': 'خروج للاستراحة',
            '3': 'عودة من الاستراحة',
            '4': 'دخول وقت إضافي',
            '5': 'خروج وقت إضافي',
        }
        return type_map.get(self.punch_type, 'غير محدد')


class AttendanceProcessingLog(models.Model):
    """نموذج سجل معالجة بيانات الحضور"""
    STATUS_CHOICES = [
        ('success', 'نجح'),
        ('failed', 'فشل'),
        ('partial', 'جزئي'),
    ]
    
    log_id = models.BigAutoField(primary_key=True, verbose_name='معرف السجل')
    device = models.ForeignKey(ZKDevice, on_delete=models.CASCADE, verbose_name='الجهاز')
    process_date = models.DateField(verbose_name='تاريخ المعالجة')
    records_fetched = models.PositiveIntegerField(default=0, verbose_name='السجلات المجلبة')
    records_processed = models.PositiveIntegerField(default=0, verbose_name='السجلات المعالجة')
    records_failed = models.PositiveIntegerField(default=0, verbose_name='السجلات الفاشلة')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='الحالة')
    error_message = models.TextField(blank=True, null=True, verbose_name='رسالة الخطأ')
    processing_time = models.DurationField(blank=True, null=True, verbose_name='وقت المعالجة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'سجل معالجة الحضور'
        verbose_name_plural = 'سجلات معالجة الحضور'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.device.device_name} - {self.process_date} ({self.get_status_display()})'
    
    @property
    def success_rate(self):
        """حساب نسبة النجاح"""
        if self.records_fetched > 0:
            return (self.records_processed / self.records_fetched) * 100
        return 0


class EmployeeDeviceMapping(models.Model):
    """نموذج ربط الموظفين بأجهزة ZK"""
    mapping_id = models.AutoField(primary_key=True, verbose_name='معرف الربط')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    device = models.ForeignKey(ZKDevice, on_delete=models.CASCADE, verbose_name='الجهاز')
    device_user_id = models.CharField(max_length=20, verbose_name='معرف المستخدم في الجهاز')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    last_used = models.DateTimeField(blank=True, null=True, verbose_name='آخر استخدام')
    
    class Meta:
        verbose_name = 'ربط موظف بجهاز'
        verbose_name_plural = 'ربط الموظفين بالأجهزة'
        unique_together = ['device', 'device_user_id']
        
    def __str__(self):
        return f'{self.employee.emp_code} - {self.device.device_name} ({self.device_user_id})'


class AttendanceSummary(models.Model):
    """نموذج ملخص الحضور الشهري"""
    summary_id = models.BigAutoField(primary_key=True, verbose_name='معرف الملخص')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    year = models.PositiveIntegerField(verbose_name='السنة')
    month = models.PositiveIntegerField(verbose_name='الشهر')
    total_work_days = models.PositiveIntegerField(default=0, verbose_name='إجمالي أيام العمل')
    present_days = models.PositiveIntegerField(default=0, verbose_name='أيام الحضور')
    absent_days = models.PositiveIntegerField(default=0, verbose_name='أيام الغياب')
    leave_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='أيام الإجازة')
    late_days = models.PositiveIntegerField(default=0, verbose_name='أيام التأخير')
    early_leave_days = models.PositiveIntegerField(default=0, verbose_name='أيام المغادرة المبكرة')
    total_work_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='إجمالي ساعات العمل')
    overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='ساعات إضافية')
    late_minutes = models.PositiveIntegerField(default=0, verbose_name='إجمالي دقائق التأخير')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'ملخص حضور'
        verbose_name_plural = 'ملخصات الحضور'
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month', 'employee__emp_code']
        
    def __str__(self):
        return f'{self.employee.emp_code} - {self.year}/{self.month:02d}'
    
    @property
    def attendance_rate(self):
        """حساب نسبة الحضور"""
        if self.total_work_days > 0:
            return (self.present_days / self.total_work_days) * 100
        return 0
    
    @property
    def punctuality_rate(self):
        """حساب نسبة الالتزام بالوقت"""
        if self.present_days > 0:
            return ((self.present_days - self.late_days) / self.present_days) * 100
        return 0
