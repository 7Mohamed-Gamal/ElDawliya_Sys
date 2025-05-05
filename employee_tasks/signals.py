from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import EmployeeTask, TaskStep, TaskReminder

# تنفيذ إشارات للمهام
@receiver(post_save, sender=EmployeeTask)
def task_post_save(sender, instance, created, **kwargs):
    """
    معالجة إشارة حفظ المهمة
    """
    # إذا تم تغيير حالة المهمة إلى مكتملة، قم بتعيين تاريخ الإنجاز
    if instance.status == 'completed' and not instance.completion_date:
        instance.completion_date = timezone.now().date()
        # استخدام update() لتجنب تشغيل post_save مرة أخرى
        EmployeeTask.objects.filter(pk=instance.pk).update(completion_date=instance.completion_date)
    
    # إذا تم تغيير حالة المهمة من مكتملة، قم بإزالة تاريخ الإنجاز
    elif instance.status != 'completed' and instance.completion_date:
        # استخدام update() لتجنب تشغيل post_save مرة أخرى
        EmployeeTask.objects.filter(pk=instance.pk).update(completion_date=None)
    
    # إذا كانت نسبة الإنجاز 100%، قم بتعيين الحالة إلى مكتملة
    if instance.progress == 100 and instance.status != 'completed':
        # استخدام update() لتجنب تشغيل post_save مرة أخرى
        EmployeeTask.objects.filter(pk=instance.pk).update(status='completed', completion_date=timezone.now().date())

# تنفيذ إشارات لخطوات المهام
@receiver(post_save, sender=TaskStep)
def task_step_post_save(sender, instance, created, **kwargs):
    """
    معالجة إشارة حفظ خطوة المهمة
    """
    # إذا تم تعيين الخطوة كمكتملة، قم بتعيين تاريخ الإنجاز
    if instance.completed and not instance.completion_date:
        instance.completion_date = timezone.now().date()
        # استخدام update() لتجنب تشغيل post_save مرة أخرى
        TaskStep.objects.filter(pk=instance.pk).update(completion_date=instance.completion_date)
    
    # إذا تم تغيير حالة الخطوة من مكتملة، قم بإزالة تاريخ الإنجاز
    elif not instance.completed and instance.completion_date:
        # استخدام update() لتجنب تشغيل post_save مرة أخرى
        TaskStep.objects.filter(pk=instance.pk).update(completion_date=None)
    
    # تحديث نسبة إنجاز المهمة بناءً على خطواتها
    task = instance.task
    steps_count = task.steps.count()
    
    if steps_count > 0:
        completed_steps = task.steps.filter(completed=True).count()
        progress = int((completed_steps / steps_count) * 100)
        
        # تحديث نسبة الإنجاز فقط إذا كانت مختلفة
        if task.progress != progress:
            # استخدام update() لتجنب تشغيل post_save مرة أخرى
            EmployeeTask.objects.filter(pk=task.pk).update(progress=progress)
            
            # إذا كانت جميع الخطوات مكتملة، قم بتعيين حالة المهمة إلى مكتملة
            if progress == 100 and task.status != 'completed':
                EmployeeTask.objects.filter(pk=task.pk).update(
                    status='completed',
                    completion_date=timezone.now().date()
                )

# تنفيذ إشارات لتذكيرات المهام
@receiver(post_save, sender=TaskReminder)
def task_reminder_post_save(sender, instance, created, **kwargs):
    """
    معالجة إشارة حفظ تذكير المهمة
    """
    # يمكن إضافة منطق إضافي هنا إذا لزم الأمر
    pass
