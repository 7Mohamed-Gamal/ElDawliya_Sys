# =============================================================================
# ElDawliya HR Management System - Salary Component Views
# =============================================================================
# Views for salary component management
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from Hr.models.legacy.legacy_models import SalaryItem as SalaryComponent
from Hr.models.legacy_employee import LegacyEmployee as Employee
from Hr.forms.new_payroll_forms import SalaryComponentForm


# =============================================================================
# SALARY COMPONENT VIEWS
# =============================================================================

@login_required
def component_list(request):
    """عرض قائمة مكونات الراتب"""
    components = SalaryComponent.objects.all().order_by('name')
    
    # البحث والتصفية
    search_query = request.GET.get('search', '')
    component_type_filter = request.GET.get('component_type', '')
    
    if search_query:
        components = components.filter(
            Q(name__icontains=search_query) |
            Q(item_code__icontains=search_query)
        )
    
    if component_type_filter:
        components = components.filter(type=component_type_filter)
    
    # الترقيم
    paginator = Paginator(components, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'components': page_obj,
        'search_query': search_query,
        'component_type_filter': component_type_filter,
        'title': _('مكونات الراتب'),
    }
    
    return render(request, 'Hr/payroll/salary_component_list.html', context)


@login_required
def component_detail(request, component_id):
    """عرض تفاصيل مكون الراتب"""
    component = get_object_or_404(SalaryComponent, item_code=component_id)
    
    # إحصائيات الاستخدام
    from Hr.models.legacy.legacy_models import EmployeeSalaryItem
    usage_stats = {
        'total_employees': EmployeeSalaryItem.objects.filter(salary_item=component).count(),
        'active_employees': EmployeeSalaryItem.objects.filter(
            salary_item=component, is_active=True
        ).count(),
    }
    
    context = {
        'component': component,
        'usage_stats': usage_stats,
        'title': f"تفاصيل مكون الراتب - {component.name}",
    }
    
    return render(request, 'Hr/payroll/salary_component_detail.html', context)


@login_required
def component_create(request):
    """إنشاء مكون راتب جديد"""
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            component = form.save()
            
            messages.success(request, _('تم إنشاء مكون الراتب بنجاح'))
            return redirect('Hr:salary_components:detail', component_id=component.item_code)
    else:
        form = SalaryComponentForm()
    
    context = {
        'form': form,
        'title': _('إضافة مكون راتب جديد'),
        'action': 'create',
    }
    
    return render(request, 'Hr/payroll/salary_component_form.html', context)


@login_required
def component_edit(request, component_id):
    """تحديث مكون الراتب"""
    component = get_object_or_404(SalaryComponent, item_code=component_id)
    
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث مكون الراتب بنجاح'))
            return redirect('Hr:salary_components:detail', component_id=component.item_code)
    else:
        form = SalaryComponentForm(instance=component)
    
    context = {
        'form': form,
        'component': component,
        'title': f"تحديث مكون الراتب - {component.name}",
        'action': 'edit',
    }
    
    return render(request, 'Hr/payroll/salary_component_form.html', context)


@login_required
def component_delete(request, component_id):
    """حذف مكون الراتب"""
    component = get_object_or_404(SalaryComponent, item_code=component_id)
    
    if request.method == 'POST':
        # التحقق من عدم وجود استخدام للمكون
        from Hr.models.legacy.legacy_models import EmployeeSalaryItem
        if EmployeeSalaryItem.objects.filter(salary_item=component).exists():
            messages.error(
                request, 
                _('لا يمكن حذف مكون الراتب لأنه مستخدم من قبل موظفين')
            )
            return redirect('Hr:salary_components:detail', component_id=component.item_code)
        
        component_name = component.name
        component.delete()
        messages.success(request, f'تم حذف مكون الراتب "{component_name}" بنجاح')
        return redirect('Hr:salary_components:list')
    
    context = {
        'component': component,
        'title': f"حذف مكون الراتب - {component.name}",
    }
    
    return render(request, 'Hr/payroll/salary_component_delete.html', context)


@login_required
def component_toggle_status(request, component_id):
    """تبديل حالة مكون الراتب (نشط/غير نشط)"""
    if request.method == 'POST':
        component = get_object_or_404(SalaryComponent, item_code=component_id)
        component.is_active = not component.is_active
        component.save()
        
        status_text = 'نشط' if component.is_active else 'غير نشط'
        messages.success(
            request, 
            f'تم تغيير حالة مكون الراتب "{component.name}" إلى {status_text}'
        )
        
        return JsonResponse({
            'success': True,
            'is_active': component.is_active,
            'message': f'تم تغيير الحالة إلى {status_text}'
        })
    
    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def component_duplicate(request, component_id):
    """نسخ مكون الراتب"""
    original_component = get_object_or_404(SalaryComponent, item_code=component_id)
    
    if request.method == 'POST':
        # إنشاء كود جديد للنسخة
        new_code = f"{original_component.item_code}_COPY"
        counter = 1
        while SalaryComponent.objects.filter(item_code=new_code).exists():
            new_code = f"{original_component.item_code}_COPY_{counter}"
            counter += 1
        
        # إنشاء نسخة جديدة
        new_component = SalaryComponent.objects.create(
            item_code=new_code,
            name=f"{original_component.name} - نسخة",
            type=original_component.type,
            default_value=original_component.default_value,
            is_auto_applied=original_component.is_auto_applied,
            is_active=original_component.is_active
        )
        
        messages.success(request, f'تم نسخ مكون الراتب بنجاح')
        return redirect('Hr:salary_components:edit', component_id=new_component.item_code)
    
    context = {
        'component': original_component,
        'title': f"نسخ مكون الراتب - {original_component.name}",
    }
    
    return render(request, 'Hr/payroll/salary_component_duplicate.html', context)


@login_required
def component_search_ajax(request):
    """البحث السريع عن مكونات الراتب - AJAX"""
    query = request.GET.get('q', '')
    component_type = request.GET.get('component_type', '')
    
    components = SalaryComponent.objects.filter(is_active=True)
    
    if query:
        components = components.filter(
            Q(name__icontains=query) |
            Q(item_code__icontains=query)
        )
    
    if component_type:
        components = components.filter(type=component_type)
    
    components = components[:10]  # الحد الأقصى 10 نتائج
    
    results = []
    for component in components:
        results.append({
            'id': str(component.item_code),
            'name': component.name,
            'code': component.item_code,
            'type': component.type,
            'default_value': float(component.default_value) if component.default_value else 0,
            'is_auto_applied': component.is_auto_applied,
        })
    
    return JsonResponse({'results': results})
