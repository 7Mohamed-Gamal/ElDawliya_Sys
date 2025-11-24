"""
Utility views for the inventory application.
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone

from inventory.decorators import inventory_module_permission_required
from inventory.models_local import Product

@login_required
@inventory_module_permission_required('dashboard', 'view')
def debug_view(request):
    """عرض معلومات التشخيص"""
    context = {
        'page_title': 'صفحة التشخيص',
        'debug_info': {
            'total_products': Product.objects.count(),
            'low_stock_products': Product.objects.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            ).count(),
            'out_of_stock_products': Product.objects.filter(quantity=0).count(),
        }
    }
    return render(request, 'inventory/debug.html', context)

@login_required
@csrf_exempt
def check_product_exists(request):
    """التحقق من وجود منتج برقم معين"""
    product_id = request.GET.get('product_id', '')
    exists = Product.objects.filter(product_id=product_id).exists()
    return JsonResponse({'exists': exists})

@login_required
@csrf_exempt
def check_product_quantity(request):
    """التحقق من كمية منتج معين"""
    product_id = request.GET.get('product_id', '')
    requested_quantity = float(request.GET.get('quantity', 0))

    try:
        product = Product.objects.get(product_id=product_id)
        available = product.quantity >= requested_quantity
        return JsonResponse({
            'available': available,
            'current_quantity': product.quantity,
            'requested_quantity': requested_quantity
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'available': False,
            'error': 'المنتج غير موجود'
        })

# نموذج بسيط لإضافة منتج
@login_required
@inventory_module_permission_required('products', 'add')
def basic_product_add(request):
    """
    نقطة نهاية بسيطة لإضافة منتج جديد
    """
    if request.method == 'POST':
        try:
            # طباعة بيانات النموذج للتشخيص
            print("="*50)
            print("BASIC PRODUCT ADD")
            print("="*50)
            for key, value in request.POST.items():
                print(f"{key}: {value}")

            # التحقق من وجود البيانات الأساسية
            product_id = request.POST.get('product_id')
            name = request.POST.get('name')

            if not product_id or not name:
                messages.error(request, 'يجب إدخال رقم الصنف واسم الصنف')
                return render(request, 'inventory/basic_product_form.html')

            # التحقق من عدم وجود منتج بنفس الرقم
            if Product.objects.filter(product_id=product_id).exists():
                messages.error(request, f'يوجد صنف بنفس الرقم: {product_id}')
                return render(request, 'inventory/basic_product_form.html')

            # إنشاء المنتج
            initial_quantity = request.POST.get('initial_quantity', 0)
            if initial_quantity == '':
                initial_quantity = 0

            unit_price = request.POST.get('unit_price', 0)
            if unit_price == '':
                unit_price = 0

            # تحويل القيم إلى أرقام عشرية
            initial_quantity_float = float(initial_quantity)

            # إنشاء المنتج مع تعيين الرصيد الحالي والرصيد الافتتاحي بنفس القيمة
            product = Product(
                product_id=product_id,
                name=name,
                initial_quantity=initial_quantity_float,
                quantity=initial_quantity_float,
                unit_price=float(unit_price)
            )

            print(f"Creating product with initial_quantity={initial_quantity_float} and quantity={initial_quantity_float}")

            # حفظ المنتج
            product.save()
            print(f"Product saved successfully: {product.product_id} - {product.name}")

            # إظهار رسالة نجاح
            messages.success(request, f'تم إضافة الصنف "{name}" بنجاح')

            # إعادة توجيه إلى قائمة المنتجات
            return redirect('inventory:product_list')

        except Exception as e:
            print(f"ERROR in basic_product_add: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'حدث خطأ أثناء حفظ الصنف: {str(e)}')
            return render(request, 'inventory/basic_product_form.html')

    # إذا كان الطلب GET، عرض النموذج
    return render(request, 'inventory/basic_product_form.html')
