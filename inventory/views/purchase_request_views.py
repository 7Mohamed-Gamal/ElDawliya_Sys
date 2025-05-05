"""
Purchase request views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import F
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from inventory.decorators import inventory_module_permission_required, inventory_class_permission_required
from inventory.models_local import Product, PurchaseRequest
from inventory.forms import PurchaseRequestForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('purchase_requests', 'view')
class PurchaseRequestListView(ListView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_list.html'
    context_object_name = 'purchase_requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة طلبات الشراء'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('purchase_requests', 'add')
class PurchaseRequestCreateView(CreateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'inventory/purchase_request_form.html'
    success_url = reverse_lazy('inventory:purchase_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة طلب شراء جديد'
        # Add product ID from URL if provided
        product_id = self.request.GET.get('product_id')
        if product_id:
            product = get_object_or_404(Product, product_id=product_id)
            context['product'] = product
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة طلب الشراء بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('purchase_requests', 'edit')
class PurchaseRequestUpdateView(UpdateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'inventory/purchase_request_form.html'
    success_url = reverse_lazy('inventory:purchase_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل طلب الشراء'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل طلب الشراء بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('purchase_requests', 'delete')
class PurchaseRequestDeleteView(DeleteView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_confirm_delete.html'
    success_url = reverse_lazy('inventory:purchase_request_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف طلب الشراء بنجاح')
        return super().delete(request, *args, **kwargs)

@login_required
@inventory_class_permission_required('purchase_requests', 'edit')
def mark_purchase_request_as_completed(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    purchase_request.status = 'completed'
    purchase_request.save()
    messages.success(request, 'تم تحديث حالة طلب الشراء إلى "تم التنفيذ"')
    return redirect('inventory:purchase_request_list')

@login_required
@inventory_module_permission_required('purchase_requests', 'add')
def create_purchase_request(request, product_id):
    """
    تحويل طلب إنشاء طلب شراء إلى نظام طلبات الشراء الرئيسي
    """
    import json
    import requests
    from django.conf import settings
    
    product = get_object_or_404(Product, product_id=product_id)
    
    # استخدام نظام طلبات الشراء الرئيسي عبر الـ API
    try:
        # استدعاء API ترحيل المنتج إلى طلب شراء من تطبيق Purchase_orders
        from django.urls import reverse
        api_url = request.build_absolute_uri(reverse('Purchase_orders:transfer_product_to_purchase_request'))
        
        # تجهيز بيانات الطلب
        data = {
            'product_id': product_id,
            'action': 'add'
        }
        
        # استخدام الـ session الحالية للحفاظ على المصادقة
        from django.http import HttpRequest
        from datetime import datetime
        from django.middleware.csrf import get_token
        
        # استخدام requests مع تمرير الـ session والـ csrf token من الـ request الحالي
        import urllib.parse
        from django.http import HttpResponse
        from django.views.decorators.csrf import csrf_exempt
        
        # الحل البديل: إنشاء طلب مباشر إلى views.py في Purchase_orders
        from Purchase_orders.views import transfer_product_to_purchase_request as purchase_api_view

        # إنشاء request مشابه للـ AJAX request
        ajax_request = HttpRequest()
        ajax_request.method = 'POST'
        ajax_request.user = request.user
        ajax_request.META = request.META.copy()
        ajax_request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        ajax_request.body = json.dumps(data).encode('utf-8')
        ajax_request._body = ajax_request.body
        
        # استدعاء الـ view مباشرة
        response = purchase_api_view(ajax_request)
        
        # فحص النتيجة
        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            request_id = response_data.get('request_id')
            
            messages.success(request, f'تم إنشاء طلب شراء جديد للصنف {product.name}')
            return redirect('Purchase_orders:purchase_request_detail', pk=request_id)
        else:
            error_data = json.loads(response.content.decode('utf-8'))
            error_message = error_data.get('message', 'حدث خطأ أثناء إنشاء طلب الشراء')
            messages.error(request, error_message)
            return redirect('inventory:product_list')
            
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء إنشاء طلب الشراء: {str(e)}')
        return redirect('inventory:product_list')
