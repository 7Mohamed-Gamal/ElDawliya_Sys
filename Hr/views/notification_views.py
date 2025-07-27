"""
Views للإشعارات الذكية
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json

from ..models_notifications import (
    Notification, NotificationTemplate, NotificationRule,
    NotificationPreference, NotificationDigest
)
from ..services.notification_service import AdvancedNotificationService


@login_required
def notification_center(request):
    """مركز الإشعارات"""
    
    # الحصول على الإشعارات
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'template', 'rule').order_by('-created_at')
    
    # الفلترة
    search = request.GET.get('search', '')
    notification_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    if search:
        notifications = notifications.filter(
            Q(title__icontains=search) | Q(message__icontains=search)
        )
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if status:
        if status == 'unread':
            notifications = notifications.exclude(status='read')
        elif status == 'read':
            notifications = notifications.filter(status='read')
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            notifications = notifications.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            notifications = notifications.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            notifications = notifications.filter(created_at__date__gte=month_ago)
    
    # الإحصائيات
    stats = {
        'total_count': Notification.objects.filter(recipient=request.user).count(),
        'unread_count': Notification.objects.filter(
            recipient=request.user
        ).exclude(status='read').count(),
        'today_count': Notification.objects.filter(
            recipient=request.user,
            created_at__date=timezone.now().date()
        ).count(),
        'urgent_count': Notification.objects.filter(
            recipient=request.user,
            priority='urgent'
        ).count(),
    }
    
    # التصفح
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # تفضيلات المستخدم
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'enabled': True,
            'email_enabled': True,
            'in_app_enabled': True,
            'push_enabled': True,
            'sms_enabled': False
        }
    )
    
    context = {
        'notifications': notifications,
        'stats': stats,
        'preferences': preferences,
        'search': search,
        'notification_type': notification_type,
        'status': status,
        'date_filter': date_filter,
    }
    
    return render(request, 'Hr/notifications/notification_center.html', context)


@login_required
@require_http_methods([\"POST\"])
def mark_notification_read(request, notification_id):
    """تحديد الإشعار كمقروء"""
    
    try:
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods([\"POST\"])
def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    
    try:
        updated_count = Notification.objects.filter(
            recipient=request.user
        ).exclude(status='read').update(
            status='read',
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods([\"DELETE\"])
def delete_notification(request, notification_id):
    """حذف الإشعار"""
    
    try:
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def check_new_notifications(request):
    """التحقق من الإشعارات الجديدة"""
    
    try:
        # آخر تحقق (من session أو cookie)
        last_check = request.session.get('last_notification_check')
        if last_check:
            last_check = datetime.fromisoformat(last_check)
        else:
            last_check = timezone.now() - timedelta(minutes=5)
        
        # الإشعارات الجديدة
        new_notifications = Notification.objects.filter(
            recipient=request.user,
            created_at__gt=last_check
        ).count()
        
        # إجمالي غير المقروءة
        unread_count = Notification.objects.filter(
            recipient=request.user
        ).exclude(status='read').count()
        
        # تحديث آخر تحقق
        request.session['last_notification_check'] = timezone.now().isoformat()
        
        return JsonResponse({
            'has_new': new_notifications > 0,
            'new_count': new_notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods([\"GET\", \"POST\"])
def notification_preferences(request):
    """إعدادات الإشعارات"""
    
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'enabled': True,
            'email_enabled': True,
            'in_app_enabled': True,
            'push_enabled': True,
            'sms_enabled': False
        }
    )
    
    if request.method == 'POST':
        try:
            # تحديث الإعدادات
            preferences.enabled = request.POST.get('enabled') == 'on'
            preferences.email_enabled = request.POST.get('email_enabled') == 'on'
            preferences.sms_enabled = request.POST.get('sms_enabled') == 'on'
            preferences.push_enabled = request.POST.get('push_enabled') == 'on'
            preferences.in_app_enabled = request.POST.get('in_app_enabled') == 'on'
            
            preferences.digest_enabled = request.POST.get('digest_enabled') == 'on'
            preferences.digest_frequency = request.POST.get('digest_frequency', 'daily')
            
            preferences.quiet_hours_enabled = request.POST.get('quiet_hours_enabled') == 'on'
            
            quiet_hours_start = request.POST.get('quiet_hours_start')
            if quiet_hours_start:
                preferences.quiet_hours_start = datetime.strptime(quiet_hours_start, '%H:%M').time()
            
            quiet_hours_end = request.POST.get('quiet_hours_end')
            if quiet_hours_end:
                preferences.quiet_hours_end = datetime.strptime(quiet_hours_end, '%H:%M').time()
            
            preferences.save()
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'تم حفظ إعدادات الإشعارات بنجاح')
                return redirect('hr:notification_center')
                
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    
    context = {
        'preferences': preferences
    }
    
    return render(request, 'Hr/notifications/preferences.html', context)


@login_required
def notification_templates(request):
    """إدارة قوالب الإشعارات"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.view_notificationtemplate'):
        messages.error(request, 'ليس لديك صلاحية لعرض قوالب الإشعارات')
        return redirect('hr:dashboard')
    
    templates = NotificationTemplate.objects.all().order_by('name')
    
    # الفلترة
    search = request.GET.get('search', '')
    notification_type = request.GET.get('type', '')
    
    if search:
        templates = templates.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(code__icontains=search)
        )
    
    if notification_type:
        templates = templates.filter(notification_type=notification_type)
    
    # التصفح
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page')
    templates = paginator.get_page(page_number)
    
    context = {
        'templates': templates,
        'search': search,
        'notification_type': notification_type,
    }
    
    return render(request, 'Hr/notifications/templates.html', context)


@login_required
def notification_rules(request):
    """إدارة قواعد الإشعارات"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.view_notificationrule'):
        messages.error(request, 'ليس لديك صلاحية لعرض قواعد الإشعارات')
        return redirect('hr:dashboard')
    
    rules = NotificationRule.objects.select_related('template').all().order_by('name')
    
    # الفلترة
    search = request.GET.get('search', '')
    trigger_event = request.GET.get('event', '')
    is_active = request.GET.get('active', '')
    
    if search:
        rules = rules.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    if trigger_event:
        rules = rules.filter(trigger_event=trigger_event)
    
    if is_active:
        rules = rules.filter(is_active=is_active == 'true')
    
    # التصفح
    paginator = Paginator(rules, 20)
    page_number = request.GET.get('page')
    rules = paginator.get_page(page_number)
    
    context = {
        'rules': rules,
        'search': search,
        'trigger_event': trigger_event,
        'is_active': is_active,
        'trigger_events': NotificationRule.TRIGGER_EVENTS,
    }
    
    return render(request, 'Hr/notifications/rules.html', context)


@login_required
def notification_analytics(request):
    """تحليلات الإشعارات"""
    
    # التحقق من الصلاحيات
    if not request.user.has_perm('Hr.view_notification'):
        messages.error(request, 'ليس لديك صلاحية لعرض تحليلات الإشعارات')
        return redirect('hr:dashboard')
    
    # الفترة الزمنية
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # الإحصائيات العامة
    total_notifications = Notification.objects.filter(
        created_at__gte=start_date
    ).count()
    
    sent_notifications = Notification.objects.filter(
        created_at__gte=start_date,
        status__in=['sent', 'delivered', 'read']
    ).count()
    
    failed_notifications = Notification.objects.filter(
        created_at__gte=start_date,
        status='failed'
    ).count()
    
    # الإشعارات حسب النوع
    notifications_by_type = Notification.objects.filter(
        created_at__gte=start_date
    ).values('notification_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # الإشعارات حسب الحالة
    notifications_by_status = Notification.objects.filter(
        created_at__gte=start_date
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # الإشعارات اليومية
    daily_notifications = []
    for i in range(days):
        date = (timezone.now() - timedelta(days=i)).date()
        count = Notification.objects.filter(
            created_at__date=date
        ).count()
        daily_notifications.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    daily_notifications.reverse()
    
    # أكثر القوالب استخداماً
    top_templates = NotificationTemplate.objects.annotate(
        usage_count=Count('notifications', filter=Q(
            notifications__created_at__gte=start_date
        ))
    ).filter(usage_count__gt=0).order_by('-usage_count')[:10]
    
    # معدل النجاح
    success_rate = 0
    if total_notifications > 0:
        success_rate = (sent_notifications / total_notifications) * 100
    
    context = {
        'days': days,
        'total_notifications': total_notifications,
        'sent_notifications': sent_notifications,
        'failed_notifications': failed_notifications,
        'success_rate': round(success_rate, 2),
        'notifications_by_type': notifications_by_type,
        'notifications_by_status': notifications_by_status,
        'daily_notifications': daily_notifications,
        'top_templates': top_templates,
    }
    
    return render(request, 'Hr/notifications/analytics.html', context)


@login_required
@require_http_methods([\"POST\"])
def send_test_notification(request):
    """إرسال إشعار تجريبي"""
    
    try:
        service = AdvancedNotificationService()
        
        notification = service.create_notification(
            recipient=request.user,
            title='إشعار تجريبي',
            message='هذا إشعار تجريبي للتأكد من عمل النظام بشكل صحيح',
            notification_type='info',
            sender=request.user
        )
        
        if notification:
            return JsonResponse({
                'success': True,
                'message': 'تم إرسال الإشعار التجريبي بنجاح'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'فشل في إرسال الإشعار التجريبي'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notification_digest_history(request):
    """تاريخ ملخصات الإشعارات"""
    
    digests = NotificationDigest.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # التصفح
    paginator = Paginator(digests, 20)
    page_number = request.GET.get('page')
    digests = paginator.get_page(page_number)
    
    context = {
        'digests': digests
    }
    
    return render(request, 'Hr/notifications/digest_history.html', context)


@login_required
def notification_digest_detail(request, digest_id):
    """تفاصيل ملخص الإشعارات"""
    
    digest = get_object_or_404(
        NotificationDigest,
        id=digest_id,
        user=request.user
    )
    
    context = {
        'digest': digest
    }
    
    return render(request, 'Hr/notifications/digest_detail.html', context)