from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem
from accounts.models import Users_Login_New

from .utils import create_purchase_notification

# إشارات طلبات الشراء (Purchase_orders)
@receiver(post_save, sender=PurchaseRequest)
def purchase_request_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إنشاء أو تحديث طلب شراء"""
    if created:
        # إنشاء تنبيه للمستخدم الذي قدم الطلب
        create_purchase_notification(
            user=instance.requested_by,
            title=_('تم إنشاء طلب شراء جديد'),
            message=_(f'تم إنشاء طلب شراء جديد برقم: {instance.request_number}'),
            priority='medium',
            content_object=instance,
            url=f'/purchase/requests/detail/{instance.pk}/'
        )
        
        # إنشاء تنبيهات للمستخدمين المسؤولين عن الموافقة على طلبات الشراء
        # هنا نفترض أن المستخدمين المسؤولين هم المستخدمين النشطين
        # يمكن تعديل هذا الشرط حسب هيكل النظام
        approvers = Users_Login_New.objects.filter(is_active=True)
        for approver in approvers:
            if approver != instance.requested_by:  # تجنب إرسال تنبيه مكرر لمقدم الطلب
                create_purchase_notification(
                    user=approver,
                    title=_('طلب شراء جديد بحاجة للموافقة'),
                    message=_(f'تم إنشاء طلب شراء جديد برقم: {instance.request_number} بواسطة {instance.requested_by.username}'),
                    priority='high',
                    content_object=instance,
                    url=f'/purchase/requests/detail/{instance.pk}/'
                )
    else:
        # إذا تم تغيير حالة الطلب
        if instance.status == 'approved':
            # إنشاء تنبيه لمقدم الطلب
            create_purchase_notification(
                user=instance.requested_by,
                title=_('تمت الموافقة على طلب الشراء'),
                message=_(f'تمت الموافقة على طلب الشراء رقم: {instance.request_number}'),
                priority='high',
                content_object=instance,
                url=f'/purchase/requests/detail/{instance.pk}/'
            )
            
            # إنشاء تنبيه للمستخدم الذي وافق على الطلب
            if instance.approved_by and instance.approved_by != instance.requested_by:
                create_purchase_notification(
                    user=instance.approved_by,
                    title=_('تمت الموافقة على طلب الشراء'),
                    message=_(f'قمت بالموافقة على طلب الشراء رقم: {instance.request_number}'),
                    priority='medium',
                    content_object=instance,
                    url=f'/purchase/requests/detail/{instance.pk}/'
                )
        
        elif instance.status == 'rejected':
            # إنشاء تنبيه لمقدم الطلب
            create_purchase_notification(
                user=instance.requested_by,
                title=_('تم رفض طلب الشراء'),
                message=_(f'تم رفض طلب الشراء رقم: {instance.request_number}'),
                priority='high',
                content_object=instance,
                url=f'/purchase/requests/detail/{instance.pk}/'
            )
        
        elif instance.status == 'completed':
            # إنشاء تنبيه لمقدم الطلب
            create_purchase_notification(
                user=instance.requested_by,
                title=_('تم إكمال طلب الشراء'),
                message=_(f'تم إكمال طلب الشراء رقم: {instance.request_number}'),
                priority='medium',
                content_object=instance,
                url=f'/purchase/requests/detail/{instance.pk}/'
            )


@receiver(post_save, sender=PurchaseRequestItem)
def purchase_request_item_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند تغيير حالة عنصر في طلب الشراء"""
    if not created and instance.status in ['approved', 'rejected', 'transferred']:
        # الحصول على طلب الشراء المرتبط
        purchase_request = instance.purchase_request
        
        # تحديد نص حالة العنصر
        status_text = {
            'approved': _('تمت الموافقة على'),
            'rejected': _('تم رفض'),
            'transferred': _('تم ترحيل'),
        }[instance.status]
        
        # إنشاء تنبيه لمقدم الطلب
        create_purchase_notification(
            user=purchase_request.requested_by,
            title=_(f'{status_text} عنصر في طلب الشراء'),
            message=_(f'{status_text} العنصر {instance.product.product_name} في طلب الشراء رقم: {purchase_request.request_number}'),
            priority='medium',
            content_object=purchase_request,
            url=f'/purchase/requests/detail/{purchase_request.pk}/'
        )