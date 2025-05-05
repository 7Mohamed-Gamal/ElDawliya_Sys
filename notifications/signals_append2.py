# إشارات الاجتماعات (Meetings)
@receiver(post_save, sender=Meeting)
def meeting_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث اجتماع"""
    if created:
        # إنشاء تنبيه للحضور
        for attendee in instance.attendees.all():
            # إنشاء تنبيه لكل شخص مدعو للاجتماع
            create_meeting_notification(
                user=attendee.user,
                title=_('دعوة لاجتماع جديد'),
                message=_(f'تمت دعوتك لحضور اجتماع جديد بعنوان: {instance.title} بتاريخ {instance.date}'),
                priority='medium',
                content_object=instance,
                url=f'/meetings/detail/{instance.pk}/'
            )
    else:
        # إذا تم تغيير حالة الاجتماع أو تاريخه
        old_instance = getattr(instance, '_pre_save_instance', None)
        if old_instance:
            # التحقق من تغيير حالة الاجتماع
            if old_instance.status != instance.status:
                status_text = _('اكتمل') if instance.status == 'completed' else _('تم إلغاء')
                
                # إرسال تنبيه لجميع الحضور
                for attendee in instance.attendees.all():
                    create_meeting_notification(
                        user=attendee.user,
                        title=_(f'{status_text} الاجتماع'),
                        message=_(f'{status_text} الاجتماع: {instance.title} الذي كان مقرراً في {instance.date}'),
                        priority='medium',
                        content_object=instance,
                        url=f'/meetings/detail/{instance.pk}/'
                    )
            
            # التحقق من تغيير تاريخ الاجتماع
            if old_instance.date != instance.date:
                # إرسال تنبيه لجميع الحضور بتغيير التاريخ
                for attendee in instance.attendees.all():
                    create_meeting_notification(
                        user=attendee.user,
                        title=_('تغيير موعد الاجتماع'),
                        message=_(f'تم تغيير موعد الاجتماع: {instance.title} من {old_instance.date} إلى {instance.date}'),
                        priority='high',
                        content_object=instance,
                        url=f'/meetings/detail/{instance.pk}/'
                    )


@receiver(post_save, sender=Attendee)
def meeting_attendee_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة شخص لحضور اجتماع"""
    if created:
        # إنشاء تنبيه للشخص المضاف لحضور الاجتماع
        create_meeting_notification(
            user=instance.user,
            title=_('تمت إضافتك كحاضر لاجتماع'),
            message=_(f'تمت إضافتك كحاضر لاجتماع: {instance.meeting.title} بتاريخ {instance.meeting.date}'),
            priority='medium',
            content_object=instance.meeting,
            url=f'/meetings/detail/{instance.meeting.pk}/'
        )


@receiver(post_save, sender=Task)
def meeting_task_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث مهمة مرتبطة باجتماع"""
    if created:
        # إنشاء تنبيه للشخص المكلف بالمهمة
        create_meeting_notification(
            user=instance.assigned_to,
            title=_('تم تكليفك بمهمة جديدة في اجتماع'),
            message=_(f'تم تكليفك بمهمة جديدة بعنوان: {instance.description} مرتبطة باجتماع {instance.meeting.title}'),
            priority='medium',
            content_object=instance,
            url=f'/tasks/{instance.pk}/'
        )
    else:
        # إذا تم تغيير حالة المهمة
        if instance.status == 'completed' and instance.meeting:
            # إنشاء تنبيه لمنشئ المهمة
            create_meeting_notification(
                user=instance.created_by,
                title=_('تم إكمال مهمة اجتماع'),
                message=_(f'تم إكمال المهمة: {instance.description} المرتبطة باجتماع {instance.meeting.title}'),
                priority='medium',
                content_object=instance,
                url=f'/tasks/{instance.pk}/'
            )
