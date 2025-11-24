from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import F

# استيراد النماذج من التطبيقات الأخرى
# Temporarily disabled due to model conflicts
# from Hr.models.task_models import EmployeeTask, TaskStep
# Temporarily disabled - will be replaced with new modular HR apps
# from Hr.models.employee.employee_models import Employee
# from Hr.models.leave.leave_request_models import LeaveRequest
# from Hr.models import Car

# استيراد ملفات الإشارات الإضافية
# TODO: Replace wildcard import
# from .signals_meetings import specific_items
# TODO: Replace wildcard import
# from .signals_tasks import specific_items
# TODO: Replace wildcard import
# from .signals_inventory import specific_items
# TODO: Replace wildcard import
# from .signals_purchase import specific_items
# TODO: Replace wildcard import
# from .signals_inventory_purchase import specific_items
# Temporarily commented out to avoid import errors
# from meetings.models import Meeting, Attendee
# from tasks.models import Task, TaskStep as MeetingTaskStep
# from inventory.models import TblProducts, TblInvoiceitems
# from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem

from .utils import (
    create_hr_notification,
    create_meeting_notification,
    create_inventory_notification,
    create_purchase_notification,
    create_system_notification
)


# إشارات الموارد البشرية (HR) - temporarily disabled due to model conflicts
# @receiver(post_save, sender=EmployeeTask)
def employee_task_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث مهمة موظف"""
    if created:
        # إنشاء تنبيه للموظف المكلف بالمهمة
        # تحقق من وجود المستخدم المرتبط بالموظف (إذا كان موجوداً)
        if instance.employee and hasattr(instance.employee, 'user') and instance.employee.user:
            create_hr_notification(
                user=instance.employee.user,
                title=_('تم تكليفك بمهمة جديدة'),
                message=_(f'تم تكليفك بمهمة جديدة بعنوان: {instance.title}'),
                priority='medium',
                content_object=instance,
                url=f'/Hr/tasks/{instance.pk}/'
            )
    else:
        # إذا تم تغيير حالة المهمة إلى مكتملة
        if instance.status == 'completed' and instance.assigned_by:
            create_hr_notification(
                user=instance.assigned_by,
                title=_('تم إكمال المهمة'),
                message=_(f'تم إكمال المهمة: {instance.title} بواسطة {instance.employee.emp_full_name}'),
                priority='medium',
                content_object=instance,
                url=f'/Hr/tasks/{instance.pk}/'
            )


# Temporarily disabled - will be replaced with new modular HR apps
# @receiver(post_save, sender=TaskStep)
# @receiver(post_save, sender=LeaveRequest)
# @receiver(pre_save, sender=Employee)
# @receiver(pre_save, sender=Car)
# All HR-related signals temporarily disabled until new modular apps are created
