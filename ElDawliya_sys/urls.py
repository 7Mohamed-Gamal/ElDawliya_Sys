from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin  # Import Django's default admin
from .views import test_view

# Import the database setup view directly to avoid database dependency
# This allows the database setup URL to work even when the database is unavailable
from administrator.views import database_setup

# تطبيق نظام الصلاحيات في موقع الإدارة
# ملاحظات:
# 1. تم نقل تسجيل النماذج إلى ملفات admin.py الخاصة بكل تطبيق
# 2. تم نقل تسجيل نماذج administrator إلى ملف administrator/admin.py
# 3. تم نقل تسجيل نماذج admin_permissions إلى ملف admin_permissions/admin.py
# 4. تم نقل تسجيل نموذج Users_Login_New إلى ملف accounts/admin.py
# 5. نموذج Group مسجل بالفعل في نظام Django الأساسي

# Special URL patterns that should work even when the database is unavailable
# These URLs are defined first to ensure they're accessible during database errors
special_urlpatterns = [
    # Direct access to database setup page - this must work even when DB is down
    path('administrator/database-setup/', database_setup, name='database_setup'),
]

# Regular URL patterns that require database access
urlpatterns = [
    path('test/', test_view, name='test'),  # مسار اختبار بسيط
    path('admin/', admin.site.urls),  # لوحة الإدارة الافتراضية
    path('accounts/', include('accounts.urls')),  # مسارات تطبيق الحسابات
    path('meetings/', include('meetings.urls')),  # مسارات تطبيق الاجتماعات
    path('tasks/', include('tasks.urls')),  # مسارات تطبيق المهام
    path('Hr/', include('Hr.urls_minimal')), #مسارات تطبيق الموارد البشرية - USING WORKING VERSION
    path('attendance/', include('attendance.urls')),
    path('inventory/', include('inventory.urls')), # مسارات تطبيق مخزن قطع الغيار
    path('purchase/', include('Purchase_orders.urls')), # مسارات تطبيق طلبات الشراء
    path('administrator/', include('administrator.urls')),  # مسارات تطبيق مدير النظام
    path('notifications/', include('notifications.urls')),  # مسارات تطبيق التنبيهات
    path('audit/', include('audit.urls')),  # مسارات تطبيق تسجيل الأحداث
    path('employee-tasks/', include('employee_tasks.urls')),  # مسارات تطبيق مهام الموظفين
    path('cars/', include('cars.urls')),  # مسارات تطبيق السيارات
    path('api/v1/', include('api.urls')),  # مسارات API
    path('', lambda request: redirect('accounts:login'), name='home'),  # إعادة توجيه الصفحة الرئيسية إلى صفحة الحسابات
]

# Combine special and regular URL patterns
urlpatterns = special_urlpatterns + urlpatterns

# إضافة مسارات الوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
