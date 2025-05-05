import django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q

from .models import (
    Department, Module, Permission,
    TemplatePermission, UserGroup
)
from .forms import (
    PermissionForm, TemplatePermissionForm, UserGroupForm, GroupForm,
    UserPermissionForm, GroupPermissionForm, UnifiedPermissionForm
)
from .views import system_admin_required
from accounts.forms import CustomUserCreationForm

User = get_user_model()


# Permission Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionListView(ListView):
    """List all permissions for modules"""
    model = Permission
    template_name = 'administrator/permission_list.html'
    context_object_name = 'permissions'
    paginate_by = 50  # تقسيم النتائج إلى صفحات لتحسين الأداء

    def get_queryset(self):
        queryset = Permission.objects.select_related('module', 'module__department').prefetch_related('groups', 'users')

        # البحث حسب المعايير المختلفة
        search_query = self.request.GET.get('search', '')
        department_id = self.request.GET.get('department', '')
        permission_type = self.request.GET.get('permission_type', '')
        is_active = self.request.GET.get('is_active', '')

        if search_query:
            queryset = queryset.filter(
                Q(module__name__icontains=search_query) |
                Q(module__department__name__icontains=search_query)
            )

        if department_id:
            queryset = queryset.filter(module__department_id=department_id)

        if permission_type:
            queryset = queryset.filter(permission_type=permission_type)

        if is_active in ['true', 'false']:
            is_active_bool = is_active == 'true'
            queryset = queryset.filter(is_active=is_active_bool)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # إضافة قائمة الأقسام للفلترة
        context['departments'] = Department.objects.all()
        # إضافة أنواع الصلاحيات للفلترة
        context['permission_types'] = Permission.PERMISSION_TYPES
        # إضافة معايير البحث الحالية للحفاظ عليها عند تغيير الصفحة
        context['current_search'] = self.request.GET.get('search', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['current_permission_type'] = self.request.GET.get('permission_type', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionCreateView(CreateView):
    """Create a new permission"""
    model = Permission
    form_class = PermissionForm
    template_name = 'administrator/permission_form.html'
    success_url = reverse_lazy('administrator:permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الصلاحية بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionUpdateView(UpdateView):
    """Update an existing permission"""
    model = Permission
    form_class = PermissionForm
    template_name = 'administrator/permission_form.html'
    success_url = reverse_lazy('administrator:permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الصلاحية بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class PermissionDeleteView(DeleteView):
    """Delete a permission"""
    model = Permission
    template_name = 'administrator/permission_confirm_delete.html'
    success_url = reverse_lazy('administrator:permission_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الصلاحية بنجاح')
        return super().delete(request, *args, **kwargs)


# Template Permission Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionListView(ListView):
    """List all template permissions"""
    model = TemplatePermission
    template_name = 'administrator/template_permission_list.html'
    context_object_name = 'template_permissions'


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionCreateView(CreateView):
    """Create a new template permission"""
    model = TemplatePermission
    form_class = TemplatePermissionForm
    template_name = 'administrator/template_permission_form.html'
    success_url = reverse_lazy('administrator:template_permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء صلاحية القالب بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionUpdateView(UpdateView):
    """Update an existing template permission"""
    model = TemplatePermission
    form_class = TemplatePermissionForm
    template_name = 'administrator/template_permission_form.html'
    success_url = reverse_lazy('administrator:template_permission_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث صلاحية القالب بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class TemplatePermissionDeleteView(DeleteView):
    """Delete a template permission"""
    model = TemplatePermission
    template_name = 'administrator/template_permission_confirm_delete.html'
    success_url = reverse_lazy('administrator:template_permission_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف صلاحية القالب بنجاح')
        return super().delete(request, *args, **kwargs)


# Group Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupListView(ListView):
    """List all user groups"""
    model = Group
    template_name = 'administrator/group_list.html'
    context_object_name = 'groups'


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupCreateView(CreateView):
    """Create a new user group"""
    model = Group
    form_class = GroupForm
    template_name = 'administrator/group_form.html'
    success_url = reverse_lazy('administrator:group_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء المجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupDetailView(DetailView):
    """View details of a user group"""
    model = Group
    template_name = 'administrator/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        # Get users in this group
        context['users'] = User.objects.filter(groups=group)
        # Get permissions for this group
        context['permissions'] = Permission.objects.filter(groups=group)
        # Get template permissions for this group
        context['template_permissions'] = TemplatePermission.objects.filter(groups=group)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupUpdateView(UpdateView):
    """Update an existing user group"""
    model = Group
    form_class = GroupForm
    template_name = 'administrator/group_form.html'
    success_url = reverse_lazy('administrator:group_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class GroupDeleteView(DeleteView):
    """Delete a user group"""
    model = Group
    template_name = 'administrator/group_confirm_delete.html'
    success_url = reverse_lazy('administrator:group_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المجموعة بنجاح')
        return super().delete(request, *args, **kwargs)


# User-Group Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupListView(ListView):
    """List all user-group memberships"""
    model = UserGroup
    template_name = 'administrator/user_group_list.html'
    context_object_name = 'user_groups'

    def get_queryset(self):
        return UserGroup.objects.select_related('user', 'group').all()


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupCreateView(CreateView):
    """Create a new user-group membership"""
    model = UserGroup
    form_class = UserGroupForm
    template_name = 'administrator/user_group_form.html'
    success_url = reverse_lazy('administrator:user_group_list')

    def get_initial(self):
        initial = super().get_initial()
        # If user_id is provided in URL parameters, pre-select that user
        user_id = self.kwargs.get('user_id') or self.request.GET.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                initial['user'] = user
            except User.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المستخدم للمجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupUpdateView(UpdateView):
    """Update an existing user-group membership"""
    model = UserGroup
    form_class = UserGroupForm
    template_name = 'administrator/user_group_form.html'
    success_url = reverse_lazy('administrator:user_group_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث عضوية المجموعة بنجاح')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(system_admin_required, name='dispatch')
class UserGroupDeleteView(DeleteView):
    """Delete a user-group membership"""
    model = UserGroup
    template_name = 'administrator/user_group_confirm_delete.html'
    success_url = reverse_lazy('administrator:user_group_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم إزالة المستخدم من المجموعة بنجاح')
        return super().delete(request, *args, **kwargs)


# Permission Dashboard and Management
@login_required
@system_admin_required
def permission_dashboard(request):
    """Dashboard for permissions management"""
    users_count = User.objects.count()
    groups_count = Group.objects.count()
    permissions_count = Permission.objects.count()
    template_permissions_count = TemplatePermission.objects.count()

    context = {
        'users_count': users_count,
        'groups_count': groups_count,
        'permissions_count': permissions_count,
        'template_permissions_count': template_permissions_count,
        'page_title': 'إدارة الصلاحيات'
    }

    return render(request, 'administrator/permission_dashboard.html', context)


@login_required
@system_admin_required
def permissions_help(request):
    """Help page for permissions system"""
    return render(request, 'administrator/permission_help.html', {'page_title': 'دليل نظام الصلاحيات'})


@login_required
@system_admin_required
def user_create(request):
    """Create a new user with quick links to manage permissions and groups"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'تم إنشاء المستخدم {user.username} بنجاح!')

            # Check if we should redirect to add user to group
            if 'save_and_add_to_group' in request.POST:
                return redirect('administrator:user_group_add_with_user', user_id=user.id)
            # Check if we should redirect to edit permissions
            elif 'save_and_edit_permissions' in request.POST:
                return redirect('administrator:edit_user_permissions', user_id=user.id)
            # Default redirect to user list
            return redirect('administrator:user_permission_list')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'page_title': 'إضافة مستخدم جديد',
        'groups': Group.objects.all(),
    }

    return render(request, 'administrator/user_create.html', context)


@login_required
@system_admin_required
def user_detail(request, pk):
    """View details of a user"""
    user = get_object_or_404(User, id=pk)

    # Get user's groups
    user_groups = user.groups.all()

    # Get user's permissions
    user_permissions = user.user_permissions.all()

    # Get user's department permissions
    from .models import UserDepartmentPermission, UserModulePermission
    user_dept_permissions = UserDepartmentPermission.objects.filter(user=user).select_related('department')

    # Get user's module permissions
    user_module_permissions = UserModulePermission.objects.filter(user=user).select_related('module')

    context = {
        'user_obj': user,
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'user_dept_permissions': user_dept_permissions,
        'user_module_permissions': user_module_permissions,
        'page_title': f'تفاصيل المستخدم: {user.username}'
    }

    return render(request, 'administrator/user_detail.html', context)


@login_required
@system_admin_required
def user_permission_list(request):
    """List all user permissions."""
    users = User.objects.filter(is_active=True)
    context = {
        'users': users,
        'title': 'صلاحيات المستخدمين'
    }
    return render(request, 'administrator/user_permission_list.html', context)


@login_required
@system_admin_required
def auto_create_permissions(request):
    """Automatically create permissions for all modules."""
    if request.method == 'POST':
        # Get module_id from the form if specified
        module_id = request.POST.get('module_id')

        if module_id:
            # If a specific module is selected
            modules = Module.objects.filter(id=module_id, is_active=True)
        else:
            # Get all active modules
            modules = Module.objects.filter(is_active=True)

        # استخراج أنواع الصلاحيات من النموذج
        permission_types = [ptype[0] for ptype in Permission.PERMISSION_TYPES]

        # Create permissions for each module and permission type
        created_count = 0

        # طباعة معلومات التصحيح
        print(f"عدد الوحدات: {modules.count()}")
        print(f"أنواع الصلاحيات: {permission_types}")

        for module in modules:
            print(f"إنشاء صلاحيات للوحدة: {module.name}")
            for perm_type in permission_types:
                # Check if permission already exists
                perm, created = Permission.objects.get_or_create(
                    module=module,
                    permission_type=perm_type,
                    defaults={'is_active': True}
                )
                if created:
                    print(f"تم إنشاء صلاحية جديدة: {module.name} - {perm_type}")
                    created_count += 1
                else:
                    print(f"الصلاحية موجودة بالفعل: {module.name} - {perm_type}")

        if created_count > 0:
            messages.success(request, f'تم إنشاء {created_count} صلاحية جديدة بنجاح')
        else:
            messages.info(request, 'لم يتم إنشاء أي صلاحيات جديدة، جميع الصلاحيات موجودة بالفعل')
        return redirect('administrator:permission_list')

    # GET request - show confirmation page
    # Get all modules with their related departments and permissions for display
    modules = Module.objects.filter(is_active=True).select_related('department').prefetch_related('permissions')

    return render(request, 'administrator/auto_create_permissions.html', {
        'title': 'إنشاء صلاحيات تلقائياً',
        'modules': modules
    })


@login_required
@system_admin_required
def edit_user_permissions(request, user_id):
    """Edit permissions for a specific user."""
    user = get_object_or_404(User, id=user_id)

    # Inicializar selected_* variables para evitar errores
    selected_groups = []
    selected_view_permissions = []
    selected_add_permissions = []
    selected_change_permissions = []
    selected_delete_permissions = []
    selected_print_permissions = []
    selected_templates = []

    if request.method == 'POST':
        form = UserPermissionForm(request.POST)
        if form.is_valid():
            try:
                # Iniciar una transacción para asegurar que todos los cambios se apliquen o ninguno
                from django.db import transaction
                with transaction.atomic():
                    # Limpiar el caché de permisos para asegurar que los cambios se reflejen inmediatamente
                    from .utils import clear_permission_cache, clear_user_permission_cache
                    clear_user_permission_cache(user.id)

                    # Update user's groups
                    selected_groups = form.cleaned_data['groups']

                    # Obtener grupos actuales
                    current_groups = user.groups.all()

                    # Eliminar grupos que ya no están seleccionados
                    for group in current_groups:
                        if group not in selected_groups:
                            user.groups.remove(group)

                    # Añadir nuevos grupos seleccionados
                    for group in selected_groups:
                        if group not in current_groups:
                            user.groups.add(group)

                    # Actualizar permisos para cada tipo
                    for perm_type in ['view', 'add', 'change', 'delete', 'print']:
                        # Obtener permisos seleccionados
                        selected_perms = form.cleaned_data[f'{perm_type}_permissions']

                        # Obtener permisos actuales
                        current_perms = Permission.objects.filter(permission_type=perm_type, users=user)

                        # Eliminar permisos que ya no están seleccionados
                        for perm in current_perms:
                            if perm not in selected_perms:
                                perm.users.remove(user)

                        # Añadir nuevos permisos seleccionados
                        for perm in selected_perms:
                            perm.users.add(user)

                    # Actualizar plantillas
                    selected_templates = form.cleaned_data['templates']

                    # Obtener plantillas actuales
                    current_templates = TemplatePermission.objects.filter(users=user)

                    # Eliminar plantillas que ya no están seleccionadas
                    for template in current_templates:
                        if template not in selected_templates:
                            template.users.remove(user)

                    # Añadir nuevas plantillas seleccionadas
                    for template in selected_templates:
                        template.users.add(user)

                # Mensaje de éxito
                messages.success(request, f'تم تحديث صلاحيات المستخدم {user.username} بنجاح')

                # Si es una solicitud AJAX, devolver respuesta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': f'تم تحديث صلاحيات المستخدم {user.username} بنجاح'
                    })

                return redirect('administrator:user_permission_list')

            except Exception as e:
                # Registrar el error para depuración
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al guardar permisos de usuario: {str(e)}")

                # Mensaje de error
                messages.error(request, f'حدث خطأ أثناء حفظ الصلاحيات: {str(e)}')

                # Si es una solicitud AJAX, devolver respuesta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'حدث خطأ أثناء حفظ الصلاحيات',
                        'error_details': str(e)
                    }, status=500)
        else:
            # Si hay errores en el formulario
            error_messages = []
            for field, errors in form.errors.items():
                error_messages.append(f"{field}: {', '.join(errors)}")

            error_message = "حدث خطأ في النموذج: " + " | ".join(error_messages)
            messages.error(request, error_message)

            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'حدث خطأ أثناء حفظ الصلاحيات',
                    'errors': form.errors
                }, status=400)
    else:
        # Initialize form with current permissions
        initial_data = {
            'user': user,
            'groups': user.groups.all(),
            'view_permissions': Permission.objects.filter(permission_type='view', users=user),
            'add_permissions': Permission.objects.filter(permission_type='add', users=user),
            'change_permissions': Permission.objects.filter(permission_type='change', users=user),
            'delete_permissions': Permission.objects.filter(permission_type='delete', users=user),
            'print_permissions': Permission.objects.filter(permission_type='print', users=user),
            'templates': TemplatePermission.objects.filter(users=user),
        }
        form = UserPermissionForm(initial=initial_data)

        # Guardar los IDs seleccionados para la plantilla
        selected_groups = [g.id for g in initial_data['groups']]
        selected_view_permissions = [p.id for p in initial_data['view_permissions']]
        selected_add_permissions = [p.id for p in initial_data['add_permissions']]
        selected_change_permissions = [p.id for p in initial_data['change_permissions']]
        selected_delete_permissions = [p.id for p in initial_data['delete_permissions']]
        selected_print_permissions = [p.id for p in initial_data['print_permissions']]
        selected_templates = [t.id for t in initial_data['templates']]

    # Obtener datos adicionales para la interfaz
    groups_count = Group.objects.count()
    departments_count = Department.objects.count()
    modules_count = Module.objects.count()
    permissions_count = Permission.objects.count()
    templates_count = TemplatePermission.objects.count()

    # Organizar permisos por departamento para una mejor visualización
    departments_with_modules = []
    for dept in Department.objects.all():
        modules_with_permissions = []
        for module in dept.modules.all():
            module_permissions = {
                'module': module,
                'permissions': {
                    'view': Permission.objects.filter(module=module, permission_type='view').first(),
                    'add': Permission.objects.filter(module=module, permission_type='add').first(),
                    'change': Permission.objects.filter(module=module, permission_type='change').first(),
                    'delete': Permission.objects.filter(module=module, permission_type='delete').first(),
                    'print': Permission.objects.filter(module=module, permission_type='print').first(),
                }
            }
            modules_with_permissions.append(module_permissions)

        departments_with_modules.append({
            'department': dept,
            'modules': modules_with_permissions
        })

    context = {
        'form': form,
        'user_obj': user,
        'title': f'تعديل صلاحيات {user.username}',
        'groups_count': groups_count,
        'departments_count': departments_count,
        'modules_count': modules_count,
        'permissions_count': permissions_count,
        'templates_count': templates_count,
        'departments_with_modules': departments_with_modules,
        'selected_groups': selected_groups,
        'selected_view_permissions': selected_view_permissions,
        'selected_add_permissions': selected_add_permissions,
        'selected_change_permissions': selected_change_permissions,
        'selected_delete_permissions': selected_delete_permissions,
        'selected_print_permissions': selected_print_permissions,
        'selected_templates': selected_templates,
    }
    return render(request, 'administrator/edit_user_permissions.html', context)


@login_required
@system_admin_required
def edit_group_permissions(request, group_id):
    """Edit permissions for a specific group."""
    group = get_object_or_404(Group, id=group_id)

    # Obtener estadísticas del grupo para mostrar en la interfaz
    user_count = User.objects.filter(groups=group).count()

    # Inicializar selected_* variables para evitar errores
    selected_departments = []
    selected_modules = []
    selected_view_permissions = []
    selected_add_permissions = []
    selected_change_permissions = []
    selected_delete_permissions = []
    selected_print_permissions = []
    selected_templates = []

    if request.method == 'POST':
        # If group ID is in POST data but not in the right format for the form,
        # ensure it's properly set for validation
        if 'group' in request.POST and request.POST['group'].isdigit():
            # Create a mutable copy of POST data
            post_data = request.POST.copy()
            # Ensure the group ID matches the current group
            if int(post_data['group']) == group.id:
                form = GroupPermissionForm(post_data)
            else:
                # If someone is trying to modify a different group, force the correct group ID
                post_data['group'] = str(group.id)
                form = GroupPermissionForm(post_data)
                messages.warning(request, 'تم تصحيح معرف المجموعة في النموذج')
        else:
            # If group is missing, add it to the form data
            post_data = request.POST.copy()
            post_data['group'] = str(group.id)
            form = GroupPermissionForm(post_data)

        if form.is_valid():
            try:
                # Iniciar una transacción para asegurar que todos los cambios se apliquen o ninguno
                from django.db import transaction
                with transaction.atomic():
                    # Limpiar el caché de permisos para asegurar que los cambios se reflejen inmediatamente
                    from .utils import clear_permission_cache
                    clear_permission_cache()

                    # Update departments and modules
                    departments = form.cleaned_data['departments']
                    modules = form.cleaned_data['modules']

                    # Actualizar departamentos - usar método más eficiente
                    # Primero, eliminar todas las relaciones existentes
                    for dept in Department.objects.filter(groups=group):
                        if dept not in departments:
                            dept.groups.remove(group)

                    # Luego, añadir las nuevas relaciones
                    for dept in departments:
                        dept.groups.add(group)

                    # Actualizar módulos - usar método más eficiente
                    # Primero, eliminar todas las relaciones existentes
                    for module in Module.objects.filter(groups=group):
                        if module not in modules:
                            module.groups.remove(group)

                    # Luego, añadir las nuevas relaciones
                    for module in modules:
                        module.groups.add(group)

                    # Actualizar permisos para cada tipo
                    for perm_type in ['view', 'add', 'change', 'delete', 'print']:
                        # Obtener permisos seleccionados
                        selected_perms = form.cleaned_data[f'{perm_type}_permissions']

                        # Obtener permisos actuales
                        current_perms = Permission.objects.filter(permission_type=perm_type, groups=group)

                        # Eliminar permisos que ya no están seleccionados
                        for perm in current_perms:
                            if perm not in selected_perms:
                                perm.groups.remove(group)

                        # Añadir nuevos permisos seleccionados
                        for perm in selected_perms:
                            perm.groups.add(group)

                    # Actualizar plantillas
                    selected_templates = form.cleaned_data['templates']

                    # Obtener plantillas actuales
                    current_templates = TemplatePermission.objects.filter(groups=group)

                    # Eliminar plantillas que ya no están seleccionadas
                    for template in current_templates:
                        if template not in selected_templates:
                            template.groups.remove(group)

                    # Añadir nuevas plantillas seleccionadas
                    for template in selected_templates:
                        template.groups.add(group)

                # Mensaje de éxito
                messages.success(request, f'تم تحديث صلاحيات المجموعة {group.name} بنجاح')

                # Si es una solicitud AJAX, devolver respuesta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': f'تم تحديث صلاحيات المجموعة {group.name} بنجاح'
                    })

                return redirect('administrator:group_permission_list')

            except Exception as e:
                # Registrar el error para depuración
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al guardar permisos: {str(e)}")

                # Mensaje de error
                messages.error(request, f'حدث خطأ أثناء حفظ الصلاحيات: {str(e)}')

                # Si es una solicitud AJAX, devolver respuesta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'حدث خطأ أثناء حفظ الصلاحيات',
                        'error_details': str(e)
                    }, status=500)
        else:
            # Si hay errores en el formulario
            error_messages = []
            for field, errors in form.errors.items():
                error_messages.append(f"{field}: {', '.join(errors)}")

            error_message = "حدث خطأ في النموذج: " + " | ".join(error_messages)
            messages.error(request, error_message)

            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': error_message,
                    'errors': form.errors
                }, status=400)
    else:
        # Initialize form with current permissions
        initial_data = {
            'group': group,
            'departments': Department.objects.filter(groups=group).distinct(),
            'modules': Module.objects.filter(groups=group).distinct(),
            'view_permissions': Permission.objects.filter(permission_type='view', groups=group),
            'add_permissions': Permission.objects.filter(permission_type='add', groups=group),
            'change_permissions': Permission.objects.filter(permission_type='change', groups=group),
            'delete_permissions': Permission.objects.filter(permission_type='delete', groups=group),
            'print_permissions': Permission.objects.filter(permission_type='print', groups=group),
            'templates': TemplatePermission.objects.filter(groups=group),
        }
        form = GroupPermissionForm(initial=initial_data)

        # Guardar los IDs seleccionados para la plantilla
        selected_departments = [d.id for d in initial_data['departments']]
        selected_modules = [m.id for m in initial_data['modules']]
        selected_view_permissions = [p.id for p in initial_data['view_permissions']]
        selected_add_permissions = [p.id for p in initial_data['add_permissions']]
        selected_change_permissions = [p.id for p in initial_data['change_permissions']]
        selected_delete_permissions = [p.id for p in initial_data['delete_permissions']]
        selected_print_permissions = [p.id for p in initial_data['print_permissions']]
        selected_templates = [t.id for t in initial_data['templates']]

    # Obtener datos adicionales para la interfaz
    departments_count = Department.objects.count()
    modules_count = Module.objects.count()
    permissions_count = Permission.objects.count()
    templates_count = TemplatePermission.objects.count()

    # Organizar permisos por departamento para una mejor visualización
    departments_with_modules = []
    for dept in Department.objects.all():
        modules_with_permissions = []
        for module in dept.modules.all():
            module_permissions = {
                'module': module,
                'permissions': {
                    'view': Permission.objects.filter(module=module, permission_type='view').first(),
                    'add': Permission.objects.filter(module=module, permission_type='add').first(),
                    'change': Permission.objects.filter(module=module, permission_type='change').first(),
                    'delete': Permission.objects.filter(module=module, permission_type='delete').first(),
                    'print': Permission.objects.filter(module=module, permission_type='print').first(),
                }
            }
            modules_with_permissions.append(module_permissions)

        departments_with_modules.append({
            'department': dept,
            'modules': modules_with_permissions
        })

    context = {
        'form': form,
        'group': group,
        'title': f'تعديل صلاحيات {group.name}',
        'user_count': user_count,
        'departments_count': departments_count,
        'modules_count': modules_count,
        'permissions_count': permissions_count,
        'templates_count': templates_count,
        'departments_with_modules': departments_with_modules,
        'selected_departments': selected_departments,
        'selected_modules': selected_modules,
        'selected_view_permissions': selected_view_permissions,
        'selected_add_permissions': selected_add_permissions,
        'selected_change_permissions': selected_change_permissions,
        'selected_delete_permissions': selected_delete_permissions,
        'selected_print_permissions': selected_print_permissions,
        'selected_templates': selected_templates,
    }
    return render(request, 'administrator/edit_group_permissions.html', context)


@login_required
@system_admin_required
def group_permission_list(request):
    """List all groups with their permissions."""
    groups = Group.objects.all()

    # Obtener estadísticas para cada grupo
    groups_with_stats = []
    for group in groups:
        user_count = User.objects.filter(groups=group).count()
        department_count = Department.objects.filter(groups=group).count()
        module_count = Module.objects.filter(groups=group).count()
        permission_count = Permission.objects.filter(groups=group).count()
        template_count = TemplatePermission.objects.filter(groups=group).count()

        groups_with_stats.append({
            'id': group.id,
            'name': group.name,
            'user_count': user_count,
            'department_count': department_count,
            'module_count': module_count,
            'permission_count': permission_count,
            'template_count': template_count,
            'allowed_departments': Department.objects.filter(groups=group),
            'allowed_modules': Module.objects.filter(groups=group),
            'template_permissions': TemplatePermission.objects.filter(groups=group),
            'custom_permissions': Permission.objects.filter(groups=group)
        })

    # Obtener conteos totales para estadísticas
    departments_count = Department.objects.count()
    modules_count = Module.objects.count()
    permissions_count = Permission.objects.count()
    templates_count = TemplatePermission.objects.count()

    context = {
        'groups': groups_with_stats,
        'departments_count': departments_count,
        'modules_count': modules_count,
        'permissions_count': permissions_count,
        'templates_count': templates_count,
        'page_title': 'صلاحيات المجموعات'
    }
    return render(request, 'administrator/group_permission_list.html', context)


@login_required
@system_admin_required
def select_all_permissions(request, group_id=None, user_id=None):
    """
    Seleccionar todos los permisos para un grupo o usuario.
    Esta vista se utiliza para facilitar la asignación de todos los permisos de una vez.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        # Iniciar una transacción para asegurar que todos los cambios se apliquen o ninguno
        from django.db import transaction
        with transaction.atomic():
            # Limpiar el caché de permisos para asegurar que los cambios se reflejen inmediatamente
            from .utils import clear_permission_cache, clear_user_permission_cache, clear_group_permission_cache

            # Determinar si estamos trabajando con un grupo o un usuario
            if group_id:
                group = get_object_or_404(Group, id=group_id)

                # Obtener todos los departamentos
                departments = Department.objects.all()
                for dept in departments:
                    dept.groups.add(group)

                # Obtener todos los módulos
                modules = Module.objects.all()
                for module in modules:
                    module.groups.add(group)

                # Obtener todos los permisos
                permissions = Permission.objects.all()
                for perm in permissions:
                    perm.groups.add(group)

                # Obtener todas las plantillas
                templates = TemplatePermission.objects.all()
                for template in templates:
                    template.groups.add(group)

                # Limpiar caché
                clear_group_permission_cache(group_id)

                return JsonResponse({
                    'status': 'success',
                    'message': f'تم منح جميع الصلاحيات للمجموعة {group.name} بنجاح'
                })

            elif user_id:
                user = get_object_or_404(User, id=user_id)

                # Obtener todos los permisos
                permissions = Permission.objects.all()
                for perm in permissions:
                    perm.users.add(user)

                # Obtener todas las plantillas
                templates = TemplatePermission.objects.all()
                for template in templates:
                    template.users.add(user)

                # Limpiar caché
                clear_user_permission_cache(user_id)

                return JsonResponse({
                    'status': 'success',
                    'message': f'تم منح جميع الصلاحيات للمستخدم {user.username} بنجاح'
                })

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'يجب تحديد مجموعة أو مستخدم'
                }, status=400)

    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al asignar todos los permisos: {str(e)}")

        return JsonResponse({
            'status': 'error',
            'message': f'حدث خطأ أثناء منح الصلاحيات: {str(e)}'
        }, status=500)


@login_required
@system_admin_required
def clear_all_permissions(request, group_id=None, user_id=None):
    """
    Eliminar todos los permisos para un grupo o usuario.
    Esta vista se utiliza para facilitar la eliminación de todos los permisos de una vez.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        # Iniciar una transacción para asegurar que todos los cambios se apliquen o ninguno
        from django.db import transaction
        with transaction.atomic():
            # Limpiar el caché de permisos para asegurar que los cambios se reflejen inmediatamente
            from .utils import clear_permission_cache, clear_user_permission_cache, clear_group_permission_cache

            # Determinar si estamos trabajando con un grupo o un usuario
            if group_id:
                group = get_object_or_404(Group, id=group_id)

                # Eliminar todos los departamentos
                Department.objects.filter(groups=group).update(groups=None)

                # Eliminar todos los módulos
                Module.objects.filter(groups=group).update(groups=None)

                # Eliminar todos los permisos
                Permission.objects.filter(groups=group).update(groups=None)

                # Eliminar todas las plantillas
                TemplatePermission.objects.filter(groups=group).update(groups=None)

                # Limpiar caché
                clear_group_permission_cache(group_id)

                return JsonResponse({
                    'status': 'success',
                    'message': f'تم إزالة جميع الصلاحيات من المجموعة {group.name} بنجاح'
                })

            elif user_id:
                user = get_object_or_404(User, id=user_id)

                # Eliminar todos los permisos
                Permission.objects.filter(users=user).update(users=None)

                # Eliminar todas las plantillas
                TemplatePermission.objects.filter(users=user).update(users=None)

                # Limpiar caché
                clear_user_permission_cache(user_id)

                return JsonResponse({
                    'status': 'success',
                    'message': f'تم إزالة جميع الصلاحيات من المستخدم {user.username} بنجاح'
                })

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'يجب تحديد مجموعة أو مستخدم'
                }, status=400)

    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al eliminar todos los permisos: {str(e)}")

        return JsonResponse({
            'status': 'error',
            'message': f'حدث خطأ أثناء إزالة الصلاحيات: {str(e)}'
        }, status=500)
