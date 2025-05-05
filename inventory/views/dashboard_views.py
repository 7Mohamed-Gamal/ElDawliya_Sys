"""
Dashboard views for the inventory application.
"""
from django.shortcuts import render
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from inventory.decorators import inventory_module_permission_required
from inventory.models_local import Product, Voucher

@login_required
@inventory_module_permission_required('dashboard', 'view')
def dashboard(request):
    """عرض لوحة تحكم المخزن"""
    try:
        # إحصائيات المنتجات
        total_products = Product.objects.count()

        # الأصناف التي تحت الحد الأدنى
        low_stock_products = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        )
        low_stock_count = low_stock_products.count()

        # الأصناف غير المتوفرة
        out_of_stock_count = Product.objects.filter(quantity=0).count()

        # إحصائيات الأذونات
        total_vouchers = Voucher.objects.count()

        # آخر الأذونات
        recent_vouchers = Voucher.objects.all().order_by('-date')[:5]

        # الأصناف التي تحتاج إلى طلب شراء
        purchase_needed_products = Product.objects.filter(
            quantity__lte=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).exclude(
            purchase_requests__status='pending'
        )[:5]

        context = {
            'total_products': total_products,
            'low_stock_products': low_stock_products[:5],  # أول 5 منتجات فقط للعرض
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_vouchers': total_vouchers,
            'recent_vouchers': recent_vouchers,
            'purchase_needed_products': purchase_needed_products
        }

        return render(request, 'inventory/dashboard.html', context)
    except Exception as e:
        # في حالة وجود خطأ في الاتصال بقاعدة البيانات أو أي خطأ آخر
        messages.error(request, f'حدث خطأ: {str(e)}')
        context = {
            'error_message': str(e),
            'total_products': 0,
            'low_stock_products': [],
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'total_vouchers': 0,
            'recent_vouchers': []
        }
        return render(request, 'inventory/dashboard.html', context)

@login_required
@csrf_exempt
@inventory_module_permission_required('dashboard', 'view')
def check_low_stock(request):
    """Check for low stock items and return them as JSON"""
    low_stock_products = Product.objects.filter(
        quantity__lt=F('minimum_threshold'),
        minimum_threshold__gt=0
    ).values('product_id', 'name', 'quantity', 'minimum_threshold')

    return JsonResponse(list(low_stock_products), safe=False)
