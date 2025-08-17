"""
HR API Filters - فلاتر واجهات برمجة التطبيقات للموارد البشرية
"""
import django_filters
from django.db.models import Q
from datetime import date, datetime, timedelta
from django_filters import rest_framework as filters

from ..models_enhanced import (
    Employee, AttendanceRecordEnhanced, AttendanceSummary,
    LeaveRequest, LeaveBalance, WorkShiftEnhanced
)

class EmployeeFilter(filters.FilterSet):
    """فلتر الموظفين المتقدم"""
    
    # Basic filters
    company = filters.NumberFilter(field_name='company__id')
    branch = filters.NumberFilter(field_name='branch__id')
    department = filters.NumberFilter(field_name='department__id')
    job_position = filters.NumberFilter(field_name='job_position__id')
    direct_manager = filters.NumberFilter(field_name='direct_manager__id')
    
    # Status filters
    status = filters.ChoiceFilter(choices=[
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('terminated', 'منتهي الخدمة'),
        ('suspended', 'موقوف')
    ])
    employment_type = filters.ChoiceFilter(choices=[
        ('full_time', 'دوام كامل'),
        ('part_time', 'دوام جزئي'),
        ('contract', 'عقد'),
        ('temporary', 'مؤقت')
    ])
    
    # Date filters
    hire_date_from = filters.DateFilter(field_name='hire_date', lookup_expr='gte')
    hire_date_to = filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    birth_date_from = filters.DateFilter(field_name='birth_date', lookup_expr='gte')
    birth_date_to = filters.DateFilter(field_name='birth_date', lookup_expr='lte')
    
    # Salary filters
    salary_min = filters.NumberFilter(field_name='basic_salary', lookup_expr='gte')
    salary_max = filters.NumberFilter(field_name='basic_salary', lookup_expr='lte')
    
    # Age filters
    age_min = filters.NumberFilter(method='filter_age_min')
    age_max = filters.NumberFilter(method='filter_age_max')
    
    # Service years filters
    service_years_min = filters.NumberFilter(method='filter_service_years_min')
    service_years_max = filters.NumberFilter(method='filter_service_years_max')
    
    # Gender filter
    gender = filters.ChoiceFilter(choices=[
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ])
    
    # Marital status filter
    marital_status = filters.ChoiceFilter(choices=[
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل')
    ])
    
    # Education level filter
    education_level = filters.CharFilter(method='filter_education_level')
    
    # Has specific records filters
    has_education = filters.BooleanFilter(method='filter_has_education')
    has_insurance = filters.BooleanFilter(method='filter_has_insurance')
    has_vehicle = filters.BooleanFilter(method='filter_has_vehicle')
    
    # Search in multiple fields
    search = filters.CharFilter(method='filter_search')
    
    # Advanced filters
    upcoming_birthday = filters.NumberFilter(method='filter_upcoming_birthday')
    probation_ending = filters.NumberFilter(method='filter_probation_ending')
    contract_expiring = filters.NumberFilter(method='filter_contract_expiring')
    
    class Meta:
        model = Employee
        fields = [
            'company', 'branch', 'department', 'job_position', 'direct_manager',
            'status', 'employment_type', 'gender', 'marital_status',
            'hire_date_from', 'hire_date_to', 'birth_date_from', 'birth_date_to',
            'salary_min', 'salary_max', 'age_min', 'age_max',
            'service_years_min', 'service_years_max', 'education_level',
            'has_education', 'has_insurance', 'has_vehicle', 'search',
            'upcoming_birthday', 'probation_ending', 'contract_expiring'
        ]
    
    def filter_age_min(self, queryset, name, value):
        """فلتر العمر الأدنى"""
        if value:
            birth_date_max = date.today() - timedelta(days=value * 365)
            return queryset.filter(birth_date__lte=birth_date_max)
        return queryset
    
    def filter_age_max(self, queryset, name, value):
        """فلتر العمر الأقصى"""
        if value:
            birth_date_min = date.today() - timedelta(days=value * 365)
            return queryset.filter(birth_date__gte=birth_date_min)
        return queryset
    
    def filter_service_years_min(self, queryset, name, value):
        """فلتر سنوات الخدمة الأدنى"""
        if value:
            hire_date_max = date.today() - timedelta(days=value * 365)
            return queryset.filter(hire_date__lte=hire_date_max)
        return queryset
    
    def filter_service_years_max(self, queryset, name, value):
        """فلتر سنوات الخدمة الأقصى"""
        if value:
            hire_date_min = date.today() - timedelta(days=value * 365)
            return queryset.filter(hire_date__gte=hire_date_min)
        return queryset
    
    def filter_education_level(self, queryset, name, value):
        """فلتر المستوى التعليمي"""
        if value:
            return queryset.filter(education_records__education_type__icontains=value).distinct()
        return queryset
    
    def filter_has_education(self, queryset, name, value):
        """فلتر وجود سجلات تعليمية"""
        if value is not None:
            if value:
                return queryset.filter(education_records__isnull=False).distinct()
            else:
                return queryset.filter(education_records__isnull=True)
        return queryset
    
    def filter_has_insurance(self, queryset, name, value):
        """فلتر وجود سجلات تأمين"""
        if value is not None:
            if value:
                return queryset.filter(insurance_records__isnull=False).distinct()
            else:
                return queryset.filter(insurance_records__isnull=True)
        return queryset
    
    def filter_has_vehicle(self, queryset, name, value):
        """فلتر وجود سجلات مركبات"""
        if value is not None:
            if value:
                return queryset.filter(vehicle_records__isnull=False).distinct()
            else:
                return queryset.filter(vehicle_records__isnull=True)
        return queryset
    
    def filter_search(self, queryset, name, value):
        """البحث في حقول متعددة"""
        if value:
            return queryset.filter(
                Q(first_name__icontains=value) |
                Q(last_name__icontains=value) |
                Q(employee_number__icontains=value) |
                Q(email__icontains=value) |
                Q(phone_primary__icontains=value) |
                Q(national_id__icontains=value) |
                Q(department__name__icontains=value) |
                Q(job_position__title__icontains=value)
            )
        return queryset
    
    def filter_upcoming_birthday(self, queryset, name, value):
        """فلتر أعياد الميلاد القادمة"""
        if value:
            today = date.today()
            future_date = today + timedelta(days=value)
            
            # Handle year boundary
            if future_date.year > today.year:
                return queryset.filter(
                    Q(birth_date__month__gte=today.month, birth_date__day__gte=today.day) |
                    Q(birth_date__month__lte=future_date.month, birth_date__day__lte=future_date.day)
                )
            else:
                return queryset.filter(
                    birth_date__month=today.month,
                    birth_date__day__gte=today.day,
                    birth_date__day__lte=future_date.day
                )
        return queryset
    
    def filter_probation_ending(self, queryset, name, value):
        """فلتر انتهاء فترة التجربة"""
        if value:
            future_date = date.today() + timedelta(days=value)
            return queryset.filter(
                probation_end_date__lte=future_date,
                probation_end_date__gte=date.today()
            )
        return queryset
    
    def filter_contract_expiring(self, queryset, name, value):
        """فلتر انتهاء العقود"""
        if value:
            future_date = date.today() + timedelta(days=value)
            return queryset.filter(
                contract_end_date__lte=future_date,
                contract_end_date__gte=date.today()
            )
        return queryset

class AttendanceRecordFilter(filters.FilterSet):
    """فلتر سجلات الحضور"""
    
    # Basic filters
    employee = filters.NumberFilter(field_name='employee__id')
    employee_number = filters.CharFilter(field_name='employee__employee_number')
    department = filters.NumberFilter(field_name='employee__department__id')
    machine = filters.NumberFilter(field_name='machine__id')
    shift = filters.NumberFilter(field_name='shift__id')
    
    # Date filters
    date = filters.DateFilter()
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Time filters
    time_from = filters.TimeFilter(field_name='timestamp__time', lookup_expr='gte')
    time_to = filters.TimeFilter(field_name='timestamp__time', lookup_expr='lte')
    
    # Attendance type filter
    attendance_type = filters.ChoiceFilter(choices=[
        ('check_in', 'دخول'),
        ('check_out', 'خروج'),
        ('break_start', 'بداية استراحة'),
        ('break_end', 'نهاية استراحة')
    ])
    
    # Status filters
    status = filters.ChoiceFilter(choices=[
        ('on_time', 'في الوقت'),
        ('late', 'متأخر'),
        ('early', 'مبكر'),
        ('overtime', 'وقت إضافي')
    ])
    
    # Verification method filter
    verification_method = filters.ChoiceFilter(choices=[
        ('fingerprint', 'بصمة'),
        ('face', 'وجه'),
        ('card', 'كارت'),
        ('pin', 'رقم سري'),
        ('manual', 'يدوي')
    ])
    
    # Approval filters
    is_approved = filters.BooleanFilter()
    is_modified = filters.BooleanFilter()
    
    # Location filters
    has_location = filters.BooleanFilter(method='filter_has_location')
    location_accuracy_min = filters.NumberFilter(field_name='location_accuracy', lookup_expr='gte')
    
    # Work hours filters
    work_hours_min = filters.NumberFilter(field_name='work_hours', lookup_expr='gte')
    work_hours_max = filters.NumberFilter(field_name='work_hours', lookup_expr='lte')
    overtime_hours_min = filters.NumberFilter(field_name='overtime_hours', lookup_expr='gte')
    
    class Meta:
        model = AttendanceRecordEnhanced
        fields = [
            'employee', 'employee_number', 'department', 'machine', 'shift',
            'date', 'date_from', 'date_to', 'time_from', 'time_to',
            'attendance_type', 'status', 'verification_method',
            'is_approved', 'is_modified', 'has_location', 'location_accuracy_min',
            'work_hours_min', 'work_hours_max', 'overtime_hours_min'
        ]
    
    def filter_has_location(self, queryset, name, value):
        """فلتر وجود بيانات الموقع"""
        if value is not None:
            if value:
                return queryset.filter(latitude__isnull=False, longitude__isnull=False)
            else:
                return queryset.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
        return queryset

class AttendanceSummaryFilter(filters.FilterSet):
    """فلتر ملخصات الحضور"""
    
    # Basic filters
    employee = filters.NumberFilter(field_name='employee__id')
    employee_number = filters.CharFilter(field_name='employee__employee_number')
    department = filters.NumberFilter(field_name='employee__department__id')
    shift = filters.NumberFilter(field_name='shift__id')
    
    # Date filters
    date = filters.DateFilter()
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    month = filters.NumberFilter(field_name='date__month')
    year = filters.NumberFilter(field_name='date__year')
    
    # Attendance status filters
    is_present = filters.BooleanFilter()
    is_absent = filters.BooleanFilter()
    is_late = filters.BooleanFilter()
    is_early_leave = filters.BooleanFilter()
    is_on_leave = filters.BooleanFilter()
    is_holiday = filters.BooleanFilter()
    
    # Work hours filters
    total_work_hours_min = filters.NumberFilter(field_name='total_work_hours', lookup_expr='gte')
    total_work_hours_max = filters.NumberFilter(field_name='total_work_hours', lookup_expr='lte')
    overtime_hours_min = filters.NumberFilter(field_name='overtime_hours', lookup_expr='gte')
    
    # Late/early filters
    late_minutes_min = filters.NumberFilter(field_name='late_minutes', lookup_expr='gte')
    early_leave_minutes_min = filters.NumberFilter(field_name='early_leave_minutes', lookup_expr='gte')
    
    # Approval filter
    is_approved = filters.BooleanFilter()
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'employee', 'employee_number', 'department', 'shift',
            'date', 'date_from', 'date_to', 'month', 'year',
            'is_present', 'is_absent', 'is_late', 'is_early_leave',
            'is_on_leave', 'is_holiday', 'total_work_hours_min',
            'total_work_hours_max', 'overtime_hours_min',
            'late_minutes_min', 'early_leave_minutes_min', 'is_approved'
        ]

class LeaveRequestFilter(filters.FilterSet):
    """فلتر طلبات الإجازات"""
    
    # Basic filters
    employee = filters.NumberFilter(field_name='employee__id')
    employee_number = filters.CharFilter(field_name='employee__employee_number')
    department = filters.NumberFilter(field_name='employee__department__id')
    leave_type = filters.NumberFilter(field_name='leave_type__id')
    
    # Status filter
    status = filters.ChoiceFilter(choices=[
        ('pending', 'في الانتظار'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('cancelled', 'ملغي')
    ])
    
    # Date filters
    start_date = filters.DateFilter()
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date = filters.DateFilter()
    end_date_from = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Request date filters
    requested_at_from = filters.DateTimeFilter(field_name='requested_at', lookup_expr='gte')
    requested_at_to = filters.DateTimeFilter(field_name='requested_at', lookup_expr='lte')
    
    # Duration filters
    days_requested_min = filters.NumberFilter(field_name='days_requested', lookup_expr='gte')
    days_requested_max = filters.NumberFilter(field_name='days_requested', lookup_expr='lte')
    
    # Priority filter
    priority = filters.ChoiceFilter(choices=[
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('high', 'عالي'),
        ('urgent', 'عاجل')
    ])
    
    # Approval filters
    approved_by = filters.NumberFilter(field_name='approved_by__id')
    approved_at_from = filters.DateTimeFilter(field_name='approved_at', lookup_expr='gte')
    approved_at_to = filters.DateTimeFilter(field_name='approved_at', lookup_expr='lte')
    
    # Current/future filters
    is_current = filters.BooleanFilter(method='filter_is_current')
    is_future = filters.BooleanFilter(method='filter_is_future')
    is_past = filters.BooleanFilter(method='filter_is_past')
    
    class Meta:
        model = LeaveRequest
        fields = [
            'employee', 'employee_number', 'department', 'leave_type', 'status',
            'start_date', 'start_date_from', 'start_date_to',
            'end_date', 'end_date_from', 'end_date_to',
            'requested_at_from', 'requested_at_to',
            'days_requested_min', 'days_requested_max', 'priority',
            'approved_by', 'approved_at_from', 'approved_at_to',
            'is_current', 'is_future', 'is_past'
        ]
    
    def filter_is_current(self, queryset, name, value):
        """فلتر الإجازات الحالية"""
        if value is not None:
            today = date.today()
            if value:
                return queryset.filter(start_date__lte=today, end_date__gte=today)
            else:
                return queryset.exclude(start_date__lte=today, end_date__gte=today)
        return queryset
    
    def filter_is_future(self, queryset, name, value):
        """فلتر الإجازات المستقبلية"""
        if value is not None:
            today = date.today()
            if value:
                return queryset.filter(start_date__gt=today)
            else:
                return queryset.exclude(start_date__gt=today)
        return queryset
    
    def filter_is_past(self, queryset, name, value):
        """فلتر الإجازات الماضية"""
        if value is not None:
            today = date.today()
            if value:
                return queryset.filter(end_date__lt=today)
            else:
                return queryset.exclude(end_date__lt=today)
        return queryset