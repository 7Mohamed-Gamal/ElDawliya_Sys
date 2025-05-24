from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from .models import SystemSettings, Department, Module

class SystemSettingsForm(forms.ModelForm):
    """Form for system settings configuration."""
    class Meta:
        model = SystemSettings
        fields = [
            'company_name', 'company_address', 'company_phone', 'company_email',
            'company_website', 'company_logo',
            'system_name', 'enable_debugging', 'maintenance_mode',
            'timezone', 'date_format',
            'language', 'font_family', 'text_direction',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'company_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'system_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'enable_debugging': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'timezone': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'date_format': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'text_direction': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة خيارات للمنطقة الزمنية
        timezone_choices = [
            ('Asia/Riyadh', 'الرياض (Asia/Riyadh)'),
            ('Asia/Dubai', 'دبي (Asia/Dubai)'),
            ('Asia/Kuwait', 'الكويت (Asia/Kuwait)'),
            ('Asia/Qatar', 'قطر (Asia/Qatar)'),
            ('Asia/Bahrain', 'البحرين (Asia/Bahrain)'),
            ('Africa/Cairo', 'القاهرة (Africa/Cairo)'),
            ('UTC', 'التوقيت العالمي (UTC)'),
        ]
        self.fields['timezone'].widget = forms.Select(
            choices=timezone_choices,
            attrs={'class': 'form-select', 'required': True}
        )

        # إضافة خيارات لتنسيق التاريخ
        date_format_choices = [
            ('Y-m-d', 'YYYY-MM-DD (2024-01-15)'),
            ('d/m/Y', 'DD/MM/YYYY (15/01/2024)'),
            ('m/d/Y', 'MM/DD/YYYY (01/15/2024)'),
            ('d-m-Y', 'DD-MM-YYYY (15-01-2024)'),
        ]
        self.fields['date_format'].widget = forms.Select(
            choices=date_format_choices,
            attrs={'class': 'form-select', 'required': True}
        )

        # تعيين القيم الحالية للحقول المطلوبة
        if self.instance and self.instance.pk:
            self.fields['timezone'].initial = self.instance.timezone
            self.fields['date_format'].initial = self.instance.date_format

    def clean(self):
        cleaned_data = super().clean()

        # التحقق من الحقول المطلوبة
        company_name = cleaned_data.get('company_name')
        system_name = cleaned_data.get('system_name')
        timezone = cleaned_data.get('timezone')
        date_format = cleaned_data.get('date_format')

        if not company_name:
            self.add_error('company_name', 'اسم الشركة مطلوب')
        if not system_name:
            self.add_error('system_name', 'اسم النظام مطلوب')
        if not timezone:
            self.add_error('timezone', 'المنطقة الزمنية مطلوبة')
        if not date_format:
            self.add_error('date_format', 'تنسيق التاريخ مطلوب')

        return cleaned_data


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
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="وصف المجموعة"
    )

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات"
    )

    users = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="المستخدمون"
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'اسم المجموعة',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing group, pre-select its users
        if self.instance.pk:
            self.initial['users'] = self.instance.user_set.all()

    def save(self, commit=True):
        group = super().save(commit)
        if commit:
            # Update group users
            current_users = set(group.user_set.all())
            selected_users = set(self.cleaned_data.get('users', []))

            # Remove users no longer in the group
            for user in current_users - selected_users:
                user.groups.remove(group)

            # Add new users to the group
            for user in selected_users - current_users:
                user.groups.add(group)

        return group


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
