from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import SystemSettings, Department, Module, Permission, TemplatePermission, UserGroup

User = get_user_model()


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
            ('sqlite3', 'SQLite (للتطوير)'),
            ('mssql', 'SQL Server (للإنتاج)'),
        ],
        label="نوع قاعدة البيانات",
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


class PermissionForm(forms.ModelForm):
    """Form for managing module permissions."""
    class Meta:
        model = Permission
        fields = ['module', 'permission_type', 'is_active', 'groups', 'users']
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
            'users': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        }


class TemplatePermissionForm(forms.ModelForm):
    """Form for managing template/view permissions."""
    class Meta:
        model = TemplatePermission
        fields = ['name', 'app_name', 'template_path', 'url_pattern', 'description', 'is_active', 'groups', 'users']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'app_name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_path': forms.TextInput(attrs={'class': 'form-control'}),
            'url_pattern': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
            'users': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        }


class UserGroupForm(forms.ModelForm):
    """Form for managing user group membership."""
    class Meta:
        model = UserGroup
        fields = ['user', 'group', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'user': 'المستخدم',
            'group': 'المجموعة',
            'notes': 'ملاحظات',
        }


class GroupForm(forms.ModelForm):
    """Form for creating and editing groups."""
    description = forms.CharField(
        label="وصف المجموعة",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="المستخدمون",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10})
    )

    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'اسم المجموعة',
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        # If we have an instance, get its profile and users
        if instance:
            try:
                profile = instance.profile
                initial['description'] = profile.description
            except:
                pass

            # Get current users in this group
            initial['users'] = User.objects.filter(groups=instance)

        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        group = super().save(commit=commit)

        if commit:
            # Get or create the profile
            from .models import GroupProfile
            profile, created = GroupProfile.objects.get_or_create(group=group)

            # Update the description
            profile.description = self.cleaned_data.get('description', '')
            profile.save()

            # Update users in the group
            selected_users = self.cleaned_data.get('users', [])

            # Get current users in the group
            current_users = User.objects.filter(groups=group)

            # Remove users that are no longer selected
            for user in current_users:
                if user not in selected_users:
                    user.groups.remove(group)

            # Add newly selected users
            for user in selected_users:
                if user not in current_users:
                    user.groups.add(group)

        return group


class UserPermissionForm(forms.Form):
    """Custom form for managing user permissions."""
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="المستخدم",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        label="المجموعات",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    view_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='view'),
        label="صلاحيات العرض",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    add_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='add'),
        label="صلاحيات الإضافة",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    change_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='change'),
        label="صلاحيات التعديل",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    delete_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='delete'),
        label="صلاحيات الحذف",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    print_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='print'),
        label="صلاحيات الطباعة",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    templates = forms.ModelMultipleChoiceField(
        queryset=TemplatePermission.objects.all(),
        label="القوالب المسموح بها",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )


class GroupPermissionForm(forms.Form):
    """Custom form for managing group permissions."""
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="المجموعة",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        label="الأقسام المسموح بها",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        label="الوحدات المسموح بها",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    view_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='view'),
        label="صلاحيات العرض",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    add_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='add'),
        label="صلاحيات الإضافة",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    change_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='change'),
        label="صلاحيات التعديل",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    delete_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='delete'),
        label="صلاحيات الحذف",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    print_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(permission_type='print'),
        label="صلاحيات الطباعة",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    templates = forms.ModelMultipleChoiceField(
        queryset=TemplatePermission.objects.all(),
        label="القوالب المسموح بها",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )


class UnifiedPermissionForm(forms.Form):
    """Unified form for managing permissions in a single screen."""
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="المستخدم",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="المجموعة",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'] = forms.MultipleChoiceField(
            choices=self._get_permission_choices(),
            label="الصلاحيات",
            required=False,
            widget=forms.CheckboxSelectMultiple()
        )

    def _get_permission_choices(self):
        """Get all possible permission choices for modules."""
        choices = []
        for dept in Department.objects.all():
            for module in dept.modules.all():
                for perm in Permission.PERMISSION_TYPES:
                    perm_id = f"{module.id}_{perm[0]}"
                    perm_label = f"{dept.name} - {module.name} - {dict(Permission.PERMISSION_TYPES)[perm[0]]}"
                    choices.append((perm_id, perm_label))
        return choices
