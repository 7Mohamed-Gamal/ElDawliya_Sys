from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.db.models import Count

from .models import Department, Module, Permission, TemplatePermission
from .forms import GroupPermissionForm
from .views import system_admin_required


@login_required
@system_admin_required
def improved_edit_group_permissions(request, group_id):
    """
    Vista mejorada para editar permisos de grupo con una interfaz más intuitiva y profesional.
    """
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            # Actualizar departamentos y módulos
            departments = form.cleaned_data['departments']
            modules = form.cleaned_data['modules']
            
            # Limpiar y actualizar relaciones de departamentos
            group.allowed_departments.clear()
            for dept in departments:
                group.allowed_departments.add(dept)
            
            # Limpiar y actualizar relaciones de módulos
            group.allowed_modules.clear()
            for module in modules:
                group.allowed_modules.add(module)
            
            # Gestionar permisos por tipo
            for perm_type in ['view', 'add', 'change', 'delete', 'print']:
                # Obtener permisos actuales de este tipo
                current_perms = set(Permission.objects.filter(
                    permission_type=perm_type,
                    groups=group
                ).values_list('id', flat=True))
                
                # Obtener permisos seleccionados
                selected_perms = set([p.id for p in form.cleaned_data[f'{perm_type}_permissions']])
                
                # Eliminar permisos que ya no están seleccionados
                perms_to_remove = current_perms - selected_perms
                if perms_to_remove:
                    for perm_id in perms_to_remove:
                        perm = Permission.objects.get(id=perm_id)
                        perm.groups.remove(group)
                
                # Añadir nuevos permisos seleccionados
                for perm in form.cleaned_data[f'{perm_type}_permissions']:
                    if perm.id not in current_perms:
                        perm.groups.add(group)
            
            # Gestionar permisos de plantillas
            current_templates = set(TemplatePermission.objects.filter(
                groups=group
            ).values_list('id', flat=True))
            
            selected_templates = set([t.id for t in form.cleaned_data['templates']])
            
            # Eliminar plantillas que ya no están seleccionadas
            templates_to_remove = current_templates - selected_templates
            if templates_to_remove:
                for template_id in templates_to_remove:
                    template = TemplatePermission.objects.get(id=template_id)
                    template.groups.remove(group)
            
            # Añadir nuevas plantillas seleccionadas
            for template in form.cleaned_data['templates']:
                if template.id not in current_templates:
                    template.groups.add(group)
            
            messages.success(request, f'تم تحديث صلاحيات المجموعة {group.name} بنجاح')
            
            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'تم تحديث صلاحيات المجموعة {group.name} بنجاح'
                })
            
            return redirect('administrator:group_permission_list')
        else:
            # Si hay errores en el formulario y es una solicitud AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'حدث خطأ أثناء حفظ الصلاحيات',
                    'errors': form.errors
                }, status=400)
    else:
        # Inicializar formulario con permisos actuales
        initial_data = {
            'group': group,
            'departments': Department.objects.filter(allowed_by_groups=group).distinct(),
            'modules': Module.objects.filter(allowed_by_groups=group).distinct(),
            'view_permissions': Permission.objects.filter(permission_type='view', groups=group),
            'add_permissions': Permission.objects.filter(permission_type='add', groups=group),
            'change_permissions': Permission.objects.filter(permission_type='change', groups=group),
            'delete_permissions': Permission.objects.filter(permission_type='delete', groups=group),
            'print_permissions': Permission.objects.filter(permission_type='print', groups=group),
            'templates': TemplatePermission.objects.filter(groups=group),
        }
        form = GroupPermissionForm(initial=initial_data)
    
    # Obtener todos los departamentos para la interfaz
    departments = Department.objects.prefetch_related('module_set').all()
    
    # Obtener aplicaciones únicas para filtrar plantillas
    template_apps = TemplatePermission.objects.values_list('app_name', flat=True).distinct()
    
    context = {
        'form': form,
        'group': group,
        'departments': departments,
        'template_apps': template_apps,
        'title': f'تعديل صلاحيات {group.name} - النظام المحسن'
    }
    
    return render(request, 'administrator/improved_edit_group_permissions.html', context)