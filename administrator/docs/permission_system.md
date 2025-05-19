# Permission System Documentation

## Overview

The application includes multiple permission systems that have evolved over time:

1. **Original Django Permission System**: Using Django's built-in permission system with models, groups, and permissions.
2. **Custom Department/Module Permission System**: A custom implementation that checks permissions based on departments and modules.
3. **RBAC (Role-Based Access Control)**: A newer implementation that provides more granular control over permissions.
4. **Template-based Permission System**: Allows controlling access to specific templates.
5. **Operation and Page Permission System**: A newer system that controls access to specific operations and pages.

For new development, we recommend using the **RBAC system** as it provides the most flexibility and is actively maintained.

## Permission Systems

### 1. Django Permission System

This is Django's built-in permission system, which is based on the `auth.Permission` model and the `Group` model.

#### Usage

```python
# Check if a user has a permission
if user.has_perm('app_label.permission_codename'):
    # Do something
```

### 2. Department/Module Permission System

This system is based on the `Department`, `Module`, and `Permission` models. It allows controlling access to specific departments and modules.

#### Models

- `Department`: Represents a department in the system
- `Module`: Represents a module within a department
- `Permission`: Represents a permission for a module
- `UserDepartmentPermission`: Assigns department permissions to users
- `UserModulePermission`: Assigns module permissions to users

#### Usage in Views

```python
from administrator.decorators import module_permission_required

@module_permission_required(department_name="الموارد البشرية", module_name="إدارة الموظفين", permission_type="view")
def employee_list(request):
    # View code
```

#### Usage in Templates

```html
{% load permissions %}

{% has_module_permission "الموارد البشرية" "إدارة الموظفين" "view" as can_view_employees %}
{% if can_view_employees %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}
```

### 3. RBAC System

The RBAC system is a more flexible and powerful permission system that allows for more granular control over permissions. See [RBAC Permission System Documentation](rbac_permissions.md) for more details.

#### Usage in Views

```python
from administrator.rbac_views import require_permission

@require_permission('edit_articles')
def edit_article(request, article_id):
    # View code
```

#### Usage in Templates

```html
{% load permissions %}

{% if user|has_rbac_permission:"edit_articles" %}
    <a href="{% url 'edit_article' article.id %}" class="btn btn-primary">تعديل المقال</a>
{% endif %}
```

### 4. Template-based Permission System

This system allows controlling access to specific templates.

#### Models

- `TemplatePermission`: Represents a permission for a template

#### Usage in Templates

```html
{% load permissions %}

{% if user|has_template_permission:"Hr/reports/monthly_salary_report.html" %}
    <a href="{% url 'hr:monthly_salary_report' %}" class="btn btn-primary">عرض تقرير الرواتب الشهري</a>
{% endif %}
```

### 5. Operation and Page Permission System

This system allows controlling access to specific operations and pages.

#### Models

- `AppModule`: Represents an application module
- `OperationPermission`: Represents a permission for an operation
- `PagePermission`: Represents a permission for a page
- `UserOperationPermission`: Assigns operation permissions to users
- `UserPagePermission`: Assigns page permissions to users

#### Usage in Views

```python
from administrator.permission_decorators import operation_permission_required, page_permission_required

@operation_permission_required('hr', 'employee', 'view')
def employee_list(request):
    # View code

@page_permission_required('hr', 'employee_list')
def employee_list(request):
    # View code
```

#### Usage in Templates

```html
{% load permissions %}

{% has_op_perm 'hr' 'employee' 'view' as can_view_employee %}
{% if can_view_employee %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}

{% has_pg_perm 'hr' 'employee_list' as can_view_employee_list %}
{% if can_view_employee_list %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}
```

## Middleware

The application includes middleware for checking permissions:

### SimplifiedPermissionMiddleware

This middleware checks if a user has access to a specific URL based on their group membership. It works by checking the URL prefix against the departments that the user has access to.

## Best Practices

1. **Use RBAC for new features**: For new features, use the RBAC permission system instead of the older permission systems.
2. **Be consistent**: Choose one permission system and stick with it for a given feature.
3. **Document permissions**: Document the permissions used in your application to make them easier to understand and maintain.
4. **Test permissions**: Test permissions thoroughly to ensure that they work as expected.
5. **Use decorators**: Use decorators to check permissions in views to keep your code DRY.
6. **Use template tags**: Use template tags to check permissions in templates to keep your templates DRY.

## Migration to RBAC

If you're using the older permission systems, consider migrating to the RBAC system for better flexibility and maintainability.

### Migration Steps

1. Identify the permissions used in your application
2. Create equivalent permissions in the RBAC system
3. Assign the permissions to roles
4. Update your code to use the RBAC permission functions and decorators
5. Test thoroughly to ensure that permissions work as expected

## Troubleshooting

### Permission Caching

If permissions are not being applied correctly, try clearing the cache:

```python
from administrator.rbac_permissions import clear_user_permissions_cache, clear_role_permissions_cache

# Clear cache for a user
clear_user_permissions_cache(user)

# Clear cache for a role
clear_role_permissions_cache(role)
```

### Permission Debugging

To debug permission issues, you can print the permissions for a user:

```python
from administrator.rbac_permissions import get_all_user_permissions

# Get all permissions for a user
permissions = get_all_user_permissions(user)
print(f"Permissions for {user.username}: {permissions}")
```
