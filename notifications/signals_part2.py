@receiver(pre_save, sender=Employee)
def employee_contract_expiry_notification(sender, instance, **kwargs):
    """إنشاء تنبيه عند اقتراب انتهاء العقد"""
    if instance.pk:
        try:
            old_instance = Employee.objects.get(pk=instance.pk)
            
            # التحقق من تغيير تاريخ انتهاء العقد أو تعيين تاريخ جديد
            if (old_instance.contract_expiry_date != instance.contract_expiry_date and 
                    instance.contract_expiry_date is not None):
                
                # إنشاء تنبيه للمستخدمين المسؤولين عن الموارد البشرية
                hr_managers = Employee.objects.filter(is_manager=True)
                for manager in hr_managers:
                    if manager.user:
                        create_hr_notification(
                            user=manager.user,
                            title=_('تحديث تاريخ انتهاء العقد'),
                            message=_(f'تم تحديث تاريخ انتهاء عقد الموظف {instance.emp_full_name} إلى {instance.contract_expiry_date}'),
                            priority='medium',
                            content_object=instance,
                            url=f'/Hr/employees/detail/{instance.emp_id}/'
                        )
                
                # إنشاء تنبيه للموظف نفسه
                if instance.user:
                    create_hr_notification(
                        user=instance.user,
                        title=_('تحديث تاريخ انتهاء العقد'),
                        message=_(f'تم تحديث تاريخ انتهاء عقدك إلى {instance.contract_expiry_date}'),
                        priority='medium',
                        content_object=instance,
                        url=f'/Hr/employees/profile/'
                    )
        except Employee.DoesNotExist:
            pass


@receiver(pre_save, sender=Car)
def car_license_expiry_notification(sender, instance, **kwargs):
    """إنشاء تنبيه عند اقتراب انتهاء رخصة السيارة"""
    if instance.pk:
        try:
            old_instance = Car.objects.get(pk=instance.pk)
            
            # التحقق من تغيير تاريخ انتهاء رخصة السيارة أو تعيين تاريخ جديد
            if (old_instance.car_license_expiration_date != instance.car_license_expiration_date and 
                    instance.car_license_expiration_date is not None):
                
                # إنشاء تنبيه للمستخدمين المسؤولين عن الموارد البشرية
                hr_managers = Employee.objects.filter(is_manager=True)
                for manager in hr_managers:
                    if manager.user:
                        create_hr_notification(
                            user=manager.user,
                            title=_('تحديث تاريخ انتهاء رخصة السيارة'),
                            message=_(f'تم تحديث تاريخ انتهاء رخصة السيارة {instance.car_name} إلى {instance.car_license_expiration_date}'),
                            priority='medium',
                            content_object=instance,
                            url=f'/Hr/cars/detail/{instance.car_id}/'
                        )
        except Car.DoesNotExist:
            pass


@receiver(pre_save, sender=Car)
def driver_license_expiry_notification(sender, instance, **kwargs):
    """إنشاء تنبيه عند اقتراب انتهاء رخصة السائق"""
    if instance.pk:
        try:
            old_instance = Car.objects.get(pk=instance.pk)
            
            # التحقق من تغيير تاريخ انتهاء رخصة السائق أو تعيين تاريخ جديد
            if (old_instance.driver_license_expiration_date != instance.driver_license_expiration_date and 
                    instance.driver_license_expiration_date is not None):
                
                # إنشاء تنبيه للمستخدمين المسؤولين عن الموارد البشرية
                hr_managers = Employee.objects.filter(is_manager=True)
                for manager in hr_managers:
                    if manager.user:
                        create_hr_notification(
                            user=manager.user,
                            title=_('تحديث تاريخ انتهاء رخصة السائق'),
                            message=_(f'تم تحديث تاريخ انتهاء رخصة السائق {instance.driver_name} إلى {instance.driver_license_expiration_date}'),
                            priority='medium',
                            content_object=instance,
                            url=f'/Hr/cars/detail/{instance.car_id}/'
                        )
        except Car.DoesNotExist:
            pass


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


@receiver(post_save, sender=MeetingTaskStep)
def meeting_task_step_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة خطوة جديدة لمهمة اجتماع"""
    if created:
        # الحصول على المهمة المرتبطة
        try:
            task = Task.objects.get(pk=instance.task.pk)
            
            # إنشاء تنبيه للشخص المكلف بالمهمة ومنشئ المهمة
            for user in [task.assigned_to, task.created_by]:
                if user:
                    create_meeting_notification(
                        user=user,
                        title=_('تم إضافة خطوة جديدة لمهمة اجتماع'),
                        message=_(f'تم إضافة خطوة جديدة لمهمة: {task.description} المرتبطة باجتماع {task.meeting.title}'),
                        priority='low',
                        content_object=task,
                        url=f'/tasks/{task.pk}/'
                    )
        except Task.DoesNotExist:
            pass
