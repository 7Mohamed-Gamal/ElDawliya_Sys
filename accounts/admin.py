from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users_Login_New

# Register custom user model
@admin.register(Users_Login_New)
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
