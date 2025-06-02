from django.db import models
from django.utils.translation import gettext_lazy as _
import json
from .employee_model import Employee
from django.core.validators import MinValueValidator, MaxValueValidator

class AttendanceRule(models.Model):
    """
    Model for defining attendance rules
    """
    WEEKDAY_CHOICES = [
        (0, _('الاثنين')),
        (1, _('الثلاثاء')),
        (2, _('الأربعاء')),
        (3, _('الخميس')),
        (4, _('الجمعة')),
        (5, _('السبت')),
        (6, _('الأحد')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('اسم القاعدة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
    work_schedule = models.JSONField(verbose_name=_('جدول العمل'))  # Store work schedule as JSON
    late_grace_minutes = models.PositiveIntegerField(default=0, verbose_name=_('فترة سماح التأخير (دقائق)'))
    early_leave_grace_minutes = models.PositiveIntegerField(default=0, verbose_name=_('فترة سماح الانصراف المبكر (دقائق)'))
    weekly_off_days = models.JSONField(default=list, verbose_name=_('أيام الإجازة الأسبوعية'))  # Store as JSON array of weekday numbers
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return self.name
    
    def get_work_schedule(self):
        """
        Returns the work schedule as a Python object
        """
        if isinstance(self.work_schedule, str):
            return json.loads(self.work_schedule)
        return self.work_schedule
    
    def get_weekly_off_days(self):
        """
        Returns the weekly off days as a Python list
        """
        if isinstance(self.weekly_off_days, str):
            return json.loads(self.weekly_off_days)
        return self.weekly_off_days
    
    class Meta:
        verbose_name = _('قاعدة الحضور')
        verbose_name_plural = _('قواعد الحضور')
        db_table = 'Hr_AttendanceRule'
        managed = True


class EmployeeAttendanceRule(models.Model):
    """
    Model to link employees to attendance rules
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_rules', verbose_name=_('الموظف'))
    attendance_rule = models.ForeignKey(AttendanceRule, on_delete=models.CASCADE, related_name='employees', verbose_name=_('قاعدة الحضور'))
    effective_date = models.DateField(verbose_name=_('تاريخ السريان'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return f"{self.employee} - {self.attendance_rule}"
    
    class Meta:
        verbose_name = _('قاعدة حضور الموظف')
        verbose_name_plural = _('قواعد حضور الموظفين')
        db_table = 'Hr_EmployeeAttendanceRule'
        managed = True


class OfficialHoliday(models.Model):
    """
    Model for defining official holidays
    """
    name = models.CharField(max_length=100, verbose_name=_('اسم الإجازة'))
    date = models.DateField(verbose_name=_('تاريخ الإجازة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
    is_recurring = models.BooleanField(default=False, verbose_name=_('إجازة متكررة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    class Meta:
        verbose_name = _('إجازة رسمية')
        verbose_name_plural = _('إجازات رسمية')
        db_table = 'Hr_OfficialHoliday'
        unique_together = ('name', 'date')
        managed = True


class AttendanceMachine(models.Model):
    """
    Model for storing attendance machine details
    """
    MACHINE_TYPE_CHOICES = [
        ('in', _('حضور')),
        ('out', _('انصراف')),
        ('both', _('حضور وانصراف')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('اسم الماكينة'))
    ip_address = models.CharField(max_length=15, verbose_name=_('عنوان IP'))
    port = models.PositiveIntegerField(default=4370, verbose_name=_('المنفذ'))
    machine_type = models.CharField(max_length=10, choices=MACHINE_TYPE_CHOICES, verbose_name=_('نوع الماكينة'))
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الموقع'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('ماكينة الحضور')
        verbose_name_plural = _('ماكينات الحضور')
        db_table = 'Hr_AttendanceMachine'
        managed = True


class AttendanceRecord(models.Model):
    """
    Model for storing attendance records
    """
    RECORD_TYPE_CHOICES = [
        ('in', _('حضور')),
        ('out', _('انصراف')),
    ]
    
    SOURCE_CHOICES = [
        ('machine', _('ماكينة')),
        ('manual', _('يدوي')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records', verbose_name=_('الموظف'))
    record_date = models.DateField(verbose_name=_('تاريخ التسجيل'))
    record_time = models.TimeField(verbose_name=_('وقت التسجيل'))
    record_type = models.CharField(max_length=5, choices=RECORD_TYPE_CHOICES, verbose_name=_('نوع التسجيل'))
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='machine', verbose_name=_('المصدر'))
    machine = models.ForeignKey(AttendanceMachine, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('الماكينة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return f"{self.employee} - {self.record_date} {self.record_time} - {self.get_record_type_display()}"
    
    class Meta:
        verbose_name = _('سجل الحضور')
        verbose_name_plural = _('سجلات الحضور')
        db_table = 'Hr_AttendanceRecord'
        ordering = ['record_date', 'record_time']
        managed = True


class AttendanceSummary(models.Model):
    """
    Model for storing daily attendance summaries
    """
    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('early_leave', _('انصراف مبكر')),
        ('holiday', _('إجازة')),
        ('weekend', _('عطلة أسبوعية')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_summaries', verbose_name=_('الموظف'))
    date = models.DateField(verbose_name=_('التاريخ'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name=_('الحالة'))
    time_in = models.TimeField(null=True, blank=True, verbose_name=_('وقت الحضور'))
    time_out = models.TimeField(null=True, blank=True, verbose_name=_('وقت الانصراف'))
    late_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق التأخير'))
    early_leave_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق الانصراف المبكر'))
    overtime_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق العمل الإضافي'))
    working_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق العمل'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = _('ملخص الحضور')
        verbose_name_plural = _('ملخصات الحضور')
        db_table = 'Hr_AttendanceSummary'
        unique_together = ('employee', 'date')
        ordering = ['date']
        managed = True
