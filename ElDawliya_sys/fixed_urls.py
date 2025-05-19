from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_site import admin_site

# تطبيق نظام الصلاحيات في موقع الإدارة
# تسجيل نماذج من تطبيقات مختلفة للإدارة المخصصة
from django.contrib.auth.models import Group
from accounts.models import Users_Login_New
from accounts.admin import CustomUserAdmin
from administrator.admin import (
    SystemSettingsAdmin, DepartmentAdmin, ModuleAdmin, PermissionAdmin,
    TemplatePermissionAdmin, UserGroupAdmin, UserDepartmentPermissionAdmin,
    UserModulePermissionAdmin, GroupProfileAdmin, AppModuleAdmin,
    OperationPermissionAdmin, PagePermissionAdmin, UserOperationPermissionAdmin,
    UserPagePermissionAdmin
)

from administrator.models import (
    SystemSettings, Department, Module, Permission, TemplatePermission,
    UserGroup, UserDepartmentPermission, UserModulePermission, GroupProfile
)

from django.contrib.auth.models import Permission

# Helper function to safely register models without causing AlreadyRegistered exceptions
def safe_register(admin_site, model, admin_class=None):
    try:
        admin_site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass  # Model is already registered, skip it

# تسجيل النماذج في موقع الإدارة المخصص
safe_register(admin_site, SystemSettings, SystemSettingsAdmin)
safe_register(admin_site, Department, DepartmentAdmin)
safe_register(admin_site, Module, ModuleAdmin)
safe_register(admin_site, Permission, PermissionAdmin)
safe_register(admin_site, TemplatePermission, TemplatePermissionAdmin)
safe_register(admin_site, UserGroup, UserGroupAdmin)
safe_register(admin_site, UserDepartmentPermission, UserDepartmentPermissionAdmin)
safe_register(admin_site, UserModulePermission, UserModulePermissionAdmin)
safe_register(admin_site, GroupProfile, GroupProfileAdmin)

# تسجيل نماذج نظام الصلاحيات الأساسية
safe_register(admin_site, Group)
safe_register(admin_site, Users_Login_New, CustomUserAdmin)

urlpatterns = [
    path('admin/', admin_site.urls),  # لوحة الإدارة المخصصة
    path('accounts/', include('accounts.urls')),  # مسارات تطبيق الحسابات
    path('meetings/', include('meetings.urls')),  # مسارات تطبيق الاجتماعات
    path('tasks/', include('tasks.urls')),  # مسارات تطبيق المهام
    path('Hr/', include('Hr.urls')), #مسارات تطبيق الموارد البشرية
    path('inventory/', include('inventory.urls')), # مسارات تطبيق مخزن قطع الغيار
    path('purchase/', include('Purchase_orders.urls')), # مسارات تطبيق طلبات الشراء
    path('administrator/', include('administrator.urls')),  # مسارات تطبيق مدير النظام
    path('notifications/', include('notifications.urls')),  # مسارات تطبيق التنبيهات
    path('', lambda request: redirect('accounts:login'), name='home'),  # إعادة توجيه الصفحة الرئيسية إلى صفحة الحسابات
]

# إضافة مسارات الوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
