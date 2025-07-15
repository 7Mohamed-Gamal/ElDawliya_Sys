"""
Comprehensive verification script for voucher deletion system
This script verifies which view is being used and tests the complete workflow.
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
from django.urls import reverse, resolve
from django.test import RequestFactory

def check_url_configuration():
    """Check which view is actually being used for voucher deletion"""
    print("=== Checking URL Configuration ===")
    
    # Test the URL resolution
    try:
        url = reverse('inventory:voucher_delete', kwargs={'pk': 'TEST_123'})
        print(f"✅ URL resolved: {url}")
        
        # Check which view is mapped to this URL
        resolver_match = resolve(url)
        view_class = resolver_match.func.view_class
        view_module = view_class.__module__
        view_name = view_class.__name__
        
        print(f"✅ View class: {view_module}.{view_name}")
        
        # Check if it's the correct view
        if 'views.voucher_views' in view_module:
            print("✅ Using CURRENT implementation (voucher_views.VoucherDeleteView)")
            return True
        elif 'views_legacy' in view_module:
            print("⚠️  Using LEGACY implementation (views_legacy.VoucherDeleteView)")
            return False
        else:
            print(f"❓ Unknown view implementation: {view_module}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking URL configuration: {e}")
        return False

def check_view_implementation():
    """Check the actual implementation of the view being used"""
    print("\n=== Checking View Implementation ===")
    
    try:
        from inventory.views.voucher_views import VoucherDeleteView
        
        # Check if the view has the correct delete method
        delete_method = getattr(VoucherDeleteView, 'delete', None)
        if delete_method:
            print("✅ VoucherDeleteView.delete method found")
            
            # Check if it uses VoucherHandler
            import inspect
            source = inspect.getsource(delete_method)
            if 'VoucherHandler.handle_voucher_deletion' in source:
                print("✅ View uses VoucherHandler.handle_voucher_deletion")
                return True
            else:
                print("❌ View does NOT use VoucherHandler.handle_voucher_deletion")
                return False
        else:
            print("❌ VoucherDeleteView.delete method not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking view implementation: {e}")
        return False

def create_real_test_scenario():
    """Create a real test scenario similar to what the user experienced"""
    print("\n=== Creating Real Test Scenario ===")
    
    # Create test data
    category, _ = Category.objects.get_or_create(
        name="Test Category Real",
        defaults={'description': 'Real test category'}
    )
    
    unit, _ = Unit.objects.get_or_create(
        name="قطعة",
        defaults={'description': 'Test unit'}
    )
    
    # Create test product with realistic data
    product, created = Product.objects.get_or_create(
        product_id="REAL_TEST_PROD_001",
        defaults={
            'name': "Real Test Product",
            'category': category,
            'unit': unit,
            'initial_quantity': Decimal('50.00'),
            'quantity': Decimal('50.00'),
            'unit_price': Decimal('25.00')
        }
    )
    if not created:
        # Reset quantity for testing
        product.quantity = Decimal('50.00')
        product.save()
    
    print(f"✅ Created test product: {product.name}")
    print(f"   Initial quantity: {product.quantity}")
    
    return product

def test_withdrawal_voucher_scenario(product):
    """Test the exact scenario the user described"""
    print("\n=== Testing Withdrawal Voucher Scenario ===")
    
    # Step 1: Create withdrawal voucher
    voucher = Voucher.objects.create(
        voucher_number="REAL_WITHDRAW_TEST_001",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Step 2: Add items that will be withdrawn
    withdrawn_quantity = Decimal('15.00')
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=withdrawn_quantity
    )
    
    print(f"✅ Created withdrawal voucher: {voucher.voucher_number}")
    print(f"   Withdrawn quantity: {withdrawn_quantity}")
    
    # Step 3: Simulate voucher creation effect (reduce inventory)
    original_quantity = product.quantity
    product.quantity -= withdrawn_quantity
    product.save()
    
    print(f"✅ Inventory reduced from {original_quantity} to {product.quantity}")
    
    # Step 4: Test deletion using VoucherHandler
    print("\n--- Testing Deletion ---")
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        print("✅ VoucherHandler.handle_voucher_deletion() completed")
        
        # Check if inventory was restored
        product.refresh_from_db()
        if product.quantity == original_quantity:
            print(f"✅ SUCCESS: Inventory restored to {product.quantity}")
            print("✅ The voucher deletion system is working correctly!")
            
            # Clean up
            voucher.delete()
            return True
        else:
            print(f"❌ FAILURE: Inventory is {product.quantity}, expected {original_quantity}")
            print("❌ The voucher deletion system is NOT working correctly!")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during deletion: {e}")
        return False

def check_for_potential_issues():
    """Check for potential issues that might cause the problem"""
    print("\n=== Checking for Potential Issues ===")
    
    issues_found = []
    
    # Check 1: Multiple VoucherDeleteView implementations
    try:
        from inventory.views.voucher_views import VoucherDeleteView as CurrentView
        from inventory.views_legacy import VoucherDeleteView as LegacyView
        issues_found.append("⚠️  Multiple VoucherDeleteView implementations exist")
    except ImportError:
        print("✅ No conflicting view implementations found")
    
    # Check 2: Database transaction issues
    try:
        from django.db import transaction
        with transaction.atomic():
            # Test transaction
            pass
        print("✅ Database transactions working correctly")
    except Exception as e:
        issues_found.append(f"❌ Database transaction issue: {e}")
    
    # Check 3: Model field issues
    try:
        # Check if VoucherItem has the correct fields
        from inventory.models_local import VoucherItem
        fields = [f.name for f in VoucherItem._meta.fields]
        required_fields = ['quantity_added', 'quantity_disbursed']
        for field in required_fields:
            if field not in fields:
                issues_found.append(f"❌ Missing field: VoucherItem.{field}")
        
        if not issues_found:
            print("✅ VoucherItem model has all required fields")
    except Exception as e:
        issues_found.append(f"❌ Model field check failed: {e}")
    
    return issues_found

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    # Delete test products
    Product.objects.filter(product_id__startswith="REAL_TEST_PROD_").delete()
    
    # Delete test vouchers
    Voucher.objects.filter(voucher_number__startswith="REAL_").delete()
    
    print("✅ Cleanup completed!")

def main():
    """Run comprehensive verification"""
    print("Starting Comprehensive Voucher Deletion System Verification...")
    print("=" * 70)
    
    verification_results = []
    
    try:
        # Step 1: Check URL configuration
        url_ok = check_url_configuration()
        verification_results.append(("URL Configuration", url_ok))
        
        # Step 2: Check view implementation
        view_ok = check_view_implementation()
        verification_results.append(("View Implementation", view_ok))
        
        # Step 3: Check for potential issues
        issues = check_for_potential_issues()
        verification_results.append(("Potential Issues", len(issues) == 0))
        
        if issues:
            print("\n⚠️  Issues Found:")
            for issue in issues:
                print(f"   {issue}")
        
        # Step 4: Test real scenario
        if url_ok and view_ok:
            product = create_real_test_scenario()
            scenario_ok = test_withdrawal_voucher_scenario(product)
            verification_results.append(("Real Scenario Test", scenario_ok))
        else:
            print("\n❌ Skipping real scenario test due to configuration issues")
            verification_results.append(("Real Scenario Test", False))
        
        # Print summary
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY:")
        print("=" * 70)
        
        all_passed = True
        for test_name, result in verification_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 70)
        if all_passed:
            print("🎉 SYSTEM VERIFICATION PASSED!")
            print("✅ The voucher deletion system is working correctly.")
            print("✅ If the user is still experiencing issues, it might be:")
            print("   - Browser caching")
            print("   - User permissions")
            print("   - Network connectivity")
            print("   - Using a different URL or interface")
        else:
            print("⚠️  SYSTEM VERIFICATION FAILED!")
            print("❌ There are issues with the voucher deletion system.")
            print("❌ Please review the failed components above.")
        print("=" * 70)
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()
