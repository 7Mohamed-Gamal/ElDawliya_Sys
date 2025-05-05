from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.core.paginator import Paginator

User = get_user_model()

from .rbac_permissions import (
    PERMISSION_CATEGORIES,
    get_user_roles,
    get_role_permissions,
    get_all_user_permissions,
    has_permission, 
    clear_user_permissions_cache,
    clear_role_permissions_cache,
    create_default_permissions,
    assign_default_admin_permissions,
    assign_category_permissions
)

def require_permission(permission_name):
    """
    Custom decorator to check RBAC permissions.
    
    Args:
        permission_name: Permission codename to check
        
    Returns:
        Decorator function that checks if the user has the required permission.
        If not, redirects to the permission denied page.
    """
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, permission_name):
                messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
                return redirect('home')  # Redirect to homepage or access denied page
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

@login_required
@require_permission('view_roles')
def permissions_dashboard(request):
    """Dashboard view for the RBAC permissions system."""
    # Get counts for dashboard stats
    roles = Group.objects.annotate(user_count=Count('user'))
    permissions = Permission.objects.all()
    users = User.objects.filter(is_active=True)
    
    # Organize permissions by category for display
    permissions_by_category = {}
    for p in permissions:
        # Try to get the category attribute, default to 'other'
        category = getattr(p, 'category', 'other')
        
        if category not in permissions_by_category:
            permissions_by_category[category] = []
            
        permissions_by_category[category].append(p)
    
    context = {
        'title': 'نظام إدارة الصلاحيات',
        'roles': roles,
        'permissions': permissions,
        'users': users,
        'categories': PERMISSION_CATEGORIES,
    }
    
    return render(request, 'administrator/rbac/dashboard.html', context)

# ===== Role Management Views =====

@login_required
@require_permission('view_roles')
def role_list(request):
    """List all roles (groups) in the system."""
    roles = Group.objects.annotate(user_count=Count('user'))
    
    # Paginate the roles list
    paginator = Paginator(roles, 10)  # 10 roles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'قائمة الأدوار',
        'roles': page_obj,
    }
    
    return render(request, 'administrator/rbac/role_list.html', context)

@login_required
@require_permission('add_role')
def role_create(request):
    """Create a new role (group)."""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, "يرجى إدخال اسم للدور.")
            return redirect('administrator:rbac_role_create')
        
        # Check if a role with this name already exists
        if Group.objects.filter(name=name).exists():
            messages.error(request, f"الدور '{name}' موجود بالفعل.")
            return redirect('administrator:rbac_role_create')
        
        # Create the role
        role = Group.objects.create(name=name)
        messages.success(request, f"تم إنشاء الدور '{name}' بنجاح.")
        
        # Redirect to the role permissions page to assign permissions
        return redirect('administrator:rbac_role_permissions', role_id=role.id)
    
    context = {
        'title': 'إنشاء دور جديد',
    }
    
    return render(request, 'administrator/rbac/role_form.html', context)

@login_required
@require_permission('edit_role')
def role_edit(request, role_id):
    """Edit an existing role (group)."""
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, "يرجى إدخال اسم للدور.")
            return redirect('administrator:rbac_role_edit', role_id=role.id)
        
        # Check if a role with this name already exists (excluding this role)
        if Group.objects.exclude(id=role.id).filter(name=name).exists():
            messages.error(request, f"الدور '{name}' موجود بالفعل.")
            return redirect('administrator:rbac_role_edit', role_id=role.id)
        
        # Update the role name
        role.name = name
        role.save()
        messages.success(request, f"تم تحديث الدور '{name}' بنجاح.")
        
        return redirect('administrator:rbac_role_detail', role_id=role.id)
    
    context = {
        'title': f'تعديل الدور: {role.name}',
        'role': role,
    }
    
    return render(request, 'administrator/rbac/role_form.html', context)

@login_required
@require_permission('view_roles')
def role_detail(request, role_id):
    """View details of a role including its permissions and users."""
    role = get_object_or_404(Group, id=role_id)
    permissions = role.permissions.all()
    users = role.user_set.all()
    
    # Organize permissions by category for display
    permissions_by_category = {}
    for p in permissions:
        # Try to get the category attribute, default to 'other'
        category = getattr(p, 'category', 'other')
        
        if category not in permissions_by_category:
            permissions_by_category[category] = []
            
        permissions_by_category[category].append(p)
    
    context = {
        'title': f'تفاصيل الدور: {role.name}',
        'role': role,
        'permissions': permissions,
        'permissions_by_category': permissions_by_category,
        'users': users,
    }
    
    return render(request, 'administrator/rbac/role_detail.html', context)

@login_required
@require_permission('delete_role')
def role_delete(request, role_id):
    """Delete a role (group)."""
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        messages.success(request, f"تم حذف الدور '{role_name}' بنجاح.")
        return redirect('administrator:rbac_role_list')
    
    context = {
        'title': f'حذف الدور: {role.name}',
        'role': role,
    }
    
    return render(request, 'administrator/rbac/role_confirm_delete.html', context)

@login_required
@require_permission('edit_role')
def role_permissions(request, role_id):
    """Manage permissions for a role (group)."""
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        # Get selected permission IDs from the form
        permission_ids = request.POST.getlist('permissions')
        
        # Clear existing permissions and add the selected ones
        role.permissions.clear()
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.add(*permissions)
        
        # Clear cache for this role
        clear_role_permissions_cache(role)
        
        messages.success(request, f"تم تحديث صلاحيات الدور '{role.name}' بنجاح.")
        return redirect('administrator:rbac_role_detail', role_id=role.id)
    
    # Get all permissions and organize by category
    all_permissions = Permission.objects.all()
    all_permissions_by_category = {}
    
    for p in all_permissions:
        # Try to get the category attribute, default to 'other'
        category = getattr(p, 'category', 'other')
        category_name = PERMISSION_CATEGORIES.get(category, 'أخرى')
        
        if category_name not in all_permissions_by_category:
            all_permissions_by_category[category_name] = []
            
        all_permissions_by_category[category_name].append(p)
    
    # Get IDs of currently selected permissions
    selected_permissions = role.permissions.values_list('id', flat=True)
    
    context = {
        'title': f'إدارة صلاحيات الدور: {role.name}',
        'role': role,
        'all_permissions_by_category': all_permissions_by_category,
        'selected_permissions': selected_permissions,
    }
    
    return render(request, 'administrator/rbac/role_permissions.html', context)

@login_required
@require_permission('edit_role')
def bulk_assign_permissions(request, role_id):
    """Bulk assign permissions to a role by category."""
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        # Get selected categories from the form
        categories = request.POST.getlist('categories')
        
        if not categories:
            messages.warning(request, "لم يتم تحديد أي فئات. لم يتم إجراء أي تغييرات.")
            return redirect('administrator:rbac_bulk_assign_permissions', role_id=role.id)
        
        # Get current permissions for the role
        current_permissions = set(role.permissions.values_list('id', flat=True))
        new_permissions = set()
        
        # Add permissions from each selected category
        for category in categories:
            # This assumes you've added a 'category' attribute to Permission objects
            permissions = [
                p for p in Permission.objects.all() 
                if hasattr(p, 'category') and p.category == category
            ]
            
            if permissions:
                new_permission_ids = set(p.id for p in permissions)
                new_permissions.update(new_permission_ids)
        
        # Combine current permissions with new ones
        combined_permissions = current_permissions.union(new_permissions)
        
        # Update the role's permissions
        role.permissions.set(Permission.objects.filter(id__in=combined_permissions))
        
        # Clear cache for this role
        clear_role_permissions_cache(role)
        
        messages.success(request, f"تم تحديث صلاحيات الدور '{role.name}' بنجاح.")
        return redirect('administrator:rbac_role_permissions', role_id=role.id)
    
    context = {
        'title': f'إضافة صلاحيات بالفئة للدور: {role.name}',
        'role': role,
        'categories': PERMISSION_CATEGORIES,
    }
    
    return render(request, 'administrator/rbac/bulk_assign_permissions.html', context)

# ===== User Management Views =====

@login_required
@require_permission('view_users')
def user_list(request):
    """List all users in the system."""
    users = User.objects.filter(is_active=True)
    
    # Get the action from query parameters
    action = request.GET.get('action', '')
    
    # Paginate the users list
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Set title based on action
    if action == 'assign_roles':
        title = 'تعيين الأدوار للمستخدمين'
    else:
        title = 'قائمة المستخدمين'
    
    context = {
        'title': title,
        'users': page_obj,
        'action': action,  # Pass the action to the template
    }
    
    return render(request, 'administrator/rbac/user_list.html', context)

@login_required
@require_permission('view_users')
def user_detail(request, user_id):
    """View details of a user including their roles and permissions."""
    user_obj = get_object_or_404(User, id=user_id)
    roles = get_user_roles(user_obj)
    permissions = get_all_user_permissions(user_obj)
    
    context = {
        'title': f'تفاصيل المستخدم: {user_obj.username}',
        'user_obj': user_obj,
        'roles': roles,
        'permissions': permissions,
    }
    
    return render(request, 'administrator/rbac/user_detail.html', context)

@login_required
@require_permission('assign_roles')
def user_roles(request, user_id):
    """Manage roles for a user."""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Get selected role IDs from the form
        role_ids = request.POST.getlist('roles')
        
        # Clear existing roles and add the selected ones
        user_obj.groups.clear()
        
        if role_ids:
            roles = Group.objects.filter(id__in=role_ids)
            user_obj.groups.add(*roles)
        
        # Clear cache for this user
        clear_user_permissions_cache(user_obj)
        
        messages.success(request, f"تم تحديث أدوار المستخدم '{user_obj.username}' بنجاح.")
        return redirect('administrator:rbac_user_detail', user_id=user_obj.id)
    
    # Get all roles
    all_roles = Group.objects.all()
    
    # Get IDs of currently selected roles
    selected_roles = user_obj.groups.values_list('id', flat=True)
    
    context = {
        'title': f'إدارة أدوار المستخدم: {user_obj.username}',
        'user_obj': user_obj,
        'all_roles': all_roles,
        'selected_roles': selected_roles,
    }
    
    return render(request, 'administrator/rbac/user_roles.html', context)

# ===== Permission Management Views =====

@login_required
@require_permission('view_roles')
def permission_list(request):
    """List all permissions in the system."""
    permissions = Permission.objects.all()
    
    # Organize permissions by category for display
    permissions_by_category = {}
    for p in permissions:
        # Try to get the category attribute, default to 'other'
        category = getattr(p, 'category', 'other')
        category_name = PERMISSION_CATEGORIES.get(category, 'أخرى')
        
        if category_name not in permissions_by_category:
            permissions_by_category[category_name] = []
            
        permissions_by_category[category_name].append(p)
    
    context = {
        'title': 'قائمة الصلاحيات',
        'permissions_by_category': permissions_by_category,
    }
    
    return render(request, 'administrator/rbac/permission_list.html', context)

@login_required
@require_permission('manage_permissions')
def permission_create(request):
    """Create a new permission."""
    from django.contrib.contenttypes.models import ContentType
    
    if request.method == 'POST':
        name = request.POST.get('name')
        codename = request.POST.get('codename')
        category = request.POST.get('category')
        
        if not name or not codename or not category:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة.")
            return redirect('administrator:rbac_permission_create')
        
        # Check if a permission with this codename already exists
        if Permission.objects.filter(codename=codename).exists():
            messages.error(request, f"الصلاحية '{codename}' موجودة بالفعل.")
            return redirect('administrator:rbac_permission_create')
        
        # Get the content type for Group (as a generic model)
        content_type = ContentType.objects.get_for_model(Group)
        
        # Create the permission
        permission = Permission.objects.create(
            name=name,
            codename=codename,
            content_type=content_type
        )
        
        # Add the category attribute to the permission
        setattr(permission, 'category', category)
        
        messages.success(request, f"تم إنشاء الصلاحية '{name}' بنجاح.")
        return redirect('administrator:rbac_permission_list')
    
    context = {
        'title': 'إنشاء صلاحية جديدة',
        'categories': PERMISSION_CATEGORIES,
    }
    
    return render(request, 'administrator/rbac/permission_form.html', context)

@login_required
@require_permission('manage_permissions')
def permission_edit(request, permission_id):
    """Edit an existing permission."""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        
        if not name or not category:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة.")
            return redirect('administrator:rbac_permission_edit', permission_id=permission.id)
        
        # Update the permission
        permission.name = name
        setattr(permission, 'category', category)
        permission.save()
        
        messages.success(request, f"تم تحديث الصلاحية '{name}' بنجاح.")
        return redirect('administrator:rbac_permission_list')
    
    context = {
        'title': f'تعديل الصلاحية: {permission.name}',
        'permission': permission,
        'categories': PERMISSION_CATEGORIES,
    }
    
    return render(request, 'administrator/rbac/permission_form.html', context)

@login_required
@require_permission('manage_permissions')
def permission_delete(request, permission_id):
    """Delete a permission."""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        permission_name = permission.name
        permission.delete()
        messages.success(request, f"تم حذف الصلاحية '{permission_name}' بنجاح.")
        return redirect('administrator:rbac_permission_list')
    
    context = {
        'title': f'حذف الصلاحية: {permission.name}',
        'permission': permission,
    }
    
    return render(request, 'administrator/rbac/permission_confirm_delete.html', context)

@login_required
@require_permission('manage_permissions')
def create_default_permissions_view(request):
    """Create default permissions for the system."""
    if request.method == 'POST':
        # Create default permissions
        permissions = create_default_permissions()
        
        # Count total permissions created
        total_count = sum(len(perms) for perms in permissions.values())
        
        messages.success(request, f"تم إنشاء {total_count} صلاحية بنجاح.")
        return redirect('administrator:rbac_permission_list')
    
    context = {
        'title': 'إنشاء الصلاحيات الافتراضية',
        'categories': PERMISSION_CATEGORIES,
    }
    
    return render(request, 'administrator/rbac/create_default_permissions.html', context)

@login_required
@require_permission('view_roles')
def audit_log(request):
    """View the audit log for RBAC system changes."""
    # في المستقبل، يمكن إضافة نموذج لتتبع التغييرات في نظام الصلاحيات
    # حاليًا سنعرض صفحة بسيطة توضح أن هذه الميزة قيد التطوير
    
    context = {
        'title': 'سجل التغييرات',
        'message': 'هذه الميزة قيد التطوير. سيتم إضافة سجل تفصيلي للتغييرات في نظام الصلاحيات قريبًا.',
    }
    
    return render(request, 'administrator/rbac/audit_log.html', context)
