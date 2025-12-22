from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # لوحة التحكم الرئيسية للتنبيهات
    path('', views.notification_dashboard, name='dashboard'),

    # قوائم التنبيهات
    path('list/', views.notification_list, name='list'),
    path('list/<str:notification_type>/', views.notification_list, name='list_by_type'),

    # تفاصيل التنبيه
    path('<int:pk>/', views.notification_detail, name='detail'),

    # تعليم التنبيهات كمقروءة
    path('<int:pk>/mark-as-read/', views.mark_notification_as_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_as_read'),
    path('mark-all-as-read/<str:notification_type>/', views.mark_all_notifications_as_read, name='mark_all_as_read_by_type'),

    # تنبيهات المستخدم
    path('my-notifications/', views.user_notifications, name='user_notifications'),
]
