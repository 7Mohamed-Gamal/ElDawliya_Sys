from django.db import models
from org.models import Branch, Department, Job


class Employee(models.Model):
    """Employee class"""
    emp_id = models.AutoField(primary_key=True, db_column='EmpID')
    emp_code = models.CharField(max_length=20, unique=True, db_column='EmpCode')
    first_name = models.CharField(max_length=100, db_column='FirstName', blank=True, null=True)
    second_name = models.CharField(max_length=100, db_column='SecondName', blank=True, null=True)
    third_name = models.CharField(max_length=100, db_column='ThirdName', blank=True, null=True)
    last_name = models.CharField(max_length=100, db_column='LastName', blank=True, null=True)
    # FullName computed column will be added via RunSQL migration
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]

    STATUS_CHOICES = [
        ('Active', 'نشط'),
        ('Inactive', 'غير نشط'),
        ('Terminated', 'منتهي الخدمة'),
        ('Suspended', 'معلق'),
        ('On Leave', 'في إجازة'),
    ]

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, db_column='Gender', verbose_name='الجنس')
    birth_date = models.DateField(db_column='BirthDate', blank=True, null=True, verbose_name='تاريخ الميلاد')
    nationality = models.CharField(max_length=50, db_column='Nationality', blank=True, null=True, verbose_name='الجنسية')
    national_id = models.CharField(max_length=20, db_column='NationalID', blank=True, null=True, verbose_name='رقم الهوية الوطنية')
    passport_no = models.CharField(max_length=20, db_column='PassportNo', blank=True, null=True, verbose_name='رقم جواز السفر')
    mobile = models.CharField(max_length=50, db_column='Mobile', blank=True, null=True, verbose_name='الجوال')
    email = models.EmailField(max_length=100, db_column='Email', blank=True, null=True, verbose_name='البريد الإلكتروني')
    address = models.CharField(max_length=500, db_column='Address', blank=True, null=True, verbose_name='العنوان')
    hire_date = models.DateField(db_column='HireDate', blank=True, null=True, verbose_name='تاريخ التوظيف')
    join_date = models.DateField(db_column='JoinDate', blank=True, null=True, verbose_name='تاريخ الالتحاق')
    probation_end = models.DateField(db_column='ProbationEnd', blank=True, null=True, verbose_name='تاريخ انتهاء فترة التجربة')
    job = models.ForeignKey(Job, on_delete=models.PROTECT, db_column='JobID', related_name='employees', verbose_name='الوظيفة')
    dept = models.ForeignKey(Department, on_delete=models.PROTECT, db_column='DeptID', related_name='employees', verbose_name='القسم')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, db_column='BranchID', related_name='employees', verbose_name='الفرع')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='ManagerID',
                               related_name='subordinates', verbose_name='المدير المباشر')
    emp_status = models.CharField(max_length=30, choices=STATUS_CHOICES, db_column='EmpStatus', default='Active', verbose_name='حالة الموظف')
    termination_date = models.DateField(db_column='TerminationDate', blank=True, null=True, verbose_name='تاريخ إنهاء الخدمة')
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True, verbose_name='ملاحظات')
    photo = models.BinaryField(db_column='Photo', blank=True, null=True, verbose_name='الصورة الشخصية')
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(db_column='UpdatedAt', auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'Employees'
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفون'
        ordering = ['emp_code']
        indexes = [
            models.Index(fields=['emp_status']),
            models.Index(fields=['dept', 'emp_status']),
            models.Index(fields=['branch', 'emp_status']),
            models.Index(fields=['hire_date']),
            models.Index(fields=['manager']),
            models.Index(fields=['emp_code']),
            models.Index(fields=['email']),
            models.Index(fields=['national_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """__str__ function"""
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
    """EmployeeBankAccount class"""
    acc_id = models.AutoField(primary_key=True, db_column='AccID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID',
                           related_name='bank_accounts', verbose_name='الموظف')
    bank = models.ForeignKey('banks.Bank', on_delete=models.SET_NULL, db_column='BankID',
                            blank=True, null=True, related_name='employee_accounts', verbose_name='البنك')
    account_no = models.CharField(max_length=50, db_column='AccountNo', blank=True, null=True, verbose_name='رقم الحساب')
    iban = models.CharField(max_length=50, db_column='IBAN', blank=True, null=True, verbose_name='رقم الآيبان')
    is_primary = models.BooleanField(default=False, verbose_name='الحساب الأساسي')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeBankAccounts'
        verbose_name = 'حساب بنكي'
        verbose_name_plural = 'حسابات الموظفين البنكية'
        ordering = ['-is_primary', 'bank__bank_name']
        indexes = [
            models.Index(fields=['emp', 'is_primary']),
            models.Index(fields=['emp', 'is_active']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.bank.bank_name if self.bank else 'Unknown Bank'}"


class EmployeeDocument(models.Model):
    """EmployeeDocument class"""
    DOCUMENT_TYPES = [
        ('ID', 'بطاقة الهوية'),
        ('PASSPORT', 'جواز السفر'),
        ('CONTRACT', 'عقد العمل'),
        ('CERTIFICATE', 'شهادة'),
        ('MEDICAL', 'تقرير طبي'),
        ('OTHER', 'أخرى'),
    ]

    doc_id = models.AutoField(primary_key=True, db_column='DocID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID',
                           related_name='documents', verbose_name='الموظف')
    doc_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES, db_column='DocType', verbose_name='نوع المستند')
    doc_name = models.CharField(max_length=255, db_column='DocName', blank=True, null=True, verbose_name='اسم المستند')
    file_data = models.BinaryField(db_column='FileData', blank=True, null=True, verbose_name='بيانات الملف')
    file_ext = models.CharField(max_length=10, db_column='FileExt', blank=True, null=True, verbose_name='امتداد الملف')
    upload_date = models.DateTimeField(db_column='UploadDate', auto_now_add=True, verbose_name='تاريخ الرفع')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True, verbose_name='ملاحظات')

    class Meta:
        """Meta class"""
        db_table = 'EmployeeDocuments'
        verbose_name = 'مستند'
        verbose_name_plural = 'مستندات الموظفين'
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['emp', 'doc_type']),
            models.Index(fields=['emp', 'is_active']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        """__str__ function"""
        return f"{self.emp.get_full_name()} - {self.get_doc_type_display()}"

    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            from datetime import date
            return date.today() > self.expiry_date
        return False

    @property
    def days_until_expiry(self):
        """Calculate days until document expires"""
        if self.expiry_date:
            from datetime import date
            delta = self.expiry_date - date.today()
            return delta.days if delta.days > 0 else 0
        return None

# Import extended models for comprehensive HR management
try:
    # TODO: Replace wildcard import
# from .models_extended import specific_items
except ImportError:
    # Extended models not yet available during initial migration
    pass
