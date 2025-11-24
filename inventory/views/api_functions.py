"""
API functions for the inventory application.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from inventory.models_local import Product, Category, Unit

@login_required
@csrf_exempt
def product_details_api(request):
    """
    نقطة نهاية API لجلب بيانات المنتج بناءً على كود المنتج
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_code = data.get('product_code')

            if not product_code:
                return JsonResponse({'success': False, 'message': 'كود المنتج مطلوب'})

            try:
                # محاولة العثور على المنتج بالكود المحدد
                product = Product.objects.get(product_id=product_code)

                # إعداد بيانات المنتج للإرجاع بشكل مفصل
                product_data = {
                    'id': product.product_id,
                    'name': product.name,
                    'description': product.description or '',
                    'category': product.category.name if product.category else '',
                    'category_id': product.category.id if product.category else None,
                    'unit_name': product.unit.name if product.unit else '',
                    'unit_id': product.unit.id if product.unit else None,
                    'initial_quantity': float(product.initial_quantity),
                    'quantity': float(product.quantity),
                    'minimum_threshold': float(product.minimum_threshold),
                    'maximum_threshold': float(product.maximum_threshold),
                    'unit_price': float(product.unit_price),
                    'location': product.location or '',
                }

                return JsonResponse({'success': True, 'product': product_data})
            except Product.DoesNotExist:
                # إذا لم يتم العثور على المنتج، نرجع رسالة خطأ
                return JsonResponse({'success': False, 'message': 'المنتج غير موجود'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'بيانات JSON غير صالحة'})
        except Exception as e:
            # إضافة معالجة أفضل للأخطاء
            print(f"Error in product_details_api: {str(e)}")
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'طريقة الطلب غير مدعومة'})


@login_required
@csrf_exempt
def search_products_api(request):
    """
    نقطة نهاية API للبحث المرن عن المنتجات بالاسم أو الكود أو التصنيف
    مع دعم الفلترة حسب التصنيف وحالة المخزون
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            search_term = data.get('search_term', '').strip()
            category_id = data.get('category_id', '').strip()
            stock_status = data.get('stock_status', '').strip()

            # بناء الاستعلام الأساسي
            query = Product.objects.all()

            # تطبيق فلتر البحث بالنص إذا تم توفيره
            if search_term:
                query = query.filter(
                    Q(product_id__icontains=search_term) |
                    Q(name__icontains=search_term) |
                    Q(category__name__icontains=search_term)
                )

            # تطبيق فلتر التصنيف إذا تم توفيره
            if category_id:
                query = query.filter(category_id=category_id)

            # تطبيق فلتر حالة المخزون إذا تم توفيره
            if stock_status == 'available':
                query = query.filter(quantity__gt=0)
            elif stock_status == 'out':
                query = query.filter(quantity__lte=0)

            # ترتيب النتائج وتحديد العدد الأقصى
            products = query.order_by('name')[:50]  # زيادة الحد الأقصى إلى 50

            # تحويل نتائج البحث إلى قائمة
            products_list = []
            for product in products:
                products_list.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'quantity': float(product.quantity),
                    'unit_name': product.unit.name if product.unit else '',
                    'unit_price': float(product.unit_price),
                    'category_name': product.category.name if product.category else '',
                    'category_id': product.category.id if product.category else '',
                    'minimum_threshold': float(product.minimum_threshold) if product.minimum_threshold else 0,
                })

            return JsonResponse({'success': True, 'products': products_list})

        except Exception as e:
            print(f"Error in search_products_api: {str(e)}")
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'طريقة الطلب غير مدعومة'})


@login_required
def get_categories_api(request):
    """
    نقطة نهاية API لجلب قائمة التصنيفات للاستخدام في الفلترة
    """
    try:
        # جلب جميع التصنيفات مرتبة حسب الاسم
        categories = Category.objects.all().order_by('name')

        # تحويل النتائج إلى قائمة
        categories_list = []
        for category in categories:
            categories_list.append({
                'id': category.id,
                'name': category.name,
            })

        return JsonResponse({'success': True, 'categories': categories_list})

    except Exception as e:
        print(f"Error in get_categories_api: {str(e)}")
        return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})


@login_required
def get_units_api(request):
    """
    نقطة نهاية API لجلب قائمة وحدات القياس للاستخدام في الفلترة
    """
    try:
        # جلب جميع وحدات القياس مرتبة حسب الاسم
        units = Unit.objects.all().order_by('name')

        # تحويل النتائج إلى قائمة
        units_list = []
        for unit in units:
            units_list.append({
                'id': unit.id,
                'name': unit.name,
            })

        return JsonResponse({'success': True, 'units': units_list})

    except Exception as e:
        print(f"Error in get_units_api: {str(e)}")
        return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
