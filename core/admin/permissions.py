"""
Admin interface for hierarchical permissions system
واجهة الإدارة لنظام الصلاحيات الهرمي
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import widgets

from ..models.permissions import (
    Module, Permission, Role, UserRole, ObjectPermission,
    ApprovalWorkflow, ApprovalStep, PermissionCache
)

User = get_user_model()


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """
    Admin interface for system modules
    واجهة إدارة وحدات النظام
    """
    list_display = ['display_name', 'name', 'parent', 'order', 'is_active', 'permissions_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['order', 'display_name']
    list_editable = ['order', 'is_active']

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'display_name', 'description', 'parent')
        }),
        ('إعدادات العرض', {
            'fields': ('icon', 'order', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def permissions_count(self, obj):
        """Display count of permissions for this module"""
        count = obj.permissions.count()
        if count > 0:
            url = reverse('admin:core_permission_changelist') + f'?module__id__exact={obj.id}'
            return format_html('<a href="{}">{} صلاحية</a>', url, count)
        return '0 صلاحية'
    permissions_count.short_description = 'عدد الصلاحيات'

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('parent')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for permissions
    واجهة إدارة الصلاحيات
    """
    list_display = ['name', 'module', 'permission_type', 'scope', 'is_sensitive', 'is_active']
    list_filter = ['permission_type', 'scope', 'is_sensitive', 'is_active', 'module']
    search_fields = ['name', 'codename', 'description']
    ordering = ['module__order', 'permission_type', 'name']
    list_editable = ['is_active']

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('module', 'permission_type', 'codename', 'name', 'description')
        }),
        ('إعدادات الصلاحية', {
            'fields': ('scope', 'is_sensitive', 'requires_approval', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at']

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('module')


class UserRoleInline(admin.TabularInline):
    """
    Inline for user roles in Role admin
    """
    model = UserRole
    extra = 0
    fields = ['user', 'granted_by', 'granted_at', 'expires_at', 'is_active']
    readonly_fields = ['granted_at']

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('user', 'granted_by')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin interface for roles
    واجهة إدارة الأدوار
    """
    list_display = ['display_name', 'name', 'role_type', 'parent_role', 'users_count', 'is_active']
    list_filter = ['role_type', 'is_system_role', 'is_active', 'parent_role']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['display_name']
    list_editable = ['is_active']

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'display_name', 'description', 'role_type')
        }),
        ('الهيكل الهرمي', {
            'fields': ('parent_role',)
        }),
        ('إعدادات الدور', {
            'fields': ('is_system_role', 'is_active', 'max_users')
        }),
        ('الصلاحيات', {
            'fields': ('permissions',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['permissions']
    inlines = [UserRoleInline]

    def users_count(self, obj):
        """Display count of users assigned to this role"""
        count = obj.get_users_count()
        if count > 0:
            url = reverse('admin:core_userrole_changelist') + f'?role__id__exact={obj.id}'
            return format_html('<a href="{}">{} مستخدم</a>', url, count)
        return '0 مستخدم'
    users_count.short_description = 'عدد المستخدمين'

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('parent_role')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for user role assignments
    واجهة إدارة تعيينات أدوار المستخدمين
    """
    list_display = ['user', 'role', 'granted_by', 'granted_at', 'expires_at', 'is_active', 'status']
    list_filter = ['is_active', 'role', 'granted_at', 'expires_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'role__name']
    ordering = ['-granted_at']
    list_editable = ['is_active']
    date_hierarchy = 'granted_at'

    fieldsets = (
        ('تعيين الدور', {
            'fields': ('user', 'role', 'granted_by')
        }),
        ('إعدادات الوقت', {
            'fields': ('granted_at', 'expires_at', 'is_active')
        }),
        ('شروط إضافية', {
            'fields': ('conditions', 'notes'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['granted_at']

    def status(self, obj):
        """Display status of role assignment"""
        if not obj.is_active:
            return format_html('<span style="color: red;">معطل</span>')
        elif obj.is_expired():
            return format_html('<span style="color: orange;">منتهي الصلاحية</span>')
        else:
            return format_html('<span style="color: green;">نشط</span>')
    status.short_description = 'الحالة'

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('user', 'role', 'granted_by')


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for object-level permissions
    واجهة إدارة الصلاحيات على مستوى الكائن
    """
    list_display = ['user', 'permission', 'content_type', 'object_id', 'granted_by', 'granted_at', 'is_active']
    list_filter = ['is_active', 'permission', 'content_type', 'granted_at']
    search_fields = ['user__username', 'permission__name', 'object_id']
    ordering = ['-granted_at']
    date_hierarchy = 'granted_at'

    fieldsets = (
        ('صلاحية الكائن', {
            'fields': ('user', 'permission', 'content_type', 'object_id')
        }),
        ('معلومات المنح', {
            'fields': ('granted_by', 'granted_at', 'expires_at', 'is_active')
        }),
    )

    readonly_fields = ['granted_at']

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related(
            'user', 'permission', 'content_type', 'granted_by'
        )


class ApprovalStepInline(admin.TabularInline):
    """
    Inline for approval steps in ApprovalWorkflow admin
    """
    model = ApprovalStep
    extra = 0
    fields = ['level', 'name', 'requires_all', 'status', 'approved_by', 'approved_at']
    readonly_fields = ['approved_at']
    ordering = ['level']


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    """
    Admin interface for approval workflows
    واجهة إدارة سير عمل الموافقات
    """
    list_display = ['title', 'workflow_type', 'requested_by', 'target_user', 'status', 'created_at']
    list_filter = ['workflow_type', 'status', 'created_at']
    search_fields = ['title', 'description', 'requested_by__username', 'target_user__username']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('معلومات سير العمل', {
            'fields': ('workflow_type', 'title', 'description')
        }),
        ('المستخدمون', {
            'fields': ('requested_by', 'target_user')
        }),
        ('الحالة والبيانات', {
            'fields': ('status', 'data')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
    inlines = [ApprovalStepInline]

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('requested_by', 'target_user')


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    """
    Admin interface for approval steps
    واجهة إدارة خطوات الموافقة
    """
    list_display = ['workflow', 'level', 'name', 'status', 'approved_by', 'approved_at']
    list_filter = ['status', 'approved_at']
    search_fields = ['workflow__title', 'name']
    ordering = ['workflow', 'level']

    fieldsets = (
        ('خطوة الموافقة', {
            'fields': ('workflow', 'level', 'name', 'requires_all')
        }),
        ('المعتمدون', {
            'fields': ('approvers',)
        }),
        ('حالة الموافقة', {
            'fields': ('status', 'approved_by', 'approved_at', 'comments')
        }),
    )

    readonly_fields = ['approved_at']
    filter_horizontal = ['approvers']

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('workflow', 'approved_by')


@admin.register(PermissionCache)
class PermissionCacheAdmin(admin.ModelAdmin):
    """
    Admin interface for permission cache
    واجهة إدارة ذاكرة تخزين الصلاحيات
    """
    list_display = ['user', 'permission_hash_short', 'created_at', 'expires_at', 'is_expired_status']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__username', 'permission_hash']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('ذاكرة التخزين المؤقت', {
            'fields': ('user', 'permission_hash', 'permissions_data')
        }),
        ('معلومات الوقت', {
            'fields': ('created_at', 'expires_at')
        }),
    )

    readonly_fields = ['created_at']

    def permission_hash_short(self, obj):
        """Display shortened permission hash"""
        return f"{obj.permission_hash[:16]}..."
    permission_hash_short.short_description = 'هاش الصلاحية'

    def is_expired_status(self, obj):
        """Display expiration status"""
        if obj.is_expired():
            return format_html('<span style="color: red;">منتهي الصلاحية</span>')
        else:
            return format_html('<span style="color: green;">صالح</span>')
    is_expired_status.short_description = 'حالة الصلاحية'

    def get_queryset(self, request):
        """get_queryset function"""
        return super().get_queryset(request).select_related('user')

    actions = ['clear_expired_cache']

    def clear_expired_cache(self, request, queryset):
        """Clear expired cache entries"""
        from django.utils import timezone
        expired_count = queryset.filter(expires_at__lt=timezone.now()).delete()[0]
        self.message_user(request, f'تم حذف {expired_count} إدخال منتهي الصلاحية من ذاكرة التخزين المؤقت.')
    clear_expired_cache.short_description = 'حذف الإدخالات منتهية الصلاحية'


# Custom admin site configuration
class PermissionAdminSite(admin.AdminSite):
    """
    Custom admin site for permissions management
    موقع إدارة مخصص لإدارة الصلاحيات
    """
    site_header = 'إدارة الصلاحيات الهرمية'
    site_title = 'نظام الصلاحيات'
    index_title = 'لوحة تحكم الصلاحيات'

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)

        # Custom ordering for permissions app
        for app in app_list:
            if app['name'] == 'Core':
                # Custom model ordering
                model_order = [
                    'Module', 'Permission', 'Role', 'UserRole',
                    'ObjectPermission', 'ApprovalWorkflow', 'ApprovalStep',
                    'PermissionCache'
                ]

                app['models'].sort(key=lambda x: (
                    model_order.index(x['object_name'])
                    if x['object_name'] in model_order
                    else len(model_order)
                ))

        return app_list


# Create custom admin site instance
permission_admin_site = PermissionAdminSite(name='permission_admin')

# Register models with custom admin site
permission_admin_site.register(Module, ModuleAdmin)
permission_admin_site.register(Permission, PermissionAdmin)
permission_admin_site.register(Role, RoleAdmin)
permission_admin_site.register(UserRole, UserRoleAdmin)
permission_admin_site.register(ObjectPermission, ObjectPermissionAdmin)
permission_admin_site.register(ApprovalWorkflow, ApprovalWorkflowAdmin)
permission_admin_site.register(ApprovalStep, ApprovalStepAdmin)
permission_admin_site.register(PermissionCache, PermissionCacheAdmin)
