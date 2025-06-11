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

# ------------------- Dashboard -------------------

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

# ------------------- Products (الأصناف) -------------------

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
        context['low_stock_count'] = get_low_stock_count()
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
        context['categories'] = Category.objects.all()
        context['units'] = Unit.objects.all()
        context['page_title'] = 'إضافة صنف جديد'
        context['low_stock_count'] = get_low_stock_count()
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('vouchers', 'view')
class VoucherDetailView(DetailView):
    model = Voucher
    template_name = 'inventory/voucher_detail.html'
    context_object_name = 'voucher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()
        
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
        
        # إضافة تفاصيل العناصر
        context['voucher_items'] = voucher.items.all()
        
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
            if hasattr(form, 'set_required_fields'):
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
        
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        try:
            # Save the form to create the voucher
            response = super().form_valid(form)
            voucher = self.object
            
            # Get the total number of forms from the formset management form
            total_forms = int(self.request.POST.get('form-TOTAL_FORMS', 0))
            
            # تتبع عدد العناصر التي تمت إضافتها
            items_added = 0
            
            # Process each form in the formset
            for i in range(total_forms):
                # Get product code and product ID from the form
                product_code = self.request.POST.get(f'form-{i}-product_code')
                product_id = self.request.POST.get(f'form-{i}-product')
                quantity = self.request.POST.get(f'form-{i}-quantity')
                
                # Skip if no product ID or quantity or quantity is 0
                if not product_id or not quantity:
                    continue
                
                try:
                    quantity_value = float(quantity)
                    if quantity_value <= 0:
                        continue
                except (ValueError, TypeError):
                    continue
                
                # Get the product (first try by product_id field, then by code if that doesn't work)
                try:
                    # First attempt to get by product_id (primary key)
                    product = Product.objects.get(product_id=product_id)
                except Product.DoesNotExist:
                    try:
                        # If that fails, try using the product code
                        if product_code:
                            product = Product.objects.get(product_id=product_code)
                        else:
                            continue
                    except Product.DoesNotExist:
                        continue
                
                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)
                
                # Set the appropriate quantity field and update product quantity based on voucher type
                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    item.quantity_added = quantity_value
                    # Update product quantity - add quantity
                    product.quantity += quantity_value
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # For disbursement vouchers or supplier return vouchers
                    item.quantity_disbursed = quantity_value
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                
                # Set unit price from product
                item.unit_price = product.unit_price
                
                # Set machine and machine unit for disbursement vouchers
                if voucher.voucher_type == 'إذن صرف':
                    item.machine = self.request.POST.get(f'form-{i}-machine_name', '')
                    item.machine_unit = self.request.POST.get(f'form-{i}-machine_unit', '')
                
                # Save the updated product and the voucher item
                product.save()
                item.save()
                items_added += 1
            
            # إذا لم يتم إضافة أي عناصر، أضف رسالة تحذير
            if items_added == 0:
                messages.warning(self.request, 'تم إضافة الإذن بنجاح، ولكن لم يتم إضافة أي أصناف. يرجى التحقق من الأصناف المضافة.')
            else:
                messages.success(self.request, f'تم إضافة الإذن بنجاح مع {items_added} صنف. رقم الإذن: {voucher.voucher_number}')
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
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
        
        context['low_stock_count'] = get_low_stock_count()
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
            
            # Get the total number of forms from the formset management form
            total_forms = int(self.request.POST.get('form-TOTAL_FORMS', 0))
            
            # تتبع عدد العناصر التي تمت إضافتها
            items_added = 0
            
            # Process each form in the formset
            for i in range(total_forms):
                # Get product code and product ID from the form
                product_code = self.request.POST.get(f'form-{i}-product_code')
                product_id = self.request.POST.get(f'form-{i}-product')
                quantity = self.request.POST.get(f'form-{i}-quantity')
                
                # Skip if no product ID or quantity or quantity is 0
                if not product_id or not quantity:
                    continue
                
                try:
                    quantity_value = float(quantity)
                    if quantity_value <= 0:
                        continue
                except (ValueError, TypeError):
                    continue
                
                # Get the product
                try:
                    product = Product.objects.get(product_id=product_id)
                except Product.DoesNotExist:
                    try:
                        # If that fails, try using the product code
                        if product_code:
                            product = Product.objects.get(product_id=product_code)
                        else:
                            continue
                    except Product.DoesNotExist:
                        continue
                
                # Create the voucher item
                item = VoucherItem(voucher=voucher, product=product)
                
                # Set the appropriate quantity field and update product quantity based on voucher type
                if voucher.voucher_type == 'إذن اضافة' or voucher.voucher_type == 'اذن مرتجع عميل':
                    # For addition vouchers or client return vouchers
                    item.quantity_added = quantity_value
                    # Update product quantity - add quantity
                    product.quantity += quantity_value
                elif voucher.voucher_type == 'إذن صرف' or voucher.voucher_type == 'إذن مرتجع مورد':
                    # For disbursement vouchers or supplier return vouchers
                    item.quantity_disbursed = quantity_value
                    # Update product quantity - subtract quantity
                    product.quantity -= quantity_value
                
                # Set unit price from product
                item.unit_price = product.unit_price
                
                # Set machine and machine unit for disbursement vouchers
                if voucher.voucher_type == 'إذن صرف':
                    item.machine = self.request.POST.get(f'form-{i}-machine_name', '')
                    item.machine_unit = self.request.POST.get(f'form-{i}-machine_unit', '')
                
                # Save the updated product and the voucher item
                product.save()
                item.save()
                items_added += 1
            
            # إذا لم يتم إضافة أي عناصر، أضف رسالة تحذير
            if items_added == 0:
                messages.warning(self.request, 'تم تعديل الإذن بنجاح، ولكن لم يتم إضافة أي أصناف. يرجى التحقق من الأصناف المضافة.')
            else:
                messages.success(self.request, f'تم تعديل الإذن بنجاح مع {items_added} صنف. رقم الإذن: {voucher.voucher_number}')
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
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
            
            # Delete voucher
            messages.success(request, 'تم حذف الإذن بنجاح')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف الإذن: {str(e)}')
            return redirect('inventory:voucher_list')

    def form_valid(self, form):
        try:
            # عند إنشاء منتج جديد، نقوم بتعيين الرصيد الحالي من الرصيد الافتتاحي
            initial_quantity = form.cleaned_data.get('initial_quantity', 0)
            current_quantity = form.cleaned_data.get('quantity', 0)

            # إذا كان الرصيد الافتتاحي موجود ولكن الرصيد الحالي غير موجود
            if initial_quantity and not current_quantity:
                form.instance.quantity = initial_quantity
            # إذا كان الرصيد الحالي موجود ولكن الرصيد الافتتاحي غير موجود
            elif current_quantity and not initial_quantity:
                form.instance.initial_quantity = current_quantity
            # إذا كانت القيمتان مختلفتان، نستخدم الرصيد الافتتاحي
            elif initial_quantity != current_quantity:
                form.instance.quantity = initial_quantity

            # معالجة التصنيف الجديد إذا تم إدخاله
            new_category = self.request.POST.get('new_category')
            new_category_name = self.request.POST.get('new_category_name')

            if new_category == 'true' and new_category_name:
                category = Category.objects.create(
                    name=new_category_name,
                    description=self.request.POST.get('new_category_description', '')
                )
                form.instance.category = category

            # معالجة وحدة القياس الجديدة إذا تم إدخالها
            new_unit = self.request.POST.get('new_unit')
            new_unit_name = self.request.POST.get('new_unit_name')
            unit_value = self.request.POST.get('unit')

            if new_unit == 'true' and new_unit_name:
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
                    pass

            # إنشاء رقم منتج تلقائي إذا لم يتم توفيره
            if not form.instance.product_id:
                form.instance.product_id = f"P{timezone.now().strftime('%Y%m%d%H%M%S')}"

            # حفظ المنتج
            product = form.save()
            
            # إظهار رسالة نجاح
            name = form.cleaned_data.get('name')
            messages.success(self.request, f'تم إضافة الصنف "{name}" بنجاح')

            return super().form_valid(form)
        except Exception as e:
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
        context['categories'] = Category.objects.all()
        context['units'] = Unit.objects.all()
        context['page_title'] = 'تعديل الصنف'
        context['low_stock_count'] = get_low_stock_count()
        return context

    def form_valid(self, form):
        try:
            # Check if we need to create a new category
            new_category = self.request.POST.get('new_category')
            new_category_name = self.request.POST.get('new_category_name')

            if new_category == 'true' and new_category_name:
                # Create new category
                category = Category.objects.create(
                    name=new_category_name,
                    description=self.request.POST.get('new_category_description', '')
                )
                # Set the new category to the product
                form.instance.category = category

            # Check if we need to create a new unit
            new_unit = self.request.POST.get('new_unit')
            new_unit_name = self.request.POST.get('new_unit_name')
            unit_value = self.request.POST.get('unit')

            # If the unit dropdown has "new" selected
            if unit_value == "new" or new_unit == 'true':
                # Get the unit name and symbol from the request directly
                direct_unit_name = self.request.POST.get('new_unit_name')
                direct_unit_symbol = self.request.POST.get('new_unit_symbol')

                # Create new unit with valid values
                unit_name = direct_unit_name or new_unit_name or "وحدة جديدة"
                unit_symbol = direct_unit_symbol or self.request.POST.get('new_unit_symbol', '')
                
                unit = Unit.objects.create(
                    name=unit_name,
                    symbol=unit_symbol
                )
                # Set the new unit to the product
                form.instance.unit = unit
            elif unit_value and unit_value != "":
                # If a regular unit is selected
                try:
                    unit_id = int(unit_value)
                    unit = Unit.objects.get(id=unit_id)
                    form.instance.unit = unit
                except (ValueError, Unit.DoesNotExist):
                    pass

            messages.success(self.request, 'تم تعديل الصنف بنجاح')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'حدث خطأ أثناء تعديل الصنف: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'delete')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')

# ------------------- Customers (العملاء) -------------------

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'view')
class CustomerListView(ListView):
    model = Customer
    template_name = 'inventory/customer_list.html'
    context_object_name = 'customers'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة العملاء'
        context['low_stock_count'] = get_low_stock_count()
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'add')
class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة عميل جديد'
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة العميل بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'edit')
class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'inventory/customer_form.html'
    success_url = reverse_lazy('inventory:customer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل العميل'
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل العميل بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('customers', 'delete')
class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'inventory/customer_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف العميل بنجاح')
        return super().delete(request, *args, **kwargs)

# ------------------- Categories (التصنيفات) -------------------

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'view')
class CategoryListView(ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة التصنيفات'
        context['low_stock_count'] = get_low_stock_count()
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'add')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة تصنيف جديد'
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة التصنيف بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'edit')
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تعديل التصنيف'
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل التصنيف بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('categories', 'delete')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف التصنيف بنجاح')
        return super().delete(request, *args, **kwargs)

# ------------------- Units (وحدات القياس) -------------------

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'view')
class UnitListView(ListView):
    model = Unit
    template_name = 'inventory/unit_list.html'
    context_object_name = 'units'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة وحدات القياس'
        context['low_stock_count'] = get_low_stock_count()
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'add')
class UnitCreateView(CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'inventory/unit_form.html'
    success_url = reverse_lazy('inventory:unit_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إضافة وحدة قياس جديدة'
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة وحدة القياس بنجاح')
        return super().form_valid(form)

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
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل وحدة القياس بنجاح')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('units', 'delete')
class UnitDeleteView(DeleteView):
    model = Unit
    template_name = 'inventory/unit_confirm_delete.html'
    success_url = reverse_lazy('inventory:unit_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف وحدة القياس بنجاح')
        return super().delete(request, *args, **kwargs)

# ------------------- Suppliers (الموردين) -------------------

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('suppliers', 'view')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الموردين'
        context['low_stock_count'] = get_low_stock_count()
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
        context['low_stock_count'] = get_low_stock_count()
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
        context['low_stock_count'] = get_low_stock_count()
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

# ------------------- Departments (الأقسام) -------------------

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('departments', 'view')
class DepartmentListView(ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأقسام'
        context['low_stock_count'] = get_low_stock_count()
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
        context['low_stock_count'] = get_low_stock_count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'تم إضافة القسم "{form.instance.name}" بنجاح')
        return super().form_valid(form)

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
        context['low_stock_count'] = get_low_stock_count()
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

# ------------------- Vouchers (الأذونات) -------------------

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
        
        # إحصائيات الأذونات للفلاتر الجانبية
        context['addition_count'] = Voucher.objects.filter(voucher_type='إذن اضافة').count()
        context['disbursement_count'] = Voucher.objects.filter(voucher_type='إذن صرف').count()
        context['client_return_count'] = Voucher.objects.filter(voucher_type='اذن مرتجع عميل').count()
        context['supplier_return_count'] = Voucher.objects.filter(voucher_type='إذن مرتجع مورد').count()
        
        context['low_stock_count'] = get_low_stock_count()
        return context
