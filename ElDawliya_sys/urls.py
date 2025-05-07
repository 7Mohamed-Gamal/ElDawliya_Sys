from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_site import admin_site
from .views import test_view

# تطبيق نظام الصلاحيات في موقع الإدارة
# ملاحظات:
# 1. تم نقل تسجيل النماذج إلى ملفات admin.py الخاصة بكل تطبيق
# 2. تم نقل تسجيل نماذج administrator إلى ملف administrator/admin.py
# 3. تم نقل تسجيل نماذج admin_permissions إلى ملف admin_permissions/admin.py
# 4. تم نقل تسجيل نموذج Users_Login_New إلى ملف accounts/admin.py
# 5. نموذج Group مسجل بالفعل في نظام Django الأساسي

urlpatterns = [
    path('test/', test_view, name='test'),  # مسار اختبار بسيط
    path('admin/', admin_site.urls),  # لوحة الإدارة المخصصة
    path('accounts/', include('accounts.urls')),  # مسارات تطبيق الحسابات
    path('meetings/', include('meetings.urls')),  # مسارات تطبيق الاجتماعات
    path('tasks/', include('tasks.urls')),  # مسارات تطبيق المهام
    path('Hr/', include('Hr.urls')), #مسارات تطبيق الموارد البشرية
    path('inventory/', include('inventory.urls')), # مسارات تطبيق مخزن قطع الغيار
    path('purchase/', include('Purchase_orders.urls')), # مسارات تطبيق طلبات الشراء
    path('administrator/', include('administrator.urls')),  # مسارات تطبيق مدير النظام
    path('notifications/', include('notifications.urls')),  # مسارات تطبيق التنبيهات
    path('audit/', include('audit.urls')),  # مسارات تطبيق تسجيل الأحداث
    path('employee-tasks/', include('employee_tasks.urls')),  # مسارات تطبيق مهام الموظفين
    path('', lambda request: redirect('accounts:login'), name='home'),  # إعادة توجيه الصفحة الرئيسية إلى صفحة الحسابات
]

# إضافة مسارات الوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
