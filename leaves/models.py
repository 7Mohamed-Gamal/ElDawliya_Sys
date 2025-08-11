from django.db import models
from employees.models import Employee


class LeaveType(models.Model):
    leave_type_id = models.AutoField(primary_key=True, db_column='LeaveTypeID')
    leave_name = models.CharField(max_length=100, db_column='LeaveName')
    max_days_per_year = models.IntegerField(db_column='MaxDaysPerYear', blank=True, null=True)
    is_paid = models.BooleanField(db_column='IsPaid', default=False)

    class Meta:
        db_table = 'LeaveTypes'
        verbose_name = 'نوع إجازة'
        verbose_name_plural = 'أنواع الإجازات'

    def __str__(self):
        return self.leave_name


class EmployeeLeave(models.Model):
    leave_id = models.AutoField(primary_key=True, db_column='LeaveID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, db_column='LeaveTypeID')
    start_date = models.DateField(db_column='StartDate')
    end_date = models.DateField(db_column='EndDate')
    # Days computed column will be added via RunSQL migration
    reason = models.CharField(max_length=500, db_column='Reason', blank=True, null=True)
    status = models.CharField(max_length=30, db_column='Status', default='Pending')
    approved_by = models.IntegerField(db_column='ApprovedBy', blank=True, null=True)
    approved_date = models.DateTimeField(db_column='ApprovedDate', blank=True, null=True)

    class Meta:
        db_table = 'EmployeeLeaves'
        verbose_name = 'إجازة'
        verbose_name_plural = 'إجازات الموظفين'

    def __str__(self):
        return f"{self.emp_id} - {self.start_date}"


class PublicHoliday(models.Model):
    holiday_id = models.AutoField(primary_key=True, db_column='HolidayID')
    holiday_date = models.DateField(db_column='HolidayDate')
    description = models.CharField(max_length=255, db_column='Description', blank=True, null=True)

    class Meta:
        db_table = 'PublicHolidays'
        verbose_name = 'عطلة رسمية'
        verbose_name_plural = 'العطلات الرسمية'

# Create your models here.
