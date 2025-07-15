"""
Test script to investigate the specific balance update issue
This script tests the exact sequence of operations during voucher deletion
to identify why movement history updates but current balances don't.
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
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def create_test_data():
    """Create test data for balance update testing"""
    print("Creating test data...")
    
    # Create category and unit if they don't exist
    category, _ = Category.objects.get_or_create(
        name="Balance Test Category",
        defaults={'description': 'Test category for balance update testing'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product
    product, created = Product.objects.get_or_create(
        product_id="BALANCE_TEST_PROD_001",
        defaults={
            'name': "Balance Test Product",
            'category': category,
            'unit': unit,
            'initial_quantity': Decimal('100.00'),
            'quantity': Decimal('100.00'),
            'unit_price': Decimal('10.00')
        }
    )
    if not created:
        # Reset quantity for testing
        product.quantity = Decimal('100.00')
        product.save()
    
    print(f"✅ Created test product: {product.name} with quantity {product.quantity}")
    return product

def test_voucher_handler_only(product):
    """Test only the VoucherHandler.handle_voucher_deletion method"""
    print("\n=== Testing VoucherHandler Only ===")
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="BALANCE_TEST_WITHDRAW_001",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Add item to voucher
    test_quantity = Decimal('25.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate voucher creation effect (reduce inventory)
    original_quantity = product.quantity
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created voucher: {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    print(f"VoucherItems count before deletion: {VoucherItem.objects.filter(voucher=voucher).count()}")
    
    # Test VoucherHandler deletion only (without deleting the voucher)
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("✅ VoucherHandler.handle_voucher_deletion() completed")
        
        # Check product quantity immediately after handler
        product.refresh_from_db()
        print(f"Product quantity after handler: {product.quantity}")
        
        # Check if VoucherItems still exist
        voucher_items_count = VoucherItem.objects.filter(voucher=voucher).count()
        print(f"VoucherItems count after handler: {voucher_items_count}")
        
        # Check if voucher still exists
        voucher_exists = Voucher.objects.filter(voucher_number=voucher.voucher_number).exists()
        print(f"Voucher still exists: {voucher_exists}")
        
        if product.quantity == original_quantity:
            print("✅ SUCCESS: Product quantity correctly restored by handler")
            result = True
        else:
            print(f"❌ FAILURE: Product quantity is {product.quantity}, expected {original_quantity}")
            result = False
        
        # Clean up manually
        voucher.delete()
        return result
        
    except Exception as e:
        print(f"❌ ERROR during handler test: {e}")
        voucher.delete()
        return False

def test_complete_deletion_sequence(product):
    """Test the complete deletion sequence as done by the view"""
    print("\n=== Testing Complete Deletion Sequence ===")
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="BALANCE_TEST_WITHDRAW_002",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Add item to voucher
    test_quantity = Decimal('30.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate voucher creation effect (reduce inventory)
    original_quantity = product.quantity
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created voucher: {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Simulate the exact sequence from VoucherDeleteView
    try:
        print("Step 1: Calling VoucherHandler.handle_voucher_deletion()")
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Check product quantity after handler but before voucher deletion
        product.refresh_from_db()
        print(f"Product quantity after handler (before voucher deletion): {product.quantity}")
        
        print("Step 2: Deleting voucher (which will delete VoucherItems)")
        voucher.delete()
        
        # Check product quantity after complete deletion
        product.refresh_from_db()
        print(f"Product quantity after complete deletion: {product.quantity}")
        
        # Check if VoucherItems were deleted
        voucher_items_count = VoucherItem.objects.filter(product=product).count()
        print(f"Remaining VoucherItems for product: {voucher_items_count}")
        
        if product.quantity == original_quantity:
            print("✅ SUCCESS: Product quantity correctly restored after complete deletion")
            return True
        else:
            print(f"❌ FAILURE: Product quantity is {product.quantity}, expected {original_quantity}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR during complete deletion test: {e}")
        return False

def test_transaction_isolation():
    """Test if there are transaction isolation issues"""
    print("\n=== Testing Transaction Isolation ===")
    
    product = create_test_data()
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="BALANCE_TEST_WITHDRAW_003",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Add item to voucher
    test_quantity = Decimal('20.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate voucher creation effect (reduce inventory)
    original_quantity = product.quantity
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created voucher: {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test with explicit transaction
    try:
        with transaction.atomic():
            print("Inside transaction: Calling VoucherHandler.handle_voucher_deletion()")
            updated_products = VoucherHandler.handle_voucher_deletion(voucher)
            
            # Check product quantity inside transaction
            product.refresh_from_db()
            print(f"Product quantity inside transaction after handler: {product.quantity}")
            
            print("Inside transaction: Deleting voucher")
            voucher.delete()
            
            # Check product quantity inside transaction after deletion
            product.refresh_from_db()
            print(f"Product quantity inside transaction after voucher deletion: {product.quantity}")
        
        # Check product quantity after transaction commits
        product.refresh_from_db()
        print(f"Product quantity after transaction commit: {product.quantity}")
        
        if product.quantity == original_quantity:
            print("✅ SUCCESS: Transaction isolation working correctly")
            return True
        else:
            print(f"❌ FAILURE: Product quantity is {product.quantity}, expected {original_quantity}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR during transaction test: {e}")
        return False

def test_database_commit_issue():
    """Test if there's a database commit issue"""
    print("\n=== Testing Database Commit Issue ===")
    
    product = create_test_data()
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="BALANCE_TEST_WITHDRAW_004",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Add item to voucher
    test_quantity = Decimal('15.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate voucher creation effect (reduce inventory)
    original_quantity = product.quantity
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created voucher: {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    try:
        # Call handler
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Force database commit
        from django.db import connection
        connection.commit()
        
        # Check product quantity after forced commit
        product.refresh_from_db()
        print(f"Product quantity after handler and forced commit: {product.quantity}")
        
        # Delete voucher
        voucher.delete()
        
        # Force another commit
        connection.commit()
        
        # Final check
        product.refresh_from_db()
        print(f"Product quantity after voucher deletion and forced commit: {product.quantity}")
        
        if product.quantity == original_quantity:
            print("✅ SUCCESS: Database commits working correctly")
            return True
        else:
            print(f"❌ FAILURE: Product quantity is {product.quantity}, expected {original_quantity}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR during commit test: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="BALANCE_TEST_PROD_").delete()
    
    # Delete test vouchers (if any remain)
    Voucher.objects.filter(voucher_number__startswith="BALANCE_TEST_").delete()
    
    print("✅ Cleanup completed!")

def main():
    """Run balance update issue tests"""
    print("Starting Balance Update Issue Investigation...")
    print("=" * 70)
    
    test_results = []
    
    try:
        # Create test data
        product = create_test_data()
        
        # Test 1: VoucherHandler only
        handler_result = test_voucher_handler_only(product)
        test_results.append(("VoucherHandler Only", handler_result))
        
        # Reset product quantity
        product.quantity = Decimal('100.00')
        product.save()
        
        # Test 2: Complete deletion sequence
        complete_result = test_complete_deletion_sequence(product)
        test_results.append(("Complete Deletion Sequence", complete_result))
        
        # Test 3: Transaction isolation
        transaction_result = test_transaction_isolation()
        test_results.append(("Transaction Isolation", transaction_result))
        
        # Test 4: Database commit issue
        commit_result = test_database_commit_issue()
        test_results.append(("Database Commit", commit_result))
        
        # Print summary
        print("\n" + "=" * 70)
        print("BALANCE UPDATE INVESTIGATION SUMMARY:")
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
            print("✅ The balance update system is working correctly.")
            print("✅ The issue might be browser-related or user-specific.")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("❌ There are issues with the balance update system.")
            print("❌ The problem is in the system logic, not user-related.")
        print("=" * 70)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
