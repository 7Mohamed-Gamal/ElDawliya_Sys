# =============================================================================
# ElDawliya HR Management System - Payroll Views
# =============================================================================
# Views for payroll management (Salary Components, Payroll Entries, etc.)
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import json

from Hr.models import (
    SalaryComponent, EmployeeSalaryStructure, PayrollPeriod,
    PayrollEntry, Employee, Company, HRAuditLog
)
from Hr.forms.new_payroll_forms import (
    SalaryComponentForm, EmployeeSalaryStructureForm, PayrollPeriodForm,
    PayrollEntryForm, PayrollCalculationForm, PayrollReportForm
)


# =============================================================================
# SALARY COMPONENT VIEWS
# =============================================================================

class SalaryComponentListView(LoginRequiredMixin, ListView):
    """عرض قائمة مكونات الراتب"""
    model = SalaryComponent
    template_name = 'Hr/payroll/salary_component_list.html'
    context_object_name = 'salary_components'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SalaryComponent.objects.select_related('company').order_by(
            'company__name', 'component_type', 'name'
        )
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # التصفية حسب نوع المكون
        component_type = self.request.GET.get('component_type')
        if component_type:
            queryset = queryset.filter(component_type=component_type)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        # البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة مكونات الراتب')
        
        # خيارات التصفية
        context['companies'] = Company.objects.filter(is_active=True)
        context['component_types'] = SalaryComponent._meta.get_field('component_type').choices
        context['search_value'] = self.request.GET.get('search', '')
        
        # إحصائيات
        context['total_components'] = SalaryComponent.objects.count()
        context['active_components'] = SalaryComponent.objects.filter(is_active=True).count()
        context['basic_components'] = SalaryComponent.objects.filter(component_type='basic').count()
        context['allowance_components'] = SalaryComponent.objects.filter(component_type='allowance').count()
        context['deduction_components'] = SalaryComponent.objects.filter(component_type='deduction').count()
        
        return context


class SalaryComponentDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل مكون الراتب"""
    model = SalaryComponent
    template_name = 'Hr/payroll/salary_component_detail.html'
    context_object_name = 'salary_component'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        salary_component = self.get_object()
        
        context['title'] = f"تفاصيل مكون الراتب - {salary_component.name}"
        
        # إحصائيات المكون
        context['employees_count'] = salary_component.employee_structures.filter(
            is_active=True
        ).count()
        context['total_amount'] = salary_component.employee_structures.filter(
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # الموظفين المرتبطين
        context['employee_structures'] = salary_component.employee_structures.filter(
            is_active=True
        ).select_related('employee')[:10]
        
        return context


class SalaryComponentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء مكون راتب جديد"""
    model = SalaryComponent
    form_class = SalaryComponentForm
    template_name = 'Hr/payroll/salary_component_form.html'
    permission_required = 'Hr.add_salarycomponent'
    success_url = reverse_lazy('hr:salary_component_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة مكون راتب جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء مكون الراتب بنجاح'))
        
        # تسجيل في سجل التدقيق
        HRAuditLog.objects.create(
            user=self.request.user,
            action='create',
            model_name='SalaryComponent',
            object_id=str(form.instance.pk),
            object_repr=str(form.instance),
            changes={'created': 'مكون راتب جديد'}
        )
        
        return super().form_valid(form)


class SalaryComponentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """تحديث مكون الراتب"""
    model = SalaryComponent
    form_class = SalaryComponentForm
    template_name = 'Hr/payroll/salary_component_form.html'
    permission_required = 'Hr.change_salarycomponent'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"تحديث مكون الراتب - {self.get_object().name}"
        context['action'] = 'update'
        return context
    
    def get_success_url(self):
        return reverse('hr:salary_component_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث مكون الراتب بنجاح'))
        return super().form_valid(form)


# =============================================================================
# EMPLOYEE SALARY STRUCTURE VIEWS
# =============================================================================

class EmployeeSalaryStructureListView(LoginRequiredMixin, ListView):
    """عرض هياكل رواتب الموظفين"""
    model = EmployeeSalaryStructure
    template_name = 'Hr/payroll/salary_structure_list.html'
    context_object_name = 'salary_structures'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = EmployeeSalaryStructure.objects.select_related(
            'employee', 'salary_component'
        ).order_by('employee__full_name', 'salary_component__name')
        
        # التصفية حسب الموظف
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # التصفية حسب مكون الراتب
        component_id = self.request.GET.get('component')
        if component_id:
            queryset = queryset.filter(salary_component_id=component_id)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('هياكل رواتب الموظفين')
        
        # خيارات التصفية
        context['employees'] = Employee.objects.filter(status='active')
        context['salary_components'] = SalaryComponent.objects.filter(is_active=True)
        
        return context


class EmployeeSalaryStructureCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء هيكل راتب للموظف"""
    model = EmployeeSalaryStructure
    form_class = EmployeeSalaryStructureForm
    template_name = 'Hr/payroll/salary_structure_form.html'
    permission_required = 'Hr.add_employeesalarystructure'
    success_url = reverse_lazy('hr:salary_structure_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        employee_id = self.request.GET.get('employee')
        if employee_id:
            try:
                kwargs['employee'] = Employee.objects.get(pk=employee_id)
            except Employee.DoesNotExist:
                pass
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة هيكل راتب للموظف')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم إنشاء هيكل الراتب بنجاح'))
        return super().form_valid(form)


# =============================================================================
# PAYROLL PERIOD VIEWS
# =============================================================================

class PayrollPeriodListView(LoginRequiredMixin, ListView):
    """عرض قائمة فترات الرواتب"""
    model = PayrollPeriod
    template_name = 'Hr/payroll/payroll_period_list.html'
    context_object_name = 'payroll_periods'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PayrollPeriod.objects.select_related('company').order_by('-start_date')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة فترات الرواتب')
        
        # خيارات التصفية
        context['companies'] = Company.objects.filter(is_active=True)
        context['status_choices'] = PayrollPeriod._meta.get_field('status').choices
        
        # إحصائيات
        context['total_periods'] = PayrollPeriod.objects.count()
        context['draft_periods'] = PayrollPeriod.objects.filter(status='draft').count()
        context['calculated_periods'] = PayrollPeriod.objects.filter(status='calculated').count()
        context['paid_periods'] = PayrollPeriod.objects.filter(status='paid').count()
        
        return context


class PayrollPeriodDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل فترة الراتب"""
    model = PayrollPeriod
    template_name = 'Hr/payroll/payroll_period_detail.html'
    context_object_name = 'payroll_period'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll_period = self.get_object()
        
        context['title'] = f"تفاصيل فترة الراتب - {payroll_period.name}"
        
        # إحصائيات الفترة
        context['total_entries'] = payroll_period.payroll_entries.count()
        context['calculated_entries'] = payroll_period.payroll_entries.filter(
            status='calculated'
        ).count()
        context['approved_entries'] = payroll_period.payroll_entries.filter(
            status='approved'
        ).count()
        context['paid_entries'] = payroll_period.payroll_entries.filter(
            status='paid'
        ).count()
        
        # سجلات الرواتب
        context['payroll_entries'] = payroll_period.payroll_entries.select_related(
            'employee'
        ).order_by('employee__full_name')
        
        return context


class PayrollPeriodCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء فترة راتب جديدة"""
    model = PayrollPeriod
    form_class = PayrollPeriodForm
    template_name = 'Hr/payroll/payroll_period_form.html'
    permission_required = 'Hr.add_payrollperiod'
    success_url = reverse_lazy('hr:payroll_period_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إنشاء فترة راتب جديدة')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم إنشاء فترة الراتب بنجاح'))
        
        # تسجيل في سجل التدقيق
        HRAuditLog.objects.create(
            user=self.request.user,
            action='create',
            model_name='PayrollPeriod',
            object_id=str(form.instance.pk),
            object_repr=str(form.instance),
            changes={'created': 'فترة راتب جديدة'}
        )
        
        return super().form_valid(form)


# =============================================================================
# PAYROLL ENTRY VIEWS
# =============================================================================

class PayrollEntryListView(LoginRequiredMixin, ListView):
    """عرض سجلات الرواتب"""
    model = PayrollEntry
    template_name = 'Hr/payroll/payroll_entry_list.html'
    context_object_name = 'payroll_entries'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = PayrollEntry.objects.select_related(
            'payroll_period', 'employee'
        ).order_by('-payroll_period__start_date', 'employee__full_name')
        
        # التصفية حسب فترة الراتب
        period_id = self.request.GET.get('period')
        if period_id:
            queryset = queryset.filter(payroll_period_id=period_id)
        
        # التصفية حسب الموظف
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('سجلات الرواتب')
        
        # خيارات التصفية
        context['payroll_periods'] = PayrollPeriod.objects.all().order_by('-start_date')
        context['employees'] = Employee.objects.filter(status='active')
        context['status_choices'] = PayrollEntry._meta.get_field('status').choices
        
        return context


class PayrollEntryDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل سجل الراتب"""
    model = PayrollEntry
    template_name = 'Hr/payroll/payroll_entry_detail.html'
    context_object_name = 'payroll_entry'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll_entry = self.get_object()
        
        context['title'] = f"تفاصيل راتب {payroll_entry.employee.full_name} - {payroll_entry.payroll_period.name}"
        
        # هيكل الراتب للموظف
        context['salary_structure'] = payroll_entry.employee.salary_structures.filter(
            is_active=True,
            effective_date__lte=payroll_entry.payroll_period.end_date
        ).select_related('salary_component')
        
        return context


class PayrollEntryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء سجل راتب جديد"""
    model = PayrollEntry
    form_class = PayrollEntryForm
    template_name = 'Hr/payroll/payroll_entry_form.html'
    permission_required = 'Hr.add_payrollentry'
    success_url = reverse_lazy('hr:payroll_entry_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إنشاء سجل راتب جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم إنشاء سجل الراتب بنجاح'))
        return super().form_valid(form)


# =============================================================================
# PAYROLL CALCULATION
# =============================================================================

@login_required
def payroll_calculation_view(request):
    """عرض حساب الرواتب"""
    if request.method == 'POST':
        form = PayrollCalculationForm(request.POST)
        if form.is_valid():
            # تنفيذ حساب الرواتب
            result = calculate_payroll(form.cleaned_data, request.user)
            
            if result['success']:
                messages.success(request, f"تم حساب رواتب {result['count']} موظف بنجاح")
                return redirect('hr:payroll_period_detail', pk=form.cleaned_data['payroll_period'].pk)
            else:
                messages.error(request, f"حدث خطأ في حساب الرواتب: {result['error']}")
    else:
        form = PayrollCalculationForm()
    
    return render(request, 'Hr/payroll/payroll_calculation.html', {
        'form': form,
        'title': _('حساب الرواتب التلقائي')
    })


def calculate_payroll(data, user):
    """دالة حساب الرواتب التلقائي"""
    try:
        payroll_period = data['payroll_period']
        employees = data.get('employees')
        
        if not employees:
            # حساب رواتب جميع الموظفين النشطين
            employees = Employee.objects.filter(
                company=payroll_period.company,
                status='active'
            )
        
        calculated_count = 0
        
        with transaction.atomic():
            for employee in employees:
                # التحقق من عدم وجود سجل راتب مسبق
                existing_entry = PayrollEntry.objects.filter(
                    payroll_period=payroll_period,
                    employee=employee
                ).first()
                
                if existing_entry:
                    continue  # تخطي إذا كان موجود
                
                # حساب الراتب
                payroll_data = calculate_employee_payroll(employee, payroll_period, data)
                
                # إنشاء سجل الراتب
                PayrollEntry.objects.create(
                    payroll_period=payroll_period,
                    employee=employee,
                    created_by=user,
                    **payroll_data
                )
                
                calculated_count += 1
        
        return {'success': True, 'count': calculated_count}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def calculate_employee_payroll(employee, payroll_period, options):
    """حساب راتب موظف واحد"""
    # الحصول على هيكل الراتب
    salary_structure = employee.salary_structures.filter(
        is_active=True,
        effective_date__lte=payroll_period.end_date
    )
    
    # حساب المكونات
    basic_salary = Decimal('0.00')
    total_allowances = Decimal('0.00')
    total_bonuses = Decimal('0.00')
    total_deductions = Decimal('0.00')
    
    for structure in salary_structure:
        component = structure.salary_component
        amount = structure.amount
        
        if component.component_type == 'basic':
            basic_salary += amount
        elif component.component_type == 'allowance':
            total_allowances += amount
        elif component.component_type == 'bonus':
            total_bonuses += amount
        elif component.component_type == 'deduction':
            total_deductions += amount
    
    # حساب الحضور والغياب (إذا كان مطلوب)
    working_days = 30  # افتراضي
    present_days = 30  # افتراضي
    absent_days = 0
    leave_days = 0
    overtime_hours = Decimal('0.00')
    overtime_amount = Decimal('0.00')
    
    if options.get('include_attendance'):
        # حساب بيانات الحضور الفعلية
        pass  # سيتم تطويرها لاحقاً
    
    # حساب الضريبة والتأمين
    tax_amount = Decimal('0.00')
    insurance_amount = Decimal('0.00')
    
    # حساب الراتب الإجمالي والصافي
    gross_salary = basic_salary + total_allowances + total_bonuses + overtime_amount
    net_salary = gross_salary - total_deductions - tax_amount - insurance_amount
    
    return {
        'basic_salary': basic_salary,
        'total_allowances': total_allowances,
        'total_bonuses': total_bonuses,
        'overtime_amount': overtime_amount,
        'gross_salary': gross_salary,
        'total_deductions': total_deductions,
        'tax_amount': tax_amount,
        'insurance_amount': insurance_amount,
        'net_salary': net_salary,
        'working_days': working_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'leave_days': leave_days,
        'overtime_hours': overtime_hours,
        'status': 'calculated'
    }
