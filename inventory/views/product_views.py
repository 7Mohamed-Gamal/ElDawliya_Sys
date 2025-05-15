"""
Product views for the inventory application.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Product, Category, Unit
from inventory.forms import ProductForm

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'view')
class ProductListView(ListView):
    """عرض قائمة الأصناف"""
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        stock_status = self.request.GET.get('stock_status', '')

        if search_query:
            queryset = queryset.filter(
                Q(product_id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        if category:
            queryset = queryset.filter(category__id=category)

        if stock_status == 'low':
            # تحت الحد الأدنى - كمية أقل من الحد الأدنى
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            # نفذت الكمية - الكمية تساوي صفر
            queryset = queryset.filter(quantity=0)
        elif stock_status == 'normal':
            # متوفر - كمية أكبر من الحد الأدنى (وليس مساوي له)
            queryset = queryset.filter(
                Q(quantity__gt=F('minimum_threshold')) | Q(minimum_threshold=0),
                quantity__gt=0
            )
        elif stock_status == 'equal':
            # مساوى الحد الأدنى - كمية تساوي الحد الأدنى بالضبط
            queryset = queryset.filter(
                quantity=F('minimum_threshold'),
                minimum_threshold__gt=0
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # حساب إحصائيات المخزون
        # مساوي الحد الأدنى
        equal_stock_count = Product.objects.filter(
            quantity=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        
        # تحت الحد الأدنى
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        
        # نفذت الكمية
        out_of_stock = Product.objects.filter(quantity=0).count()
        
        # المتوفر (كمية أكبر من الحد الأدنى، ليس مساوي له)
        normal_stock_count = Product.objects.filter(
            Q(quantity__gt=F('minimum_threshold')) | Q(minimum_threshold=0),
            quantity__gt=0
        ).count()
        
        context['equal_stock_count'] = equal_stock_count
        context['low_stock_count'] = low_stock_count
        context['out_of_stock'] = out_of_stock
        context['normal_stock_count'] = normal_stock_count
        context['title'] = 'قائمة الأصناف'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'add')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

    def post(self, request, *args, **kwargs):
        """
        معالجة طلب POST لإضافة منتج جديد
        """
        print("="*50)
        print("PRODUCT CREATE VIEW - POST METHOD - SIMPLIFIED")
        print("="*50)
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")

        # التحقق من وجود البيانات الأساسية
        if not request.POST.get('product_id') or not request.POST.get('name'):
            print("ERROR: Missing required fields")
            messages.error(request, 'يجب إدخال رقم الصنف واسم الصنف')
            return self.form_invalid(self.get_form())

        # محاولة معالجة النموذج
        form = self.get_form()
        if form.is_valid():
            print("Form is valid, proceeding to form_valid")
            return self.form_valid(form)
        else:
            print("Form is invalid")
            print("Form errors:", form.errors)
            messages.error(request, 'يوجد أخطاء في النموذج، يرجى التحقق من البيانات المدخلة')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add categories for the form
        context['categories'] = Category.objects.all()
        # Add units for the form
        context['units'] = Unit.objects.all()
        # Add page title
        context['page_title'] = 'إضافة صنف جديد'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        """
        تنفيذ عملية حفظ المنتج بعد التحقق من صحة النموذج
        """
        try:
            # طباعة بيانات النموذج للتشخيص
            print("="*50)
            print("PRODUCT FORM SUBMISSION - SIMPLIFIED")
            print("="*50)
            print("Form data:", self.request.POST)
            print("Form cleaned data:", form.cleaned_data)

            # التحقق من وجود البيانات الأساسية
            product_id = form.cleaned_data.get('product_id')
            name = form.cleaned_data.get('name')

            if not product_id or not name:
                raise ValueError("يجب إدخال رقم الصنف واسم الصنف")

            # تعيين الرصيد الحالي من الرصيد الافتتاحي والعكس
            initial_quantity = form.cleaned_data.get('initial_quantity', 0)
            current_quantity = form.cleaned_data.get('quantity', 0)

            # إذا كان الرصيد الافتتاحي موجود ولكن الرصيد الحالي غير موجود
            if initial_quantity and not current_quantity:
                print(f"Setting current quantity from initial: {initial_quantity}")
                form.instance.quantity = initial_quantity
            # إذا كان الرصيد الحالي موجود ولكن الرصيد الافتتاحي غير موجود
            elif current_quantity and not initial_quantity:
                print(f"Setting initial quantity from current: {current_quantity}")
                form.instance.initial_quantity = current_quantity
            # إذا كانت القيمتان مختلفتان، نستخدم الرصيد الافتتاحي
            elif initial_quantity != current_quantity:
                print(f"Values differ - Setting both to initial: {initial_quantity}")
                form.instance.quantity = initial_quantity

            print(f"Final values - Initial: {form.instance.initial_quantity}, Current: {form.instance.quantity}")

            # معالجة التصنيف الجديد إذا تم إدخاله
            new_category = self.request.POST.get('new_category')
            new_category_name = self.request.POST.get('new_category_name')

            if new_category == 'true' and new_category_name:
                print(f"Creating new category: {new_category_name}")
                category = Category.objects.create(
                    name=new_category_name,
                    description=self.request.POST.get('new_category_description', '')
                )
                form.instance.category = category

            # معالجة وحدة القياس الجديدة إذا تم إدخالها
            new_unit = self.request.POST.get('new_unit')
            new_unit_name = self.request.POST.get('new_unit_name')
            unit_value = self.request.POST.get('unit')

            print(f"Unit value: {unit_value}, New unit: {new_unit}, New unit name: {new_unit_name}")

            if new_unit == 'true' and new_unit_name:
                print(f"Creating new unit: {new_unit_name}")
                unit = Unit.objects.create(
                    name=new_unit_name,
                    symbol=self.request.POST.get('new_unit_symbol', '')
                )
                form.instance.unit = unit
            elif unit_value and unit_value != 'new':
                try:
                    unit_id = int(unit_value)
                    unit = Unit.objects.get(id=unit_id)
                    form.instance.unit = unit
                except (ValueError, Unit.DoesNotExist):
                    print(f"Invalid unit ID: {unit_value}")

            # إنشاء رقم منتج تلقائي إذا لم يتم توفيره
            if not form.instance.product_id:
                form.instance.product_id = f"P{timezone.now().strftime('%Y%m%d%H%M%S')}"

            # حفظ المنتج
            print("Saving product...")
            product = form.save(commit=False)
            print(f"Product before save: {product.product_id} - {product.name}")
            product.save()
            print(f"Product saved successfully: {product.product_id} - {product.name}")

            # إظهار رسالة نجاح
            messages.success(self.request, f'تم إضافة الصنف "{name}" بنجاح')

            return super().form_valid(form)
        except Exception as e:
            print(f"ERROR in form_valid: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'حدث خطأ أثناء حفظ الصنف: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'edit')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add categories for the form
        context['categories'] = Category.objects.all()
        # Add units for the form
        context['units'] = Unit.objects.all()
        # Add page title
        context['page_title'] = 'تعديل الصنف'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        # Print all form data for debugging
        print("Form data (update):", self.request.POST)
        print("Form cleaned data (update):", form.cleaned_data)

        # Check if we need to create a new category
        new_category = form.cleaned_data.get('new_category')
        new_category_name = form.cleaned_data.get('new_category_name')

        print(f"New category: {new_category}, Name: {new_category_name}")

        if new_category == 'true' and new_category_name:
            # Create new category
            category = Category.objects.create(
                name=new_category_name,
                description=form.cleaned_data.get('new_category_description', '')
            )
            # Set the new category to the product
            form.instance.category = category
            print(f"Created new category: {category}")

        # Check if we need to create a new unit
        new_unit = form.cleaned_data.get('new_unit')
        new_unit_name = form.cleaned_data.get('new_unit_name')
        new_unit_symbol = form.cleaned_data.get('new_unit_symbol')

        print(f"New unit (update): {new_unit}, Name: {new_unit_name}, Symbol: {new_unit_symbol}")

        # Check if unit is "new" in the dropdown
        unit_value = self.request.POST.get('unit')
        print(f"Unit dropdown value (update): {unit_value}")

        # If the unit dropdown has "new" selected but the hidden field wasn't set properly
        if unit_value == "new" or new_unit == 'true':
            # Get the unit name and symbol from the request directly
            direct_unit_name = self.request.POST.get('new_unit_name')
            direct_unit_symbol = self.request.POST.get('new_unit_symbol')
            print(f"Direct unit name (update): {direct_unit_name}, Symbol: {direct_unit_symbol}")

            if direct_unit_name:
                new_unit = 'true'
                new_unit_name = direct_unit_name
                new_unit_symbol = direct_unit_symbol
                form.cleaned_data['new_unit'] = 'true'
                form.cleaned_data['new_unit_name'] = direct_unit_name
                form.cleaned_data['new_unit_symbol'] = direct_unit_symbol

            # Create new unit
            unit = Unit.objects.create(
                name=new_unit_name or "وحدة جديدة",
                symbol=new_unit_symbol or ""
            )
            # Set the new unit to the product
            form.instance.unit = unit
            print(f"Created new unit (update): {unit}")
        elif unit_value and unit_value != "":
            # If a regular unit is selected
            try:
                unit_id = int(unit_value)
                unit = Unit.objects.get(id=unit_id)
                form.instance.unit = unit
                print(f"Selected existing unit (update): {unit}")
            except (ValueError, Unit.DoesNotExist):
                print(f"Invalid unit ID (update): {unit_value}")
        else:
            # No unit selected
            form.instance.unit = None
            print("No unit selected (update)")

        messages.success(self.request, 'تم تعديل الصنف بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'delete')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')
