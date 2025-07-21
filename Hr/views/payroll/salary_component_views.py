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

from Hr.models import SalaryComponent, Employee
from Hr.forms.new_payroll_forms import SalaryComponentForm


# =============================================================================
# SALARY COMPONENT VIEWS
# =============================================================================

@login_required
def component_list(request):
    """عرض قائمة مكونات الراتب"""
    components = SalaryComponent.objects.all().order_by('display_order', 'name')
    
    # البحث والتصفية
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    component_type_filter = request.GET.get('component_type', '')
    
    if search_query:
        components = components.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        components = components.filter(category=category_filter)
    
    if component_type_filter:
        components = components.filter(component_type=component_type_filter)
    
    # الترقيم
    paginator = Paginator(components, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'components': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'component_type_filter': component_type_filter,
        'title': _('مكونات الراتب'),
        'categories': SalaryComponent.CATEGORIES,
        'component_types': SalaryComponent.COMPONENT_TYPES,
    }
    
    return render(request, 'Hr/payroll/salary_component_list.html', context)


@login_required
def component_detail(request, component_id):
    """عرض تفاصيل مكون الراتب"""
    component = get_object_or_404(SalaryComponent, id=component_id)
    
    # إحصائيات الاستخدام
    usage_stats = {
        'total_employees': component.employee_salary_components.count(),
        'active_employees': component.employee_salary_components.filter(
            is_active=True
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
            component = form.save(commit=False)
            component.created_by = request.user
            component.save()
            
            messages.success(request, _('تم إنشاء مكون الراتب بنجاح'))
            return redirect('Hr:salary_components:detail', component_id=component.id)
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
    component = get_object_or_404(SalaryComponent, id=component_id)
    
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث مكون الراتب بنجاح'))
            return redirect('Hr:salary_components:detail', component_id=component.id)
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
    component = get_object_or_404(SalaryComponent, id=component_id)
    
    if request.method == 'POST':
        # التحقق من عدم وجود استخدام للمكون
        if component.employee_salary_components.exists():
            messages.error(
                request, 
                _('لا يمكن حذف مكون الراتب لأنه مستخدم من قبل موظفين')
            )
            return redirect('Hr:salary_components:detail', component_id=component.id)
        
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
        component = get_object_or_404(SalaryComponent, id=component_id)
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
    original_component = get_object_or_404(SalaryComponent, id=component_id)
    
    if request.method == 'POST':
        # إنشاء نسخة جديدة
        new_component = SalaryComponent.objects.create(
            name=f"{original_component.name} - نسخة",
            code=f"{original_component.code}_COPY",
            component_type=original_component.component_type,
            category=original_component.category,
            calculation_method=original_component.calculation_method,
            default_amount=original_component.default_amount,
            percentage_base=original_component.percentage_base,
            is_taxable=original_component.is_taxable,
            is_mandatory=original_component.is_mandatory,
            description=f"نسخة من {original_component.description}",
            created_by=request.user
        )
        
        messages.success(request, f'تم نسخ مكون الراتب بنجاح')
        return redirect('Hr:salary_components:edit', component_id=new_component.id)
    
    context = {
        'component': original_component,
        'title': f"نسخ مكون الراتب - {original_component.name}",
    }
    
    return render(request, 'Hr/payroll/salary_component_duplicate.html', context)


@login_required
def component_search_ajax(request):
    """البحث السريع عن مكونات الراتب - AJAX"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    components = SalaryComponent.objects.filter(is_active=True)
    
    if query:
        components = components.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )
    
    if category:
        components = components.filter(category=category)
    
    components = components[:10]  # الحد الأقصى 10 نتائج
    
    results = []
    for component in components:
        results.append({
            'id': str(component.id),
            'name': component.name,
            'code': component.code,
            'category': component.get_category_display(),
            'component_type': component.get_component_type_display(),
            'default_amount': float(component.default_amount) if component.default_amount else 0,
        })
    
    return JsonResponse({'results': results})
