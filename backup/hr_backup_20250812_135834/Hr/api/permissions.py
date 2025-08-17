"""
HR API Permissions - صلاحيات واجهات برمجة التطبيقات للموارد البشرية
"""
from rest_framework import permissions
from django.contrib.auth.models import Group

class IsHRStaffOrReadOnly(permissions.BasePermission):
    """
    صلاحية للموظفين في قسم الموارد البشرية أو القراءة فقط
    """
    
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for HR staff
        if request.user and request.user.is_authenticated:
            # Check if user is superuser
            if request.user.is_superuser:
                return True
            
            # Check if user has HR staff role
            if hasattr(request.user, 'employee'):
                employee = request.user.employee
                return (
                    employee.is_hr_staff or 
                    employee.department.name in ['الموارد البشرية', 'Human Resources'] or
                    request.user.groups.filter(name__in=['HR_Staff', 'HR_Manager']).exists()
                )
        
        return False

class IsHRManagerOrReadOnly(permissions.BasePermission):
    """
    صلاحية لمدراء الموارد البشرية أو القراءة فقط
    """
    
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for HR managers
        if request.user and request.user.is_authenticated:
            # Check if user is superuser
            if request.user.is_superuser:
                return True
            
            # Check if user has HR manager role
            if hasattr(request.user, 'employee'):
                employee = request.user.employee
                return (
                    employee.is_hr_manager or
                    employee.job_position.title in ['مدير الموارد البشرية', 'HR Manager'] or
                    request.user.groups.filter(name='HR_Manager').exists()
                )
        
        return False

class IsHRStaffOrOwner(permissions.BasePermission):
    """
    صلاحية لموظفي الموارد البشرية أو مالك السجل
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # HR staff can access all objects
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            if employee.is_hr_staff:
                return True
        
        # Check if user is in HR group
        if request.user.groups.filter(name__in=['HR_Staff', 'HR_Manager']).exists():
            return True
        
        # Owner can access their own records
        if hasattr(obj, 'employee'):
            return obj.employee.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False

class IsOwnerOrHRStaff(permissions.BasePermission):
    """
    صلاحية للمالك أو موظفي الموارد البشرية
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Owner can access their own records
        if hasattr(obj, 'employee') and hasattr(request.user, 'employee'):
            if obj.employee == request.user.employee:
                return True
        
        # HR staff can access all records
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            if employee.is_hr_staff:
                return True
        
        # Check if user is in HR group
        if request.user.groups.filter(name__in=['HR_Staff', 'HR_Manager']).exists():
            return True
        
        return False

class IsManagerOrHRStaff(permissions.BasePermission):
    """
    صلاحية للمدراء أو موظفي الموارد البشرية
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # HR staff can access all records
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            
            # HR staff access
            if employee.is_hr_staff:
                return True
            
            # Manager access to subordinates
            if employee.is_manager:
                if hasattr(obj, 'employee'):
                    return obj.employee.direct_manager == employee
                elif hasattr(obj, 'direct_manager'):
                    return obj.direct_manager == employee
        
        # Check if user is in management groups
        if request.user.groups.filter(name__in=['HR_Staff', 'HR_Manager', 'Department_Manager']).exists():
            return True
        
        return False

class CanApproveLeave(permissions.BasePermission):
    """
    صلاحية الموافقة على الإجازات
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # HR staff can approve all leave requests
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            
            # HR staff can approve
            if employee.is_hr_staff:
                return True
            
            # Direct manager can approve subordinate's leave
            if hasattr(obj, 'employee') and obj.employee.direct_manager == employee:
                return True
            
            # Department manager can approve department employees' leave
            if (employee.is_manager and 
                hasattr(obj, 'employee') and 
                obj.employee.department == employee.department):
                return True
        
        # Check if user has approval permissions
        if request.user.groups.filter(name__in=['HR_Manager', 'Department_Manager', 'Leave_Approver']).exists():
            return True
        
        return False

class CanManageAttendance(permissions.BasePermission):
    """
    صلاحية إدارة الحضور
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has attendance management role
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            if (employee.is_hr_staff or 
                employee.job_position.title in ['مشرف الحضور', 'Attendance Supervisor']):
                return True
        
        # Check if user is in attendance management group
        if request.user.groups.filter(name__in=['HR_Staff', 'Attendance_Manager']).exists():
            return True
        
        return False

class CanManagePayroll(permissions.BasePermission):
    """
    صلاحية إدارة الرواتب
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has payroll management role
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            if (employee.is_hr_staff or 
                employee.job_position.title in ['محاسب الرواتب', 'Payroll Accountant']):
                return True
        
        # Check if user is in payroll management group
        if request.user.groups.filter(name__in=['HR_Staff', 'Payroll_Manager', 'Finance_Staff']).exists():
            return True
        
        return False

class CanViewReports(permissions.BasePermission):
    """
    صلاحية عرض التقارير
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has reporting role
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            if (employee.is_hr_staff or 
                employee.is_manager or
                employee.job_position.level in ['senior', 'manager', 'director']):
                return True
        
        # Check if user is in reporting groups
        if request.user.groups.filter(name__in=[
            'HR_Staff', 'HR_Manager', 'Department_Manager', 
            'Report_Viewer', 'Management'
        ]).exists():
            return True
        
        return False

class CanExportData(permissions.BasePermission):
    """
    صلاحية تصدير البيانات
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has data export role
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            if (employee.is_hr_staff or 
                employee.is_manager):
                return True
        
        # Check if user is in data export groups
        if request.user.groups.filter(name__in=[
            'HR_Staff', 'HR_Manager', 'Data_Export', 'Management'
        ]).exists():
            return True
        
        return False