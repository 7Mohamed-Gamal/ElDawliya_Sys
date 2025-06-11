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

from .models import PurchaseRequest, PurchaseRequestItem, Vendor
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

            # معالجة الأصناف المختارة
            items_created = 0
            items_errors = []

            # جلب بيانات الأصناف من النموذج
            for key, value in request.POST.items():
                if key.startswith('items[') and key.endswith('][product_id]'):
                    # استخراج الفهرس من اسم الحقل
                    index = key.split('[')[1].split(']')[0]

                    product_id = value
                    quantity_key = f'items[{index}][quantity_requested]'
                    notes_key = f'items[{index}][notes]'

                    quantity_requested = request.POST.get(quantity_key, 0)
                    notes = request.POST.get(notes_key, '')

                    try:
                        # البحث عن المنتج
                        try:
                            product = TblProducts.objects.get(product_id=product_id)
                        except TblProducts.DoesNotExist:
                            # محاولة جلب من النموذج المحلي
                            from inventory.models_local import Product
                            local_product = Product.objects.get(product_id=product_id)
                            product, created = TblProducts.objects.get_or_create(
                                product_id=local_product.product_id,
                                defaults={
                                    'product_name': local_product.name,
                                    'qte_in_stock': local_product.quantity,
                                    'minimum_threshold': local_product.minimum_threshold,
                                    'maximum_threshold': local_product.maximum_threshold,
                                    'unit_price': local_product.unit_price
                                }
                            )

                        # التحقق من صحة الكمية
                        quantity_requested = float(quantity_requested)
                        if quantity_requested <= 0:
                            items_errors.append(f'كمية غير صحيحة للصنف {product.product_name}')
                            continue

                        # إنشاء عنصر طلب الشراء
                        PurchaseRequestItem.objects.create(
                            purchase_request=purchase_request,
                            product=product,
                            quantity_requested=quantity_requested,
                            notes=notes,
                            status='pending'
                        )
                        items_created += 1

                    except Exception as e:
                        items_errors.append(f'خطأ في إضافة الصنف {product_id}: {str(e)}')

            # عرض رسائل النتائج
            if items_created > 0:
                messages.success(request, f'تم إنشاء طلب الشراء بنجاح مع {items_created} صنف')
            else:
                messages.warning(request, 'تم إنشاء طلب الشراء ولكن لم يتم إضافة أي أصناف')

            if items_errors:
                for error in items_errors:
                    messages.error(request, error)

            return redirect('Purchase_orders:purchase_request_detail', pk=purchase_request.pk)
    else:
        # إنشاء رقم طلب فريد
        request_number = f"PR-{uuid.uuid4().hex[:8].upper()}"
        form = PurchaseRequestForm(initial={'request_number': request_number})

    # إضافة الموردين إلى السياق
    vendors = Vendor.objects.all()

    context = {
        'form': form,
        'vendors': vendors,
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
        # دعم كلا من JSON و form data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'تنسيق JSON غير صالح'}, status=400)
        else:
            data = request.POST

        product_id = data.get('product_id')
        action = data.get('action', 'add')  # 'add' by default

        print(f"Received request - Product ID: {product_id}, Action: {action}")

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'معرف المنتج غير محدد'}, status=400)

        try:
            try:
                # أولاً، حاول العثور على المنتج في جدول TblProducts
                product = TblProducts.objects.get(product_id=product_id)
                print(f"Found product in TblProducts: {product.product_name}")
            except TblProducts.DoesNotExist:
                # إذا لم يتم العثور على المنتج، حاول في جدول Product المحلي
                # استيراد النموذج المحلي
                from inventory.models_local import Product

                try:
                    local_product = Product.objects.get(product_id=product_id)
                    print(f"Found product in local Product model: {local_product.name}")

                    # إنشاء أو العثور على منتج مطابق في TblProducts
                    product, created = TblProducts.objects.get_or_create(
                        product_id=local_product.product_id,
                        defaults={
                            'product_name': local_product.name,
                            'qte_in_stock': local_product.quantity,
                            'minimum_threshold': local_product.minimum_threshold,
                            'maximum_threshold': local_product.maximum_threshold,
                            'unit_price': local_product.unit_price
                        }
                    )

                    if created:
                        print(f"Created new product in TblProducts based on local product: {product.product_id}")
                    else:
                        print(f"Found existing product in TblProducts: {product.product_id}")
                except Product.DoesNotExist:
                    # إذا لم يتم العثور على المنتج في كلا النموذجين
                    raise Exception(f"لم يتم العثور على المنتج برقم {product_id} في أي من قواعد البيانات")

        except Exception as e:
            error_message = f'خطأ في العثور على المنتج: {str(e)}'
            print(error_message)
            return JsonResponse({'status': 'error', 'message': error_message}, status=400)

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

            # تحديد الكمية المطلوبة من البيانات المرسلة أو حسابها تلقائيًا
            quantity_requested = data.get('quantity_requested', 0)
            notes = data.get('notes', '')

            # إذا لم يتم تحديد كمية، حساب الكمية بناءً على الفرق بين الحد الأدنى والكمية الحالية
            if quantity_requested <= 0 and product.minimum_threshold and product.qte_in_stock is not None:
                if product.qte_in_stock < product.minimum_threshold:
                    quantity_requested = product.minimum_threshold - product.qte_in_stock
                    if quantity_requested <= 0:
                        quantity_requested = product.minimum_threshold  # الحد الأدنى على الأقل

            # استخدام القيمة الافتراضية إذا ظلت الكمية صفر أو سالبة
            if quantity_requested <= 0:
                quantity_requested = 1

            # إنشاء عنصر طلب الشراء
            item = PurchaseRequestItem.objects.create(
                purchase_request=pending_request,
                product=product,
                quantity_requested=quantity_requested,
                notes=notes,
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
    try:
        try:
            # أولاً، حاول العثور على المنتج في جدول TblProducts
            product = TblProducts.objects.get(product_id=product_id)
        except TblProducts.DoesNotExist:
            # إذا لم يتم العثور على المنتج، حاول في جدول Product المحلي
            # واجلب المنتج من TblProducts
            from inventory.models_local import Product
            local_product = Product.objects.get(product_id=product_id)
            product, created = TblProducts.objects.get_or_create(
                product_id=local_product.product_id,
                defaults={
                    'product_name': local_product.name,
                    'qte_in_stock': local_product.quantity,
                    'minimum_threshold': local_product.minimum_threshold,
                    'maximum_threshold': local_product.maximum_threshold,
                    'unit_price': local_product.unit_price
                }
            )
    except Exception as e:
        return JsonResponse({
            'in_purchase_request': False,
            'error': f'لم يتم العثور على المنتج: {str(e)}'
        })

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

@login_required
@purchase_module_permission_required('purchase_requests', 'view')
def pending_approval_list(request):
    """عرض قائمة طلبات الشراء قيد الموافقة"""
    purchase_requests = PurchaseRequest.objects.filter(status='pending').order_by('-request_date')

    context = {
        'purchase_requests': purchase_requests,
        'title': 'طلبات الشراء قيد الموافقة'
    }

    return render(request, 'Purchase_orders/pending_approval_list.html', context)

@login_required
@purchase_module_permission_required('purchase_requests', 'view')
def approved_requests_list(request):
    """عرض قائمة طلبات الشراء المعتمدة"""
    purchase_requests = PurchaseRequest.objects.filter(status='approved').order_by('-approval_date')

    context = {
        'purchase_requests': purchase_requests,
        'title': 'طلبات الشراء المعتمدة'
    }

    return render(request, 'Purchase_orders/approved_requests_list.html', context)

@login_required
@purchase_module_permission_required('purchase_requests', 'view')
def rejected_requests_list(request):
    """عرض قائمة طلبات الشراء المرفوضة"""
    purchase_requests = PurchaseRequest.objects.filter(status='rejected').order_by('-approval_date')

    context = {
        'purchase_requests': purchase_requests,
        'title': 'طلبات الشراء المرفوضة'
    }

    return render(request, 'Purchase_orders/rejected_requests_list.html', context)

@login_required
@purchase_module_permission_required('purchase_requests', 'view')
def vendors_list(request):
    """عرض قائمة الموردين"""
    vendors = Vendor.objects.all()

    context = {
        'vendors': vendors,
        'title': 'قائمة الموردين'
    }

    return render(request, 'Purchase_orders/vendors_list.html', context)

@login_required
@purchase_module_permission_required('purchase_requests', 'edit')
def get_vendor_details(request, vendor_id):
    """الحصول على بيانات المورد للتعديل"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            data = {
                'id': vendor.id,
                'name': vendor.name,
                'contact_person': vendor.contact_person or '',
                'phone': vendor.phone or '',
                'email': vendor.email or '',
                'address': vendor.address or ''
            }
            return JsonResponse(data)
        except Vendor.DoesNotExist:
            return JsonResponse({'error': 'المورد غير موجود'}, status=404)

    return JsonResponse({'error': 'طلب غير صالح'}, status=400)

@login_required
@purchase_module_permission_required('purchase_requests', 'edit')
def create_vendor(request):
    """إنشاء مورد جديد"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            vendor = Vendor.objects.create(
                name=data.get('name'),
                contact_person=data.get('contact_person'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address')
            )
            return JsonResponse({
                'id': vendor.id,
                'name': vendor.name,
                'message': 'تم إنشاء المورد بنجاح'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'طلب غير صالح'}, status=400)

@login_required
@purchase_module_permission_required('purchase_requests', 'edit')
def update_vendor(request, vendor_id):
    """تحديث بيانات المورد"""
    if request.method == 'PUT' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            data = json.loads(request.body)

            vendor.name = data.get('name', vendor.name)
            vendor.contact_person = data.get('contact_person', vendor.contact_person)
            vendor.phone = data.get('phone', vendor.phone)
            vendor.email = data.get('email', vendor.email)
            vendor.address = data.get('address', vendor.address)
            vendor.save()

            return JsonResponse({
                'id': vendor.id,
                'name': vendor.name,
                'message': 'تم تحديث المورد بنجاح'
            })
        except Vendor.DoesNotExist:
            return JsonResponse({'error': 'المورد غير موجود'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'طلب غير صالح'}, status=400)

@login_required
@purchase_module_permission_required('purchase_requests', 'delete')
def delete_vendor(request, vendor_id):
    """حذف مورد"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            vendor.delete()
            return JsonResponse({'message': 'تم حذف المورد بنجاح'})
        except Vendor.DoesNotExist:
            return JsonResponse({'error': 'المورد غير موجود'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'طلب غير صالح'}, status=400)

@login_required
def delete_purchase_request(request, pk):
    """حذف طلب شراء"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    # التحقق من أن الطلب في حالة قيد الانتظار فقط
    if purchase_request.status != 'pending':
        messages.error(request, 'لا يمكن حذف طلب الشراء إلا إذا كان في حالة قيد الانتظار')
        return redirect('Purchase_orders:purchase_request_detail', pk=purchase_request.pk)

    # حفظ رقم الطلب للرسالة
    request_number = purchase_request.request_number

    if request.method == 'POST':
        # حذف الطلب (سيتم حذف العناصر تلقائيًا بسبب علاقة CASCADE)
        purchase_request.delete()

        messages.success(request, f'تم حذف طلب الشراء {request_number} بنجاح')
        return redirect('Purchase_orders:purchase_request_list')
    elif request.method == 'GET':
        # في حالة GET، يمكن أن نحذف الطلب مباشرة إذا تم النقر على زر الحذف في القائمة
        purchase_request.delete()

        messages.success(request, f'تم حذف طلب الشراء {request_number} بنجاح')
        return redirect('Purchase_orders:purchase_request_list')

    # في حالة أخرى، عرض صفحة تأكيد الحذف
    context = {
        'purchase_request': purchase_request,
        'title': f'حذف طلب الشراء #{purchase_request.request_number}'
    }

    return render(request, 'Purchase_orders/purchase_request_confirm_delete.html', context)

@login_required
@purchase_module_permission_required('reports', 'view')
def reports(request):
    """عرض تقارير طلبات الشراء"""
    # إحصائيات طلبات الشراء
    pending_requests = PurchaseRequest.objects.filter(status='pending').count()
    approved_requests = PurchaseRequest.objects.filter(status='approved').count()
    rejected_requests = PurchaseRequest.objects.filter(status='rejected').count()
    completed_requests = PurchaseRequest.objects.filter(status='completed').count()
    total_requests = PurchaseRequest.objects.count()

    # طلبات الشراء الأخيرة
    recent_requests = PurchaseRequest.objects.all().order_by('-request_date')[:10]

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'completed_requests': completed_requests,
        'total_requests': total_requests,
        'recent_requests': recent_requests,
        'title': 'تقارير طلبات الشراء'
    }

    return render(request, 'Purchase_orders/reports.html', context)

@login_required
@purchase_module_permission_required('purchase_requests', 'view')
def get_products_api(request):
    """API endpoint لجلب قطع الغيار للاستخدام في نموذج طلب الشراء"""
    try:
        # محاولة جلب البيانات من TblProducts أولاً
        products_data = []

        try:
            # جلب البيانات من TblProducts
            products = TblProducts.objects.all().order_by('product_name')

            for product in products:
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'qte_in_stock': float(product.qte_in_stock or 0),
                    'minimum_threshold': float(product.minimum_threshold or 0),
                    'maximum_threshold': float(product.maximum_threshold or 0),
                    'unit_price': float(product.unit_price or 0),
                    'cat_name': product.cat_name or '',
                    'cat_id': product.cat.cat_id if product.cat else None,
                    'unit_name': product.unit_name or '',
                    'unit_id': product.unit.unit_id if product.unit else None,
                    'location': product.location or '',
                }
                products_data.append(product_data)

        except Exception as e:
            print(f"Error fetching from TblProducts: {str(e)}")

            # إذا فشل جلب البيانات من TblProducts، جرب من النموذج المحلي
            try:
                from inventory.models_local import Product
                local_products = Product.objects.all().order_by('name')

                for product in local_products:
                    product_data = {
                        'product_id': product.product_id,
                        'product_name': product.name,
                        'name': product.name,  # إضافة حقل name للتوافق
                        'qte_in_stock': float(product.quantity or 0),
                        'quantity': float(product.quantity or 0),  # إضافة حقل quantity للتوافق
                        'minimum_threshold': float(product.minimum_threshold or 0),
                        'maximum_threshold': float(product.maximum_threshold or 0),
                        'unit_price': float(product.unit_price or 0),
                        'cat_name': product.category.name if product.category else '',
                        'category_name': product.category.name if product.category else '',  # للتوافق
                        'cat_id': product.category.id if product.category else None,
                        'category_id': product.category.id if product.category else None,  # للتوافق
                        'unit_name': product.unit.name if product.unit else '',
                        'unit_id': product.unit.id if product.unit else None,
                        'location': product.location or '',
                    }
                    products_data.append(product_data)

            except Exception as local_e:
                print(f"Error fetching from local Product model: {str(local_e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'خطأ في جلب بيانات قطع الغيار: {str(local_e)}'
                }, status=500)

        return JsonResponse({
            'success': True,
            'products': products_data,
            'results': products_data,  # للتوافق مع الكود الموجود
            'count': len(products_data)
        })

    except Exception as e:
        print(f"General error in get_products_api: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ عام: {str(e)}'
        }, status=500)
