from .models import SystemSettings, Department, Module, UserDepartmentPermission, UserModulePermission

def system_settings(request):
    """
    Context processor to make system settings available to all templates.
    """
    settings = SystemSettings.get_settings()
    return {
        'system_settings': settings,
        'current_language': settings.language,
        'current_font': settings.font_family,
        'text_direction': settings.text_direction,
        'is_rtl': settings.text_direction == 'rtl',
    }

def user_permissions(request):
    """
    Context processor to make user permissions available to all templates.
    """
    user = request.user
    is_admin = user.is_authenticated and (user.is_superuser or getattr(user, 'Role', '') == 'admin')

    # Default values for unauthenticated users
    if not user.is_authenticated:
        return {
            'user_departments': [],
            'user_modules': {},
            'user_module_permissions': {},
            'is_admin': False,
        }

    # Get departments available to the user
    user_departments = []
    user_department_ids = []
    user_modules = {}
    user_module_permissions = {}

    # Admin users have access to everything
    if is_admin:
        # Get all active departments
        departments = Department.objects.filter(is_active=True).order_by('order')
        user_departments = departments
        user_department_ids = list(departments.values_list('id', flat=True))

        # Get all active modules
        modules = Module.objects.filter(is_active=True, department__in=departments).order_by('department__order', 'order')

        # Organize modules by department
        for dept in departments:
            dept_modules = modules.filter(department=dept)
            user_modules[dept.url_name] = list(dept_modules.values('id', 'name', 'url', 'icon', 'bg_color'))

            # Set full permissions for all modules
            for module in dept_modules:
                user_module_permissions[module.url] = {
                    'can_view': True,
                    'can_add': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_print': True
                }
    else:
        # Get departments the user has direct permission to
        direct_dept_permissions = UserDepartmentPermission.objects.filter(
            user=user,
            can_view=True,
            department__is_active=True
        ).select_related('department')

        direct_dept_ids = [p.department.id for p in direct_dept_permissions]
        direct_depts = [p.department for p in direct_dept_permissions]

        # Get departments the user has access to via groups
        if user.groups.exists():
            user_groups = user.groups.all()
            group_depts = Department.objects.filter(
                is_active=True,
                groups__in=user_groups
            ).exclude(id__in=direct_dept_ids).distinct()

            # Also add departments that don't have any groups (available to all)
            open_depts = Department.objects.filter(
                is_active=True,
                require_admin=False,
                groups__isnull=True
            ).exclude(id__in=direct_dept_ids).distinct()

            # Combine all department sources
            all_depts = list(direct_depts) + list(group_depts) + list(open_depts)
            user_department_ids = [d.id for d in all_depts]
            user_departments = Department.objects.filter(id__in=user_department_ids).distinct().order_by('order')
        else:
            # Just use direct permissions and open departments
            open_depts = Department.objects.filter(
                is_active=True,
                require_admin=False,
                groups__isnull=True
            ).exclude(id__in=direct_dept_ids).distinct()

            all_depts = list(direct_depts) + list(open_depts)
            user_department_ids = [d.id for d in all_depts]
            user_departments = Department.objects.filter(id__in=user_department_ids).distinct().order_by('order')

        # Get modules the user has direct permission to
        direct_module_permissions = UserModulePermission.objects.filter(
            user=user,
            can_view=True,
            module__is_active=True,
            module__department__in=user_departments
        ).select_related('module', 'module__department')

        # Organize modules by department and set permissions
        for dept in user_departments:
            dept_modules = []

            # Get modules for this department that the user has direct permission to
            for perm in direct_module_permissions.filter(module__department=dept):
                module = perm.module
                dept_modules.append({
                    'id': module.id,
                    'name': module.name,
                    'url': module.url,
                    'icon': module.icon,
                    'bg_color': module.bg_color
                })

                # Set permissions for this module
                user_module_permissions[module.url] = {
                    'can_view': perm.can_view,
                    'can_add': perm.can_add,
                    'can_edit': perm.can_edit,
                    'can_delete': perm.can_delete,
                    'can_print': perm.can_print
                }

            # Get modules for this department that the user has access to via groups
            if user.groups.exists():
                group_modules = Module.objects.filter(
                    is_active=True,
                    department=dept,
                    groups__in=user_groups
                ).exclude(id__in=[m['id'] for m in dept_modules]).distinct()

                for module in group_modules:
                    dept_modules.append({
                        'id': module.id,
                        'name': module.name,
                        'url': module.url,
                        'icon': module.icon,
                        'bg_color': module.bg_color
                    })

                    # Set default permissions for group-based access
                    user_module_permissions[module.url] = {
                        'can_view': True,
                        'can_add': False,
                        'can_edit': False,
                        'can_delete': False,
                        'can_print': False
                    }

            # Get modules that don't have any groups (available to all with department access)
            open_modules = Module.objects.filter(
                is_active=True,
                department=dept,
                groups__isnull=True,
                require_admin=False
            ).exclude(id__in=[m['id'] for m in dept_modules]).distinct()

            for module in open_modules:
                dept_modules.append({
                    'id': module.id,
                    'name': module.name,
                    'url': module.url,
                    'icon': module.icon,
                    'bg_color': module.bg_color
                })

                # Set default permissions for open modules
                user_module_permissions[module.url] = {
                    'can_view': True,
                    'can_add': False,
                    'can_edit': False,
                    'can_delete': False,
                    'can_print': False
                }

            # Store modules for this department
            user_modules[dept.url_name] = dept_modules

    # Convert QuerySet to list of URL names for easier template use
    user_department_urls = [dept.url_name for dept in user_departments]

    return {
        'user_departments': user_departments,
        'user_department_urls': user_department_urls,
        'user_modules': user_modules,
        'user_module_permissions': user_module_permissions,
        'is_admin': is_admin,
    }
