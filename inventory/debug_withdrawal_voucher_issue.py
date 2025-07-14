"""
Debug script to investigate potential causes of withdrawal voucher deletion issues
This script checks for common issues that might prevent proper inventory restoration
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

from inventory.models_local import Product, Voucher, VoucherItem
from inventory.voucher_handlers import VoucherHandler
from django.db import transaction

def check_existing_withdrawal_vouchers():
    """Check existing withdrawal vouchers and their structure"""
    print("=== Checking Existing Withdrawal Vouchers ===")
    
    withdrawal_vouchers = Voucher.objects.filter(voucher_type="إذن صرف")
    print(f"Found {withdrawal_vouchers.count()} withdrawal vouchers")
    
    if withdrawal_vouchers.exists():
        print("\nAnalyzing voucher structure:")
        for voucher in withdrawal_vouchers[:5]:  # Check first 5
            print(f"\nVoucher: {voucher.voucher_number}")
            print(f"  Type: '{voucher.voucher_type}'")
            print(f"  Date: {voucher.date}")
            print(f"  Items count: {voucher.items.count()}")
            
            for item in voucher.items.all():
                print(f"    Product: {item.product.name}")
                print(f"      Current quantity: {item.product.quantity}")
                print(f"      quantity_added: {item.quantity_added}")
                print(f"      quantity_disbursed: {item.quantity_disbursed}")
                
                # Check for potential issues
                if item.quantity_disbursed is None or item.quantity_disbursed == 0:
                    print(f"      ⚠️  WARNING: quantity_disbursed is {item.quantity_disbursed}")
                if item.quantity_added is not None and item.quantity_added > 0:
                    print(f"      ⚠️  WARNING: quantity_added is set for withdrawal voucher")

def check_voucher_creation_vs_deletion_logic():
    """Check if voucher creation and deletion logic are consistent"""
    print("\n=== Checking Voucher Creation vs Deletion Logic ===")
    
    # Check voucher creation logic
    print("Voucher creation logic for withdrawal vouchers:")
    print("  - Should set quantity_disbursed field")
    print("  - Should reduce product.quantity")
    
    print("\nVoucher deletion logic for withdrawal vouchers:")
    print("  - Should add back quantity_disbursed to product.quantity")
    
    # Test with a sample
    withdrawal_vouchers = Voucher.objects.filter(voucher_type="إذن صرف")
    if withdrawal_vouchers.exists():
        sample_voucher = withdrawal_vouchers.first()
        print(f"\nSample voucher: {sample_voucher.voucher_number}")
        
        for item in sample_voucher.items.all():
            print(f"  Product: {item.product.name}")
            print(f"    Current quantity: {item.product.quantity}")
            print(f"    quantity_disbursed: {item.quantity_disbursed}")
            
            if item.quantity_disbursed:
                expected_after_deletion = item.product.quantity + item.quantity_disbursed
                print(f"    Expected quantity after deletion: {expected_after_deletion}")

def check_for_multiple_deletion_handlers():
    """Check if there are multiple deletion handlers that might conflict"""
    print("\n=== Checking for Multiple Deletion Handlers ===")
    
    # Check if there are multiple VoucherDeleteView implementations
    from inventory.views.voucher_views import VoucherDeleteView as NewVoucherDeleteView
    
    try:
        from inventory.views_legacy import VoucherDeleteView as LegacyVoucherDeleteView
        print("✅ Found legacy VoucherDeleteView")
        print("⚠️  WARNING: Multiple VoucherDeleteView implementations exist")
        print("   Make sure the correct one is being used in URLs")
    except ImportError:
        print("✅ No legacy VoucherDeleteView found")
    
    # Check URL configuration
    from inventory.urls import urlpatterns
    for pattern in urlpatterns:
        if hasattr(pattern, 'name') and pattern.name == 'voucher_delete':
            print(f"✅ voucher_delete URL found: {pattern}")
            break
    else:
        print("❌ voucher_delete URL not found")

def check_transaction_rollback_issues():
    """Check for potential transaction rollback issues"""
    print("\n=== Checking Transaction Rollback Issues ===")
    
    # Test if there are any database constraints that might cause rollbacks
    withdrawal_vouchers = Voucher.objects.filter(voucher_type="إذن صرف")
    if withdrawal_vouchers.exists():
        sample_voucher = withdrawal_vouchers.first()
        
        print(f"Testing transaction with voucher: {sample_voucher.voucher_number}")
        
        # Simulate the deletion process without actually deleting
        try:
            with transaction.atomic():
                for item in sample_voucher.items.all():
                    product = item.product
                    original_quantity = product.quantity
                    
                    print(f"  Product: {product.name}")
                    print(f"    Original quantity: {original_quantity}")
                    
                    # Simulate the deletion logic
                    if sample_voucher.voucher_type == 'إذن صرف':
                        new_quantity = product.quantity + (item.quantity_disbursed or 0)
                        print(f"    Would become: {new_quantity}")
                        
                        if new_quantity < 0:
                            print(f"    ❌ Would result in negative quantity!")
                        else:
                            print(f"    ✅ Quantity change is valid")
                
                # Don't actually save - this is just a test
                raise Exception("Test rollback")
                
        except Exception as e:
            if "Test rollback" in str(e):
                print("✅ Transaction test completed successfully")
            else:
                print(f"❌ Transaction error: {e}")

def check_browser_cache_issues():
    """Check for potential browser cache issues"""
    print("\n=== Checking for Browser Cache Issues ===")
    
    print("Potential browser cache issues:")
    print("  1. Browser might be showing cached inventory quantities")
    print("  2. AJAX requests might not be refreshing the page")
    print("  3. JavaScript might be interfering with the deletion process")
    
    print("\nRecommendations:")
    print("  - Clear browser cache and cookies")
    print("  - Try deletion in an incognito/private browser window")
    print("  - Check browser developer console for JavaScript errors")
    print("  - Refresh the page after deletion to see updated quantities")

def check_permissions_and_middleware():
    """Check for permission and middleware issues"""
    print("\n=== Checking Permissions and Middleware ===")
    
    print("Potential permission issues:")
    print("  - User might not have proper delete permissions")
    print("  - Middleware might be intercepting the deletion request")
    print("  - CSRF token issues might cause silent failures")
    
    print("\nTo check:")
    print("  - Verify user has 'vouchers.delete' permission")
    print("  - Check server logs for permission denied errors")
    print("  - Ensure CSRF tokens are properly included in forms")

def test_specific_voucher_deletion(voucher_number):
    """Test deletion of a specific voucher by number"""
    print(f"\n=== Testing Specific Voucher Deletion: {voucher_number} ===")
    
    try:
        voucher = Voucher.objects.get(voucher_number=voucher_number)
        print(f"Found voucher: {voucher.voucher_number}")
        print(f"Type: {voucher.voucher_type}")
        print(f"Date: {voucher.date}")
        
        # Record current state
        print("\nCurrent state:")
        for item in voucher.items.all():
            print(f"  Product: {item.product.name}")
            print(f"    Current quantity: {item.product.quantity}")
            print(f"    quantity_disbursed: {item.quantity_disbursed}")
        
        # Test deletion (but don't actually delete)
        print("\nTesting deletion logic:")
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        print("Deletion would result in:")
        for prod_info in updated_products:
            print(f"  Product: {prod_info['name']}")
            print(f"    Old quantity: {prod_info['old_quantity']}")
            print(f"    New quantity: {prod_info['new_quantity']}")
            print(f"    Difference: {prod_info['difference']}")
        
        print("\n⚠️  NOTE: This was a test - the voucher was NOT actually deleted")
        
    except Voucher.DoesNotExist:
        print(f"❌ Voucher {voucher_number} not found")
    except Exception as e:
        print(f"❌ Error testing voucher deletion: {e}")

def main():
    """Run all diagnostic checks"""
    print("Withdrawal Voucher Deletion Diagnostic Tool")
    print("=" * 50)
    
    # Run all checks
    check_existing_withdrawal_vouchers()
    check_voucher_creation_vs_deletion_logic()
    check_for_multiple_deletion_handlers()
    check_transaction_rollback_issues()
    check_browser_cache_issues()
    check_permissions_and_middleware()
    
    # Test specific voucher if any exist
    withdrawal_vouchers = Voucher.objects.filter(voucher_type="إذن صرف")
    if withdrawal_vouchers.exists():
        sample_voucher = withdrawal_vouchers.first()
        test_specific_voucher_deletion(sample_voucher.voucher_number)
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 50)
    print("1. Check the output above for any WARNING or ERROR messages")
    print("2. If no issues found, the problem might be:")
    print("   - Browser cache (clear cache and try again)")
    print("   - User permissions (check user has delete permissions)")
    print("   - JavaScript errors (check browser console)")
    print("   - Network issues (check if deletion request reaches server)")
    print("3. Try deleting a voucher in an incognito browser window")
    print("4. Check server logs during deletion attempt")

if __name__ == "__main__":
    main()
