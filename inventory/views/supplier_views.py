"""
Supplier views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Supplier, Product
from inventory.forms import SupplierForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'add')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة مورد جديد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'edit')
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل المورد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'delete')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المورد بنجاح')
        return super().delete(request, *args, **kwargs)
