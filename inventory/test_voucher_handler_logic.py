"""
Test script to verify VoucherHandler.handle_voucher_deletion logic
This script tests the voucher deletion logic for all voucher types to ensure
it properly updates both movement records and current balances.
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
from django.utils import timezone
import datetime

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
        product_id="TEST_PROD_001",
        defaults={
            'name': "Test Product",
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

def test_addition_voucher_deletion():
    """Test deletion of addition voucher (إذن إضافة)"""
    print("\n=== Testing Addition Voucher Deletion ===")
    
    product = create_test_data()
    
    # Create addition voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_ADD_001",
        voucher_type="إذن اضافة",
        date=datetime.date.today()
    )
    
    # Add item to voucher
    test_quantity = Decimal('20.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_added=test_quantity
    )
    
    # Simulate the effect of voucher creation
    product.quantity += test_quantity
    product.save()
    
    print(f"Created addition voucher with quantity {test_quantity}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion
    try:
        # Step 1: Call VoucherHandler
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Check product quantity after handler
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        print(f"Product quantity after handler: {product.quantity}")
        print(f"Expected quantity: {expected_quantity}")
        
        if product.quantity == expected_quantity:
            print("✅ Product quantity correctly updated by handler")
            handler_success = True
        else:
            print("❌ Product quantity NOT correctly updated by handler")
            handler_success = False
        
        # Step 2: Delete the voucher
        voucher_id = voucher.voucher_number
        voucher.delete()
        
        # Check if voucher was deleted
        voucher_exists = Voucher.objects.filter(voucher_number=voucher_id).exists()
        if not voucher_exists:
            print("✅ Voucher successfully deleted")
            deletion_success = True
        else:
            print("❌ Voucher NOT deleted")
            deletion_success = False
        
        # Step 3: Check if VoucherItems were deleted
        items_exist = VoucherItem.objects.filter(voucher__voucher_number=voucher_id).exists()
        if not items_exist:
            print("✅ VoucherItems successfully deleted")
            items_success = True
        else:
            print("❌ VoucherItems NOT deleted")
            items_success = False
        
        return handler_success and deletion_success and items_success
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        # Clean up in case of error
        if Voucher.objects.filter(voucher_number=voucher.voucher_number).exists():
            voucher.delete()
        # Reset product quantity
        product.quantity = Decimal('100.00')
        product.save()
        return False

def test_withdrawal_voucher_deletion():
    """Test deletion of withdrawal voucher (إذن صرف)"""
    print("\n=== Testing Withdrawal Voucher Deletion ===")
    
    product = create_test_data()
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_WITHDRAW_001",
        voucher_type="إذن صرف",
        date=datetime.date.today()
    )
    
    # Add item to voucher
    test_quantity = Decimal('30.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate the effect of voucher creation
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created withdrawal voucher with quantity {test_quantity}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion
    try:
        # Step 1: Call VoucherHandler
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Check product quantity after handler
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        print(f"Product quantity after handler: {product.quantity}")
        print(f"Expected quantity: {expected_quantity}")
        
        if product.quantity == expected_quantity:
            print("✅ Product quantity correctly updated by handler")
            handler_success = True
        else:
            print("❌ Product quantity NOT correctly updated by handler")
            handler_success = False
        
        # Step 2: Delete the voucher
        voucher_id = voucher.voucher_number
        voucher.delete()
        
        # Check if voucher was deleted
        voucher_exists = Voucher.objects.filter(voucher_number=voucher_id).exists()
        if not voucher_exists:
            print("✅ Voucher successfully deleted")
            deletion_success = True
        else:
            print("❌ Voucher NOT deleted")
            deletion_success = False
        
        # Step 3: Check if VoucherItems were deleted
        items_exist = VoucherItem.objects.filter(voucher__voucher_number=voucher_id).exists()
        if not items_exist:
            print("✅ VoucherItems successfully deleted")
            items_success = True
        else:
            print("❌ VoucherItems NOT deleted")
            items_success = False
        
        return handler_success and deletion_success and items_success
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        # Clean up in case of error
        if Voucher.objects.filter(voucher_number=voucher.voucher_number).exists():
            voucher.delete()
        # Reset product quantity
        product.quantity = Decimal('100.00')
        product.save()
        return False

def test_customer_return_voucher_deletion():
    """Test deletion of customer return voucher (اذن مرتجع عميل)"""
    print("\n=== Testing Customer Return Voucher Deletion ===")
    
    product = create_test_data()
    
    # Create customer return voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_CUST_RET_001",
        voucher_type="اذن مرتجع عميل",
        date=datetime.date.today()
    )
    
    # Add item to voucher
    test_quantity = Decimal('15.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_added=test_quantity
    )
    
    # Simulate the effect of voucher creation
    product.quantity += test_quantity
    product.save()
    
    print(f"Created customer return voucher with quantity {test_quantity}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion
    try:
        # Step 1: Call VoucherHandler
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Check product quantity after handler
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        print(f"Product quantity after handler: {product.quantity}")
        print(f"Expected quantity: {expected_quantity}")
        
        if product.quantity == expected_quantity:
            print("✅ Product quantity correctly updated by handler")
            handler_success = True
        else:
            print("❌ Product quantity NOT correctly updated by handler")
            handler_success = False
        
        # Step 2: Delete the voucher
        voucher_id = voucher.voucher_number
        voucher.delete()
        
        # Check if voucher was deleted
        voucher_exists = Voucher.objects.filter(voucher_number=voucher_id).exists()
        if not voucher_exists:
            print("✅ Voucher successfully deleted")
            deletion_success = True
        else:
            print("❌ Voucher NOT deleted")
            deletion_success = False
        
        # Step 3: Check if VoucherItems were deleted
        items_exist = VoucherItem.objects.filter(voucher__voucher_number=voucher_id).exists()
        if not items_exist:
            print("✅ VoucherItems successfully deleted")
            items_success = True
        else:
            print("❌ VoucherItems NOT deleted")
            items_success = False
        
        return handler_success and deletion_success and items_success
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        # Clean up in case of error
        if Voucher.objects.filter(voucher_number=voucher.voucher_number).exists():
            voucher.delete()
        # Reset product quantity
        product.quantity = Decimal('100.00')
        product.save()
        return False

def test_supplier_return_voucher_deletion():
    """Test deletion of supplier return voucher (إذن مرتجع مورد)"""
    print("\n=== Testing Supplier Return Voucher Deletion ===")
    
    product = create_test_data()
    
    # Create supplier return voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_SUPP_RET_001",
        voucher_type="إذن مرتجع مورد",
        date=datetime.date.today()
    )
    
    # Add item to voucher
    test_quantity = Decimal('25.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=test_quantity
    )
    
    # Simulate the effect of voucher creation
    product.quantity -= test_quantity
    product.save()
    
    print(f"Created supplier return voucher with quantity {test_quantity}")
    print(f"Product quantity after voucher creation: {product.quantity}")
    
    # Test deletion
    try:
        # Step 1: Call VoucherHandler
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Check product quantity after handler
        product.refresh_from_db()
        expected_quantity = Decimal('100.00')  # Original quantity
        
        print(f"Product quantity after handler: {product.quantity}")
        print(f"Expected quantity: {expected_quantity}")
        
        if product.quantity == expected_quantity:
            print("✅ Product quantity correctly updated by handler")
            handler_success = True
        else:
            print("❌ Product quantity NOT correctly updated by handler")
            handler_success = False
        
        # Step 2: Delete the voucher
        voucher_id = voucher.voucher_number
        voucher.delete()
        
        # Check if voucher was deleted
        voucher_exists = Voucher.objects.filter(voucher_number=voucher_id).exists()
        if not voucher_exists:
            print("✅ Voucher successfully deleted")
            deletion_success = True
        else:
            print("❌ Voucher NOT deleted")
            deletion_success = False
        
        # Step 3: Check if VoucherItems were deleted
        items_exist = VoucherItem.objects.filter(voucher__voucher_number=voucher_id).exists()
        if not items_exist:
            print("✅ VoucherItems successfully deleted")
            items_success = True
        else:
            print("❌ VoucherItems NOT deleted")
            items_success = False
        
        return handler_success and deletion_success and items_success
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        # Clean up in case of error
        if Voucher.objects.filter(voucher_number=voucher.voucher_number).exists():
            voucher.delete()
        # Reset product quantity
        product.quantity = Decimal('100.00')
        product.save()
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id="TEST_PROD_001").delete()
    
    # Delete test vouchers (if any remain)
    Voucher.objects.filter(voucher_number__startswith="TEST_").delete()
    
    print("Cleanup completed!")

def main():
    """Run all voucher deletion tests"""
    print("Starting Voucher Handler Logic Tests...")
    print("=" * 70)
    
    test_results = []
    
    try:
        # Test all voucher types
        test_results.append(("Addition Voucher", test_addition_voucher_deletion()))
        test_results.append(("Withdrawal Voucher", test_withdrawal_voucher_deletion()))
        test_results.append(("Customer Return Voucher", test_customer_return_voucher_deletion()))
        test_results.append(("Supplier Return Voucher", test_supplier_return_voucher_deletion()))
        
        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY:")
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
            print("✅ VoucherHandler.handle_voucher_deletion() is working correctly for all voucher types")
            print("✅ Both product quantities and movement records are properly updated")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("❌ There are issues with the voucher deletion logic")
            print("❌ Please review the failed tests above")
        print("=" * 70)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
