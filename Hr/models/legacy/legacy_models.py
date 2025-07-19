"""
Legacy Models for HRMS
Contains backward compatibility models with original table structures
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class LegacyDepartment(models.Model):
    """Legacy Department model for backward compatibility"""
    dept_code = models.IntegerField(primary_key=True, verbose_name=_("رمز القسم"))
    dept_name = models.CharField(max_length=250, verbose_name=_("اسم القسم"))
    manager_id = models.IntegerField(null=True, blank=True, verbose_name=_("كود مدير القسم"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    note = models.TextField(null=True, blank=True, verbose_name=_("ملاحظات"))

    def __str__(self):
        return self.dept_name or ''

    class Meta:
        managed = True
        db_table = 'Tbl_Department'
        verbose_name = _("القسم (قديم)")
        verbose_name_plural = _("الأقسام (قديمة)")


class Job(models.Model):
    """Legacy Job model - matches actual Tbl_Jop table structure"""
    jop_code = models.IntegerField(
        db_column='Jop_Code',
        primary_key=True,
        verbose_name=_("رمز الوظيفة")
    )
    jop_name = models.CharField(
        db_column='Jop_Name',
        max_length=50,
        verbose_name=_("اسم الوظيفة")
    )
    department = models.ForeignKey(
        'LegacyDepartment',
        db_column='Dept_Code',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )

    def __str__(self):
        return self.jop_name or ''

    class Meta:
        managed = True
        db_table = 'Tbl_Jop'
        verbose_name = _("الوظيفة")
        verbose_name_plural = _("الوظائف")


class JobInsurance(models.Model):
    """Legacy Job Insurance model"""
    job_code_insurance = models.IntegerField(primary_key=True, verbose_name=_("رمز وظيفة التأمين"))
    job_name_insurance = models.CharField(max_length=250, verbose_name=_("اسم وظيفة التأمين"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    note = models.TextField(null=True, blank=True, verbose_name=_("ملاحظات"))

    def __str__(self):
        return self.job_name_insurance or ''

    class Meta:
        managed = True
        db_table = 'Tbl_Job_Insurance'
        verbose_name = _("وظيفة التأمين")
        verbose_name_plural = _("وظائف التأمين")


class Car(models.Model):
    """Legacy Car model"""
    car_id = models.CharField(max_length=50, primary_key=True, verbose_name=_("رقم السيارة"))
    car_name = models.CharField(max_length=250, verbose_name=_("اسم السيارة"))
    car_type = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("نوع السيارة"))
    supplier = models.CharField(max_length=250, null=True, blank=True, verbose_name=_("المورد"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    note = models.TextField(null=True, blank=True, verbose_name=_("ملاحظات"))

    def __str__(self):
        return f"{self.car_name} ({self.car_id})"

    class Meta:
        managed = True
        db_table = 'Tbl_Car'
        verbose_name = _("السيارة")
        verbose_name_plural = _("السيارات")


class SalaryItem(models.Model):
    """Legacy Salary Item model"""
    item_code = models.CharField(max_length=50, primary_key=True, verbose_name=_("رمز البند"))
    name = models.CharField(max_length=250, verbose_name=_("اسم البند"))
    type = models.CharField(max_length=50, verbose_name=_("نوع البند"))
    default_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("القيمة الافتراضية"))
    is_auto_applied = models.BooleanField(default=False, verbose_name=_("تطبيق تلقائي"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'Tbl_Salary_Item'
        verbose_name = _("بند الراتب")
        verbose_name_plural = _("بنود الرواتب")


class EmployeeSalaryItem(models.Model):
    """Legacy Employee Salary Item model"""
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, verbose_name=_("بند الراتب"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ"))
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ النهاية"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Salary_Item'
        verbose_name = _("بند راتب الموظف")
        verbose_name_plural = _("بنود رواتب الموظفين")


class AttendanceRule(models.Model):
    """Legacy Attendance Rule model"""
    name = models.CharField(max_length=250, verbose_name=_("اسم القاعدة"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'Tbl_Attendance_Rule'
        verbose_name = _("قاعدة الحضور")
        verbose_name_plural = _("قواعد الحضور")


class EmployeeAttendanceRule(models.Model):
    """Legacy Employee Attendance Rule model"""
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    attendance_rule = models.ForeignKey(AttendanceRule, on_delete=models.CASCADE, verbose_name=_("قاعدة الحضور"))
    effective_date = models.DateField(verbose_name=_("تاريخ السريان"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Attendance_Rule'
        verbose_name = _("قاعدة حضور الموظف")
        verbose_name_plural = _("قواعد حضور الموظفين")


class OfficialHoliday(models.Model):
    """Legacy Official Holiday model"""
    name = models.CharField(max_length=250, verbose_name=_("اسم العطلة"))
    date = models.DateField(verbose_name=_("التاريخ"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        managed = True
        db_table = 'Tbl_Official_Holiday'
        verbose_name = _("العطلة الرسمية")
        verbose_name_plural = _("العطل الرسمية")


class LegacyPayrollPeriod(models.Model):
    """Legacy Payroll Period model"""
    period = models.CharField(max_length=50, verbose_name=_("الفترة"))
    status = models.CharField(max_length=50, verbose_name=_("الحالة"))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("إجمالي المبلغ"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_legacy_payroll_periods', verbose_name=_("أنشئ بواسطة"))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_legacy_payroll_periods', verbose_name=_("اعتمد بواسطة"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    def __str__(self):
        return self.period

    class Meta:
        managed = True
        db_table = 'Tbl_Payroll_Period'
        verbose_name = _("فترة الرواتب القديمة")
        verbose_name_plural = _("فترات الرواتب القديمة")


class LegacyPayrollEntry(models.Model):
    """Legacy Payroll Entry model"""
    period = models.ForeignKey(LegacyPayrollPeriod, on_delete=models.CASCADE, verbose_name=_("الفترة"))
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("إجمالي المبلغ"))
    status = models.CharField(max_length=50, verbose_name=_("الحالة"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        managed = True
        db_table = 'Tbl_Payroll_Entry'
        verbose_name = _("قيد الراتب (قديم)")
        verbose_name_plural = _("قيود الرواتب (قديمة)")


class PayrollItemDetail(models.Model):
    """Legacy Payroll Item Detail model"""
    payroll_entry = models.ForeignKey(LegacyPayrollEntry, on_delete=models.CASCADE, verbose_name=_("قيد الراتب"))
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, verbose_name=_("بند الراتب"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ"))

    class Meta:
        managed = True
        db_table = 'Tbl_Payroll_Item_Detail'
        verbose_name = _("تفاصيل بند الراتب")
        verbose_name_plural = _("تفاصيل بنود الرواتب")


class PickupPoint(models.Model):
    """Legacy Pickup Point model"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_("السيارة"))
    location = models.CharField(max_length=250, verbose_name=_("الموقع"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))

    def __str__(self):
        return f"{self.car} - {self.location}"

    class Meta:
        managed = True
        db_table = 'Tbl_Pickup_Point'
        verbose_name = _("نقطة الالتقاط")
        verbose_name_plural = _("نقاط الالتقاط")


class EmployeeTask(models.Model):
    """Legacy Employee Task model"""
    title = models.CharField(max_length=250, verbose_name=_("العنوان"))
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("أسند بواسطة"))
    due_date = models.DateField(verbose_name=_("تاريخ الاستحقاق"))
    status = models.CharField(max_length=50, verbose_name=_("الحالة"))
    priority = models.CharField(max_length=50, verbose_name=_("الأولوية"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))

    def __str__(self):
        return self.title

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Task'
        verbose_name = _("مهمة الموظف")
        verbose_name_plural = _("مهام الموظفين")


class EmployeeNote(models.Model):
    """Legacy Employee Note model"""
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    title = models.CharField(max_length=250, verbose_name=_("العنوان"))
    content = models.TextField(verbose_name=_("المحتوى"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("أنشئ بواسطة"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    def __str__(self):
        return self.title

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Note'
        verbose_name = _("ملاحظة الموظف")
        verbose_name_plural = _("ملاحظات الموظفين")


class EmployeeNoteHistory(models.Model):
    """Legacy Employee Note History model"""
    note = models.ForeignKey(EmployeeNote, on_delete=models.CASCADE, verbose_name=_("الملاحظة"))
    old_content = models.TextField(verbose_name=_("المحتوى القديم"))
    new_content = models.TextField(verbose_name=_("المحتوى الجديد"))
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("غير بواسطة"))
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ التغيير"))

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Note_History'
        verbose_name = _("تاريخ ملاحظة الموظف")
        verbose_name_plural = _("تاريخ ملاحظات الموظفين")


class EmployeeFile(models.Model):
    """Legacy Employee File model"""
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    title = models.CharField(max_length=250, verbose_name=_("العنوان"))
    file = models.FileField(upload_to='employee_files/', verbose_name=_("الملف"))
    file_type = models.CharField(max_length=50, verbose_name=_("نوع الملف"))
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("رفع بواسطة"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    def __str__(self):
        return self.title

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_File'
        verbose_name = _("ملف الموظف")
        verbose_name_plural = _("ملفات الموظفين")


class HrTask(models.Model):
    """Legacy HR Task model"""
    title = models.CharField(max_length=250, verbose_name=_("العنوان"))
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("أسند إلى"))
    due_date = models.DateField(verbose_name=_("تاريخ الاستحقاق"))
    status = models.CharField(max_length=50, verbose_name=_("الحالة"))
    priority = models.CharField(max_length=50, verbose_name=_("الأولوية"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))

    def __str__(self):
        return self.title

    class Meta:
        managed = True
        db_table = 'Tbl_Hr_Task'
        verbose_name = _("مهمة الموارد البشرية")
        verbose_name_plural = _("مهام الموارد البشرية")


class EmployeeLeave(models.Model):
    """Legacy Employee Leave model"""
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    leave_type = models.ForeignKey('LeaveType', on_delete=models.CASCADE, verbose_name=_("نوع الإجازة"))
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(verbose_name=_("تاريخ النهاية"))
    reason = models.TextField(verbose_name=_("السبب"))
    status = models.CharField(max_length=50, verbose_name=_("الحالة"))

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Leave'
        verbose_name = _("إجازة الموظف")
        verbose_name_plural = _("إجازات الموظفين")


class EmployeeEvaluation(models.Model):
    """Legacy Employee Evaluation model"""
    employee = models.ForeignKey('Hr.Employee', on_delete=models.CASCADE, verbose_name=_("الموظف"))
    evaluation_date = models.DateField(verbose_name=_("تاريخ التقييم"))
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("المقيم"))
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, verbose_name=_("التقييم العام"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("التعليقات"))

    def __str__(self):
        return f"{self.employee} - {self.evaluation_date}"

    class Meta:
        managed = True
        db_table = 'Tbl_Employee_Evaluation'
        verbose_name = _("تقييم الموظف")
        verbose_name_plural = _("تقييمات الموظفين")


# HrJob model moved from job_models.py
class HrJob(models.Model):
    """Legacy HrJob model - matches Tbl_Jop table structure with original field names"""
    jop_code = models.IntegerField(  # اسم الحقل: jop_code (بالإنجليزية o)
        db_column='Jop_Code', 
        primary_key=True,
        verbose_name=_("رمز الوظيفة")
    )
    jop_name = models.CharField(
        db_column='Jop_Name',
        max_length=50,
        verbose_name=_("اسم الوظيفة")
    )
    department = models.ForeignKey(
        LegacyDepartment,
        db_column='Dept_Code',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )

    def __str__(self):
        return self.jop_name or ''

    class Meta:
        managed = True  # Changed to True to manage this model in the legacy namespace
        db_table = 'Tbl_Jop'
        verbose_name = _("الوظيفة (قديم)")
        verbose_name_plural = _("الوظائف (قديمة)")

# Note: All employee references now point to Hr.Employee model
