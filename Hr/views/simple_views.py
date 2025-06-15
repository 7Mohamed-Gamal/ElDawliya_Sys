# =============================================================================
# ElDawliya HR Management System - Simple Views for Testing
# =============================================================================
# Simple views to test URL patterns without complex functionality
# =============================================================================

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# =============================================================================
# SIMPLE TEMPLATE VIEWS
# =============================================================================

@method_decorator(login_required, name='dispatch')
class SimpleListView(TemplateView):
    """عرض قائمة بسيط للاختبار"""
    template_name = 'Hr/simple_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'قائمة بسيطة',
            'items': [],
            'message': 'هذا عرض بسيط للاختبار'
        })
        return context

@method_decorator(login_required, name='dispatch')
class SimpleDetailView(TemplateView):
    """عرض تفاصيل بسيط للاختبار"""
    template_name = 'Hr/simple_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'تفاصيل بسيطة',
            'item_id': kwargs.get('pk', 1),
            'message': 'هذا عرض تفاصيل بسيط للاختبار'
        })
        return context

@method_decorator(login_required, name='dispatch')
class SimpleCreateView(TemplateView):
    """عرض إنشاء بسيط للاختبار"""
    template_name = 'Hr/simple_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'إنشاء جديد',
            'form_action': 'create',
            'message': 'هذا نموذج بسيط للاختبار'
        })
        return context

# =============================================================================
# AJAX VIEWS
# =============================================================================

@login_required
def simple_ajax_view(request):
    """عرض AJAX بسيط للاختبار"""
    return JsonResponse({
        'success': True,
        'message': 'تم الاتصال بنجاح',
        'data': {
            'timestamp': str(timezone.now()),
            'user': request.user.username
        }
    })

@login_required
def simple_search_ajax(request):
    """بحث AJAX بسيط للاختبار"""
    query = request.GET.get('q', '')
    return JsonResponse({
        'success': True,
        'query': query,
        'results': [
            {'id': 1, 'name': f'نتيجة 1 للبحث: {query}'},
            {'id': 2, 'name': f'نتيجة 2 للبحث: {query}'},
        ]
    })

# =============================================================================
# FUNCTION-BASED VIEWS
# =============================================================================

@login_required
def simple_function_view(request):
    """عرض دالة بسيط للاختبار"""
    context = {
        'title': 'عرض دالة بسيط',
        'message': 'هذا عرض دالة بسيط للاختبار',
        'user': request.user
    }
    return render(request, 'Hr/simple_function.html', context)

@login_required
def get_branches_by_company(request):
    """الحصول على الفروع حسب الشركة - للاختبار"""
    company_id = request.GET.get('company_id')
    return JsonResponse({
        'success': True,
        'company_id': company_id,
        'branches': [
            {'id': 1, 'name': 'الفرع الرئيسي'},
            {'id': 2, 'name': 'فرع القاهرة'},
        ]
    })

@login_required
def get_departments_by_branch(request):
    """الحصول على الأقسام حسب الفرع - للاختبار"""
    branch_id = request.GET.get('branch_id')
    return JsonResponse({
        'success': True,
        'branch_id': branch_id,
        'departments': [
            {'id': 1, 'name': 'قسم الموارد البشرية'},
            {'id': 2, 'name': 'قسم المحاسبة'},
        ]
    })

@login_required
def get_job_positions_by_department(request):
    """الحصول على المناصب حسب القسم - للاختبار"""
    department_id = request.GET.get('department_id')
    return JsonResponse({
        'success': True,
        'department_id': department_id,
        'positions': [
            {'id': 1, 'name': 'مدير الموارد البشرية'},
            {'id': 2, 'name': 'موظف موارد بشرية'},
        ]
    })

# =============================================================================
# CALCULATION VIEWS
# =============================================================================

@login_required
def payroll_calculation_view(request):
    """عرض حساب الرواتب - للاختبار"""
    context = {
        'title': 'حساب الرواتب',
        'message': 'هذا عرض حساب الرواتب للاختبار',
        'calculation_status': 'جاهز للحساب'
    }
    return render(request, 'Hr/simple_calculation.html', context)

@login_required
def calculate_payroll(request):
    """حساب الرواتب - للاختبار"""
    return JsonResponse({
        'success': True,
        'message': 'تم حساب الرواتب بنجاح',
        'calculated_entries': 10,
        'total_amount': 50000.00
    })

@login_required
def calculate_employee_payroll(request, employee_id):
    """حساب راتب موظف - للاختبار"""
    return JsonResponse({
        'success': True,
        'employee_id': employee_id,
        'message': f'تم حساب راتب الموظف {employee_id} بنجاح',
        'net_salary': 5000.00
    })

# =============================================================================
# ATTENDANCE VIEWS
# =============================================================================

@login_required
def new_attendance_dashboard_data(request):
    """بيانات لوحة تحكم الحضور - للاختبار"""
    return JsonResponse({
        'success': True,
        'data': {
            'present_today': 45,
            'absent_today': 5,
            'late_today': 3,
            'total_employees': 50
        }
    })

@login_required
def new_attendance_quick_add(request):
    """إضافة سريعة للحضور - للاختبار"""
    return JsonResponse({
        'success': True,
        'message': 'تم تسجيل الحضور بنجاح',
        'timestamp': str(timezone.now())
    })

# =============================================================================
# EMPLOYEE VIEWS
# =============================================================================

@login_required
def new_employee_search_ajax(request):
    """البحث عن الموظفين - للاختبار"""
    query = request.GET.get('q', '')
    return JsonResponse({
        'success': True,
        'query': query,
        'employees': [
            {
                'id': 1,
                'name': 'أحمد محمد',
                'employee_number': 'EMP001',
                'department': 'الموارد البشرية'
            },
            {
                'id': 2,
                'name': 'فاطمة علي',
                'employee_number': 'EMP002',
                'department': 'المحاسبة'
            }
        ]
    })

@login_required
def new_employee_quick_stats(request, pk):
    """إحصائيات سريعة للموظف - للاختبار"""
    return JsonResponse({
        'success': True,
        'employee_id': pk,
        'stats': {
            'attendance_rate': 95.5,
            'leave_balance': 15,
            'performance_score': 4.2
        }
    })

@login_required
def new_employee_status_update(request, pk):
    """تحديث حالة الموظف - للاختبار"""
    return JsonResponse({
        'success': True,
        'employee_id': pk,
        'message': 'تم تحديث حالة الموظف بنجاح'
    })

@login_required
def new_employee_bulk_update(request):
    """تحديث مجمع للموظفين - للاختبار"""
    return JsonResponse({
        'success': True,
        'message': 'تم التحديث المجمع بنجاح',
        'updated_count': 5
    })

@login_required
def new_export_employees_excel(request):
    """تصدير الموظفين إلى Excel - للاختبار"""
    return JsonResponse({
        'success': True,
        'message': 'تم تصدير البيانات بنجاح',
        'file_url': '/media/exports/employees.xlsx'
    })

# =============================================================================
# IMPORTS
# =============================================================================

from django.utils import timezone
