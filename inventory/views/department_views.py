"""
Department views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Department
from inventory.forms import DepartmentForm

@method_decorator(login_required, name='dispatch')
# @inventory_class_permission_required('departments', 'view')
class DepartmentListView(ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأقسام'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'add')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة قسم جديد'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'edit')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل القسم'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل القسم بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'delete')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'inventory/department_confirm_delete.html'
    success_url = reverse_lazy('inventory:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف القسم بنجاح')
        return super().delete(request, *args, **kwargs)
