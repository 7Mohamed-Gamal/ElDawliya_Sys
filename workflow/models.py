from django.db import models
from employees.models import Employee


class WorkflowStep(models.Model):
    """WorkflowStep class"""
    step_id = models.AutoField(primary_key=True, db_column='StepID')
    step_name = models.CharField(max_length=100, db_column='StepName')
    sequence_no = models.IntegerField(db_column='SequenceNo')
    role_id = models.IntegerField(db_column='RoleID', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'WorkflowSteps'
        verbose_name = 'خطوة سير عمل'
        verbose_name_plural = 'خطوات سير العمل'


class WorkflowInstance(models.Model):
    """WorkflowInstance class"""
    instance_id = models.AutoField(primary_key=True, db_column='InstanceID')
    step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, db_column='StepID', blank=True, null=True)
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID', blank=True, null=True)
    status = models.CharField(max_length=30, db_column='Status')
    action_date = models.DateTimeField(db_column='ActionDate', blank=True, null=True)
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'WorkflowInstances'
        verbose_name = 'حالة سير عمل'
        verbose_name_plural = 'حالات سير العمل'

# Create your models here.
