"""HR API Serializers

This module contains serializers for the HR API endpoints, including:
- Employee serializers
- Organization serializers (Company, Branch, Department, JobPosition)
- Attendance serializers
- Payroll serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from Hr.models.employee.employee_models import Employee
from Hr.models import Company, Branch, Department, JobPosition
from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.attendance.work_shift_models import WorkShift
from Hr.models.attendance.attendance_machine_models import AttendanceMachine
from Hr.models.payroll.payroll_period_models import PayrollPeriod
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure, SalaryComponent

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'name_en', 'description', 'address', 'phone', 
            'email', 'website', 'tax_number', 'commercial_register',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    """Serializer for Branch model"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id', 'company', 'company_name', 'name', 'name_en', 'code',
            'address', 'phone', 'email', 'manager_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'branch', 'branch_name', 'parent', 'parent_name', 'name', 
            'name_en', 'code', 'description', 'manager_name', 'is_active',
            'employee_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_count']
    
    def get_employee_count(self, obj):
        """Get the number of active employees in this department"""
        return obj.employees.filter(is_active=True).count()


class JobPositionSerializer(serializers.ModelSerializer):
    """Serializer for JobPosition model"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPosition
        fields = [
            'id', 'department', 'department_name', 'name', 'name_en', 'code',
            'description', 'requirements', 'responsibilities', 'level',
            'is_active', 'employee_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_count']
    
    def get_employee_count(self, obj):
        """Get the number of active employees in this position"""
        return obj.employees.filter(is_active=True).count()


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer for Employee list view (minimal fields)"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    age = serializers.SerializerMethodField()
    service_years = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'full_name', 'email', 'phone',
            'department', 'department_name', 'branch', 'branch_name',
            'position', 'position_name', 'hire_date', 'is_active',
            'status', 'age', 'service_years'
        ]
        read_only_fields = ['id', 'age', 'service_years']
    
    def get_age(self, obj):
        """Calculate employee age"""
        if obj.birth_date:
            from datetime import date
            today = date.today()
            return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        return None
    
    def get_service_years(self, obj):
        """Calculate years of service"""
        if obj.hire_date:
            from datetime import date
            today = date.today()
            return round((today - obj.hire_date).days / 365.25, 1)
        return None


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer for Employee detail view (all fields)"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    age = serializers.SerializerMethodField()
    service_years = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'full_name', 'first_name', 'last_name',
            'email', 'phone', 'mobile', 'national_id', 'passport_number',
            'birth_date', 'gender', 'marital_status', 'nationality',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'department', 'department_name', 'branch', 'branch_name',
            'position', 'position_name', 'hire_date', 'contract_type',
            'employment_status', 'is_active', 'status', 'notes',
            'age', 'service_years', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'age', 'service_years', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
    
    def get_age(self, obj):
        """Calculate employee age"""
        if obj.birth_date:
            from datetime import date
            today = date.today()
            return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        return None
    
    def get_service_years(self, obj):
        """Calculate years of service"""
        if obj.hire_date:
            from datetime import date
            today = date.today()
            return round((today - obj.hire_date).days / 365.25, 1)
        return None


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Employee create/update operations"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'full_name', 'first_name', 'last_name',
            'email', 'phone', 'mobile', 'national_id', 'passport_number',
            'birth_date', 'gender', 'marital_status', 'nationality',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'department', 'branch', 'position', 'hire_date', 'contract_type',
            'employment_status', 'is_active', 'status', 'notes'
        ]
    
    def validate_employee_number(self, value):
        """Validate employee number uniqueness"""
        if self.instance:
            # Update case - exclude current instance
            if Employee.objects.filter(employee_number=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Employee with this number already exists.")
        else:
            # Create case
            if Employee.objects.filter(employee_number=value).exists():
                raise serializers.ValidationError("Employee with this number already exists.")
        return value
    
    def validate_national_id(self, value):
        """Validate national ID uniqueness"""
        if value:
            if self.instance:
                # Update case - exclude current instance
                if Employee.objects.filter(national_id=value).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Employee with this national ID already exists.")
            else:
                # Create case
                if Employee.objects.filter(national_id=value).exists():
                    raise serializers.ValidationError("Employee with this national ID already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if value:
            if self.instance:
                # Update case - exclude current instance
                if Employee.objects.filter(email=value).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Employee with this email already exists.")
            else:
                # Create case
                if Employee.objects.filter(email=value).exists():
                    raise serializers.ValidationError("Employee with this email already exists.")
        return value


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord model"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_number = serializers.CharField(source='employee.employee_number', read_only=True)
    machine_name = serializers.CharField(source='machine.name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_number', 'date',
            'check_in_time', 'check_out_time', 'worked_hours', 'overtime_hours',
            'machine', 'machine_name', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'worked_hours', 'overtime_hours', 'created_at', 'updated_at']


class WorkShiftSerializer(serializers.ModelSerializer):
    """Serializer for WorkShift model"""
    
    class Meta:
        model = WorkShift
        fields = [
            'id', 'name', 'name_en', 'start_time', 'end_time', 'break_duration',
            'total_hours', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceMachineSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceMachine model"""
    
    class Meta:
        model = AttendanceMachine
        fields = [
            'id', 'name', 'model', 'serial_number', 'ip_address', 'port',
            'location', 'is_active', 'last_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_sync', 'created_at', 'updated_at']


class PayrollPeriodSerializer(serializers.ModelSerializer):
    """Serializer for PayrollPeriod model"""
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'name', 'start_date', 'end_date', 'status', 'closed_date',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'closed_date', 'created_at', 'updated_at']


class SalaryComponentSerializer(serializers.ModelSerializer):
    """Serializer for SalaryComponent model"""
    
    class Meta:
        model = SalaryComponent
        fields = [
            'id', 'name', 'name_en', 'component_type', 'calculation_type',
            'amount', 'percentage', 'is_taxable', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeSalaryStructureSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeSalaryStructure model"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    salary_components = SalaryComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmployeeSalaryStructure
        fields = [
            'id', 'employee', 'employee_name', 'basic_salary', 'effective_date',
            'is_active', 'salary_components', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Statistics and Analytics Serializers

class EmployeeStatisticsSerializer(serializers.Serializer):
    """Serializer for employee statistics"""
    
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    inactive_employees = serializers.IntegerField()
    department_counts = serializers.ListField()
    branch_counts = serializers.ListField()
    position_counts = serializers.ListField()
    status_counts = serializers.ListField()


class AttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary"""
    
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    total_worked_hours = serializers.FloatField()
    average_daily_hours = serializers.FloatField()
    late_arrivals = serializers.IntegerField()
    early_departures = serializers.IntegerField()


class PayrollCalculationSerializer(serializers.Serializer):
    """Serializer for payroll calculation results"""
    
    employee_id = serializers.UUIDField()
    employee_name = serializers.CharField()
    period_id = serializers.UUIDField()
    period_name = serializers.CharField()
    basic_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    allowances = serializers.DictField()
    deductions = serializers.DictField()
    total_allowances = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    worked_days = serializers.IntegerField()
    total_days = serializers.IntegerField()
    attendance_rate = serializers.FloatField()


class LeaveBalanceSerializer(serializers.Serializer):
    """Serializer for leave balance information"""
    
    employee_id = serializers.UUIDField()
    employee_name = serializers.CharField()
    leave_type_id = serializers.CharField()
    leave_type_name = serializers.CharField()
    year = serializers.IntegerField()
    entitlement = serializers.IntegerField()
    carry_forward = serializers.IntegerField()
    total_entitlement = serializers.IntegerField()
    used_days = serializers.IntegerField()
    available_balance = serializers.IntegerField()
    pending_requests = serializers.IntegerField()


class DashboardAnalyticsSerializer(serializers.Serializer):
    """Serializer for dashboard analytics"""
    
    employee_stats = serializers.DictField()
    attendance_stats = serializers.DictField()
    department_stats = serializers.ListField()
    generated_at = serializers.DateTimeField()


# Bulk operation serializers

class BulkEmployeeImportSerializer(serializers.Serializer):
    """Serializer for bulk employee import"""
    
    file = serializers.FileField()
    update_existing = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        if not value.name.endswith(('.csv', '.xlsx', '.xls')):
            raise serializers.ValidationError("File must be CSV or Excel format.")
        
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("File size must be less than 5MB.")
        
        return value


class BulkAttendanceImportSerializer(serializers.Serializer):
    """Serializer for bulk attendance import"""
    
    file = serializers.FileField()
    machine_id = serializers.UUIDField(required=False)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        if not value.name.endswith(('.csv', '.xlsx', '.xls')):
            raise serializers.ValidationError("File must be CSV or Excel format.")
        
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size must be less than 10MB.")
        
        return value