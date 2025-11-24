from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from employees.models import Employee


class LeaveType(models.Model):
    """نموذج أنواع الإجازات"""
    LEAVE_CALCULATION_METHODS = [
        ('days', 'بالأيام'),
        ('hours', 'بالساعات'),
        ('half_days', 'بأنصاف الأيام'),
    ]

    ACCRUAL_FREQUENCY = [
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
        ('on_hire', 'عند التعيين'),
    ]

    leave_type_id = models.AutoField(primary_key=True, db_column='LeaveTypeID')
    leave_name = models.CharField(max_length=100, db_column='LeaveName', verbose_name='اسم نوع الإجازة')
    leave_code = models.CharField(max_length=10, unique=True, verbose_name='رمز الإجازة')
    max_days_per_year = models.IntegerField(db_column='MaxDaysPerYear', blank=True, null=True, verbose_name='الحد الأقصى للأيام سنوياً')
    is_paid = models.BooleanField(db_column='IsPaid', default=True, verbose_name='إجازة مدفوعة الأجر')
    requires_approval = models.BooleanField(default=True, verbose_name='تتطلب موافقة')
    can_carry_forward = models.BooleanField(default=False, verbose_name='يمكن ترحيلها للسنة التالية')
    max_carry_forward_days = models.IntegerField(default=0, verbose_name='الحد الأقصى للترحيل')
    calculation_method = models.CharField(max_length=20, choices=LEAVE_CALCULATION_METHODS, default='days', verbose_name='طريقة الحساب')
    accrual_frequency = models.CharField(max_length=20, choices=ACCRUAL_FREQUENCY, default='yearly', verbose_name='تكرار الاستحقاق')
    accrual_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'), verbose_name='معدل الاستحقاق')
    minimum_service_months = models.IntegerField(default=0, verbose_name='الحد الأدنى للخدمة (بالشهور)')
    gender_specific = models.CharField(max_length=10, choices=[('all', 'جميع الموظفين'), ('male', 'ذكور فقط'), ('female', 'إناث فقط')], default='all', verbose_name='خاص بالجنس')
    affects_attendance = models.BooleanField(default=True, verbose_name='تؤثر على الحضور')
    excludes_holidays = models.BooleanField(default=True, verbose_name='استثناء العطل الرسمية')
    requires_medical_certificate = models.BooleanField(default=False, verbose_name='تتطلب شهادة طبية')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    color_code = models.CharField(max_length=7, default='#007bff', verbose_name='لون العرض')
    sort_order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'LeaveTypes'
        verbose_name = 'نوع إجازة'
        verbose_name_plural = 'أنواع الإجازات'
        ordering = ['sort_order', 'leave_name']

    def __str__(self):
        """__str__ function"""
        return self.leave_name

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.max_days_per_year is not None and self.max_days_per_year < 0:
            raise ValidationError('الحد الأقصى للأيام يجب أن يكون رقماً موجباً')

        if self.can_carry_forward and self.max_carry_forward_days < 0:
            raise ValidationError('الحد الأقصى للترحيل يجب أن يكون رقماً موجباً')

        if self.minimum_service_months < 0:
            raise ValidationError('الحد الأدنى للخدمة يجب أن يكون رقماً موجباً')

    def calculate_accrual_amount(self, months_of_service):
        """حساب مقدار الاستحقاق"""
        if months_of_service < self.minimum_service_months:
            return 0

        if self.accrual_frequency == 'monthly':
            return float(self.accrual_rate)
        elif self.accrual_frequency == 'quarterly':
            return float(self.accrual_rate) if months_of_service % 3 == 0 else 0
        elif self.accrual_frequency == 'yearly':
            return float(self.accrual_rate) if months_of_service % 12 == 0 else 0
        else:  # on_hire
            return float(self.accrual_rate) if months_of_service == 0 else 0


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
        """Meta class"""
        db_table = 'EmployeeLeaves'
        verbose_name = 'إجازة'
        verbose_name_plural = 'إجازات الموظفين'
        unique_together = ['emp', 'start_date', 'end_date']

    def __str__(self):
        """__str__ function"""
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
        # التحقق من وجود الحقول المطلوبة قبل المتابعة
        if not hasattr(self, 'emp') or not hasattr(self, 'leave_type') or not self.emp_id or not self.leave_type_id:
            return

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
                # Calculate total days using Python instead of database aggregation for SQL Server compatibility
                approved_leaves = EmployeeLeave.objects.filter(
                    emp=self.emp,
                    leave_type=self.leave_type,
                    status='Approved',
                    start_date__year=year
                ).exclude(pk=self.pk)

                total_days_this_year = sum(
                    (leave.end_date - leave.start_date).days + 1
                    for leave in approved_leaves
                )

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
        """Meta class"""
        db_table = 'PublicHolidays'
        verbose_name = 'عطلة رسمية'
        verbose_name_plural = 'العطلات الرسمية'
        unique_together = ['holiday_date']

    def __str__(self):
        """__str__ function"""
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
        """Meta class"""
        verbose_name = 'رصيد إجازة'
        verbose_name_plural = 'أرصدة الإجازات'
        unique_together = ['emp', 'leave_type', 'year']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp} - {self.leave_type.leave_name} ({self.year})"

    @property
    def remaining_days(self):
        """حساب الأيام المتبقية"""
        return max(Decimal('0'), self.allocated_days + self.carried_forward - self.used_days)

    def can_take_leave(self, days_requested):
        """التحقق من إمكانية أخذ الإجازة المطلوبة"""
        return self.remaining_days >= Decimal(str(days_requested))

    def use_leave_days(self, days_used):
        """استخدام أيام الإجازة وتحديث الرصيد"""
        if self.can_take_leave(days_used):
            self.used_days += Decimal(str(days_used))
            self.save()
            return True
        return False

    def restore_leave_days(self, days_to_restore):
        """استرداد أيام الإجازة (عند إلغاء الإجازة)"""
        self.used_days = max(Decimal('0'), self.used_days - Decimal(str(days_to_restore)))
        self.save()

    def calculate_carry_forward_eligible(self, max_carry_forward_percentage=30):
        """حساب الأيام المؤهلة للترحيل للسنة القادمة"""
        max_carry_forward = (self.allocated_days * Decimal(str(max_carry_forward_percentage))) / Decimal('100')
        return min(self.remaining_days, max_carry_forward)

    @property
    def utilization_percentage(self):
        """حساب نسبة الاستخدام"""
        total_available = self.allocated_days + self.carried_forward
        if total_available > 0:
            return (self.used_days / total_available) * 100
        return 0

    def update_used_days(self):
        """تحديث الأيام المستخدمة من الإجازات المعتمدة"""
        # Calculate used days using Python instead of database aggregation for SQL Server compatibility
        approved_leaves = EmployeeLeave.objects.filter(
            emp=self.emp,
            leave_type=self.leave_type,
            status='Approved',
            start_date__year=self.year
        )

        used = sum(
            (leave.end_date - leave.start_date).days + 1
            for leave in approved_leaves
        )

        self.used_days = used
        self.save()


class LeavePolicy(models.Model):
    """نموذج سياسات الإجازات"""
    policy_id = models.AutoField(primary_key=True)
    policy_name = models.CharField(max_length=100, verbose_name='اسم السياسة')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='نوع الإجازة')
    department = models.ForeignKey('org.Department', on_delete=models.CASCADE, blank=True, null=True, verbose_name='القسم')
    job_position = models.ForeignKey('org.Job', on_delete=models.CASCADE, blank=True, null=True, verbose_name='المنصب')
    min_service_years = models.IntegerField(default=0, verbose_name='الحد الأدنى لسنوات الخدمة')
    max_consecutive_days = models.IntegerField(blank=True, null=True, verbose_name='الحد الأقصى للأيام المتتالية')
    advance_notice_days = models.IntegerField(default=0, verbose_name='عدد أيام الإشعار المسبق')
    blackout_start_date = models.DateField(blank=True, null=True, verbose_name='بداية فترة الحظر')
    blackout_end_date = models.DateField(blank=True, null=True, verbose_name='نهاية فترة الحظر')
    requires_replacement = models.BooleanField(default=False, verbose_name='تتطلب بديل')
    max_pending_requests = models.IntegerField(default=1, verbose_name='الحد الأقصى للطلبات المعلقة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class"""
        verbose_name = 'سياسة إجازة'
        verbose_name_plural = 'سياسات الإجازات'

    def __str__(self):
        """__str__ function"""
        return self.policy_name

    def is_applicable_to_employee(self, employee):
        """فحص إذا كانت السياسة قابلة للتطبيق على الموظف"""
        # فحص القسم
        if self.department and employee.dept != self.department:
            return False

        # فحص المنصب
        if self.job_position and employee.job != self.job_position:
            return False

        # فحص سنوات الخدمة
        if employee.hire_date:
            service_years = (date.today() - employee.hire_date).days / 365.25
            if service_years < self.min_service_years:
                return False

        return True


class LeaveRequest(models.Model):
    """نموذج طلبات الإجازات (محسن)"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('submitted', 'مقدم'),
        ('under_review', 'قيد المراجعة'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
        ('cancelled', 'ملغى'),
        ('expired', 'منتهي الصلاحية'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('high', 'عالي'),
        ('urgent', 'عاجل'),
    ]

    request_id = models.AutoField(primary_key=True)
    request_number = models.CharField(max_length=20, unique=True, verbose_name='رقم الطلب')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', verbose_name='الموظف')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, verbose_name='نوع الإجازة')
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    duration_days = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='عدد الأيام')
    reason = models.TextField(verbose_name='سبب الإجازة')
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name='جهة الاتصال في حالة الطوارئ')
    replacement_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='replacement_for', verbose_name='الموظف البديل')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='الحالة')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='الأولوية')
    attachment = models.FileField(upload_to='leave_attachments/', blank=True, null=True, verbose_name='مرفق')
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ التقديم')
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_requests', verbose_name='مراجع من')
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ المراجعة')
    review_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات المراجعة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class"""
        verbose_name = 'طلب إجازة'
        verbose_name_plural = 'طلبات الإجازات'
        ordering = ['-created_at']

    def __str__(self):
        """__str__ function"""
        return f'{self.request_number} - {self.employee}'

    def save(self, *args, **kwargs):
        """save function"""
        if not self.request_number:
            # إنشاء رقم طلب تلقائي
            year = date.today().year
            count = LeaveRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f'LR{year}{count:04d}'

        if not self.duration_days:
            self.duration_days = (self.end_date - self.start_date).days + 1

        super().save(*args, **kwargs)

    def submit(self):
        """تقديم الطلب"""
        if self.status == 'draft':
            self.status = 'submitted'
            self.submitted_at = timezone.now()
            self.save()

    def approve(self, reviewer, notes=None):
        """اعتماد الطلب"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if notes:
            self.review_notes = notes
        self.save()

        # إنشاء سجل إجازة في جدول EmployeeLeave
        EmployeeLeave.objects.create(
            emp=self.employee,
            leave_type=self.leave_type,
            start_date=self.start_date,
            end_date=self.end_date,
            reason=self.reason,
            status='Approved',
            approved_by=reviewer,
            approved_date=timezone.now()
        )

    def reject(self, reviewer, reason):
        """رفض الطلب"""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = reason
        self.save()


class LeaveWorkflow(models.Model):
    """نموذج سير عمل اعتماد الإجازات"""
    workflow_id = models.AutoField(primary_key=True)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='نوع الإجازة')
    step_order = models.IntegerField(verbose_name='ترتيب الخطوة')
    approver_role = models.CharField(max_length=50, verbose_name='دور المعتمد')
    approver_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, verbose_name='الموظف المعتمد')
    is_required = models.BooleanField(default=True, verbose_name='إجباري')
    conditions = models.TextField(blank=True, null=True, verbose_name='الشروط')

    class Meta:
        """Meta class"""
        verbose_name = 'سير عمل الإجازة'
        verbose_name_plural = 'سير عمل الإجازات'
        ordering = ['leave_type', 'step_order']

    def __str__(self):
        """__str__ function"""
        return f'{self.leave_type.leave_name} - خطوة {self.step_order}'


class LeaveApprovalStep(models.Model):
    """نموذج خطوات اعتماد الإجازات"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
        ('skipped', 'متجاوز'),
    ]

    step_id = models.AutoField(primary_key=True)
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='approval_steps', verbose_name='طلب الإجازة')
    workflow_step = models.ForeignKey(LeaveWorkflow, on_delete=models.CASCADE, verbose_name='خطوة سير العمل')
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, verbose_name='المعتمد')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    comments = models.TextField(blank=True, null=True, verbose_name='تعليقات')
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ المعالجة')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""
        verbose_name = 'خطوة اعتماد'
        verbose_name_plural = 'خطوات الاعتماد'
        ordering = ['workflow_step__step_order']

    def __str__(self):
        """__str__ function"""
        return f'{self.leave_request.request_number} - خطوة {self.workflow_step.step_order}'


class LeaveQuota(models.Model):
    """نموذج حصص الإجازات"""
    quota_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='نوع الإجازة')
    year = models.IntegerField(verbose_name='السنة')
    total_quota = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='إجمالي الحصة')
    used_quota = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='الحصة المستخدمة')
    carried_forward = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='المرحل من العام السابق')
    expires_at = models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class"""
        verbose_name = 'حصة إجازة'
        verbose_name_plural = 'حصص الإجازات'
        unique_together = ['employee', 'leave_type', 'year']

    def __str__(self):
        """__str__ function"""
        return f'{self.employee} - {self.leave_type.leave_name} ({self.year})'

    @property
    def available_quota(self):
        """الحصة المتاحة"""
        return self.total_quota + self.carried_forward - self.used_quota

    @property
    def utilization_rate(self):
        """معدل الاستخدام"""
        total = self.total_quota + self.carried_forward
        if total > 0:
            return (self.used_quota / total) * 100
        return 0


class LeaveCalendar(models.Model):
    """نموذج تقويم الإجازات"""
    calendar_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    date = models.DateField(verbose_name='التاريخ')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, blank=True, null=True, verbose_name='نوع الإجازة')
    is_holiday = models.BooleanField(default=False, verbose_name='عطلة رسمية')
    is_weekend = models.BooleanField(default=False, verbose_name='عطلة نهاية أسبوع')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""
        verbose_name = 'تقويم إجازة'
        verbose_name_plural = 'تقويم الإجازات'
        unique_together = ['employee', 'date']
        ordering = ['date']

    def __str__(self):
        """__str__ function"""
        return f'{self.employee} - {self.date}'


# Create your models here.
