from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model

from inventory.models import TblProducts, TblInvoiceitems
from accounts.models import Users_Login_New

from .utils import create_inventory_notification

User = get_user_model()

# إشارات المخزن (Inventory)
@receiver(post_save, sender=TblProducts)
def product_threshold_notification(sender, instance, **kwargs):
    """إنشاء تنبيه عند وصول المنتج للحد الأدنى أو نفاده من المخزن"""
    # التحقق من وجود كمية محددة وحد أدنى محدد
    if instance.qte_in_stock is not None and instance.minimum_threshold is not None:
        # الحصول على مستخدمي النظام المسؤولين عن المخزن
        # هنا نفترض أن المستخدمين المسؤولين عن المخزن هم المستخدمين النشطين
        # يمكن تعديل هذا الشرط حسب هيكل النظام
        inventory_managers = Users_Login_New.objects.filter(is_active=True)
        
        # إذا وصل المنتج للحد الأدنى
        if instance.qte_in_stock <= instance.minimum_threshold and instance.qte_in_stock > 0:
            for manager in inventory_managers:
                create_inventory_notification(
                    user=manager,
                    title=_('منتج وصل للحد الأدنى'),
                    message=_(f'المنتج {instance.product_name} وصل للحد الأدنى. الكمية المتبقية: {instance.qte_in_stock}'),
                    priority='high',
                    content_object=instance,
                    url=f'/inventory/products/detail/{instance.product_id}/'
                )
        
        # إذا نفد المنتج من المخزن
        elif instance.qte_in_stock <= 0:
            for manager in inventory_managers:
                create_inventory_notification(
                    user=manager,
                    title=_('منتج نفد من المخزن'),
                    message=_(f'المنتج {instance.product_name} نفد من المخزن. يرجى إعادة الطلب.'),
                    priority='urgent',
                    content_object=instance,
                    url=f'/inventory/products/detail/{instance.product_id}/'
                )


@receiver(post_save, sender=TblInvoiceitems)
def new_inventory_transaction_notification(sender, instance, created, **kwargs):
    """إنشاء تنبيه عند إضافة حركة جديدة في المخزن"""
    if created:
        # الحصول على مستخدمي النظام المسؤولين عن المخزن
        inventory_managers = Users_Login_New.objects.filter(is_active=True)
        
        # تحديد نوع الحركة
        transaction_type = ""
        if instance.quantity_elwarad and instance.quantity_elwarad > 0:
            transaction_type = _("وارد")
        elif instance.quantity_elmonsarf and instance.quantity_elmonsarf > 0:
            transaction_type = _("منصرف")
        elif instance.quantity_mortagaaelmawarden and instance.quantity_mortagaaelmawarden > 0:
            transaction_type = _("مرتجع موردين")
        elif instance.quantity_mortagaaomalaa and instance.quantity_mortagaaomalaa > 0:
            transaction_type = _("مرتجع عملاء")
        
        if transaction_type:
            for manager in inventory_managers:
                create_inventory_notification(
                    user=manager,
                    title=_('حركة جديدة في المخزن'),
                    message=_(f'تم تسجيل حركة {transaction_type} جديدة للمنتج {instance.product_name}'),
                    priority='medium',
                    content_object=instance,
                    url=f'/inventory/transactions/'
                )