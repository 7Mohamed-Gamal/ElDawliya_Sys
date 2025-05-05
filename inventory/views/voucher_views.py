"""
Voucher views for the inventory application.
"""
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, F
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from datetime import datetime

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import (
    Product, Voucher, VoucherItem, Supplier, Customer, Department
)
from inventory.forms import VoucherForm
from inventory.voucher_handlers import VoucherHandler

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
        voucher_type = self.request.GET.get('type', 'إذن اضافة')

        # Set page title based on voucher type
        if voucher_type == 'إذن اضافة':
            context['page_title'] = 'إضافة إذن اضافة'
        elif voucher_type == 'إذن صرف':
            context['page_title'] = 'إضافة إذن صرف'
        elif voucher_type == 'اذن مرتجع عميل':
            context['page_title'] = 'إضافة إذن مرتجع عميل'
        elif voucher_type == 'إذن مرتجع مورد':
            context['page_title'] = 'إضافة إذن مرتجع مورد'
        else:
            context['page_title'] = 'إضافة إذن جديد'

        context['today'] = timezone.now().date().strftime('%Y-%m-%d')
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')
        context['voucher_type'] = voucher_type
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

            # Prepare items data
            items_data = VoucherHandler.prepare_items_data(self.request, voucher.voucher_type)

            # Use the handler to handle the creation
            updated_products = VoucherHandler.handle_voucher_creation(voucher, items_data)

            # إنشاء رسالة نجاح مفصلة
            success_msg = f'تم إضافة الإذن {voucher.voucher_number} بنجاح'

            # إضافة تفاصيل الأصناف إذا كانت هناك أصناف
            if updated_products:
                items_count = len(updated_products)
                success_msg += f' مع {items_count} صنف'

                # إضافة معلومات عن تأثير الإذن على المخزون
                if voucher.voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                    success_msg += f' (تمت إضافة الكميات إلى المخزون)'
                else:
                    success_msg += f' (تم خصم الكميات من المخزون)'

            messages.success(self.request, success_msg)
            return response

        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'حدث خطأ أثناء إضافة الإذن: {str(e)}')
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

        # Set page title based on voucher type
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

        context['today'] = timezone.now().date().strftime('%Y-%m-%d')
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')
        context['voucher_type'] = voucher.voucher_type
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
            old_items = list(voucher.items.all())

            # Save the updated voucher first
            response = super().form_valid(form)
            voucher = self.object

            # Prepare new items data
            new_items_data = VoucherHandler.prepare_items_data(self.request, voucher.voucher_type)

            # Use the handler to handle the update
            updated_products = VoucherHandler.handle_voucher_update(voucher, old_items, new_items_data)

            # إنشاء رسالة نجاح مفصلة
            success_msg = f'تم تعديل الإذن {voucher.voucher_number} بنجاح وتحديث أرصدة الأصناف المرتبطة به.'

            # إضافة تفاصيل التغييرات إذا كانت هناك تغييرات
            if updated_products:
                # عرض عدد الأصناف التي تم تعديلها
                added_count = sum(1 for p in updated_products if p['action'] == 'إضافة')
                modified_count = sum(1 for p in updated_products if p['action'] == 'تعديل')
                deleted_count = sum(1 for p in updated_products if p['action'] == 'حذف')

                details = []
                if added_count > 0:
                    details.append(f'تمت إضافة {added_count} صنف جديد')
                if modified_count > 0:
                    details.append(f'تم تعديل {modified_count} صنف')
                if deleted_count > 0:
                    details.append(f'تم حذف {deleted_count} صنف')

                if details:
                    success_msg += f' ({", ".join(details)})'

            messages.success(self.request, success_msg)
            return response

        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
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
            updated_products = VoucherHandler.handle_voucher_deletion(voucher)
            response = super().delete(request, *args, **kwargs)

            # إنشاء رسالة نجاح مفصلة
            success_msg = f'تم حذف الإذن {voucher.voucher_number} بنجاح وتحديث أرصدة الأصناف المرتبطة به.'
            messages.success(request, success_msg)

            return response
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('inventory:voucher_detail', pk=voucher.voucher_number)
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
                print(f"Found voucher by ID: {obj.voucher_number}, Type: {obj.voucher_type}")
                return obj
            except (Voucher.DoesNotExist, ValueError):
                # إذا فشل البحث بالمعرف، نحاول البحث برقم الإذن
                obj = queryset.get(voucher_number=pk)
                print(f"Found voucher by number: {obj.voucher_number}, Type: {obj.voucher_type}")
                return obj
        except Voucher.DoesNotExist:
            raise Http404("لا يوجد إذن بهذا الرقم")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.object

        print(f"Preparing context for voucher: {voucher.voucher_number}")

        # الحصول على عناصر الإذن باستخدام استعلام مباشر
        # استخدام استعلام مباشر بدلاً من العلاقة العكسية
        voucher_items = VoucherItem.objects.filter(voucher=voucher).select_related('product', 'product__unit')

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
