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

# تسجيل النماذج في موقع الإدارة المخصص
admin_site.register(SystemSettings, SystemSettingsAdmin)
admin_site.register(Department, DepartmentAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(Permission, PermissionAdmin)
admin_site.register(TemplatePermission, TemplatePermissionAdmin)
admin_site.register(UserGroup, UserGroupAdmin)
admin_site.register(UserDepartmentPermission, UserDepartmentPermissionAdmin)
admin_site.register(UserModulePermission, UserModulePermissionAdmin)
admin_site.register(GroupProfile, GroupProfileAdmin)

# تسجيل نماذج نظام الصلاحيات الأساسية
admin_site.register(Group)
admin_site.register(Users_Login_New, CustomUserAdmin)

urlpatterns = [
    path('admin/', admin_site.urls),  # لوحة الإدارة المخصصة
    path('accounts/', include('accounts.urls')),  # مسارات تطبيق الحسابات
    path('meetings/', include('meetings.urls')),  # مسارات تطبيق الاجتماعات
    path('tasks/', include('tasks.urls')),  # مسارات تطبيق المهام
    path('Hr/', include('Hr.urls')), #مسارات تطبيق الموارد البشرية
    path('inventory/', include('inventory.urls_minimal')),  # مسارات تطبيق مخزن قطع الغيار (النسخة المبسطة)
    path('purchase/', include('Purchase_orders.urls')), # مسارات تطبيق طلبات الشراء
    path('administrator/', include('administrator.urls')),  # مسارات تطبيق مدير النظام
    path('notifications/', include('notifications.urls')),  # مسارات تطبيق التنبيهات
    path('', lambda request: redirect('accounts:login'), name='home'),  # إعادة توجيه الصفحة الرئيسية إلى صفحة الحسابات
]

# إضافة مسارات الوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
