from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin  # Import Django's default admin
from .views import test_view
from accounts.views import global_search_api

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
    path('', include('frontend.urls')),  # مسارات الواجهة الأمامية (Dashboard)
    
    # Core Business Apps
    path('hr/', include('apps.hr.urls')),  # مسارات نظام الموارد البشرية
    path('inventory/', include('apps.inventory.urls')), # مسارات تطبيق مخزن قطع الغيار
    path('purchase/', include('apps.procurement.purchase_orders.urls')), # مسارات تطبيق طلبات الشراء
    path('procurement/', include('apps.procurement.urls')), # مسارات المشتريات العامة
    path('finance/', include('apps.finance.urls')), # مسارات المالية
    path('banks/', include('apps.finance.banks.urls')),  # مسارات البنوك
    path('companies/', include('companies.urls')),  # مسارات الشركات
    path('projects/', include('apps.projects.urls')),  # مسارات المشاريع
    path('meetings/', include('apps.projects.meetings.urls')),  # مسارات تطبيق الاجتماعات
    path('reports/', include('apps.reports.urls')),  # مسارات التقارير



    path('administrator/', include('administrator.urls')),  # مسارات تطبيق مدير النظام
    path('notifications/', include('notifications.urls')),  # مسارات تطبيق التنبيهات
    
    path('api/v1/', include('api.urls')),  # مسارات API
    path('api/global-search/', global_search_api, name='global_search_api'),  # Global search API endpoint
    
    path('', lambda request: redirect('frontend:dashboard') if request.user.is_authenticated else redirect('accounts:login'), name='home'),  # Smart Redirect
]

# Combine special and regular URL patterns
urlpatterns = special_urlpatterns + urlpatterns

# إضافة مسارات الوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
