from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from meetings.models import Meeting, Attendee
from tasks.models import Task, TaskStep as MeetingTaskStep

from .utils import create_meeting_notification

# إشارات الاجتماعات (Meetings)
@receiver(post_save, sender=Meeting)
def meeting_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث اجتماع"""
    if created:
        # إنشاء تنبيه للمنشئ
        create_meeting_notification(
            user=instance.created_by,
            title=_('تم إنشاء اجتماع جديد'),
            message=_(f'تم إنشاء اجتماع جديد بعنوان: {instance.title}'),
            priority='medium',
            content_object=instance,
            url=f'/meetings/detail/{instance.pk}/'
        )
        
        # إنشاء تنبيهات للحضور
        attendees = Attendee.objects.filter(meeting=instance)
        for attendee in attendees:
            if attendee.user != instance.created_by:  # تجنب إرسال تنبيه مكرر للمنشئ
                create_meeting_notification(
                    user=attendee.user,
                    title=_('دعوة لحضور اجتماع جديد'),
                    message=_(f'تمت دعوتك لحضور اجتماع بعنوان: {instance.title} في تاريخ {instance.date}'),
                    priority='high',
                    content_object=instance,
                    url=f'/meetings/detail/{instance.pk}/'
                )
    else:
        # إذا تم تغيير حالة الاجتماع
        if instance.status == 'completed':
            # إنشاء تنبيه للمنشئ
            create_meeting_notification(
                user=instance.created_by,
                title=_('تم إكمال الاجتماع'),
                message=_(f'تم إكمال الاجتماع: {instance.title}'),
                priority='medium',
                content_object=instance,
                url=f'/meetings/detail/{instance.pk}/'
            )
            
            # إنشاء تنبيهات للحضور
            attendees = Attendee.objects.filter(meeting=instance)
            for attendee in attendees:
                if attendee.user != instance.created_by:  # تجنب إرسال تنبيه مكرر للمنشئ
                    create_meeting_notification(
                        user=attendee.user,
                        title=_('تم إكمال الاجتماع'),
                        message=_(f'تم إكمال الاجتماع: {instance.title}'),
                        priority='medium',
                        content_object=instance,
                        url=f'/meetings/detail/{instance.pk}/'
                    )
        elif instance.status == 'cancelled':
            # إنشاء تنبيهات للحضور عند إلغاء الاجتماع
            attendees = Attendee.objects.filter(meeting=instance)
            for attendee in attendees:
                create_meeting_notification(
                    user=attendee.user,
                    title=_('تم إلغاء الاجتماع'),
                    message=_(f'تم إلغاء الاجتماع: {instance.title}'),
                    priority='high',
                    content_object=instance,
                    url=f'/meetings/detail/{instance.pk}/'
                )


@receiver(post_save, sender=Attendee)
def attendee_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة حضور جديد للاجتماع"""
    if created:
        # إنشاء تنبيه للمستخدم المضاف
        create_meeting_notification(
            user=instance.user,
            title=_('تمت إضافتك إلى اجتماع'),
            message=_(f'تمت إضافتك إلى اجتماع بعنوان: {instance.meeting.title} في تاريخ {instance.meeting.date}'),
            priority='medium',
            content_object=instance.meeting,
            url=f'/meetings/detail/{instance.meeting.pk}/'
        )