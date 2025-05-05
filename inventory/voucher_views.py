from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import (
    Product, Voucher, Supplier, Customer, Department
)
from inventory.forms import VoucherForm
from inventory.voucher_handlers import VoucherHandler

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

        context['today'] = timezone.now().date().strftime('%Y-%m-%d')
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')
        context['voucher_type'] = voucher.voucher_type
        context['voucher_items'] = voucher.items.all()

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
@inventory_class_permission_required('vouchers', 'add')
class VoucherCreateView(CreateView):
    model = Voucher
    form_class = VoucherForm
    template_name = 'inventory/voucher_form.html'
    success_url = reverse_lazy('inventory:voucher_list')

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

        context['today'] = timezone.now().date().strftime('%Y-%m-%d')
        context['suppliers'] = Supplier.objects.all().order_by('name')
        context['departments'] = Department.objects.all().order_by('name')
        context['customers'] = Customer.objects.all().order_by('name')
        context['products'] = Product.objects.all().order_by('name')
        context['voucher_type'] = voucher_type
        context['voucher_items'] = []

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