from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models_local import Product, Voucher, VoucherItem

class VoucherHandler:
    @staticmethod
    def handle_voucher_deletion(voucher):
        """
        معالجة حذف الإذن وتحديث أرصدة الأصناف
        عند حذف الإذن، يتم عكس تأثيره على أرصدة الأصناف:
        - إذن إضافة: خصم الكمية المضافة من الرصيد الحالي
        - إذن صرف: إضافة الكمية المنصرفة إلى الرصيد الحالي
        - إذن مرتجع عميل: خصم الكمية المضافة من الرصيد الحالي
        - إذن مرتجع مورد: إضافة الكمية المنصرفة إلى الرصيد الحالي
        """
        with transaction.atomic():
            updated_products = []

            for item in voucher.items.all():
                product = item.product
                original_quantity = product.quantity

                if voucher.voucher_type == 'إذن اضافة':
                    # عكس الإضافة - خصم الكمية المضافة
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن صرف':
                    # عكس الصرف - إضافة الكمية المنصرفة
                    product.quantity += item.quantity_disbursed or 0
                elif voucher.voucher_type == 'اذن مرتجع عميل':
                    # عكس مرتجع العميل - خصم الكمية المضافة
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن مرتجع مورد':
                    # عكس مرتجع المورد - إضافة الكمية المنصرفة
                    product.quantity += item.quantity_disbursed or 0

                # التحقق من أن الكمية لا تقل عن صفر
                if product.quantity < 0:
                    raise ValidationError(
                        f"لا يمكن حذف الإذن لأن ذلك سيؤدي إلى رصيد سالب للصنف {product.name} (الرصيد الحالي: {original_quantity})"
                    )

                product.save()
                updated_products.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'old_quantity': original_quantity,
                    'new_quantity': product.quantity,
                    'difference': product.quantity - original_quantity
                })

            return updated_products

    @staticmethod
    def handle_voucher_update(voucher, old_items, new_items_data):
        """
        معالجة تحديث الإذن وتحديث أرصدة الأصناف

        عند تعديل الإذن، يتم:
        1. عكس تأثير الأصناف المحذوفة
        2. تحديث الأصناف الموجودة بناءً على فرق الكمية
        3. إضافة تأثير الأصناف الجديدة

        يتم التعامل مع كل نوع إذن بشكل مختلف:
        - إذن إضافة: زيادة الرصيد عند الإضافة، خفض الرصيد عند الحذف
        - إذن صرف: خفض الرصيد عند الإضافة، زيادة الرصيد عند الحذف
        - إذن مرتجع عميل: زيادة الرصيد عند الإضافة، خفض الرصيد عند الحذف
        - إذن مرتجع مورد: خفض الرصيد عند الإضافة، زيادة الرصيد عند الحذف
        """
        with transaction.atomic():
            updated_products = []

            # 1. معالجة الأصناف المحذوفة - عكس تأثيرها
            current_product_ids = {str(item['product_id']) for item in new_items_data}
            for old_item in old_items:
                product = old_item.product
                original_quantity = product.quantity

                if str(product.product_id) not in current_product_ids:
                    # تم حذف الصنف - عكس تأثيره
                    if voucher.voucher_type == 'إذن اضافة':
                        # عكس الإضافة - خصم الكمية المضافة
                        product.quantity -= old_item.quantity_added or 0
                    elif voucher.voucher_type == 'إذن صرف':
                        # عكس الصرف - إضافة الكمية المنصرفة
                        product.quantity += old_item.quantity_disbursed or 0
                    elif voucher.voucher_type == 'اذن مرتجع عميل':
                        # عكس مرتجع العميل - خصم الكمية المضافة
                        product.quantity -= old_item.quantity_added or 0
                    elif voucher.voucher_type == 'إذن مرتجع مورد':
                        # عكس مرتجع المورد - إضافة الكمية المنصرفة
                        product.quantity += old_item.quantity_disbursed or 0

                    # التحقق من أن الكمية لا تقل عن صفر
                    if product.quantity < 0:
                        raise ValidationError(
                            f"لا يمكن حذف الصنف {product.name} من الإذن لأن ذلك سيؤدي إلى رصيد سالب (الرصيد الحالي: {original_quantity})"
                        )

                    product.save()
                    updated_products.append({
                        'product_id': product.product_id,
                        'name': product.name,
                        'action': 'حذف',
                        'old_quantity': original_quantity,
                        'new_quantity': product.quantity,
                        'difference': product.quantity - original_quantity
                    })

            # حذف جميع الأصناف الحالية من الإذن
            voucher.items.all().delete()

            # 2. معالجة الأصناف الجديدة/المحدثة
            for item_data in new_items_data:
                product = get_object_or_404(Product, product_id=item_data['product_id'])
                quantity = Decimal(item_data['quantity'])
                original_quantity = product.quantity

                # البحث عن الصنف في الأصناف القديمة
                old_item = next((item for item in old_items if str(item.product.product_id) == str(item_data['product_id'])), None)

                # حساب التغيير في الرصيد
                if old_item:
                    # تعديل صنف موجود
                    if voucher.voucher_type == 'إذن اضافة':
                        old_qty = old_item.quantity_added or 0
                        diff = quantity - old_qty
                        product.quantity += diff
                    elif voucher.voucher_type == 'إذن صرف':
                        old_qty = old_item.quantity_disbursed or 0
                        diff = quantity - old_qty
                        product.quantity -= diff
                    elif voucher.voucher_type == 'اذن مرتجع عميل':
                        old_qty = old_item.quantity_added or 0
                        diff = quantity - old_qty
                        product.quantity += diff
                    elif voucher.voucher_type == 'إذن مرتجع مورد':
                        old_qty = old_item.quantity_disbursed or 0
                        diff = quantity - old_qty
                        product.quantity -= diff

                    action = 'تعديل'
                else:
                    # صنف جديد
                    if voucher.voucher_type == 'إذن اضافة':
                        product.quantity += quantity
                    elif voucher.voucher_type == 'إذن صرف':
                        product.quantity -= quantity
                    elif voucher.voucher_type == 'اذن مرتجع عميل':
                        product.quantity += quantity
                    elif voucher.voucher_type == 'إذن مرتجع مورد':
                        product.quantity -= quantity

                    action = 'إضافة'

                # التحقق من أن الكمية لا تقل عن صفر
                if product.quantity < 0:
                    raise ValidationError(
                        f"لا يمكن {action} الصنف {product.name} بالكمية المحددة لأن ذلك سيؤدي إلى رصيد سالب (الرصيد الحالي: {original_quantity})"
                    )

                # إنشاء عنصر إذن جديد
                item = VoucherItem(voucher=voucher, product=product)
                if voucher.voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                    item.quantity_added = quantity
                else:
                    item.quantity_disbursed = quantity

                if voucher.voucher_type == 'إذن صرف':
                    item.machine = item_data.get('machine', '')
                    item.machine_unit = item_data.get('machine_unit', '')

                product.save()
                item.save()

                updated_products.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'action': action,
                    'old_quantity': original_quantity,
                    'new_quantity': product.quantity,
                    'difference': product.quantity - original_quantity
                })

            return updated_products

    @staticmethod
    def handle_voucher_creation(voucher, items_data):
        """
        معالجة إنشاء إذن جديد وتحديث أرصدة الأصناف

        عند إنشاء إذن جديد، يتم تحديث أرصدة الأصناف بناءً على نوع الإذن:
        - إذن إضافة: زيادة الرصيد الحالي
        - إذن صرف: خفض الرصيد الحالي
        - إذن مرتجع عميل: زيادة الرصيد الحالي
        - إذن مرتجع مورد: خفض الرصيد الحالي
        """
        with transaction.atomic():
            updated_products = []

            for item_data in items_data:
                product = get_object_or_404(Product, product_id=item_data['product_id'])
                quantity = Decimal(item_data['quantity'])
                original_quantity = product.quantity

                # إنشاء عنصر إذن جديد
                item = VoucherItem(voucher=voucher, product=product)

                if voucher.voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                    item.quantity_added = quantity
                    product.quantity += quantity
                else:
                    item.quantity_disbursed = quantity
                    product.quantity -= quantity

                    # التحقق من أن الكمية لا تقل عن صفر للإذونات التي تخفض الرصيد
                    if product.quantity < 0:
                        raise ValidationError(
                            f"لا يمكن إضافة الصنف {product.name} بالكمية المحددة لأن ذلك سيؤدي إلى رصيد سالب (الرصيد الحالي: {original_quantity})"
                        )

                if voucher.voucher_type == 'إذن صرف':
                    item.machine = item_data.get('machine', '')
                    item.machine_unit = item_data.get('machine_unit', '')

                product.save()
                item.save()

                updated_products.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'action': 'إضافة',
                    'old_quantity': original_quantity,
                    'new_quantity': product.quantity,
                    'difference': product.quantity - original_quantity
                })

            return updated_products

    @staticmethod
    def prepare_items_data(request, voucher_type):
        """تحضير بيانات الأصناف من بيانات الطلب"""
        items_data = []
        
        # تحقق من نمط تسمية الحقول (Django formset أو arrays باستخدام [])
        if any(key.startswith('form-') for key in request.POST.keys()):
            # نمط Django formset
            # حساب عدد العناصر في النموذج
            form_count = 0
            while f'form-{form_count}-product' in request.POST:
                form_count += 1
            
            for i in range(form_count):
                product_id = request.POST.get(f'form-{i}-product')
                quantity = request.POST.get(f'form-{i}-quantity')
                machine = request.POST.get(f'form-{i}-machine_name', '')
                machine_unit = request.POST.get(f'form-{i}-machine_unit', '')
                
                if product_id and quantity:
                    item_data = {
                        'product_id': product_id,
                        'quantity': quantity,
                    }
                    
                    if voucher_type == 'إذن صرف':
                        item_data['machine'] = machine
                        item_data['machine_unit'] = machine_unit
                    
                    items_data.append(item_data)
        else:
            # نمط المصفوفات (Arrays)
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            machines = request.POST.getlist('machine[]')
            machine_units = request.POST.getlist('machine_unit[]')
            
            for i in range(len(product_ids)):
                if not product_ids[i] or not quantities[i]:
                    continue
                
                item_data = {
                    'product_id': product_ids[i],
                    'quantity': quantities[i],
                }
                
                if voucher_type == 'إذن صرف':
                    item_data['machine'] = machines[i] if i < len(machines) else ''
                    item_data['machine_unit'] = machine_units[i] if i < len(machine_units) else ''
                
                items_data.append(item_data)


        return items_data
