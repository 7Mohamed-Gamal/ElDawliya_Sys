"""
Org Models - Compatibility Layer
================================
This module provides backward compatibility by re-exporting models from core.models.
All actual model definitions have been moved to core/models/ to avoid duplication.
"""
from django.db import models
from companies.models import Company

# Import from unified core models to maintain backward compatibility
from core.models.hr import Department as CoreDepartment


class Branch(models.Model):
    """Branch class"""
    branch_id = models.AutoField(primary_key=True, db_column='BranchID')
    branch_name = models.CharField(max_length=150, db_column='BranchName')
    branch_address = models.CharField(max_length=500, db_column='BranchAddress', blank=True, null=True)
    phone = models.CharField(max_length=50, db_column='Phone', blank=True, null=True)
    manager_id = models.IntegerField(db_column='ManagerID', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, db_column='CompanyID', null=True, blank=True)
    is_active = models.BooleanField(db_column='IsActive', default=True)

    class Meta:
        """Meta class"""
        db_table = 'Branches'
        verbose_name = 'الفرع'
        verbose_name_plural = 'الأفرع'

    def __str__(self):
        """__str__ function"""
        return self.branch_name


# Compatibility alias - use core.models.hr.Department instead
Department = CoreDepartment


class Job(models.Model):
    """Job class"""
    job_id = models.AutoField(primary_key=True, db_column='JobID')
    job_title = models.CharField(max_length=150, db_column='JobTitle')
    job_level = models.IntegerField(db_column='JobLevel', blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='BasicSalary', blank=True, null=True)
    description = models.CharField(max_length=500, db_column='Description', blank=True, null=True)
    is_active = models.BooleanField(db_column='IsActive', default=True)

    class Meta:
        """Meta class"""
        db_table = 'Jobs'
        verbose_name = 'الوظيفة'
        verbose_name_plural = 'الوظائف'

    def __str__(self):
        """__str__ function"""
        return self.job_title


__all__ = ['Branch', 'Department', 'Job']
