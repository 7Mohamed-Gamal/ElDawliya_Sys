"""
Test script to verify voucher deletion logic
This script tests the VoucherHandler.handle_voucher_deletion method
to ensure proper inventory balance adjustments for all voucher types.
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
    
    # Create test products
    products = []
    for i in range(1, 4):
        product, created = Product.objects.get_or_create(
            product_id=f"TEST_PROD_{i}",
            defaults={
                'name': f"Test Product {i}",
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
        products.append(product)
    
    print(f"Created/Updated {len(products)} test products")
    return products

def test_addition_voucher_deletion():
    """Test deletion of addition voucher (إذن اضافة)"""
    print("\n=== Testing Addition Voucher Deletion ===")
    
    products = create_test_data()
    
    # Create addition voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_ADD_001",
        voucher_type="إذن اضافة",
        date="2024-01-01"
    )
    
    # Add items to voucher
    test_quantities = [Decimal('10.00'), Decimal('20.00'), Decimal('15.00')]
    for i, product in enumerate(products):
        VoucherItem.objects.create(
            voucher=voucher,
            product=product,
            quantity_added=test_quantities[i]
        )
        # Simulate the effect of voucher creation
        product.quantity += test_quantities[i]
        product.save()
    
    # Record quantities before deletion
    quantities_before = {p.product_id: p.quantity for p in products}
    print("Quantities before deletion:", quantities_before)
    
    # Test deletion
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("Deletion successful!")
        
        # Check quantities after deletion
        for product in products:
            product.refresh_from_db()
        quantities_after = {p.product_id: p.quantity for p in products}
        print("Quantities after deletion:", quantities_after)
        
        # Verify the quantities were correctly reversed
        for i, product in enumerate(products):
            expected_quantity = Decimal('100.00')  # Original quantity
            if product.quantity != expected_quantity:
                print(f"❌ ERROR: Product {product.product_id} quantity is {product.quantity}, expected {expected_quantity}")
                return False
            else:
                print(f"✅ Product {product.product_id} quantity correctly restored to {product.quantity}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False
    finally:
        # Cleanup
        voucher.delete()

def test_withdrawal_voucher_deletion():
    """Test deletion of withdrawal voucher (إذن صرف)"""
    print("\n=== Testing Withdrawal Voucher Deletion ===")
    
    products = create_test_data()
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_WITHDRAW_001",
        voucher_type="إذن صرف",
        date="2024-01-01"
    )
    
    # Add items to voucher
    test_quantities = [Decimal('10.00'), Decimal('20.00'), Decimal('15.00')]
    for i, product in enumerate(products):
        VoucherItem.objects.create(
            voucher=voucher,
            product=product,
            quantity_disbursed=test_quantities[i]
        )
        # Simulate the effect of voucher creation
        product.quantity -= test_quantities[i]
        product.save()
    
    # Record quantities before deletion
    quantities_before = {p.product_id: p.quantity for p in products}
    print("Quantities before deletion:", quantities_before)
    
    # Test deletion
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("Deletion successful!")
        
        # Check quantities after deletion
        for product in products:
            product.refresh_from_db()
        quantities_after = {p.product_id: p.quantity for p in products}
        print("Quantities after deletion:", quantities_after)
        
        # Verify the quantities were correctly reversed
        for i, product in enumerate(products):
            expected_quantity = Decimal('100.00')  # Original quantity
            if product.quantity != expected_quantity:
                print(f"❌ ERROR: Product {product.product_id} quantity is {product.quantity}, expected {expected_quantity}")
                return False
            else:
                print(f"✅ Product {product.product_id} quantity correctly restored to {product.quantity}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False
    finally:
        # Cleanup
        voucher.delete()

def test_customer_return_voucher_deletion():
    """Test deletion of customer return voucher (اذن مرتجع عميل)"""
    print("\n=== Testing Customer Return Voucher Deletion ===")
    
    products = create_test_data()
    
    # Create customer return voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_CUST_RET_001",
        voucher_type="اذن مرتجع عميل",
        date="2024-01-01"
    )
    
    # Add items to voucher
    test_quantities = [Decimal('5.00'), Decimal('8.00'), Decimal('12.00')]
    for i, product in enumerate(products):
        VoucherItem.objects.create(
            voucher=voucher,
            product=product,
            quantity_added=test_quantities[i]
        )
        # Simulate the effect of voucher creation
        product.quantity += test_quantities[i]
        product.save()
    
    # Record quantities before deletion
    quantities_before = {p.product_id: p.quantity for p in products}
    print("Quantities before deletion:", quantities_before)
    
    # Test deletion
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("Deletion successful!")
        
        # Check quantities after deletion
        for product in products:
            product.refresh_from_db()
        quantities_after = {p.product_id: p.quantity for p in products}
        print("Quantities after deletion:", quantities_after)
        
        # Verify the quantities were correctly reversed
        for i, product in enumerate(products):
            expected_quantity = Decimal('100.00')  # Original quantity
            if product.quantity != expected_quantity:
                print(f"❌ ERROR: Product {product.product_id} quantity is {product.quantity}, expected {expected_quantity}")
                return False
            else:
                print(f"✅ Product {product.product_id} quantity correctly restored to {product.quantity}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False
    finally:
        # Cleanup
        voucher.delete()

def test_supplier_return_voucher_deletion():
    """Test deletion of supplier return voucher (إذن مرتجع مورد)"""
    print("\n=== Testing Supplier Return Voucher Deletion ===")
    
    products = create_test_data()
    
    # Create supplier return voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_SUPP_RET_001",
        voucher_type="إذن مرتجع مورد",
        date="2024-01-01"
    )
    
    # Add items to voucher
    test_quantities = [Decimal('7.00'), Decimal('12.00'), Decimal('9.00')]
    for i, product in enumerate(products):
        VoucherItem.objects.create(
            voucher=voucher,
            product=product,
            quantity_disbursed=test_quantities[i]
        )
        # Simulate the effect of voucher creation
        product.quantity -= test_quantities[i]
        product.save()
    
    # Record quantities before deletion
    quantities_before = {p.product_id: p.quantity for p in products}
    print("Quantities before deletion:", quantities_before)
    
    # Test deletion
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("Deletion successful!")
        
        # Check quantities after deletion
        for product in products:
            product.refresh_from_db()
        quantities_after = {p.product_id: p.quantity for p in products}
        print("Quantities after deletion:", quantities_after)
        
        # Verify the quantities were correctly reversed
        for i, product in enumerate(products):
            expected_quantity = Decimal('100.00')  # Original quantity
            if product.quantity != expected_quantity:
                print(f"❌ ERROR: Product {product.product_id} quantity is {product.quantity}, expected {expected_quantity}")
                return False
            else:
                print(f"✅ Product {product.product_id} quantity correctly restored to {product.quantity}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False
    finally:
        # Cleanup
        voucher.delete()

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="TEST_PROD_").delete()
    
    # Delete test vouchers (if any remain)
    Voucher.objects.filter(voucher_number__startswith="TEST_").delete()
    
    print("Cleanup completed!")

def main():
    """Run all voucher deletion tests"""
    print("Starting Voucher Deletion Tests...")
    print("=" * 50)
    
    test_results = []
    
    try:
        # Test all voucher types
        test_results.append(("Addition Voucher", test_addition_voucher_deletion()))
        test_results.append(("Withdrawal Voucher", test_withdrawal_voucher_deletion()))
        test_results.append(("Customer Return Voucher", test_customer_return_voucher_deletion()))
        test_results.append(("Supplier Return Voucher", test_supplier_return_voucher_deletion()))
        
        # Print summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY:")
        print("=" * 50)
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 ALL TESTS PASSED! Voucher deletion logic is working correctly.")
        else:
            print("⚠️  SOME TESTS FAILED! Please review the voucher deletion logic.")
        print("=" * 50)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
