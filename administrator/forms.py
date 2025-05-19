from django import forms
from django.contrib.auth.models import Group, Permission
from .models import SystemSettings, Department, Module

class SystemSettingsForm(forms.ModelForm):
    """Form for system settings configuration."""
    class Meta:
        model = SystemSettings
        fields = [
            'db_host', 'db_name', 'db_user', 'db_password', 'db_port',
            'company_name', 'company_address', 'company_phone', 'company_email',
            'company_website', 'company_logo',
            'system_name', 'enable_debugging', 'maintenance_mode',
            'timezone', 'date_format',
            'language', 'font_family', 'text_direction',
        ]
        widgets = {
            'db_password': forms.PasswordInput(render_value=True),
            'company_address': forms.Textarea(attrs={'rows': 3}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'text_direction': forms.Select(attrs={'class': 'form-select'}),
        }


class DepartmentForm(forms.ModelForm):
    """Form for department configuration."""
    class Meta:
        model = Department
        fields = ['name', 'icon', 'url_name', 'description', 'is_active', 'order', 'require_admin', 'groups']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }


class ModuleForm(forms.ModelForm):
    """Form for module configuration."""
    class Meta:
        model = Module
        fields = ['department', 'name', 'icon', 'url', 'description', 'is_active', 'order', 'bg_color']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'bg_color': forms.TextInput(attrs={'type': 'color'}),
        }


class DatabaseConfigForm(forms.Form):
    """Form for database configuration."""
    db_engine = forms.ChoiceField(
        choices=[
            ('mssql', 'SQL Server (للإنتاج)'),
        ],
        label="نوع قاعدة البيانات",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    db_connection_type = forms.ChoiceField(
        choices=[
            ('default', 'الاتصال الافتراضي (Default)'),
            ('primary', 'الاتصال الاحتياطي (Primary)'),
        ],
        label="نوع الاتصال بقاعدة البيانات",
        help_text="اختر نوع الاتصال بقاعدة البيانات. سيتم محاولة الاتصال بالنوع المحدد أولاً، وإذا فشل الاتصال سيتم الانتقال تلقائيًا إلى النوع الآخر.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    db_name = forms.CharField(
        max_length=100,
        label="اسم قاعدة البيانات",
        required=True
    )

    db_name_sqlite = forms.CharField(
        max_length=100,
        label="اسم ملف SQLite",
        required=False,
        initial="db.sqlite3"
    )

    db_name_mssql = forms.CharField(
        max_length=100,
        label="اسم قاعدة بيانات SQL Server",
        required=False,
        initial="El_Dawliya_International"
    )

    db_host = forms.CharField(
        max_length=100,
        label="عنوان الخادم",
        required=False,
        initial="localhost"
    )

    db_port = forms.CharField(
        max_length=10,
        label="المنفذ",
        required=False,
        initial="1433"
    )

    use_windows_auth = forms.BooleanField(
        label="استخدام مصادقة Windows",
        required=False,
        initial=True
    )

    db_user = forms.CharField(
        max_length=100,
        label="اسم المستخدم",
        required=False
    )

    db_password = forms.CharField(
        max_length=100,
        label="كلمة المرور",
        required=False,
        widget=forms.PasswordInput(render_value=True)
    )


class GroupForm(forms.ModelForm):
    """Form for managing user groups."""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات"
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'اسم المجموعة',
        }


class UserPermissionForm(forms.Form):
    """Form for managing user permissions."""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات"
    )


class GroupPermissionForm(forms.Form):
    """Form for managing group permissions."""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات"
    )
