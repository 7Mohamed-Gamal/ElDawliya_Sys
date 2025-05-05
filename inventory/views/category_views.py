"""
Category views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Category
from inventory.forms import CategoryForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'view')
class CategoryListView(ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'add')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'edit')
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'delete')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')

@login_required
@inventory_class_permission_required('categories', 'add')
@csrf_exempt
def category_add_ajax(request):
    """
    إضافة تصنيف جديد عبر AJAX
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Received category_add_ajax request: {request.method}")

    if request.method == 'POST':
        try:
            # Log request headers and body for debugging
            logger.info(f"Request headers: {request.headers}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")

            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')

            logger.info(f"Parsed data - name: {name}, description: {description}")

            if not name:
                logger.warning("Category name is required but was not provided")
                return JsonResponse({'success': False, 'error': 'اسم التصنيف مطلوب'})

            # Check if category with this name already exists
            existing_category = Category.objects.filter(name=name).first()
            if existing_category:
                logger.info(f"Category with name '{name}' already exists with ID: {existing_category.id}")
                return JsonResponse({
                    'success': True,
                    'category_id': existing_category.id,
                    'name': existing_category.name,
                    'message': 'التصنيف موجود بالفعل'
                })

            # إنشاء تصنيف جديد
            category = Category.objects.create(
                name=name,
                description=description
            )

            logger.info(f"Created new category with ID: {category.id}, name: {category.name}")

            return JsonResponse({
                'success': True,
                'category_id': category.id,
                'name': category.name
            })
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'success': False, 'error': f'خطأ في تحليل البيانات: {str(e)}'})
        except Exception as e:
            logger.error(f"Error in category_add_ajax: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    logger.warning(f"Unsupported request method: {request.method}")
    return JsonResponse({'success': False, 'error': 'طريقة الطلب غير مدعومة'})
