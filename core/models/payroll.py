"""
نماذج الرواتب المحسنة
Enhanced Payroll Models
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .base import BaseModel, AuditableModel
from .hr import Employee


class PayrollRun(AuditableModel):
    """تشغيل الرواتب المحسن"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('calculating', _('جاري الحساب')),
        ('review', _('قيد المراجعة')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
        ('cancelled', _('ملغى')),
        ('closed', _('مغلق')),
    ]

    PAYROLL_TYPES = [
        ('monthly', _('شهري')),
        ('bi_weekly', _('نصف شهري')),
        ('weekly', _('أسبوعي')),
        ('bonus', _('مكافآت')),
        ('final_settlement', _('تصفية نهائية')),
        ('overtime_only', _('وقت إضافي فقط')),
    ]

    # Basic Information
    run_number = models.CharField(max_length=20, unique=True, verbose_name=_('رقم التشغيل'))
    payroll_type = models.CharField(max_length=20, choices=PAYROLL_TYPES, default='monthly', verbose_name=_('نوع الراتب'))
    title = models.CharField(max_length=200, verbose_name=_('عنوان التشغيل'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))

    # Period Information
    period_start = models.DateField(verbose_name=_('بداية الفترة'))
    period_end = models.DateField(verbose_name=_('نهاية الفترة'))
    pay_date = models.DateField(verbose_name=_('تاريخ الدفع'))

    # Processing Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    total_employees = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي الموظفين'))
    processed_employees = models.PositiveIntegerField(default=0, verbose_name=_('الموظفين المعالجين'))

    # Financial Totals
    total_gross_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي المبلغ الإجمالي'))
    total_allowances = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي البدلات'))
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي الخصومات'))
    total_overtime = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي الوقت الإضافي'))
    total_bonuses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي المكافآت'))
    total_net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي المبلغ الصافي'))

    # Employer Costs
    total_gosi_employer = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي تأمينات صاحب العمل'))
    total_employer_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي تكلفة صاحب العمل'))

    # Processing Settings
    include_overtime = models.BooleanField(default=True, verbose_name=_('تضمين الوقت الإضافي'))
    include_bonuses = models.BooleanField(default=True, verbose_name=_('تضمين المكافآت'))
    include_deductions = models.BooleanField(default=True, verbose_name=_('تضمين الخصومات'))
    prorate_salaries = models.BooleanField(default=True, verbose_name=_('تقسيم الرواتب نسبياً'))

    # Approval Workflow
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_payroll_runs', verbose_name=_('معتمد بواسطة'))
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الاعتماد'))

    # Processing Metadata
    calculation_started_at = models.DateTimeField(blank=True, null=True, verbose_name=_('بداية الحساب'))
    calculation_completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('انتهاء الحساب'))
    processing_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات المعالجة'))

    class Meta:
        """Meta class"""
        verbose_name = _('تشغيل راتب')
        verbose_name_plural = _('تشغيلات الرواتب')
        ordering = ['-period_end', '-created_at']

    def __str__(self):
        """__str__ function"""
        return f"{self.run_number} - {self.title}"

    def save(self, *args, **kwargs):
        """حفظ محسن مع توليد رقم التشغيل"""
        if not self.run_number:
            self._generate_run_number()
        super().save(*args, **kwargs)

    def _generate_run_number(self):
        """توليد رقم تشغيل تلقائي"""
        year = self.period_end.year
        month = self.period_end.month
        count = PayrollRun.objects.filter(
            period_end__year=year,
            period_end__month=month
        ).count() + 1
        self.run_number = f'PR{year}{month:02d}{count:03d}'

    @property
    def is_editable(self):
        """فحص إذا كان بالإمكان تعديل التشغيل"""
        return self.status in ['draft', 'calculating']

    @property
    def processing_progress(self):
        """نسبة إنجاز المعالجة"""
        if self.total_employees > 0:
            return (self.processed_employees / self.total_employees) * 100
        return 0

    @property
    def period_description(self):
        """وصف الفترة"""
        return f"{self.period_start.strftime('%Y-%m-%d')} إلى {self.period_end.strftime('%Y-%m-%d')}"

    def start_calculation(self, user=None):
        """بدء عملية حساب الرواتب"""
        if self.status == 'draft':
            self.status = 'calculating'
            self.calculation_started_at = timezone.now()
            if user:
                self.updated_by = user
            self.save()

    def complete_calculation(self, user=None):
        """إنهاء عملية حساب الرواتب"""
        if self.status == 'calculating':
            self.status = 'review'
            self.calculation_completed_at = timezone.now()
            self.calculate_totals()
            if user:
                self.updated_by = user
            self.save()

    def approve(self, approved_by):
        """اعتماد الرواتب"""
        if self.status == 'review':
            self.status = 'approved'
            self.approved_by = approved_by
            self.approved_at = timezone.now()
            self.save()

    def mark_as_paid(self, user=None):
        """تحديد كمدفوع"""
        if self.status == 'approved':
            self.status = 'paid'
            if user:
                self.updated_by = user
            self.save()

            # تحديث تاريخ الدفع لجميع التفاصيل
            self.payroll_details.update(paid_date=date.today())

    def calculate_totals(self):
        """حساب المجاميع من تفاصيل الرواتب"""
        details = self.payroll_details.all()

        self.total_employees = details.count()
        self.processed_employees = details.filter(is_processed=True).count()

        # حساب المجاميع المالية
        totals = details.aggregate(
            gross=models.Sum('gross_salary'),
            allowances=models.Sum('total_allowances'),
            deductions=models.Sum('total_deductions'),
            overtime=models.Sum('overtime_amount'),
            bonuses=models.Sum('bonus_amount'),
            net=models.Sum('net_salary'),
            gosi_employer=models.Sum('gosi_employer_contribution'),
        )

        self.total_gross_amount = totals['gross'] or 0
        self.total_allowances = totals['allowances'] or 0
        self.total_deductions = totals['deductions'] or 0
        self.total_overtime = totals['overtime'] or 0
        self.total_bonuses = totals['bonuses'] or 0
        self.total_net_amount = totals['net'] or 0
        self.total_gosi_employer = totals['gosi_employer'] or 0
        self.total_employer_cost = self.total_gross_amount + self.total_gosi_employer

    def get_employees_for_processing(self):
        """الحصول على الموظفين المؤهلين للمعالجة"""
        return Employee.objects.filter(
            emp_status='active',
            hire_date__lte=self.period_end
        ).select_related('department', 'job_position', 'manager')


class PayrollDetail(AuditableModel):
    """تفاصيل رواتب الموظفين المحسنة"""
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payroll_details', verbose_name=_('تشغيل الراتب'))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('الموظف'))

    # Basic Salary Components
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('الراتب الأساسي'))
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل السكن'))
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل المواصلات'))
    food_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل الطعام'))
    mobile_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدل الهاتف'))
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('بدلات أخرى'))

    # Variable Pay Components
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('ساعات إضافية'))
    overtime_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('معدل الوقت الإضافي'))
    overtime_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('مبلغ الوقت الإضافي'))
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('مكافآت'))
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('عمولة'))

    # Attendance-based Calculations
    worked_days = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('أيام العمل'))
    absent_days = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('أيام الغياب'))
    leave_days = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('أيام الإجازة'))
    late_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_('ساعات التأخير'))

    # Deductions
    gosi_employee_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('مساهمة الموظف في التأمينات'))
    gosi_employer_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('مساهمة صاحب العمل في التأمينات'))
    income_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('ضريبة الدخل'))
    medical_insurance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('التأمين الطبي'))
    loan_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('خصم القروض'))
    advance_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('خصم السلف'))
    absence_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('خصم الغياب'))
    late_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('خصم التأخير'))
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('خصومات أخرى'))

    # Calculated Totals
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('إجمالي البدلات'))
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('إجمالي الراتب'))
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('إجمالي الخصومات'))
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('صافي الراتب'))

    # Processing Information
    is_processed = models.BooleanField(default=False, verbose_name=_('تم المعالجة'))
    calculation_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات الحساب'))
    paid_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الدفع'))
    payment_method = models.CharField(max_length=20, default='bank_transfer', verbose_name=_('طريقة الدفع'))

    # Proration Information
    is_prorated = models.BooleanField(default=False, verbose_name=_('مقسم نسبياً'))
    proration_factor = models.DecimalField(max_digits=5, decimal_places=4, default=1, verbose_name=_('معامل التقسيم'))
    proration_reason = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('سبب التقسيم'))

    class Meta:
        """Meta class"""
        verbose_name = _('تفصيل راتب')
        verbose_name_plural = _('تفاصيل الرواتب')
        unique_together = ['payroll_run', 'employee']
        ordering = ['employee__emp_code']

    def __str__(self):
        """__str__ function"""
        return f"{self.payroll_run.run_number} - {self.employee.get_full_name()}"

    def calculate_totals(self):
        """حساب المجاميع"""
        # حساب إجمالي البدلات
        self.total_allowances = (
            self.housing_allowance + self.transport_allowance +
            self.food_allowance + self.mobile_allowance + self.other_allowances
        )

        # حساب إجمالي الراتب
        self.gross_salary = (
            self.basic_salary + self.total_allowances +
            self.overtime_amount + self.bonus_amount + self.commission_amount
        )

        # تطبيق التقسيم النسبي إذا كان مطلوباً
        if self.is_prorated and self.proration_factor != 1:
            self.gross_salary = (self.gross_salary * self.proration_factor).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        # حساب إجمالي الخصومات
        self.total_deductions = (
            self.gosi_employee_contribution + self.income_tax + self.medical_insurance +
            self.loan_deduction + self.advance_deduction + self.absence_deduction +
            self.late_deduction + self.other_deductions
        )

        # حساب صافي الراتب
        self.net_salary = max(Decimal('0'), self.gross_salary - self.total_deductions)

    def calculate_gosi_contributions(self):
        """حساب مساهمات التأمينات الاجتماعية"""
        # معدلات التأمينات الاجتماعية في السعودية (2024)
        employee_rate = Decimal('0.10')  # 10% للموظف
        employer_rate = Decimal('0.12')  # 12% لصاحب العمل

        # الحد الأقصى للراتب الخاضع للتأمينات (45,000 ريال)
        max_insurable_salary = Decimal('45000')

        # الراتب الخاضع للتأمينات
        insurable_salary = min(self.basic_salary, max_insurable_salary)

        self.gosi_employee_contribution = (insurable_salary * employee_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        self.gosi_employer_contribution = (insurable_salary * employer_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    def calculate_overtime(self):
        """حساب الوقت الإضافي"""
        if self.overtime_hours > 0 and self.overtime_rate > 0:
            # حساب الأجر بالساعة من الراتب الأساسي
            monthly_hours = Decimal('176')  # 22 يوم × 8 ساعات
            hourly_rate = self.basic_salary / monthly_hours

            # حساب مبلغ الوقت الإضافي
            self.overtime_amount = (
                hourly_rate * self.overtime_rate * self.overtime_hours
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def calculate_absence_deduction(self):
        """حساب خصم الغياب"""
        if self.absent_days > 0:
            # حساب الأجر اليومي
            monthly_working_days = Decimal('22')
            daily_rate = self.basic_salary / monthly_working_days

            self.absence_deduction = (daily_rate * self.absent_days).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

    def calculate_late_deduction(self):
        """حساب خصم التأخير"""
        if self.late_hours > 0:
            # حساب الأجر بالساعة
            monthly_hours = Decimal('176')
            hourly_rate = self.basic_salary / monthly_hours

            self.late_deduction = (hourly_rate * self.late_hours).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

    def apply_proration(self, worked_days, total_days, reason=None):
        """تطبيق التقسيم النسبي"""
        if worked_days < total_days:
            self.is_prorated = True
            self.proration_factor = Decimal(str(worked_days)) / Decimal(str(total_days))
            self.proration_reason = reason or f"عمل {worked_days} من أصل {total_days} يوم"

    def process_payroll(self):
        """معالجة الراتب بالكامل"""
        # حساب المساهمات
        self.calculate_gosi_contributions()

        # حساب الوقت الإضافي
        self.calculate_overtime()

        # حساب خصومات الغياب والتأخير
        self.calculate_absence_deduction()
        self.calculate_late_deduction()

        # حساب المجاميع
        self.calculate_totals()

        # تحديد كمعالج
        self.is_processed = True

    def save(self, *args, **kwargs):
        """حفظ محسن مع حساب المجاميع"""
        self.calculate_totals()
        super().save(*args, **kwargs)


class PayrollBonus(BaseModel):
    """مكافآت الرواتب"""
    BONUS_TYPES = [
        ('performance', _('مكافأة أداء')),
        ('annual', _('مكافأة سنوية')),
        ('project', _('مكافأة مشروع')),
        ('attendance', _('مكافأة حضور')),
        ('holiday', _('مكافأة عيد')),
        ('special', _('مكافأة خاصة')),
        ('commission', _('عمولة')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_bonuses', verbose_name=_('الموظف'))
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPES, verbose_name=_('نوع المكافأة'))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('المبلغ'))
    description = models.TextField(verbose_name=_('الوصف'))
    effective_date = models.DateField(verbose_name=_('تاريخ السريان'))
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='bonuses', verbose_name=_('تشغيل الراتب'))

    # Tax and Processing
    is_taxable = models.BooleanField(default=True, verbose_name=_('خاضعة للضريبة'))
    is_recurring = models.BooleanField(default=False, verbose_name=_('متكررة'))
    is_processed = models.BooleanField(default=False, verbose_name=_('تم المعالجة'))

    # Approval
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_bonuses', verbose_name=_('معتمد بواسطة'))
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الاعتماد'))

    class Meta:
        """Meta class"""
        verbose_name = _('مكافأة راتب')
        verbose_name_plural = _('مكافآت الرواتب')
        ordering = ['-effective_date']

    def __str__(self):
        """__str__ function"""
        return f'{self.employee.get_full_name()} - {self.get_bonus_type_display()} - {self.amount}'


class PayrollDeduction(BaseModel):
    """خصومات الرواتب"""
    DEDUCTION_TYPES = [
        ('disciplinary', _('خصم تأديبي')),
        ('loan', _('خصم قرض')),
        ('advance', _('خصم سلفة')),
        ('insurance', _('خصم تأمين')),
        ('absence', _('خصم غياب')),
        ('late', _('خصم تأخير')),
        ('damage', _('خصم أضرار')),
        ('other', _('خصم آخر')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_deductions', verbose_name=_('الموظف'))
    deduction_type = models.CharField(max_length=20, choices=DEDUCTION_TYPES, verbose_name=_('نوع الخصم'))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('المبلغ'))
    description = models.TextField(verbose_name=_('الوصف'))
    effective_date = models.DateField(verbose_name=_('تاريخ السريان'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الانتهاء'))
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='deductions', verbose_name=_('تشغيل الراتب'))

    # Processing
    is_recurring = models.BooleanField(default=False, verbose_name=_('متكرر'))
    is_processed = models.BooleanField(default=False, verbose_name=_('تم المعالجة'))
    installments_total = models.PositiveIntegerField(default=1, verbose_name=_('عدد الأقساط'))
    installments_remaining = models.PositiveIntegerField(default=1, verbose_name=_('الأقساط المتبقية'))

    # Approval
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_deductions', verbose_name=_('معتمد بواسطة'))
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الاعتماد'))

    class Meta:
        """Meta class"""
        verbose_name = _('خصم راتب')
        verbose_name_plural = _('خصومات الرواتب')
        ordering = ['-effective_date']

    def __str__(self):
        """__str__ function"""
        return f'{self.employee.get_full_name()} - {self.get_deduction_type_display()} - {self.amount}'

    @property
    def installment_amount(self):
        """مبلغ القسط الواحد"""
        if self.installments_total > 0:
            return self.amount / self.installments_total
        return self.amount

    @property
    def is_completed(self):
        """فحص إذا كان الخصم مكتمل"""
        return self.installments_remaining <= 0
