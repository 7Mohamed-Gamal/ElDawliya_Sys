"""HR API Permissions

This module contains custom permission classes for the HR API endpoints.
"""

from rest_framework import permissions
from django.contrib.auth.models import Group


class IsHRManager(permissions.BasePermission):
    """
    Custom permission to only allow HR managers to access certain endpoints.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is in HR Manager group
        return request.user.groups.filter(name='HR Manager').exists() or request.user.is_superuser


class IsHRStaff(permissions.BasePermission):
    """
    Custom permission to only allow HR staff to access HR endpoints.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is in HR Staff or HR Manager group
        hr_groups = ['HR Staff', 'HR Manager']
        return (
            request.user.groups.filter(name__in=hr_groups).exists() or 
            request.user.is_superuser
        )


class IsEmployeeOwnerOrHRStaff(permissions.BasePermission):
    """
    Custom permission to allow employees to access their own data or HR staff to access all.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # HR staff can access all employee data
        hr_groups = ['HR Staff', 'HR Manager']
        if (request.user.groups.filter(name__in=hr_groups).exists() or 
            request.user.is_superuser):
            return True
        
        # Employees can only access their own data
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # For employee objects, check if the user is the employee
        if hasattr(obj, 'email') and obj.email == request.user.email:
            return True
        
        return False


class IsPayrollManager(permissions.BasePermission):
    """
    Custom permission to only allow payroll managers to access payroll endpoints.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is in Payroll Manager group
        payroll_groups = ['Payroll Manager', 'HR Manager']
        return (
            request.user.groups.filter(name__in=payroll_groups).exists() or 
            request.user.is_superuser
        )


class IsAttendanceManager(permissions.BasePermission):
    """
    Custom permission to only allow attendance managers to manage attendance.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is in Attendance Manager group
        attendance_groups = ['Attendance Manager', 'HR Manager']
        return (
            request.user.groups.filter(name__in=attendance_groups).exists() or 
            request.user.is_superuser
        )


class CanViewReports(permissions.BasePermission):
    """
    Custom permission for viewing reports.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Users who can view reports
        report_groups = ['HR Manager', 'HR Staff', 'Payroll Manager', 'Department Manager']
        return (
            request.user.groups.filter(name__in=report_groups).exists() or 
            request.user.is_superuser
        )


class CanManageOrganization(permissions.BasePermission):
    """
    Custom permission for managing organizational structure.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only HR managers and system admins can manage organizational structure
        return (
            request.user.groups.filter(name='HR Manager').exists() or 
            request.user.is_superuser
        )


class ReadOnlyOrHRStaff(permissions.BasePermission):
    """
    Custom permission to allow read-only access to all authenticated users,
    but write access only to HR staff.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for HR staff
        hr_groups = ['HR Staff', 'HR Manager']
        return (
            request.user.groups.filter(name__in=hr_groups).exists() or 
            request.user.is_superuser
        )


class DepartmentManagerPermission(permissions.BasePermission):
    """
    Custom permission for department managers to access their department's data.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # HR staff can access all data
        hr_groups = ['HR Staff', 'HR Manager']
        if (request.user.groups.filter(name__in=hr_groups).exists() or 
            request.user.is_superuser):
            return True
        
        # Department managers can access their department's data
        if request.user.groups.filter(name='Department Manager').exists():
            # Check if the object belongs to the manager's department
            if hasattr(obj, 'department'):
                # Get the user's employee record to find their department
                try:
                    from Hr.models.employee.employee_models import Employee
                    employee = Employee.objects.get(email=request.user.email)
                    return obj.department == employee.department
                except Employee.DoesNotExist:
                    return False
        
        return False