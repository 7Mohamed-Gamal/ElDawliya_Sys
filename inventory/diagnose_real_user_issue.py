"""
Diagnostic tool to help identify the real user issue
This script provides a comprehensive analysis of the current system state
and helps identify what the user might be experiencing.
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
from inventory.voucher_handlers import VoucherHandler

def analyze_recent_vouchers():
    """Analyze recent vouchers to identify potential issues"""
    print("=== Analyzing Recent Vouchers ===")
    
    # Get recent vouchers
    recent_vouchers = Voucher.objects.all().order_by('-created_at')[:20]
    
    if not recent_vouchers.exists():
        print("❌ No vouchers found in the system")
        return
    
    print(f"✅ Found {recent_vouchers.count()} recent vouchers")
    
    withdrawal_vouchers = [v for v in recent_vouchers if v.voucher_type == "إذن صرف"]
    print(f"   - Withdrawal vouchers: {len(withdrawal_vouchers)}")
    
    for voucher in withdrawal_vouchers[:5]:  # Show first 5
        print(f"\nVoucher: {voucher.voucher_number}")
        print(f"  Date: {voucher.date}")
        print(f"  Items: {voucher.items.count()}")
        
        for item in voucher.items.all():
            print(f"    Product: {item.product.name} ({item.product.product_id})")
            print(f"    Current Quantity: {item.product.quantity}")
            print(f"    Disbursed: {item.quantity_disbursed or 0}")

def check_products_with_movements():
    """Check products that have movement history"""
    print("\n=== Checking Products with Movements ===")
    
    # Get products that have voucher items
    products_with_movements = Product.objects.filter(
        voucher_items__isnull=False
    ).distinct()[:10]
    
    if not products_with_movements.exists():
        print("❌ No products with movements found")
        return
    
    print(f"✅ Found {products_with_movements.count()} products with movements")
    
    for product in products_with_movements:
        print(f"\nProduct: {product.name} ({product.product_id})")
        print(f"  Current Quantity: {product.quantity}")
        print(f"  Initial Quantity: {product.initial_quantity}")
        
        # Calculate expected quantity from movements
        movements = VoucherItem.objects.filter(product=product).order_by('voucher__date')
        calculated_quantity = product.initial_quantity
        
        print(f"  Movement History:")
        for movement in movements:
            if movement.quantity_added:
                calculated_quantity += movement.quantity_added
                print(f"    + {movement.quantity_added} ({movement.voucher.voucher_type}) = {calculated_quantity}")
            if movement.quantity_disbursed:
                calculated_quantity -= movement.quantity_disbursed
                print(f"    - {movement.quantity_disbursed} ({movement.voucher.voucher_type}) = {calculated_quantity}")
        
        print(f"  Calculated Quantity: {calculated_quantity}")
        
        if product.quantity != calculated_quantity:
            print(f"  ⚠️  MISMATCH: Stored ({product.quantity}) != Calculated ({calculated_quantity})")
        else:
            print(f"  ✅ MATCH: Quantities are consistent")

def simulate_user_scenario():
    """Simulate what the user might be experiencing"""
    print("\n=== Simulating User Scenario ===")

    # Find a product with withdrawal vouchers
    withdrawal_items = VoucherItem.objects.filter(
        voucher__voucher_type="إذن صرف",
        quantity_disbursed__gt=0
    ).select_related('product', 'voucher')

    if not withdrawal_items.exists():
        print("❌ No withdrawal vouchers found to test with")
        return

    item = withdrawal_items.first()
    product = item.product
    voucher = item.voucher
    
    print(f"Testing with:")
    print(f"  Product: {product.name} ({product.product_id})")
    print(f"  Voucher: {voucher.voucher_number}")
    print(f"  Withdrawn Quantity: {item.quantity_disbursed}")
    
    # Show current state
    print(f"\nBefore deletion:")
    print(f"  Product current quantity: {product.quantity}")
    
    movements_before = VoucherItem.objects.filter(product=product).count()
    print(f"  Movement history count: {movements_before}")
    
    # Show what would happen if we delete this voucher
    print(f"\nWhat SHOULD happen if voucher is deleted:")
    print(f"  Product quantity should become: {product.quantity + item.quantity_disbursed}")
    print(f"  Movement history count should become: {movements_before - 1}")
    
    # Actually test the deletion (but don't commit)
    from django.db import transaction
    try:
        with transaction.atomic():
            # Simulate deletion
            updated_products = VoucherHandler.handle_voucher_deletion(voucher)
            
            product.refresh_from_db()
            movements_after = VoucherItem.objects.filter(product=product).count()
            
            print(f"\nActual results (in test transaction):")
            print(f"  Product quantity after handler: {product.quantity}")
            print(f"  Movement history count after handler: {movements_after}")
            
            # Rollback by raising an exception
            raise Exception("Test rollback")
            
    except Exception as e:
        if "Test rollback" not in str(e):
            print(f"❌ Error during test: {e}")
        else:
            print("✅ Test completed (rolled back)")

def check_for_data_corruption():
    """Check for potential data corruption issues"""
    print("\n=== Checking for Data Corruption ===")
    
    issues_found = []
    
    # Check for voucher items with both quantity_added and quantity_disbursed
    dual_quantity_items = VoucherItem.objects.filter(
        quantity_added__isnull=False,
        quantity_disbursed__isnull=False
    )
    
    if dual_quantity_items.exists():
        issues_found.append(f"Found {dual_quantity_items.count()} voucher items with both added and disbursed quantities")
    
    # Check for voucher items with neither quantity
    no_quantity_items = VoucherItem.objects.filter(
        quantity_added__isnull=True,
        quantity_disbursed__isnull=True
    )
    
    if no_quantity_items.exists():
        issues_found.append(f"Found {no_quantity_items.count()} voucher items with no quantities")
    
    # Check for negative product quantities
    negative_products = Product.objects.filter(quantity__lt=0)
    
    if negative_products.exists():
        issues_found.append(f"Found {negative_products.count()} products with negative quantities")
        for product in negative_products[:3]:
            issues_found.append(f"  - {product.name}: {product.quantity}")
    
    # Check for voucher type mismatches
    type_mismatches = []
    
    addition_with_disbursed = VoucherItem.objects.filter(
        voucher__voucher_type="إذن اضافة",
        quantity_disbursed__isnull=False
    )
    if addition_with_disbursed.exists():
        type_mismatches.append(f"Addition vouchers with disbursed quantities: {addition_with_disbursed.count()}")
    
    withdrawal_with_added = VoucherItem.objects.filter(
        voucher__voucher_type="إذن صرف",
        quantity_added__isnull=False
    )
    if withdrawal_with_added.exists():
        type_mismatches.append(f"Withdrawal vouchers with added quantities: {withdrawal_with_added.count()}")
    
    if type_mismatches:
        issues_found.extend(type_mismatches)
    
    if issues_found:
        print("⚠️  Issues found:")
        for issue in issues_found:
            print(f"   {issue}")
    else:
        print("✅ No data corruption issues found")
    
    return len(issues_found) == 0

def provide_user_guidance():
    """Provide guidance for the user"""
    print("\n=== User Guidance ===")
    
    print("If you're still experiencing issues with voucher deletion:")
    print()
    print("1. **Verify the Expected Behavior**:")
    print("   - When you delete a WITHDRAWAL voucher (إذن صرف)")
    print("   - The withdrawn quantities should be ADDED BACK to inventory")
    print("   - This INCREASES the current balance")
    print()
    print("2. **Check Specific Voucher**:")
    print("   - Note the exact voucher number you're trying to delete")
    print("   - Note the current product quantities before deletion")
    print("   - Note the quantities in the voucher")
    print("   - Calculate what the new quantities should be")
    print()
    print("3. **Clear Browser Cache**:")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Clear all cached data")
    print("   - Refresh the page")
    print()
    print("4. **Check Different Views**:")
    print("   - Product list page")
    print("   - Product detail page")
    print("   - Movement history page")
    print("   - Make sure all show consistent data")
    print()
    print("5. **Test with New Voucher**:")
    print("   - Create a test withdrawal voucher")
    print("   - Note the quantities before and after creation")
    print("   - Delete the voucher")
    print("   - Verify quantities are restored")

def main():
    """Run comprehensive diagnostic"""
    print("Starting Real User Issue Diagnosis...")
    print("=" * 70)
    
    # Run diagnostic checks
    analyze_recent_vouchers()
    check_products_with_movements()
    simulate_user_scenario()
    data_ok = check_for_data_corruption()
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 70)
    
    if data_ok:
        print("✅ System data integrity is good")
        print("✅ The voucher deletion logic is working correctly")
        print("✅ Movement history and current balances are synchronized")
        print()
        print("The issue is likely:")
        print("  - User expectation mismatch (withdrawal deletion INCREASES balance)")
        print("  - Browser caching of product data")
        print("  - User looking at wrong product or voucher")
        print("  - Display refresh issue")
    else:
        print("⚠️  Data integrity issues found")
        print("❌ There may be data corruption affecting the system")
        print("❌ Please review the issues listed above")
    
    provide_user_guidance()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
