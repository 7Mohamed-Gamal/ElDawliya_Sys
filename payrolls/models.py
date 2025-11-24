from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from employees.models import Employee
from leaves.models import EmployeeLeave, LeaveType
from attendance.models import EmployeeAttendance, AttendanceSummary
from loans.models import EmployeeLoan, LoanInstallment


class EmployeeSalary(models.Model):
    """نموذج رواتب الموظفين المحسن"""
    SALARY_TYPES = [
        ('monthly', 'شهري'),
        ('hourly', 'بالساعة'),
        ('daily', 'يومي'),
        ('project', 'مشروع'),
    ]

    salary_id = models.AutoField(primary_key=True, db_column='SalaryID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPES, default='monthly', verbose_name='نوع الراتب')
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='BasicSalary', verbose_name='الراتب الأساسي')
    housing_allow = models.DecimalField(max_digits=18, decimal_places=2, db_column='HousingAllow', default=0, verbose_name='بدل السكن')
    transport_allow = models.DecimalField(max_digits=18, decimal_places=2, db_column='Transport', default=0, verbose_name='بدل المواصلات')
    food_allow = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='بدل الطعام')
    mobile_allow = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='بدل الهاتف')
    other_allow = models.DecimalField(max_digits=18, decimal_places=2, db_column='OtherAllow', default=0, verbose_name='بدلات أخرى')

    # Deductions
    gosi_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='GosiDeduction', default=0, verbose_name='خصم التأمينات')
    tax_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='TaxDeduction', default=0, verbose_name='خصم الضرائب')
    insurance_deduction = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='خصم التأمين الطبي')
    other_deduction = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='خصومات أخرى')

    # Overtime settings
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.5'), verbose_name='معدل الوقت الإضافي')
    weekend_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.0'), verbose_name='معدل عمل نهاية الأسبوع')
    holiday_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.5'), verbose_name='معدل عمل العطل')

    # Leave deduction settings
    deduct_unpaid_leave = models.BooleanField(default=True, verbose_name='خصم الإجازات غير مدفوعة الأجر')
    deduct_late_minutes = models.BooleanField(default=True, verbose_name='خصم دقائق التأخير')
    deduct_absent_days = models.BooleanField(default=True, verbose_name='خصم أيام الغياب')

    currency = models.CharField(max_length=3, db_column='Currency', default='SAR', verbose_name='العملة')
    effective_date = models.DateField(db_column='EffectiveDate', verbose_name='تاريخ السريان')
    end_date = models.DateField(db_column='EndDate', blank=True, null=True, verbose_name='تاريخ الانتهاء')
    is_current = models.BooleanField(db_column='IsCurrent', default=True, verbose_name='ساري حالياً')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_salaries', verbose_name='أنشئ بواسطة')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeSalaries'
        verbose_name = 'راتب موظف'
        verbose_name_plural = 'رواتب الموظفين'
        ordering = ['-effective_date']

    def __str__(self):
        """__str__ function"""
        return f"{self.emp} - {self.basic_salary} {self.currency}"

    @property
    def total_allowances(self):
        """إجمالي البدلات"""
        return (
            self.housing_allow + self.transport_allow +
            self.food_allow + self.mobile_allow + self.other_allow
        )

    @property
    def total_deductions(self):
        """إجمالي الخصومات"""
        return (
            self.gosi_deduction + self.tax_deduction +
            self.insurance_deduction + self.other_deduction
        )

    @property
    def gross_salary(self):
        """إجمالي الراتب قبل الخصومات"""
        return self.basic_salary + self.total_allowances

    @property
    def net_salary(self):
        """صافي الراتب"""
        return self.gross_salary - self.total_deductions

    def calculate_hourly_rate(self):
        """حساب الأجر بالساعة"""
        if self.salary_type == 'hourly':
            return self.basic_salary
        elif self.salary_type == 'monthly':
            # افتراض 8 ساعات يومياً × 22 يوم عمل شهرياً
            return self.basic_salary / Decimal('176')  # 8 * 22
        elif self.salary_type == 'daily':
            return self.basic_salary / Decimal('8')
        return Decimal('0')

    def calculate_overtime_rate(self):
        """حساب معدل الوقت الإضافي"""
        return self.calculate_hourly_rate() * self.overtime_rate

    def calculate_weekend_rate(self):
        """حساب معدل عمل نهاية الأسبوع"""
        return self.calculate_hourly_rate() * self.weekend_rate

    def calculate_holiday_rate(self):
        """حساب معدل عمل العطل"""
        return self.calculate_hourly_rate() * self.holiday_rate

    def calculate_monthly_deductions(self, attendance_data=None):
        """حساب الخصومات الشهرية بناءً على الحضور"""
        total_deductions = self.total_deductions

        if attendance_data and self.deduct_absent_days:
            daily_rate = self.calculate_daily_rate()
            absent_days = attendance_data.get('absent_days', 0)
            total_deductions += daily_rate * Decimal(str(absent_days))

        if attendance_data and self.deduct_late_minutes:
            hourly_rate = self.calculate_hourly_rate()
            late_minutes = attendance_data.get('late_minutes', 0)
            late_deduction = (hourly_rate / Decimal('60')) * Decimal(str(late_minutes))
            total_deductions += late_deduction

        return total_deductions

    def calculate_monthly_earnings(self, overtime_hours=0, weekend_hours=0, holiday_hours=0):
        """حساب الأرباح الشهرية مع الوقت الإضافي"""
        base_earnings = self.gross_salary

        # إضافة الوقت الإضافي
        if overtime_hours > 0:
            overtime_amount = self.calculate_overtime_rate() * Decimal(str(overtime_hours))
            base_earnings += overtime_amount

        # إضافة عمل نهاية الأسبوع
        if weekend_hours > 0:
            weekend_amount = self.calculate_weekend_rate() * Decimal(str(weekend_hours))
            base_earnings += weekend_amount

        # إضافة عمل العطل
        if holiday_hours > 0:
            holiday_amount = self.calculate_holiday_rate() * Decimal(str(holiday_hours))
            base_earnings += holiday_amount

        return base_earnings

    def calculate_daily_rate(self):
        """حساب الأجر اليومي"""
        if self.salary_type == 'daily':
            return self.basic_salary
        elif self.salary_type == 'monthly':
            return self.basic_salary / 22  # 22 يوم عمل في الشهر
        elif self.salary_type == 'hourly':
            return self.basic_salary * 8
        return 0

    def clean(self):
        """التحقق من صحة البيانات"""
        if self.basic_salary < 0:
            raise ValidationError('الراتب الأساسي لا يمكن أن يكون سالباً')

        if self.end_date and self.effective_date:
            if self.end_date <= self.effective_date:
                raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان')

        # التأكد من وجود راتب واحد فقط ساري لكل موظف
        if self.is_current:
            existing_current = EmployeeSalary.objects.filter(
                emp=self.emp,
                is_current=True
            ).exclude(pk=self.pk)

            if existing_current.exists():
                raise ValidationError('يوجد راتب ساري بالفعل لهذا الموظف')


class PayrollRun(models.Model):
    """نموذج تشغيل الرواتب المحسن"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('calculating', 'جاري الحساب'),
        ('review', 'قيد المراجعة'),
        ('approved', 'معتمد'),
        ('paid', 'مدفوع'),
        ('cancelled', 'ملغى'),
    ]

    PAYROLL_TYPES = [
        ('monthly', 'شهري'),
        ('bi_weekly', 'نصف شهري'),
        ('weekly', 'أسبوعي'),
        ('bonus', 'مكافآت'),
        ('final_settlement', 'تصفية نهائية'),
    ]

    run_id = models.AutoField(primary_key=True, db_column='RunID')
    run_number = models.CharField(max_length=20, unique=True, verbose_name='رقم التشغيل')
    payroll_type = models.CharField(max_length=20, choices=PAYROLL_TYPES, default='monthly', verbose_name='نوع الراتب')
    run_date = models.DateField(db_column='RunDate', default=date.today, verbose_name='تاريخ التشغيل')
    period_start = models.DateField(verbose_name='بداية الفترة')
    period_end = models.DateField(verbose_name='نهاية الفترة')
    month_year = models.CharField(max_length=7, db_column='MonthYear', verbose_name='الشهر والسنة')
    status = models.CharField(max_length=30, db_column='Status', choices=STATUS_CHOICES, default='draft', verbose_name='الحالة')

    # Processing details
    total_employees = models.IntegerField(default=0, verbose_name='إجمالي الموظفين')
    processed_employees = models.IntegerField(default=0, verbose_name='الموظفين المعالجين')
    total_gross_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='إجمالي المبلغ الإجمالي')
    total_deductions = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='إجمالي الخصومات')
    total_net_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='إجمالي المبلغ الصافي')

    # Approval workflow
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_payrolls', verbose_name='أنشئ بواسطة')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='approved_payrolls', verbose_name='معتمد بواسطة')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاعتماد')
    confirmed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, db_column='ConfirmedBy', blank=True, null=True, related_name='confirmed_payrolls', verbose_name='مؤكد بواسطة')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ التأكيد')

    # Processing metadata
    processing_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات المعالجة')
    calculation_method = models.CharField(max_length=50, default='attendance_based', verbose_name='طريقة الحساب')
    include_overtime = models.BooleanField(default=True, verbose_name='تضمين الوقت الإضافي')
    include_bonuses = models.BooleanField(default=True, verbose_name='تضمين المكافآت')
    include_deductions = models.BooleanField(default=True, verbose_name='تضمين الخصومات')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'PayrollRuns'
        verbose_name = 'تشغيل راتب'
        verbose_name_plural = 'تشغيلات الرواتب'
        ordering = ['-run_date', '-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.run_number} - {self.month_year}"

    def save(self, *args, **kwargs):
        """save function"""
        if not self.run_number:
            # Generate unique run number
            year = self.run_date.year
            month = self.run_date.month
            count = PayrollRun.objects.filter(
                run_date__year=year,
                run_date__month=month
            ).count() + 1
            self.run_number = f'PR{year}{month:02d}{count:03d}'

        if not self.month_year:
            self.month_year = f"{self.run_date.year}-{self.run_date.month:02d}"

        super().save(*args, **kwargs)

    @property
    def is_editable(self):
        """فحص إذا كان بالإمكان تعديل التشغيل"""
        return self.status in ['draft', 'calculating', 'review']

    @property
    def processing_progress(self):
        """نسبة إنجاز المعالجة"""
        if self.total_employees > 0:
            return (self.processed_employees / self.total_employees) * 100
        return 0

    def calculate_totals(self):
        """حساب المجاميع من تفاصيل الرواتب"""
        details = self.payroll_details.all()

        self.total_employees = details.count()
        self.processed_employees = details.filter(is_processed=True).count()

        totals = details.aggregate(
            gross=models.Sum('gross_salary'),
            deductions=models.Sum('total_deductions'),
            net=models.Sum('net_salary')
        )

        self.total_gross_amount = totals['gross'] or 0
        self.total_deductions = totals['deductions'] or 0
        self.total_net_amount = totals['net'] or 0

        self.save()

    def start_calculation(self):
        """بدء عملية حساب الرواتب"""
        if self.status == 'draft':
            self.status = 'calculating'
            self.save()

    def complete_calculation(self):
        """إنهاء عملية حساب الرواتب"""
        if self.status == 'calculating':
            self.status = 'review'
            self.calculate_totals()
            self.save()

    def approve(self, approved_by):
        """اعتماد الرواتب"""
        if self.status == 'review':
            self.status = 'approved'
            self.approved_by = approved_by
            self.approved_at = timezone.now()
            self.save()

    def mark_as_paid(self, confirmed_by):
        """تحديد كمدفوع"""
        if self.status == 'approved':
            self.status = 'paid'
            self.confirmed_by = confirmed_by
            self.confirmed_at = timezone.now()
            self.save()

            # Update payment dates for all details
            self.payroll_details.update(paid_date=date.today())

    def cancel(self):
        """إلغاء التشغيل"""
        if self.status in ['draft', 'calculating', 'review']:
            self.status = 'cancelled'
            self.save()


class PayrollDetail(models.Model):
    """نموذج تفاصيل رواتب الموظفين المحسن"""
    payroll_detail_id = models.AutoField(primary_key=True, db_column='PayrollDetailID')
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, db_column='RunID', related_name='payroll_details', verbose_name='تشغيل الراتب')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', verbose_name='الموظف')

    # Basic salary components
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='BasicSalary', verbose_name='الراتب الأساسي')
    housing_allowance = models.DecimalField(max_digits=18, decimal_places=2, db_column='Housing', default=0, verbose_name='بدل السكن')
    transport_allowance = models.DecimalField(max_digits=18, decimal_places=2, db_column='Transport', default=0, verbose_name='بدل المواصلات')
    food_allowance = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='بدل الطعام')
    mobile_allowance = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='بدل الهاتف')
    other_allowances = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='بدلات أخرى')

    # Variable pay components
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='ساعات إضافية')
    overtime_amount = models.DecimalField(max_digits=18, decimal_places=2, db_column='Overtime', default=0, verbose_name='مبلغ الوقت الإضافي')
    bonus_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='مكافآت')
    commission_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='عمولة')

    # Attendance-based calculations
    worked_days = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='أيام العمل')
    absent_days = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='أيام الغياب')
    leave_days = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='أيام الإجازة')
    late_minutes = models.IntegerField(default=0, verbose_name='دقائق التأخير')

    # Deductions
    gosi_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='GOSI', default=0, verbose_name='خصم التأمينات')
    tax_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='Tax', default=0, verbose_name='خصم الضرائب')
    insurance_deduction = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='خصم التأمين الطبي')
    loan_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='LoanDeduction', default=0, verbose_name='خصم القروض')
    absence_deduction = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='خصم الغياب')
    late_deduction = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='خصم التأخير')
    other_deductions = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='خصومات أخرى')

    # Calculated totals
    gross_salary = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='إجمالي الراتب')
    total_allowances = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='إجمالي البدلات')
    total_deductions = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='إجمالي الخصومات')
    net_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='NetSalary', default=0, verbose_name='صافي الراتب')

    # Processing metadata
    is_processed = models.BooleanField(default=False, verbose_name='تم المعالجة')
    calculation_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات الحساب')
    paid_date = models.DateField(db_column='PaidDate', blank=True, null=True, verbose_name='تاريخ الدفع')
    payment_method = models.CharField(max_length=20, default='bank_transfer', verbose_name='طريقة الدفع')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'PayrollDetails'
        verbose_name = 'تفصيل راتب'
        verbose_name_plural = 'تفاصيل الرواتب'
        unique_together = ['run', 'emp']
        ordering = ['emp__emp_code']

    def __str__(self):
        """__str__ function"""
        return f"{self.run.run_number} - {self.emp}"

    def calculate_totals(self):
        """حساب المجاميع"""
        # Calculate total allowances
        self.total_allowances = (
            self.housing_allowance + self.transport_allowance +
            self.food_allowance + self.mobile_allowance + self.other_allowances
        )

        # Calculate gross salary
        self.gross_salary = (
            self.basic_salary + self.total_allowances +
            self.overtime_amount + self.bonus_amount + self.commission_amount
        )

        # Calculate total deductions
        self.total_deductions = (
            self.gosi_deduction + self.tax_deduction + self.insurance_deduction +
            self.loan_deduction + self.absence_deduction + self.late_deduction +
            self.other_deductions
        )

        # Calculate net salary
        self.net_salary = self.gross_salary - self.total_deductions

        # Ensure net salary is not negative
        if self.net_salary < 0:
            self.net_salary = 0

    def save(self, *args, **kwargs):
        """save function"""
        self.calculate_totals()
        super().save(*args, **kwargs)

    def mark_as_processed(self):
        """تحديد كمعالج"""
        self.is_processed = True
        self.save()


class PayrollBonus(models.Model):
    """نموذج مكافآت الموظفين"""
    BONUS_TYPES = [
        ('performance', 'مكافأة أداء'),
        ('annual', 'مكافأة سنوية'),
        ('project', 'مكافأة مشروع'),
        ('attendance', 'مكافأة حضور'),
        ('special', 'مكافأة خاصة'),
    ]

    bonus_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPES, verbose_name='نوع المكافأة')
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='المبلغ')
    description = models.TextField(verbose_name='الوصف')
    effective_date = models.DateField(verbose_name='تاريخ السريان')
    is_recurring = models.BooleanField(default=False, verbose_name='متكررة')
    is_taxable = models.BooleanField(default=True, verbose_name='خاضعة للضريبة')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='approved_bonuses', verbose_name='معتمد بواسطة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""
        verbose_name = 'مكافأة موظف'
        verbose_name_plural = 'مكافآت الموظفين'
        ordering = ['-effective_date']

    def __str__(self):
        """__str__ function"""
        return f'{self.employee} - {self.get_bonus_type_display()} - {self.amount}'


class PayrollDeduction(models.Model):
    """نموذج خصومات الموظفين"""
    DEDUCTION_TYPES = [
        ('disciplinary', 'خصم تأديبي'),
        ('loan', 'خصم قرض'),
        ('advance', 'خصم سلفة'),
        ('insurance', 'خصم تأمين'),
        ('other', 'خصم آخر'),
    ]

    deduction_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    deduction_type = models.CharField(max_length=20, choices=DEDUCTION_TYPES, verbose_name='نوع الخصم')
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='المبلغ')
    description = models.TextField(verbose_name='الوصف')
    effective_date = models.DateField(verbose_name='تاريخ السريان')
    end_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء')
    is_recurring = models.BooleanField(default=False, verbose_name='متكرر')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='approved_deductions', verbose_name='معتمد بواسطة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""
        verbose_name = 'خصم موظف'
        verbose_name_plural = 'خصومات الموظفين'
        ordering = ['-effective_date']

    def __str__(self):
        """__str__ function"""
        return f'{self.employee} - {self.get_deduction_type_display()} - {self.amount}'


class PayrollCalculationRule(models.Model):
    """نموذج قواعد حساب الرواتب"""
    rule_id = models.AutoField(primary_key=True)
    rule_name = models.CharField(max_length=100, verbose_name='اسم القاعدة')
    rule_type = models.CharField(max_length=20, choices=[
        ('overtime', 'وقت إضافي'),
        ('deduction', 'خصم'),
        ('bonus', 'مكافأة'),
        ('tax', 'ضريبة'),
    ], verbose_name='نوع القاعدة')
    formula = models.TextField(verbose_name='معادلة الحساب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class"""
        verbose_name = 'قاعدة حساب راتب'
        verbose_name_plural = 'قواعد حساب الرواتب'

    def __str__(self):
        """__str__ function"""
        return self.rule_name


# Create your models here.
