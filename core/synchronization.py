"""
Real-time Data Synchronization Service for ElDawliya System
خدمة المزامنة الفورية للبيانات في نظام الدولية

This module handles real-time synchronization between modules and ensures
data consistency across the entire system.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
from typing import Dict, List, Optional, Any
import logging
import json

# Temporarily disabled - will be replaced with new modular HR apps
# from Hr.models import Employee, Department  # Legacy
from django.contrib.auth import get_user_model

# Temporary placeholders until new modular HR apps are created
Employee = get_user_model()  # Placeholder

class Department:
    """Temporary placeholder class"""
    def __init__(self):
        self.id = 0
        self.dept_name = ""
from tasks.models import Task
from meetings.models import Meeting, MeetingTask
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest

logger = logging.getLogger(__name__)


class SynchronizationService:
    """
    Service for handling real-time data synchronization
    خدمة التعامل مع المزامنة الفورية للبيانات
    """
    
    def __init__(self):
        self.sync_log = []
        self.cache_timeout = 300
    
    def sync_employee_data(self, employee: Employee, action: str):
        """
        Synchronize employee data across all modules
        مزامنة بيانات الموظف عبر جميع الوحدات
        """
        try:
            with transaction.atomic():
                # Update related tasks
                if hasattr(employee, 'user') and employee.user:
                    if action == 'update':
                        # Update task assignments if employee department changed
                        Task.objects.filter(assigned_to=employee.user).update(
                            updated_at=timezone.now()
                        )
                    
                    elif action == 'delete':
                        # Reassign tasks to department manager or mark as unassigned
                        tasks_to_reassign = Task.objects.filter(assigned_to=employee.user)
                        if employee.department and employee.department.manager:
                            if hasattr(employee.department.manager, 'user'):
                                tasks_to_reassign.update(
                                    assigned_to=employee.department.manager.user,
                                    updated_at=timezone.now()
                                )
                        else:
                            tasks_to_reassign.update(
                                assigned_to=None,
                                updated_at=timezone.now()
                            )
                
                # Update meeting attendances
                if action == 'delete':
                    # Remove from future meetings
                    future_meetings = Meeting.objects.filter(
                        date_time__gte=timezone.now(),
                        attendee__employee=employee
                    )
                    for meeting in future_meetings:
                        meeting.attendee_set.filter(employee=employee).delete()
                
                # Invalidate related caches
                self._invalidate_employee_caches(employee)
                
                # Log the synchronization
                self._log_sync_action('employee', employee.emp_id, action)
                
        except Exception as e:
            logger.error(f"Error synchronizing employee data: {e}")
    
    def sync_department_data(self, department: Department, action: str):
        """
        Synchronize department data across modules
        مزامنة بيانات القسم عبر الوحدات
        """
        try:
            with transaction.atomic():
                if action == 'update':
                    # Update all employees in department
                    department.employees.update(updated_at=timezone.now())
                    
                elif action == 'delete':
                    # Move employees to default department or mark as unassigned
                    default_dept = Department.objects.filter(dept_name='عام').first()
                    if default_dept:
                        department.employees.update(department=default_dept)
                
                # Invalidate related caches
                self._invalidate_department_caches(department)
                
                # Log the synchronization
                self._log_sync_action('department', department.id, action)
                
        except Exception as e:
            logger.error(f"Error synchronizing department data: {e}")
    
    def sync_task_data(self, task: Task, action: str):
        """
        Synchronize task data across modules
        مزامنة بيانات المهمة عبر الوحدات
        """
        try:
            with transaction.atomic():
                if action in ['create', 'update']:
                    # Update related employee task counts
                    if task.assigned_to:
                        employee = Employee.objects.filter(user=task.assigned_to).first()
                        if employee:
                            self._invalidate_employee_caches(employee)
                
                # Invalidate task-related caches
                cache.delete_many([
                    f"user_tasks_{task.assigned_to.id}" if task.assigned_to else None,
                    f"task_statistics_{task.assigned_to.id}" if task.assigned_to else None
                ])
                
                # Log the synchronization
                self._log_sync_action('task', task.id, action)
                
        except Exception as e:
            logger.error(f"Error synchronizing task data: {e}")
    
    def sync_meeting_data(self, meeting: Meeting, action: str):
        """
        Synchronize meeting data across modules
        مزامنة بيانات الاجتماع عبر الوحدات
        """
        try:
            with transaction.atomic():
                if action in ['create', 'update']:
                    # Update attendee notifications
                    for attendee in meeting.attendee_set.all():
                        if attendee.employee:
                            self._invalidate_employee_caches(attendee.employee)
                
                elif action == 'delete':
                    # Clean up related meeting tasks
                    MeetingTask.objects.filter(meeting=meeting).delete()
                
                # Invalidate meeting-related caches
                cache.delete_many([
                    f"meeting_attendees_{meeting.id}",
                    f"upcoming_meetings"
                ])
                
                # Log the synchronization
                self._log_sync_action('meeting', meeting.id, action)
                
        except Exception as e:
            logger.error(f"Error synchronizing meeting data: {e}")
    
    def sync_inventory_data(self, product: TblProducts, action: str):
        """
        Synchronize inventory data across modules
        مزامنة بيانات المخزون عبر الوحدات
        """
        try:
            with transaction.atomic():
                if action in ['create', 'update']:
                    # Update related purchase requests
                    related_requests = PurchaseRequest.objects.filter(
                        purchaserequestitem__product=product
                    ).distinct()
                    
                    for request in related_requests:
                        request.updated_at = timezone.now()
                        request.save()
                
                # Invalidate inventory-related caches
                cache.delete_many([
                    f"product_details_{product.product_id}",
                    "inventory_summary",
                    "low_stock_products"
                ])
                
                # Log the synchronization
                self._log_sync_action('inventory', product.product_id, action)
                
        except Exception as e:
            logger.error(f"Error synchronizing inventory data: {e}")
    
    def _invalidate_employee_caches(self, employee: Employee):
        """Invalidate all caches related to an employee"""
        cache_keys = [
            f"employee_relations_{employee.emp_id}",
            f"employee_tasks_unified_{employee.emp_id}",
            f"employee_analytics_{employee.emp_id}"
        ]
        
        if employee.department:
            cache_keys.append(f"department_analytics_{employee.department.id}")
        
        cache.delete_many(cache_keys)
    
    def _invalidate_department_caches(self, department: Department):
        """Invalidate all caches related to a department"""
        cache_keys = [
            f"department_analytics_{department.id}",
            f"department_employees_{department.id}",
            "department_summary"
        ]
        cache.delete_many(cache_keys)
    
    def _log_sync_action(self, entity_type: str, entity_id: Any, action: str):
        """Log synchronization action for debugging"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'entity_type': entity_type,
            'entity_id': str(entity_id),
            'action': action
        }
        
        self.sync_log.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.sync_log) > 100:
            self.sync_log = self.sync_log[-100:]
        
        logger.info(f"Sync: {entity_type} {entity_id} - {action}")
    
    def get_sync_log(self) -> List[Dict]:
        """Get recent synchronization log"""
        return self.sync_log.copy()
    
    def clear_sync_log(self):
        """Clear synchronization log"""
        self.sync_log.clear()


# Singleton instance
sync_service = SynchronizationService()


# Signal handlers for automatic synchronization
@receiver(post_save)
def employee_post_save(sender, instance, created, **kwargs):
    """Handle employee save events"""
    action = 'create' if created else 'update'
    sync_service.sync_employee_data(instance, action)


@receiver(post_delete)
def employee_post_delete(sender, instance, **kwargs):
    """Handle employee delete events"""
    sync_service.sync_employee_data(instance, 'delete')


@receiver(post_save)
def department_post_save(sender, instance, created, **kwargs):
    """Handle department save events"""
    action = 'create' if created else 'update'
    sync_service.sync_department_data(instance, action)


@receiver(post_delete)
def department_post_delete(sender, instance, **kwargs):
    """Handle department delete events"""
    sync_service.sync_department_data(instance, 'delete')


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Handle task save events"""
    action = 'create' if created else 'update'
    sync_service.sync_task_data(instance, action)


@receiver(post_delete, sender=Task)
def task_post_delete(sender, instance, **kwargs):
    """Handle task delete events"""
    sync_service.sync_task_data(instance, 'delete')


@receiver(post_save, sender=Meeting)
def meeting_post_save(sender, instance, created, **kwargs):
    """Handle meeting save events"""
    action = 'create' if created else 'update'
    sync_service.sync_meeting_data(instance, action)


@receiver(post_delete, sender=Meeting)
def meeting_post_delete(sender, instance, **kwargs):
    """Handle meeting delete events"""
    sync_service.sync_meeting_data(instance, 'delete')


@receiver(post_save, sender=TblProducts)
def product_post_save(sender, instance, created, **kwargs):
    """Handle product save events"""
    action = 'create' if created else 'update'
    sync_service.sync_inventory_data(instance, action)
