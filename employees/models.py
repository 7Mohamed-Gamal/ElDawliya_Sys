from django.db import models
from org.models import Branch, Department, Job


class Employee(models.Model):
    emp_id = models.AutoField(primary_key=True, db_column='EmpID')
    emp_code = models.CharField(max_length=20, unique=True, db_column='EmpCode')
    first_name = models.CharField(max_length=100, db_column='FirstName', blank=True, null=True)
    second_name = models.CharField(max_length=100, db_column='SecondName', blank=True, null=True)
    third_name = models.CharField(max_length=100, db_column='ThirdName', blank=True, null=True)
    last_name = models.CharField(max_length=100, db_column='LastName', blank=True, null=True)
    # FullName computed column will be added via RunSQL migration
    gender = models.CharField(max_length=1, db_column='Gender')
    birth_date = models.DateField(db_column='BirthDate', blank=True, null=True)
    nationality = models.CharField(max_length=50, db_column='Nationality', blank=True, null=True)
    national_id = models.CharField(max_length=20, db_column='NationalID', blank=True, null=True)
    passport_no = models.CharField(max_length=20, db_column='PassportNo', blank=True, null=True)
    mobile = models.CharField(max_length=50, db_column='Mobile', blank=True, null=True)
    email = models.EmailField(max_length=100, db_column='Email', blank=True, null=True)
    address = models.CharField(max_length=500, db_column='Address', blank=True, null=True)
    hire_date = models.DateField(db_column='HireDate', blank=True, null=True)
    join_date = models.DateField(db_column='JoinDate', blank=True, null=True)
    probation_end = models.DateField(db_column='ProbationEnd', blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.PROTECT, db_column='JobID')
    dept = models.ForeignKey(Department, on_delete=models.PROTECT, db_column='DeptID')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, db_column='BranchID')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='ManagerID')
    emp_status = models.CharField(max_length=30, db_column='EmpStatus', default='Active')
    termination_date = models.DateField(db_column='TerminationDate', blank=True, null=True)
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True)
    photo = models.BinaryField(db_column='Photo', blank=True, null=True)
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UpdatedAt', blank=True, null=True)

    class Meta:
        db_table = 'Employees'
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفون'

    def __str__(self):
        return f"{self.emp_code} - {self.get_full_name()}"

    def get_full_name(self):
        """Get employee's full name"""
        names = [self.first_name, self.second_name, self.third_name, self.last_name]
        return ' '.join([name for name in names if name])

    @property
    def full_name(self):
        """Property for full name"""
        return self.get_full_name()

    @property
    def emp_full_name(self):
        """Alias for compatibility with other modules"""
        return self.get_full_name()

    @property
    def age(self):
        """Calculate employee age"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def years_of_service(self):
        """Calculate years of service"""
        if self.hire_date:
            from datetime import date
            today = date.today()
            return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))
        return None

    @property
    def is_active(self):
        """Check if employee is active"""
        return self.emp_status == 'Active'

    @property
    def is_on_probation(self):
        """Check if employee is still on probation"""
        if self.probation_end:
            from datetime import date
            return date.today() <= self.probation_end
        return False

    def clean(self):
        """Validate employee data"""
        from django.core.exceptions import ValidationError
        from datetime import date

        # Validate dates
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError('تاريخ الميلاد لا يمكن أن يكون في المستقبل')

        if self.hire_date and self.hire_date > date.today():
            raise ValidationError('تاريخ التوظيف لا يمكن أن يكون في المستقبل')

        if self.join_date and self.hire_date and self.join_date < self.hire_date:
            raise ValidationError('تاريخ الالتحاق لا يمكن أن يكون قبل تاريخ التوظيف')

        if self.probation_end and self.hire_date and self.probation_end < self.hire_date:
            raise ValidationError('تاريخ انتهاء فترة التجربة لا يمكن أن يكون قبل تاريخ التوظيف')

        if self.termination_date and self.hire_date and self.termination_date < self.hire_date:
            raise ValidationError('تاريخ إنهاء الخدمة لا يمكن أن يكون قبل تاريخ التوظيف')

    def save(self, *args, **kwargs):
        """Override save to perform validations"""
        self.full_clean()
        super().save(*args, **kwargs)


class EmployeeBankAccount(models.Model):
    acc_id = models.AutoField(primary_key=True, db_column='AccID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    bank = models.ForeignKey('banks.Bank', on_delete=models.SET_NULL, db_column='BankID', blank=True, null=True)
    account_no = models.CharField(max_length=50, db_column='AccountNo', blank=True, null=True)
    iban = models.CharField(max_length=50, db_column='IBAN', blank=True, null=True)

    class Meta:
        db_table = 'EmployeeBankAccounts'
        verbose_name = 'حساب بنكي'
        verbose_name_plural = 'حسابات الموظفين البنكية'


class EmployeeDocument(models.Model):
    doc_id = models.AutoField(primary_key=True, db_column='DocID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    doc_type = models.CharField(max_length=100, db_column='DocType')
    doc_name = models.CharField(max_length=255, db_column='DocName', blank=True, null=True)
    file_data = models.BinaryField(db_column='FileData', blank=True, null=True)
    file_ext = models.CharField(max_length=10, db_column='FileExt', blank=True, null=True)
    upload_date = models.DateTimeField(db_column='UploadDate', auto_now_add=True)
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True)

    class Meta:
        db_table = 'EmployeeDocuments'
        verbose_name = 'مستند'
        verbose_name_plural = 'مستندات الموظفين'

# Import extended models for comprehensive HR management
try:
    from .models_extended import *
except ImportError:
    # Extended models not yet available during initial migration
    pass
