"""
Unified Data Integration Layer for ElDawliya System
طبقة التكامل الموحدة للبيانات في نظام الدولية

This module provides a centralized data access layer that ensures:
- Consistent data validation across modules
- Real-time synchronization between related entities
- Unified permission checking
- Optimized database queries with caching
- Cross-module data integrity
"""

from django.db import models, transaction
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from django.utils import timezone
from typing import Dict, List, Optional, Any, Union
import logging

# Import models from all modules
from Hr.models import Employee, Department, Job
from tasks.models import Task
from meetings.models import Meeting
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest

User = get_user_model()
logger = logging.getLogger(__name__)


class DataIntegrationService:
    """
    Centralized service for managing data integration across all modules
    خدمة مركزية لإدارة تكامل البيانات عبر جميع الوحدات
    """
    
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.cache_timeout = 300  # 5 minutes default cache
    
    # Employee-related integration methods
    def get_employee_with_relations(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee with all related data (tasks, meetings, etc.)
        جلب الموظف مع جميع البيانات المرتبطة
        """
        cache_key = f"employee_relations_{employee_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            employee = Employee.objects.select_related(
                'department', 'job_position', 'direct_manager'
            ).prefetch_related(
                'employeetask_set',
                'employeeleave_set',
                'attendancerecord_set'
            ).get(emp_id=employee_id)
            
            # Cache the result
            cache.set(cache_key, employee, self.cache_timeout)
            return employee
            
        except Employee.DoesNotExist:
            logger.warning(f"Employee {employee_id} not found")
            return None
    
    def get_employee_tasks_unified(self, employee_id: str) -> List[Dict]:
        """
        Get all tasks assigned to an employee (HR tasks + regular tasks + meeting tasks)
        جلب جميع المهام المخصصة للموظف
        """
        cache_key = f"employee_tasks_unified_{employee_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        unified_tasks = []
        
        try:
            employee = Employee.objects.get(emp_id=employee_id)
            
            # Get HR tasks
            hr_tasks = employee.employeetask_set.select_related('created_by').all()
            for task in hr_tasks:
                unified_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'priority': task.priority,
                    'due_date': task.due_date,
                    'type': 'hr_task',
                    'module': 'hr',
                    'url': f'/Hr/tasks/{task.id}/',
                    'created_by': task.created_by.username if task.created_by else None,
                    'created_at': task.created_at
                })
            
            # Get regular tasks assigned to employee's user account
            if hasattr(employee, 'user'):
                regular_tasks = Task.objects.filter(
                    assigned_to=employee.user
                ).select_related('created_by').all()
                
                for task in regular_tasks:
                    unified_tasks.append({
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'status': task.status,
                        'priority': task.priority,
                        'due_date': task.end_date,
                        'type': 'regular_task',
                        'module': 'tasks',
                        'url': f'/tasks/{task.id}/',
                        'created_by': task.created_by.username if task.created_by else None,
                        'created_at': task.created_at
                    })
            
            # Get meeting tasks
            from meetings.models import MeetingTask
            meeting_tasks = MeetingTask.objects.filter(
                assigned_to=employee.user if hasattr(employee, 'user') else None
            ).select_related('meeting', 'assigned_by').all()
            
            for task in meeting_tasks:
                unified_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'priority': getattr(task, 'priority', 'medium'),
                    'due_date': task.due_date,
                    'type': 'meeting_task',
                    'module': 'meetings',
                    'url': f'/meetings/{task.meeting.id}/tasks/{task.id}/',
                    'created_by': task.assigned_by.username if task.assigned_by else None,
                    'created_at': task.created_at,
                    'meeting_title': task.meeting.title
                })
            
            # Sort by due date and priority
            unified_tasks.sort(key=lambda x: (
                x['due_date'] or timezone.now().date(),
                {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['priority'], 2)
            ))
            
            # Cache the result
            cache.set(cache_key, unified_tasks, self.cache_timeout)
            return unified_tasks
            
        except Employee.DoesNotExist:
            logger.warning(f"Employee {employee_id} not found")
            return []
    
    def get_department_analytics(self, department_id: int) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a department
        جلب التحليلات الشاملة للقسم
        """
        cache_key = f"department_analytics_{department_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            department = Department.objects.get(id=department_id)
            employees = department.employees.filter(working_condition='سارى')
            
            analytics = {
                'department_info': {
                    'id': department.id,
                    'name': department.dept_name,
                    'code': department.dept_code,
                    'manager': department.manager.emp_full_name if department.manager else None
                },
                'employee_count': employees.count(),
                'active_tasks': 0,
                'completed_tasks': 0,
                'overdue_tasks': 0,
                'upcoming_meetings': 0,
                'recent_activities': []
            }
            
            # Calculate task statistics
            for employee in employees:
                if hasattr(employee, 'user'):
                    # Regular tasks
                    user_tasks = Task.objects.filter(assigned_to=employee.user)
                    analytics['active_tasks'] += user_tasks.filter(status__in=['pending', 'in_progress']).count()
                    analytics['completed_tasks'] += user_tasks.filter(status='completed').count()
                    analytics['overdue_tasks'] += user_tasks.filter(
                        end_date__lt=timezone.now().date(),
                        status__in=['pending', 'in_progress']
                    ).count()
                
                # HR tasks
                hr_tasks = employee.employeetask_set.all()
                analytics['active_tasks'] += hr_tasks.filter(status__in=['pending', 'in_progress']).count()
                analytics['completed_tasks'] += hr_tasks.filter(status='completed').count()
                analytics['overdue_tasks'] += hr_tasks.filter(
                    due_date__lt=timezone.now().date(),
                    status__in=['pending', 'in_progress']
                ).count()
            
            # Get upcoming meetings
            analytics['upcoming_meetings'] = Meeting.objects.filter(
                attendee__employee__department=department,
                date_time__gte=timezone.now()
            ).distinct().count()
            
            # Cache the result
            cache.set(cache_key, analytics, self.cache_timeout)
            return analytics
            
        except Department.DoesNotExist:
            logger.warning(f"Department {department_id} not found")
            return {}
    
    # Data validation methods
    def validate_cross_module_data(self, data: Dict[str, Any], module: str) -> Dict[str, List[str]]:
        """
        Validate data consistency across modules
        التحقق من صحة البيانات عبر الوحدات
        """
        errors = {}
        
        if module == 'hr':
            errors.update(self._validate_hr_data(data))
        elif module == 'tasks':
            errors.update(self._validate_task_data(data))
        elif module == 'meetings':
            errors.update(self._validate_meeting_data(data))
        elif module == 'inventory':
            errors.update(self._validate_inventory_data(data))
        elif module == 'purchase_orders':
            errors.update(self._validate_purchase_data(data))
        
        return errors
    
    def _validate_hr_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate HR module data"""
        errors = {}
        
        # Validate employee data
        if 'employee_id' in data:
            if not Employee.objects.filter(emp_id=data['employee_id']).exists():
                errors['employee_id'] = ['Employee does not exist']
        
        # Validate department
        if 'department_id' in data:
            if not Department.objects.filter(id=data['department_id']).exists():
                errors['department_id'] = ['Department does not exist']
        
        return errors
    
    def _validate_task_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate task module data"""
        errors = {}
        
        # Validate assigned user
        if 'assigned_to' in data:
            if not User.objects.filter(id=data['assigned_to']).exists():
                errors['assigned_to'] = ['Assigned user does not exist']
        
        return errors
    
    def _validate_meeting_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate meeting module data"""
        errors = {}
        
        # Validate attendees
        if 'attendees' in data:
            for attendee_id in data['attendees']:
                if not User.objects.filter(id=attendee_id).exists():
                    errors.setdefault('attendees', []).append(f'User {attendee_id} does not exist')
        
        return errors
    
    def _validate_inventory_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate inventory module data"""
        errors = {}
        
        # Validate product
        if 'product_id' in data:
            if not TblProducts.objects.filter(product_id=data['product_id']).exists():
                errors['product_id'] = ['Product does not exist']
        
        return errors
    
    def _validate_purchase_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate purchase order module data"""
        errors = {}
        
        # Validate requester
        if 'requested_by' in data:
            if not User.objects.filter(id=data['requested_by']).exists():
                errors['requested_by'] = ['Requesting user does not exist']
        
        return errors
    
    # Cache management methods
    def invalidate_cache(self, cache_pattern: str):
        """
        Invalidate cache entries matching a pattern
        إلغاء صحة ذاكرة التخزين المؤقت
        """
        # This is a simplified implementation
        # In production, you might want to use Redis with pattern matching
        if cache_pattern.startswith('employee_'):
            cache.delete_many([
                key for key in cache._cache.keys() 
                if key.startswith(cache_pattern)
            ])
    
    def clear_all_cache(self):
        """Clear all integration cache"""
        cache.clear()


# Singleton instance
data_integration_service = DataIntegrationService()
