"""
Test real voucher deletion using the existing voucher in the system
This will test the actual deletion process on the real voucher found in the system
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

def test_real_voucher_deletion():
    """Test deletion of the real voucher found in the system"""
    print("=== Testing Real Voucher Deletion ===")
    
    # Find the existing withdrawal voucher
    voucher_number = "OUT-20250615-9540"
    
    try:
        voucher = Voucher.objects.get(voucher_number=voucher_number)
        print(f"Found voucher: {voucher.voucher_number}")
        print(f"Type: {voucher.voucher_type}")
        print(f"Date: {voucher.date}")
        
        # Record current state
        print("\nCurrent state before deletion:")
        product_states = {}
        for item in voucher.items.all():
            product = item.product
            product_states[product.product_id] = {
                'name': product.name,
                'current_quantity': product.quantity,
                'quantity_disbursed': item.quantity_disbursed,
                'expected_after_deletion': product.quantity + (item.quantity_disbursed or 0)
            }
            print(f"  Product: {product.name}")
            print(f"    Current quantity: {product.quantity}")
            print(f"    quantity_disbursed: {item.quantity_disbursed}")
            print(f"    Expected after deletion: {product_states[product.product_id]['expected_after_deletion']}")
        
        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will actually delete voucher {voucher_number}")
        print("This is a real voucher in your system!")
        
        # For safety, let's create a backup first
        print("\nCreating backup of voucher data...")
        backup_data = {
            'voucher_number': voucher.voucher_number,
            'voucher_type': voucher.voucher_type,
            'date': voucher.date,
            'supplier': voucher.supplier,
            'department': voucher.department,
            'customer': voucher.customer,
            'notes': voucher.notes,
            'items': []
        }
        
        for item in voucher.items.all():
            backup_data['items'].append({
                'product_id': item.product.product_id,
                'quantity_added': item.quantity_added,
                'quantity_disbursed': item.quantity_disbursed,
                'machine': item.machine,
                'machine_unit': item.machine_unit,
                'unit_price': item.unit_price
            })
        
        print("Backup created successfully!")
        
        # Perform the actual deletion
        print(f"\nPerforming actual deletion of voucher {voucher_number}...")
        
        try:
            # Use the VoucherHandler to delete
            updated_products = VoucherHandler.handle_voucher_deletion(voucher)
            
            print("VoucherHandler.handle_voucher_deletion() completed!")
            print(f"Updated {len(updated_products)} products:")
            
            for prod_info in updated_products:
                print(f"  Product: {prod_info['name']}")
                print(f"    Old quantity: {prod_info['old_quantity']}")
                print(f"    New quantity: {prod_info['new_quantity']}")
                print(f"    Difference: {prod_info['difference']}")
            
            # Now delete the voucher itself
            voucher.delete()
            print(f"Voucher {voucher_number} deleted from database!")
            
            # Verify the results
            print("\nVerifying results:")
            all_correct = True
            for product_id, expected_state in product_states.items():
                try:
                    product = Product.objects.get(product_id=product_id)
                    actual_quantity = product.quantity
                    expected_quantity = expected_state['expected_after_deletion']
                    
                    print(f"  Product: {expected_state['name']}")
                    print(f"    Expected: {expected_quantity}")
                    print(f"    Actual: {actual_quantity}")
                    
                    if actual_quantity == expected_quantity:
                        print(f"    ✅ CORRECT")
                    else:
                        print(f"    ❌ INCORRECT (difference: {actual_quantity - expected_quantity})")
                        all_correct = False
                        
                except Product.DoesNotExist:
                    print(f"    ❌ Product {product_id} not found!")
                    all_correct = False
            
            if all_correct:
                print(f"\n🎉 SUCCESS: Voucher deletion worked correctly!")
                print("All inventory quantities were properly restored.")
            else:
                print(f"\n❌ FAILURE: Voucher deletion did not work correctly!")
                print("Some inventory quantities were not properly restored.")
            
            # Show backup data for potential restoration
            print(f"\nBackup data for voucher {voucher_number}:")
            print("=" * 40)
            import json
            print(json.dumps(backup_data, indent=2, default=str))
            print("=" * 40)
            print("You can use this data to recreate the voucher if needed.")
            
            return all_correct
            
        except Exception as e:
            print(f"❌ ERROR during deletion: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Voucher.DoesNotExist:
        print(f"❌ Voucher {voucher_number} not found")
        return False

def create_and_test_new_voucher():
    """Create a new test voucher and test its deletion"""
    print("\n=== Creating and Testing New Voucher ===")
    
    # Find a product to use
    products = Product.objects.all()[:1]
    if not products:
        print("❌ No products found in the system")
        return False
    
    product = products[0]
    initial_quantity = product.quantity
    withdrawal_quantity = Decimal('1.00')  # Small amount for safety
    
    print(f"Using product: {product.name}")
    print(f"Initial quantity: {initial_quantity}")
    print(f"Withdrawal amount: {withdrawal_quantity}")
    
    # Create test voucher
    voucher = Voucher.objects.create(
        voucher_number="TEST_REAL_WITHDRAWAL",
        voucher_type="إذن صرف",
        date="2024-01-15"
    )
    
    # Add item
    VoucherItem.objects.create(
        voucher=voucher,
        product=product,
        quantity_disbursed=withdrawal_quantity
    )
    
    # Simulate voucher creation effect
    product.quantity -= withdrawal_quantity
    product.save()
    
    print(f"Voucher created: {voucher.voucher_number}")
    print(f"Product quantity after withdrawal: {product.quantity}")
    
    # Test deletion
    try:
        updated_products = VoucherHandler.handle_voucher_deletion(voucher)
        voucher.delete()
        
        product.refresh_from_db()
        final_quantity = product.quantity
        
        print(f"Product quantity after deletion: {final_quantity}")
        
        if final_quantity == initial_quantity:
            print("✅ Test voucher deletion worked correctly!")
            return True
        else:
            print(f"❌ Test voucher deletion failed! Expected {initial_quantity}, got {final_quantity}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test voucher deletion: {e}")
        # Clean up
        try:
            voucher.delete()
        except:
            pass
        return False

def main():
    """Main function"""
    print("Real Voucher Deletion Test")
    print("=" * 30)
    
    # First, test with a new voucher to be safe
    test_result = create_and_test_new_voucher()
    
    if test_result:
        print("\n" + "=" * 50)
        print("Test voucher deletion worked correctly.")
        print("The withdrawal voucher deletion system is functioning properly.")
        print("=" * 50)
        
        # Ask if user wants to test with real voucher
        print("\nThe system appears to be working correctly.")
        print("If you're still experiencing issues, it might be:")
        print("1. Browser cache - try clearing cache and refreshing")
        print("2. User permissions - check if you have delete permissions")
        print("3. JavaScript errors - check browser console")
        print("4. Network issues - check if requests reach the server")
        
    else:
        print("\n" + "=" * 50)
        print("❌ Test voucher deletion failed!")
        print("There is an issue with the withdrawal voucher deletion system.")
        print("=" * 50)

if __name__ == "__main__":
    main()
