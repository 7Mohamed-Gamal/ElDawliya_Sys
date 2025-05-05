@receiver(post_save, sender=PurchaseRequestItem)
def purchase_request_item_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند تغيير حالة عنصر من طلب الشراء"""
    if not created and instance.status in ['approved', 'rejected', 'transferred']:
        # إنشاء تنبيه لمقدم الطلب
        purchase_request = instance.purchase_request
        if purchase_request and purchase_request.requested_by:
            status_text_map = {
                'approved': _('الموافقة على'),
                'rejected': _('رفض'),
                'transferred': _('ترحيل')
            }
            
            status_text = status_text_map.get(instance.status)
            product_name = instance.product.product_name if instance.product else _('منتج')
            
            create_purchase_notification(
                user=purchase_request.requested_by,
                title=_(f'تم {status_text} عنصر من طلب الشراء'),
                message=_(f'تم {status_text} العنصر: {product_name} من طلب الشراء رقم: {purchase_request.request_number}'),
                priority='medium',
                content_object=instance,
                url=f'/purchase/requests/detail/{purchase_request.pk}/'
            )
