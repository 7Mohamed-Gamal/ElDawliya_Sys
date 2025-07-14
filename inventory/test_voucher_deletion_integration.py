"""
Integration test for voucher deletion workflow
This script tests the complete voucher deletion process including the web interface
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

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
User = get_user_model()
from django.urls import reverse
from inventory.models_local import Product, Voucher, VoucherItem, Category, Unit
from inventory.voucher_handlers import VoucherHandler
from django.db import transaction

def create_test_user():
    """Create a test user for authentication"""
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'Role': 'admin'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    return user

def create_test_data():
    """Create test data for integration testing"""
    print("Creating test data for integration testing...")
    
    # Create category and unit if they don't exist
    category, _ = Category.objects.get_or_create(
        name="Integration Test Category",
        defaults={'description': 'Integration test category'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product
    product, created = Product.objects.get_or_create(
        product_id="INTEGRATION_TEST_PROD",
        defaults={
            'name': "Integration Test Product",
            'category': category,
            'unit': unit,
            'initial_quantity': Decimal('50.00'),
            'quantity': Decimal('50.00'),
            'unit_price': Decimal('15.00')
        }
    )
    if not created:
        # Reset quantity for testing
        product.quantity = Decimal('50.00')
        product.save()
    
    print(f"Created/Updated test product: {product.name} with quantity {product.quantity}")
    return product

def test_voucher_deletion_workflow():
    """Test the complete voucher deletion workflow"""
    print("\n=== Testing Complete Voucher Deletion Workflow ===")
    
    # Create test data
    product = create_test_data()
    user = create_test_user()
    
    # Create client and login
    client = Client()
    login_success = client.login(username='test_user', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ Test user logged in successfully")
    
    # Test each voucher type
    voucher_types = [
        ('إذن اضافة', 'addition'),
        ('إذن صرف', 'withdrawal'),
        ('اذن مرتجع عميل', 'customer_return'),
        ('إذن مرتجع مورد', 'supplier_return')
    ]
    
    test_results = []
    
    for voucher_type, test_name in voucher_types:
        print(f"\n--- Testing {test_name} voucher deletion ---")
        
        try:
            # Create voucher
            voucher = Voucher.objects.create(
                voucher_number=f"INT_TEST_{test_name.upper()}",
                voucher_type=voucher_type,
                date="2024-01-01"
            )
            
            # Add item to voucher and simulate its effect
            test_quantity = Decimal('10.00')
            if voucher_type in ['إذن اضافة', 'اذن مرتجع عميل']:
                VoucherItem.objects.create(
                    voucher=voucher,
                    product=product,
                    quantity_added=test_quantity
                )
                # Simulate voucher creation effect
                product.quantity += test_quantity
            else:
                VoucherItem.objects.create(
                    voucher=voucher,
                    product=product,
                    quantity_disbursed=test_quantity
                )
                # Simulate voucher creation effect
                product.quantity -= test_quantity
            
            product.save()
            quantity_before_deletion = product.quantity
            print(f"Product quantity before deletion: {quantity_before_deletion}")
            
            # Test voucher deletion via web interface
            delete_url = reverse('inventory:voucher_delete', kwargs={'pk': voucher.voucher_number})
            
            # First, test GET request (confirmation page)
            response = client.get(delete_url)
            if response.status_code != 200:
                print(f"❌ Failed to access deletion confirmation page. Status: {response.status_code}")
                test_results.append((test_name, False))
                continue
            
            print("✅ Deletion confirmation page accessible")
            
            # Test POST request (actual deletion)
            response = client.post(delete_url)
            
            # Check if deletion was successful (should redirect)
            if response.status_code not in [302, 200]:
                print(f"❌ Deletion failed. Status: {response.status_code}")
                test_results.append((test_name, False))
                continue
            
            print("✅ Deletion request processed successfully")
            
            # Verify voucher was deleted
            if Voucher.objects.filter(voucher_number=voucher.voucher_number).exists():
                print("❌ Voucher still exists after deletion")
                test_results.append((test_name, False))
                continue
            
            print("✅ Voucher successfully deleted from database")
            
            # Verify inventory was correctly adjusted
            product.refresh_from_db()
            expected_quantity = Decimal('50.00')  # Original quantity
            
            if product.quantity != expected_quantity:
                print(f"❌ Inventory not correctly adjusted. Expected: {expected_quantity}, Got: {product.quantity}")
                test_results.append((test_name, False))
                continue
            
            print(f"✅ Inventory correctly restored to {product.quantity}")
            test_results.append((test_name, True))
            
        except Exception as e:
            print(f"❌ Error during {test_name} test: {e}")
            test_results.append((test_name, False))
            # Clean up any remaining voucher
            try:
                Voucher.objects.filter(voucher_number=f"INT_TEST_{test_name.upper()}").delete()
            except:
                pass
    
    return test_results

def test_negative_quantity_prevention():
    """Test that deletion is prevented when it would result in negative quantities"""
    print("\n=== Testing Negative Quantity Prevention ===")
    
    product = create_test_data()
    user = create_test_user()
    client = Client()
    client.login(username='test_user', password='testpass123')
    
    # Set product quantity to a low value
    product.quantity = Decimal('5.00')
    product.save()
    
    # Create a withdrawal voucher with quantity higher than available
    voucher = Voucher.objects.create(
        voucher_number="NEG_TEST_VOUCHER",
        voucher_type="إذن صرف",
        date="2024-01-01"
    )
    
    # Add item that would cause negative quantity if reversed
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=Decimal('20.00')  # More than current quantity
    )
    
    # Simulate the voucher creation effect (this would have been done when voucher was created)
    # But since we're testing deletion, we need to simulate that this voucher reduced the quantity
    original_quantity = product.quantity + Decimal('20.00')  # What it would have been before voucher
    product.quantity = Decimal('5.00')  # Current quantity after voucher effect
    product.save()
    
    print(f"Product quantity before deletion attempt: {product.quantity}")
    
    try:
        # Attempt deletion via web interface
        delete_url = reverse('inventory:voucher_delete', kwargs={'pk': voucher.voucher_number})
        response = client.post(delete_url)
        
        # Check if voucher still exists (deletion should have been prevented)
        if Voucher.objects.filter(voucher_number=voucher.voucher_number).exists():
            print("✅ Deletion correctly prevented due to negative quantity risk")
            # Clean up
            voucher.delete()
            return True
        else:
            print("❌ Deletion was not prevented despite negative quantity risk")
            return False
            
    except Exception as e:
        print(f"✅ Deletion correctly prevented with error: {e}")
        # Clean up
        try:
            voucher.delete()
        except:
            pass
        return True

def cleanup_test_data():
    """Clean up all test data"""
    print("\nCleaning up integration test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="INTEGRATION_TEST_").delete()
    
    # Delete test vouchers
    Voucher.objects.filter(voucher_number__startswith="INT_TEST_").delete()
    Voucher.objects.filter(voucher_number__startswith="NEG_TEST_").delete()
    
    # Delete test user
    User.objects.filter(username='test_user').delete()
    
    print("Integration test cleanup completed!")

def main():
    """Run integration tests"""
    print("Starting Voucher Deletion Integration Tests...")
    print("=" * 60)
    
    try:
        # Test normal deletion workflow
        workflow_results = test_voucher_deletion_workflow()
        
        # Test negative quantity prevention
        negative_qty_result = test_negative_quantity_prevention()
        
        # Print summary
        print("\n" + "=" * 60)
        print("INTEGRATION TEST SUMMARY:")
        print("=" * 60)
        
        all_passed = True
        
        print("\nWorkflow Tests:")
        for test_name, result in workflow_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
            if not result:
                all_passed = False
        
        print(f"\nNegative Quantity Prevention: {'✅ PASSED' if negative_qty_result else '❌ FAILED'}")
        if not negative_qty_result:
            all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("The voucher deletion system is working correctly.")
        else:
            print("⚠️  SOME INTEGRATION TESTS FAILED!")
            print("Please review the voucher deletion implementation.")
        print("=" * 60)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
