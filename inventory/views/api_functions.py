"""
API functions for the inventory application.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from inventory.models_local import Product

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

                # إعداد بيانات المنتج للإرجاع
                product_data = {
                    'id': product.product_id,
                    'name': product.name,
                    'quantity': float(product.quantity),
                    'unit_name': product.unit.name if product.unit else '',
                    'unit_price': float(product.unit_price),
                    'category': product.category.name if product.category else '',
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
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            search_term = data.get('search_term', '').strip()

            if not search_term:
                # إرجاع قائمة فارغة إذا كان مصطلح البحث فارغًا
                return JsonResponse({'success': True, 'products': []})

            # البحث في المنتجات بناءً على الكود أو الاسم أو التصنيف
            products = Product.objects.filter(
                Q(product_id__icontains=search_term) |
                Q(name__icontains=search_term) |
                Q(category__name__icontains=search_term)
            ).order_by('name')[:20]  # تحديد النتائج بـ 20 منتج كحد أقصى

            # تحويل نتائج البحث إلى قائمة
            products_list = []
            for product in products:
                products_list.append({
                    'id': product.product_id,
                    'name': product.name,
                    'quantity': float(product.quantity),
                    'unit_name': product.unit.name if product.unit else '',
                    'unit_price': float(product.unit_price),
                    'category': product.category.name if product.category else '',
                })

            return JsonResponse({'success': True, 'products': products_list})

        except Exception as e:
            print(f"Error in search_products_api: {str(e)}")
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'طريقة الطلب غير مدعومة'})
