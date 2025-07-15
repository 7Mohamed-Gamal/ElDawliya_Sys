"""
Test script to verify voucher deletion directly using the VoucherHandler
This script tests the actual deletion logic without using the web interface.
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

def create_test_data():
    """Create test data for voucher deletion testing"""
    print("Creating test data...")
    
    # Create category and unit if they don't exist
    category, _ = Category.objects.get_or_create(
        name="Test Category",
        defaults={'description': 'Test category for voucher deletion testing'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product
    product, created = Product.objects.get_or_create(
        product_id="TEST_DIRECT_PROD_001",
        defaults={
            'name': "Test Direct Product",
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
    
    print(f"Created/Updated test product: {product.name} with quantity {product.quantity}")
    return product

def test_withdrawal_voucher_deletion():
    """Test deletion of withdrawal voucher (إذن صرف)"""
    print("\n=== Testing Withdrawal Voucher Deletion ===")
    
    # Create test data
    product = create_test_data()
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_DIRECT_WITHDRAW_001",
        voucher_type="إذن صرف",
        date="2024-01-01"
    )
    
    # Add item to voucher
    test_quantity = Decimal('25.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate the effect of voucher creation (reduce inventory)
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created withdrawal voucher {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion using VoucherHandler
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("VoucherHandler.handle_voucher_deletion() completed successfully!")
        
        # Check product quantities
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        if product.quantity != expected_quantity:
            print(f"❌ ERROR: Product quantity is {product.quantity}, expected {expected_quantity}")
            print("❌ Inventory balance was NOT restored correctly!")
            return False
        else:
            print(f"✅ Product quantity correctly restored to {product.quantity}")
            print("✅ Inventory balance restoration working correctly!")
        
        # Now delete the voucher itself
        voucher.delete()
        print(f"Voucher {voucher.voucher_number} deleted from database!")
        
        return True
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False

def test_addition_voucher_deletion():
    """Test deletion of addition voucher (إذن اضافة)"""
    print("\n=== Testing Addition Voucher Deletion ===")
    
    # Create test data
    product = create_test_data()
    
    # Create addition voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_DIRECT_ADD_001",
        voucher_type="إذن اضافة",
        date="2024-01-01"
    )
    
    # Add item to voucher
    test_quantity = Decimal('30.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_added=test_quantity
    )
    
    # Simulate the effect of voucher creation (increase inventory)
    product.quantity += test_quantity
    product.save()
    
    print(f"Created addition voucher {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion using VoucherHandler
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("VoucherHandler.handle_voucher_deletion() completed successfully!")
        
        # Check product quantities
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        if product.quantity != expected_quantity:
            print(f"❌ ERROR: Product quantity is {product.quantity}, expected {expected_quantity}")
            print("❌ Inventory balance was NOT restored correctly!")
            return False
        else:
            print(f"✅ Product quantity correctly restored to {product.quantity}")
            print("✅ Inventory balance restoration working correctly!")
        
        # Now delete the voucher itself
        voucher.delete()
        print(f"Voucher {voucher.voucher_number} deleted from database!")
        
        return True
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False

def test_customer_return_voucher_deletion():
    """Test deletion of customer return voucher (اذن مرتجع عميل)"""
    print("\n=== Testing Customer Return Voucher Deletion ===")
    
    # Create test data
    product = create_test_data()
    
    # Create customer return voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_DIRECT_CUST_RET_001",
        voucher_type="اذن مرتجع عميل",
        date="2024-01-01"
    )
    
    # Add item to voucher
    test_quantity = Decimal('15.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_added=test_quantity
    )
    
    # Simulate the effect of voucher creation (increase inventory)
    product.quantity += test_quantity
    product.save()
    
    print(f"Created customer return voucher {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion using VoucherHandler
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("VoucherHandler.handle_voucher_deletion() completed successfully!")
        
        # Check product quantities
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        if product.quantity != expected_quantity:
            print(f"❌ ERROR: Product quantity is {product.quantity}, expected {expected_quantity}")
            print("❌ Inventory balance was NOT restored correctly!")
            return False
        else:
            print(f"✅ Product quantity correctly restored to {product.quantity}")
            print("✅ Inventory balance restoration working correctly!")
        
        # Now delete the voucher itself
        voucher.delete()
        print(f"Voucher {voucher.voucher_number} deleted from database!")
        
        return True
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False

def test_supplier_return_voucher_deletion():
    """Test deletion of supplier return voucher (إذن مرتجع مورد)"""
    print("\n=== Testing Supplier Return Voucher Deletion ===")
    
    # Create test data
    product = create_test_data()
    
    # Create supplier return voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_DIRECT_SUPP_RET_001",
        voucher_type="إذن مرتجع مورد",
        date="2024-01-01"
    )
    
    # Add item to voucher
    test_quantity = Decimal('20.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate the effect of voucher creation (decrease inventory)
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created supplier return voucher {voucher.voucher_number}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion using VoucherHandler
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("VoucherHandler.handle_voucher_deletion() completed successfully!")
        
        # Check product quantities
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        if product.quantity != expected_quantity:
            print(f"❌ ERROR: Product quantity is {product.quantity}, expected {expected_quantity}")
            print("❌ Inventory balance was NOT restored correctly!")
            return False
        else:
            print(f"✅ Product quantity correctly restored to {product.quantity}")
            print("✅ Inventory balance restoration working correctly!")
        
        # Now delete the voucher itself
        voucher.delete()
        print(f"Voucher {voucher.voucher_number} deleted from database!")
        
        return True
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="TEST_DIRECT_PROD_").delete()
    
    # Delete test vouchers (if any remain)
    Voucher.objects.filter(voucher_number__startswith="TEST_DIRECT_").delete()
    
    print("Cleanup completed!")

def main():
    """Run direct voucher deletion tests"""
    print("Starting Direct Voucher Deletion Tests...")
    print("=" * 60)
    
    test_results = []
    
    try:
        # Test all voucher types
        test_results.append(("Withdrawal Voucher", test_withdrawal_voucher_deletion()))
        test_results.append(("Addition Voucher", test_addition_voucher_deletion()))
        test_results.append(("Customer Return Voucher", test_customer_return_voucher_deletion()))
        test_results.append(("Supplier Return Voucher", test_supplier_return_voucher_deletion()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("DIRECT TEST SUMMARY:")
        print("=" * 60)
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL DIRECT TESTS PASSED! Voucher deletion logic is working correctly.")
            print("✅ Inventory balance management is functioning properly!")
        else:
            print("⚠️  SOME DIRECT TESTS FAILED! There may be an issue with the voucher deletion logic.")
            print("❌ Please check the VoucherHandler.handle_voucher_deletion implementation!")
        print("=" * 60)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
