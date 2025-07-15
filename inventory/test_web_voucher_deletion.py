"""
Test script to verify voucher deletion through the web interface
This script tests the actual web views to ensure proper inventory balance adjustments.
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

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from inventory.models_local import Product, Voucher, VoucherItem, Category, Unit
from inventory.voucher_handlers import VoucherHandler

User = get_user_model()

def create_test_user():
    """Create a test user for authentication"""
    try:
        user = User.objects.get(username='test_user')
        user.delete()  # Delete if exists to start fresh
    except User.DoesNotExist:
        pass

    user = User.objects.create_user(
        username='test_user',
        password='testpass123'
    )
    # Set additional required fields if they exist
    if hasattr(user, 'is_staff'):
        user.is_staff = True
    if hasattr(user, 'is_superuser'):
        user.is_superuser = True
    user.save()
    return user

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
        product_id="TEST_WEB_PROD_001",
        defaults={
            'name': "Test Web Product",
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

def test_withdrawal_voucher_web_deletion():
    """Test deletion of withdrawal voucher through web interface"""
    print("\n=== Testing Withdrawal Voucher Web Deletion ===")
    
    # Create test data
    product = create_test_data()
    user = create_test_user()
    
    # Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_WEB_WITHDRAW_001",
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
    
    # Create client and login
    client = Client()
    login_success = client.login(username='test_user', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ Test user logged in successfully")
    
    # Test deletion through web interface
    delete_url = reverse('inventory:voucher_delete', kwargs={'pk': voucher.voucher_number})
    print(f"Attempting to delete voucher via URL: {delete_url}")
    
    # First, get the confirmation page
    response = client.get(delete_url)
    if response.status_code != 200:
        print(f"❌ Failed to get delete confirmation page. Status: {response.status_code}")
        return False
    
    print("✅ Delete confirmation page loaded successfully")
    
    # Now perform the actual deletion
    response = client.post(delete_url)
    
    # Check if deletion was successful (should redirect)
    if response.status_code not in [302, 200]:
        print(f"❌ Deletion failed. Status: {response.status_code}")
        return False
    
    print("✅ Voucher deletion request completed")
    
    # Check if voucher was actually deleted
    try:
        Voucher.objects.get(voucher_number=voucher.voucher_number)
        print("❌ Voucher still exists after deletion")
        return False
    except Voucher.DoesNotExist:
        print("✅ Voucher successfully deleted from database")
    
    # Check if product quantity was restored
    product.refresh_from_db()
    expected_quantity = Decimal('100.00')  # Original quantity
    
    if product.quantity != expected_quantity:
        print(f"❌ ERROR: Product quantity is {product.quantity}, expected {expected_quantity}")
        print("❌ Inventory balance was NOT restored correctly!")
        return False
    else:
        print(f"✅ Product quantity correctly restored to {product.quantity}")
        print("✅ Inventory balance restoration working correctly!")
    
    return True

def test_addition_voucher_web_deletion():
    """Test deletion of addition voucher through web interface"""
    print("\n=== Testing Addition Voucher Web Deletion ===")
    
    # Create test data
    product = create_test_data()
    user = create_test_user()
    
    # Create addition voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_WEB_ADD_001",
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
    
    # Create client and login
    client = Client()
    login_success = client.login(username='test_user', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ Test user logged in successfully")
    
    # Test deletion through web interface
    delete_url = reverse('inventory:voucher_delete', kwargs={'pk': voucher.voucher_number})
    print(f"Attempting to delete voucher via URL: {delete_url}")
    
    # Perform the actual deletion
    response = client.post(delete_url)
    
    # Check if deletion was successful (should redirect)
    if response.status_code not in [302, 200]:
        print(f"❌ Deletion failed. Status: {response.status_code}")
        return False
    
    print("✅ Voucher deletion request completed")
    
    # Check if voucher was actually deleted
    try:
        Voucher.objects.get(voucher_number=voucher.voucher_number)
        print("❌ Voucher still exists after deletion")
        return False
    except Voucher.DoesNotExist:
        print("✅ Voucher successfully deleted from database")
    
    # Check if product quantity was restored
    product.refresh_from_db()
    expected_quantity = Decimal('100.00')  # Original quantity
    
    if product.quantity != expected_quantity:
        print(f"❌ ERROR: Product quantity is {product.quantity}, expected {expected_quantity}")
        print("❌ Inventory balance was NOT restored correctly!")
        return False
    else:
        print(f"✅ Product quantity correctly restored to {product.quantity}")
        print("✅ Inventory balance restoration working correctly!")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")

    # Delete test products
    Product.objects.filter(product_id__startswith="TEST_WEB_PROD_").delete()

    # Delete test vouchers (if any remain)
    Voucher.objects.filter(voucher_number__startswith="TEST_WEB_").delete()

    # Delete test user
    try:
        user = User.objects.filter(username='test_user').first()
        if user:
            user.delete()
    except Exception as e:
        print(f"Error deleting test user: {e}")

    print("Cleanup completed!")

def main():
    """Run web interface voucher deletion tests"""
    print("Starting Web Interface Voucher Deletion Tests...")
    print("=" * 60)
    
    test_results = []
    
    try:
        # Test voucher types through web interface
        test_results.append(("Withdrawal Voucher (Web)", test_withdrawal_voucher_web_deletion()))
        test_results.append(("Addition Voucher (Web)", test_addition_voucher_web_deletion()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("WEB INTERFACE TEST SUMMARY:")
        print("=" * 60)
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL WEB TESTS PASSED! Voucher deletion through web interface is working correctly.")
            print("✅ Inventory balance management is functioning properly!")
        else:
            print("⚠️  SOME WEB TESTS FAILED! There may be an issue with the web interface.")
            print("❌ Please check the voucher deletion implementation!")
        print("=" * 60)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
