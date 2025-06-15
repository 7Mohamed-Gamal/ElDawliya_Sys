# =============================================================================
# ElDawliya HR Management System - Company Views
# =============================================================================
# Views for company structure management (Company, Branch, Department, JobPosition)
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db import transaction
import json

from Hr.models import Company, Branch, Department, JobPosition, Employee
from Hr.forms.company_forms import CompanyForm, BranchForm, DepartmentForm, JobPositionForm


# =============================================================================
# COMPANY VIEWS
# =============================================================================

class CompanyListView(LoginRequiredMixin, ListView):
    """عرض قائمة الشركات"""
    model = Company
    template_name = 'Hr/company/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Company.objects.all().order_by('name')
        
        # البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(email__icontains=search)
            )
        
        # التصفية حسب الحالة
        status = self.request.GET.get('status')
        if status:
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة الشركات')
        context['search_value'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        
        # إحصائيات
        context['total_companies'] = Company.objects.count()
        context['active_companies'] = Company.objects.filter(is_active=True).count()
        context['inactive_companies'] = Company.objects.filter(is_active=False).count()
        
        return context


class CompanyDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل الشركة"""
    model = Company
    template_name = 'Hr/company/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        
        context['title'] = f"تفاصيل الشركة - {company.name}"
        
        # إحصائيات الشركة
        context['branches_count'] = company.branches.count()
        context['departments_count'] = company.departments.count()
        context['employees_count'] = company.employees.count()
        context['active_employees'] = company.employees.filter(status='active').count()
        
        # الفروع والأقسام
        context['branches'] = company.branches.filter(is_active=True)[:5]
        context['departments'] = company.departments.filter(is_active=True)[:5]
        context['recent_employees'] = company.employees.filter(status='active').order_by('-created_at')[:5]
        
        return context


class CompanyCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء شركة جديدة"""
    model = Company
    form_class = CompanyForm
    template_name = 'Hr/company/company_form.html'
    permission_required = 'Hr.add_company'
    success_url = reverse_lazy('hr:company_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة شركة جديدة')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء الشركة بنجاح'))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, _('حدث خطأ في البيانات المدخلة'))
        return super().form_invalid(form)


class CompanyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """تحديث بيانات الشركة"""
    model = Company
    form_class = CompanyForm
    template_name = 'Hr/company/company_form.html'
    permission_required = 'Hr.change_company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"تحديث بيانات الشركة - {self.get_object().name}"
        context['action'] = 'update'
        return context
    
    def get_success_url(self):
        return reverse('hr:company_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث بيانات الشركة بنجاح'))
        return super().form_valid(form)


class CompanyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """حذف الشركة"""
    model = Company
    template_name = 'Hr/company/company_confirm_delete.html'
    permission_required = 'Hr.delete_company'
    success_url = reverse_lazy('hr:company_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        context['title'] = f"حذف الشركة - {company.name}"
        
        # التحقق من وجود بيانات مرتبطة
        context['has_branches'] = company.branches.exists()
        context['has_employees'] = company.employees.exists()
        context['branches_count'] = company.branches.count()
        context['employees_count'] = company.employees.count()
        
        return context
    
    def delete(self, request, *args, **kwargs):
        company = self.get_object()
        
        # التحقق من وجود بيانات مرتبطة
        if company.employees.exists():
            messages.error(request, _('لا يمكن حذف الشركة لوجود موظفين مرتبطين بها'))
            return redirect('hr:company_detail', pk=company.pk)
        
        messages.success(request, f"تم حذف الشركة '{company.name}' بنجاح")
        return super().delete(request, *args, **kwargs)


# =============================================================================
# BRANCH VIEWS
# =============================================================================

class BranchListView(LoginRequiredMixin, ListView):
    """عرض قائمة الفروع"""
    model = Branch
    template_name = 'Hr/branch/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Branch.objects.select_related('company', 'manager').order_by('company__name', 'name')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(company__name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة الفروع')
        context['companies'] = Company.objects.filter(is_active=True)
        context['search_value'] = self.request.GET.get('search', '')
        context['company_filter'] = self.request.GET.get('company', '')
        
        return context


class BranchDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل الفرع"""
    model = Branch
    template_name = 'Hr/branch/branch_detail.html'
    context_object_name = 'branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branch = self.get_object()
        
        context['title'] = f"تفاصيل الفرع - {branch.name}"
        context['departments_count'] = branch.departments.count()
        context['employees_count'] = branch.employees.count()
        context['departments'] = branch.departments.filter(is_active=True)
        
        return context


class BranchCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء فرع جديد"""
    model = Branch
    form_class = BranchForm
    template_name = 'Hr/branch/branch_form.html'
    permission_required = 'Hr.add_branch'
    success_url = reverse_lazy('hr:branch_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        company_id = self.request.GET.get('company')
        if company_id:
            try:
                kwargs['company'] = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة فرع جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء الفرع بنجاح'))
        return super().form_valid(form)


class BranchUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """تحديث بيانات الفرع"""
    model = Branch
    form_class = BranchForm
    template_name = 'Hr/branch/branch_form.html'
    permission_required = 'Hr.change_branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"تحديث بيانات الفرع - {self.get_object().name}"
        context['action'] = 'update'
        return context
    
    def get_success_url(self):
        return reverse('hr:branch_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث بيانات الفرع بنجاح'))
        return super().form_valid(form)


# =============================================================================
# DEPARTMENT VIEWS
# =============================================================================

class DepartmentListView(LoginRequiredMixin, ListView):
    """عرض قائمة الأقسام"""
    model = Department
    template_name = 'Hr/department/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Department.objects.select_related(
            'company', 'branch', 'parent_department', 'manager'
        ).order_by('company__name', 'name')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # التصفية حسب الفرع
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة الأقسام')
        context['companies'] = Company.objects.filter(is_active=True)
        context['branches'] = Branch.objects.filter(is_active=True)
        
        return context


class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء قسم جديد"""
    model = Department
    form_class = DepartmentForm
    template_name = 'Hr/department/department_form.html'
    permission_required = 'Hr.add_department'
    success_url = reverse_lazy('hr:department_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة قسم جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء القسم بنجاح'))
        return super().form_valid(form)


# =============================================================================
# JOB POSITION VIEWS
# =============================================================================

class JobPositionListView(LoginRequiredMixin, ListView):
    """عرض قائمة المناصب الوظيفية"""
    model = JobPosition
    template_name = 'Hr/job_position/job_position_list.html'
    context_object_name = 'job_positions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = JobPosition.objects.select_related(
            'company', 'department'
        ).order_by('company__name', 'department__name', 'title')
        
        # التصفية حسب الشركة
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # التصفية حسب المستوى
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إدارة المناصب الوظيفية')
        context['companies'] = Company.objects.filter(is_active=True)
        context['levels'] = JobPosition._meta.get_field('level').choices
        
        return context


class JobPositionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء منصب وظيفي جديد"""
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'Hr/job_position/job_position_form.html'
    permission_required = 'Hr.add_jobposition'
    success_url = reverse_lazy('hr:job_position_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('إضافة منصب وظيفي جديد')
        context['action'] = 'create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء المنصب الوظيفي بنجاح'))
        return super().form_valid(form)


# =============================================================================
# AJAX VIEWS FOR DYNAMIC FILTERING
# =============================================================================

@login_required
def get_branches_by_company(request):
    """الحصول على الفروع حسب الشركة - AJAX"""
    company_id = request.GET.get('company_id')
    branches = []
    
    if company_id:
        branches = list(
            Branch.objects.filter(company_id=company_id, is_active=True)
            .values('id', 'name')
            .order_by('name')
        )
    
    return JsonResponse({'branches': branches})


@login_required
def get_departments_by_branch(request):
    """الحصول على الأقسام حسب الفرع - AJAX"""
    branch_id = request.GET.get('branch_id')
    departments = []
    
    if branch_id:
        departments = list(
            Department.objects.filter(branch_id=branch_id, is_active=True)
            .values('id', 'name')
            .order_by('name')
        )
    
    return JsonResponse({'departments': departments})


@login_required
def get_job_positions_by_department(request):
    """الحصول على المناصب حسب القسم - AJAX"""
    department_id = request.GET.get('department_id')
    job_positions = []
    
    if department_id:
        job_positions = list(
            JobPosition.objects.filter(department_id=department_id, is_active=True)
            .values('id', 'title')
            .order_by('title')
        )
    
    return JsonResponse({'job_positions': job_positions})
