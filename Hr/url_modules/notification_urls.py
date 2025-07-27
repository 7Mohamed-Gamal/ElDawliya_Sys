"""
URLs للإشعارات الذكية
"""

from django.urls import path
from ..views.notification_views import (
    notification_center,
    mark_notification_read,
    mark_all_notifications_read,
    delete_notification,
    check_new_notifications,
    notification_preferences,
    notification_templates,
    notification_rules,
    notification_analytics,
    send_test_notification,
    notification_digest_history,
    notification_digest_detail,
)

app_name = 'notifications'

urlpatterns = [
    # مركز الإشعارات
    path('', notification_center, name='center'),
    path('center/', notification_center, name='notification_center'),
    
    # إجراءات الإشعارات
    path('<uuid:notification_id>/mark-read/', mark_notification_read, name='mark_read'),
    path('mark-all-read/', mark_all_notifications_read, name='mark_all_read'),
    path('<uuid:notification_id>/delete/', delete_notification, name='delete'),
    path('check-new/', check_new_notifications, name='check_new'),
    
    # الإعدادات
    path('preferences/', notification_preferences, name='preferences'),
    
    # الإدارة
    path('templates/', notification_templates, name='templates'),
    path('rules/', notification_rules, name='rules'),
    path('analytics/', notification_analytics, name='analytics'),
    
    # اختبار
    path('test/', send_test_notification, name='test'),
    
    # ملخصات الإشعارات
    path('digests/', notification_digest_history, name='digest_history'),
    path('digests/<uuid:digest_id>/', notification_digest_detail, name='digest_detail'),
]