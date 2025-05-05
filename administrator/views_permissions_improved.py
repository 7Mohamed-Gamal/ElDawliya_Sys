from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import Group
from django.db.models import Q

from .models import Department, Module, Permission, TemplatePermission
from .forms_improved import ImprovedGroupPermissionForm, ImprovedTemplatePermissionForm, ImprovedModuleForm
from .views import system_admin_required


@login_required
@system_admin_required
def improved_group_permissions(request, group_id=None):
    """Vista mejorada para gestionar permisos de grupo de manera más intuitiva."""
    
    # Si se proporciona un ID de grupo, obtener el grupo
    group = None
    if group_id:
        group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = ImprovedGroupPermissionForm(request.POST, group_id=group_id)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'تم حفظ صلاحيات المجموعة "{group.name}" بنجاح')
            return redirect('administrator:improved_group_permissions', group_id=group.id)
    else:
        # Si hay un grupo seleccionado, inicializar el formulario con sus permisos actuales
        initial_data = {}
        if group:
            # Marcar departamentos permitidos
            for dept in group.allowed_departments.all():
                initial_data[f'dept_{dept.id}'] = True
            
            # Marcar módulos permitidos
            for module in group.allowed_modules.all():
                initial_data[f'module_{module.id}'] = True
            
            # Marcar permisos asignados
            for permission in Permission.objects.filter(groups=group):
                field_name = f'perm_{permission.module.id}_{permission.permission_type}'
                initial_data[field_name] = True
            
            form = ImprovedGroupPermissionForm(initial=initial_data, group_id=group_id)
        else:
            form = ImprovedGroupPermissionForm()
    
    # Obtener todos los grupos para el selector
    groups = Group.objects.all().order_by('name')
    
    context = {
        'form': form,
        'groups': groups,
        'selected_group': group,
        'page_title': 'إدارة صلاحيات المجموعات - النظام المحسن',
    }
    
    return render(request, 'administrator/improved_group_permissions.html', context)


@login_required
@system_admin_required
def improved_template_permission_create(request):
    """Vista mejorada para crear permisos de plantilla."""
    if request.method == 'POST':
        form = ImprovedTemplatePermissionForm(request.POST)
        if form.is_valid():
            template_permission = form.save()
            messages.success(request, 'تم إنشاء صلاحية القالب بنجاح')
            return redirect('administrator:template_permission_list')
    else:
        form = ImprovedTemplatePermissionForm()
    
    context = {
        'form': form,
        'page_title': 'إضافة صلاحية قالب جديدة - النظام المحسن',
    }
    
    return render(request, 'administrator/improved_template_permission_form.html', context)


@login_required
@system_admin_required
def improved_template_permission_update(request, pk):
    """Vista mejorada para actualizar permisos de plantilla."""
    template_permission = get_object_or_404(TemplatePermission, pk=pk)
    
    if request.method == 'POST':
        form = ImprovedTemplatePermissionForm(request.POST, instance=template_permission)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث صلاحية القالب بنجاح')
            return redirect('administrator:template_permission_list')
    else:
        form = ImprovedTemplatePermissionForm(instance=template_permission)
    
    context = {
        'form': form,
        'template_permission': template_permission,
        'page_title': f'تعديل صلاحية القالب: {template_permission.name} - النظام المحسن',
    }
    
    return render(request, 'administrator/improved_template_permission_form.html', context)


@login_required
@system_admin_required
def improved_module_create(request):
    """Vista mejorada para crear módulos con sugerencias de URL."""
    if request.method == 'POST':
        form = ImprovedModuleForm(request.POST)
        if form.is_valid():
            module = form.save()
            messages.success(request, 'تم إنشاء الوحدة بنجاح')
            
            # Crear permisos básicos para este módulo
            permission_types = ['view', 'add', 'change', 'delete']
            for perm_type in permission_types:
                Permission.objects.get_or_create(
                    module=module,
                    permission_type=perm_type,
                    defaults={'is_active': True}
                )
            
            return redirect('administrator:module_list')
    else:
        form = ImprovedModuleForm()
    
    context = {
        'form': form,
        'page_title': 'إضافة وحدة جديدة - النظام المحسن',
    }
    
    return render(request, 'administrator/improved_module_form.html', context)


@login_required
@system_admin_required
def improved_module_update(request, pk):
    """Vista mejorada para actualizar módulos."""
    module = get_object_or_404(Module, pk=pk)
    
    if request.method == 'POST':
        form = ImprovedModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الوحدة بنجاح')
            return redirect('administrator:module_list')
    else:
        form = ImprovedModuleForm(instance=module)
    
    context = {
        'form': form,
        'module': module,
        'page_title': f'تعديل الوحدة: {module.name} - النظام المحسن',
    }
    
    return render(request, 'administrator/improved_module_form.html', context)