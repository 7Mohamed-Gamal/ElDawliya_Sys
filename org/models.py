from django.db import models
from companies.models import Company


class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True, db_column='BranchID')
    branch_name = models.CharField(max_length=150, db_column='BranchName')
    branch_address = models.CharField(max_length=500, db_column='BranchAddress', blank=True, null=True)
    phone = models.CharField(max_length=50, db_column='Phone', blank=True, null=True)
    manager_id = models.IntegerField(db_column='ManagerID', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, db_column='CompanyID', null=True, blank=True)
    is_active = models.BooleanField(db_column='IsActive', default=True)

    class Meta:
        db_table = 'Branches'
        verbose_name = 'الفرع'
        verbose_name_plural = 'الأفرع'

    def __str__(self):
        return self.branch_name


class Department(models.Model):
    dept_id = models.AutoField(primary_key=True, db_column='DeptID')
    dept_name = models.CharField(max_length=150, db_column='DeptName')
    parent_dept = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='ParentDeptID')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, db_column='BranchID')
    manager_id = models.IntegerField(db_column='ManagerID', blank=True, null=True)
    is_active = models.BooleanField(db_column='IsActive', default=True)

    class Meta:
        db_table = 'Departments'
        verbose_name = 'القسم'
        verbose_name_plural = 'الأقسام'

    def __str__(self):
        return self.dept_name


class Job(models.Model):
    job_id = models.AutoField(primary_key=True, db_column='JobID')
    job_title = models.CharField(max_length=150, db_column='JobTitle')
    job_level = models.IntegerField(db_column='JobLevel', blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=18, decimal_places=2, db_column='BasicSalary', blank=True, null=True)
    description = models.CharField(max_length=500, db_column='Description', blank=True, null=True)
    is_active = models.BooleanField(db_column='IsActive', default=True)

    class Meta:
        db_table = 'Jobs'
        verbose_name = 'الوظيفة'
        verbose_name_plural = 'الوظائف'

    def __str__(self):
        return self.job_title

# Create your models here.
