# =============================================================================
# ElDawliya HR Management System - New Leave Management Views
# =============================================================================
# Views for leave management (Leave Types, Requests, Balances)
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
    LeaveType, EmployeeLeaveBalance, LeaveRequest,
    Employee, Company, HRAuditLog
)
from Hr.forms.new_leave_forms import (
    LeaveTypeForm, EmployeeLeaveBalanceForm, LeaveRequestForm,
    LeaveRequestApprovalForm, LeaveReportForm
)


# =============================================================================
# LEAVE TYPE VIEWS
# =============================================================================

class NewLeaveTypeListView(LoginRequiredMixin, ListView):
    """عرض قائمة أنواع الإجازات الجديد"""
    model = LeaveType
    template_name = 'Hr/new_leave/leave_type_list.html'
    context_object_name = 'leave_types'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = LeaveType.objects.select_related('company').order_by('company__name', 'name')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
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
        context['title'] = _('إدارة أنواع الإجازات')
        context['companies'] = Company.objects.filter(is_active=True)
        context['search_value'] = self.request.GET.get('search', '')
        
        # إحصائيات
        context['total_leave_types'] = LeaveType.objects.count()
        context['active_leave_types'] = LeaveType.objects.filter(is_active=True).count()
        context['paid_leave_types'] = LeaveType.objects.filter(is_paid=True).count()
        
        return context


class NewLeaveTypeDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل نوع الإجازة الجديد"""
    model = LeaveType
    template_name = 'Hr/new_leave/leave_type_detail.html'
    context_object_name = 'leave_type'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        leave_type = self.get_object()
        
        context['title'] = f"تفاصيل نوع الإجازة - {leave_type.name}"
        
        # إحصائيات نوع الإجازة
        context['total_requests'] = leave_type.leave_requests.count()
        context['approved_requests'] = leave_type.leave_requests.filter(status='approved').count()
        context['pending_requests'] = leave_type.leave_requests.filter(status='submitted').count()
        context['employees_with_balance'] = leave_type.employee_balances.filter(
            allocated_days__gt=0
        ).count()
        
        # الطلبات الحديثة
        context['recent_requests'] = leave_type.leave_requests.select_related(
            'employee'
        ).order_by('-created_at')[:5]
        
        return context


class NewLeaveTypeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء نوع إجازة جديد"""
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = 'Hr/new_leave/leave_type_form.html'
    permission_required = 'Hr.add_leavetype'
    success_url = reverse_lazy('hr:new_leave_type_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة نوع إجازة جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء نوع الإجازة بنجاح'))
        
        # تسجيل في سجل التدقيق
        HRAuditLog.objects.create(
            user=self.request.user,
            action='create',
            model_name='LeaveType',
            object_id=str(form.instance.pk),
            object_repr=str(form.instance),
            changes={'created': 'نوع إجازة جديد'}
        )
        
        return super().form_valid(form)


class NewLeaveTypeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """تحديث نوع الإجازة"""
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = 'Hr/new_leave/leave_type_form.html'
    permission_required = 'Hr.change_leavetype'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"تحديث نوع الإجازة - {self.get_object().name}"
        context['action'] = 'update'
        return context
    
    def get_success_url(self):
        return reverse('hr:new_leave_type_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث نوع الإجازة بنجاح'))
        return super().form_valid(form)


# =============================================================================
# EMPLOYEE LEAVE BALANCE VIEWS
# =============================================================================

class NewEmployeeLeaveBalanceListView(LoginRequiredMixin, ListView):
    """عرض أرصدة إجازات الموظفين الجديد"""
    model = EmployeeLeaveBalance
    template_name = 'Hr/new_leave/leave_balance_list.html'
    context_object_name = 'leave_balances'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = EmployeeLeaveBalance.objects.select_related(
            'employee', 'leave_type'
        ).order_by('employee__full_name', 'leave_type__name')
        
        # التصفية حسب الموظف
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # التصفية حسب نوع الإجازة
        leave_type_id = self.request.GET.get('leave_type')
        if leave_type_id:
            queryset = queryset.filter(leave_type_id=leave_type_id)
        
        # التصفية حسب السنة
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(year=year)
        else:
            # السنة الحالية افتراضياً
            queryset = queryset.filter(year=date.today().year)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('أرصدة إجازات الموظفين')
        
        # خيارات التصفية
        context['employees'] = Employee.objects.filter(status='active')
        context['leave_types'] = LeaveType.objects.filter(is_active=True)
        context['years'] = range(date.today().year - 2, date.today().year + 2)
        
        # القيم المحددة
        context['employee_filter'] = self.request.GET.get('employee', '')
        context['leave_type_filter'] = self.request.GET.get('leave_type', '')
        context['year_filter'] = self.request.GET.get('year', str(date.today().year))
        
        return context


class NewEmployeeLeaveBalanceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء رصيد إجازة للموظف"""
    model = EmployeeLeaveBalance
    form_class = EmployeeLeaveBalanceForm
    template_name = 'Hr/new_leave/leave_balance_form.html'
    permission_required = 'Hr.add_employeeleavebalance'
    success_url = reverse_lazy('hr:new_leave_balance_list')
    
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
        context['title'] = _('إضافة رصيد إجازة للموظف')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء رصيد الإجازة بنجاح'))
        return super().form_valid(form)


# =============================================================================
# LEAVE REQUEST VIEWS
# =============================================================================

class NewLeaveRequestListView(LoginRequiredMixin, ListView):
    """عرض قائمة طلبات الإجازات الجديد"""
    model = LeaveRequest
    template_name = 'Hr/new_leave/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'approved_by'
        ).order_by('-created_at')
        
        # التصفية حسب الموظف
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # التصفية حسب نوع الإجازة
        leave_type_id = self.request.GET.get('leave_type')
        if leave_type_id:
            queryset = queryset.filter(leave_type_id=leave_type_id)
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # التصفية حسب التاريخ
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(end_date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('طلبات الإجازات')
        
        # خيارات التصفية
        context['employees'] = Employee.objects.filter(status='active')
        context['leave_types'] = LeaveType.objects.filter(is_active=True)
        context['status_choices'] = LeaveRequest.STATUS_CHOICES
        
        # القيم المحددة
        context['employee_filter'] = self.request.GET.get('employee', '')
        context['leave_type_filter'] = self.request.GET.get('leave_type', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # إحصائيات
        all_requests = LeaveRequest.objects.all()
        context['total_requests'] = all_requests.count()
        context['pending_requests'] = all_requests.filter(status='submitted').count()
        context['approved_requests'] = all_requests.filter(status='approved').count()
        context['rejected_requests'] = all_requests.filter(status='rejected').count()
        
        return context


class NewLeaveRequestDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل طلب الإجازة الجديد"""
    model = LeaveRequest
    template_name = 'Hr/new_leave/leave_request_detail.html'
    context_object_name = 'leave_request'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        leave_request = self.get_object()
        
        context['title'] = f"تفاصيل طلب الإجازة - {leave_request.employee.full_name}"
        
        # رصيد الإجازة المتاح
        try:
            balance = EmployeeLeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            context['leave_balance'] = balance
        except EmployeeLeaveBalance.DoesNotExist:
            context['leave_balance'] = None
        
        # طلبات الإجازة الأخرى للموظف
        context['other_requests'] = LeaveRequest.objects.filter(
            employee=leave_request.employee
        ).exclude(pk=leave_request.pk).order_by('-created_at')[:5]
        
        return context


class NewLeaveRequestCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء طلب إجازة جديد"""
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'Hr/new_leave/leave_request_form.html'
    permission_required = 'Hr.add_leaverequest'
    
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
        context['title'] = _('تقديم طلب إجازة جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم تقديم طلب الإجازة بنجاح'))
        
        # تسجيل في سجل التدقيق
        HRAuditLog.objects.create(
            user=self.request.user,
            action='create',
            model_name='LeaveRequest',
            object_id=str(form.instance.pk),
            object_repr=str(form.instance),
            changes={'created': 'طلب إجازة جديد'}
        )
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('hr:new_leave_request_detail', kwargs={'pk': self.object.pk})
