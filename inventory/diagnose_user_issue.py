"""
Diagnostic script to help identify the specific issue the user is experiencing
This script checks the current state of vouchers and products to identify problems.
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

def check_recent_withdrawal_vouchers():
    """Check recent withdrawal vouchers to see if any have issues"""
    print("=== Checking Recent Withdrawal Vouchers ===")
    
    # Get recent withdrawal vouchers
    withdrawal_vouchers = Voucher.objects.filter(
        voucher_type="إذن صرف"
    ).order_by('-created_at')[:10]
    
    if not withdrawal_vouchers.exists():
        print("❌ No withdrawal vouchers found in the system")
        return False
    
    print(f"✅ Found {withdrawal_vouchers.count()} recent withdrawal vouchers")
    
    for voucher in withdrawal_vouchers:
        print(f"\nVoucher: {voucher.voucher_number}")
        print(f"  Date: {voucher.date}")
        print(f"  Items: {voucher.items.count()}")
        
        # Check each item
        for item in voucher.items.all():
            print(f"    Product: {item.product.name}")
            print(f"    Current Quantity: {item.product.quantity}")
            print(f"    Disbursed Quantity: {item.quantity_disbursed or 0}")
    
    return True

def simulate_voucher_deletion_test():
    """Create a test voucher and simulate deletion to verify the system"""
    print("\n=== Simulating Voucher Deletion Test ===")
    
    try:
        # Find a product with sufficient quantity
        products = Product.objects.filter(quantity__gte=10)[:1]
        if not products.exists():
            print("❌ No products with sufficient quantity found for testing")
            return False
        
        product = products.first()
        original_quantity = product.quantity
        test_quantity = Decimal('5.00')
        
        print(f"✅ Using product: {product.name}")
        print(f"   Original quantity: {original_quantity}")
        
        # Create test withdrawal voucher
        voucher = Voucher.objects.create(
            voucher_number="DIAGNOSTIC_TEST_001",
            voucher_type="إذن صرف",
            date="2024-01-15"
        )
        
        # Add item
        VoucherItem.objects.create(
            voucher=voucher,
            product=product,
            quantity_disbursed=test_quantity
        )
        
        # Simulate voucher creation effect
        product.quantity -= test_quantity
        product.save()
        
        print(f"✅ Created test voucher: {voucher.voucher_number}")
        print(f"   Quantity after withdrawal: {product.quantity}")
        
        # Test deletion
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        
        # Check result
        product.refresh_from_db()
        if product.quantity == original_quantity:
            print(f"✅ SUCCESS: Quantity restored to {product.quantity}")
            result = True
        else:
            print(f"❌ FAILURE: Quantity is {product.quantity}, expected {original_quantity}")
            result = False
        
        # Clean up
        voucher.delete()
        
        # Restore original quantity just in case
        product.quantity = original_quantity
        product.save()
        
        return result
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def check_product_quantities():
    """Check for any products with unusual quantities that might indicate issues"""
    print("\n=== Checking Product Quantities ===")
    
    # Check for negative quantities
    negative_products = Product.objects.filter(quantity__lt=0)
    if negative_products.exists():
        print("⚠️  WARNING: Found products with negative quantities:")
        for product in negative_products:
            print(f"   {product.name}: {product.quantity}")
    else:
        print("✅ No products with negative quantities found")
    
    # Check for very low quantities
    low_products = Product.objects.filter(quantity__lt=5, quantity__gte=0)
    if low_products.exists():
        print(f"\n📊 Found {low_products.count()} products with low quantities (< 5):")
        for product in low_products[:5]:  # Show first 5
            print(f"   {product.name}: {product.quantity}")
    
    # Check for very high quantities (might indicate accumulation issues)
    high_products = Product.objects.filter(quantity__gt=1000)
    if high_products.exists():
        print(f"\n📊 Found {high_products.count()} products with very high quantities (> 1000):")
        for product in high_products[:5]:  # Show first 5
            print(f"   {product.name}: {product.quantity}")

def check_voucher_items_data_integrity():
    """Check for voucher items with missing or incorrect data"""
    print("\n=== Checking Voucher Items Data Integrity ===")
    
    # Check withdrawal vouchers with missing quantity_disbursed
    withdrawal_items = VoucherItem.objects.filter(
        voucher__voucher_type="إذن صرف",
        quantity_disbursed__isnull=True
    )
    
    if withdrawal_items.exists():
        print(f"⚠️  WARNING: Found {withdrawal_items.count()} withdrawal voucher items with missing quantity_disbursed:")
        for item in withdrawal_items[:5]:
            print(f"   Voucher: {item.voucher.voucher_number}, Product: {item.product.name}")
    else:
        print("✅ All withdrawal voucher items have quantity_disbursed values")
    
    # Check addition vouchers with missing quantity_added
    addition_items = VoucherItem.objects.filter(
        voucher__voucher_type="إذن اضافة",
        quantity_added__isnull=True
    )
    
    if addition_items.exists():
        print(f"⚠️  WARNING: Found {addition_items.count()} addition voucher items with missing quantity_added:")
        for item in addition_items[:5]:
            print(f"   Voucher: {item.voucher.voucher_number}, Product: {item.product.name}")
    else:
        print("✅ All addition voucher items have quantity_added values")

def provide_recommendations():
    """Provide recommendations based on the diagnostic results"""
    print("\n=== Recommendations ===")
    
    print("If you're still experiencing issues with voucher deletion:")
    print()
    print("1. **Clear Browser Cache**:")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Clear cache and cookies")
    print("   - Try again")
    print()
    print("2. **Try Incognito Mode**:")
    print("   - Open browser in private/incognito mode")
    print("   - Login and test voucher deletion")
    print()
    print("3. **Check Browser Console**:")
    print("   - Press F12 to open developer tools")
    print("   - Go to Console tab")
    print("   - Look for any error messages")
    print()
    print("4. **Test with Different Voucher**:")
    print("   - Try deleting a different withdrawal voucher")
    print("   - Check if the issue is voucher-specific")
    print()
    print("5. **Check User Permissions**:")
    print("   - Ensure you have 'delete' permission for vouchers")
    print("   - Contact administrator if needed")

def main():
    """Run diagnostic checks"""
    print("Starting Voucher Deletion Issue Diagnosis...")
    print("=" * 60)
    
    diagnostic_results = []
    
    # Run diagnostic checks
    vouchers_ok = check_recent_withdrawal_vouchers()
    diagnostic_results.append(("Recent Vouchers Check", vouchers_ok))
    
    test_ok = simulate_voucher_deletion_test()
    diagnostic_results.append(("Deletion Test", test_ok))
    
    check_product_quantities()
    check_voucher_items_data_integrity()
    
    # Print summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 60)
    
    system_working = True
    for test_name, result in diagnostic_results:
        if result is not None:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                system_working = False
    
    print("\n" + "=" * 60)
    if system_working:
        print("🎉 SYSTEM IS WORKING CORRECTLY!")
        print("✅ The voucher deletion logic is functioning properly.")
        print("✅ The issue is likely browser-related or user-specific.")
    else:
        print("⚠️  SYSTEM ISSUES DETECTED!")
        print("❌ There may be data integrity or system issues.")
        print("❌ Please contact the system administrator.")
    print("=" * 60)
    
    provide_recommendations()

if __name__ == "__main__":
    main()
