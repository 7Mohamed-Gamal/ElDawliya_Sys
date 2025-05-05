from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db import transaction

from .models_new import (
    AppModule, OperationPermission, PagePermission,
    UserOperationPermission, UserPagePermission
)

User = get_user_model()

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.Role == 'admin'

# Decorator for admin-only views
admin_required = user_passes_test(is_admin)

@login_required
@admin_required
def permissions_dashboard(request):
    """Dashboard for the permissions system"""
    users_count = User.objects.count()
    app_modules_count = AppModule.objects.count()
    operation_permissions_count = OperationPermission.objects.count()
    page_permissions_count = PagePermission.objects.count()
    
    context = {
        'users_count': users_count,
        'app_modules_count': app_modules_count,
        'operation_permissions_count': operation_permissions_count,
        'page_permissions_count': page_permissions_count,
        'title': 'لوحة تحكم الصلاحيات'
    }
    
    return render(request, 'administrator/new/permissions_dashboard.html', context)


# App Module Views
@login_required
@admin_required
def app_module_list(request):
    """
    List all app modules
    """
    search_query = request.GET.get('search', '')
    
    if search_query:
        app_modules = AppModule.objects.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('order', 'name')
    else:
        app_modules = AppModule.objects.all().order_by('order', 'name')
    
    context = {
        'title': 'قائمة التطبيقات',
        'app_modules': app_modules,
        'search_query': search_query,
    }
    return render(request, 'administrator/new/app_module_list.html', context)


@login_required
@admin_required
def app_module_create(request):
    """
    Create a new app module
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not code:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('administrator:app_module_create')
        
        if AppModule.objects.filter(code=code).exists():
            messages.error(request, f'كود التطبيق "{code}" موجود بالفعل')
            return redirect('administrator:app_module_create')
        
        app_module = AppModule.objects.create(
            name=name,
            code=code,
            description=description,
            icon=icon,
            order=order,
            is_active=is_active
        )
        
        messages.success(request, f'تم إنشاء التطبيق "{name}" بنجاح')
        return redirect('administrator:app_module_list')
    
    context = {
        'title': 'إضافة تطبيق جديد',
    }
    return render(request, 'administrator/new/app_module_form.html', context)


@login_required
@admin_required
def app_module_edit(request, pk):
    """
    Edit an existing app module
    """
    app_module = get_object_or_404(AppModule, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not code:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('administrator:app_module_edit', pk=pk)
        
        # Check if code exists for other modules
        if AppModule.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, f'كود التطبيق "{code}" موجود بالفعل')
            return redirect('administrator:app_module_edit', pk=pk)
        
        app_module.name = name
        app_module.code = code
        app_module.description = description
        app_module.icon = icon
        app_module.order = order
        app_module.is_active = is_active
        app_module.save()
        
        messages.success(request, f'تم تحديث التطبيق "{name}" بنجاح')
        return redirect('administrator:app_module_list')
    
    context = {
        'title': f'تعديل التطبيق: {app_module.name}',
        'app_module': app_module,
    }
    return render(request, 'administrator/new/app_module_form.html', context)


@login_required
@admin_required
def app_module_delete(request, pk):
    """
    Delete an app module
    """
    app_module = get_object_or_404(AppModule, pk=pk)
    
    if request.method == 'POST':
        name = app_module.name
        app_module.delete()
        messages.success(request, f'تم حذف التطبيق "{name}" بنجاح')
        return redirect('administrator:app_module_list')
    
    context = {
        'title': f'حذف التطبيق: {app_module.name}',
        'app_module': app_module,
    }
    return render(request, 'administrator/new/app_module_confirm_delete.html', context)


# Operation Permission Views
@login_required
@admin_required
def operation_permission_list(request):
    """
    List all operation permissions
    """
    search_query = request.GET.get('search', '')
    selected_app_module = request.GET.get('app_module', '')
    
    operation_permissions = OperationPermission.objects.all()
    
    if search_query:
        operation_permissions = operation_permissions.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if selected_app_module:
        operation_permissions = operation_permissions.filter(app_module_id=selected_app_module)
    
    operation_permissions = operation_permissions.order_by('app_module__name', 'name', 'permission_type')
    
    context = {
        'title': 'قائمة صلاحيات العمليات',
        'operation_permissions': operation_permissions,
        'app_modules': AppModule.objects.all().order_by('name'),
        'search_query': search_query,
        'selected_app_module': selected_app_module,
    }
    return render(request, 'administrator/new/operation_permission_list.html', context)


@login_required
@admin_required
def operation_permission_create(request):
    """
    Create a new operation permission
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        permission_type = request.POST.get('permission_type')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not permission_type or not code:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('administrator:operation_permission_create')
        
        # Check if permission already exists
        if OperationPermission.objects.filter(
            app_module_id=app_module_id,
            code=code,
            permission_type=permission_type
        ).exists():
            messages.error(request, f'صلاحية العملية بالكود "{code}" ونوع الصلاحية "{permission_type}" موجودة بالفعل لهذا التطبيق')
            return redirect('administrator:operation_permission_create')
        
        operation_permission = OperationPermission.objects.create(
            name=name,
            app_module_id=app_module_id,
            permission_type=permission_type,
            code=code,
            description=description,
            is_active=is_active
        )
        
        messages.success(request, f'تم إنشاء صلاحية العملية "{name}" بنجاح')
        return redirect('administrator:operation_permission_list')
    
    context = {
        'title': 'إضافة صلاحية عملية جديدة',
        'app_modules': AppModule.objects.all().order_by('name'),
        'permission_types': OperationPermission.PERMISSION_TYPES,
    }
    return render(request, 'administrator/new/operation_permission_form.html', context)


@login_required
@admin_required
def operation_permission_edit(request, pk):
    """
    Edit an existing operation permission
    """
    operation_permission = get_object_or_404(OperationPermission, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        permission_type = request.POST.get('permission_type')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not permission_type or not code:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('administrator:operation_permission_edit', pk=pk)
        
        # Check if permission already exists for other permissions
        if OperationPermission.objects.filter(
            app_module_id=app_module_id,
            code=code,
            permission_type=permission_type
        ).exclude(pk=pk).exists():
            messages.error(request, f'صلاحية العملية بالكود "{code}" ونوع الصلاحية "{permission_type}" موجودة بالفعل لهذا التطبيق')
            return redirect('administrator:operation_permission_edit', pk=pk)
        
        operation_permission.name = name
        operation_permission.app_module_id = app_module_id
        operation_permission.permission_type = permission_type
        operation_permission.code = code
        operation_permission.description = description
        operation_permission.is_active = is_active
        operation_permission.save()
        
        messages.success(request, f'تم تحديث صلاحية العملية "{name}" بنجاح')
        return redirect('administrator:operation_permission_list')
    
    context = {
        'title': f'تعديل صلاحية العملية: {operation_permission.name}',
        'operation_permission': operation_permission,
        'app_modules': AppModule.objects.all().order_by('name'),
        'permission_types': OperationPermission.PERMISSION_TYPES,
    }
    return render(request, 'administrator/new/operation_permission_form.html', context)


@login_required
@admin_required
def operation_permission_delete(request, pk):
    """
    Delete an operation permission
    """
    operation_permission = get_object_or_404(OperationPermission, pk=pk)
    
    if request.method == 'POST':
        name = operation_permission.name
        operation_permission.delete()
        messages.success(request, f'تم حذف صلاحية العملية "{name}" بنجاح')
        return redirect('administrator:operation_permission_list')
    
    context = {
        'title': f'حذف صلاحية العملية: {operation_permission.name}',
        'operation_permission': operation_permission,
    }
    return render(request, 'administrator/new/operation_permission_confirm_delete.html', context)


# Page Permission Views
@login_required
@admin_required
def page_permission_list(request):
    """
    List all page permissions
    """
    search_query = request.GET.get('search', '')
    selected_app_module = request.GET.get('app_module', '')
    
    page_permissions = PagePermission.objects.all()
    
    if search_query:
        page_permissions = page_permissions.filter(
            Q(name__icontains=search_query) | 
            Q(url_pattern__icontains=search_query) |
            Q(template_path__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if selected_app_module:
        page_permissions = page_permissions.filter(app_module_id=selected_app_module)
    
    page_permissions = page_permissions.order_by('app_module__name', 'name')
    
    context = {
        'title': 'قائمة صلاحيات الصفحات',
        'page_permissions': page_permissions,
        'app_modules': AppModule.objects.all().order_by('name'),
        'search_query': search_query,
        'selected_app_module': selected_app_module,
    }
    return render(request, 'administrator/new/page_permission_list.html', context)


@login_required
@admin_required
def page_permission_create(request):
    """
    Create a new page permission
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        url_pattern = request.POST.get('url_pattern')
        template_path = request.POST.get('template_path', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not url_pattern:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('administrator:page_permission_create')
        
        # Check if permission already exists
        if PagePermission.objects.filter(
            app_module_id=app_module_id,
            url_pattern=url_pattern
        ).exists():
            messages.error(request, f'صلاحية الصفحة بنمط URL "{url_pattern}" موجودة بالفعل لهذا التطبيق')
            return redirect('administrator:page_permission_create')
        
        page_permission = PagePermission.objects.create(
            name=name,
            app_module_id=app_module_id,
            url_pattern=url_pattern,
            template_path=template_path,
            description=description,
            is_active=is_active
        )
        
        messages.success(request, f'تم إنشاء صلاحية الصفحة "{name}" بنجاح')
        return redirect('administrator:page_permission_list')
    
    context = {
        'title': 'إضافة صلاحية صفحة جديدة',
        'app_modules': AppModule.objects.all().order_by('name'),
    }
    return render(request, 'administrator/new/page_permission_form.html', context)


@login_required
@admin_required
def page_permission_edit(request, pk):
    """
    Edit an existing page permission
    """
    page_permission = get_object_or_404(PagePermission, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        url_pattern = request.POST.get('url_pattern')
        template_path = request.POST.get('template_path', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not url_pattern:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('administrator:page_permission_edit', pk=pk)
        
        # Check if permission already exists for other permissions
        if PagePermission.objects.filter(
            app_module_id=app_module_id,
            url_pattern=url_pattern
        ).exclude(pk=pk).exists():
            messages.error(request, f'صلاحية الصفحة بنمط URL "{url_pattern}" موجودة بالفعل لهذا التطبيق')
            return redirect('administrator:page_permission_edit', pk=pk)
        
        page_permission.name = name
        page_permission.app_module_id = app_module_id
        page_permission.url_pattern = url_pattern
        page_permission.template_path = template_path
        page_permission.description = description
        page_permission.is_active = is_active
        page_permission.save()
        
        messages.success(request, f'تم تحديث صلاحية الصفحة "{name}" بنجاح')
        return redirect('administrator:page_permission_list')
    
    context = {
        'title': f'تعديل صلاحية الصفحة: {page_permission.name}',
        'page_permission': page_permission,
        'app_modules': AppModule.objects.all().order_by('name'),
    }
    return render(request, 'administrator/new/page_permission_form.html', context)


@login_required
@admin_required
def page_permission_delete(request, pk):
    """
    Delete a page permission
    """
    page_permission = get_object_or_404(PagePermission, pk=pk)
    
    if request.method == 'POST':
        name = page_permission.name
        page_permission.delete()
        messages.success(request, f'تم حذف صلاحية الصفحة "{name}" بنجاح')
        return redirect('administrator:page_permission_list')
    
    context = {
        'title': f'حذف صلاحية الصفحة: {page_permission.name}',
        'page_permission': page_permission,
    }
    return render(request, 'administrator/new/page_permission_confirm_delete.html', context)


# User Permission Views
@login_required
@admin_required
def user_permission_list(request):
    """
    List all users for permission management
    """
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = User.objects.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        ).order_by('username')
    else:
        users = User.objects.all().order_by('username')
    
    context = {
        'title': 'قائمة صلاحيات المستخدمين',
        'users': users,
        'search_query': search_query,
    }
    return render(request, 'administrator/new/user_permission_list.html', context)


@login_required
@admin_required
def user_permission_detail(request, user_id):
    """
    View user permissions
    """
    user_obj = get_object_or_404(User, pk=user_id)
    
    # Get user operation permissions grouped by app module
    user_operation_permissions = UserOperationPermission.objects.filter(user=user_obj).select_related('operation', 'operation__app_module')
    operation_permissions_by_module = {}
    
    for permission in user_operation_permissions:
        module_name = permission.operation.app_module.name
        if module_name not in operation_permissions_by_module:
            operation_permissions_by_module[module_name] = []
        operation_permissions_by_module[module_name].append(permission)
    
    # Get user page permissions grouped by app module
    user_page_permissions = UserPagePermission.objects.filter(user=user_obj).select_related('page', 'page__app_module')
    page_permissions_by_module = {}
    
    for permission in user_page_permissions:
        module_name = permission.page.app_module.name
        if module_name not in page_permissions_by_module:
            page_permissions_by_module[module_name] = []
        page_permissions_by_module[module_name].append(permission)
    
    context = {
        'title': f'تفاصيل صلاحيات المستخدم: {user_obj.username}',
        'user_obj': user_obj,
        'operation_permissions_by_module': operation_permissions_by_module,
        'page_permissions_by_module': page_permissions_by_module,
    }
    return render(request, 'administrator/new/user_permission_detail.html', context)


@login_required
@admin_required
def manage_user_permissions(request, user_id):
    """
    Manage user permissions
    """
    user_obj = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        # Get selected permissions
        operation_permissions = request.POST.getlist('operation_permissions')
        page_permissions = request.POST.getlist('page_permissions')
        
        # Clear existing permissions
        UserOperationPermission.objects.filter(user=user_obj).delete()
        UserPagePermission.objects.filter(user=user_obj).delete()
        
        # Add new operation permissions
        for op_id in operation_permissions:
            UserOperationPermission.objects.create(
                user=user_obj,
                operation_id=op_id
            )
        
        # Add new page permissions
        for page_id in page_permissions:
            UserPagePermission.objects.create(
                user=user_obj,
                page_id=page_id
            )
        
        messages.success(request, f'تم تحديث صلاحيات المستخدم "{user_obj.username}" بنجاح')
        return redirect('administrator:user_permission_detail', user_id=user_id)
    
    # Get all app modules
    app_modules = AppModule.objects.filter(is_active=True).order_by('order', 'name')
    
    # Get all operation permissions grouped by app module
    operation_permissions_by_module = {}
    for app_module in app_modules:
        operation_permissions = OperationPermission.objects.filter(
            app_module=app_module,
            is_active=True
        ).order_by('name', 'permission_type')
        
        if operation_permissions.exists():
            operation_permissions_by_module[app_module.id] = operation_permissions
    
    # Get all page permissions grouped by app module
    page_permissions_by_module = {}
    for app_module in app_modules:
        page_permissions = PagePermission.objects.filter(
            app_module=app_module,
            is_active=True
        ).order_by('name')
        
        if page_permissions.exists():
            page_permissions_by_module[app_module.id] = page_permissions
    
    # Get user's current permissions
    user_operation_permissions = UserOperationPermission.objects.filter(user=user_obj).values_list('operation_id', flat=True)
    user_page_permissions = UserPagePermission.objects.filter(user=user_obj).values_list('page_id', flat=True)
    
    context = {
        'title': f'إدارة صلاحيات المستخدم: {user_obj.username}',
        'user_obj': user_obj,
        'app_modules': app_modules,
        'operation_permissions_by_module': operation_permissions_by_module,
        'page_permissions_by_module': page_permissions_by_module,
        'user_operation_permissions': user_operation_permissions,
        'user_page_permissions': user_page_permissions,
    }
    return render(request, 'administrator/new/manage_user_permissions.html', context)

@login_required
@admin_required
def app_module_list(request):
    """List all application modules"""
    app_modules = AppModule.objects.all().order_by('order', 'name')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        app_modules = app_modules.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'app_modules': app_modules,
        'search_query': search_query,
        'title': 'قائمة التطبيقات'
    }
    
    return render(request, 'administrator/new/app_module_list.html', context)

@login_required
@admin_required
def app_module_create(request):
    """Create a new application module"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not code:
            messages.error(request, 'يجب تحديد اسم وكود التطبيق')
            return redirect('administrator:app_module_create')
        
        try:
            app_module = AppModule.objects.create(
                name=name,
                code=code,
                description=description,
                icon=icon,
                order=order,
                is_active=is_active
            )
            messages.success(request, f'تم إنشاء التطبيق {app_module.name} بنجاح')
            return redirect('administrator:app_module_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء التطبيق: {str(e)}')
    
    context = {
        'title': 'إنشاء تطبيق جديد'
    }
    
    return render(request, 'administrator/new/app_module_form.html', context)

@login_required
@admin_required
def app_module_edit(request, pk):
    """Edit an existing application module"""
    app_module = get_object_or_404(AppModule, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not code:
            messages.error(request, 'يجب تحديد اسم وكود التطبيق')
            return redirect('administrator:app_module_edit', pk=pk)
        
        try:
            app_module.name = name
            app_module.code = code
            app_module.description = description
            app_module.icon = icon
            app_module.order = order
            app_module.is_active = is_active
            app_module.save()
            
            messages.success(request, f'تم تحديث التطبيق {app_module.name} بنجاح')
            return redirect('administrator:app_module_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث التطبيق: {str(e)}')
    
    context = {
        'app_module': app_module,
        'title': f'تعديل التطبيق: {app_module.name}'
    }
    
    return render(request, 'administrator/new/app_module_form.html', context)

@login_required
@admin_required
def app_module_delete(request, pk):
    """Delete an application module"""
    app_module = get_object_or_404(AppModule, pk=pk)
    
    if request.method == 'POST':
        try:
            name = app_module.name
            app_module.delete()
            messages.success(request, f'تم حذف التطبيق {name} بنجاح')
            return redirect('administrator:app_module_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف التطبيق: {str(e)}')
            return redirect('administrator:app_module_list')
    
    context = {
        'app_module': app_module,
        'title': f'حذف التطبيق: {app_module.name}'
    }
    
    return render(request, 'administrator/new/app_module_confirm_delete.html', context)

@login_required
@admin_required
def operation_permission_list(request):
    """List all operation permissions"""
    operation_permissions = OperationPermission.objects.all().select_related('app_module')
    
    # Handle filtering by app module
    app_module_id = request.GET.get('app_module')
    if app_module_id:
        operation_permissions = operation_permissions.filter(app_module_id=app_module_id)
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        operation_permissions = operation_permissions.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get all app modules for filter dropdown
    app_modules = AppModule.objects.all().order_by('name')
    
    context = {
        'operation_permissions': operation_permissions,
        'app_modules': app_modules,
        'selected_app_module': app_module_id,
        'search_query': search_query,
        'title': 'قائمة صلاحيات العمليات'
    }
    
    return render(request, 'administrator/new/operation_permission_list.html', context)

@login_required
@admin_required
def operation_permission_create(request):
    """Create a new operation permission"""
    app_modules = AppModule.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        permission_type = request.POST.get('permission_type')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not permission_type or not code:
            messages.error(request, 'يجب تحديد جميع الحقول المطلوبة')
            return redirect('administrator:operation_permission_create')
        
        try:
            app_module = AppModule.objects.get(id=app_module_id)
            operation_permission = OperationPermission.objects.create(
                name=name,
                app_module=app_module,
                permission_type=permission_type,
                code=code,
                description=description,
                is_active=is_active
            )
            messages.success(request, f'تم إنشاء صلاحية العملية {operation_permission.name} بنجاح')
            return redirect('administrator:operation_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء صلاحية العملية: {str(e)}')
    
    context = {
        'app_modules': app_modules,
        'permission_types': OperationPermission.PERMISSION_TYPES,
        'title': 'إنشاء صلاحية عملية جديدة'
    }
    
    return render(request, 'administrator/new/operation_permission_form.html', context)

@login_required
@admin_required
def operation_permission_edit(request, pk):
    """Edit an existing operation permission"""
    operation_permission = get_object_or_404(OperationPermission, pk=pk)
    app_modules = AppModule.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        permission_type = request.POST.get('permission_type')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not permission_type or not code:
            messages.error(request, 'يجب تحديد جميع الحقول المطلوبة')
            return redirect('administrator:operation_permission_edit', pk=pk)
        
        try:
            app_module = AppModule.objects.get(id=app_module_id)
            operation_permission.name = name
            operation_permission.app_module = app_module
            operation_permission.permission_type = permission_type
            operation_permission.code = code
            operation_permission.description = description
            operation_permission.is_active = is_active
            operation_permission.save()
            
            messages.success(request, f'تم تحديث صلاحية العملية {operation_permission.name} بنجاح')
            return redirect('administrator:operation_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث صلاحية العملية: {str(e)}')
    
    context = {
        'operation_permission': operation_permission,
        'app_modules': app_modules,
        'permission_types': OperationPermission.PERMISSION_TYPES,
        'title': f'تعديل صلاحية العملية: {operation_permission.name}'
    }
    
    return render(request, 'administrator/new/operation_permission_form.html', context)

@login_required
@admin_required
def operation_permission_delete(request, pk):
    """Delete an operation permission"""
    operation_permission = get_object_or_404(OperationPermission, pk=pk)
    
    if request.method == 'POST':
        try:
            name = operation_permission.name
            operation_permission.delete()
            messages.success(request, f'تم حذف صلاحية العملية {name} بنجاح')
            return redirect('administrator:operation_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف صلاحية العملية: {str(e)}')
            return redirect('administrator:operation_permission_list')
    
    context = {
        'operation_permission': operation_permission,
        'title': f'حذف صلاحية العملية: {operation_permission.name}'
    }
    
    return render(request, 'administrator/new/operation_permission_confirm_delete.html', context)

@login_required
@admin_required
def page_permission_list(request):
    """List all page permissions"""
    page_permissions = PagePermission.objects.all().select_related('app_module')
    
    # Handle filtering by app module
    app_module_id = request.GET.get('app_module')
    if app_module_id:
        page_permissions = page_permissions.filter(app_module_id=app_module_id)
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        page_permissions = page_permissions.filter(
            Q(name__icontains=search_query) | 
            Q(url_pattern__icontains=search_query) |
            Q(template_path__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get all app modules for filter dropdown
    app_modules = AppModule.objects.all().order_by('name')
    
    context = {
        'page_permissions': page_permissions,
        'app_modules': app_modules,
        'selected_app_module': app_module_id,
        'search_query': search_query,
        'title': 'قائمة صلاحيات الصفحات'
    }
    
    return render(request, 'administrator/new/page_permission_list.html', context)

@login_required
@admin_required
def page_permission_create(request):
    """Create a new page permission"""
    app_modules = AppModule.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        url_pattern = request.POST.get('url_pattern')
        template_path = request.POST.get('template_path', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not url_pattern:
            messages.error(request, 'يجب تحديد جميع الحقول المطلوبة')
            return redirect('administrator:page_permission_create')
        
        try:
            app_module = AppModule.objects.get(id=app_module_id)
            page_permission = PagePermission.objects.create(
                name=name,
                app_module=app_module,
                url_pattern=url_pattern,
                template_path=template_path,
                description=description,
                is_active=is_active
            )
            messages.success(request, f'تم إنشاء صلاحية الصفحة {page_permission.name} بنجاح')
            return redirect('administrator:page_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء صلاحية الصفحة: {str(e)}')
    
    context = {
        'app_modules': app_modules,
        'title': 'إنشاء صلاحية صفحة جديدة'
    }
    
    return render(request, 'administrator/new/page_permission_form.html', context)

@login_required
@admin_required
def page_permission_edit(request, pk):
    """Edit an existing page permission"""
    page_permission = get_object_or_404(PagePermission, pk=pk)
    app_modules = AppModule.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        app_module_id = request.POST.get('app_module')
        url_pattern = request.POST.get('url_pattern')
        template_path = request.POST.get('template_path', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not app_module_id or not url_pattern:
            messages.error(request, 'يجب تحديد جميع الحقول المطلوبة')
            return redirect('administrator:page_permission_edit', pk=pk)
        
        try:
            app_module = AppModule.objects.get(id=app_module_id)
            page_permission.name = name
            page_permission.app_module = app_module
            page_permission.url_pattern = url_pattern
            page_permission.template_path = template_path
            page_permission.description = description
            page_permission.is_active = is_active
            page_permission.save()
            
            messages.success(request, f'تم تحديث صلاحية الصفحة {page_permission.name} بنجاح')
            return redirect('administrator:page_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث صلاحية الصفحة: {str(e)}')
    
    context = {
        'page_permission': page_permission,
        'app_modules': app_modules,
        'title': f'تعديل صلاحية الصفحة: {page_permission.name}'
    }
    
    return render(request, 'administrator/new/page_permission_form.html', context)

@login_required
@admin_required
def page_permission_delete(request, pk):
    """Delete a page permission"""
    page_permission = get_object_or_404(PagePermission, pk=pk)
    
    if request.method == 'POST':
        try:
            name = page_permission.name
            page_permission.delete()
            messages.success(request, f'تم حذف صلاحية الصفحة {name} بنجاح')
            return redirect('administrator:page_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف صلاحية الصفحة: {str(e)}')
            return redirect('administrator:page_permission_list')
    
    context = {
        'page_permission': page_permission,
        'title': f'حذف صلاحية الصفحة: {page_permission.name}'
    }
    
    return render(request, 'administrator/new/page_permission_confirm_delete.html', context)

@login_required
@admin_required
def user_permission_list(request):
    """List all users with their permissions"""
    users = User.objects.filter(is_active=True).order_by('username')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
        'title': 'قائمة صلاحيات المستخدمين'
    }
    
    return render(request, 'administrator/new/user_permission_list.html', context)

@login_required
@admin_required
def manage_user_permissions(request, user_id):
    """Manage permissions for a specific user"""
    user = get_object_or_404(User, pk=user_id)
    app_modules = AppModule.objects.filter(is_active=True).order_by('order', 'name')
    
    # Get all operation permissions grouped by app module
    operation_permissions_by_module = {}
    for app_module in app_modules:
        operation_permissions_by_module[app_module.id] = OperationPermission.objects.filter(
            app_module=app_module,
            is_active=True
        ).order_by('name', 'permission_type')
    
    # Get all page permissions grouped by app module
    page_permissions_by_module = {}
    for app_module in app_modules:
        page_permissions_by_module[app_module.id] = PagePermission.objects.filter(
            app_module=app_module,
            is_active=True
        ).order_by('name')
    
    # Get user's current operation permissions
    user_operation_permissions = set(
        UserOperationPermission.objects.filter(user=user).values_list('operation_id', flat=True)
    )
    
    # Get user's current page permissions
    user_page_permissions = set(
        UserPagePermission.objects.filter(user=user).values_list('page_id', flat=True)
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Process operation permissions
                # First, delete all existing operation permissions for this user
                UserOperationPermission.objects.filter(user=user).delete()
                
                # Then, add the selected operation permissions
                selected_operation_permissions = request.POST.getlist('operation_permissions')
                for operation_id in selected_operation_permissions:
                    try:
                        operation = OperationPermission.objects.get(id=operation_id)
                        UserOperationPermission.objects.create(user=user, operation=operation)
                    except OperationPermission.DoesNotExist:
                        pass
                
                # Process page permissions
                # First, delete all existing page permissions for this user
                UserPagePermission.objects.filter(user=user).delete()
                
                # Then, add the selected page permissions
                selected_page_permissions = request.POST.getlist('page_permissions')
                for page_id in selected_page_permissions:
                    try:
                        page = PagePermission.objects.get(id=page_id)
                        UserPagePermission.objects.create(user=user, page=page)
                    except PagePermission.DoesNotExist:
                        pass
                
                messages.success(request, f'تم تحديث صلاحيات المستخدم {user.username} بنجاح')
                return redirect('administrator:user_permission_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث الصلاحيات: {str(e)}')
    
    context = {
        'user_obj': user,
        'app_modules': app_modules,
        'operation_permissions_by_module': operation_permissions_by_module,
        'page_permissions_by_module': page_permissions_by_module,
        'user_operation_permissions': user_operation_permissions,
        'user_page_permissions': user_page_permissions,
        'title': f'إدارة صلاحيات المستخدم: {user.username}'
    }
    
    return render(request, 'administrator/new/manage_user_permissions.html', context)

@login_required
@admin_required
def user_permission_detail(request, user_id):
    """View details of a user's permissions"""
    user = get_object_or_404(User, pk=user_id)
    
    # Get user's operation permissions
    user_operation_permissions = UserOperationPermission.objects.filter(user=user).select_related(
        'operation', 'operation__app_module'
    ).order_by('operation__app_module__name', 'operation__name')
    
    # Get user's page permissions
    user_page_permissions = UserPagePermission.objects.filter(user=user).select_related(
        'page', 'page__app_module'
    ).order_by('page__app_module__name', 'page__name')
    
    # Group operation permissions by app module
    operation_permissions_by_module = {}
    for perm in user_operation_permissions:
        module_name = perm.operation.app_module.name
        if module_name not in operation_permissions_by_module:
            operation_permissions_by_module[module_name] = []
        operation_permissions_by_module[module_name].append(perm)
    
    # Group page permissions by app module
    page_permissions_by_module = {}
    for perm in user_page_permissions:
        module_name = perm.page.app_module.name
        if module_name not in page_permissions_by_module:
            page_permissions_by_module[module_name] = []
        page_permissions_by_module[module_name].append(perm)
    
    context = {
        'user_obj': user,
        'operation_permissions_by_module': operation_permissions_by_module,
        'page_permissions_by_module': page_permissions_by_module,
        'title': f'تفاصيل صلاحيات المستخدم: {user.username}'
    }
    
    return render(request, 'administrator/new/user_permission_detail.html', context)