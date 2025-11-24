from django.db import models
from employees.models import Employee


class LoanType(models.Model):
    """LoanType class"""
    loan_type_id = models.AutoField(primary_key=True, db_column='LoanTypeID')
    type_name = models.CharField(max_length=100, db_column='TypeName')
    max_amount = models.DecimalField(max_digits=18, decimal_places=2, db_column='MaxAmount', blank=True, null=True)
    max_installments = models.IntegerField(db_column='MaxInstallments', blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, db_column='InterestRate', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'LoanTypes'
        verbose_name = 'نوع سلفة'
        verbose_name_plural = 'أنواع السلف'


class EmployeeLoan(models.Model):
    """EmployeeLoan class"""
    loan_id = models.AutoField(primary_key=True, db_column='LoanID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT, db_column='LoanTypeID', blank=True, null=True)
    request_amount = models.DecimalField(max_digits=18, decimal_places=2, db_column='RequestAmount', blank=True, null=True)
    approved_amount = models.DecimalField(max_digits=18, decimal_places=2, db_column='ApprovedAmount', blank=True, null=True)
    installment_amt = models.DecimalField(max_digits=18, decimal_places=2, db_column='InstallmentAmt', blank=True, null=True)
    start_date = models.DateField(db_column='StartDate', blank=True, null=True)
    end_date = models.DateField(db_column='EndDate', blank=True, null=True)
    status = models.CharField(max_length=30, db_column='Status', default='Pending')
    approved_by = models.IntegerField(db_column='ApprovedBy', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'EmployeeLoans'
        verbose_name = 'سلفة موظف'
        verbose_name_plural = 'سلف الموظفين'


class LoanInstallment(models.Model):
    """LoanInstallment class"""
    installment_id = models.AutoField(primary_key=True, db_column='InstallmentID')
    loan = models.ForeignKey(EmployeeLoan, on_delete=models.CASCADE, db_column='LoanID')
    due_date = models.DateField(db_column='DueDate', blank=True, null=True)
    paid_date = models.DateField(db_column='PaidDate', blank=True, null=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, db_column='Amount', blank=True, null=True)
    penalty = models.DecimalField(max_digits=18, decimal_places=2, db_column='Penalty', default=0)
    status = models.CharField(max_length=20, db_column='Status', default='Pending')

    class Meta:
        """Meta class"""
        db_table = 'LoanInstallments'
        verbose_name = 'قسط سلفة'
        verbose_name_plural = 'أقساط السلف'

# Create your models here.
