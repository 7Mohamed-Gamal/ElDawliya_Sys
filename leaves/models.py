from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta
from employees.models import Employee


class LeaveType(models.Model):
    """نموذج أنواع الإجازات"""
    leave_type_id = models.AutoField(primary_key=True, db_column='LeaveTypeID')
    leave_name = models.CharField(max_length=100, db_column='LeaveName', verbose_name='اسم نوع الإجازة')
    max_days_per_year = models.IntegerField(db_column='MaxDaysPerYear', blank=True, null=True, verbose_name='الحد الأقصى للأيام سنوياً')
    is_paid = models.BooleanField(db_column='IsPaid', default=False, verbose_name='إجازة مدفوعة الأجر')
    requires_approval = models.BooleanField(default=True, verbose_name='تتطلب موافقة')
    can_carry_forward = models.BooleanField(default=False, verbose_name='يمكن ترحيلها للسنة التالية')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        db_table = 'LeaveTypes'
        verbose_name = 'نوع إجازة'
        verbose_name_plural = 'أنواع الإجازات'

    def __str__(self):
        return self.leave_name

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.max_days_per_year is not None and self.max_days_per_year < 0:
            raise ValidationError('الحد الأقصى للأيام يجب أن يكون رقماً موجباً')


class EmployeeLeave(models.Model):
    """نموذج إجازات الموظفين"""
    STATUS_CHOICES = [
        ('Pending', 'في الانتظار'),
        ('Approved', 'معتمدة'),
        ('Rejected', 'مرفوضة'),
        ('Cancelled', 'ملغاة'),
    ]

    leave_id = models.AutoField(primary_key=True, db_column='LeaveID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, db_column='LeaveTypeID', verbose_name='نوع الإجازة')
    start_date = models.DateField(db_column='StartDate', verbose_name='تاريخ البداية')
    end_date = models.DateField(db_column='EndDate', verbose_name='تاريخ النهاية')
    # Days computed column will be added via RunSQL migration
    reason = models.TextField(db_column='Reason', blank=True, null=True, verbose_name='السبب')
    status = models.CharField(max_length=30, db_column='Status', choices=STATUS_CHOICES, default='Pending', verbose_name='الحالة')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, db_column='ApprovedBy', blank=True, null=True, related_name='approved_leaves', verbose_name='معتمد من')
    approved_date = models.DateTimeField(db_column='ApprovedDate', blank=True, null=True, verbose_name='تاريخ الاعتماد')
    rejection_reason = models.TextField(blank=True, null=True, verbose_name='سبب الرفض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الطلب')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        db_table = 'EmployeeLeaves'
        verbose_name = 'إجازة'
        verbose_name_plural = 'إجازات الموظفين'
        unique_together = ['emp', 'start_date', 'end_date']

    def __str__(self):
        return f"{self.emp} - {self.leave_type.leave_name} ({self.start_date})"

    @property
    def duration_days(self):
        """حساب مدة الإجازة بالأيام"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def is_current(self):
        """التحقق من كون الإجازة حالية"""
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def is_future(self):
        """التحقق من كون الإجازة مستقبلية"""
        return self.start_date > date.today()

    @property
    def is_past(self):
        """التحقق من كون الإجازة منتهية"""
        return self.end_date < date.today()

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('تاريخ بداية الإجازة يجب أن يكون قبل تاريخ النهاية')
            
            # التحقق من عدم تداخل الإجازات
            overlapping_leaves = EmployeeLeave.objects.filter(
                emp=self.emp,
                status__in=['Pending', 'Approved'],
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            ).exclude(pk=self.pk)
            
            if overlapping_leaves.exists():
                raise ValidationError('يوجد تداخل مع إجازة أخرى معتمدة أو في الانتظار')
            
            # التحقق من الحد الأقصى للأيام
            if self.leave_type.max_days_per_year:
                year = self.start_date.year
                total_days_this_year = EmployeeLeave.objects.filter(
                    emp=self.emp,
                    leave_type=self.leave_type,
                    status='Approved',
                    start_date__year=year
                ).exclude(pk=self.pk).aggregate(
                    total=models.Sum(models.F('end_date') - models.F('start_date') + 1)
                )['total'] or 0
                
                if total_days_this_year + self.duration_days > self.leave_type.max_days_per_year:
                    raise ValidationError(f'تجاوز الحد الأقصى المسموح ({self.leave_type.max_days_per_year} يوم) لهذا النوع من الإجازات')

    def approve(self, approved_by):
        """اعتماد الإجازة"""
        self.status = 'Approved'
        self.approved_by = approved_by
        self.approved_date = timezone.now()
        self.save()

    def reject(self, rejected_by, reason=None):
        """رفض الإجازة"""
        self.status = 'Rejected'
        self.approved_by = rejected_by
        self.approved_date = timezone.now()
        if reason:
            self.rejection_reason = reason
        self.save()

    def cancel(self):
        """إلغاء الإجازة"""
        if self.status in ['Pending', 'Approved'] and self.is_future:
            self.status = 'Cancelled'
            self.save()
        else:
            raise ValidationError('لا يمكن إلغاء هذه الإجازة')


class PublicHoliday(models.Model):
    """نموذج العطلات الرسمية"""
    holiday_id = models.AutoField(primary_key=True, db_column='HolidayID')
    holiday_date = models.DateField(db_column='HolidayDate', verbose_name='تاريخ العطلة')
    description = models.CharField(max_length=255, db_column='Description', blank=True, null=True, verbose_name='الوصف')
    is_recurring = models.BooleanField(default=False, verbose_name='عطلة متكررة سنوياً')
    is_active = models.BooleanField(default=True, verbose_name='نشطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        db_table = 'PublicHolidays'
        verbose_name = 'عطلة رسمية'
        verbose_name_plural = 'العطلات الرسمية'
        unique_together = ['holiday_date']

    def __str__(self):
        return f"{self.description} - {self.holiday_date}"

    @classmethod
    def is_holiday(cls, check_date):
        """التحقق من كون التاريخ عطلة رسمية"""
        return cls.objects.filter(
            holiday_date=check_date,
            is_active=True
        ).exists()


class LeaveBalance(models.Model):
    """نموذج أرصدة الإجازات"""
    balance_id = models.AutoField(primary_key=True)
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='نوع الإجازة')
    year = models.IntegerField(verbose_name='السنة')
    allocated_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='الأيام المخصصة')
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='الأيام المستخدمة')
    carried_forward = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='الأيام المرحلة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'رصيد إجازة'
        verbose_name_plural = 'أرصدة الإجازات'
        unique_together = ['emp', 'leave_type', 'year']

    def __str__(self):
        return f"{self.emp} - {self.leave_type.leave_name} ({self.year})"

    @property
    def remaining_days(self):
        """حساب الأيام المتبقية"""
        return self.allocated_days + self.carried_forward - self.used_days

    @property
    def utilization_percentage(self):
        """حساب نسبة الاستخدام"""
        total_available = self.allocated_days + self.carried_forward
        if total_available > 0:
            return (self.used_days / total_available) * 100
        return 0

    def update_used_days(self):
        """تحديث الأيام المستخدمة من الإجازات المعتمدة"""
        used = EmployeeLeave.objects.filter(
            emp=self.emp,
            leave_type=self.leave_type,
            status='Approved',
            start_date__year=self.year
        ).aggregate(
            total=models.Sum(models.F('end_date') - models.F('start_date') + 1)
        )['total'] or 0
        
        self.used_days = used
        self.save()

# Create your models here.
