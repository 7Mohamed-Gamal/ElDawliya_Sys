"""
API views for the inventory application.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from inventory.models_local import Product, Category, Unit, Supplier, Customer, Department

@login_required
def search_products(request):
    """البحث عن المنتجات بالاسم أو الرمز أو التصنيف"""
    search_term = request.GET.get('term', '')
    category_id = request.GET.get('category', '')
    
    if not search_term and not category_id:
        return JsonResponse({'results': []})
    
    query = Q()
    
    if search_term:
        query |= Q(name__icontains=search_term)
        query |= Q(product_id__icontains=search_term)
    
    if category_id:
        query &= Q(category_id=category_id)
    
    products = Product.objects.filter(query)[:20]
    
    results = []
    for product in products:
        unit_name = product.unit.name if product.unit else ''
        unit_symbol = product.unit.symbol if product.unit else ''
        
        results.append({
            'id': product.product_id,
            'text': f"{product.name} ({product.product_id})",
            'name': product.name,
            'product_id': product.product_id,
            'quantity': product.quantity,
            'unit_price': product.unit_price,
            'unit': unit_name,
            'unit_symbol': unit_symbol,
            'category': product.category.name if product.category else '',
            'location': product.location or '',
        })
    
    return JsonResponse({'results': results})

@login_required
def get_product_details(request, product_id):
    """الحصول على تفاصيل منتج محدد"""
    try:
        product = get_object_or_404(Product, product_id=product_id)
        
        unit_name = product.unit.name if product.unit else ''
        unit_symbol = product.unit.symbol if product.unit else ''
        
        data = {
            'id': product.id,
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'category': product.category.name if product.category else '',
            'category_id': product.category.id if product.category else None,
            'unit': unit_name,
            'unit_symbol': unit_symbol,
            'unit_id': product.unit.id if product.unit else None,
            'quantity': product.quantity,
            'initial_quantity': product.initial_quantity,
            'minimum_threshold': product.minimum_threshold,
            'unit_price': product.unit_price,
            'location': product.location,
            'notes': product.notes,
            'success': True
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_categories(request):
    """الحصول على قائمة التصنيفات"""
    categories = Category.objects.all().order_by('name')
    data = [{'id': category.id, 'name': category.name} for category in categories]
    return JsonResponse({'categories': data})

@login_required
def get_units(request):
    """الحصول على قائمة وحدات القياس"""
    units = Unit.objects.all().order_by('name')
    data = [{'id': unit.id, 'name': unit.name, 'symbol': unit.symbol} for unit in units]
    return JsonResponse({'units': data})

@login_required
def get_suppliers(request):
    """الحصول على قائمة الموردين"""
    suppliers = Supplier.objects.all().order_by('name')
    data = [{'id': supplier.id, 'name': supplier.name} for supplier in suppliers]
    return JsonResponse({'suppliers': data})

@login_required
def get_customers(request):
    """الحصول على قائمة العملاء"""
    customers = Customer.objects.all().order_by('name')
    data = [{'id': customer.id, 'name': customer.name} for customer in customers]
    return JsonResponse({'customers': data})

@login_required
def get_departments(request):
    """الحصول على قائمة الأقسام"""
    departments = Department.objects.all().order_by('name')
    data = [{'id': department.id, 'name': department.name} for department in departments]
    return JsonResponse({'departments': data})
