"""
Fix inventory balance mismatch issue
This script identifies and fixes discrepancies between stored product quantities
and calculated quantities based on movement history.
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

def identify_mismatched_products():
    """Identify products with quantity mismatches"""
    print("=== Identifying Products with Quantity Mismatches ===")
    
    mismatched_products = []
    
    # Get all products that have movements
    products_with_movements = Product.objects.filter(
        voucher_items__isnull=False
    ).distinct()
    
    print(f"Checking {products_with_movements.count()} products with movements...")
    
    for product in products_with_movements:
        # Calculate expected quantity from movements
        movements = VoucherItem.objects.filter(product=product).order_by('voucher__date')
        calculated_quantity = product.initial_quantity
        
        movement_details = []
        
        for movement in movements:
            if movement.quantity_added:
                calculated_quantity += movement.quantity_added
                movement_details.append({
                    'type': 'add',
                    'amount': movement.quantity_added,
                    'voucher': movement.voucher.voucher_number,
                    'voucher_type': movement.voucher.voucher_type,
                    'date': movement.voucher.date
                })
            if movement.quantity_disbursed:
                calculated_quantity -= movement.quantity_disbursed
                movement_details.append({
                    'type': 'subtract',
                    'amount': movement.quantity_disbursed,
                    'voucher': movement.voucher.voucher_number,
                    'voucher_type': movement.voucher.voucher_type,
                    'date': movement.voucher.date
                })
        
        # Check for mismatch
        if product.quantity != calculated_quantity:
            mismatch_info = {
                'product': product,
                'stored_quantity': product.quantity,
                'calculated_quantity': calculated_quantity,
                'difference': product.quantity - calculated_quantity,
                'movement_details': movement_details
            }
            mismatched_products.append(mismatch_info)
    
    return mismatched_products

def display_mismatches(mismatched_products):
    """Display detailed information about mismatches"""
    print(f"\n=== Found {len(mismatched_products)} Products with Mismatches ===")
    
    if not mismatched_products:
        print("✅ No quantity mismatches found!")
        return
    
    for i, mismatch in enumerate(mismatched_products, 1):
        product = mismatch['product']
        print(f"\n{i}. Product: {product.name} ({product.product_id})")
        print(f"   Initial Quantity: {product.initial_quantity}")
        print(f"   Current Stored Quantity: {mismatch['stored_quantity']}")
        print(f"   Calculated Quantity: {mismatch['calculated_quantity']}")
        print(f"   Difference: {mismatch['difference']} (stored - calculated)")
        
        print(f"   Movement History:")
        running_total = product.initial_quantity
        for detail in mismatch['movement_details']:
            if detail['type'] == 'add':
                running_total += detail['amount']
                print(f"     + {detail['amount']} ({detail['voucher_type']}) = {running_total} [{detail['voucher']}] {detail['date']}")
            else:
                running_total -= detail['amount']
                print(f"     - {detail['amount']} ({detail['voucher_type']}) = {running_total} [{detail['voucher']}] {detail['date']}")

def fix_quantity_mismatches(mismatched_products, dry_run=True):
    """Fix quantity mismatches by updating stored quantities to match calculated ones"""
    print(f"\n=== {'DRY RUN: ' if dry_run else ''}Fixing Quantity Mismatches ===")
    
    if not mismatched_products:
        print("✅ No mismatches to fix!")
        return
    
    if dry_run:
        print("This is a DRY RUN - no changes will be made to the database.")
        print("Set dry_run=False to actually apply the fixes.")
    
    fixed_products = []
    
    for mismatch in mismatched_products:
        product = mismatch['product']
        old_quantity = mismatch['stored_quantity']
        new_quantity = mismatch['calculated_quantity']
        
        print(f"\nFixing: {product.name} ({product.product_id})")
        print(f"  Changing quantity from {old_quantity} to {new_quantity}")
        
        if not dry_run:
            try:
                with transaction.atomic():
                    product.quantity = new_quantity
                    product.save()
                    print(f"  ✅ Successfully updated quantity")
                    fixed_products.append(product)
            except Exception as e:
                print(f"  ❌ Error updating quantity: {e}")
        else:
            print(f"  📝 Would update quantity (dry run)")
    
    if not dry_run:
        print(f"\n✅ Successfully fixed {len(fixed_products)} products")
    else:
        print(f"\n📝 Would fix {len(mismatched_products)} products")

def create_backup_report(mismatched_products):
    """Create a backup report of current state before fixing"""
    print("\n=== Creating Backup Report ===")
    
    import json
    from datetime import datetime
    
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'mismatched_products': []
    }
    
    for mismatch in mismatched_products:
        product = mismatch['product']
        backup_data['mismatched_products'].append({
            'product_id': product.product_id,
            'product_name': product.name,
            'initial_quantity': float(product.initial_quantity),
            'stored_quantity': float(mismatch['stored_quantity']),
            'calculated_quantity': float(mismatch['calculated_quantity']),
            'difference': float(mismatch['difference']),
            'movement_details': [
                {
                    'type': detail['type'],
                    'amount': float(detail['amount']),
                    'voucher': detail['voucher'],
                    'voucher_type': detail['voucher_type'],
                    'date': detail['date'].isoformat()
                }
                for detail in mismatch['movement_details']
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

def verify_fix(mismatched_products):
    """Verify that the fixes were applied correctly"""
    print("\n=== Verifying Fixes ===")
    
    all_fixed = True
    
    for mismatch in mismatched_products:
        product = mismatch['product']
        product.refresh_from_db()
        
        expected_quantity = mismatch['calculated_quantity']
        
        if product.quantity == expected_quantity:
            print(f"✅ {product.name}: {product.quantity} (correct)")
        else:
            print(f"❌ {product.name}: {product.quantity}, expected {expected_quantity}")
            all_fixed = False
    
    if all_fixed:
        print("\n🎉 All fixes verified successfully!")
    else:
        print("\n⚠️  Some fixes may not have been applied correctly")
    
    return all_fixed

def main():
    """Main function to identify and fix inventory balance mismatches"""
    print("Starting Inventory Balance Mismatch Fix...")
    print("=" * 70)
    
    # Step 1: Identify mismatched products
    mismatched_products = identify_mismatched_products()
    
    # Step 2: Display detailed information
    display_mismatches(mismatched_products)
    
    if not mismatched_products:
        print("\n🎉 No inventory balance mismatches found!")
        print("✅ The system is consistent.")
        return
    
    # Step 3: Create backup report
    backup_file = create_backup_report(mismatched_products)
    
    # Step 4: Show what would be fixed (dry run)
    fix_quantity_mismatches(mismatched_products, dry_run=True)
    
    # Step 5: Ask user for confirmation
    print("\n" + "=" * 70)
    print("IMPORTANT: This will modify product quantities in the database!")
    print("Make sure you have a database backup before proceeding.")
    print("=" * 70)
    
    response = input("\nDo you want to apply these fixes? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        # Step 6: Apply fixes
        fix_quantity_mismatches(mismatched_products, dry_run=False)
        
        # Step 7: Verify fixes
        verify_fix(mismatched_products)
        
        print("\n" + "=" * 70)
        print("✅ Inventory balance mismatch fix completed!")
        print("✅ Product quantities have been synchronized with movement history.")
        print("✅ Voucher deletion should now work correctly.")
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
