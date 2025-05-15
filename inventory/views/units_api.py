"""
API functions for unit operations in the inventory application.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from inventory.models_local import Unit

@login_required
def get_units_api(request):
    """
    نقطة نهاية API لجلب قائمة وحدات القياس للاستخدام في الفلترة
    API endpoint to fetch units for filtering
    """
    try:
        # جلب جميع الوحدات مرتبة حسب الاسم
        units = Unit.objects.all().order_by('name')
        
        # تحويل النتائج إلى قائمة
        units_list = []
        for unit in units:
            units_list.append({
                'id': unit.id,
                'name': unit.name,
                'symbol': unit.symbol if hasattr(unit, 'symbol') else '',
            })
        
        return JsonResponse({'success': True, 'units': units_list})
    
    except Exception as e:
        print(f"Error in get_units_api: {str(e)}")
        return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
