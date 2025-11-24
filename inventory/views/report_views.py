"""
Report views for the inventory application.
"""
from django.shortcuts import render
from django.db.models import F, Sum, Count, Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from inventory.decorators import inventory_module_permission_required
from inventory.models_local import Product, Voucher, VoucherItem, Category

@login_required
@inventory_module_permission_required('stock_report', 'view')
def stock_report(request):
    """تقرير المخزون"""
    # الحصول على معايير التصفية
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    search_query = request.GET.get('search', '')

    # بناء الاستعلام الأساسي
    products = Product.objects.all()

    # تطبيق معايير التصفية
    if category_id:
        products = products.filter(category_id=category_id)

    if stock_status == 'low':
        products = products.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        )
    elif stock_status == 'out':
        products = products.filter(quantity=0)

    if search_query:
        products = products.filter(
            Q(product_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # ترتيب النتائج
    products = products.order_by('category__name', 'name')

    # الحصول على جميع التصنيفات للفلتر
    categories = Category.objects.all()

    # إحصائيات إضافية
    total_products = products.count()
    total_value = sum(product.quantity * (product.unit_price or 0) for product in products)
    low_stock_count = products.filter(
        quantity__lt=F('minimum_threshold'),
        minimum_threshold__gt=0
    ).count()
    out_of_stock_count = products.filter(quantity=0).count()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'stock_status': stock_status,
        'search_query': search_query,
        'total_products': total_products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'page_title': 'تقرير المخزون'
    }

    return render(request, 'inventory/reports/stock_report.html', context)

@login_required
@inventory_module_permission_required('stock_report', 'view')
def movement_report(request):
    """تقرير حركة الأصناف"""
    # الحصول على معايير التصفية
    product_id = request.GET.get('product_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    voucher_type = request.GET.get('voucher_type', '')

    # بناء الاستعلام الأساسي
    voucher_items = VoucherItem.objects.select_related('voucher', 'product')

    # تطبيق معايير التصفية
    if product_id:
        voucher_items = voucher_items.filter(product__product_id=product_id)

    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            voucher_items = voucher_items.filter(voucher__date__gte=date_from)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            voucher_items = voucher_items.filter(voucher__date__lte=date_to)
        except (ValueError, TypeError):
            pass

    if voucher_type:
        voucher_items = voucher_items.filter(voucher__voucher_type=voucher_type)

    # ترتيب النتائج
    voucher_items = voucher_items.order_by('-voucher__date', '-voucher__created_at')

    # الحصول على جميع المنتجات للفلتر
    products = Product.objects.all().order_by('name')

    # إحصائيات إضافية
    total_items = voucher_items.count()

    # إجمالي الكميات المضافة والمنصرفة
    total_added = voucher_items.filter(
        Q(voucher__voucher_type='إذن اضافة') | Q(voucher__voucher_type='اذن مرتجع عميل')
    ).aggregate(total=Sum('quantity_added'))['total'] or 0

    total_disbursed = voucher_items.filter(
        Q(voucher__voucher_type='إذن صرف') | Q(voucher__voucher_type='إذن مرتجع مورد')
    ).aggregate(total=Sum('quantity_disbursed'))['total'] or 0

    context = {
        'voucher_items': voucher_items,
        'products': products,
        'selected_product': product_id,
        'date_from': date_from if isinstance(date_from, str) else date_from.strftime('%Y-%m-%d') if date_from else '',
        'date_to': date_to if isinstance(date_to, str) else date_to.strftime('%Y-%m-%d') if date_to else '',
        'voucher_type': voucher_type,
        'total_items': total_items,
        'total_added': total_added,
        'total_disbursed': total_disbursed,
        'page_title': 'تقرير حركة الأصناف'
    }

    return render(request, 'inventory/reports/movement_report.html', context)

@login_required
@inventory_module_permission_required('stock_report', 'view')
def voucher_report(request):
    """تقرير الأذونات"""
    # الحصول على معايير التصفية
    voucher_type = request.GET.get('voucher_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    supplier_id = request.GET.get('supplier_id', '')
    department_id = request.GET.get('department_id', '')
    customer_id = request.GET.get('customer_id', '')

    # بناء الاستعلام الأساسي
    vouchers = Voucher.objects.all()

    # تطبيق معايير التصفية
    if voucher_type:
        vouchers = vouchers.filter(voucher_type=voucher_type)

    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__gte=date_from)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__lte=date_to)
        except (ValueError, TypeError):
            pass

    if supplier_id:
        vouchers = vouchers.filter(supplier_id=supplier_id)

    if department_id:
        vouchers = vouchers.filter(department_id=department_id)

    if customer_id:
        vouchers = vouchers.filter(customer_id=customer_id)

    # ترتيب النتائج
    vouchers = vouchers.order_by('-date', '-created_at')

    # إحصائيات إضافية
    total_vouchers = vouchers.count()
    vouchers_by_type = vouchers.values('voucher_type').annotate(count=Count('id'))

    # إجمالي قيمة الأذونات
    total_value = 0
    for voucher in vouchers:
        for item in voucher.items.all():
            if item.total_price:
                total_value += item.total_price

    context = {
        'vouchers': vouchers,
        'voucher_type': voucher_type,
        'date_from': date_from if isinstance(date_from, str) else date_from.strftime('%Y-%m-%d') if date_from else '',
        'date_to': date_to if isinstance(date_to, str) else date_to.strftime('%Y-%m-%d') if date_to else '',
        'supplier_id': supplier_id,
        'department_id': department_id,
        'customer_id': customer_id,
        'total_vouchers': total_vouchers,
        'vouchers_by_type': vouchers_by_type,
        'total_value': total_value,
        'page_title': 'تقرير الأذونات'
    }

    return render(request, 'inventory/reports/voucher_report.html', context)
