"""
Customer views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Customer
from inventory.forms import CustomerForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'view')
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'add')
class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'edit')
class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'delete')
class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')
