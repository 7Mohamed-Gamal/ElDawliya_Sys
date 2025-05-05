from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from tasks.models import Task, TaskStep

from .utils import create_meeting_notification

# إشارات المهام (Tasks)
@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث مهمة"""
    if created:
        # إنشاء تنبيه للمستخدم المكلف بالمهمة
        create_meeting_notification(
            user=instance.assigned_to,
            title=_('تم تكليفك بمهمة جديدة'),
            message=_(f'تم تكليفك بمهمة جديدة: {instance.description[:50]}'),
            priority='high',
            content_object=instance,
            url=f'/tasks/{instance.pk}/'
        )
        
        # إنشاء تنبيه للمستخدم الذي أنشأ المهمة (إذا كان مختلفًا)
        if instance.created_by and instance.created_by != instance.assigned_to:
            create_meeting_notification(
                user=instance.created_by,
                title=_('تم إنشاء مهمة جديدة'),
                message=_(f'تم إنشاء مهمة جديدة وتكليفها إلى {instance.assigned_to.username}: {instance.description[:50]}'),
                priority='medium',
                content_object=instance,
                url=f'/tasks/{instance.pk}/'
            )
    else:
        # إذا تم تغيير حالة المهمة
        if instance.status == 'completed':
            # إنشاء تنبيه للمستخدم الذي أنشأ المهمة
            if instance.created_by:
                create_meeting_notification(
                    user=instance.created_by,
                    title=_('تم إكمال المهمة'),
                    message=_(f'تم إكمال المهمة: {instance.description[:50]} بواسطة {instance.assigned_to.username}'),
                    priority='medium',
                    content_object=instance,
                    url=f'/tasks/{instance.pk}/'
                )
        elif instance.status == 'in_progress':
            # إنشاء تنبيه للمستخدم الذي أنشأ المهمة
            if instance.created_by and instance.created_by != instance.assigned_to:
                create_meeting_notification(
                    user=instance.created_by,
                    title=_('تم بدء العمل على المهمة'),
                    message=_(f'تم بدء العمل على المهمة: {instance.description[:50]} بواسطة {instance.assigned_to.username}'),
                    priority='low',
                    content_object=instance,
                    url=f'/tasks/{instance.pk}/'
                )
        elif instance.status == 'canceled':
            # إنشاء تنبيه للمستخدم الذي أنشأ المهمة
            if instance.created_by and instance.created_by != instance.assigned_to:
                create_meeting_notification(
                    user=instance.created_by,
                    title=_('تم إلغاء المهمة'),
                    message=_(f'تم إلغاء المهمة: {instance.description[:50]}'),
                    priority='medium',
                    content_object=instance,
                    url=f'/tasks/{instance.pk}/'
                )


@receiver(post_save, sender=TaskStep)
def task_step_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة خطوة جديدة للمهمة"""
    if created:
        # الحصول على المهمة المرتبطة
        task = instance.task
        
        # إنشاء تنبيه للمستخدم الذي أنشأ المهمة (إذا كان مختلفًا عن المكلف بالمهمة)
        if task.created_by and task.created_by != task.assigned_to:
            create_meeting_notification(
                user=task.created_by,
                title=_('تم إضافة خطوة جديدة للمهمة'),
                message=_(f'تم إضافة خطوة جديدة للمهمة: {task.description[:50]}'),
                priority='low',
                content_object=task,
                url=f'/tasks/{task.pk}/'
            )