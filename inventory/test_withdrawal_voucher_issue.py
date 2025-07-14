"""
Specific test to reproduce and diagnose withdrawal voucher deletion issue
This script tests withdrawal voucher deletion to identify why inventory is not being restored
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
from django.core.exceptions import ValidationError

def create_test_product():
    """Create a test product for withdrawal voucher testing"""
    print("Creating test product...")
    
    # Create category and unit if they don't exist
    category, _ = Category.objects.get_or_create(
        name="Withdrawal Test Category",
        defaults={'description': 'Test category for withdrawal voucher testing'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product with sufficient initial quantity
    product, created = Product.objects.get_or_create(
        product_id="WITHDRAWAL_TEST_PROD",
        defaults={
            'name': "Withdrawal Test Product",
            'category': category,
            'unit': unit,
            'initial_quantity': Decimal('100.00'),
            'quantity': Decimal('100.00'),
            'unit_price': Decimal('25.00')
        }
    )
    if not created:
        # Reset quantity for testing
        product.quantity = Decimal('100.00')
        product.save()
    
    print(f"Test product created: {product.name} with quantity {product.quantity}")
    return product

def test_withdrawal_voucher_creation_and_deletion():
    """Test the complete workflow of withdrawal voucher creation and deletion"""
    print("\n=== Testing Withdrawal Voucher Creation and Deletion ===")
    
    product = create_test_product()
    initial_quantity = product.quantity
    withdrawal_quantity = Decimal('25.00')
    
    print(f"Initial product quantity: {initial_quantity}")
    print(f"Withdrawal quantity: {withdrawal_quantity}")
    
    # Step 1: Create withdrawal voucher
    print("\n--- Step 1: Creating withdrawal voucher ---")
    voucher = Voucher.objects.create(
        voucher_number="WITHDRAWAL_TEST_001",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    print(f"Created voucher: {voucher.voucher_number} of type '{voucher.voucher_type}'")
    
    # Step 2: Add item to voucher
    print("\n--- Step 2: Adding item to voucher ---")
    voucher_item = VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=withdrawal_quantity
    )
    print(f"Added item: {product.name} with quantity_disbursed={voucher_item.quantity_disbursed}")
    
    # Step 3: Simulate voucher creation effect (reduce inventory)
    print("\n--- Step 3: Simulating voucher creation effect ---")
    product.quantity -= withdrawal_quantity
    product.save()
    quantity_after_withdrawal = product.quantity
    print(f"Product quantity after withdrawal: {quantity_after_withdrawal}")
    
    # Step 4: Test voucher deletion using VoucherHandler
    print("\n--- Step 4: Testing voucher deletion ---")
    print("Calling VoucherHandler.handle_voucher_deletion()...")
    
    try:
        # Get fresh voucher and product data
        voucher.refresh_from_db()
        product.refresh_from_db()
        
        print(f"Before deletion - Product quantity: {product.quantity}")
        print(f"Voucher type: '{voucher.voucher_type}'")
        print(f"Voucher items count: {voucher.items.count()}")
        
        # Print voucher items details
        for item in voucher.items.all():
            print(f"  Item: {item.product.name}")
            print(f"    quantity_added: {item.quantity_added}")
            print(f"    quantity_disbursed: {item.quantity_disbursed}")
        
        # Call the deletion handler
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        print("Deletion handler completed successfully!")
        print(f"Updated products count: {len(updated_products)}")
        
        # Check the results
        product.refresh_from_db()
        final_quantity = product.quantity
        print(f"Product quantity after deletion: {final_quantity}")
        
        # Verify the result
        expected_quantity = initial_quantity  # Should be restored to original
        if final_quantity == expected_quantity:
            print(f"✅ SUCCESS: Inventory correctly restored to {final_quantity}")
            return True
        else:
            print(f"❌ FAILURE: Expected {expected_quantity}, got {final_quantity}")
            print(f"   Difference: {final_quantity - expected_quantity}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            voucher.delete()
            print("Test voucher cleaned up")
        except:
            pass

def test_voucher_type_matching():
    """Test if voucher type string matching is working correctly"""
    print("\n=== Testing Voucher Type String Matching ===")
    
    # Test the exact string matching
    test_voucher_type = "إذن صرف"
    
    print(f"Test voucher type: '{test_voucher_type}'")
    print(f"Length: {len(test_voucher_type)}")
    print(f"Bytes: {test_voucher_type.encode('utf-8')}")
    
    # Test the condition
    if test_voucher_type == 'إذن صرف':
        print("✅ String matching works correctly")
    else:
        print("❌ String matching failed!")
        print("Expected: 'إذن صرف'")
        print(f"Got: '{test_voucher_type}'")
    
    # Test with actual voucher
    product = create_test_product()
    voucher = Voucher.objects.create(
        voucher_number="TYPE_TEST_001",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    print(f"\nActual voucher type from database: '{voucher.voucher_type}'")
    print(f"Length: {len(voucher.voucher_type)}")
    print(f"Bytes: {voucher.voucher_type.encode('utf-8')}")
    
    # Test the condition with database value
    if voucher.voucher_type == 'إذن صرف':
        print("✅ Database voucher type matching works correctly")
    else:
        print("❌ Database voucher type matching failed!")
    
    # Clean up
    voucher.delete()

def test_voucher_handler_logic_step_by_step():
    """Test the VoucherHandler logic step by step to identify the issue"""
    print("\n=== Testing VoucherHandler Logic Step by Step ===")
    
    product = create_test_product()
    initial_quantity = product.quantity
    withdrawal_quantity = Decimal('15.00')
    
    # Create voucher and item
    voucher = Voucher.objects.create(
        voucher_number="STEP_TEST_001",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    voucher_item = VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=withdrawal_quantity
    )
    
    # Simulate withdrawal effect
    product.quantity -= withdrawal_quantity
    product.save()
    
    print(f"Setup complete:")
    print(f"  Initial quantity: {initial_quantity}")
    print(f"  After withdrawal: {product.quantity}")
    print(f"  Withdrawal amount: {withdrawal_quantity}")
    
    # Now manually execute the handler logic step by step
    print("\n--- Manual execution of handler logic ---")
    
    with transaction.atomic():
        updated_products = []
        
        for item in voucher.items.all():
            print(f"\nProcessing item: {item.product.name}")
            product_obj = item.product
            original_quantity = product_obj.quantity
            print(f"  Original quantity: {original_quantity}")
            print(f"  Voucher type: '{voucher.voucher_type}'")
            print(f"  Item quantity_disbursed: {item.quantity_disbursed}")
            
            if voucher.voucher_type == 'إذن اضافة':
                print("  -> Addition voucher logic")
                product_obj.quantity -= item.quantity_added or 0
            elif voucher.voucher_type == 'إذن صرف':
                print("  -> Withdrawal voucher logic (THIS SHOULD EXECUTE)")
                print(f"  -> Adding back: {item.quantity_disbursed or 0}")
                product_obj.quantity += item.quantity_disbursed or 0
            elif voucher.voucher_type == 'اذن مرتجع عميل':
                print("  -> Customer return logic")
                product_obj.quantity -= item.quantity_added or 0
            elif voucher.voucher_type == 'إذن مرتجع مورد':
                print("  -> Supplier return logic")
                product_obj.quantity += item.quantity_disbursed or 0
            else:
                print(f"  -> NO MATCH! Voucher type '{voucher.voucher_type}' not recognized")
            
            print(f"  New quantity: {product_obj.quantity}")
            
            # Check for negative quantity
            if product_obj.quantity < 0:
                print(f"  ❌ Would result in negative quantity!")
                raise ValidationError(f"Negative quantity for {product_obj.name}")
            
            product_obj.save()
            updated_products.append({
                'product_id': product_obj.product_id,
                'name': product_obj.name,
                'old_quantity': original_quantity,
                'new_quantity': product_obj.quantity,
                'difference': product_obj.quantity - original_quantity
            })
    
    print(f"\nFinal result:")
    print(f"  Final quantity: {product.quantity}")
    print(f"  Expected: {initial_quantity}")
    print(f"  Success: {product.quantity == initial_quantity}")
    
    # Clean up
    voucher.delete()
    
    return product.quantity == initial_quantity

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="WITHDRAWAL_TEST_").delete()
    Product.objects.filter(product_id__startswith="STEP_TEST_").delete()
    
    # Delete test vouchers
    Voucher.objects.filter(voucher_number__startswith="WITHDRAWAL_TEST_").delete()
    Voucher.objects.filter(voucher_number__startswith="TYPE_TEST_").delete()
    Voucher.objects.filter(voucher_number__startswith="STEP_TEST_").delete()
    
    print("Cleanup completed!")

def main():
    """Run withdrawal voucher deletion tests"""
    print("Starting Withdrawal Voucher Deletion Investigation...")
    print("=" * 60)
    
    try:
        # Test 1: Voucher type string matching
        test_voucher_type_matching()
        
        # Test 2: Step-by-step handler logic
        step_by_step_success = test_voucher_handler_logic_step_by_step()
        
        # Test 3: Complete workflow test
        workflow_success = test_withdrawal_voucher_creation_and_deletion()
        
        # Summary
        print("\n" + "=" * 60)
        print("INVESTIGATION SUMMARY:")
        print("=" * 60)
        print(f"Step-by-step logic test: {'✅ PASSED' if step_by_step_success else '❌ FAILED'}")
        print(f"Complete workflow test: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
        
        if step_by_step_success and workflow_success:
            print("\n🎉 WITHDRAWAL VOUCHER DELETION IS WORKING CORRECTLY!")
            print("The issue might be elsewhere in the system.")
        else:
            print("\n⚠️ ISSUE CONFIRMED: Withdrawal voucher deletion is not working properly.")
            print("Further investigation needed.")
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
