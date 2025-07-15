"""
Test script to investigate UI balance disconnect issue
This script tests the exact user interface workflow to identify
why movement history shows correctly but current balances don't update.
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

from inventory.models_local import Product, Voucher, VoucherItem, Category, Unit
from inventory.voucher_handlers import VoucherHandler
from django.db import transaction

def create_test_scenario():
    """Create a realistic test scenario"""
    print("Creating realistic test scenario...")
    
    # Create category and unit if they don't exist
    category, _ = Category.objects.get_or_create(
        name="UI Test Category",
        defaults={'description': 'Test category for UI testing'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product
    product, created = Product.objects.get_or_create(
        product_id="UI_TEST_PROD_001",
        defaults={
            'name': "UI Test Product",
            'category': category,
            'unit': unit,
            'initial_quantity': Decimal('200.00'),
            'quantity': Decimal('200.00'),
            'unit_price': Decimal('15.00')
        }
    )
    if not created:
        # Reset quantity for testing
        product.quantity = Decimal('200.00')
        product.save()
    
    print(f"✅ Created test product: {product.name}")
    print(f"   Product ID: {product.product_id}")
    print(f"   Initial quantity: {product.quantity}")
    
    return product

def create_multiple_vouchers(product):
    """Create multiple vouchers to simulate real usage"""
    print("\n=== Creating Multiple Vouchers ===")
    
    vouchers = []
    
    # Create addition voucher
    voucher1 = Voucher.objects.create(
        voucher_number="UI_ADD_001",
        voucher_type="إذن اضافة",
        date="2024-01-10"
    )
    VoucherItem.objects.create(
        voucher=voucher1,
        product=product,
        quantity_added=Decimal('50.00')
    )
    product.quantity += Decimal('50.00')
    product.save()
    vouchers.append(voucher1)
    print(f"Created addition voucher: {voucher1.voucher_number}, quantity now: {product.quantity}")
    
    # Create withdrawal voucher
    voucher2 = Voucher.objects.create(
        voucher_number="UI_WITHDRAW_001",
        voucher_type="إذن صرف",
        date="2024-01-12"
    )
    VoucherItem.objects.create(
        voucher=voucher2,
        product=product,
        quantity_disbursed=Decimal('30.00')
    )
    product.quantity -= Decimal('30.00')
    product.save()
    vouchers.append(voucher2)
    print(f"Created withdrawal voucher: {voucher2.voucher_number}, quantity now: {product.quantity}")
    
    # Create customer return voucher
    voucher3 = Voucher.objects.create(
        voucher_number="UI_CUST_RET_001",
        voucher_type="اذن مرتجع عميل",
        date="2024-01-14"
    )
    VoucherItem.objects.create(
        voucher=voucher3,
        product=product,
        quantity_added=Decimal('10.00')
    )
    product.quantity += Decimal('10.00')
    product.save()
    vouchers.append(voucher3)
    print(f"Created customer return voucher: {voucher3.voucher_number}, quantity now: {product.quantity}")
    
    return vouchers

def check_movement_history(product):
    """Check the movement history as shown in the UI"""
    print(f"\n=== Checking Movement History for {product.name} ===")
    
    # Get all voucher items for this product (this is what the UI shows)
    movements = VoucherItem.objects.filter(
        product=product
    ).select_related('voucher', 'product').order_by('-voucher__date')
    
    print(f"Total movements found: {movements.count()}")
    
    for i, movement in enumerate(movements, 1):
        print(f"{i}. Date: {movement.voucher.date}")
        print(f"   Voucher: {movement.voucher.voucher_number}")
        print(f"   Type: {movement.voucher.voucher_type}")
        if movement.quantity_added:
            print(f"   Added: {movement.quantity_added}")
        if movement.quantity_disbursed:
            print(f"   Disbursed: {movement.quantity_disbursed}")
        print()
    
    return movements

def test_voucher_deletion_with_ui_check(product, vouchers):
    """Test voucher deletion and check both movement history and current balance"""
    print(f"\n=== Testing Voucher Deletion with UI Check ===")
    
    # Get the withdrawal voucher to delete
    withdrawal_voucher = next(v for v in vouchers if v.voucher_type == "إذن صرف")
    
    print(f"About to delete withdrawal voucher: {withdrawal_voucher.voucher_number}")
    print(f"Current product quantity: {product.quantity}")
    
    # Check movement history before deletion
    movements_before = check_movement_history(product)
    print(f"Movement history count before deletion: {movements_before.count()}")
    
    # Perform deletion using the same method as the view
    try:
        # Step 1: Call VoucherHandler (this updates product quantities)
        updated_products = VoucherHandler.handle_voucher_deletion(withdrawal_voucher)
        print("✅ VoucherHandler.handle_voucher_deletion() completed")
        
        # Check product quantity after handler
        product.refresh_from_db()
        print(f"Product quantity after handler: {product.quantity}")
        
        # Step 2: Delete the voucher (this removes VoucherItems)
        withdrawal_voucher.delete()
        print("✅ Voucher deleted")
        
        # Check product quantity after voucher deletion
        product.refresh_from_db()
        print(f"Product quantity after voucher deletion: {product.quantity}")
        
        # Check movement history after deletion
        movements_after = check_movement_history(product)
        print(f"Movement history count after deletion: {movements_after.count()}")
        
        # Verify the results
        expected_quantity = Decimal('230.00')  # 200 + 50 + 10 (withdrawal should be reversed)
        
        if product.quantity == expected_quantity:
            print(f"✅ SUCCESS: Current balance correctly updated to {product.quantity}")
        else:
            print(f"❌ FAILURE: Current balance is {product.quantity}, expected {expected_quantity}")
        
        if movements_after.count() == movements_before.count() - 1:
            print("✅ SUCCESS: Movement history correctly updated (one less movement)")
        else:
            print(f"❌ FAILURE: Movement history count is {movements_after.count()}, expected {movements_before.count() - 1}")
        
        return product.quantity == expected_quantity and movements_after.count() == movements_before.count() - 1
        
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False

def test_calculated_vs_stored_balance(product):
    """Test if there's a difference between calculated and stored balance"""
    print(f"\n=== Testing Calculated vs Stored Balance ===")
    
    # Get current stored balance
    stored_balance = product.quantity
    print(f"Stored balance: {stored_balance}")
    
    # Calculate balance from movement history
    movements = VoucherItem.objects.filter(product=product)
    calculated_balance = product.initial_quantity
    
    print(f"Starting from initial quantity: {calculated_balance}")
    
    for movement in movements.order_by('voucher__date'):
        if movement.quantity_added:
            calculated_balance += movement.quantity_added
            print(f"  + {movement.quantity_added} ({movement.voucher.voucher_type}) = {calculated_balance}")
        if movement.quantity_disbursed:
            calculated_balance -= movement.quantity_disbursed
            print(f"  - {movement.quantity_disbursed} ({movement.voucher.voucher_type}) = {calculated_balance}")
    
    print(f"Calculated balance: {calculated_balance}")
    
    if stored_balance == calculated_balance:
        print("✅ SUCCESS: Stored and calculated balances match")
        return True
    else:
        print(f"❌ FAILURE: Stored balance ({stored_balance}) != Calculated balance ({calculated_balance})")
        return False

def test_multiple_deletion_scenario(product):
    """Test multiple voucher deletions to see if there's a cumulative issue"""
    print(f"\n=== Testing Multiple Deletion Scenario ===")
    
    # Create several vouchers
    vouchers_to_delete = []
    
    # Create and immediately track multiple withdrawal vouchers
    for i in range(3):
        voucher = Voucher.objects.create(
            voucher_number=f"UI_MULTI_WITHDRAW_{i+1:03d}",
            voucher_type="إذن صرف",
            date="2024-01-15"
        )
        VoucherItem.objects.create(
            voucher=voucher,
            product=product,
            quantity_disbursed=Decimal('5.00')
        )
        product.quantity -= Decimal('5.00')
        product.save()
        vouchers_to_delete.append(voucher)
        print(f"Created voucher {voucher.voucher_number}, quantity now: {product.quantity}")
    
    initial_quantity = product.quantity
    print(f"Initial quantity before deletions: {initial_quantity}")
    
    # Delete vouchers one by one and check balance each time
    for i, voucher in enumerate(vouchers_to_delete):
        print(f"\nDeleting voucher {i+1}: {voucher.voucher_number}")
        
        # Use VoucherHandler and delete
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        voucher.delete()
        
        product.refresh_from_db()
        expected_quantity = initial_quantity + Decimal('5.00') * (i + 1)
        
        print(f"  Quantity after deletion {i+1}: {product.quantity}")
        print(f"  Expected quantity: {expected_quantity}")
        
        if product.quantity != expected_quantity:
            print(f"  ❌ FAILURE at deletion {i+1}")
            return False
    
    print("✅ SUCCESS: Multiple deletions working correctly")
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="UI_TEST_PROD_").delete()
    
    # Delete test vouchers (if any remain)
    Voucher.objects.filter(voucher_number__startswith="UI_").delete()
    
    print("✅ Cleanup completed!")

def main():
    """Run UI balance disconnect investigation"""
    print("Starting UI Balance Disconnect Investigation...")
    print("=" * 70)
    
    test_results = []
    
    try:
        # Create test scenario
        product = create_test_scenario()
        vouchers = create_multiple_vouchers(product)
        
        # Test 1: Check calculated vs stored balance
        balance_match = test_calculated_vs_stored_balance(product)
        test_results.append(("Calculated vs Stored Balance", balance_match))
        
        # Test 2: Test voucher deletion with UI check
        deletion_result = test_voucher_deletion_with_ui_check(product, vouchers)
        test_results.append(("Voucher Deletion with UI Check", deletion_result))
        
        # Test 3: Test multiple deletion scenario
        multiple_deletion_result = test_multiple_deletion_scenario(product)
        test_results.append(("Multiple Deletion Scenario", multiple_deletion_result))
        
        # Print summary
        print("\n" + "=" * 70)
        print("UI BALANCE DISCONNECT INVESTIGATION SUMMARY:")
        print("=" * 70)
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 70)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ The UI balance system is working correctly.")
            print("✅ Movement history and current balances are synchronized.")
            print("✅ The issue might be:")
            print("   - Browser caching of product list/detail pages")
            print("   - User looking at cached data")
            print("   - Specific voucher data corruption")
            print("   - User permissions affecting display")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("❌ There are issues with the UI balance system.")
            print("❌ Movement history and current balances are NOT synchronized.")
        print("=" * 70)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
