from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, Resolver404
from django.conf import settings
from .models import Department, Module, UserDepartmentPermission, UserModulePermission

class SimplifiedPermissionMiddleware:
    """
    Middleware to handle simplified permissions based on Django Groups.

    This middleware checks if a user has access to a specific URL based on their group membership.
    It works by checking the URL prefix against the departments that the user has access to.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Get the current path
        path = request.path_info.lstrip('/')

        # Exclude some paths from permission check
        if path.startswith(('admin/', 'accounts/login/', 'accounts/logout/', 'static/', 'media/')):
            return self.get_response(request)

        # Always allow superusers and admin users
        if request.user.is_superuser or request.user.Role == 'admin':
            return self.get_response(request)

        # Check if trying to access system admin section
        if path.startswith('administrator/'):
            messages.error(request, 'لا تملك صلاحية الوصول إلى هذا القسم')
            return redirect('accounts:home')

        # Check department-based permissions
        # For example, if path starts with 'Hr/', check if user has access to HR department
        try:
            # Get the first part of the path (e.g., 'Hr' from 'Hr/employees/')
            app_name = path.split('/')[0].lower()

            # Skip permission check for the home page
            if not app_name:
                return self.get_response(request)

            # Check if user has access to this department
            has_access = False

            # Admin users always have access
            if request.user.Role == 'admin' or request.user.is_superuser:
                has_access = True
            else:
                # Find department by URL name (case insensitive)
                try:
                    department = Department.objects.get(url_name__iexact=app_name)

                    # Check if department requires admin
                    if department.require_admin and request.user.Role != 'admin':
                        has_access = False
                    # Check if user has direct permission to the department
                    elif UserDepartmentPermission.objects.filter(user=request.user, department=department, can_view=True).exists():
                        has_access = True
                    # Check if user is in any of the allowed groups
                    elif department.groups.exists():
                        # Check if any of the user's groups are in the department's allowed groups
                        user_groups = request.user.groups.all()
                        has_access = department.groups.filter(id__in=user_groups).exists()
                    # If no groups specified, everyone can access
                    else:
                        has_access = True

                except Department.DoesNotExist:
                    # If department doesn't exist, allow access (might be a different app)
                    has_access = True

            if not has_access:
                messages.error(request, f'ليس لديك صلاحية الوصول إلى قسم {app_name}')
                return redirect('accounts:home')

            # If user has access to the department, check if they have access to the specific module
            # This is only relevant for URLs that match a module's URL pattern
            if has_access and len(path.split('/')) > 1:
                try:
                    # Get the full URL to check against module URLs
                    full_url = '/' + path

                    # Find modules that match this URL
                    modules = Module.objects.filter(department=department, is_active=True)

                    # Check if any module matches this URL
                    for module in modules:
                        if module.url == full_url or full_url.startswith(module.url + '/'):
                            # Check if user has permission to view this module
                            module_access = False

                            # Admin users always have access
                            if request.user.Role == 'admin' or request.user.is_superuser:
                                module_access = True
                            # Check if module requires admin
                            elif module.require_admin and request.user.Role != 'admin':
                                module_access = False
                            # Check if user has direct permission to the module
                            elif UserModulePermission.objects.filter(user=request.user, module=module, can_view=True).exists():
                                module_access = True
                            # Check if user is in any of the allowed groups
                            elif module.groups.exists():
                                user_groups = request.user.groups.all()
                                module_access = module.groups.filter(id__in=user_groups).exists()
                            # If no groups specified, everyone with department access can access
                            else:
                                module_access = True

                            if not module_access:
                                messages.error(request, f'ليس لديك صلاحية الوصول إلى هذه الصفحة')
                                return redirect('accounts:home')

                            # If we found a matching module and user has access, no need to check other modules
                            break
                except Exception as e:
                    # If there's an error checking module permissions, log it but allow access
                    print(f"Error checking module permissions: {e}")
                    pass

        except (IndexError, Resolver404):
            # If there's an error resolving the URL, allow access
            pass

        return self.get_response(request)
