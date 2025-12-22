"""
Signals for meeting-related notifications.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

try:
    from apps.projects.meetings.models import Meeting, Attendee
    MEETINGS_AVAILABLE = True
except ImportError:
    MEETINGS_AVAILABLE = False

from .utils import create_meeting_notification


if MEETINGS_AVAILABLE:
    @receiver(post_save, sender=Meeting)
    def meeting_created_notification(sender, instance, created, **kwargs):
        """
        Send notification when a new meeting is created.
        """
        if created:
            # Notify all attendees about the new meeting
            for attendee in instance.attendees.all():
                create_meeting_notification(
                    user=attendee.user,
                    meeting=instance,
                    notification_type='meeting_created',
                    message=_('تم إنشاء اجتماع جديد: {}').format(instance.title)
                )


    @receiver(post_save, sender=Meeting)
    def meeting_updated_notification(sender, instance, created, **kwargs):
        """
        Send notification when a meeting is updated.
        """
        if not created:
            # Notify all attendees about the meeting update
            for attendee in instance.attendees.all():
                create_meeting_notification(
                    user=attendee.user,
                    meeting=instance,
                    notification_type='meeting_updated',
                    message=_('تم تحديث الاجتماع: {}').format(instance.title)
                )


    @receiver(post_save, sender=Attendee)
    def attendee_added_notification(sender, instance, created, **kwargs):
        """
        Send notification when an attendee is added to a meeting.
        """
        if created:
            create_meeting_notification(
                user=instance.user,
                meeting=instance.meeting,
                notification_type='meeting_invitation',
                message=_('تمت دعوتك للاجتماع: {}').format(instance.meeting.title)
            )

