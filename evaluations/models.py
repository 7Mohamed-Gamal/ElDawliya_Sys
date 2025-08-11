from django.db import models
from employees.models import Employee


class EvaluationPeriod(models.Model):
    period_id = models.AutoField(primary_key=True, db_column='PeriodID')
    period_name = models.CharField(max_length=100, db_column='PeriodName')
    start_date = models.DateField(db_column='StartDate')
    end_date = models.DateField(db_column='EndDate')

    class Meta:
        db_table = 'EvaluationPeriods'
        verbose_name = 'فترة تقييم'
        verbose_name_plural = 'فترات التقييم'

    def __str__(self):
        return self.period_name


class EmployeeEvaluation(models.Model):
    eval_id = models.AutoField(primary_key=True, db_column='EvalID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE, db_column='PeriodID')
    manager_id = models.IntegerField(db_column='ManagerID', blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, db_column='Score', blank=True, null=True)
    notes = models.CharField(max_length=1000, db_column='Notes', blank=True, null=True)
    eval_date = models.DateField(db_column='EvalDate', blank=True, null=True)

    class Meta:
        db_table = 'EmployeeEvaluations'
        verbose_name = 'تقييم'
        verbose_name_plural = 'تقييمات الموظفين'

    def __str__(self):
        return f"{self.emp_id} - {self.period_id}"

# Create your models here.
