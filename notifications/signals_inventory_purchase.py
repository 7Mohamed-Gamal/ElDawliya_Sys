"""
Signals for combined inventory and purchase notifications.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

try:
    from inventory.models_local import Product, PurchaseRequest as InventoryPurchaseRequest
    INVENTORY_PURCHASE_AVAILABLE = True
except ImportError:
    INVENTORY_PURCHASE_AVAILABLE = False

from .utils import create_notification


if INVENTORY_PURCHASE_AVAILABLE:
    @receiver(post_save, sender=InventoryPurchaseRequest)
    def inventory_purchase_request_created_notification(sender, instance, created, **kwargs):
        """
        Send notification when a new inventory purchase request is created.
        """
        if created:
            # Notify purchase managers
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            purchase_managers = User.objects.filter(
                groups__name__in=['Purchase Manager', 'مدير المشتريات', 'Inventory Manager', 'مدير المخزون']
            ).distinct()
            
            for manager in purchase_managers:
                create_notification(
                    user=manager,
                    notification_type='inventory_purchase_request_created',
                    title=_('طلب شراء جديد من المخزون'),
                    message=_('طلب شراء جديد للصنف: {} - الكمية: {}').format(
                        instance.product.name,
                        instance.quantity
                    ),
                    related_object=instance
                )


    @receiver(post_save, sender=InventoryPurchaseRequest)
    def inventory_purchase_request_status_changed_notification(sender, instance, created, **kwargs):
        """
        Send notification when inventory purchase request status changes.
        """
        if not created and instance.status:
            # Notify relevant users about status change
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            status_text = dict(InventoryPurchaseRequest.STATUS_CHOICES).get(instance.status, instance.status)
            
            # Notify inventory managers
            inventory_managers = User.objects.filter(
                groups__name__in=['Inventory Manager', 'مدير المخزون']
            ).distinct()
            
            for manager in inventory_managers:
                create_notification(
                    user=manager,
                    notification_type='inventory_purchase_request_status_changed',
                    title=_('تحديث حالة طلب الشراء'),
                    message=_('تم تغيير حالة طلب شراء الصنف "{}" إلى: {}').format(
                        instance.product.name,
                        status_text
                    ),
                    related_object=instance
                )


    @receiver(post_save, sender=Product)
    def auto_create_purchase_request_notification(sender, instance, created, **kwargs):
        """
        Automatically create purchase request when product reaches minimum threshold.
        """
        if not created and instance.quantity <= instance.minimum_threshold:
            # Check if there's already a pending purchase request for this product
            existing_request = InventoryPurchaseRequest.objects.filter(
                product=instance,
                status='pending'
            ).exists()
            
            if not existing_request:
                # Create automatic purchase request
                suggested_quantity = instance.maximum_threshold - instance.quantity
                
                purchase_request = InventoryPurchaseRequest.objects.create(
                    product=instance,
                    quantity=suggested_quantity,
                    status='pending',
                    notes=_('طلب شراء تلقائي - الصنف وصل إلى الحد الأدنى')
                )
                
                # Notify purchase managers
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                purchase_managers = User.objects.filter(
                    groups__name__in=['Purchase Manager', 'مدير المشتريات']
                ).distinct()
                
                for manager in purchase_managers:
                    create_notification(
                        user=manager,
                        notification_type='auto_purchase_request_created',
                        title=_('طلب شراء تلقائي'),
                        message=_('تم إنشاء طلب شراء تلقائي للصنف "{}" - الكمية المقترحة: {}').format(
                            instance.name,
                            suggested_quantity
                        ),
                        related_object=purchase_request
                    )

