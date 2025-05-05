from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import F

# استيراد النماذج من التطبيقات الأخرى
from Hr.models.task_models import EmployeeTask, TaskStep
from Hr.models.employee_model import Employee
from Hr.models.leave_models import EmployeeLeave
from Hr.models.car_models import Car
from meetings.models import Meeting, Attendee
from tasks.models import Task, TaskStep as MeetingTaskStep
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem

from .utils import (
    create_hr_notification,
    create_meeting_notification,
    create_inventory_notification,
    create_purchase_notification,
    create_system_notification
)


# إشارات الموارد البشرية (HR)
@receiver(post_save, sender=EmployeeTask)
def employee_task_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث مهمة موظف"""
    if created:
        # إنشاء تنبيه للموظف المكلف بالمهمة
        if instance.employee and instance.employee.user:
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
        if instance.status == 'completed' and instance.employee and instance.employee.user:
            create_hr_notification(
                user=instance.assigned_by,
                title=_('تم إكمال المهمة'),
                message=_(f'تم إكمال المهمة: {instance.title} بواسطة {instance.employee.emp_full_name}'),
                priority='medium',
                content_object=instance,
                url=f'/Hr/tasks/{instance.pk}/'
            )


@receiver(post_save, sender=TaskStep)
def task_step_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة خطوة جديدة للمهمة"""
    if created:
        # الحصول على المهمة المرتبطة
        try:
            task = EmployeeTask.objects.get(pk=instance.task_id)
            
            # إنشاء تنبيه للمستخدم الذي قام بتكليف المهمة
            if task.assigned_by:
                create_hr_notification(
                    user=task.assigned_by,
                    title=_('تم إضافة خطوة جديدة للمهمة'),
                    message=_(f'تم إضافة خطوة جديدة للمهمة: {task.title}'),
                    priority='low',
                    content_object=task,
                    url=f'/Hr/tasks/{task.pk}/'
                )
        except EmployeeTask.DoesNotExist:
            pass


@receiver(post_save, sender=EmployeeLeave)
def employee_leave_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث طلب إجازة"""
    if created:
        # إنشاء تنبيه للمدير
        managers = Employee.objects.filter(is_manager=True)
        for manager in managers:
            if manager.user:
                create_hr_notification(
                    user=manager.user,
                    title=_('طلب إجازة جديد'),
                    message=_(f'تم تقديم طلب إجازة جديد من قبل: {instance.employee.emp_full_name}'),
                    priority='medium',
                    content_object=instance,
                    url=f'/Hr/leaves/{instance.pk}/'
                )
    else:
        # إذا تم تغيير حالة الإجازة
        if instance.status in ['approved', 'rejected'] and instance.employee.user:
            status_text = _('الموافقة على') if instance.status == 'approved' else _('رفض')
            create_hr_notification(
                user=instance.employee.user,
                title=_(f'تم {status_text} طلب الإجازة'),
                message=_(f'تم {status_text} طلب الإجازة الخاص بك من تاريخ {instance.start_date} إلى {instance.end_date}'),
                priority='high',
                content_object=instance,
                url=f'/Hr/leaves/{instance.pk}/'
            )


@receiver(pre_save, sender=Employee)
def employee_health_card_expiry_notification(sender, instance, **kwargs):
    """إنشاء تنبيه عند اقتراب انتهاء البطاقة الصحية"""
    # التحقق من وجود القيمة الأصلية للموظف (في حالة التعديل)
    if instance.pk:
        try:
            old_instance = Employee.objects.get(pk=instance.pk)
            
            # التحقق من تغيير تاريخ انتهاء البطاقة الصحية أو تعيين تاريخ جديد
            if (old_instance.health_card_expiration_date != instance.health_card_expiration_date and 
                    instance.health_card_expiration_date is not None):
                
                # إنشاء تنبيه للمستخدم المسؤول عن الموارد البشرية
                hr_managers = Employee.objects.filter(is_manager=True)
                for manager in hr_managers:
                    if manager.user:
                        create_hr_notification(
                            user=manager.user,
                            title=_('تحديث تاريخ انتهاء البطاقة الصحية'),
                            message=_(f'تم تحديث تاريخ انتهاء البطاقة الصحية للموظف {instance.emp_full_name} إلى {instance.health_card_expiration_date}'),
                            priority='medium',
                            content_object=instance,
                            url=f'/Hr/employees/detail/{instance.emp_id}/'
                        )
                
                # إنشاء تنبيه للموظف نفسه
                if instance.user:
                    create_hr_notification(
                        user=instance.user,
                        title=_('تحديث تاريخ انتهاء البطاقة الصحية'),
                        message=_(f'تم تحديث تاريخ انتهاء البطاقة الصحية الخاصة بك إلى {instance.health_card_expiration_date}'),
                        priority='medium',
                        content_object=instance,
                        url=f'/Hr/employees/profile/'
                    )
        except Employee.DoesNotExist:
            pass
