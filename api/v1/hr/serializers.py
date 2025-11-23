"""
HR API Serializers
مسلسلات API الموارد البشرية
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

# Import HR models (these will be created in the HR services implementation)
# from apps.hr.models import Employee, Department, JobPosition, Attendance, Leave, Payroll, Evaluation

User = get_user_model()


class DepartmentSerializer(serializers.Serializer):
    """
    Serializer for Department model
    مسلسل نموذج القسم
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    name_ar = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    manager_name = serializers.CharField(read_only=True)
    employee_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)


class JobPositionSerializer(serializers.Serializer):
    """
    Serializer for JobPosition model
    مسلسل نموذج المنصب الوظيفي
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    title_ar = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    department_id = serializers.IntegerField()
    department_name = serializers.CharField(read_only=True)
    level = serializers.CharField(max_length=50, required=False)
    min_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)


class EmployeeSerializer(serializers.Serializer):
    """
    Serializer for Employee model
    مسلسل نموذج الموظف
    """
    id = serializers.UUIDField(read_only=True)
    emp_code = serializers.CharField(max_length=20, required=False)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    first_name_ar = serializers.CharField(max_length=100, required=False)
    last_name_ar = serializers.CharField(max_length=100, required=False)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    mobile = serializers.CharField(max_length=20, required=False)
    
    # Personal Information
    national_id = serializers.CharField(max_length=20, required=False)
    passport_number = serializers.CharField(max_length=20, required=False)
    birth_date = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=[('M', 'ذكر'), ('F', 'أنثى')], required=False)
    marital_status = serializers.ChoiceField(
        choices=[('single', 'أعزب'), ('married', 'متزوج'), ('divorced', 'مطلق'), ('widowed', 'أرمل')],
        required=False
    )
    nationality = serializers.CharField(max_length=100, required=False)
    
    # Address Information
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    postal_code = serializers.CharField(max_length=10, required=False)
    
    # Employment Information
    department_id = serializers.IntegerField()
    department = DepartmentSerializer(read_only=True)
    job_position_id = serializers.IntegerField()
    job_position = JobPositionSerializer(read_only=True)
    manager_id = serializers.UUIDField(required=False, allow_null=True)
    manager_name = serializers.CharField(read_only=True)
    
    hire_date = serializers.DateField()
    termination_date = serializers.DateField(required=False, allow_null=True)
    emp_status = serializers.ChoiceField(
        choices=[
            ('active', 'نشط'),
            ('inactive', 'غير نشط'),
            ('terminated', 'منتهي الخدمة'),
            ('suspended', 'موقوف')
        ],
        default='active'
    )
    
    # Salary Information
    basic_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    allowances = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    total_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # System fields
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # Computed fields
    service_years = serializers.FloatField(read_only=True)
    age = serializers.IntegerField(read_only=True)


class AttendanceSerializer(serializers.Serializer):
    """
    Serializer for Attendance model
    مسلسل نموذج الحضور
    """
    id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField()
    employee = EmployeeSerializer(read_only=True)
    att_date = serializers.DateField()
    
    # Time tracking
    check_in_time = serializers.TimeField(required=False, allow_null=True)
    check_out_time = serializers.TimeField(required=False, allow_null=True)
    break_start_time = serializers.TimeField(required=False, allow_null=True)
    break_end_time = serializers.TimeField(required=False, allow_null=True)
    
    # Calculated fields
    total_hours = serializers.FloatField(read_only=True)
    regular_hours = serializers.FloatField(read_only=True)
    overtime_hours = serializers.FloatField(read_only=True)
    break_hours = serializers.FloatField(read_only=True)
    
    # Status and notes
    status = serializers.ChoiceField(
        choices=[
            ('present', 'حاضر'),
            ('absent', 'غائب'),
            ('late', 'متأخر'),
            ('early_leave', 'انصراف مبكر'),
            ('half_day', 'نصف يوم'),
            ('holiday', 'عطلة'),
            ('sick_leave', 'إجازة مرضية')
        ],
        default='present'
    )
    
    late_minutes = serializers.IntegerField(default=0)
    early_leave_minutes = serializers.IntegerField(default=0)
    
    # Location and device info
    check_in_location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    check_out_location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    device_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    notes = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)


class LeaveSerializer(serializers.Serializer):
    """
    Serializer for Leave model
    مسلسل نموذج الإجازة
    """
    id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField()
    employee = EmployeeSerializer(read_only=True)
    
    leave_type = serializers.ChoiceField(
        choices=[
            ('annual', 'إجازة سنوية'),
            ('sick', 'إجازة مرضية'),
            ('maternity', 'إجازة أمومة'),
            ('paternity', 'إجازة أبوة'),
            ('emergency', 'إجازة طارئة'),
            ('unpaid', 'إجازة بدون راتب'),
            ('study', 'إجازة دراسية'),
            ('hajj', 'إجازة حج'),
            ('other', 'أخرى')
        ]
    )
    
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_days = serializers.IntegerField(read_only=True)
    
    reason = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)
    
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'في الانتظار'),
            ('approved', 'موافق عليها'),
            ('rejected', 'مرفوضة'),
            ('cancelled', 'ملغية')
        ],
        default='pending'
    )
    
    # Approval workflow
    approved_by_id = serializers.UUIDField(required=False, allow_null=True)
    approved_by_name = serializers.CharField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)
    approval_comments = serializers.CharField(required=False, allow_blank=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PayrollSerializer(serializers.Serializer):
    """
    Serializer for Payroll model
    مسلسل نموذج الراتب
    """
    id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField()
    employee = EmployeeSerializer(read_only=True)
    
    pay_period = serializers.CharField(max_length=7)  # YYYY-MM format
    pay_date = serializers.DateField()
    
    # Salary components
    basic_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    allowances = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    tax_deduction = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_deduction = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_deduction = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Calculated totals
    gross_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Attendance data
    working_days = serializers.IntegerField()
    actual_working_days = serializers.IntegerField()
    overtime_hours = serializers.FloatField(default=0)
    
    status = serializers.ChoiceField(
        choices=[
            ('draft', 'مسودة'),
            ('calculated', 'محسوب'),
            ('approved', 'موافق عليه'),
            ('paid', 'مدفوع')
        ],
        default='draft'
    )
    
    notes = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class EvaluationSerializer(serializers.Serializer):
    """
    Serializer for Evaluation model
    مسلسل نموذج التقييم
    """
    id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField()
    employee = EmployeeSerializer(read_only=True)
    evaluator_id = serializers.UUIDField()
    evaluator_name = serializers.CharField(read_only=True)
    
    evaluation_period = serializers.CharField(max_length=7)  # YYYY-MM format
    evaluation_type = serializers.ChoiceField(
        choices=[
            ('annual', 'تقييم سنوي'),
            ('probation', 'تقييم فترة التجربة'),
            ('promotion', 'تقييم ترقية'),
            ('quarterly', 'تقييم ربع سنوي'),
            ('project', 'تقييم مشروع')
        ]
    )
    
    # Evaluation criteria scores (1-5 scale)
    job_knowledge = serializers.IntegerField(min_value=1, max_value=5)
    quality_of_work = serializers.IntegerField(min_value=1, max_value=5)
    productivity = serializers.IntegerField(min_value=1, max_value=5)
    communication = serializers.IntegerField(min_value=1, max_value=5)
    teamwork = serializers.IntegerField(min_value=1, max_value=5)
    leadership = serializers.IntegerField(min_value=1, max_value=5, required=False)
    initiative = serializers.IntegerField(min_value=1, max_value=5)
    reliability = serializers.IntegerField(min_value=1, max_value=5)
    
    # Calculated overall score
    overall_score = serializers.FloatField(read_only=True)
    overall_rating = serializers.CharField(read_only=True)  # Excellent, Good, Satisfactory, etc.
    
    # Comments and feedback
    strengths = serializers.CharField(required=False, allow_blank=True)
    areas_for_improvement = serializers.CharField(required=False, allow_blank=True)
    goals_for_next_period = serializers.CharField(required=False, allow_blank=True)
    evaluator_comments = serializers.CharField(required=False, allow_blank=True)
    employee_comments = serializers.CharField(required=False, allow_blank=True)
    
    status = serializers.ChoiceField(
        choices=[
            ('draft', 'مسودة'),
            ('submitted', 'مقدم'),
            ('reviewed', 'تمت المراجعة'),
            ('approved', 'موافق عليه'),
            ('completed', 'مكتمل')
        ],
        default='draft'
    )
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# Additional serializers for specific API operations

class EmployeeBulkImportSerializer(serializers.Serializer):
    """
    Serializer for bulk employee import
    مسلسل الاستيراد المجمع للموظفين
    """
    file = serializers.FileField()
    format = serializers.ChoiceField(choices=['excel', 'csv'], default='excel')
    skip_duplicates = serializers.BooleanField(default=True)
    update_existing = serializers.BooleanField(default=False)


class AttendanceClockSerializer(serializers.Serializer):
    """
    Serializer for clock in/out operations
    مسلسل عمليات تسجيل الدخول/الخروج
    """
    employee_id = serializers.UUIDField()
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    device_id = serializers.CharField(max_length=50, required=False, allow_blank=True)


class LeaveApplicationSerializer(serializers.Serializer):
    """
    Serializer for leave application
    مسلسل طلب الإجازة
    """
    employee_id = serializers.UUIDField()
    leave_type = serializers.ChoiceField(
        choices=[
            ('annual', 'إجازة سنوية'),
            ('sick', 'إجازة مرضية'),
            ('maternity', 'إجازة أمومة'),
            ('paternity', 'إجازة أبوة'),
            ('emergency', 'إجازة طارئة'),
            ('unpaid', 'إجازة بدون راتب'),
            ('study', 'إجازة دراسية'),
            ('hajj', 'إجازة حج'),
            ('other', 'أخرى')
        ]
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)


class LeaveApprovalSerializer(serializers.Serializer):
    """
    Serializer for leave approval
    مسلسل موافقة الإجازة
    """
    leave_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comments = serializers.CharField(required=False, allow_blank=True)


class PayrollCalculationSerializer(serializers.Serializer):
    """
    Serializer for payroll calculation
    مسلسل حساب الراتب
    """
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    pay_period = serializers.CharField(max_length=7)  # YYYY-MM format
    include_overtime = serializers.BooleanField(default=True)
    include_deductions = serializers.BooleanField(default=True)