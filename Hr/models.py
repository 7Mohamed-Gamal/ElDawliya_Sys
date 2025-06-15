# =============================================================================
# ElDawliya HR Management System - Models
# =============================================================================
# Comprehensive HR management system with modern Django architecture
# Supports RTL Arabic interface and enterprise-level functionality
# =============================================================================

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid


# =============================================================================
# CORE MODELS - Company Structure
# =============================================================================

class Company(models.Model):
    """نموذج الشركة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name=_('اسم الشركة'))
    name_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('كود الشركة'))
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الرقم الضريبي'))
    commercial_register = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('السجل التجاري'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    website = models.URLField(blank=True, null=True, verbose_name=_('الموقع الإلكتروني'))
    logo = models.ImageField(upload_to='company/logos/', blank=True, null=True, verbose_name=_('الشعار'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('شركة')
        verbose_name_plural = _('الشركات')
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(models.Model):
    """نموذج الفرع"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches', verbose_name=_('الشركة'))
    name = models.CharField(max_length=200, verbose_name=_('اسم الفرع'))
    code = models.CharField(max_length=20, verbose_name=_('كود الفرع'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف'))
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_branches', verbose_name=_('مدير الفرع'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('فرع')
        verbose_name_plural = _('الفروع')
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Department(models.Model):
    """نموذج القسم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name=_('الشركة'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments', verbose_name=_('الفرع'))
    name = models.CharField(max_length=200, verbose_name=_('اسم القسم'))
    code = models.CharField(max_length=20, verbose_name=_('كود القسم'))
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='sub_departments', verbose_name=_('القسم الرئيسي'))
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_departments', verbose_name=_('مدير القسم'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_('الميزانية'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('قسم')
        verbose_name_plural = _('الأقسام')
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class JobPosition(models.Model):
    """نموذج المنصب الوظيفي"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_positions', verbose_name=_('الشركة'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='job_positions', verbose_name=_('القسم'))
    title = models.CharField(max_length=200, verbose_name=_('المسمى الوظيفي'))
    title_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('المسمى بالإنجليزية'))
    code = models.CharField(max_length=20, verbose_name=_('كود المنصب'))
    level = models.CharField(max_length=50, choices=[
        ('entry', _('مبتدئ')),
        ('junior', _('مبتدئ متقدم')),
        ('mid', _('متوسط')),
        ('senior', _('كبير')),
        ('lead', _('قائد فريق')),
        ('manager', _('مدير')),
        ('director', _('مدير عام')),
        ('executive', _('تنفيذي'))
    ], default='entry', verbose_name=_('المستوى'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف الوظيفي'))
    requirements = models.TextField(blank=True, null=True, verbose_name=_('المتطلبات'))
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('الحد الأدنى للراتب'))
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('الحد الأقصى للراتب'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('منصب وظيفي')
        verbose_name_plural = _('المناصب الوظيفية')
        unique_together = ['company', 'code']
        ordering = ['company', 'department', 'title']

    def __str__(self):
        return f"{self.department.name} - {self.title}"


# =============================================================================
# EMPLOYEE MANAGEMENT
# =============================================================================

class Employee(models.Model):
    """نموذج الموظف الشامل"""

    # Employee Status Choices
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('on_leave', _('في إجازة')),
        ('terminated', _('منتهي الخدمة')),
        ('suspended', _('موقوف')),
    ]

    GENDER_CHOICES = [
        ('male', _('ذكر')),
        ('female', _('أنثى')),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('تعاقد')),
        ('temporary', _('مؤقت')),
        ('intern', _('متدرب')),
    ]

    # Primary Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=20, unique=True, verbose_name=_('رقم الموظف'))

    # Personal Information
    first_name = models.CharField(max_length=100, verbose_name=_('الاسم الأول'))
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم الأوسط'))
    last_name = models.CharField(max_length=100, verbose_name=_('اسم العائلة'))
    full_name = models.CharField(max_length=300, blank=True, verbose_name=_('الاسم الكامل'))
    name_english = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))

    # Contact Information
    email = models.EmailField(unique=True, verbose_name=_('البريد الإلكتروني'))
    phone_primary = models.CharField(max_length=20, verbose_name=_('الهاتف الأساسي'))
    phone_secondary = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف الثانوي'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))

    # Personal Details
    national_id = models.CharField(max_length=20, unique=True, verbose_name=_('رقم الهوية'))
    passport_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم جواز السفر'))
    date_of_birth = models.DateField(verbose_name=_('تاريخ الميلاد'))
    place_of_birth = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('مكان الميلاد'))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name=_('الجنس'))
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, verbose_name=_('الحالة الاجتماعية'))
    nationality = models.CharField(max_length=50, verbose_name=_('الجنسية'))
    religion = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الديانة'))

    # Employment Information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', verbose_name=_('الشركة'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='employees', verbose_name=_('الفرع'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees', verbose_name=_('القسم'))
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='employees', verbose_name=_('المنصب'))
    direct_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='subordinates', verbose_name=_('المدير المباشر'))

    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, verbose_name=_('نوع التوظيف'))
    hire_date = models.DateField(verbose_name=_('تاريخ التوظيف'))
    probation_end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء فترة التجربة'))
    contract_start_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ بداية العقد'))
    contract_end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء العقد'))
    termination_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الخدمة'))
    termination_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب انتهاء الخدمة'))

    # Status and Settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('الحالة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))

    # Media
    photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True, verbose_name=_('الصورة الشخصية'))

    # System Fields
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT,
                                  related_name='created_employees', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    # Notes field (as requested by user)
    notes = models.TextField(null=True, blank=True, verbose_name=_('ملاحظات'))

    class Meta:
        verbose_name = _('موظف')
        verbose_name_plural = _('الموظفون')
        ordering = ['employee_number']
        indexes = [
            models.Index(fields=['employee_number']),
            models.Index(fields=['email']),
            models.Index(fields=['national_id']),
            models.Index(fields=['status']),
            models.Index(fields=['company', 'department']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate full name
        if not self.full_name:
            name_parts = [self.first_name]
            if self.middle_name:
                name_parts.append(self.middle_name)
            name_parts.append(self.last_name)
            self.full_name = ' '.join(name_parts)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_number} - {self.full_name}"

    @property
    def age(self):
        """حساب العمر"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def years_of_service(self):
        """حساب سنوات الخدمة"""
        from datetime import date
        today = date.today()
        return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))


# =============================================================================
# ATTENDANCE & TIME TRACKING
# =============================================================================

class WorkShift(models.Model):
    """نموذج الوردية"""
    SHIFT_TYPE_CHOICES = [
        ('fixed', _('ثابتة')),
        ('flexible', _('مرنة')),
        ('rotating', _('متناوبة')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='work_shifts', verbose_name=_('الشركة'))
    name = models.CharField(max_length=100, verbose_name=_('اسم الوردية'))
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES, verbose_name=_('نوع الوردية'))
    start_time = models.TimeField(verbose_name=_('وقت البداية'))
    end_time = models.TimeField(verbose_name=_('وقت النهاية'))
    break_duration = models.DurationField(blank=True, null=True, verbose_name=_('مدة الاستراحة'))
    grace_period_minutes = models.PositiveIntegerField(default=15, verbose_name=_('فترة السماح بالدقائق'))
    overtime_threshold_minutes = models.PositiveIntegerField(default=30, verbose_name=_('حد الوقت الإضافي بالدقائق'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('وردية عمل')
        verbose_name_plural = _('ورديات العمل')
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class AttendanceMachine(models.Model):
    """نموذج جهاز الحضور"""
    MACHINE_TYPE_CHOICES = [
        ('fingerprint', _('بصمة')),
        ('face', _('تعرف على الوجه')),
        ('card', _('كارت')),
        ('mobile', _('تطبيق الجوال')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_machines', verbose_name=_('الشركة'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='attendance_machines', verbose_name=_('الفرع'))
    name = models.CharField(max_length=100, verbose_name=_('اسم الجهاز'))
    machine_type = models.CharField(max_length=20, choices=MACHINE_TYPE_CHOICES, verbose_name=_('نوع الجهاز'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('عنوان IP'))
    port = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('المنفذ'))
    location = models.CharField(max_length=200, verbose_name=_('الموقع'))
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الرقم التسلسلي'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    last_sync = models.DateTimeField(blank=True, null=True, verbose_name=_('آخر مزامنة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('جهاز حضور')
        verbose_name_plural = _('أجهزة الحضور')
        ordering = ['company', 'branch', 'name']

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class EmployeeShiftAssignment(models.Model):
    """نموذج تعيين الوردية للموظف"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift_assignments', verbose_name=_('الموظف'))
    work_shift = models.ForeignKey(WorkShift, on_delete=models.CASCADE, related_name='employee_assignments', verbose_name=_('الوردية'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ النهاية'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تعيين وردية موظف')
        verbose_name_plural = _('تعيينات ورديات الموظفين')
        ordering = ['employee', '-start_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.work_shift.name}"


class AttendanceRecord(models.Model):
    """نموذج سجل الحضور"""
    ATTENDANCE_TYPE_CHOICES = [
        ('check_in', _('دخول')),
        ('check_out', _('خروج')),
        ('break_start', _('بداية استراحة')),
        ('break_end', _('نهاية استراحة')),
    ]

    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('late', _('متأخر')),
        ('early_leave', _('انصراف مبكر')),
        ('absent', _('غائب')),
        ('overtime', _('وقت إضافي')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records', verbose_name=_('الموظف'))
    machine = models.ForeignKey(AttendanceMachine, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='attendance_records', verbose_name=_('جهاز الحضور'))
    date = models.DateField(verbose_name=_('التاريخ'))
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES, verbose_name=_('نوع الحضور'))
    timestamp = models.DateTimeField(verbose_name=_('وقت التسجيل'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name=_('الحالة'))
    late_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق التأخير'))
    overtime_minutes = models.PositiveIntegerField(default=0, verbose_name=_('دقائق الوقت الإضافي'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    is_manual = models.BooleanField(default=False, verbose_name=_('يدوي'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('سجل حضور')
        verbose_name_plural = _('سجلات الحضور')
        ordering = ['employee', '-date', '-timestamp']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_attendance_type_display()}"


# =============================================================================
# LEAVE MANAGEMENT
# =============================================================================

class LeaveType(models.Model):
    """نموذج نوع الإجازة"""
    CALCULATION_TYPE_CHOICES = [
        ('days', _('أيام')),
        ('hours', _('ساعات')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='leave_types', verbose_name=_('الشركة'))
    name = models.CharField(max_length=100, verbose_name=_('اسم نوع الإجازة'))
    code = models.CharField(max_length=20, verbose_name=_('كود نوع الإجازة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    calculation_type = models.CharField(max_length=10, choices=CALCULATION_TYPE_CHOICES, default='days', verbose_name=_('نوع الحساب'))
    max_days_per_year = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأقصى للأيام في السنة'))
    max_consecutive_days = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأقصى للأيام المتتالية'))
    min_notice_days = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأدنى لأيام الإشعار المسبق'))
    is_paid = models.BooleanField(default=True, verbose_name=_('مدفوعة الأجر'))
    affects_attendance = models.BooleanField(default=True, verbose_name=_('تؤثر على الحضور'))
    carry_forward = models.BooleanField(default=False, verbose_name=_('قابلة للترحيل'))
    requires_approval = models.BooleanField(default=True, verbose_name=_('تتطلب موافقة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('نوع الإجازة')
        verbose_name_plural = _('أنواع الإجازات')
        unique_together = ['company', 'code']
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class EmployeeLeaveBalance(models.Model):
    """نموذج رصيد إجازات الموظف"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='employee_balances', verbose_name=_('نوع الإجازة'))
    year = models.PositiveIntegerField(verbose_name=_('السنة'))
    allocated_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الأيام المخصصة'))
    used_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الأيام المستخدمة'))
    remaining_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الأيام المتبقية'))
    carried_forward = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الأيام المرحلة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('رصيد إجازات موظف')
        verbose_name_plural = _('أرصدة إجازات الموظفين')
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['employee', 'year', 'leave_type']

    def save(self, *args, **kwargs):
        # Auto-calculate remaining days
        self.remaining_days = self.allocated_days + self.carried_forward - self.used_days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.year}"


class LeaveRequest(models.Model):
    """نموذج طلب الإجازة"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مقدم')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغى')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='leave_requests', verbose_name=_('نوع الإجازة'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    days_requested = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('عدد الأيام المطلوبة'))
    reason = models.TextField(verbose_name=_('السبب'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))

    # Approval workflow
    approved_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_leave_requests', verbose_name=_('تمت الموافقة بواسطة'))
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الموافقة'))
    rejection_reason = models.TextField(null=True, blank=True, verbose_name=_('سبب الرفض'))

    # Additional information
    emergency_contact = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('جهة الاتصال في حالة الطوارئ'))
    replacement_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='replacement_requests', verbose_name=_('الموظف البديل'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('ملاحظات'))

    # System fields
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('طلب إجازة')
        verbose_name_plural = _('طلبات الإجازات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate days requested
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.days_requested = Decimal(str(delta.days + 1))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"


# =============================================================================
# PAYROLL SYSTEM
# =============================================================================

class SalaryComponent(models.Model):
    """نموذج مكونات الراتب"""
    COMPONENT_TYPE_CHOICES = [
        ('basic', _('راتب أساسي')),
        ('allowance', _('بدل')),
        ('bonus', _('مكافأة')),
        ('deduction', _('خصم')),
        ('overtime', _('وقت إضافي')),
        ('commission', _('عمولة')),
    ]

    CALCULATION_METHOD_CHOICES = [
        ('fixed', _('مبلغ ثابت')),
        ('percentage', _('نسبة مئوية')),
        ('hourly', _('بالساعة')),
        ('daily', _('يومي')),
        ('formula', _('معادلة')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='salary_components', verbose_name=_('الشركة'))
    name = models.CharField(max_length=100, verbose_name=_('اسم المكون'))
    code = models.CharField(max_length=20, verbose_name=_('كود المكون'))
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES, verbose_name=_('نوع المكون'))
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHOD_CHOICES, verbose_name=_('طريقة الحساب'))
    default_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('القيمة الافتراضية'))
    is_taxable = models.BooleanField(default=True, verbose_name=_('خاضع للضريبة'))
    affects_overtime = models.BooleanField(default=False, verbose_name=_('يؤثر على الوقت الإضافي'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    formula = models.TextField(blank=True, null=True, verbose_name=_('المعادلة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('مكون راتب')
        verbose_name_plural = _('مكونات الرواتب')
        unique_together = ['company', 'code']
        ordering = ['company', 'component_type', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class EmployeeSalaryStructure(models.Model):
    """نموذج هيكل راتب الموظف"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_structures', verbose_name=_('الموظف'))
    salary_component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE, related_name='employee_structures', verbose_name=_('مكون الراتب'))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('المبلغ'))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_('النسبة المئوية'))
    effective_date = models.DateField(verbose_name=_('تاريخ السريان'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('هيكل راتب موظف')
        verbose_name_plural = _('هياكل رواتب الموظفين')
        ordering = ['employee', 'salary_component']

    def __str__(self):
        return f"{self.employee.full_name} - {self.salary_component.name}"


class PayrollPeriod(models.Model):
    """نموذج فترة الراتب"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('processing', _('قيد المعالجة')),
        ('calculated', _('محسوب')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
        ('closed', _('مغلق')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payroll_periods', verbose_name=_('الشركة'))
    name = models.CharField(max_length=100, verbose_name=_('اسم الفترة'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    pay_date = models.DateField(verbose_name=_('تاريخ الدفع'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    total_gross = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي الراتب الإجمالي'))
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي الخصومات'))
    total_net = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي الراتب الصافي'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('فترة راتب')
        verbose_name_plural = _('فترات الرواتب')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class PayrollEntry(models.Model):
    """نموذج سجل الراتب"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('calculated', _('محسوب')),
        ('approved', _('معتمد')),
        ('paid', _('مدفوع')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payroll_entries', verbose_name=_('فترة الراتب'))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_entries', verbose_name=_('الموظف'))
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الراتب الأساسي'))
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي البدلات'))
    total_bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي المكافآت'))
    overtime_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('مبلغ الوقت الإضافي'))
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الراتب الإجمالي'))
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي الخصومات'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('مبلغ الضريبة'))
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('مبلغ التأمين'))
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الراتب الصافي'))
    working_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام العمل'))
    present_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الحضور'))
    absent_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الغياب'))
    leave_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الإجازة'))
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('ساعات الوقت الإضافي'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('سجل راتب')
        verbose_name_plural = _('سجلات الرواتب')
        unique_together = ['payroll_period', 'employee']
        ordering = ['payroll_period', 'employee']

    def save(self, *args, **kwargs):
        # Auto-calculate totals
        self.gross_salary = self.basic_salary + self.total_allowances + self.total_bonuses + self.overtime_amount
        self.net_salary = self.gross_salary - self.total_deductions - self.tax_amount - self.insurance_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period.name}"


# =============================================================================
# PERFORMANCE MANAGEMENT
# =============================================================================

class EvaluationCriteria(models.Model):
    """نموذج معايير التقييم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='evaluation_criteria', verbose_name=_('الشركة'))
    name = models.CharField(max_length=200, verbose_name=_('اسم المعيار'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'),
                                validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))],
                                verbose_name=_('الوزن النسبي'))
    max_score = models.PositiveIntegerField(default=5, verbose_name=_('أقصى درجة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('معيار تقييم')
        verbose_name_plural = _('معايير التقييم')
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class PerformanceEvaluation(models.Model):
    """نموذج تقييم الأداء"""
    EVALUATION_TYPE_CHOICES = [
        ('annual', _('سنوي')),
        ('semi_annual', _('نصف سنوي')),
        ('quarterly', _('ربع سنوي')),
        ('probation', _('فترة تجربة')),
        ('project', _('مشروع')),
        ('promotion', _('ترقية')),
    ]

    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('approved', _('معتمد')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_evaluations', verbose_name=_('الموظف'))
    evaluator = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, related_name='conducted_evaluations', verbose_name=_('المقيم'))
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES, verbose_name=_('نوع التقييم'))
    evaluation_period_start = models.DateField(verbose_name=_('بداية فترة التقييم'))
    evaluation_period_end = models.DateField(verbose_name=_('نهاية فترة التقييم'))
    evaluation_date = models.DateField(verbose_name=_('تاريخ التقييم'))
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الدرجة الإجمالية'))
    overall_rating = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('التقدير الإجمالي'))
    strengths = models.TextField(blank=True, null=True, verbose_name=_('نقاط القوة'))
    areas_for_improvement = models.TextField(blank=True, null=True, verbose_name=_('مجالات التحسين'))
    goals_for_next_period = models.TextField(blank=True, null=True, verbose_name=_('أهداف الفترة القادمة'))
    employee_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات الموظف'))
    evaluator_comments = models.TextField(blank=True, null=True, verbose_name=_('تعليقات المقيم'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    approved_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_evaluations', verbose_name=_('تمت الموافقة بواسطة'))
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الموافقة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تقييم أداء')
        verbose_name_plural = _('تقييمات الأداء')
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_evaluation_type_display()} - {self.evaluation_date}"


class EvaluationScore(models.Model):
    """نموذج درجات التقييم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.ForeignKey(PerformanceEvaluation, on_delete=models.CASCADE, related_name='scores', verbose_name=_('التقييم'))
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE, verbose_name=_('المعيار'))
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('الدرجة'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('التعليقات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        verbose_name = _('درجة تقييم')
        verbose_name_plural = _('درجات التقييم')
        unique_together = ['evaluation', 'criteria']

    def __str__(self):
        return f"{self.evaluation.employee.full_name} - {self.criteria.name} - {self.score}"


# =============================================================================
# EMPLOYEE NOTES & DOCUMENTATION
# =============================================================================

class EmployeeNote(models.Model):
    """نموذج ملاحظات الموظف"""
    NOTE_TYPE_CHOICES = [
        ('positive', _('إيجابية')),
        ('negative', _('سلبية')),
        ('general', _('عامة')),
        ('disciplinary', _('تأديبية')),
        ('achievement', _('إنجاز')),
        ('warning', _('تحذير')),
    ]

    VISIBILITY_CHOICES = [
        ('private', _('خاص')),
        ('hr_only', _('الموارد البشرية فقط')),
        ('manager', _('المدير')),
        ('public', _('عام')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notes', verbose_name=_('الموظف'))
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, verbose_name=_('نوع الملاحظة'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    content = models.TextField(verbose_name=_('المحتوى'))
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='hr_only', verbose_name=_('مستوى الرؤية'))
    is_important = models.BooleanField(default=False, verbose_name=_('مهم'))
    follow_up_required = models.BooleanField(default=False, verbose_name=_('يتطلب متابعة'))
    follow_up_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ المتابعة'))
    attachments = models.FileField(upload_to='employee_notes/', blank=True, null=True, verbose_name=_('المرفقات'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('ملاحظة موظف')
        verbose_name_plural = _('ملاحظات الموظفين')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"


# =============================================================================
# ADDITIONAL HR MODELS
# =============================================================================

class EmployeeDocument(models.Model):
    """نموذج وثائق الموظف"""
    DOCUMENT_TYPE_CHOICES = [
        ('id_copy', _('صورة الهوية')),
        ('passport', _('جواز السفر')),
        ('contract', _('عقد العمل')),
        ('cv', _('السيرة الذاتية')),
        ('certificate', _('شهادة')),
        ('medical', _('تقرير طبي')),
        ('insurance', _('وثيقة تأمين')),
        ('other', _('أخرى')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents', verbose_name=_('الموظف'))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name=_('نوع الوثيقة'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    file = models.FileField(upload_to='employee_documents/', verbose_name=_('الملف'))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verified_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='verified_documents', verbose_name=_('تم التحقق بواسطة'))
    verification_date = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ التحقق'))
    uploaded_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الرفع بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('وثيقة موظف')
        verbose_name_plural = _('وثائق الموظفين')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"


class HolidayCalendar(models.Model):
    """نموذج تقويم العطل الرسمية"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holidays', verbose_name=_('الشركة'))
    name = models.CharField(max_length=200, verbose_name=_('اسم العطلة'))
    date = models.DateField(verbose_name=_('التاريخ'))
    is_recurring = models.BooleanField(default=False, verbose_name=_('متكررة سنوياً'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('عطلة رسمية')
        verbose_name_plural = _('العطل الرسمية')
        unique_together = ['company', 'name', 'date']
        ordering = ['date']

    def __str__(self):
        return f"{self.company.name} - {self.name} - {self.date}"


class EmployeeEmergencyContact(models.Model):
    """نموذج جهات الاتصال في حالات الطوارئ"""
    RELATIONSHIP_CHOICES = [
        ('spouse', _('زوج/زوجة')),
        ('parent', _('والد/والدة')),
        ('sibling', _('أخ/أخت')),
        ('child', _('ابن/ابنة')),
        ('friend', _('صديق')),
        ('other', _('أخرى')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='emergency_contacts', verbose_name=_('الموظف'))
    name = models.CharField(max_length=200, verbose_name=_('الاسم'))
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, verbose_name=_('صلة القرابة'))
    phone_primary = models.CharField(max_length=20, verbose_name=_('الهاتف الأساسي'))
    phone_secondary = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الهاتف الثانوي'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    is_primary = models.BooleanField(default=False, verbose_name=_('جهة الاتصال الأساسية'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('جهة اتصال طوارئ')
        verbose_name_plural = _('جهات اتصال الطوارئ')
        ordering = ['employee', '-is_primary', 'name']

    def __str__(self):
        return f"{self.employee.full_name} - {self.name}"


class EmployeeTraining(models.Model):
    """نموذج تدريب الموظفين"""
    STATUS_CHOICES = [
        ('planned', _('مخطط')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغى')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='trainings', verbose_name=_('الموظف'))
    training_title = models.CharField(max_length=200, verbose_name=_('عنوان التدريب'))
    training_provider = models.CharField(max_length=200, verbose_name=_('مقدم التدريب'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    duration_hours = models.PositiveIntegerField(verbose_name=_('مدة التدريب بالساعات'))
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('التكلفة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name=_('الحالة'))
    completion_certificate = models.FileField(upload_to='training_certificates/', blank=True, null=True, verbose_name=_('شهادة الإكمال'))
    grade = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('الدرجة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تدريب موظف')
        verbose_name_plural = _('تدريبات الموظفين')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.training_title}"


# =============================================================================
# HR ANALYTICS & REPORTING
# =============================================================================

class EmployeeAnalytics(models.Model):
    """نموذج تحليلات الموظف"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='analytics', verbose_name=_('الموظف'))
    year = models.PositiveIntegerField(verbose_name=_('السنة'))
    month = models.PositiveIntegerField(verbose_name=_('الشهر'))

    # Attendance Analytics
    total_working_days = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي أيام العمل'))
    days_present = models.PositiveIntegerField(default=0, verbose_name=_('أيام الحضور'))
    days_absent = models.PositiveIntegerField(default=0, verbose_name=_('أيام الغياب'))
    days_late = models.PositiveIntegerField(default=0, verbose_name=_('أيام التأخير'))
    total_late_minutes = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي دقائق التأخير'))
    total_overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي ساعات الوقت الإضافي'))

    # Leave Analytics
    total_leave_days = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي أيام الإجازة'))
    sick_leave_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الإجازة المرضية'))
    annual_leave_days = models.PositiveIntegerField(default=0, verbose_name=_('أيام الإجازة السنوية'))

    # Performance Analytics
    average_evaluation_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_('متوسط درجة التقييم'))
    completed_trainings = models.PositiveIntegerField(default=0, verbose_name=_('التدريبات المكتملة'))

    # Payroll Analytics
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الراتب الإجمالي'))
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('الراتب الصافي'))
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('إجمالي الخصومات'))
    overtime_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('مبلغ الوقت الإضافي'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تحليلات موظف')
        verbose_name_plural = _('تحليلات الموظفين')
        unique_together = ['employee', 'year', 'month']
        ordering = ['employee', '-year', '-month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}/{self.month}"


# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

class HRSystemSettings(models.Model):
    """نموذج إعدادات نظام الموارد البشرية"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='hr_settings', verbose_name=_('الشركة'))

    # Working Hours Settings
    default_working_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('8.00'), verbose_name=_('ساعات العمل الافتراضية في اليوم'))
    default_working_days_per_week = models.PositiveIntegerField(default=5, verbose_name=_('أيام العمل الافتراضية في الأسبوع'))
    weekend_days = models.CharField(max_length=20, default='friday,saturday', verbose_name=_('أيام نهاية الأسبوع'))

    # Leave Settings
    annual_leave_days = models.PositiveIntegerField(default=21, verbose_name=_('أيام الإجازة السنوية'))
    sick_leave_days = models.PositiveIntegerField(default=15, verbose_name=_('أيام الإجازة المرضية'))
    maternity_leave_days = models.PositiveIntegerField(default=90, verbose_name=_('أيام إجازة الأمومة'))
    paternity_leave_days = models.PositiveIntegerField(default=3, verbose_name=_('أيام إجازة الأبوة'))

    # Attendance Settings
    late_grace_period_minutes = models.PositiveIntegerField(default=15, verbose_name=_('فترة السماح للتأخير بالدقائق'))
    overtime_threshold_minutes = models.PositiveIntegerField(default=30, verbose_name=_('حد الوقت الإضافي بالدقائق'))
    auto_calculate_overtime = models.BooleanField(default=True, verbose_name=_('حساب الوقت الإضافي تلقائياً'))

    # Payroll Settings
    payroll_frequency = models.CharField(max_length=20, choices=[
        ('monthly', _('شهري')),
        ('bi_weekly', _('كل أسبوعين')),
        ('weekly', _('أسبوعي')),
    ], default='monthly', verbose_name=_('تكرار الراتب'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('معدل الضريبة'))
    insurance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('معدل التأمين'))

    # Notification Settings
    send_birthday_notifications = models.BooleanField(default=True, verbose_name=_('إرسال تنبيهات أعياد الميلاد'))
    send_contract_expiry_notifications = models.BooleanField(default=True, verbose_name=_('إرسال تنبيهات انتهاء العقود'))
    contract_expiry_notification_days = models.PositiveIntegerField(default=30, verbose_name=_('أيام تنبيه انتهاء العقد'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('إعدادات نظام الموارد البشرية')
        verbose_name_plural = _('إعدادات أنظمة الموارد البشرية')

    def __str__(self):
        return f"إعدادات الموارد البشرية - {self.company.name}"


# =============================================================================
# AUDIT TRAIL
# =============================================================================

class HRAuditLog(models.Model):
    """نموذج سجل التدقيق للموارد البشرية"""
    ACTION_CHOICES = [
        ('create', _('إنشاء')),
        ('update', _('تحديث')),
        ('delete', _('حذف')),
        ('approve', _('موافقة')),
        ('reject', _('رفض')),
        ('calculate', _('حساب')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('المستخدم'))
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_('الإجراء'))
    model_name = models.CharField(max_length=100, verbose_name=_('اسم النموذج'))
    object_id = models.CharField(max_length=100, verbose_name=_('معرف الكائن'))
    object_repr = models.CharField(max_length=200, verbose_name=_('تمثيل الكائن'))
    changes = models.JSONField(blank=True, null=True, verbose_name=_('التغييرات'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('عنوان IP'))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_('وكيل المستخدم'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('الوقت'))

    class Meta:
        verbose_name = _('سجل تدقيق الموارد البشرية')
        verbose_name_plural = _('سجلات تدقيق الموارد البشرية')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.model_name} - {self.timestamp}"
