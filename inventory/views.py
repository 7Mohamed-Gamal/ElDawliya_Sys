from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, F, Sum, Count
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import csv
import codecs
import json
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.conf import global_settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_module_permission_required, inventory_class_permission_required

# استيراد النماذج المحلية
from inventory.models_local import (
    Category, Product, Supplier, Customer, Department,
    Voucher, VoucherItem, LocalSystemSettings, Unit, PurchaseRequest
)

# استيراد النماذج من ملف models.py
from inventory.models import TblInvoices as Invoice, TblInvoiceitems as InvoiceItem

# استيراد النماذج
from inventory.forms import (
    ProductForm, CustomerForm, CategoryForm, SupplierForm, DepartmentForm,
    VoucherForm, VoucherItemForm, LocalSystemSettingsForm, UnitForm, PurchaseRequestForm,
    InvoiceForm, InvoiceItemForm
)

# ------------------- Helper Functions -------------------

def get_low_stock_count():
    """
    دالة مساعدة للحصول على عدد المنتجات التي تحت الحد الأدنى
    تستخدم في العديد من الصفحات لعرض إشعارات المخزون المنخفض
    """
    return Product.objects.filter(
        quantity__lt=F('minimum_threshold'),
        minimum_threshold__gt=0
    ).count()

def get_out_of_stock_count():
    """
    دالة مساعدة للحصول على عدد المنتجات غير المتوفرة (الكمية = 0)
    """
    return Product.objects.filter(quantity=0).count()

def get_common_context():
    """
    دالة مساعدة للحصول على السياق المشترك المستخدم في معظم الصفحات
    """
    return {
        'low_stock_count': get_low_stock_count(),
        'out_of_stock_count': get_out_of_stock_count(),
    }

@login_required
@inventory_module_permission_required('dashboard', 'view')
def dashboard(request):
    """
    عرض لوحة تحكم المخزن
    تعرض إحصائيات المنتجات والأذونات والأصناف التي تحتاج إلى طلب شراء
    """
    try:
        # إحصائيات المنتجات
        total_products = Product.objects.count()

        # الأصناف التي تحت الحد الأدنى
        low_stock_products = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).select_related('category', 'unit')  # تحسين الأداء باستخدام select_related

        low_stock_count = low_stock_products.count()

        # الأصناف غير المتوفرة
        out_of_stock_count = Product.objects.filter(quantity=0).count()

        # إحصائيات الأذونات
        total_vouchers = Voucher.objects.count()

        # آخر الأذونات
        recent_vouchers = Voucher.objects.all().order_by('-date')[:5].select_related(
            'supplier', 'department', 'customer'
        )  # تحسين الأداء باستخدام select_related

        # الأصناف التي تحتاج إلى طلب شراء
        purchase_needed_products = Product.objects.filter(
            quantity__lte=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).exclude(
            purchase_requests__status='pending'
        ).select_related('category', 'unit')[:5]  # تحسين الأداء باستخدام select_related

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

# إدارة الأصناف (Products)
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
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['out_of_stock'] = Product.objects.filter(quantity=0).count()
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

# إدارة العملاء (Customers)
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

# إدارة التصنيفات (Categories)
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

# إدارة وحدات القياس (Units)
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

# إدارة الموردين (Suppliers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'add')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة مورد جديد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'edit')
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل المورد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'delete')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المورد بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الأقسام (Departments)
@method_decorator(login_required, name='dispatch')
# @inventory_class_permission_required('departments', 'view')
class DepartmentListView(ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأقسام'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'add')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة قسم جديد'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'edit')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل القسم'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل القسم بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'delete')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'inventory/department_confirm_delete.html'
    success_url = reverse_lazy('inventory:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف القسم بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الأذونات (Vouchers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'view')
class VoucherListView(ListView):
    model = Voucher
    template_name = 'inventory/voucher_list.html'
    context_object_name = 'vouchers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        voucher_type = self.request.GET.get('voucher_type', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')

        if search_query:
            queryset = queryset.filter(
                Q(voucher_number__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(department__name__icontains=search_query) |
                Q(customer__name__icontains=search_query) |
                Q(recipient__icontains=search_query)
            )

        if voucher_type:
            queryset = queryset.filter(voucher_type=voucher_type)

        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except (ValueError, TypeError):
                pass

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except (ValueError, TypeError):
                pass

        return queryset.order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأذونات'
        context['search_query'] = self.request.GET.get('search', '')
        context['voucher_type'] = self.request.GET.get('voucher_type', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')

        # إحصائيات الأذونات
        context['addition_count'] = Voucher.objects.filter(voucher_type='إذن اضافة').count()
        context['disbursement_count'] = Voucher.objects.filter(voucher_type='إذن صرف').count()
        context['client_return_count'] = Voucher.objects.filter(voucher_type='اذن مرتجع عميل').count()
        context['supplier_return_count'] = Voucher.objects.filter(voucher_type='إذن مرتجع مورد').count()

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'add')
class VoucherCreateView(CreateView):
    model = Voucher
    form_class = VoucherForm
    template_name = 'inventory/voucher_form.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Pre-set voucher type if provided in URL
        voucher_type = self.request.GET.get('type', '')
        if voucher_type and voucher_type in dict(Voucher.VOUCHER_TYPES).keys():
            form.initial['voucher_type'] = voucher_type
            form.set_required_fields(voucher_type)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Basic form context
        voucher_type = self.request.GET.get('type', '')
        if voucher_type == 'إذن اضافة':
            context['page_title'] = 'إضافة إذن اضافة جديد'
        elif voucher_type == 'إذن صرف':
            context['page_title'] = 'إضافة إذن صرف جديد'
        elif voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = 'إضافة إذن مرتجع عميل جديد'
        elif voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = 'إضافة إذن مرتجع مورد جديد'
        else:
            context['page_title'] = 'إضافة إذن جديد'

        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')

        # Add data for select dropdown options
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')

        # Add voucher type for conditional form fields
        context['voucher_type'] = voucher_type

        # Add items template context
        context['voucher_items'] = []

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

    def form_valid(self, form):
        try:
            # Save the form to create the voucher
            response = super().form_valid(form)
            voucher = self.object

            # Process the items that were submitted
            print(f"Voucher created: {voucher.voucher_number}, Type: {voucher.voucher_type}")
            print(f"POST data: {self.request.POST}")

            # Get the total number of forms from the formset management form
            total_forms = int(self.request.POST.get('form-TOTAL_FORMS', 0))
            print(f"Total forms: {total_forms}")

            # تتبع عدد العناصر التي تمت إضافتها
            items_added = 0

            # Process each form in the formset
            for i in range(total_forms):
                # Get product code and product ID from the form
                product_code = self.request.POST.get(f'form-{i}-product_code')
                product_id = self.request.POST.get(f'form-{i}-product')
                quantity = self.request.POST.get(f'form-{i}-quantity')

                print(f"Processing form {i}: product_code={product_code}, product_id={product_id}, quantity={quantity}")

                # Skip if no product ID or quantity or quantity is 0
                if not product_id or not quantity:
                    print(f"Skipping form {i}: Missing product_id or quantity")
                    continue

                try:
                    quantity_value = float(quantity)
                    if quantity_value <= 0:
                        print(f"Skipping form {i}: Quantity is zero or negative")
                        continue
                except (ValueError, TypeError):
                    print(f"Invalid quantity value: {quantity}")
                    continue

                # Get the product (first try by product_id field, then by code if that doesn't work)
                try:
                    # First attempt to get by product_id (primary key)
                    product = Product.objects.get(product_id=product_id)
                    print(f"Found product by ID: {product.name}")
                except Product.DoesNotExist:
                    try:
                        # If that fails, try using the product code
                        if product_code:
                            product = Product.objects.get(product_id=product_code)
                            print(f"Found product by code: {product.name}")
                        else:
                            print(f"Product not found with ID: {product_id}")
                            continue
                    except Product.DoesNotExist:
                        print(f"Product not found with code: {product_code}")
                        continue

                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)

                # Set the appropriate quantity field and update product quantity based on voucher type
                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    item.quantity_added = quantity_value
                    # Update product quantity - add quantity
                    product.quantity += quantity_value
                    print(f"Addition voucher: Added {quantity_value} to product quantity")
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # For disbursement vouchers or supplier return vouchers
                    item.quantity_disbursed = quantity_value
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                    print(f"Disbursement voucher: Subtracted {quantity_value} from product quantity")

                # Set unit price from product
                item.unit_price = product.unit_price
                print(f"Set unit price: {item.unit_price}")

                # Set machine and machine unit for disbursement vouchers
                if voucher.voucher_type == 'إذن صرف':
                    item.machine = self.request.POST.get(f'form-{i}-machine_name', '')
                    item.machine_unit = self.request.POST.get(f'form-{i}-machine_unit', '')
                    print(f"Set machine: {item.machine}, machine unit: {item.machine_unit}")

                # Save the updated product and the voucher item
                product.save()
                item.save()
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, F, Sum, Count
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import csv
import codecs
import json
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.conf import global_settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_module_permission_required, inventory_class_permission_required

# استيراد النماذج المحلية
from inventory.models_local import (
    Category, Product, Supplier, Customer, Department,
    Voucher, VoucherItem, LocalSystemSettings, Unit, PurchaseRequest
)

# استيراد النماذج من ملف models.py
from inventory.models import TblInvoices as Invoice, TblInvoiceitems as InvoiceItem

# استيراد النماذج
from inventory.forms import (
    ProductForm, CustomerForm, CategoryForm, SupplierForm, DepartmentForm,
    VoucherForm, VoucherItemForm, LocalSystemSettingsForm, UnitForm, PurchaseRequestForm,
    InvoiceForm, InvoiceItemForm
)

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

# إدارة الأصناف (Products)
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
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['out_of_stock'] = Product.objects.filter(quantity=0).count()
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

# إدارة العملاء (Customers)
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

# إدارة التصنيفات (Categories)
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

# إدارة وحدات القياس (Units)
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

# إدارة الموردين (Suppliers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'add')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة مورد جديد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'edit')
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل المورد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'delete')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المورد بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الأقسام (Departments)
@method_decorator(login_required, name='dispatch')
# @inventory_class_permission_required('departments', 'view')
class DepartmentListView(ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأقسام'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'add')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة قسم جديد'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'edit')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل القسم'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل القسم بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'delete')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'inventory/department_confirm_delete.html'
    success_url = reverse_lazy('inventory:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف القسم بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الأذونات (Vouchers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'view')
class VoucherListView(ListView):
    model = Voucher
    template_name = 'inventory/voucher_list.html'
    context_object_name = 'vouchers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        voucher_type = self.request.GET.get('voucher_type', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')

        if search_query:
            queryset = queryset.filter(
                Q(voucher_number__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(department__name__icontains=search_query) |
                Q(customer__name__icontains=search_query) |
                Q(recipient__icontains=search_query)
            )

        if voucher_type:
            queryset = queryset.filter(voucher_type=voucher_type)

        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except (ValueError, TypeError):
                pass

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except (ValueError, TypeError):
                pass

        return queryset.order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأذونات'
        context['search_query'] = self.request.GET.get('search', '')
        context['voucher_type'] = self.request.GET.get('voucher_type', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')

        # إحصائيات الأذونات
        context['addition_count'] = Voucher.objects.filter(voucher_type='إذن اضافة').count()
        context['disbursement_count'] = Voucher.objects.filter(voucher_type='إذن صرف').count()
        context['client_return_count'] = Voucher.objects.filter(voucher_type='اذن مرتجع عميل').count()
        context['supplier_return_count'] = Voucher.objects.filter(voucher_type='إذن مرتجع مورد').count()

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'add')
class VoucherCreateView(CreateView):
    model = Voucher
    form_class = VoucherForm
    template_name = 'inventory/voucher_form.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Pre-set voucher type if provided in URL
        voucher_type = self.request.GET.get('type', '')
        if voucher_type and voucher_type in dict(Voucher.VOUCHER_TYPES).keys():
            form.initial['voucher_type'] = voucher_type
            form.set_required_fields(voucher_type)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Basic form context
        voucher_type = self.request.GET.get('type', '')
        if voucher_type == 'إذن اضافة':
            context['page_title'] = 'إضافة إذن اضافة جديد'
        elif voucher_type == 'إذن صرف':
            context['page_title'] = 'إضافة إذن صرف جديد'
        elif voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = 'إضافة إذن مرتجع عميل جديد'
        elif voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = 'إضافة إذن مرتجع مورد جديد'
        else:
            context['page_title'] = 'إضافة إذن جديد'

        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')

        # Add data for select dropdown options
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')

        # Add voucher type for conditional form fields
        context['voucher_type'] = voucher_type

        # Add items template context
        context['voucher_items'] = []

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

    def form_valid(self, form):
        try:
            # Save the form to create the voucher
            response = super().form_valid(form)
            voucher = self.object

            # تسجيل بيانات النموذج للتشخيص
            print(f"Voucher created: {voucher.voucher_number}, Type: {voucher.voucher_type}")
            print(f"POST data: {self.request.POST}")

            # Get the total number of forms from the formset management form
            total_forms = int(self.request.POST.get('form-TOTAL_FORMS', 0))
            print(f"Total forms: {total_forms}")

            # تتبع عدد العناصر التي تمت إضافتها
            items_added = 0

            # Process each form in the formset
            for i in range(total_forms):
                # Get product code and product ID from the form
                product_code = self.request.POST.get(f'form-{i}-product_code')
                product_id = self.request.POST.get(f'form-{i}-product')
                quantity = self.request.POST.get(f'form-{i}-quantity')

                print(f"Processing form {i}: product_code={product_code}, product_id={product_id}, quantity={quantity}")

                # Skip if no product ID or quantity or quantity is 0
                if not product_id or not quantity:
                    print(f"Skipping form {i}: Missing product_id or quantity")
                    continue

                try:
                    quantity_value = float(quantity)
                    if quantity_value <= 0:
                        print(f"Skipping form {i}: Quantity is zero or negative")
                        continue
                except (ValueError, TypeError):
                    print(f"Invalid quantity value: {quantity}")
                    continue

                # Get the product (first try by product_id field, then by code if that doesn't work)
                try:
                    # First attempt to get by product_id (primary key)
                    product = Product.objects.get(product_id=product_id)
                    print(f"Found product by ID: {product.name}")
                except Product.DoesNotExist:
                    try:
                        # If that fails, try using the product code
                        if product_code:
                            product = Product.objects.get(product_id=product_code)
                            print(f"Found product by code: {product.name}")
                        else:
                            print(f"Product not found with ID: {product_id}")
                            continue
                    except Product.DoesNotExist:
                        print(f"Product not found with code: {product_code}")
                        continue

                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)

                # Set the appropriate quantity field and update product quantity based on voucher type
                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    item.quantity_added = quantity_value
                    # Update product quantity - add quantity
                    product.quantity += quantity_value
                    print(f"Addition voucher: Added {quantity_value} to product quantity")
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # For disbursement vouchers or supplier return vouchers
                    item.quantity_disbursed = quantity_value
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                    print(f"Disbursement voucher: Subtracted {quantity_value} from product quantity")

                # Set unit price from product
                item.unit_price = product.unit_price
                print(f"Set unit price: {item.unit_price}")

                # Set machine and machine unit for disbursement vouchers
                if voucher.voucher_type == 'إذن صرف':
                    item.machine = self.request.POST.get(f'form-{i}-machine_name', '')
                    item.machine_unit = self.request.POST.get(f'form-{i}-machine_unit', '')
                    print(f"Set machine: {item.machine}, machine unit: {item.machine_unit}")

                # Save the updated product and the voucher item
                product.save()
                item.save()
                items_added += 1
                print(f"Successfully saved voucher item {i} for product: {product.name}")

            # التحقق من عدد العناصر التي تمت إضافتها
            print(f"Total items added: {items_added}")

            # إذا لم يتم إضافة أي عناصر، أضف رسالة تحذير
            if items_added == 0:
                messages.warning(self.request, 'تم إضافة الإذن بنجاح، ولكن لم يتم إضافة أي أصناف. يرجى التحقق من الأصناف المضافة.')
            else:
                messages.success(self.request, f'تم إضافة الإذن بنجاح مع {items_added} صنف. رقم الإذن: {voucher.voucher_number}')
            return response

        except Exception as e:
            import traceback
            print(f"Error in form_valid: {str(e)}")
            print(traceback.format_exc())
            messages.error(self.request, f'حدث خطأ أثناء حفظ الأذن: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'edit')
class VoucherUpdateView(UpdateView):
    model = Voucher
    form_class = VoucherForm
    template_name = 'inventory/voucher_form.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()

        if voucher.voucher_type == 'إذن اضافة':
            context['page_title'] = 'تعديل إذن اضافة'
        elif voucher.voucher_type == 'إذن صرف':
            context['page_title'] = 'تعديل إذن صرف'
        elif voucher.voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = 'تعديل إذن مرتجع عميل'
        elif voucher.voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = 'تعديل إذن مرتجع مورد'
        else:
            context['page_title'] = 'تعديل إذن'

        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')

        # Add data for select dropdown options
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')

        # Add voucher type for conditional form fields
        context['voucher_type'] = voucher.voucher_type

        # Add items to context
        context['voucher_items'] = voucher.items.all()

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

    def form_valid(self, form):
        try:
            voucher = self.get_object()
            print(f"Updating voucher: {voucher.voucher_number}, Type: {voucher.voucher_type}")
            print(f"POST data: {self.request.POST}")

            # التحقق من عناصر الإذن قبل التعديل
            current_items = voucher.items.all()
            print(f"Current items count: {current_items.count()}")
            for item in current_items:
                print(f"Current item: {item.product.name}, Quantity Added: {item.quantity_added}, Quantity Disbursed: {item.quantity_disbursed}")

            # Reverse the effects of the current items on product quantities
            for item in current_items:
                product = item.product

                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # Reverse addition - subtract the previously added quantity
                    product.quantity -= item.quantity_added or 0
                    print(f"Reversing addition: Subtracted {item.quantity_added} from {product.name}")
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # Reverse disbursement - add back the previously disbursed quantity
                    product.quantity += item.quantity_disbursed or 0
                    print(f"Reversing disbursement: Added {item.quantity_disbursed} to {product.name}")

                product.save()

            # Delete all current items
            voucher.items.all().delete()
            print("Deleted all current items")

            # Save the updated voucher
            response = super().form_valid(form)
            voucher = self.object
            print(f"Updated voucher: {voucher.voucher_number}")

            # Get the total number of forms from the formset management form
            total_forms = int(self.request.POST.get('form-TOTAL_FORMS', 0))
            print(f"Total forms: {total_forms}")

            # تتبع عدد العناصر التي تمت إضافتها
            items_added = 0

            # Process each form in the formset
            for i in range(total_forms):
                # Get product ID and quantity from the form
                product_id = self.request.POST.get(f'form-{i}-product')
                quantity = self.request.POST.get(f'form-{i}-quantity')

                print(f"Processing form {i}: product_id={product_id}, quantity={quantity}")

                # Skip if no product ID or quantity
                if not product_id or not quantity:
                    print(f"Skipping form {i}: Missing product_id or quantity")
                    continue

                # Get the product
                try:
                    product = Product.objects.get(product_id=product_id)
                    print(f"Found product: {product.name}")
                except Product.DoesNotExist:
                    print(f"Product not found with ID: {product_id}")
                    continue

                # Convert quantity to float
                try:
                    quantity_value = float(quantity)
                    print(f"Quantity value: {quantity_value}")
                except (ValueError, TypeError):
                    print(f"Invalid quantity value: {quantity}")
                    continue

                # Skip if quantity is zero
                if quantity_value <= 0:
                    print(f"Skipping form {i}: Quantity is zero or negative")
                    continue

                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)
                print(f"Created voucher item for product: {product.name}")

                # Set the appropriate quantity field and update product quantity based on voucher type
                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    item.quantity_added = quantity_value
                    # Update product quantity - add quantity
                    product.quantity += quantity_value
                    print(f"Addition voucher: Added {quantity_value} to product quantity")
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # For disbursement vouchers or supplier return vouchers
                    item.quantity_disbursed = quantity_value
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                    print(f"Disbursement voucher: Subtracted {quantity_value} from product quantity")

                # Set unit price from product
                item.unit_price = product.unit_price
                print(f"Set unit price: {item.unit_price}")

                # Set machine and machine unit for disbursement vouchers
                if voucher.voucher_type == 'إذن صرف':
                    item.machine = self.request.POST.get(f'form-{i}-machine_name', '')
                    item.machine_unit = self.request.POST.get(f'form-{i}-machine_unit', '')
                    print(f"Set machine: {item.machine}, machine unit: {item.machine_unit}")

                # Save the updated product and the voucher item
                product.save()
                item.save()
                items_added += 1
                print(f"Saved voucher item {i}")

            # التحقق من عدد العناصر التي تمت إضافتها
            print(f"Total items added: {items_added}")

            # التحقق من عناصر الإذن بعد الحفظ
            saved_items = voucher.items.all()
            print(f"Saved items count: {saved_items.count()}")
            for item in saved_items:
                print(f"Saved item: {item.product.name}, Quantity Added: {item.quantity_added}, Quantity Disbursed: {item.quantity_disbursed}")

            messages.success(self.request, f'تم تعديل الإذن بنجاح. رقم الإذن: {voucher.voucher_number}')
            return response

        except Exception as e:
            import traceback
            print(f"Error in form_valid: {str(e)}")
            print(traceback.format_exc())
            messages.error(self.request, f'حدث خطأ أثناء تعديل الإذن: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'delete')
class VoucherDeleteView(DeleteView):
    model = Voucher
    template_name = 'inventory/voucher_confirm_delete.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def delete(self, request, *args, **kwargs):
        try:
            voucher = self.get_object()

            # Reverse the effects of the voucher items on product quantities
            for item in voucher.items.all():
                product = item.product

                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # Reverse addition - subtract the added quantity
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # Reverse disbursement - add back the disbursed quantity
                    product.quantity += item.quantity_disbursed or 0

                product.save()

            response = super().delete(request, *args, **kwargs)
            messages.success(request, 'تم حذف الإذن بنجاح')
            return response
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف الإذن: {str(e)}')
            return redirect('inventory:voucher_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'view')
class VoucherDetailView(DetailView):
    model = Voucher
    template_name = 'inventory/voucher_detail.html'
    context_object_name = 'voucher'

    def get_object(self, queryset=None):
        """
        تجاوز الدالة الافتراضية للحصول على الكائن لضمان استخدام رقم الإذن كمفتاح أساسي
        """
        if queryset is None:
            queryset = self.get_queryset()

        # الحصول على رقم الإذن من المسار
        pk = self.kwargs.get('pk')

        # طباعة رقم الإذن للتشخيص
        print(f"Looking for voucher with ID: {pk}")

        # البحث عن الإذن
        try:
            # أولاً نحاول البحث باستخدام المعرف الأساسي
            try:
                obj = queryset.get(pk=pk)
                print(f"Found voucher by ID: {obj.id}, Number: {obj.voucher_number}, Type: {obj.voucher_type}")
                return obj
            except (Voucher.DoesNotExist, ValueError):
                # إذا فشل البحث بالمعرف، نحاول البحث برقم الإذن
                obj = queryset.get(voucher_number=pk)
                print(f"Found voucher by number: {obj.id}, Number: {obj.voucher_number}, Type: {obj.voucher_type}")
                return obj
        except Voucher.DoesNotExist:
            raise Http404("لا يوجد إذن بهذا الرقم")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.object

        print(f"Preparing context for voucher: {voucher.voucher_number}")

        # الحصول على عناصر الإذن باستخدام استعلام مباشر
        # استخدام استعلام مباشر بدلاً من العلاقة العكسية
        voucher_items = VoucherItem.objects.filter(voucher_id=voucher.id).select_related('product', 'product__unit')

        # طباعة عدد العناصر للتشخيص
        print(f"Found {voucher_items.count()} items for voucher {voucher.voucher_number}")

        # طباعة تفاصيل كل عنصر
        for item in voucher_items:
            print(f"Item: {item.id}, Product: {item.product.name}, Quantity Added: {item.quantity_added}, Quantity Disbursed: {item.quantity_disbursed}")

        context['voucher_items'] = voucher_items

        # Calculate totals for the template
        total_value = 0
        total_quantity_added = 0
        total_quantity_disbursed = 0

        for item in voucher_items:
            if item.quantity_added:
                total_quantity_added += item.quantity_added
            if item.quantity_disbursed:
                total_quantity_disbursed += item.quantity_disbursed
            total_value += item.total_price

        context['total_value'] = total_value
        context['total_quantity_added'] = total_quantity_added
        context['total_quantity_disbursed'] = total_quantity_disbursed
        context['items_count'] = voucher_items.count()

        # Determine the type-specific title
        if voucher.voucher_type == 'إذن اضافة':
            context['page_title'] = f'تفاصيل إذن اضافة #{voucher.voucher_number}'
        elif voucher.voucher_type == 'إذن صرف':
            context['page_title'] = f'تفاصيل إذن صرف #{voucher.voucher_number}'
        elif voucher.voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = f'تفاصيل إذن مرتجع عميل #{voucher.voucher_number}'
        elif voucher.voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = f'تفاصيل إذن مرتجع مورد #{voucher.voucher_number}'
        else:
            context['page_title'] = f'تفاصيل إذن #{voucher.voucher_number}'

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

# Purchase Requests Management
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('purchase_requests', 'view')
class PurchaseRequestListView(ListView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_list.html'
    context_object_name = 'purchase_requests'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', '')

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-requested_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة طلبات الشراء'
        context['selected_status'] = self.request.GET.get('status', '')

        # Get counts for sidebar
        context['pending_count'] = PurchaseRequest.objects.filter(status='pending').count()
        context['approved_count'] = PurchaseRequest.objects.filter(status='approved').count()
        context['rejected_count'] = PurchaseRequest.objects.filter(status='rejected').count()

        return context

@login_required
@inventory_module_permission_required('purchase_requests', 'add')
def create_purchase_request(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    # Check if there's already a pending purchase request for this product
    existing_request = PurchaseRequest.objects.filter(product=product, status='pending').exists()
    if existing_request:
        messages.warning(request, f'يوجد بالفعل طلب شراء قيد الانتظار للصنف {product.name}')
        return redirect('inventory:product_list')

    # Create new purchase request
    purchase_request = PurchaseRequest(
        product=product,
        status='pending'
    )
    purchase_request.save()

    messages.success(request, f'تم إنشاء طلب شراء جديد للصنف {product.name}')
    return redirect('inventory:product_list')

@login_required
@inventory_module_permission_required('purchase_requests', 'edit')
def update_purchase_request_status(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    status = request.POST.get('status', '')

    if status in ['approved', 'rejected']:
        purchase_request.status = status
        if status == 'approved':
            purchase_request.approved_date = timezone.now()
            purchase_request.approved_by = request.user.get_full_name() or request.user.username

        purchase_request.save()

        status_text = 'الموافقة على' if status == 'approved' else 'رفض'
        messages.success(request, f'تم {status_text} طلب شراء الصنف {purchase_request.product.name}')
    else:
        messages.error(request, 'حالة غير صالحة')

    return redirect('inventory:purchase_request_list')

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

@login_required
def generate_voucher_number(request):
    """Generate a new voucher number based on the voucher type"""
    voucher_type = request.GET.get('type', '')

    prefix = ''
    if voucher_type == 'إذن اضافة':
        prefix = 'ADD'
    elif voucher_type == 'إذن صرف':
        prefix = 'DIS'
    elif voucher_type == 'اذن مرتجع عميل':
        prefix = 'CRT'
    elif voucher_type == 'إذن مرتجع مورد':
        prefix = 'SRT'
    else:
        prefix = 'V'

    # Get date part and random number for uniqueness
    date_part = timezone.now().strftime('%Y%m%d')

    # Get the count of vouchers for today for this type + 1
    today = timezone.now().date()
    count = Voucher.objects.filter(
        date=today,
        voucher_number__startswith=f"{prefix}-{date_part}"
    ).count() + 1

    # Format with leading zeros for the count (e.g., 001, 002, etc.)
    voucher_number = f"{prefix}-{date_part}-{count:03d}"

    return JsonResponse({'voucher_number': voucher_number})

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

# إدارة الأصناف (Products)
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
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['out_of_stock'] = Product.objects.filter(quantity=0).count()
        context['title'] = 'قائمة الأصناف'
        return context



@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'add')
class ProductCreateView(CreateView):
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
        context['page_title'] = 'إضافة صنف جديد'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        # Print all form data for debugging
        print("Form data:", self.request.POST)
        print("Form cleaned data:", form.cleaned_data)

        # عند إنشاء منتج جديد، نقوم بتعيين الرصيد الحالي من الرصيد الافتتاحي
        form.instance.quantity = form.cleaned_data.get('initial_quantity', 0)

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

        print(f"New unit: {new_unit}, Name: {new_unit_name}, Symbol: {new_unit_symbol}")

        # Check if unit is "new" in the dropdown
        unit_value = self.request.POST.get('unit')
        print(f"Unit dropdown value: {unit_value}")

        # If the unit dropdown has "new" selected but the hidden field wasn't set properly
        if unit_value == "new" or new_unit == 'true':
            # Get the unit name and symbol from the request directly
            direct_unit_name = self.request.POST.get('new_unit_name')
            direct_unit_symbol = self.request.POST.get('new_unit_symbol')
            print(f"Direct unit name: {direct_unit_name}, Symbol: {direct_unit_symbol}")

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
            print(f"Created new unit: {unit}")
        elif unit_value and unit_value != "":
            # If a regular unit is selected
            try:
                unit_id = int(unit_value)
                unit = Unit.objects.get(id=unit_id)
                form.instance.unit = unit
                print(f"Selected existing unit: {unit}")
            except (ValueError, Unit.DoesNotExist):
                print(f"Invalid unit ID: {unit_value}")
        else:
            # No unit selected
            form.instance.unit = None
            print("No unit selected")

        # Ensure we have a product_id if not provided
        if not form.instance.product_id:
            form.instance.product_id = f"P{timezone.now().strftime('%Y%m%d%H%M%S')}"

        messages.success(self.request, 'تم إضافة الصنف بنجاح')
        return super().form_valid(form)

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

# إدارة العملاء (Customers)
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

# إدارة التصنيفات (Categories)
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

# إدارة وحدات القياس (Units)
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

# إدارة الموردين (Suppliers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'add')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة مورد جديد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'edit')
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل المورد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'delete')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المورد بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الأقسام (Departments)
@method_decorator(login_required, name='dispatch')
# @inventory_class_permission_required('departments', 'view')
class DepartmentListView(ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأقسام'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'add')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة قسم جديد'

# إدارة الأصناف (Products)
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
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['out_of_stock'] = Product.objects.filter(quantity=0).count()
        context['title'] = 'قائمة الأصناف'
        return context



@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'add')
class ProductCreateView(CreateView):
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
        context['page_title'] = 'إضافة صنف جديد'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        # Print all form data for debugging
        print("Form data:", self.request.POST)
        print("Form cleaned data:", form.cleaned_data)

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

        print(f"New unit: {new_unit}, Name: {new_unit_name}, Symbol: {new_unit_symbol}")

        # Check if unit is "new" in the dropdown
        unit_value = self.request.POST.get('unit')
        print(f"Unit dropdown value: {unit_value}")

        # If the unit dropdown has "new" selected but the hidden field wasn't set properly
        if unit_value == "new" or new_unit == 'true':
            # Get the unit name and symbol from the request directly
            direct_unit_name = self.request.POST.get('new_unit_name')
            direct_unit_symbol = self.request.POST.get('new_unit_symbol')
            print(f"Direct unit name: {direct_unit_name}, Symbol: {direct_unit_symbol}")

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
            print(f"Created new unit: {unit}")
        elif unit_value and unit_value != "":
            # If a regular unit is selected
            try:
                unit_id = int(unit_value)
                unit = Unit.objects.get(id=unit_id)
                form.instance.unit = unit
                print(f"Selected existing unit: {unit}")
            except (ValueError, Unit.DoesNotExist):
                print(f"Invalid unit ID: {unit_value}")
        else:
            # No unit selected
            form.instance.unit = None
            print("No unit selected")

        # Ensure we have a product_id if not provided
        if not form.instance.product_id:
            form.instance.product_id = f"P{timezone.now().strftime('%Y%m%d%H%M%S')}"

        messages.success(self.request, 'تم إضافة الصنف بنجاح')
        return super().form_valid(form)

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

# إدارة العملاء (Customers)
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

# إدارة التصنيفات (Categories)
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

# إدارة وحدات القياس (Units)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل وحدة القياس'
        # Add low stock count for sidebar
        context['low_stock_count'] = get_low_stock_count()

        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'add')
class VoucherCreateView(CreateView):
    model = Voucher
    form_class = VoucherForm
    template_name = 'inventory/voucher_form.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Pre-set voucher type if provided in URL
        voucher_type = self.request.GET.get('type', '')
        if voucher_type and voucher_type in dict(Voucher.VOUCHER_TYPES).keys():
            form.initial['voucher_type'] = voucher_type
            form.set_required_fields(voucher_type)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Basic form context
        voucher_type = self.request.GET.get('type', '')
        if voucher_type == 'إذن اضافة':
            context['page_title'] = 'إضافة إذن اضافة جديد'
        elif voucher_type == 'إذن صرف':
            context['page_title'] = 'إضافة إذن صرف جديد'
        elif voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = 'إضافة إذن مرتجع عميل جديد'
        elif voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = 'إضافة إذن مرتجع مورد جديد'
        else:
            context['page_title'] = 'إضافة إذن جديد'

        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')

        # Add data for select dropdown options
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')

        # Add voucher type for conditional form fields
        context['voucher_type'] = voucher_type

        # Add items template context
        context['voucher_items'] = []

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

    def form_valid(self, form):
        try:
            # Save the form to create the voucher
            response = super().form_valid(form)
            voucher = self.object

            # Process the items that were submitted
            product_ids = self.request.POST.getlist('product_id[]')
            quantities_added = self.request.POST.getlist('quantity_added[]')
            quantities_disbursed = self.request.POST.getlist('quantity_disbursed[]')
            machines = self.request.POST.getlist('machine[]')
            machine_units = self.request.POST.getlist('machine_unit[]')

            # Create the voucher items and update product quantities
            for i in range(len(product_ids)):
                if not product_ids[i]:
                    continue

                product = get_object_or_404(Product, product_id=product_ids[i])

                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)

                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    quantity_added = float(quantities_added[i]) if quantities_added[i] else 0
                    item.quantity_added = quantity_added
                    # Update product quantity - add quantity
                    product.quantity += quantity_added

                elif voucher.voucher_type == 'إذن صرف':
                    # For disbursement vouchers
                    quantity_disbursed = float(quantities_disbursed[i]) if quantities_disbursed[i] else 0
                    item.quantity_disbursed = quantity_disbursed
                    item.machine = machines[i] if i < len(machines) else ''
                    item.machine_unit = machine_units[i] if i < len(machine_units) else ''
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_disbursed

                elif voucher.voucher_type == 'إذن مرتجع مورد':
                    # For supplier return vouchers
                    quantity_disbursed = float(quantities_disbursed[i]) if quantities_disbursed[i] else 0
                    item.quantity_disbursed = quantity_disbursed
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_disbursed

                # Save the updated product and the voucher item
                product.save()
                item.save()

            messages.success(self.request, f'تم إضافة الإذن بنجاح. رقم الإذن: {voucher.voucher_number}')
            return response

        except Exception as e:
            messages.error(self.request, f'حدث خطأ أثناء حفظ الأذن: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'edit')
class VoucherUpdateView(UpdateView):
    model = Voucher
    form_class = VoucherForm
    template_name = 'inventory/voucher_form.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()

        if voucher.voucher_type == 'إذن اضافة':
            context['page_title'] = 'تعديل إذن اضافة'
        elif voucher.voucher_type == 'إذن صرف':
            context['page_title'] = 'تعديل إذن صرف'
        elif voucher.voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = 'تعديل إذن مرتجع عميل'
        elif voucher.voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = 'تعديل إذن مرتجع مورد'
        else:
            context['page_title'] = 'تعديل إذن'

        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')

        # Add data for select dropdown options
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')

        # Add voucher type for conditional form fields
        context['voucher_type'] = voucher.voucher_type

        # Add items to context
        context['voucher_items'] = voucher.items.all()

        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count

        return context

    def form_valid(self, form):
        try:
            voucher = self.get_object()

            # Reverse the effects of the current items on product quantities
            for item in voucher.items.all():
                product = item.product

                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # Reverse addition - subtract the previously added quantity
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # Reverse disbursement - add back the previously disbursed quantity
                    product.quantity += item.quantity_disbursed or 0

                product.save()

            # Delete all current items
            voucher.items.all().delete()

            # Save the updated voucher
            response = super().form_valid(form)
            voucher = self.object

            # Process the items sent from the form
            total_forms = int(self.request.POST.get('form-TOTAL_FORMS', 0))
            print(f"Total forms: {total_forms}")

            # تتبع عدد العناصر التي تمت إضافتها
            items_added = 0

            # Process each form in the formset
            for i in range(total_forms):
                # Get product code and product ID from the form
                product_code = self.request.POST.get(f'form-{i}-product_code')
                product_id = self.request.POST.get(f'form-{i}-product')
                quantity = self.request.POST.get(f'form-{i}-quantity')

                print(f"Processing form {i}: product_code={product_code}, product_id={product_id}, quantity={quantity}")

                # Skip if no product ID or quantity or quantity is 0
                if not product_id or not quantity:
                    print(f"Skipping form {i}: Missing product_id or quantity")
                    continue

                try:
                    quantity_value = float(quantity)
                    if quantity_value <= 0:
                        print(f"Skipping form {i}: Quantity is zero or negative")
                        continue
                except (ValueError, TypeError):
                    print(f"Invalid quantity value: {quantity}")
                    continue

                # Get the product (first try by product_id field, then by code if that doesn't work)
                try:
                    # First attempt to get by product_id (primary key)
                    product = Product.objects.get(product_id=product_id)
                    print(f"Found product by ID: {product.name}")
                except Product.DoesNotExist:
                    try:
                        # If that fails, try using the product code
                        if product_code:
                            product = Product.objects.get(product_id=product_code)
                            print(f"Found product by code: {product.name}")
                        else:
                            print(f"Product not found with ID: {product_id}")
                            continue
                    except Product.DoesNotExist:
                        print(f"Product not found with code: {product_code}")
                        continue

                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)

                # Set the appropriate quantity field and update product quantity based on voucher type
                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    item.quantity_added = quantity_value
                    # Update product quantity - add quantity
                    product.quantity += quantity_value
                    print(f"Addition voucher: Added {quantity_value} to product quantity")
                elif voucher.voucher_type == 'إذن صرف':
                    # For disbursement vouchers
                    item.quantity_disbursed = quantity_value
                    item.machine = self.request.POST.get(f'form-{i}-machine_name', '')
                    item.machine_unit = self.request.POST.get(f'form-{i}-machine_unit', '')
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                    print(f"Disbursement voucher: Subtracted {quantity_value} from product quantity")
                elif voucher.voucher_type == 'إذن مرتجع مورد':
                    # For supplier return vouchers
                    item.quantity_disbursed = quantity_value
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                    print(f"Supplier return voucher: Subtracted {quantity_value} from product quantity")

                # Set unit price from product
                item.unit_price = product.unit_price
                print(f"Set unit price: {item.unit_price}")

                # Save the updated product and the voucher item
                product.save()
                item.save()
                items_added += 1
                print(f"Successfully saved voucher item {i} for product: {product.name}")

            # التحقق من عدد العناصر التي تمت إضافتها
            print(f"Total items added: {items_added}")

            # التحقق من عناصر الإذن بعد الحفظ
            # استخدام استعلام مباشر بدلاً من العلاقة العكسية
            saved_items = VoucherItem.objects.filter(voucher=voucher)
            print(f"Saved items count: {saved_items.count()}")
            for item in saved_items:
                print(f"Saved item: {item.id}, Product: {item.product.name}, Quantity Added: {item.quantity_added}, Quantity Disbursed: {item.quantity_disbursed}")

            # إذا لم يتم إضافة أي عناصر، أضف رسالة تحذير
            if items_added == 0:
                messages.warning(self.request, 'تم تعديل الإذن بنجاح، ولكن لم يتم إضافة أي أصناف. يرجى التحقق من الأصناف المضافة.')
            else:
                messages.success(self.request, f'تم تعديل الإذن بنجاح مع {items_added} صنف. رقم الإذن: {voucher.voucher_number}')
            return response

        except Exception as e:
            messages.error(self.request, f'حدث خطأ أثناء تعديل الإذن: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'delete')
class VoucherDeleteView(DeleteView):
    model = Voucher
    template_name = 'inventory/voucher_confirm_delete.html'
    success_url = reverse_lazy('inventory:voucher_list')

    def delete(self, request, *args, **kwargs):
        try:
            voucher = self.get_object()

            # Reverse the effects of the voucher items on product quantities
            for item in voucher.items.all():
                product = item.product

                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # Reverse addition - subtract the added quantity
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # Reverse disbursement - add back the disbursed quantity
                    product.quantity += item.quantity_disbursed or 0

                product.save()

            response = super().delete(request, *args, **kwargs)
            messages.success(request, 'تم حذف الإذن بنجاح')
            return response
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف الإذن: {str(e)}')
            return redirect('inventory:voucher_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'view')
class VoucherDetailView(DetailView):
    model = Voucher
    template_name = 'inventory/voucher_detail.html'
    context_object_name = 'voucher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.object

        # Add voucher items to context
        context['voucher_items'] = voucher.items.all()

        # Determine the type-specific title
        if voucher.voucher_type == 'إذن اضافة':
            context['page_title'] = f'تفاصيل إذن اضافة #{voucher.voucher_number}'
        elif voucher.voucher_type == 'إذن صرف':
            context['page_title'] = f'تفاصيل إذن صرف #{voucher.voucher_number}'
        elif voucher.voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = f'تفاصيل إذن مرتجع عميل #{voucher.voucher_number}'
        elif voucher.voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = f'تفاصيل إذن مرتجع مورد #{voucher.voucher_number}'
        else:
            context['page_title'] = f'تفاصيل إذن #{voucher.voucher_number}'

        return context

# Purchase Requests Management
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('purchase_requests', 'view')
class PurchaseRequestListView(ListView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_list.html'
    context_object_name = 'purchase_requests'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', '')

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-requested_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة طلبات الشراء'
        context['selected_status'] = self.request.GET.get('status', '')

        # Get counts for sidebar
        context['pending_count'] = PurchaseRequest.objects.filter(status='pending').count()
        context['approved_count'] = PurchaseRequest.objects.filter(status='approved').count()
        context['rejected_count'] = PurchaseRequest.objects.filter(status='rejected').count()

        return context

@login_required
@inventory_module_permission_required('purchase_requests', 'add')
def create_purchase_request(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    # Check if there's already a pending purchase request for this product
    existing_request = PurchaseRequest.objects.filter(product=product, status='pending').exists()
    if existing_request:
        messages.warning(request, f'يوجد بالفعل طلب شراء قيد الانتظار للصنف {product.name}')
        return redirect('inventory:product_list')

    # Create new purchase request
    purchase_request = PurchaseRequest(
        product=product,
        status='pending'
    )
    purchase_request.save()

    messages.success(request, f'تم إنشاء طلب شراء جديد للصنف {product.name}')
    return redirect('inventory:product_list')

@login_required
@inventory_module_permission_required('purchase_requests', 'edit')
def update_purchase_request_status(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    status = request.POST.get('status', '')

    if status in ['approved', 'rejected']:
        purchase_request.status = status
        if status == 'approved':
            purchase_request.approved_date = timezone.now()
            purchase_request.approved_by = request.user.get_full_name() or request.user.username

        purchase_request.save()

        status_text = 'الموافقة على' if status == 'approved' else 'رفض'
        messages.success(request, f'تم {status_text} طلب شراء الصنف {purchase_request.product.name}')
    else:
        messages.error(request, 'حالة غير صالحة')

    return redirect('inventory:purchase_request_list')

@login_required
@csrf_exempt
@inventory_module_permission_required('dashboard', 'view')
def check_low_stock(request):
    """
    Check for low stock items and return them as JSON
    Esta vista API devuelve una lista de productos con bajo stock en formato JSON
    """
    # Verificar si el usuario tiene permisos para ver el dashboard
    if not request.user.has_perm('inventory.view_dashboard'):
        return JsonResponse({'error': 'No tienes permisos para acceder a esta información'}, status=403)

    # Obtener productos con bajo stock
    low_stock_products = Product.objects.filter(
        quantity__lt=F('minimum_threshold'),
        minimum_threshold__gt=0
    ).values('product_id', 'name', 'quantity', 'minimum_threshold')

    # Devolver como JSON
    return JsonResponse(list(low_stock_products), safe=False)

@login_required
def generate_voucher_number(request):
    """Generate a new voucher number based on the voucher type"""
    voucher_type = request.GET.get('type', '')

    prefix = ''
    if voucher_type == 'إذن اضافة':
        prefix = 'ADD'
    elif voucher_type == 'إذن صرف':
        prefix = 'DIS'
    elif voucher_type == 'اذن مرتجع عميل':
        prefix = 'CRT'
    elif voucher_type == 'إذن مرتجع مورد':
        prefix = 'SRT'
    else:
        prefix = 'V'

    # Get date part and random number for uniqueness
    date_part = timezone.now().strftime('%Y%m%d')

    # Get the count of vouchers for today for this type + 1
    today = timezone.now().date()
    count = Voucher.objects.filter(
        date=today,
        voucher_number__startswith=f"{prefix}-{date_part}"
    ).count() + 1

    # Format with leading zeros for the count (e.g., 001, 002, etc.)
    voucher_number = f"{prefix}-{date_part}-{count:03d}"

    return JsonResponse({'voucher_number': voucher_number})



# إدارة الأصناف (Products)
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
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['out_of_stock'] = Product.objects.filter(quantity=0).count()
        context['title'] = 'قائمة الأصناف'
        return context



@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'add')
class ProductCreateView(CreateView):
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
        context['page_title'] = 'إضافة صنف جديد'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        # Print all form data for debugging
        print("Form data:", self.request.POST)
        print("Form cleaned data:", form.cleaned_data)

        # عند إنشاء منتج جديد، نقوم بتعيين الرصيد الحالي من الرصيد الافتتاحي
        form.instance.quantity = form.cleaned_data.get('initial_quantity', 0)

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

        print(f"New unit: {new_unit}, Name: {new_unit_name}, Symbol: {new_unit_symbol}")

        # Check if unit is "new" in the dropdown
        unit_value = self.request.POST.get('unit')
        print(f"Unit dropdown value: {unit_value}")

        # If the unit dropdown has "new" selected but the hidden field wasn't set properly
        if unit_value == "new" or new_unit == 'true':
            # Get the unit name and symbol from the request directly
            direct_unit_name = self.request.POST.get('new_unit_name')
            direct_unit_symbol = self.request.POST.get('new_unit_symbol')
            print(f"Direct unit name: {direct_unit_name}, Symbol: {direct_unit_symbol}")

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
            print(f"Created new unit: {unit}")
        elif unit_value and unit_value != "":
            # If a regular unit is selected
            try:
                unit_id = int(unit_value)
                unit = Unit.objects.get(id=unit_id)
                form.instance.unit = unit
                print(f"Selected existing unit: {unit}")
            except (ValueError, Unit.DoesNotExist):
                print(f"Invalid unit ID: {unit_value}")
        else:
            # No unit selected
            form.instance.unit = None
            print("No unit selected")

        # Ensure we have a product_id if not provided
        if not form.instance.product_id:
            form.instance.product_id = f"P{timezone.now().strftime('%Y%m%d%H%M%S')}"

        messages.success(self.request, 'تم إضافة الصنف بنجاح')
        return super().form_valid(form)

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

# إدارة العملاء (Customers)
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

# إدارة التصنيفات (Categories)
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

# إدارة وحدات القياس (Units)
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

# إدارة الموردين (Suppliers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'add')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة مورد جديد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'edit')
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل المورد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'delete')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المورد بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الأقسام (Departments)
@method_decorator(login_required, name='dispatch')
# @inventory_class_permission_required('departments', 'view')
class DepartmentListView(ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأقسام'
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'add')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'inventory/department_form.html'
    success_url = reverse_lazy('inventory:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة قسم جديد'
        return context

    def form_valid(self, form):
        # حفظ القسم
        response = super().form_valid(form)

        # إضافة رسالة نجاح
        messages.success(self.request, f'تم إضافة القسم "{self.object.name}" بنجاح. كود القسم: {self.object.code}')

        return response

# إدارة الأصناف (Products)
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
            queryset = queryset.filter(
                quantity__lt=F('minimum_threshold'),
                minimum_threshold__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['out_of_stock'] = Product.objects.filter(quantity=0).count()
        context['title'] = 'قائمة الأصناف'
        return context



@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'add')
class ProductCreateView(CreateView):
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
        context['page_title'] = 'إضافة صنف جديد'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        # Print all form data for debugging
        print("Form data:", self.request.POST)
        print("Form cleaned data:", form.cleaned_data)

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

        print(f"New unit: {new_unit}, Name: {new_unit_name}, Symbol: {new_unit_symbol}")

        # Check if unit is "new" in the dropdown
        unit_value = self.request.POST.get('unit')
        print(f"Unit dropdown value: {unit_value}")

        # If the unit dropdown has "new" selected but the hidden field wasn't set properly
        if unit_value == "new" or new_unit == 'true':
            # Get the unit name and symbol from the request directly
            direct_unit_name = self.request.POST.get('new_unit_name')
            direct_unit_symbol = self.request.POST.get('new_unit_symbol')
            print(f"Direct unit name: {direct_unit_name}, Symbol: {direct_unit_symbol}")

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
            print(f"Created new unit: {unit}")
        elif unit_value and unit_value != "":
            # If a regular unit is selected
            try:
                unit_id = int(unit_value)
                unit = Unit.objects.get(id=unit_id)
                form.instance.unit = unit
                print(f"Selected existing unit: {unit}")
            except (ValueError, Unit.DoesNotExist):
                print(f"Invalid unit ID: {unit_value}")
        else:
            # No unit selected
            form.instance.unit = None
            print("No unit selected")

        # Ensure we have a product_id if not provided
        if not form.instance.product_id:
            form.instance.product_id = f"P{timezone.now().strftime('%Y%m%d%H%M%S')}"

        messages.success(self.request, 'تم إضافة الصنف بنجاح')
        return super().form_valid(form)

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

# إدارة العملاء (Customers)
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')

# إدارة التصنيفات (Categories)
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

# إدارة وحدات القياس (Units)
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

# إدارة الموردين (Suppliers)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'add')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة مورد جديد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'edit')
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل المورد'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل المورد بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'delete')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المورد بنجاح')
        return super().delete(request, *args, **kwargs)

# إدارة الفواتير (Invoices)
@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('invoices', 'view')
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'inventory/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search_query) |
                Q(recipient__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الفواتير'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('invoices', 'add')
class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'inventory/invoice_form.html'
    success_url = reverse_lazy('inventory:invoice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة فاتورة جديدة'
        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        invoice = self.object
        items = InvoiceItem.objects.filter(invoice_number=invoice.invoice_number)
        for item in items:
            product = item.product
            if invoice.invoice_type == 'إضافة':
                product.quantity = (product.quantity or 0) + (item.quantity_elwarad or 0)
            elif invoice.invoice_type == 'صرف':
                product.quantity = (product.quantity or 0) - (item.quantity_elmonsarf or 0)
            elif invoice.invoice_type == 'مرتجع عميل':
                product.quantity = (product.quantity or 0) + (item.quantity_mortagaaomalaa or 0)
            elif invoice.invoice_type == 'مرتجع مورد':
                product.quantity = (product.quantity or 0) - (item.quantity_mortagaaelmawarden or 0)
            product.save()
        return response

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('invoices', 'edit')
class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'inventory/invoice_form.html'
    success_url = reverse_lazy('inventory:invoice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل الفاتورة'
        # Add today's date for the date field default value
        context['today'] = timezone.now().date().strftime('%Y-%m-%d')
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

    def form_valid(self, form):
        invoice = self.get_object()
        old_items = InvoiceItem.objects.filter(invoice_number=invoice.invoice_number)
        for item in old_items:
            product = item.product
            if invoice.invoice_type == 'إضافة':
                product.quantity -= (item.quantity_elwarad or 0)
            elif invoice.invoice_type == 'صرف':
                product.quantity += (item.quantity_elmonsarf or 0)
            elif invoice.invoice_type == 'مرتجع عميل':
                product.quantity -= (item.quantity_mortagaaomalaa or 0)
            elif invoice.invoice_type == 'مرتجع مورد':
                product.quantity += (item.quantity_mortagaaelmawarden or 0)
            product.save()
        response = super().form_valid(form)
        invoice = self.object
        new_items = InvoiceItem.objects.filter(invoice_number=invoice.invoice_number)
        for item in new_items:
            product = item.product
            if invoice.invoice_type == 'إضافة':
                product.quantity += (item.quantity_elwarad or 0)
            elif invoice.invoice_type == 'صرف':
                product.quantity -= (item.quantity_elmonsarf or 0)
            elif invoice.invoice_type == 'مرتجع عميل':
                product.quantity += (item.quantity_mortagaaomalaa or 0)
            elif invoice.invoice_type == 'مرتجع مورد':
                product.quantity -= (item.quantity_mortagaaelmawarden or 0)
            product.save()
        return response

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('invoices', 'delete')
class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'inventory/invoice_confirm_delete.html'
    success_url = reverse_lazy('inventory:invoice_list')

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('invoices', 'view')
class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'inventory/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_items'] = InvoiceItem.objects.filter(invoice_number=self.object.invoice_number)
        return context

# إدارة عناصر الفاتورة (Invoice Items)
class InvoiceItemListView(ListView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_list.html'
    context_object_name = 'invoice_items'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search_query) |
                Q(product__product_name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class InvoiceItemCreateView(CreateView):
    model = InvoiceItem
    form_class = InvoiceItemForm
    template_name = 'inventory/invoice_item_form.html'
    success_url = reverse_lazy('inventory:invoice_list')

class InvoiceItemUpdateView(UpdateView):
    model = InvoiceItem
    form_class = InvoiceItemForm
    template_name = 'inventory/invoice_item_form.html'
    success_url = reverse_lazy('inventory:invoice_list')

class InvoiceItemDeleteView(DeleteView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_confirm_delete.html'
    success_url = reverse_lazy('inventory:invoice_list')

class InvoiceItemDetailView(DetailView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_detail.html'

# تقارير المخزون
class DailyReportView(ListView):
    template_name = 'inventory/daily_report.html'
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # الأصناف المضافة اليوم
        today_products = Product.objects.filter(created_at__date=today)

        # الفواتير اليومية
        today_invoices = Invoice.objects.filter(invoice_date__date=today)

        # إحصائيات الفواتير
        invoice_stats = {
            'total': today_invoices.count(),
            'addition': today_invoices.filter(invoice_type='إضافة').count(),
            'withdrawal': today_invoices.filter(invoice_type='صرف').count(),
            'customer_return': today_invoices.filter(invoice_type='مرتجع عميل').count(),
            'supplier_return': today_invoices.filter(invoice_type='مرتجع مورد').count(),
        }

        context.update({
            'today_products': today_products,
            'today_invoices': today_invoices,
            'invoice_stats': invoice_stats,
            'date': today,
        })
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('stock_report', 'view')
class StockReportView(ListView):
    model = Product
    template_name = 'inventory/stock_report.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        stock_status = self.request.GET.get('stock_status', '')

        if search_query:
            queryset = queryset.filter(
                Q(product_id__icontains=search_query) |
                Q(name__icontains=search_query)
            )

        if category:
            queryset = queryset.filter(category=category)

        if stock_status == 'low':
            queryset = queryset.filter(quantity__lt=F('minimum_threshold'))
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)
        elif stock_status == 'normal':
            queryset = queryset.filter(quantity__gte=F('minimum_threshold'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_stock_status'] = self.request.GET.get('stock_status', '')
        return context

@login_required
@inventory_module_permission_required('stock_report', 'print')
def export_to_csv(request):
    try:
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'

        # استخدام codecs للتعامل مع النصوص العربية
        writer = csv.writer(response)

        # كتابة رؤوس الأعمدة
        writer.writerow(['كود الصنف', 'اسم الصنف', 'الكمية في المخزون', 'الحد الأدنى', 'الحد الأقصى'])

        # الحصول على البيانات مع تطبيق الفلاتر
        products = Product.objects.all()
        search_query = request.GET.get('search', '')
        category = request.GET.get('category', '')
        stock_status = request.GET.get('stock_status', '')

        if search_query:
            products = products.filter(
                Q(product_id__icontains=search_query) |
                Q(name__icontains=search_query)
            )

        if category:
            try:
                category_id = int(category)
                products = products.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass

        if stock_status == 'low':
            products = products.filter(quantity__lt=F('minimum_threshold'))
        elif stock_status == 'out':
            products = products.filter(quantity=0)
        elif stock_status == 'normal':
            products = products.filter(quantity__gte=F('minimum_threshold'))

        # كتابة البيانات
        for product in products:
            writer.writerow([
                product.product_id,
                product.name,
                product.quantity,
                product.minimum_threshold,
                product.maximum_threshold
            ])

        return response
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تصدير البيانات: {str(e)}')
        return redirect('inventory:stock_report')

@login_required
@inventory_module_permission_required('settings', 'view')
def system_settings(request):
    settings = LocalSystemSettings.get_settings()

    if request.method == 'POST':
        form = LocalSystemSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()

            # تغيير لغة الواجهة
            translation.activate(form.cleaned_data['language'])
            request.session[global_settings.LANGUAGE_SESSION_KEY] = form.cleaned_data['language']

            messages.success(request, _('تم حفظ الإعدادات بنجاح'))
            return redirect('inventory:system_settings')
    else:
        form = LocalSystemSettingsForm(instance=settings)

    return render(request, 'inventory/system_settings.html', {
        'form': form,
        'settings': settings,
    })

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

# Debug view for form submission
@login_required
def debug_form_submission(request):
    """
    نقطة نهاية للتحقق من إرسال النماذج
    """
    if request.method == 'POST':
        # Log all POST data
        print("="*50)
        print("DEBUG FORM SUBMISSION")
        print("="*50)
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        # Log all FILES data
        if request.FILES:
            print("="*50)
            print("FILES:")
            for key, value in request.FILES.items():
                print(f"{key}: {value}")

        # Create a response with all the data
        response_data = {
            'post_data': dict(request.POST),
            'files_data': {k: v.name for k, v in request.FILES.items()},
            'success': True,
            'message': 'Form data received successfully'
        }

        # Return as JSON
        return JsonResponse(response_data)

    # If not POST, return a simple form
    return render(request, 'inventory/debug_form.html')

# نموذج بسيط لإضافة منتج
@login_required
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
