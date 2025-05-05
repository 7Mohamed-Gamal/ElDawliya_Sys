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
