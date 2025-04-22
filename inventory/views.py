from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, F, Sum, Count
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import codecs
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.conf import global_settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_module_permission_required, inventory_class_permission_required

# استيراد النماذج المحلية
from inventory.models_local import (
    Category, Product, Supplier, Customer,
    Invoice, InvoiceItem, LocalSystemSettings
)

# استيراد النماذج
from inventory.forms import (
    ProductForm, CustomerForm, CategoryForm, SupplierForm,
    InvoiceForm, InvoiceItemForm, LocalSystemSettingsForm
)

@login_required
@inventory_module_permission_required('dashboard', 'view')
def dashboard(request):
    """عرض لوحة تحكم المخزن"""
    try:
        # إحصائيات الفواتير
        pending_permits = Invoice.objects.filter(invoice_type='إضافة').count()
        completed_permits = Invoice.objects.filter(invoice_type='صرف').count()
        total_permits = Invoice.objects.count()

        # الأصناف التي تحت الحد الأدنى
        low_stock = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        )

        context = {
            'pending_permits': pending_permits,
            'completed_permits': completed_permits,
            'total_permits': total_permits,
            'low_stock': low_stock,
            'low_stock_count': low_stock.count(),
            'title': 'لوحة تحكم المخزن'
        }

        return render(request, 'inventory/dashboard_inventory.html', context)
    except Exception as e:
        # في حالة وجود خطأ في الاتصال بقاعدة البيانات أو أي خطأ آخر
        messages.error(request, f'حدث خطأ: {str(e)}')
        context = {
            'error_message': str(e),
            'title': 'لوحة تحكم المخزن',
            'low_stock_count': 0,
            'pending_permits': 0,
            'completed_permits': 0,
            'total_permits': 0,
            'low_stock': []
        }
        return render(request, 'inventory/dashboard_inventory.html', context)

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
        # Add page title
        context['page_title'] = 'إضافة صنف جديد'
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'edit')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

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

# إدارة الموردين (Suppliers)
class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

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
