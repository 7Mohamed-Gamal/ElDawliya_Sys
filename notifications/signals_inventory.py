"""
Signals for inventory-related notifications.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import F

try:
    from apps.inventory.models import TblProducts, TblInvoiceitems
    from apps.inventory.models_local import Product
    INVENTORY_AVAILABLE = True
except ImportError:
    INVENTORY_AVAILABLE = False

from .utils import create_inventory_notification


if INVENTORY_AVAILABLE:
    @receiver(post_save, sender=Product)
    def product_low_stock_notification(sender, instance, created, **kwargs):
        """
        Send notification when a product's stock is low.
        """
        if not created and instance.quantity <= instance.minimum_threshold:
            # Notify inventory managers about low stock
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Get users with inventory management permissions
            inventory_managers = User.objects.filter(
                groups__name__in=['Inventory Manager', 'مدير المخزون']
            ).distinct()

            for manager in inventory_managers:
                create_inventory_notification(
                    user=manager,
                    product=instance,
                    notification_type='low_stock',
                    message=_('تنبيه: الصنف "{}" وصل إلى الحد الأدنى. الكمية الحالية: {}').format(
                        instance.name,
                        instance.quantity
                    )
                )


    @receiver(post_save, sender=Product)
    def product_out_of_stock_notification(sender, instance, created, **kwargs):
        """
        Send notification when a product is out of stock.
        """
        if not created and instance.quantity <= 0:
            # Notify inventory managers about out of stock
            from django.contrib.auth import get_user_model
            User = get_user_model()

            inventory_managers = User.objects.filter(
                groups__name__in=['Inventory Manager', 'مدير المخزون']
            ).distinct()

            for manager in inventory_managers:
                create_inventory_notification(
                    user=manager,
                    product=instance,
                    notification_type='out_of_stock',
                    message=_('تحذير: الصنف "{}" نفذ من المخزون!').format(instance.name)
                )


    @receiver(post_save, sender=TblInvoiceitems)
    def invoice_item_created_notification(sender, instance, created, **kwargs):
        """
        Send notification when an invoice item is created.
        """
        if created:
            # Update product quantity based on invoice type
            try:
                product = TblProducts.objects.get(prod_id=instance.prod_id)

                if instance.invoice.invoice_type == 'in':
                    # Incoming invoice - increase stock
                    product.prod_qty = F('prod_qty') + instance.qty
                    product.save(update_fields=['prod_qty'])
                elif instance.invoice.invoice_type == 'out':
                    # Outgoing invoice - decrease stock
                    product.prod_qty = F('prod_qty') - instance.qty
                    product.save(update_fields=['prod_qty'])

                    # Check if stock is low after the transaction
                    product.refresh_from_db()
                    if product.prod_qty <= product.prod_min_qty:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()

                        inventory_managers = User.objects.filter(
                            groups__name__in=['Inventory Manager', 'مدير المخزون']
                        ).distinct()

                        for manager in inventory_managers:
                            create_inventory_notification(
                                user=manager,
                                product=product,
                                notification_type='low_stock_after_transaction',
                                message=_('تنبيه: الصنف "{}" وصل إلى الحد الأدنى بعد عملية الصرف').format(
                                    product.prod_name
                                )
                            )
            except TblProducts.DoesNotExist:
                pass

