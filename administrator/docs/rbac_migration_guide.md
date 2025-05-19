# Migration Guide: Moving to RBAC Permission System

## Overview

This guide provides step-by-step instructions for migrating from the older permission systems (Department/Module permissions or Template permissions) to the RBAC (Role-Based Access Control) system.

## Why Migrate?

The RBAC system offers several advantages:

- **More granular control**: Define permissions at a more detailed level
- **Better performance**: Optimized caching and permission checks
- **Easier management**: Centralized permission management
- **Better scalability**: Designed to handle complex permission scenarios
- **Consistent API**: Unified approach to permission checks

## Migration Steps

### 1. Identify Current Permission Usage

First, identify where and how permissions are currently being used in your code:

```bash
# Search for permission-related code in views
grep -r "module_permission_required" --include="*.py" .
grep -r "has_module_permission" --include="*.py" .
grep -r "has_template_permission" --include="*.py" .

# Search for permission-related code in templates
grep -r "has_module_permission" --include="*.html" .
grep -r "has_template_permission" --include="*.html" .
```

### 2. Map Old Permissions to RBAC Permissions

Create a mapping between old permissions and new RBAC permissions:

| Old Permission | New RBAC Permission |
|----------------|---------------------|
| Department: HR, Module: Employees, Type: view | hr_view_employees |
| Department: HR, Module: Employees, Type: add | hr_add_employees |
| Template: Hr/reports/monthly_salary_report.html | hr_view_monthly_salary_report |

### 3. Create RBAC Permissions

Use the management command to create default permissions:

```bash
python manage.py create_default_permissions
```

For custom permissions, use the RBAC API:

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Get the ContentType for Group (as a generic model to associate with)
content_type = ContentType.objects.get_for_model(Group)

# Create a custom permission
permission, created = Permission.objects.get_or_create(
    codename='hr_view_employees',
    content_type=content_type,
    defaults={'name': 'Can view employees'}
)

# Add metadata (category) to the permission
setattr(permission, 'category', 'hr')
```

### 4. Assign Permissions to Roles

Assign the new RBAC permissions to roles (groups):

```python
from django.contrib.auth.models import Group, Permission

# Get the role (group)
role = Group.objects.get(name='HR Managers')

# Get the permissions
view_employees = Permission.objects.get(codename='hr_view_employees')
add_employees = Permission.objects.get(codename='hr_add_employees')

# Assign permissions to the role
role.permissions.add(view_employees, add_employees)
```

### 5. Update View Decorators

Replace old permission decorators with RBAC decorators:

#### Old Code:
```python
from administrator.decorators import module_permission_required

@module_permission_required(department_name="الموارد البشرية", module_name="إدارة الموظفين", permission_type="view")
def employee_list(request):
    # View code
```

#### New Code:
```python
from administrator.rbac_views import require_permission

@require_permission('hr_view_employees')
def employee_list(request):
    # View code
```

### 6. Update Template Tags

Replace old template tags with RBAC template tags:

#### Old Code:
```html
{% load permissions %}

{% has_module_permission "الموارد البشرية" "إدارة الموظفين" "view" as can_view_employees %}
{% if can_view_employees %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}
```

#### New Code:
```html
{% load permissions %}

{% if user|has_rbac_permission:"hr_view_employees" %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}
```

Or using the tag syntax:

```html
{% load permissions %}

{% check_rbac_permission user "hr_view_employees" as can_view_employees %}
{% if can_view_employees %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}
```

### 7. Update Inline Permission Checks

Replace inline permission checks with RBAC permission checks:

#### Old Code:
```python
from administrator.utils import check_permission

def dashboard(request):
    can_view_employees = check_permission(
        user=request.user,
        department_name="الموارد البشرية",
        module_name="إدارة الموظفين",
        permission_type="view"
    )
    
    context = {
        'can_view_employees': can_view_employees,
    }
    
    return render(request, 'dashboard.html', context)
```

#### New Code:
```python
from administrator.rbac_permissions import has_permission

def dashboard(request):
    can_view_employees = has_permission(request.user, 'hr_view_employees')
    
    context = {
        'can_view_employees': can_view_employees,
    }
    
    return render(request, 'dashboard.html', context)
```

### 8. Test Thoroughly

Test all permission-related functionality to ensure that the migration was successful:

- Test view access
- Test template rendering
- Test permission-based UI elements
- Test permission changes

### 9. Clean Up Legacy Code

Once you've confirmed that everything is working correctly, you can gradually remove the legacy permission code.

## Compatibility Layer

During the transition period, you can use the compatibility layer to make the migration smoother:

```python
# In your views.py
from administrator.rbac_permissions import has_permission

def legacy_check_permission(user, department_name, module_name, permission_type):
    """
    Compatibility function to map old permission checks to RBAC
    """
    # Map old permission parameters to RBAC permission name
    permission_map = {
        ("الموارد البشرية", "إدارة الموظفين", "view"): "hr_view_employees",
        ("الموارد البشرية", "إدارة الموظفين", "add"): "hr_add_employees",
        # Add more mappings as needed
    }
    
    # Get the RBAC permission name
    permission_name = permission_map.get((department_name, module_name, permission_type))
    
    if permission_name:
        # Use RBAC permission check
        return has_permission(user, permission_name)
    else:
        # Fallback to admin check for unmapped permissions
        return user.is_superuser or user.Role == 'admin'
```

## Need Help?

If you encounter any issues during the migration process, please contact the system administrator or refer to the [RBAC Permission System Documentation](rbac_permissions.md) for more details.
