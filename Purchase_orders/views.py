from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import F, Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from Purchase_orders.decorators import purchase_module_permission_required, purchase_class_permission_required

from .models import PurchaseRequest, PurchaseRequestItem
from .forms import PurchaseRequestForm, PurchaseRequestItemForm, PurchaseRequestApprovalForm
from inventory.models import TblProducts

import uuid
import json

@login_required
@purchase_module_permission_required('dashboard', 'view')
def dashboard(request):
    """عرض لوحة تحكم طلبات الشراء"""
    # إحصائيات طلبات الشراء
    pending_requests = PurchaseRequest.objects.filter(status='pending').count()
    approved_requests = PurchaseRequest.objects.filter(status='approved').count()
    rejected_requests = PurchaseRequest.objects.filter(status='rejected').count()
    completed_requests = PurchaseRequest.objects.filter(status='completed').count()
    total_requests = PurchaseRequest.objects.count()

    # طلبات الشراء الأخيرة
    recent_requests = PurchaseRequest.objects.all().order_by('-request_date')[:5]

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'completed_requests': completed_requests,
        'total_requests': total_requests,
        'recent_requests': recent_requests,
        'title': 'لوحة تحكم طلبات الشراء'
    }

    return render(request, 'Purchase_orders/dashboard.html', context)

@method_decorator(login_required, name='dispatch')
@purchase_class_permission_required('purchase_requests', 'view')
class PurchaseRequestListView(ListView):
    model = PurchaseRequest
    template_name = 'Purchase_orders/purchase_request_list.html'
    context_object_name = 'purchase_requests'
    ordering = ['-request_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'قائمة طلبات الشراء'
        return context

@method_decorator(login_required, name='dispatch')
@purchase_class_permission_required('purchase_requests', 'view')
class PurchaseRequestDetailView(DetailView):
    model = PurchaseRequest
    template_name = 'Purchase_orders/purchase_request_detail.html'
    context_object_name = 'purchase_request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'تفاصيل طلب الشراء #{self.object.request_number}'
        return context

@login_required
@purchase_module_permission_required('purchase_requests', 'add')
def create_purchase_request(request):
    """إنشاء طلب شراء جديد"""
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.requested_by = request.user
            purchase_request.save()
            messages.success(request, 'تم إنشاء طلب الشراء بنجاح')
            return redirect('Purchase_orders:purchase_request_detail', pk=purchase_request.pk)
    else:
        # إنشاء رقم طلب فريد
        request_number = f"PR-{uuid.uuid4().hex[:8].upper()}"
        form = PurchaseRequestForm(initial={'request_number': request_number})

    context = {
        'form': form,
        'title': 'إنشاء طلب شراء جديد'
    }

    return render(request, 'Purchase_orders/purchase_request_form.html', context)

@login_required
@purchase_module_permission_required('purchase_items', 'add')
def add_purchase_request_item(request, pk):
    """إضافة عنصر إلى طلب الشراء"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    if request.method == 'POST':
        form = PurchaseRequestItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_request = purchase_request
            item.save()
            messages.success(request, 'تمت إضافة العنصر بنجاح')
            return redirect('Purchase_orders:purchase_request_detail', pk=purchase_request.pk)
    else:
        form = PurchaseRequestItemForm()

    context = {
        'form': form,
        'purchase_request': purchase_request,
        'title': 'إضافة عنصر لطلب الشراء'
    }

    return render(request, 'Purchase_orders/purchase_request_item_form.html', context)

@login_required
@staff_member_required
@purchase_module_permission_required('approvals', 'edit')
def approve_purchase_request(request, pk):
    """الموافقة على طلب الشراء"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    if request.method == 'POST':
        form = PurchaseRequestApprovalForm(request.POST, instance=purchase_request)
        if form.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.approved_by = request.user
            purchase_request.approval_date = timezone.now()
            purchase_request.save()

            # تحديث حالة جميع العناصر لتتماشى مع حالة الطلب
            if purchase_request.status == 'approved':
                purchase_request.items.all().update(status='approved')
            elif purchase_request.status == 'rejected':
                purchase_request.items.all().update(status='rejected')

            messages.success(request, f'تم تحديث حالة طلب الشراء إلى {purchase_request.get_status_display()}')
            return redirect('Purchase_orders:purchase_request_detail', pk=purchase_request.pk)
    else:
        form = PurchaseRequestApprovalForm(instance=purchase_request)

    context = {
        'form': form,
        'purchase_request': purchase_request,
        'title': f'مراجعة طلب الشراء #{purchase_request.request_number}'
    }

    return render(request, 'Purchase_orders/purchase_request_approval_form.html', context)

@login_required
@purchase_module_permission_required('purchase_items', 'add')
def transfer_product_to_purchase_request(request):
    """ترحيل صنف إلى طلب شراء"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        action = data.get('action')  # 'add' or 'remove'

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'معرف المنتج غير محدد'}, status=400)

        product = get_object_or_404(TblProducts, product_id=product_id)

        # التحقق من وجود طلب شراء قيد الانتظار
        pending_request = PurchaseRequest.objects.filter(status='pending').first()

        if not pending_request and action == 'add':
            # إنشاء طلب شراء جديد إذا لم يكن هناك طلب قيد الانتظار
            request_number = f"PR-{uuid.uuid4().hex[:8].upper()}"
            pending_request = PurchaseRequest.objects.create(
                request_number=request_number,
                requested_by=request.user,
                status='pending'
            )

        if action == 'add':
            # التحقق من أن المنتج ليس موجودًا بالفعل في طلب الشراء
            existing_item = PurchaseRequestItem.objects.filter(
                purchase_request=pending_request,
                product=product
            ).first()

            if existing_item:
                return JsonResponse({
                    'status': 'error',
                    'message': 'هذا الصنف موجود بالفعل في طلب الشراء'
                }, status=400)

            # تحديد الكمية المطلوبة بناءً على الفرق بين الحد الأدنى والكمية الحالية
            quantity_needed = 0
            if product.minimum_threshold and product.qte_in_stock is not None:
                if product.qte_in_stock < product.minimum_threshold:
                    quantity_needed = product.minimum_threshold - product.qte_in_stock
                    if quantity_needed <= 0:
                        quantity_needed = product.minimum_threshold  # الحد الأدنى على الأقل

            # إنشاء عنصر طلب الشراء
            item = PurchaseRequestItem.objects.create(
                purchase_request=pending_request,
                product=product,
                quantity_requested=quantity_needed if quantity_needed > 0 else 1,
                status='pending'
            )

            return JsonResponse({
                'status': 'success',
                'message': 'تمت إضافة الصنف إلى طلب الشراء',
                'request_id': pending_request.id,
                'item_id': item.id
            })

        elif action == 'remove':
            # البحث عن العنصر في طلبات الشراء المعلقة
            item = PurchaseRequestItem.objects.filter(
                purchase_request__status='pending',
                product=product,
                status='pending'
            ).first()

            if not item:
                return JsonResponse({
                    'status': 'error',
                    'message': 'لم يتم العثور على الصنف في طلبات الشراء المعلقة'
                }, status=404)

            # حذف العنصر من طلب الشراء
            request_id = item.purchase_request.id
            item_id = item.id
            item.delete()

            return JsonResponse({
                'status': 'success',
                'message': 'تمت إزالة الصنف من طلب الشراء',
                'request_id': request_id,
                'item_id': item_id
            })

        return JsonResponse({'status': 'error', 'message': 'إجراء غير معروف'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'مسموح فقط بطلبات POST'}, status=405)

@login_required
@purchase_module_permission_required('purchase_items', 'view')
def check_product_in_purchase_request(request, product_id):
    """التحقق مما إذا كان المنتج موجودًا بالفعل في طلب شراء معلق"""
    product = get_object_or_404(TblProducts, product_id=product_id)

    # التحقق من وجود المنتج في طلب شراء معلق
    item = PurchaseRequestItem.objects.filter(
        purchase_request__status__in=['pending', 'approved'],
        product=product
    ).first()

    if item:
        return JsonResponse({
            'in_purchase_request': True,
            'status': item.status,
            'request_status': item.purchase_request.status,
            'request_id': item.purchase_request.id
        })

    return JsonResponse({'in_purchase_request': False})
