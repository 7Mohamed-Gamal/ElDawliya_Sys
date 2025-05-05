from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users_Login_New
from ElDawliya_sys.admin_site import admin_site

# Register custom user model with the custom admin site
# Removed @admin.register decorator to avoid double registration
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'IsActive', 'Role']
    list_filter = ['Role', 'IsActive', 'is_staff', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('الوظيفة والصلاحيات', {'fields': ('Role', 'IsActive', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('البيانات الشخصية', {'fields': ('first_name', 'last_name', 'email')}),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

# Register with the custom admin site
admin_site.register(Users_Login_New, CustomUserAdmin)
