# RBAC Permission System Documentation

## Overview

The Role-Based Access Control (RBAC) system provides a flexible and powerful way to manage permissions in the application. It allows administrators to:

1. Create roles (groups) with specific permissions
2. Assign users to roles
3. Check permissions at various levels (views, templates, etc.)

## Key Components

### Models

1. **AppModule**: Represents an application module in the system (e.g., HR, Meetings, Inventory)
2. **OperationPermission**: Represents a permission for a specific operation (CRUD) in an application module
3. **PagePermission**: Represents a permission to access a specific page/template
4. **UserOperationPermission**: Assigns operation permissions to users
5. **UserPagePermission**: Assigns page permissions to users

### Permission Functions

1. **has_permission(user, permission_name)**: Checks if a user has a specific permission
2. **get_user_roles(user)**: Gets all roles (groups) for a user
3. **get_role_permissions(role)**: Gets all permissions for a role
4. **get_all_user_permissions(user)**: Gets all permissions for a user across all their roles
5. **clear_user_permissions_cache(user)**: Clears the permissions cache for a user
6. **clear_role_permissions_cache(role)**: Clears the permissions cache for all users in a role

### Decorators

1. **require_permission(permission_name)**: Decorator to check RBAC permissions for views
2. **operation_permission_required(app_module_code, operation_code, permission_type)**: Decorator to check if a user has permission to perform a specific operation
3. **page_permission_required(app_module_code, url_pattern)**: Decorator to check if a user has permission to access a specific page

### Template Tags

1. **has_rbac_permission**: Filter to check if a user has a specific RBAC permission
2. **check_rbac_permission**: Tag to check if a user has a specific RBAC permission
3. **has_op_perm**: Tag to check if a user has permission to perform a specific operation
4. **has_pg_perm**: Tag to check if a user has permission to access a specific page
5. **show_if_has_op_perm**: Filter to show content if a user has permission to perform a specific operation
6. **show_if_has_pg_perm**: Filter to show content if a user has permission to access a specific page

## Usage Examples

### In Views

```python
from administrator.rbac_permissions import has_permission
from administrator.rbac_views import require_permission

# Using the decorator
@require_permission('edit_articles')
def edit_article(request, article_id):
    # Edit article
    article = get_object_or_404(Article, id=article_id)
    # ...
    return render(request, 'articles/edit.html', {'article': article})

# Checking permissions inside a view
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    can_edit = has_permission(request.user, 'edit_articles')
    can_delete = has_permission(request.user, 'delete_articles')
    
    context = {
        'article': article,
        'can_edit': can_edit,
        'can_delete': can_delete,
    }
    
    return render(request, 'articles/detail.html', context)
```

### In Templates

```html
{% load permissions %}

<!-- Using the filter -->
{% if user|has_rbac_permission:"edit_articles" %}
    <a href="{% url 'edit_article' article.id %}" class="btn btn-primary">
        <i class="fas fa-edit"></i> تعديل المقال
    </a>
{% endif %}

<!-- Using the tag -->
{% check_rbac_permission user "delete_articles" as can_delete %}
{% if can_delete %}
    <a href="{% url 'delete_article' article.id %}" class="btn btn-danger">
        <i class="fas fa-trash"></i> حذف المقال
    </a>
{% endif %}

<!-- Operation permissions -->
{% has_op_perm 'hr' 'employee' 'view' as can_view_employee %}
{% if can_view_employee %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}

<!-- Page permissions -->
{% has_pg_perm 'hr' 'employee_list' as can_view_employee_list %}
{% if can_view_employee_list %}
    <a href="{% url 'hr:employee_list' %}" class="btn btn-primary">عرض الموظفين</a>
{% endif %}
```

## Best Practices

1. **Use RBAC for new features**: For new features, use the RBAC permission system instead of the older permission systems.
2. **Cache permissions**: The RBAC system already includes caching to improve performance. Make sure to clear the cache when permissions change.
3. **Clear cache when permissions change**: Use `clear_user_permissions_cache` and `clear_role_permissions_cache` when permissions change.
4. **Use descriptive permission names**: Use descriptive names for permissions to make them easier to understand.
5. **Group related permissions**: Group related permissions together to make them easier to manage.
6. **Document permissions**: Document the permissions used in your application to make them easier to understand and maintain.

## Migration from Older Permission Systems

If you're using the older permission systems (Department/Module permissions or Template permissions), consider migrating to the RBAC system for better flexibility and maintainability.

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
