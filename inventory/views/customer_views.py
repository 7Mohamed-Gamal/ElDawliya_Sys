"""
Customer views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Customer
from inventory.forms import CustomerForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'view')
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة العملاء'
        # Add low stock count for sidebar
        try:
            from django.db.models import F
            from inventory.models_local import Product
            low_stock_count = Product.objects.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            ).count()
            context['low_stock_count'] = low_stock_count
        except Exception as e:
            # Log the error but don't break the view
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating low stock count: {str(e)}")
            context['low_stock_count'] = 0
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'add')
class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة العميل بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'edit')
class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث بيانات العميل بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'delete')
class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

    def post(self, request, *args, **kwargs):
        try:
            customer = self.get_object()
            # Check for any related records before deleting
            if hasattr(customer, 'vouchers') and customer.vouchers.exists():
                messages.error(request, f'لا يمكن حذف العميل {customer.name} لوجود إذونات مرتبطة به')
                return redirect('inventory:customer_list')
                
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'تم حذف العميل {customer.name} بنجاح')
            return response
            
        except ProtectedError:
            messages.error(request, f'لا يمكن حذف العميل {self.get_object().name} لوجود سجلات مرتبطة به')
            return redirect('inventory:customer_list')
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('inventory:customer_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف العميل: {str(e)}')
            return redirect('inventory:customer_list')
