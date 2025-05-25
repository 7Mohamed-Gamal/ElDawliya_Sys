from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Users_Login_New
from django.contrib.auth.models import Permission

# Register custom user model with the custom admin site
# Removed @admin.register decorator to avoid double registration
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'Role']
    list_filter = ['Role', 'is_active', 'is_staff', 'is_superuser', 'groups']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('الوظيفة والصلاحيات'), {'fields': ('Role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('البيانات الشخصية'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('تواريخ مهمة'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ['last_login', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    filter_horizontal = ['groups', 'user_permissions']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        # إذا لم يكن المستخدم مشرفًا، قم بتقييد الحقول التي يمكنه تعديلها
        if not is_superuser:
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].disabled = True

        return form

# Register Permission model to allow managing permissions directly
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'codename']
    list_filter = ['content_type']
    search_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'content_type__model', 'codename']

    def has_add_permission(self, request):
        # Don't allow adding permissions manually - they should be created by Django
        return False

    def has_delete_permission(self, request, obj=None):
        # Don't allow deleting permissions - they should be managed by Django
        return False

# Register with the default admin site
admin.site.register(Users_Login_New, CustomUserAdmin)
admin.site.register(Permission, PermissionAdmin)
