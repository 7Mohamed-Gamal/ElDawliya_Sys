"""
Signals for purchase-related notifications.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

try:
    from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem
    PURCHASE_AVAILABLE = True
except ImportError:
    PURCHASE_AVAILABLE = False

from .utils import create_purchase_notification


if PURCHASE_AVAILABLE:
    @receiver(post_save, sender=PurchaseRequest)
    def purchase_request_created_notification(sender, instance, created, **kwargs):
        """
        Send notification when a new purchase request is created.
        """
        if created:
            # Notify purchase managers about new request
            from django.contrib.auth import get_user_model
            User = get_user_model()

            purchase_managers = User.objects.filter(
                groups__name__in=['Purchase Manager', 'مدير المشتريات']
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.distinct()

            for manager in purchase_managers:
                create_purchase_notification(
                    user=manager,
                    purchase_request=instance,
                    notification_type='purchase_request_created',
                    message=_('طلب شراء جديد رقم: {}').format(instance.request_number)
                )


    @receiver(post_save, sender=PurchaseRequest)
    def purchase_request_status_changed_notification(sender, instance, created, **kwargs):
        """
        Send notification when a purchase request status changes.
        """
        if not created and instance.status:
            # Notify the requester about status change
            if instance.requested_by:
                status_text = dict(PurchaseRequest.STATUS_CHOICES).get(instance.status, instance.status)
                create_purchase_notification(
                    user=instance.requested_by,
                    purchase_request=instance,
                    notification_type='purchase_request_status_changed',
                    message=_('تم تغيير حالة طلب الشراء رقم {} إلى: {}').format(
                        instance.request_number,
                        status_text
                    )
                )


    @receiver(post_save, sender=PurchaseRequest)
    def purchase_request_approved_notification(sender, instance, created, **kwargs):
        """
        Send notification when a purchase request is approved.
        """
        if not created and instance.status == 'approved':
            # Notify the requester
            if instance.requested_by:
                create_purchase_notification(
                    user=instance.requested_by,
                    purchase_request=instance,
                    notification_type='purchase_request_approved',
                    message=_('تمت الموافقة على طلب الشراء رقم: {}').format(instance.request_number)
                )


    @receiver(post_save, sender=PurchaseRequest)
    def purchase_request_rejected_notification(sender, instance, created, **kwargs):
        """
        Send notification when a purchase request is rejected.
        """
        if not created and instance.status == 'rejected':
            # Notify the requester
            if instance.requested_by:
                create_purchase_notification(
                    user=instance.requested_by,
                    purchase_request=instance,
                    notification_type='purchase_request_rejected',
                    message=_('تم رفض طلب الشراء رقم: {}').format(instance.request_number)
                )

