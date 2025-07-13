"""
Legacy Employee model that matches the existing database table structure
This is a temporary solution to fix the dashboard error
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class LegacyEmployee(models.Model):
    """Legacy Employee model that matches the Tbl_Employee table structure"""
    
    emp_id = models.IntegerField(
        db_column='Emp_ID', 
        primary_key=True, 
        verbose_name=_('رقم الموظف')
    )
    
    emp_first_name = models.CharField(
        blank=True, 
        db_column='Emp_First_Name', 
        max_length=50, 
        null=True, 
        verbose_name=_('الاسم الأول')
    )
    
    emp_second_name = models.CharField(
        blank=True, 
        db_column='Emp_Second_Name', 
        max_length=50, 
        null=True, 
        verbose_name=_('الاسم الثاني')
    )
    
    emp_full_name = models.CharField(
        blank=True, 
        db_column='Emp_Full_Name', 
        max_length=100, 
        null=True, 
        verbose_name=_('الاسم الكامل')
    )
    
    working_condition = models.CharField(
        blank=True, 
        choices=[
            ('سارى', 'سارى'), 
            ('إجازة', 'إجازة'), 
            ('استقالة', 'استقالة'), 
            ('انقطاع عن العمل', 'انقطاع عن العمل')
        ], 
        db_column='Working_Condition', 
        max_length=50, 
        null=True, 
        verbose_name=_('حالة العمل')
    )
    
    insurance_status = models.CharField(
        blank=True,
        choices=[
            ('مؤمن عليه', 'مؤمن عليه'),
            ('غير مؤمن عليه', 'غير مؤمن عليه')
        ],
        db_column='Insurance_Status',
        max_length=50,
        null=True,
        verbose_name=_('حالة التأمين')
    )
    
    national_id = models.CharField(
        blank=True, 
        db_column='National_ID', 
        max_length=14, 
        null=True, 
        verbose_name=_('الرقم القومي')
    )
    
    date_birth = models.DateField(
        blank=True, 
        db_column='Date_Birth', 
        null=True, 
        verbose_name=_('تاريخ الميلاد')
    )
    
    emp_date_hiring = models.DateField(
        blank=True,
        db_column='Emp_Date_Hiring',
        null=True,
        verbose_name=_('تاريخ التوظيف')
    )
    
    dept_name = models.CharField(
        blank=True, 
        db_column='Dept_Name', 
        max_length=50, 
        null=True, 
        verbose_name=_('اسم القسم')
    )
    
    jop_code = models.IntegerField(
        blank=True, 
        db_column='Jop_Code', 
        null=True, 
        verbose_name=_('كود الوظيفة')
    )
    
    # Add relationship to LegacyDepartment
    department = models.ForeignKey(
        'Hr.LegacyDepartment',
        db_column='Dept_Code',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legacy_employees',
        verbose_name=_('القسم')
    )
    
    SHIFT_TYPE_CHOICES = [
        ('morning', 'صباحي'),
        ('evening', 'مسائي'),
        ('night', 'ليلي')
    ]

    class Meta:
        managed = False  # Don't let Django manage this table - it already exists
        db_table = 'Tbl_Employee'
        verbose_name = _('الموظف')
        verbose_name_plural = _('الموظفون')
    
    def __str__(self):
        return self.emp_full_name or f"Employee {self.emp_id}"
