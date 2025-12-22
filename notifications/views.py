from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Notification
from .utils import mark_all_as_read, get_notifications_by_type


@login_required
def notification_dashboard(request):
    """
    عرض لوحة التحكم الرئيسية للتنبيهات
    """
    # إحصائيات التنبيهات
    total_notifications = Notification.objects.filter(user=request.user).count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    read_notifications = Notification.objects.filter(user=request.user, is_read=True).count()

    stats = {
        'total': total_notifications,
        'unread': unread_notifications,
        'read': read_notifications,
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

    # التحقق من وجود معلمة next في الطلب
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

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


@login_required
def user_notifications(request):
    """
    عرض تنبيهات المستخدم الحالي مع خيارات التصفية والترتيب
    """
    # الحصول على جميع تنبيهات المستخدم
    notifications = list(Notification.objects.filter(user=request.user))
    notifications.sort(key=lambda x: x.created_at, reverse=True)

    # تطبيق الفلاتر
    notification_type = request.GET.get('type')
    is_read = request.GET.get('is_read')
    priority = request.GET.get('priority')

    # فلترة حسب النوع
    if notification_type and notification_type in dict(Notification.NOTIFICATION_TYPES).keys():
        notifications = [n for n in notifications if n.notification_type == notification_type]

    # فلترة حسب حالة القراءة
    if is_read:
        if is_read == 'read':
            notifications = [n for n in notifications if n.is_read]
        elif is_read == 'unread':
            notifications = [n for n in notifications if not n.is_read]

    # فلترة حسب الأولوية
    if priority:
        notifications = [n for n in notifications if n.priority == priority]

    # التقسيم إلى صفحات
    paginator = Paginator(notifications, 20)  # 20 تنبيه في كل صفحة
    page = request.GET.get('page')

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        # إذا كانت الصفحة ليست رقمًا، عرض الصفحة الأولى
        notifications_page = paginator.page(1)
    except EmptyPage:
        # إذا كانت الصفحة خارج النطاق، عرض آخر صفحة
        notifications_page = paginator.page(paginator.num_pages)

    # إحصائيات التنبيهات
    total_count = len(notifications)
    unread_count = sum(1 for n in notifications if not n.is_read)
    read_count = sum(1 for n in notifications if n.is_read)

    stats = {
        'total': total_count,
        'unread': unread_count,
        'read': read_count,
        'hr': sum(1 for n in notifications if n.notification_type == 'hr'),
        'meetings': sum(1 for n in notifications if n.notification_type == 'meetings'),
        'inventory': sum(1 for n in notifications if n.notification_type == 'inventory'),
        'purchase': sum(1 for n in notifications if n.notification_type == 'purchase'),
        'system': sum(1 for n in notifications if n.notification_type == 'system'),
    }

    context = {
        'title': 'تنبيهاتي',
        'notifications': notifications_page,
        'stats': stats,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'priority_levels': Notification.PRIORITY_LEVELS,
        'selected_type': notification_type,
        'selected_read': is_read,
        'selected_priority': priority,
    }

    return render(request, 'notifications/user_notifications.html', context)
