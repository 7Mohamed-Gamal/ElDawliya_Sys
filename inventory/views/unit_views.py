"""
Unit views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Unit
from inventory.forms import UnitForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'view')
class UnitListView(ListView):
    model = Unit
    template_name = 'inventory/unit_list.html'
    context_object_name = 'units'

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'add')
class UnitCreateView(CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'inventory/unit_form.html'
    success_url = reverse_lazy('inventory:unit_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'edit')
class UnitUpdateView(UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'inventory/unit_form.html'
    success_url = reverse_lazy('inventory:unit_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'delete')
class UnitDeleteView(DeleteView):
    model = Unit
    template_name = 'inventory/unit_confirm_delete.html'
    success_url = reverse_lazy('inventory:unit_list')

@login_required
@inventory_class_permission_required('units', 'add')
@csrf_exempt
def unit_add_ajax(request):
    """
    إضافة وحدة قياس جديدة عبر AJAX
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Received unit_add_ajax request: {request.method}")

    if request.method == 'POST':
        try:
            # Log request headers and body for debugging
            logger.info(f"Request headers: {request.headers}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")

            data = json.loads(request.body)
            name = data.get('name')
            symbol = data.get('symbol', '')

            logger.info(f"Parsed data - name: {name}, symbol: {symbol}")

            if not name:
                logger.warning("Unit name is required but was not provided")
                return JsonResponse({'success': False, 'error': 'اسم وحدة القياس مطلوب'})

            # Check if unit with this name already exists
            existing_unit = Unit.objects.filter(name=name).first()
            if existing_unit:
                logger.info(f"Unit with name '{name}' already exists with ID: {existing_unit.id}")
                return JsonResponse({
                    'success': True,
                    'unit_id': existing_unit.id,
                    'name': existing_unit.name,
                    'symbol': existing_unit.symbol,
                    'message': 'وحدة القياس موجودة بالفعل'
                })

            # إنشاء وحدة قياس جديدة
            unit = Unit.objects.create(
                name=name,
                symbol=symbol
            )

            logger.info(f"Created new unit with ID: {unit.id}, name: {unit.name}, symbol: {unit.symbol}")

            return JsonResponse({
                'success': True,
                'unit_id': unit.id,
                'name': unit.name,
                'symbol': unit.symbol
            })
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'success': False, 'error': f'خطأ في تحليل البيانات: {str(e)}'})
        except Exception as e:
            logger.error(f"Error in unit_add_ajax: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    logger.warning(f"Unsupported request method: {request.method}")
    return JsonResponse({'success': False, 'error': 'طريقة الطلب غير مدعومة'})
