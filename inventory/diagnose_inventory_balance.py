"""
Diagnostic tool to identify inventory balance inconsistencies
This script checks for mismatches between stored product quantities and
calculated quantities based on movement history.
"""

import os
import sys
import django
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from inventory.models_local import Product, Voucher, VoucherItem
from django.db import transaction
from django.db.models import Sum, F, Q

def check_product_balance_consistency():
    """
    Check for inconsistencies between stored product quantities and
    calculated quantities based on movement history.
    """
    print("=== Checking Product Balance Consistency ===")
    
    # Get all products with movement history
    products_with_movements = Product.objects.filter(
        voucher_items__isnull=False
    ).distinct()
    
    print(f"Found {products_with_movements.count()} products with movement history")
    
    inconsistent_products = []
    
    for product in products_with_movements:
        # Calculate expected quantity from movement history
        initial_quantity = product.initial_quantity
        
        # Get all voucher items for this product
        voucher_items = VoucherItem.objects.filter(
            product=product
        ).select_related('voucher')
        
        # Calculate the expected quantity based on movement history
        calculated_quantity = initial_quantity
        movement_details = []
        
        for item in voucher_items.order_by('voucher__date', 'voucher__created_at'):
            voucher_type = item.voucher.voucher_type
            
            if voucher_type in ['إذن اضافة', 'اذن مرتجع عميل'] and item.quantity_added:
                calculated_quantity += item.quantity_added
                movement_details.append({
                    'voucher_number': item.voucher.voucher_number,
                    'voucher_type': voucher_type,
                    'date': item.voucher.date,
                    'action': 'add',
                    'quantity': item.quantity_added,
                    'running_total': calculated_quantity
                })
            elif voucher_type in ['إذن صرف', 'إذن مرتجع مورد'] and item.quantity_disbursed:
                calculated_quantity -= item.quantity_disbursed
                movement_details.append({
                    'voucher_number': item.voucher.voucher_number,
                    'voucher_type': voucher_type,
                    'date': item.voucher.date,
                    'action': 'subtract',
                    'quantity': item.quantity_disbursed,
                    'running_total': calculated_quantity
                })
        
        # Compare calculated quantity with stored quantity
        stored_quantity = product.quantity
        
        if abs(stored_quantity - calculated_quantity) > Decimal('0.001'):
            inconsistent_products.append({
                'product': product,
                'stored_quantity': stored_quantity,
                'calculated_quantity': calculated_quantity,
                'difference': stored_quantity - calculated_quantity,
                'movement_details': movement_details
            })
    
    return inconsistent_products

def display_inconsistencies(inconsistent_products):
    """Display detailed information about inconsistent products"""
    print(f"\n=== Found {len(inconsistent_products)} Products with Inconsistent Balances ===")
    
    if not inconsistent_products:
        print("✅ All product balances are consistent with their movement history!")
        return
    
    for i, inconsistency in enumerate(inconsistent_products, 1):
        product = inconsistency['product']
        print(f"\n{i}. Product: {product.name} ({product.product_id})")
        print(f"   Initial Quantity: {product.initial_quantity}")
        print(f"   Current Stored Quantity: {inconsistency['stored_quantity']}")
        print(f"   Calculated Quantity: {inconsistency['calculated_quantity']}")
        print(f"   Difference: {inconsistency['difference']} (stored - calculated)")
        
        print(f"\n   Movement History:")
        for detail in inconsistency['movement_details']:
            action_symbol = '+' if detail['action'] == 'add' else '-'
            print(f"     {detail['date']} | {detail['voucher_number']} | {detail['voucher_type']} | {action_symbol}{detail['quantity']} = {detail['running_total']}")

def check_voucher_item_integrity():
    """Check for data integrity issues in voucher items"""
    print("\n=== Checking Voucher Item Data Integrity ===")
    
    # Check for voucher items with both quantity_added and quantity_disbursed
    dual_quantity_items = VoucherItem.objects.filter(
        quantity_added__isnull=False,
        quantity_disbursed__isnull=False,
        quantity_added__gt=0,
        quantity_disbursed__gt=0
    )
    
    if dual_quantity_items.exists():
        print(f"⚠️  Found {dual_quantity_items.count()} voucher items with both added and disbursed quantities")
        for item in dual_quantity_items[:5]:  # Show first 5
            print(f"   - Voucher: {item.voucher.voucher_number}, Product: {item.product.name}")
            print(f"     Added: {item.quantity_added}, Disbursed: {item.quantity_disbursed}")
    else:
        print("✅ No voucher items with both added and disbursed quantities")
    
    # Check for voucher items with neither quantity
    no_quantity_items = VoucherItem.objects.filter(
        Q(quantity_added__isnull=True) | Q(quantity_added=0),
        Q(quantity_disbursed__isnull=True) | Q(quantity_disbursed=0)
    )
    
    if no_quantity_items.exists():
        print(f"\n⚠️  Found {no_quantity_items.count()} voucher items with no quantities")
        for item in no_quantity_items[:5]:  # Show first 5
            print(f"   - Voucher: {item.voucher.voucher_number}, Product: {item.product.name}")
    else:
        print("✅ No voucher items with missing quantities")
    
    # Check for voucher type mismatches
    type_mismatches = []
    
    addition_with_disbursed = VoucherItem.objects.filter(
        voucher__voucher_type__in=['إذن اضافة', 'اذن مرتجع عميل'],
        quantity_disbursed__isnull=False,
        quantity_disbursed__gt=0
    )
    if addition_with_disbursed.exists():
        type_mismatches.append(f"Addition vouchers with disbursed quantities: {addition_with_disbursed.count()}")
        for item in addition_with_disbursed[:3]:
            type_mismatches.append(f"  - {item.voucher.voucher_number}: {item.product.name}, Disbursed: {item.quantity_disbursed}")
    
    withdrawal_with_added = VoucherItem.objects.filter(
        voucher__voucher_type__in=['إذن صرف', 'إذن مرتجع مورد'],
        quantity_added__isnull=False,
        quantity_added__gt=0
    )
    if withdrawal_with_added.exists():
        type_mismatches.append(f"Withdrawal vouchers with added quantities: {withdrawal_with_added.count()}")
        for item in withdrawal_with_added[:3]:
            type_mismatches.append(f"  - {item.voucher.voucher_number}: {item.product.name}, Added: {item.quantity_added}")
    
    if type_mismatches:
        print("\n⚠️  Found voucher type mismatches:")
        for mismatch in type_mismatches:
            print(f"   {mismatch}")
    else:
        print("✅ No voucher type mismatches found")

def check_negative_quantities():
    """Check for products with negative quantities"""
    print("\n=== Checking for Negative Quantities ===")
    
    negative_products = Product.objects.filter(quantity__lt=0)
    
    if negative_products.exists():
        print(f"⚠️  Found {negative_products.count()} products with negative quantities:")
        for product in negative_products:
            print(f"   - {product.name} ({product.product_id}): {product.quantity}")
    else:
        print("✅ No products with negative quantities found")

def main():
    """Main function to run all diagnostic checks"""
    print("Starting Inventory Balance Diagnostic...")
    print("=" * 70)
    
    # Check product balance consistency
    inconsistent_products = check_product_balance_consistency()
    display_inconsistencies(inconsistent_products)
    
    # Check voucher item integrity
    check_voucher_item_integrity()
    
    # Check for negative quantities
    check_negative_quantities()
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 70)
    
    if inconsistent_products:
        print(f"⚠️  Found {len(inconsistent_products)} products with inconsistent balances")
        print("   This is likely the root cause of the inventory balance issue")
        print("   Run the fix_inventory_balance.py script to correct these inconsistencies")
    else:
        print("✅ All product balances are consistent with their movement history")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
