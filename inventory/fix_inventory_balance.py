"""
Fix tool to synchronize stored product quantities with movement history
This script corrects discrepancies between stored product quantities and
calculated quantities based on movement history.
"""

import os
import sys
import django
from decimal import Decimal
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from inventory.models_local import Product, Voucher, VoucherItem
from django.db import transaction

def identify_inconsistent_products():
    """Identify products with quantity inconsistencies"""
    print("=== Identifying Products with Quantity Inconsistencies ===")
    
    # Get all products with movement history
    products_with_movements = Product.objects.filter(
        voucher_items__isnull=False
    ).distinct()
    
    print(f"Checking {products_with_movements.count()} products with movements...")
    
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

def create_backup_report(inconsistent_products):
    """Create a backup report of current state before fixing"""
    print("\n=== Creating Backup Report ===")
    
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'description': 'Backup of product quantities before inventory balance fix',
        'inconsistent_products': []
    }
    
    for inconsistency in inconsistent_products:
        product = inconsistency['product']
        backup_data['inconsistent_products'].append({
            'product_id': product.product_id,
            'product_name': product.name,
            'initial_quantity': float(product.initial_quantity),
            'stored_quantity': float(inconsistency['stored_quantity']),
            'calculated_quantity': float(inconsistency['calculated_quantity']),
            'difference': float(inconsistency['difference']),
            'movement_details': [
                {
                    'voucher_number': detail['voucher_number'],
                    'voucher_type': detail['voucher_type'],
                    'date': detail['date'].isoformat(),
                    'action': detail['action'],
                    'quantity': float(detail['quantity']),
                    'running_total': float(detail['running_total'])
                }
                for detail in inconsistency['movement_details']
            ]
        })
    
    backup_filename = f"inventory_balance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup report created: {backup_filename}")
        return backup_filename
    except Exception as e:
        print(f"❌ Error creating backup report: {e}")
        return None

def fix_quantity_inconsistencies(inconsistent_products, dry_run=True):
    """Fix quantity inconsistencies by updating stored quantities to match calculated ones"""
    print(f"\n=== {'DRY RUN: ' if dry_run else ''}Fixing Quantity Inconsistencies ===")
    
    if not inconsistent_products:
        print("✅ No inconsistencies to fix!")
        return []
    
    if dry_run:
        print("This is a DRY RUN - no changes will be made to the database.")
        print("Set dry_run=False to actually apply the fixes.")
    
    fixed_products = []
    
    for inconsistency in inconsistent_products:
        product = inconsistency['product']
        old_quantity = inconsistency['stored_quantity']
        new_quantity = inconsistency['calculated_quantity']
        
        print(f"\nFixing: {product.name} ({product.product_id})")
        print(f"  Changing quantity from {old_quantity} to {new_quantity}")
        print(f"  Adjustment: {new_quantity - old_quantity}")
        
        if not dry_run:
            try:
                with transaction.atomic():
                    product.quantity = new_quantity
                    product.save()
                    print(f"  ✅ Successfully updated quantity")
                    fixed_products.append({
                        'product': product,
                        'old_quantity': old_quantity,
                        'new_quantity': new_quantity
                    })
            except Exception as e:
                print(f"  ❌ Error updating quantity: {e}")
        else:
            print(f"  📝 Would update quantity (dry run)")
    
    if not dry_run:
        print(f"\n✅ Successfully fixed {len(fixed_products)} products")
    else:
        print(f"\n📝 Would fix {len(inconsistent_products)} products")
    
    return fixed_products

def verify_fixes(fixed_products):
    """Verify that the fixes were applied correctly"""
    print("\n=== Verifying Fixes ===")
    
    if not fixed_products:
        print("No fixes to verify.")
        return True
    
    all_verified = True
    
    for fix_info in fixed_products:
        product = fix_info['product']
        expected_quantity = fix_info['new_quantity']
        
        # Refresh from database
        product.refresh_from_db()
        
        if product.quantity == expected_quantity:
            print(f"✅ {product.name}: {product.quantity} (correct)")
        else:
            print(f"❌ {product.name}: {product.quantity}, expected {expected_quantity}")
            all_verified = False
    
    if all_verified:
        print("\n🎉 All fixes verified successfully!")
    else:
        print("\n⚠️  Some fixes may not have been applied correctly")
    
    return all_verified

def test_voucher_deletion_after_fix():
    """Test voucher deletion after fixing inconsistencies"""
    print("\n=== Testing Voucher Deletion After Fix ===")
    
    # Find a product with vouchers to test deletion
    products_with_vouchers = Product.objects.filter(
        voucher_items__isnull=False
    ).distinct()[:1]
    
    if not products_with_vouchers.exists():
        print("No products with vouchers found for testing")
        return True
    
    product = products_with_vouchers.first()
    
    # Find a withdrawal voucher for this product
    withdrawal_items = VoucherItem.objects.filter(
        product=product,
        voucher__voucher_type="إذن صرف",
        quantity_disbursed__gt=0
    )[:1]
    
    if not withdrawal_items.exists():
        print("No withdrawal vouchers found for testing")
        return True
    
    item = withdrawal_items.first()
    voucher = item.voucher
    
    print(f"Testing deletion of voucher: {voucher.voucher_number}")
    print(f"Product: {product.name}")
    print(f"Current quantity: {product.quantity}")
    print(f"Withdrawal amount: {item.quantity_disbursed}")
    print(f"Expected quantity after deletion: {product.quantity + item.quantity_disbursed}")
    
    # This is just a simulation - we won't actually delete the voucher
    print("✅ Test simulation completed (no actual deletion performed)")
    return True

def main():
    """Main function to identify and fix inventory balance inconsistencies"""
    print("Starting Inventory Balance Fix Tool...")
    print("=" * 70)
    
    # Step 1: Identify inconsistent products
    inconsistent_products = identify_inconsistent_products()
    
    # Step 2: Display detailed information
    display_inconsistencies(inconsistent_products)
    
    if not inconsistent_products:
        print("\n🎉 No inventory balance inconsistencies found!")
        print("✅ The system is consistent.")
        return
    
    # Step 3: Create backup report
    backup_file = create_backup_report(inconsistent_products)
    
    # Step 4: Show what would be fixed (dry run)
    fix_quantity_inconsistencies(inconsistent_products, dry_run=True)
    
    # Step 5: Ask user for confirmation
    print("\n" + "=" * 70)
    print("IMPORTANT: This will modify product quantities in the database!")
    print("Make sure you have a database backup before proceeding.")
    print("=" * 70)
    
    response = input("\nDo you want to apply these fixes? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        # Step 6: Apply fixes
        fixed_products = fix_quantity_inconsistencies(inconsistent_products, dry_run=False)
        
        # Step 7: Verify fixes
        verification_success = verify_fixes(fixed_products)
        
        # Step 8: Test voucher deletion
        test_voucher_deletion_after_fix()
        
        print("\n" + "=" * 70)
        if verification_success:
            print("✅ Inventory balance fix completed successfully!")
            print("✅ Product quantities have been synchronized with movement history.")
            print("✅ Voucher deletion should now work correctly.")
            print("✅ Both movement history and current balances will show consistent information.")
        else:
            print("⚠️  Fix completed but verification failed!")
            print("❌ Please check the database manually.")
        
        if backup_file:
            print(f"✅ Backup report saved: {backup_file}")
        print("=" * 70)
    else:
        print("\n❌ Fix cancelled by user.")
        print("📝 No changes were made to the database.")
        if backup_file:
            print(f"📝 Analysis report saved: {backup_file}")

if __name__ == "__main__":
    main()
