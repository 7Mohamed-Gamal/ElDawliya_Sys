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


# إشارات المخزن (Inventory)
@receiver(post_save, sender=TblProducts)
def product_threshold_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند وصول المنتج للحد الأدنى أو نفاذه"""
    # التحقق من وجود المعلومات الأصلية للمنتج (في حالة التعديل)
    if instance.pk and not created:
        try:
            # التحقق مما إذا كان المنتج وصل للحد الأدنى أو نفاذه من المخزن
            if instance.qte_in_stock is not None:
                inventory_managers = Employee.objects.filter(department__dept_name__icontains='مخزن', is_manager=True)
                
                # إذا كان المنتج نفذ (الكمية = 0)
                if instance.qte_in_stock == 0:
                    for manager in inventory_managers:
                        if manager.user:
                            create_inventory_notification(
                                user=manager.user,
                                title=_('نفاذ منتج من المخزن'),
                                message=_(f'المنتج {instance.product_name} قد نفذ من المخزن بالكامل.'),
                                priority='urgent',
                                content_object=instance,
                                url=f'/inventory/products/detail/{instance.product_id}/'
                            )
                
                # إذا كان المنتج وصل للحد الأدنى
                elif (instance.minimum_threshold is not None and 
                      instance.qte_in_stock <= instance.minimum_threshold):
                    for manager in inventory_managers:
                        if manager.user:
                            create_inventory_notification(
                                user=manager.user,
                                title=_('منتج وصل للحد الأدنى'),
                                message=_(f'المنتج {instance.product_name} وصل للحد الأدنى (الكمية الحالية: {instance.qte_in_stock}).'),
                                priority='high',
                                content_object=instance,
                                url=f'/inventory/products/detail/{instance.product_id}/'
                            )
                            
                            # إنشاء تنبيه للمشتريات أيضاً إذا كان المنتج وصل للحد الأدنى
                            purchase_managers = Employee.objects.filter(department__dept_name__icontains='مشتريات', is_manager=True)
                            for pm in purchase_managers:
                                if pm.user:
                                    create_purchase_notification(
                                        user=pm.user,
                                        title=_('منتج بحاجة للطلب'),
                                        message=_(f'المنتج {instance.product_name} وصل للحد الأدنى (الكمية الحالية: {instance.qte_in_stock}) ويحتاج إلى طلب شراء جديد.'),
                                        priority='high',
                                        content_object=instance,
                                        url=f'/inventory/products/detail/{instance.product_id}/'
                                    )
        except Exception:
            pass
