from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='hr_dashboard'),
    
    # API endpoints
    path('api/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('api/notifications-count/', views.notifications_count, name='notifications_count'),
    path('api/module-status/', views.module_status, name='module_status'),
    
    # صفحات المستخدم
    path('profile/', views.profile, name='profile'),
    path('my-payslips/', views.my_payslips, name='my_payslips'),
    path('my-leaves/', views.my_leaves, name='my_leaves'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
]