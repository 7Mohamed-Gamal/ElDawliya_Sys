@receiver(post_save, sender=TblProducts)
def product_added_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة منتج جديد"""
    if created:
        # إنشاء تنبيه بإضافة منتج جديد
        inventory_managers = Employee.objects.filter(department__dept_name__icontains='مخزن')
        for manager in inventory_managers:
            if manager.user:
                create_inventory_notification(
                    user=manager.user,
                    title=_('تمت إضافة منتج جديد'),
                    message=_(f'تمت إضافة منتج جديد: {instance.product_name} بالكمية: {instance.initial_balance or 0}.'),
                    priority='medium',
                    content_object=instance,
                    url=f'/inventory/products/detail/{instance.product_id}/'
                )


@receiver(post_save, sender=TblInvoiceitems)
def inventory_transaction_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إجراء معاملة مخزنية (وارد أو منصرف)"""
    if created:
        # الحصول على المنتج المرتبط بالفاتورة
        product = instance.product
        
        if product:
            inventory_managers = Employee.objects.filter(department__dept_name__icontains='مخزن')
            
            # التحقق من نوع المعاملة (وارد أو منصرف)
            if instance.quantity_elwarad and instance.quantity_elwarad > 0:
                # معاملة وارد
                for manager in inventory_managers:
                    if manager.user:
                        create_inventory_notification(
                            user=manager.user,
                            title=_('معاملة وارد جديدة'),
                            message=_(f'تم إضافة كمية {instance.quantity_elwarad} من المنتج {product.product_name} للمخزن.'),
                            priority='medium',
                            content_object=instance,
                            url=f'/inventory/transactions/detail/{instance.invoice_code_programing}/'
                        )
            
            elif instance.quantity_elmonsarf and instance.quantity_elmonsarf > 0:
                # معاملة منصرف
                for manager in inventory_managers:
                    if manager.user:
                        create_inventory_notification(
                            user=manager.user,
                            title=_('معاملة منصرف جديدة'),
                            message=_(f'تم صرف كمية {instance.quantity_elmonsarf} من المنتج {product.product_name} من المخزن.'),
                            priority='medium',
                            content_object=instance,
                            url=f'/inventory/transactions/detail/{instance.invoice_code_programing}/'
                        )


# إشارات المشتريات (Purchase_orders)
@receiver(post_save, sender=PurchaseRequest)
def purchase_request_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث طلب شراء"""
    if created:
        # إنشاء تنبيه للمديرين المسؤولين عن الموافقة على طلبات الشراء
        purchase_approvers = Employee.objects.filter(department__dept_name__icontains='مشتريات', is_manager=True)
        for approver in purchase_approvers:
            if approver.user:
                create_purchase_notification(
                    user=approver.user,
                    title=_('طلب شراء جديد'),
                    message=_(f'تم تقديم طلب شراء جديد برقم: {instance.request_number} من قبل: {instance.requested_by.get_full_name()}'),
                    priority='medium',
                    content_object=instance,
                    url=f'/purchase/requests/detail/{instance.pk}/'
                )
    else:
        # إذا تم تغيير حالة الطلب
        if instance.status in ['approved', 'rejected'] and instance.requested_by:
            # إنشاء تنبيه لمقدم الطلب
            status_text = _('الموافقة على') if instance.status == 'approved' else _('رفض')
            
            create_purchase_notification(
                user=instance.requested_by,
                title=_(f'تم {status_text} طلب الشراء'),
                message=_(f'تم {status_text} طلب الشراء رقم: {instance.request_number}'),
                priority='high',
                content_object=instance,
                url=f'/purchase/requests/detail/{instance.pk}/'
            )
            
            # إذا تمت الموافقة على الطلب، إنشاء تنبيه للمخزن أيضاً
            if instance.status == 'approved':
                inventory_managers = Employee.objects.filter(department__dept_name__icontains='مخزن')
                for manager in inventory_managers:
                    if manager.user:
                        create_inventory_notification(
                            user=manager.user,
                            title=_('تمت الموافقة على طلب شراء'),
                            message=_(f'تمت الموافقة على طلب الشراء رقم: {instance.request_number}، سيتم توريد المنتجات قريباً.'),
                            priority='medium',
                            content_object=instance,
                            url=f'/inventory/purchase-approved/{instance.pk}/'
                        )
