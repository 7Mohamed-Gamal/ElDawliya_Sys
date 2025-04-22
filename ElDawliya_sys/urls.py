from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # لوحة الإدارة
    path('accounts/', include('accounts.urls')),  # مسارات تطبيق الحسابات
    path('meetings/', include('meetings.urls')),  # مسارات تطبيق الاجتماعات
    path('tasks/', include('tasks.urls')),  # مسارات تطبيق المهام
    path('Hr/', include('Hr.urls')), #مسارات تطبيق الموارد البشرية
    path('inventory/', include('inventory.urls')), # مسارات تطبيق مخزن قطع الغيار
    path('purchase/', include('Purchase_orders.urls')), # مسارات تطبيق طلبات الشراء
    path('administrator/', include('administrator.urls')),  # مسارات تطبيق مدير النظام
    path('', lambda request: redirect('accounts:login'), name='home'),  # إعادة توجيه الصفحة الرئيسية إلى صفحة الحسابات
]

# إضافة مسارات الوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
