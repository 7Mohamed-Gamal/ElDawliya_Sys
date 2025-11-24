from django.db import models
from employees.models import Employee


class DisciplinaryAction(models.Model):
    """DisciplinaryAction class"""
    action_id = models.AutoField(primary_key=True, db_column='ActionID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    action_type = models.CharField(max_length=50, db_column='ActionType')
    action_date = models.DateField(db_column='ActionDate')
    reason = models.CharField(max_length=500, db_column='Reason', blank=True, null=True)
    severity_level = models.IntegerField(db_column='SeverityLevel', blank=True, null=True)
    decision_by = models.IntegerField(db_column='DecisionBy', blank=True, null=True)
    valid_until = models.DateField(db_column='ValidUntil', blank=True, null=True)
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'DisciplinaryActions'
        verbose_name = 'إجراء انضباطي'
        verbose_name_plural = 'الإجراءات الانضباطية'

# Create your models here.
