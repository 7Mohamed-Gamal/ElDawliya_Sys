from django.db import transaction
from django.shortcuts import get_object_or_404
from .models_local import Product, Voucher, VoucherItem

class InventoryTransactionService:
    @staticmethod
    def handle_voucher_deletion(voucher):
        """
        Handle the deletion of a voucher by reversing its effects on product quantities
        """
        with transaction.atomic():
            for item in voucher.items.all():
                product = item.product
                
                if voucher.voucher_type == 'إذن اضافة':
                    # Reverse addition - subtract the added quantity
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن صرف':
                    # Reverse disbursement - add back the disbursed quantity
                    product.quantity += item.quantity_disbursed or 0
                elif voucher.voucher_type == 'اذن مرتجع عميل':
                    # Reverse client return - subtract the added quantity
                    product.quantity -= item.quantity_added or 0
                elif voucher.voucher_type == 'إذن مرتجع مورد':
                    # Reverse supplier return - add back the quantity
                    product.quantity += item.quantity_disbursed or 0
                
                product.save()

    @staticmethod
    def handle_voucher_update(voucher, old_items, new_items_data):
        """
        Handle the update of a voucher by:
        1. Reversing removed items' effects
        2. Updating existing items
        3. Adding new items
        """
        with transaction.atomic():
            # Track removed items and reverse their effects
            current_product_ids = {item['product_id'] for item in new_items_data}
            for old_item in old_items:
                if str(old_item.product.product_id) not in current_product_ids:
                    # Item was removed - reverse its effects
                    if voucher.voucher_type == 'إذن اضافة':
                        old_item.product.quantity -= old_item.quantity_added or 0
                    elif voucher.voucher_type == 'إذن صرف':
                        old_item.product.quantity += old_item.quantity_disbursed or 0
                    elif voucher.voucher_type == 'اذن مرتجع عميل':
                        old_item.product.quantity -= old_item.quantity_added or 0
                    elif voucher.voucher_type == 'إذن مرتجع مورد':
                        old_item.product.quantity += old_item.quantity_disbursed or 0
                    old_item.product.save()
            
            # Delete all current items
            voucher.items.all().delete()
            
            # Process new/updated items
            for item_data in new_items_data:
                product = get_object_or_404(Product, product_id=item_data['product_id'])
                quantity = float(item_data['quantity'])
                
                # Find if this product was in old items
                old_item = next((item for item in old_items if item.product.product_id == item_data['product_id']), None)
                
                # Calculate quantity difference if item existed before
                if old_item:
                    if voucher.voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                        old_qty = old_item.quantity_added or 0
                        diff = quantity - old_qty
                        product.quantity += diff
                    else:
                        old_qty = old_item.quantity_disbursed or 0
                        diff = quantity - old_qty
                        product.quantity -= diff
                else:
                    # New item
                    if voucher.voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                        product.quantity += quantity
                    else:
                        product.quantity -= quantity
                
                # Create new voucher item
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

    @staticmethod
    def handle_voucher_creation(voucher, items_data):
        """
        Handle the creation of a new voucher by adding items and updating product quantities
        """
        with transaction.atomic():
            for item_data in items_data:
                product = get_object_or_404(Product, product_id=item_data['product_id'])
                quantity = float(item_data['quantity'])
                
                # Create new voucher item
                item = VoucherItem(voucher=voucher, product=product)
                
                if voucher.voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                    item.quantity_added = quantity
                    product.quantity += quantity
                else:
                    item.quantity_disbursed = quantity
                    product.quantity -= quantity
                    
                if voucher.voucher_type == 'إذن صرف':
                    item.machine = item_data.get('machine', '')
                    item.machine_unit = item_data.get('machine_unit', '')
                
                product.save()
                item.save()