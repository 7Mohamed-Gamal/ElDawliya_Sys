from django.db import models
from employees.models import Employee


class EmployeeSalary(models.Model):
    salary_id = models.AutoField(primary_key=True, db_column='SalaryID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='BasicSalary', blank=True, null=True)
    housing_allow = models.DecimalField(max_digits=18, decimal_places=2, db_column='HousingAllow', blank=True, null=True)
    transport = models.DecimalField(max_digits=18, decimal_places=2, db_column='Transport', blank=True, null=True)
    other_allow = models.DecimalField(max_digits=18, decimal_places=2, db_column='OtherAllow', blank=True, null=True)
    gosi_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='GosiDeduction', blank=True, null=True)
    tax_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='TaxDeduction', blank=True, null=True)
    # TotalSalary computed column via RunSQL
    currency = models.CharField(max_length=3, db_column='Currency', default='SAR')
    effective_date = models.DateField(db_column='EffectiveDate', blank=True, null=True)
    end_date = models.DateField(db_column='EndDate', blank=True, null=True)
    is_current = models.BooleanField(db_column='IsCurrent', default=True)

    class Meta:
        db_table = 'EmployeeSalaries'
        verbose_name = 'راتب موظف'
        verbose_name_plural = 'رواتب الموظفين'


class PayrollRun(models.Model):
    run_id = models.AutoField(primary_key=True, db_column='RunID')
    run_date = models.DateField(db_column='RunDate', blank=True, null=True)
    month_year = models.CharField(max_length=7, db_column='MonthYear')
    status = models.CharField(max_length=30, db_column='Status', default='Draft')
    confirmed_by = models.IntegerField(db_column='ConfirmedBy', blank=True, null=True)

    class Meta:
        db_table = 'PayrollRuns'
        verbose_name = 'تشغيل راتب'
        verbose_name_plural = 'تشغيلات الرواتب'


class PayrollDetail(models.Model):
    payroll_detail_id = models.AutoField(primary_key=True, db_column='PayrollDetailID')
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, db_column='RunID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='BasicSalary', blank=True, null=True)
    housing = models.DecimalField(max_digits=18, decimal_places=2, db_column='Housing', blank=True, null=True)
    transport = models.DecimalField(max_digits=18, decimal_places=2, db_column='Transport', blank=True, null=True)
    overtime = models.DecimalField(max_digits=18, decimal_places=2, db_column='Overtime', blank=True, null=True)
    gosi = models.DecimalField(max_digits=18, decimal_places=2, db_column='GOSI', blank=True, null=True)
    tax = models.DecimalField(max_digits=18, decimal_places=2, db_column='Tax', blank=True, null=True)
    loan_deduction = models.DecimalField(max_digits=18, decimal_places=2, db_column='LoanDeduction', blank=True, null=True)
    net_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='NetSalary', blank=True, null=True)
    paid_date = models.DateField(db_column='PaidDate', blank=True, null=True)

    class Meta:
        db_table = 'PayrollDetails'
        verbose_name = 'تفصيل راتب'
        verbose_name_plural = 'تفاصيل الرواتب'

# Create your models here.
