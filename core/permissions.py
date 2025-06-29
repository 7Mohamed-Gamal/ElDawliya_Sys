"""
Unified Permission System for ElDawliya System
نظام الصلاحيات الموحد لنظام الدولية

This module provides centralized permission checking across all modules
ensuring consistent access control and security.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from typing import Dict, List, Optional, Any
import logging

# Import models from all modules
from Hr.models import Employee, Department
from tasks.models import Task
from meetings.models import Meeting
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest

User = get_user_model()
logger = logging.getLogger(__name__)


class UnifiedPermissionService:
    """
    Centralized permission service for all modules
    خدمة الصلاحيات المركزية لجميع الوحدات
    """
    
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.cache_timeout = 600  # 10 minutes cache for permissions
    
    def has_module_permission(self, module: str, action: str) -> bool:
        """
        Check if user has permission for a specific module action
        التحقق من صلاحية المستخدم لإجراء معين في وحدة
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        if self.user.is_superuser:
            return True
        
        cache_key = f"user_permission_{self.user.id}_{module}_{action}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Check specific module permissions
        has_permission = False
        
        if module == 'hr':
            has_permission = self._check_hr_permission(action)
        elif module == 'tasks':
            has_permission = self._check_task_permission(action)
        elif module == 'meetings':
            has_permission = self._check_meeting_permission(action)
        elif module == 'inventory':
            has_permission = self._check_inventory_permission(action)
        elif module == 'purchase_orders':
            has_permission = self._check_purchase_permission(action)
        elif module == 'admin':
            has_permission = self.user.is_staff
        
        # Cache the result
        cache.set(cache_key, has_permission, self.cache_timeout)
        return has_permission
    
    def _check_hr_permission(self, action: str) -> bool:
        """Check HR module permissions"""
        permission_map = {
            'view': 'Hr.view_employee',
            'add': 'Hr.add_employee',
            'change': 'Hr.change_employee',
            'delete': 'Hr.delete_employee',
            'view_salary': 'Hr.view_salary_report',
            'view_attendance': 'Hr.view_attendance_report',
            'export_data': 'Hr.export_salary_report'
        }
        
        permission_name = permission_map.get(action)
        if permission_name:
            return self.user.has_perm(permission_name)
        
        return False
    
    def _check_task_permission(self, action: str) -> bool:
        """Check task module permissions"""
        permission_map = {
            'view': 'tasks.view_task',
            'add': 'tasks.add_task',
            'change': 'tasks.change_task',
            'delete': 'tasks.delete_task'
        }
        
        permission_name = permission_map.get(action)
        if permission_name:
            return self.user.has_perm(permission_name)
        
        return False
    
    def _check_meeting_permission(self, action: str) -> bool:
        """Check meeting module permissions"""
        permission_map = {
            'view': 'meetings.view_meeting',
            'add': 'meetings.add_meeting',
            'change': 'meetings.change_meeting',
            'delete': 'meetings.delete_meeting'
        }
        
        permission_name = permission_map.get(action)
        if permission_name:
            return self.user.has_perm(permission_name)
        
        return False
    
    def _check_inventory_permission(self, action: str) -> bool:
        """Check inventory module permissions"""
        permission_map = {
            'view': 'inventory.view_tblproducts',
            'add': 'inventory.add_tblproducts',
            'change': 'inventory.change_tblproducts',
            'delete': 'inventory.delete_tblproducts'
        }
        
        permission_name = permission_map.get(action)
        if permission_name:
            return self.user.has_perm(permission_name)
        
        return False
    
    def _check_purchase_permission(self, action: str) -> bool:
        """Check purchase order module permissions"""
        permission_map = {
            'view': 'Purchase_orders.view_purchaserequest',
            'add': 'Purchase_orders.add_purchaserequest',
            'change': 'Purchase_orders.change_purchaserequest',
            'delete': 'Purchase_orders.delete_purchaserequest'
        }
        
        permission_name = permission_map.get(action)
        if permission_name:
            return self.user.has_perm(permission_name)
        
        return False
    
    def can_access_employee_data(self, employee_id: str) -> bool:
        """
        Check if user can access specific employee data
        التحقق من إمكانية الوصول لبيانات موظف معين
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        if self.user.is_superuser:
            return True
        
        try:
            employee = Employee.objects.get(emp_id=employee_id)
            
            # Check if user is the employee themselves
            if hasattr(employee, 'user') and employee.user == self.user:
                return True
            
            # Check if user is the employee's manager
            if employee.direct_manager and hasattr(employee.direct_manager, 'user'):
                if employee.direct_manager.user == self.user:
                    return True
            
            # Check if user has HR permissions
            if self.has_module_permission('hr', 'view'):
                return True
            
            # Check if user is in the same department and has department permissions
            user_employee = Employee.objects.filter(user=self.user).first()
            if user_employee and user_employee.department == employee.department:
                return self.user.has_perm('Hr.view_department_employees')
            
            return False
            
        except Employee.DoesNotExist:
            return False
    
    def can_modify_task(self, task_id: int, task_type: str = 'regular') -> bool:
        """
        Check if user can modify a specific task
        التحقق من إمكانية تعديل مهمة معينة
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        if self.user.is_superuser:
            return True
        
        try:
            if task_type == 'regular':
                task = Task.objects.get(id=task_id)
                # User can modify if they created it or it's assigned to them
                return (task.created_by == self.user or 
                       task.assigned_to == self.user or
                       self.has_module_permission('tasks', 'change'))
            
            elif task_type == 'meeting':
                from meetings.models import MeetingTask
                task = MeetingTask.objects.get(id=task_id)
                # User can modify if they created it or it's assigned to them
                return (task.assigned_by == self.user or 
                       task.assigned_to == self.user or
                       self.has_module_permission('meetings', 'change'))
            
            elif task_type == 'hr':
                from Hr.models import EmployeeTask
                task = EmployeeTask.objects.get(id=task_id)
                # User can modify if they created it or have HR permissions
                return (task.created_by == self.user or
                       self.has_module_permission('hr', 'change'))
            
            return False
            
        except (Task.DoesNotExist, Exception):
            return False
    
    def get_user_accessible_departments(self) -> List[Department]:
        """
        Get list of departments user can access
        جلب قائمة الأقسام التي يمكن للمستخدم الوصول إليها
        """
        if not self.user or not self.user.is_authenticated:
            return []
        
        if self.user.is_superuser or self.has_module_permission('hr', 'view'):
            return list(Department.objects.all())
        
        # Get user's department
        user_employee = Employee.objects.filter(user=self.user).first()
        if user_employee:
            return [user_employee.department]
        
        return []
    
    def get_user_permissions_summary(self) -> Dict[str, Dict[str, bool]]:
        """
        Get comprehensive summary of user permissions
        جلب ملخص شامل لصلاحيات المستخدم
        """
        if not self.user or not self.user.is_authenticated:
            return {}
        
        modules = ['hr', 'tasks', 'meetings', 'inventory', 'purchase_orders']
        actions = ['view', 'add', 'change', 'delete']
        
        permissions = {}
        for module in modules:
            permissions[module] = {}
            for action in actions:
                permissions[module][action] = self.has_module_permission(module, action)
        
        # Add special permissions
        permissions['admin'] = {
            'access': self.user.is_staff,
            'superuser': self.user.is_superuser
        }
        
        return permissions
    
    def invalidate_user_permissions_cache(self):
        """
        Invalidate all cached permissions for the user
        إلغاء صحة جميع الصلاحيات المخزنة مؤقتاً للمستخدم
        """
        if self.user:
            cache_pattern = f"user_permission_{self.user.id}_*"
            # In a real implementation, you'd use Redis pattern matching
            # For now, we'll clear the entire cache
            cache.clear()


# Decorator for view permission checking
def require_permission(module: str, action: str):
    """
    Decorator to require specific permission for a view
    مُزخرف لطلب صلاحية معينة للعرض
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            permission_service = UnifiedPermissionService(request.user)
            if not permission_service.has_module_permission(module, action):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("ليس لديك صلاحية للوصول لهذه الصفحة")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Singleton instance
permission_service = UnifiedPermissionService()
