"""
Signals for task-related notifications.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

try:
    from apps.projects.tasks.models import Task, TaskStep
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False

from .utils import create_notification


if TASKS_AVAILABLE:
    @receiver(post_save, sender=Task)
    def task_created_notification(sender, instance, created, **kwargs):
        """
        Send notification when a new task is created.
        """
        if created and instance.assigned_to:
            create_notification(
                user=instance.assigned_to,
                notification_type='task_assigned',
                title=_('مهمة جديدة'),
                message=_('تم تعيين مهمة جديدة لك: {}').format(instance.title),
                related_object=instance
            )


    @receiver(post_save, sender=Task)
    def task_status_changed_notification(sender, instance, created, **kwargs):
        """
        Send notification when a task status changes.
        """
        if not created and instance.status:
            # Notify task creator about status change
            if instance.created_by and instance.created_by != instance.assigned_to:
                status_text = dict(Task.STATUS_CHOICES).get(instance.status, instance.status)
                create_notification(
                    user=instance.created_by,
                    notification_type='task_status_changed',
                    title=_('تحديث حالة المهمة'),
                    message=_('تم تغيير حالة المهمة "{}" إلى: {}').format(
                        instance.title,
                        status_text
                    ),
                    related_object=instance
                )


    @receiver(post_save, sender=Task)
    def task_due_date_notification(sender, instance, created, **kwargs):
        """
        Send notification when a task is approaching its due date.
        """
        if instance.due_date and instance.assigned_to:
            days_until_due = (instance.due_date - timezone.now().date()).days

            if days_until_due <= 1 and days_until_due >= 0:
                create_notification(
                    user=instance.assigned_to,
                    notification_type='task_due_soon',
                    title=_('مهمة قريبة من الموعد النهائي'),
                    message=_('المهمة "{}" موعدها النهائي خلال {} يوم').format(
                        instance.title,
                        days_until_due
                    ),
                    related_object=instance
                )


    @receiver(post_save, sender=TaskStep)
    def task_step_completed_notification(sender, instance, created, **kwargs):
        """
        Send notification when a task step is completed.
        """
        if not created and instance.is_completed and instance.task.created_by:
            create_notification(
                user=instance.task.created_by,
                notification_type='task_step_completed',
                title=_('اكتمال خطوة في المهمة'),
                message=_('تم إكمال الخطوة "{}" في المهمة "{}"').format(
                    instance.title,
                    instance.task.title
                ),
                related_object=instance.task
            )

