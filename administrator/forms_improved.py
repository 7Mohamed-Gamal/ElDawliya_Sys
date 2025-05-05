from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import (
    Department, Module, Permission, TemplatePermission, 
    UserGroup, SystemSettings
)

User = get_user_model()


class ImprovedGroupPermissionForm(forms.Form):
    """
    Formulario mejorado para gestionar permisos de grupo de manera más intuitiva.
    """
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="المجموعة",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        group_id = kwargs.pop('group_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona un ID de grupo, preseleccionarlo
        if group_id:
            try:
                self.fields['group'].initial = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                pass
        
        # Obtener todos los departamentos
        departments = Department.objects.all().order_by('order')
        
        # Para cada departamento, crear un conjunto de campos para sus módulos y permisos
        for dept in departments:
            # Campo para activar/desactivar todo el departamento
            self.fields[f'dept_{dept.id}'] = forms.BooleanField(
                label=dept.name,
                required=False,
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input department-toggle',
                    'data-department-id': dept.id
                })
            )
            
            # Obtener módulos de este departamento
            modules = Module.objects.filter(department=dept).order_by('order')
            
            for module in modules:
                # Campo para activar/desactivar todo el módulo
                self.fields[f'module_{module.id}'] = forms.BooleanField(
                    label=module.name,
                    required=False,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input module-toggle',
                        'data-department-id': dept.id,
                        'data-module-id': module.id
                    })
                )
                
                # Campos para cada tipo de permiso
                for perm_type, perm_label in Permission.PERMISSION_TYPES:
                    field_name = f'perm_{module.id}_{perm_type}'
                    self.fields[field_name] = forms.BooleanField(
                        label=perm_label,
                        required=False,
                        widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input permission-checkbox',
                            'data-department-id': dept.id,
                            'data-module-id': module.id,
                            'data-permission-type': perm_type
                        })
                    )
    
    def get_departments(self):
        """Retorna todos los departamentos ordenados para renderizar el formulario."""
        return Department.objects.all().order_by('order')
    
    def get_modules_for_department(self, department):
        """Retorna todos los módulos para un departamento específico."""
        return Module.objects.filter(department=department).order_by('order')
    
    def get_permission_types(self):
        """Retorna los tipos de permisos disponibles."""
        return Permission.PERMISSION_TYPES
    
    def save(self, commit=True):
        """Guarda los permisos seleccionados para el grupo."""
        if not commit:
            return None
            
        group = self.cleaned_data['group']
        
        # Limpiar permisos existentes
        permissions = Permission.objects.filter(groups=group)
        for permission in permissions:
            permission.groups.remove(group)
        
        # Departamentos seleccionados
        selected_departments = []
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('dept_') and value:
                dept_id = int(field_name.split('_')[1])
                selected_departments.append(dept_id)
        
        # Actualizar departamentos permitidos
        group.allowed_departments.clear()
        for dept_id in selected_departments:
            try:
                dept = Department.objects.get(id=dept_id)
                group.allowed_departments.add(dept)
            except Department.DoesNotExist:
                pass
        
        # Módulos seleccionados
        selected_modules = []
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('module_') and value:
                module_id = int(field_name.split('_')[1])
                selected_modules.append(module_id)
        
        # Actualizar módulos permitidos
        group.allowed_modules.clear()
        for module_id in selected_modules:
            try:
                module = Module.objects.get(id=module_id)
                group.allowed_modules.add(module)
            except Module.DoesNotExist:
                pass
        
        # Permisos seleccionados
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('perm_') and value:
                parts = field_name.split('_')
                module_id = int(parts[1])
                perm_type = parts[2]
                
                try:
                    module = Module.objects.get(id=module_id)
                    permission, created = Permission.objects.get_or_create(
                        module=module,
                        permission_type=perm_type,
                        defaults={'is_active': True}
                    )
                    permission.groups.add(group)
                except Module.DoesNotExist:
                    pass
        
        return group


class ImprovedTemplatePermissionForm(forms.ModelForm):
    """Formulario mejorado para gestionar permisos de plantillas."""
    
    # Campos para ayudar a seleccionar plantillas comunes
    COMMON_TEMPLATES = [
        ('', '-- اختر من القوالب الشائعة --'),
        ('accounts/profile.html', 'صفحة الملف الشخصي'),
        ('accounts/dashboard.html', 'لوحة التحكم الرئيسية'),
        ('inventory/dashboard_inventory.html', 'لوحة تحكم المخزون'),
        ('inventory/product_list.html', 'قائمة المنتجات'),
        ('inventory/invoice_list.html', 'قائمة الفواتير'),
        ('hr/employee_list.html', 'قائمة الموظفين'),
        ('hr/dashboard_hr.html', 'لوحة تحكم الموارد البشرية'),
    ]
    
    COMMON_URL_PATTERNS = [
        ('', '-- اختر من أنماط URL الشائعة --'),
        ('accounts/profile/', 'صفحة الملف الشخصي'),
        ('accounts/dashboard/', 'لوحة التحكم الرئيسية'),
        ('inventory/', 'الصفحة الرئيسية للمخزون'),
        ('inventory/products/', 'قائمة المنتجات'),
        ('inventory/invoices/', 'قائمة الفواتير'),
        ('hr/', 'الصفحة الرئيسية للموارد البشرية'),
        ('hr/employees/', 'قائمة الموظفين'),
    ]
    
    common_template_selector = forms.ChoiceField(
        choices=COMMON_TEMPLATES,
        required=False,
        label="اختر من القوالب الشائعة",
        widget=forms.Select(attrs={'class': 'form-select mb-2'})
    )
    
    common_url_selector = forms.ChoiceField(
        choices=COMMON_URL_PATTERNS,
        required=False,
        label="اختر من أنماط URL الشائعة",
        widget=forms.Select(attrs={'class': 'form-select mb-2'})
    )
    
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
        help_texts = {
            'template_path': 'مسار القالب داخل مجلد القوالب. مثال: inventory/product_list.html',
            'url_pattern': 'نمط URL المرتبط بهذا القالب. مثال: inventory/products/',
            'app_name': 'اسم التطبيق الذي يحتوي على القالب. مثال: inventory أو accounts',
        }


class ImprovedModuleForm(forms.ModelForm):
    """Formulario mejorado para gestionar módulos con sugerencias de URL."""
    
    COMMON_URLS = [
        ('', '-- اختر من الروابط الشائعة --'),
        ('/inventory/', 'الصفحة الرئيسية للمخزون'),
        ('/inventory/products/', 'قائمة المنتجات'),
        ('/inventory/invoices/', 'قائمة الفواتير'),
        ('/hr/', 'الصفحة الرئيسية للموارد البشرية'),
        ('/hr/employees/', 'قائمة الموظفين'),
        ('/accounts/profile/', 'الملف الشخصي'),
        ('/accounts/dashboard/', 'لوحة التحكم الرئيسية'),
    ]
    
    common_url_selector = forms.ChoiceField(
        choices=COMMON_URLS,
        required=False,
        label="اختر من الروابط الشائعة",
        widget=forms.Select(attrs={'class': 'form-select mb-2'})
    )
    
    class Meta:
        model = Module
        fields = ['department', 'name', 'icon', 'url', 'description', 'is_active', 'order', 'bg_color', 'require_admin', 'groups']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'bg_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'require_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }
        help_texts = {
            'url': 'الرابط الذي سيتم توجيه المستخدم إليه عند النقر على هذه الوحدة. مثال: /inventory/ أو /tasks/view/',
        }
