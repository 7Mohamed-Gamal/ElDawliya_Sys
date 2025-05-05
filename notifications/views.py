from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone

from .models import Notification
from .utils import mark_all_as_read, get_notifications_by_type


@login_required
def notification_dashboard(request):
    """
    عرض لوحة التحكم الرئيسية للتنبيهات
    """
    # إحصائيات التنبيهات
    stats = {
        'total': Notification.objects.filter(user=request.user).count(),
        'unread': Notification.objects.filter(user=request.user, is_read=False).count(),
        'hr': Notification.objects.filter(user=request.user, notification_type='hr').count(),
        'meetings': Notification.objects.filter(user=request.user, notification_type='meetings').count(),
        'inventory': Notification.objects.filter(user=request.user, notification_type='inventory').count(),
        'purchase': Notification.objects.filter(user=request.user, notification_type='purchase').count(),
        'system': Notification.objects.filter(user=request.user, notification_type='system').count(),
    }

    # التنبيهات حسب الأولوية - استخدام طريقة متوافقة مع SQL Server
    # تجاهل الترتيب الافتراضي لتجنب مشكلة SQL Server مع GROUP BY
    priority_stats = Notification.objects.filter(user=request.user).values('priority').annotate(count=Count('id')).order_by()
    priority_data = {item['priority']: item['count'] for item in priority_stats}

    # التنبيهات الأخيرة - استخدام طريقة متوافقة مع SQL Server
    recent_notifications = list(Notification.objects.filter(user=request.user))
    recent_notifications.sort(key=lambda x: x.created_at, reverse=True)
    recent_notifications = recent_notifications[:10]

    # التنبيهات حسب النوع
    hr_notifications = get_notifications_by_type(request.user, 'hr', include_read=True)[:20]
    meetings_notifications = get_notifications_by_type(request.user, 'meetings', include_read=True)[:20]
    inventory_notifications = get_notifications_by_type(request.user, 'inventory', include_read=True)[:20]
    purchase_notifications = get_notifications_by_type(request.user, 'purchase', include_read=True)[:20]
    system_notifications = get_notifications_by_type(request.user, 'system', include_read=True)[:20]

    context = {
        'title': 'لوحة التنبيهات',
        'stats': stats,
        'priority_data': priority_data,
        'recent_notifications': recent_notifications,
        'hr_notifications': hr_notifications,
        'meetings_notifications': meetings_notifications,
        'inventory_notifications': inventory_notifications,
        'purchase_notifications': purchase_notifications,
        'system_notifications': system_notifications,
    }

    return render(request, 'notifications/dashboard.html', context)


@login_required
def notification_list(request, notification_type=None):
    """
    عرض قائمة التنبيهات حسب النوع
    """
    # تحديد نوع التنبيهات المطلوبة
    if notification_type and notification_type in dict(Notification.NOTIFICATION_TYPES).keys():
        notifications = get_notifications_by_type(request.user, notification_type, include_read=True)
        title = f'تنبيهات {dict(Notification.NOTIFICATION_TYPES)[notification_type]}'
    else:
        # استخدام طريقة متوافقة مع SQL Server
        notifications = list(Notification.objects.filter(user=request.user))
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        title = 'جميع التنبيهات'

    # تطبيق الفلاتر
    is_read = request.GET.get('is_read')
    priority = request.GET.get('priority')

    # تحقق مما إذا كان notifications هو قائمة (تم تحويله بالفعل) أو queryset
    if isinstance(notifications, list):
        # إذا كان قائمة، قم بالتصفية يدويًا
        if is_read:
            if is_read == 'read':
                notifications = [n for n in notifications if n.is_read]
            elif is_read == 'unread':
                notifications = [n for n in notifications if not n.is_read]

        if priority:
            notifications = [n for n in notifications if n.priority == priority]
    else:
        # إذا كان queryset، استخدم filter العادي
        if is_read:
            if is_read == 'read':
                notifications = notifications.filter(is_read=True)
            elif is_read == 'unread':
                notifications = notifications.filter(is_read=False)

        if priority:
            notifications = notifications.filter(priority=priority)

    context = {
        'title': title,
        'notifications': notifications,
        'notification_type': notification_type,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'priority_levels': Notification.PRIORITY_LEVELS,
    }

    return render(request, 'notifications/list.html', context)


@login_required
def notification_detail(request, pk):
    """
    عرض تفاصيل التنبيه
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    # تعليم التنبيه كمقروء
    if not notification.is_read:
        notification.mark_as_read()

    context = {
        'title': notification.title,
        'notification': notification,
    }

    return render(request, 'notifications/detail.html', context)


@login_required
def mark_notification_as_read(request, pk):
    """
    تعليم التنبيه كمقروء
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()

    # إذا كان هناك رابط للتنبيه، قم بالتوجيه إليه
    if notification.url:
        # تصحيح الروابط القديمة للمهام
        if '/tasks/detail/' in notification.url:
            task_id = notification.url.split('/tasks/detail/')[1].strip('/')
            corrected_url = f'/tasks/{task_id}/'
            return redirect(corrected_url)
        return redirect(notification.url)

    # وإلا قم بالتوجيه إلى صفحة التفاصيل
    return redirect('notifications:detail', pk=notification.pk)


@login_required
def mark_all_notifications_as_read(request, notification_type=None):
    """
    تعليم جميع التنبيهات كمقروءة
    """
    mark_all_as_read(request.user, notification_type)

    # إذا كان الطلب من AJAX، أرجع استجابة JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # وإلا قم بالتوجيه إلى الصفحة السابقة
    if notification_type:
        return redirect('notifications:list_by_type', notification_type=notification_type)
    else:
        return redirect('notifications:dashboard')
