from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Notification


def create_notification(user, title, message, notification_type, priority='medium',
                        content_object=None, url=None, icon=None):
    """
    إنشاء تنبيه جديد

    Args:
        user: المستخدم المستهدف بالتنبيه
        title: عنوان التنبيه
        message: نص التنبيه
        notification_type: نوع التنبيه (hr, meetings, inventory, purchase, system)
        priority: أولوية التنبيه (low, medium, high, urgent)
        content_object: الكائن المرتبط بالتنبيه (اختياري)
        url: رابط التنبيه (اختياري)
        icon: أيقونة التنبيه (اختياري)

    Returns:
        كائن التنبيه الذي تم إنشاؤه
    """
    notification = Notification(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        url=url
    )

    if icon:
        notification.icon = icon

    # إذا كان هناك كائن مرتبط، قم بتعيينه
    if content_object:
        notification.content_type = ContentType.objects.get_for_model(content_object)
        notification.object_id = content_object.pk

    notification.save()
    return notification


def create_hr_notification(user, title, message, priority='medium', content_object=None, url=None):
    """إنشاء تنبيه للموارد البشرية"""
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='hr',
        priority=priority,
        content_object=content_object,
        url=url,
        icon='fas fa-user-tie'
    )


def create_meeting_notification(user, title, message, priority='medium', content_object=None, url=None):
    """إنشاء تنبيه للاجتماعات"""
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='meetings',
        priority=priority,
        content_object=content_object,
        url=url,
        icon='fas fa-users'
    )


def create_inventory_notification(user, title, message, priority='medium', content_object=None, url=None):
    """إنشاء تنبيه للمخزن"""
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='inventory',
        priority=priority,
        content_object=content_object,
        url=url,
        icon='fas fa-boxes'
    )


def create_purchase_notification(user, title, message, priority='medium', content_object=None, url=None):
    """إنشاء تنبيه للمشتريات"""
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='purchase',
        priority=priority,
        content_object=content_object,
        url=url,
        icon='fas fa-shopping-cart'
    )


def create_system_notification(user, title, message, priority='medium', content_object=None, url=None, icon='fas fa-cogs'):
    """إنشاء تنبيه للنظام"""
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='system',
        priority=priority,
        content_object=content_object,
        url=url,
        icon=icon
    )


def get_unread_notifications_count(user):
    """الحصول على عدد التنبيهات غير المقروءة للمستخدم"""
    return Notification.objects.filter(user=user, is_read=False).count()


def get_notifications_by_type(user, notification_type=None, limit=None, include_read=False):
    """
    الحصول على التنبيهات حسب النوع

    Args:
        user: المستخدم
        notification_type: نوع التنبيه (اختياري)
        limit: عدد التنبيهات المطلوبة (اختياري)
        include_read: تضمين التنبيهات المقروءة (اختياري)

    Returns:
        قائمة التنبيهات
    """
    # تجاهل الترتيب الافتراضي لتجنب مشكلة SQL Server
    queryset = Notification.objects.filter(user=user).order_by()

    if not include_read:
        queryset = queryset.filter(is_read=False)

    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)

    # استخدام طريقة متوافقة مع SQL Server
    notifications = list(queryset)
    notifications.sort(key=lambda x: x.created_at, reverse=True)

    if limit:
        notifications = notifications[:limit]

    return notifications


def mark_all_as_read(user, notification_type=None):
    """
    تعليم جميع التنبيهات كمقروءة

    Args:
        user: المستخدم
        notification_type: نوع التنبيه (اختياري)
    """
    queryset = Notification.objects.filter(user=user, is_read=False)

    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)

    queryset.update(is_read=True, read_at=timezone.now())
