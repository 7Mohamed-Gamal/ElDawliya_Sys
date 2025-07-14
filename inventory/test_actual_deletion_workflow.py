"""
Test the actual deletion workflow as it happens in the web interface
This script tests the exact same process that occurs when deleting via the web interface
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
from inventory.views.voucher_views import VoucherDeleteView
from django.db import transaction
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpRequest

User = get_user_model()

def create_test_data():
    """Create test data"""
    print("Creating test data...")
    
    # Create category and unit
    category, _ = Category.objects.get_or_create(
        name="Actual Test Category",
        defaults={'description': 'Test category for actual deletion testing'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product
    product, created = Product.objects.get_or_create(
        product_id="ACTUAL_TEST_PROD",
        defaults={
            'name': "Actual Test Product",
            'category': category,
            'unit': unit,
            'initial_quantity': Decimal('200.00'),
            'quantity': Decimal('200.00'),
            'unit_price': Decimal('30.00')
        }
    )
    if not created:
        product.quantity = Decimal('200.00')
        product.save()
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='actual_test_user',
        defaults={
            'email': 'actual_test@example.com',
            'first_name': 'Actual',
            'last_name': 'Test',
            'is_staff': True,
            'is_superuser': True,
            'Role': 'admin'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    print(f"Test product: {product.name} with quantity {product.quantity}")
    print(f"Test user: {user.username}")
    return product, user

def test_actual_voucher_deletion_workflow():
    """Test the actual voucher deletion workflow as it happens in the web interface"""
    print("\n=== Testing Actual Voucher Deletion Workflow ===")
    
    product, user = create_test_data()
    initial_quantity = product.quantity
    withdrawal_quantity = Decimal('50.00')
    
    print(f"Initial product quantity: {initial_quantity}")
    print(f"Withdrawal quantity: {withdrawal_quantity}")
    
    # Step 1: Create withdrawal voucher (simulating voucher creation)
    print("\n--- Step 1: Creating withdrawal voucher ---")
    voucher = Voucher.objects.create(
        voucher_number="ACTUAL_TEST_WITHDRAWAL",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Add item to voucher
    voucher_item = VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=withdrawal_quantity
    )
    
    # Simulate the effect of voucher creation (reduce inventory)
    product.quantity -= withdrawal_quantity
    product.save()
    
    quantity_after_withdrawal = product.quantity
    print(f"Product quantity after withdrawal: {quantity_after_withdrawal}")
    
    # Step 2: Test deletion using the actual VoucherDeleteView
    print("\n--- Step 2: Testing deletion using VoucherDeleteView ---")
    
    try:
        # Create a request factory to simulate web request
        factory = RequestFactory()
        request = factory.post(f'/inventory/vouchers/{voucher.voucher_number}/delete/')
        request.user = user
        
        # Create the view instance
        view = VoucherDeleteView()
        view.request = request
        view.kwargs = {'pk': voucher.voucher_number}
        
        print("Calling VoucherDeleteView.delete() method...")
        
        # Get the voucher object (as the view would)
        voucher_obj = view.get_object()
        print(f"Retrieved voucher: {voucher_obj.voucher_number}")
        print(f"Voucher type: '{voucher_obj.voucher_type}'")
        
        # Call the deletion handler (as the view does)
        updated_products = VoucherHandler.handle_voucher_deletion(voucher_obj)
        
        print(f"VoucherHandler returned {len(updated_products)} updated products")
        for prod_info in updated_products:
            print(f"  Product: {prod_info['name']}")
            print(f"    Old quantity: {prod_info['old_quantity']}")
            print(f"    New quantity: {prod_info['new_quantity']}")
            print(f"    Difference: {prod_info['difference']}")
        
        # Check the actual product quantity
        product.refresh_from_db()
        final_quantity = product.quantity
        print(f"\nProduct quantity after deletion: {final_quantity}")
        
        # Now delete the voucher (as the view would)
        voucher_obj.delete()
        print("Voucher deleted from database")
        
        # Verify the result
        expected_quantity = initial_quantity
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

def test_direct_handler_call():
    """Test calling the handler directly on an existing voucher"""
    print("\n=== Testing Direct Handler Call ===")
    
    product, user = create_test_data()
    initial_quantity = product.quantity
    withdrawal_quantity = Decimal('30.00')
    
    # Create voucher with withdrawal
    voucher = Voucher.objects.create(
        voucher_number="DIRECT_TEST_WITHDRAWAL",
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
    
    print(f"Before deletion: {product.quantity}")
    
    # Call handler directly
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        product.refresh_from_db()
        print(f"After deletion: {product.quantity}")
        
        # Clean up
        voucher.delete()
        
        return product.quantity == initial_quantity
        
    except Exception as e:
        print(f"Error: {e}")
        voucher.delete()
        return False

def check_existing_vouchers():
    """Check if there are any existing withdrawal vouchers in the system"""
    print("\n=== Checking Existing Withdrawal Vouchers ===")
    
    withdrawal_vouchers = Voucher.objects.filter(voucher_type="إذن صرف")
    print(f"Found {withdrawal_vouchers.count()} withdrawal vouchers in the system")
    
    if withdrawal_vouchers.exists():
        print("Sample withdrawal vouchers:")
        for voucher in withdrawal_vouchers[:3]:  # Show first 3
            print(f"  {voucher.voucher_number} - {voucher.date}")
            for item in voucher.items.all()[:2]:  # Show first 2 items
                print(f"    {item.product.name}: {item.quantity_disbursed}")

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="ACTUAL_TEST_").delete()
    
    # Delete test vouchers
    Voucher.objects.filter(voucher_number__startswith="ACTUAL_TEST_").delete()
    Voucher.objects.filter(voucher_number__startswith="DIRECT_TEST_").delete()
    
    # Delete test user
    User.objects.filter(username='actual_test_user').delete()
    
    print("Cleanup completed!")

def main():
    """Run the actual deletion workflow tests"""
    print("Testing Actual Voucher Deletion Workflow...")
    print("=" * 50)
    
    try:
        # Check existing vouchers first
        check_existing_vouchers()
        
        # Test direct handler call
        direct_success = test_direct_handler_call()
        
        # Test actual workflow
        workflow_success = test_actual_voucher_deletion_workflow()
        
        # Summary
        print("\n" + "=" * 50)
        print("ACTUAL WORKFLOW TEST SUMMARY:")
        print("=" * 50)
        print(f"Direct handler call: {'✅ PASSED' if direct_success else '❌ FAILED'}")
        print(f"Actual workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
        
        if direct_success and workflow_success:
            print("\n🎉 WITHDRAWAL VOUCHER DELETION IS WORKING CORRECTLY!")
            print("The issue might be in a different part of the system.")
        else:
            print("\n⚠️ ISSUE CONFIRMED: There is a problem with withdrawal voucher deletion.")
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
