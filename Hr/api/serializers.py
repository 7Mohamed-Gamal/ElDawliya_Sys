"""
HR API Serializers - مسلسلات واجهة برمجة التطبيقات للموارد البشرية
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from datetime import date, datetime
import uuid

from ..models_enhanced import (
    Company, Branch, Department, JobPosition, Employee,
    EmployeeEducation, EmployeeInsurance, EmployeeVehicle, EmployeeFile,
    WorkShiftEnhanced, AttendanceMachineEnhanced, AttendanceRecordEnhanced,
    AttendanceSummary, EmployeeShiftAssignment,
    LeaveType, LeaveRequest, LeaveBalance
)

User = get_user_model()


# =============================================================================
# BASIC SERIALIZERS - المسلسلات الأساسية
# =============================================================================

class CompanySerializer(serializers.ModelSerializer):
    """مسلسل الشركة"""
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'name_english', 'code', 'tax_number',
            'commercial_register', 'address', 'phone', 'email',
            'website', 'logo', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    """مسلسل الفرع"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id', 'company', 'company_name', 'name', 'code', 'address',
            'phone', 'manager', 'manager_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    """مسلسل القسم"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    parent_department_name = serializers.CharField(source='parent_department.name', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'company', 'company_name', 'branch', 'branch_name',
            'name', 'code', 'parent_department', 'parent_department_name',
            'manager', 'manager_name', 'description', 'budget',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobPositionSerializer(serializers.ModelSerializer):
    """مسلسل المنصب الوظيفي"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = JobPosition
        fields = [
            'id', 'company', 'company_name', 'department', 'department_name',
            'title', 'title_english', 'code', 'level', 'level_display',
            'description', 'requirements', 'min_salary', 'max_salary',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
#
 =============================================================================
# EMPLOYEE RELATED SERIALIZERS - مسلسلات الموظفين
# =============================================================================

class EmployeeEducationSerializer(serializers.ModelSerializer):
    """مسلسل تعليم الموظف"""
    
    education_type_display = serializers.CharField(source='get_education_type_display', read_only=True)
    
    class Meta:
        model = EmployeeEducation
        fields = [
            'id', 'employee', 'education_type', 'education_type_display',
            'degree_name', 'institution_name', 'institution_location',
            'institution_country', 'field_of_study', 'specialization',
            'start_date', 'end_date', 'duration_months', 'is_current',
            'grade', 'score', 'score_type', 'certificate_number',
            'certificate_file', 'is_verified', 'verified_by', 'verified_at',
            'achievements', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeInsuranceSerializer(serializers.ModelSerializer):
    """مسلسل تأمين الموظف"""
    
    insurance_type_display = serializers.CharField(source='get_insurance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EmployeeInsurance
        fields = [
            'id', 'employee', 'insurance_type', 'insurance_type_display',
            'provider_name', 'policy_number', 'start_date', 'end_date',
            'premium_amount', 'coverage_amount', 'beneficiaries',
            'status', 'status_display', 'notes', 'documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeVehicleSerializer(serializers.ModelSerializer):
    """مسلسل مركبة الموظف"""
    
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    ownership_type_display = serializers.CharField(source='get_ownership_type_display', read_only=True)
    
    class Meta:
        model = EmployeeVehicle
        fields = [
            'id', 'employee', 'vehicle_type', 'vehicle_type_display',
            'make', 'model', 'year', 'color', 'license_plate',
            'chassis_number', 'engine_number', 'ownership_type',
            'ownership_type_display', 'registration_date',
            'insurance_expiry', 'license_expiry', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeFileSerializer(serializers.ModelSerializer):
    """مسلسل ملف الموظف"""
    
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeFile
        fields = [
            'id', 'employee', 'file_type', 'file_type_display',
            'title', 'description', 'file', 'file_size',
            'file_size_mb', 'expiry_date', 'is_expired',
            'is_confidential', 'uploaded_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_by', 'created_at', 'updated_at']
    
    def get_file_size_mb(self, obj):
        """حساب حجم الملف بالميجابايت"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0
    
    def get_is_expired(self, obj):
        """فحص انتهاء صلاحية الملف"""
        if obj.expiry_date:
            return obj.expiry_date < date.today()
        return False


class EmployeeBasicSerializer(serializers.ModelSerializer):
    """مسلسل الموظف الأساسي"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_position_title = serializers.CharField(source='job_position.title', read_only=True)
    direct_manager_name = serializers.CharField(source='direct_manager.full_name', read_only=True)
    
    # Computed fields
    age = serializers.ReadOnlyField()
    years_of_service = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'first_name', 'middle_name', 'last_name',
            'full_name', 'name_english', 'email', 'phone_primary',
            'phone_secondary', 'company', 'company_name', 'branch',
            'branch_name', 'department', 'department_name', 'job_position',
            'job_position_title', 'direct_manager', 'direct_manager_name',
            'employment_type', 'hire_date', 'status', 'age', 'years_of_service',
            'photo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'age', 'years_of_service', 'created_at', 'updated_at']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """مسلسل الموظف المفصل"""
    
    # Related data
    company = CompanySerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    job_position = JobPositionSerializer(read_only=True)
    direct_manager = EmployeeBasicSerializer(read_only=True)
    
    # Related objects
    education_records = EmployeeEducationSerializer(many=True, read_only=True)
    insurance_records = EmployeeInsuranceSerializer(many=True, read_only=True)
    vehicle_records = EmployeeVehicleSerializer(many=True, read_only=True)
    files = EmployeeFileSerializer(many=True, read_only=True)
    
    # Computed fields
    age = serializers.ReadOnlyField()
    years_of_service = serializers.ReadOnlyField()
    
    # Statistics
    education_count = serializers.SerializerMethodField()
    insurance_count = serializers.SerializerMethodField()
    vehicle_count = serializers.SerializerMethodField()
    files_count = serializers.SerializerMethodField()
    subordinates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            # Basic Information
            'id', 'employee_number', 'first_name', 'middle_name', 'last_name',
            'full_name', 'name_english', 'email', 'phone_primary', 'phone_secondary',
            'address', 'national_id', 'passport_number', 'date_of_birth',
            'place_of_birth', 'gender', 'marital_status', 'nationality', 'religion',
            
            # Employment Information
            'company', 'branch', 'department', 'job_position', 'direct_manager',
            'employment_type', 'hire_date', 'probation_end_date',
            'contract_start_date', 'contract_end_date', 'termination_date',
            'termination_reason', 'status', 'is_active',
            
            # Computed fields
            'age', 'years_of_service',
            
            # Related data
            'education_records', 'insurance_records', 'vehicle_records', 'files',
            
            # Statistics
            'education_count', 'insurance_count', 'vehicle_count',
            'files_count', 'subordinates_count',
            
            # Media and notes
            'photo', 'notes',
            
            # System fields
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'age', 'years_of_service',
            'education_count', 'insurance_count', 'vehicle_count',
            'files_count', 'subordinates_count', 'created_at', 'updated_at'
        ]
    
    def get_education_count(self, obj):
        return obj.education_records.count()
    
    def get_insurance_count(self, obj):
        return obj.insurance_records.count()
    
    def get_vehicle_count(self, obj):
        return obj.vehicle_records.count()
    
    def get_files_count(self, obj):
        return obj.files.count()
    
    def get_subordinates_count(self, obj):
        return obj.subordinates.filter(is_active=True).count()


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء وتحديث الموظف"""
    
    # Validation
    employee_number = serializers.CharField(
        validators=[UniqueValidator(queryset=Employee.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Employee.objects.all())]
    )
    national_id = serializers.CharField(
        validators=[UniqueValidator(queryset=Employee.objects.all())]
    )
    
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'first_name', 'middle_name', 'last_name',
            'name_english', 'email', 'phone_primary', 'phone_secondary',
            'address', 'national_id', 'passport_number', 'date_of_birth',
            'place_of_birth', 'gender', 'marital_status', 'nationality',
            'religion', 'company', 'branch', 'department', 'job_position',
            'direct_manager', 'employment_type', 'hire_date',
            'probation_end_date', 'contract_start_date', 'contract_end_date',
            'status', 'photo', 'notes'
        ]
    
    def validate_date_of_birth(self, value):
        """التحقق من تاريخ الميلاد"""
        if value >= date.today():
            raise serializers.ValidationError("تاريخ الميلاد يجب أن يكون في الماضي")
        
        # Check minimum age (18 years)
        age = (date.today() - value).days / 365.25
        if age < 18:
            raise serializers.ValidationError("عمر الموظف يجب أن يكون 18 سنة على الأقل")
        
        return value
    
    def validate_hire_date(self, value):
        """التحقق من تاريخ التوظيف"""
        if value > date.today():
            raise serializers.ValidationError("تاريخ التوظيف لا يمكن أن يكون في المستقبل")
        return value
    
    def validate(self, data):
        """التحقق الشامل من البيانات"""
        # Check birth date vs hire date
        if data.get('date_of_birth') and data.get('hire_date'):
            birth_date = data['date_of_birth']
            hire_date = data['hire_date']
            
            age_at_hire = (hire_date - birth_date).days / 365.25
            if age_at_hire < 18:
                raise serializers.ValidationError(
                    "عمر الموظف يجب أن يكون 18 سنة على الأقل عند التوظيف"
                )
        
        # Check contract dates
        if data.get('contract_start_date') and data.get('contract_end_date'):
            if data['contract_start_date'] >= data['contract_end_date']:
                raise serializers.ValidationError(
                    "تاريخ بداية العقد يجب أن يكون قبل تاريخ النهاية"
                )
        
        return data# =====
========================================================================
# ATTENDANCE SERIALIZERS - مسلسلات الحضور
# =============================================================================

class WorkShiftSerializer(serializers.ModelSerializer):
    """مسلسل الوردية"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    shift_type_display = serializers.CharField(source='get_shift_type_display', read_only=True)
    working_days_list = serializers.ReadOnlyField()
    total_working_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkShiftEnhanced
        fields = [
            'id', 'company', 'company_name', 'name', 'name_english', 'code',
            'shift_type', 'shift_type_display', 'start_time', 'end_time',
            'is_overnight', 'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday', 'working_days_list',
            'break_duration', 'break_type', 'multiple_breaks',
            'grace_period_in', 'grace_period_out', 'allow_early_checkin',
            'allow_late_checkout', 'overtime_threshold', 'overtime_rate',
            'weekend_overtime_rate', 'require_location', 'allowed_locations',
            'location_radius', 'total_working_hours', 'is_active',
            'effective_from', 'effective_to', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'working_days_list', 'total_working_hours', 'created_at', 'updated_at']


class AttendanceMachineSerializer(serializers.ModelSerializer):
    """مسلسل جهاز الحضور"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    machine_type_display = serializers.CharField(source='get_machine_type_display', read_only=True)
    connection_type_display = serializers.CharField(source='get_connection_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Computed fields
    is_online = serializers.ReadOnlyField()
    capacity_percentage = serializers.ReadOnlyField()
    needs_maintenance = serializers.ReadOnlyField()
    
    class Meta:
        model = AttendanceMachineEnhanced
        fields = [
            'id', 'company', 'company_name', 'branch', 'branch_name',
            'name', 'serial_number', 'machine_type', 'machine_type_display',
            'model', 'manufacturer', 'connection_type', 'connection_type_display',
            'ip_address', 'port', 'device_id', 'location', 'latitude',
            'longitude', 'allow_checkin', 'allow_checkout', 'require_verification',
            'auto_sync', 'sync_interval', 'status', 'status_display',
            'last_sync', 'last_ping', 'firmware_version', 'max_users',
            'max_records', 'current_users', 'current_records',
            'installation_date', 'last_maintenance', 'next_maintenance',
            'warranty_expiry', 'is_online', 'capacity_percentage',
            'needs_maintenance', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_online', 'capacity_percentage', 'needs_maintenance',
            'last_sync', 'last_ping', 'created_at', 'updated_at'
        ]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """مسلسل سجل الحضور"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_number = serializers.CharField(source='employee.employee_number', read_only=True)
    machine_name = serializers.CharField(source='machine.name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    
    attendance_type_display = serializers.CharField(source='get_attendance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    verification_method_display = serializers.CharField(source='get_verification_method_display', read_only=True)
    
    # Computed fields
    is_late = serializers.ReadOnlyField()
    is_overtime = serializers.ReadOnlyField()
    location_string = serializers.ReadOnlyField()
    
    class Meta:
        model = AttendanceRecordEnhanced
        fields = [
            'id', 'employee', 'employee_name', 'employee_number',
            'machine', 'machine_name', 'shift', 'shift_name', 'date',
            'timestamp', 'attendance_type', 'attendance_type_display',
            'status', 'status_display', 'verification_method',
            'verification_method_display', 'verification_score',
            'device_user_id', 'latitude', 'longitude', 'location_accuracy',
            'location_string', 'scheduled_time', 'actual_time',
            'time_difference', 'work_hours', 'overtime_hours', 'break_hours',
            'is_late', 'is_overtime', 'is_approved', 'approved_by',
            'approved_at', 'is_modified', 'modified_by', 'modified_at',
            'modification_reason', 'notes', 'raw_data', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'actual_time', 'time_difference', 'is_late', 'is_overtime',
            'location_string', 'approved_by', 'approved_at', 'modified_by',
            'modified_at', 'created_at', 'updated_at'
        ]


class AttendanceSummarySerializer(serializers.ModelSerializer):
    """مسلسل ملخص الحضور"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_number = serializers.CharField(source='employee.employee_number', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    
    # Computed fields
    attendance_status = serializers.ReadOnlyField()
    effective_work_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'id', 'employee', 'employee_name', 'employee_number', 'date',
            'shift', 'shift_name', 'is_present', 'is_absent', 'is_late',
            'is_early_leave', 'check_in_time', 'check_out_time',
            'scheduled_in_time', 'scheduled_out_time', 'total_work_hours',
            'regular_hours', 'overtime_hours', 'break_hours',
            'effective_work_hours', 'late_minutes', 'early_leave_minutes',
            'is_on_leave', 'leave_type', 'is_holiday', 'holiday_name',
            'attendance_status', 'is_approved', 'approved_by', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'attendance_status', 'effective_work_hours',
            'approved_by', 'created_at', 'updated_at'
        ]


class EmployeeShiftAssignmentSerializer(serializers.ModelSerializer):
    """مسلسل تعيين وردية الموظف"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_number = serializers.CharField(source='employee.employee_number', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    
    # Computed fields
    is_current = serializers.ReadOnlyField()
    
    class Meta:
        model = EmployeeShiftAssignment
        fields = [
            'id', 'employee', 'employee_name', 'employee_number',
            'shift', 'shift_name', 'start_date', 'end_date',
            'is_permanent', 'is_active', 'is_current', 'notes',
            'assigned_by', 'assigned_by_name', 'assigned_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_current', 'assigned_by', 'assigned_by_name',
            'assigned_at', 'created_at', 'updated_at'
        ]


# =============================================================================
# LEAVE SERIALIZERS - مسلسلات الإجازات
# =============================================================================

class LeaveTypeSerializer(serializers.ModelSerializer):
    """مسلسل نوع الإجازة"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    accrual_method_display = serializers.CharField(source='get_accrual_method_display', read_only=True)
    gender_restriction_display = serializers.CharField(source='get_gender_restriction_display', read_only=True)
    employment_type_restriction_display = serializers.CharField(source='get_employment_type_restriction_display', read_only=True)
    
    class Meta:
        model = LeaveType
        fields = [
            'id', 'company', 'company_name', 'name', 'name_english', 'code',
            'category', 'category_display', 'description', 'color',
            'default_days', 'max_days_per_year', 'max_consecutive_days',
            'min_notice_days', 'accrual_method', 'accrual_method_display',
            'accrual_rate', 'allow_carryover', 'max_carryover_days',
            'carryover_expiry_months', 'requires_approval', 'approval_levels',
            'auto_approve_days', 'exclude_weekends', 'exclude_holidays',
            'is_paid', 'gender_restriction', 'gender_restriction_display',
            'employment_type_restriction', 'employment_type_restriction_display',
            'min_service_months', 'is_active', 'effective_from', 'effective_to',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    """مسلسل طلب الإجازة"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_number = serializers.CharField(source='employee.employee_number', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    rejected_by_name = serializers.CharField(source='rejected_by.username', read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Computed fields
    duration_days = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_future = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    days_until_start = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_number',
            'leave_type', 'leave_type_name', 'start_date', 'end_date',
            'days_requested', 'duration_days', 'reason', 'priority',
            'priority_display', 'status', 'status_display', 'is_current',
            'is_future', 'is_past', 'days_until_start', 'can_be_cancelled',
            'requested_at', 'submitted_at', 'approved_by', 'approved_by_name',
            'approved_at', 'approved_days', 'approval_comments',
            'rejected_by', 'rejected_by_name', 'rejected_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration_days', 'is_current', 'is_future', 'is_past',
            'days_until_start', 'can_be_cancelled', 'requested_at',
            'approved_by', 'approved_by_name', 'approved_at',
            'rejected_by', 'rejected_by_name', 'rejected_at',
            'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """التحقق من صحة طلب الإجازة"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "تاريخ البداية يجب أن يكون قبل تاريخ النهاية"
                )
            
            if data['start_date'] < date.today():
                raise serializers.ValidationError(
                    "لا يمكن طلب إجازة في الماضي"
                )
        
        return data


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """مسلسل رصيد الإجازة"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_number = serializers.CharField(source='employee.employee_number', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    # Computed fields
    available_days = serializers.ReadOnlyField()
    utilization_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'employee_name', 'employee_number',
            'leave_type', 'leave_type_name', 'year', 'allocated_days',
            'used_days', 'remaining_days', 'available_days',
            'utilization_percentage', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'available_days', 'utilization_percentage',
            'created_at', 'updated_at'
        ]