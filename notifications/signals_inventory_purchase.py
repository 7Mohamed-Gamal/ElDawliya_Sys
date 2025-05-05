from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

from inventory.models_local import PurchaseRequest as InventoryPurchaseRequest
from Purchase_orders.models import PurchaseRequest as PurchaseOrderRequest
from Purchase_orders.models import PurchaseRequestItem
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=InventoryPurchaseRequest)
def sync_purchase_requests(sender, instance, created, **kwargs):
    """
    Signal to synchronize purchase requests between inventory app and Purchase_orders app.
    When a purchase request is created in the inventory app, 
    create a corresponding request in the Purchase_orders app.
    """
    if created:
        # Get the requesting user, or use the first active admin if not available
        requesting_user = None
        # Try to get the first admin user as a fallback
        try:
            requesting_user = User.objects.filter(is_staff=True, is_active=True).first()
        except:
            # If no admin user exists, try to get any active user
            requesting_user = User.objects.filter(is_active=True).first()
        
        if not requesting_user:
            return  # Can't continue without a user
        
        # Create a unique request number
        request_number = f"PR-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the purchase request in the Purchase_orders app
        purchase_request = PurchaseOrderRequest.objects.create(
            request_number=request_number,
            requested_by=requesting_user,
            status='pending',
            notes=f"Auto-created from inventory purchase request for product: {instance.product.name}"
        )
        
        # Find the equivalent TblProducts record for the local Product
        from inventory.models import TblProducts
        
        product = instance.product
        product_id = product.product_id
        
        print(f"DEBUG: Syncing purchase request for Product ID: {product_id}, Name: {product.name}")
        print(f"DEBUG: Looking for TblProducts record with product_id = {product_id}")
        
        # First, let's check if the TblProducts record exists
        tbl_products_count = TblProducts.objects.filter(product_id=product_id).count()
        print(f"DEBUG: Found {tbl_products_count} matching TblProducts records")
        
        tbl_products_all = TblProducts.objects.all()[:5]  # Get first 5 for sampling
        print(f"DEBUG: Sample TblProducts IDs: {[p.product_id for p in tbl_products_all]}")
        
        try:
            # Try to find the corresponding TblProducts record based on product_id
            tbl_product = TblProducts.objects.get(product_id=product_id)
            print(f"DEBUG: Successfully got TblProduct: {tbl_product.product_id} - {tbl_product.product_name}")
            
            # Calculate the quantity to request based on thresholds
            suggested_quantity = 1  # Default quantity
            
            # If the product has minimum and maximum thresholds, calculate a proper quantity
            if product.minimum_threshold and product.maximum_threshold:
                if product.quantity < product.minimum_threshold:
                    # Request enough to reach 75% of maximum threshold
                    suggested_quantity = round((product.maximum_threshold * 0.75) - product.quantity)
                    if suggested_quantity <= 0:
                        suggested_quantity = product.minimum_threshold  # At least request the minimum threshold
            
            print(f"DEBUG: Creating PurchaseRequestItem for request {purchase_request.id} with product {tbl_product.product_id}")
            
            # Create a purchase request item for the product
            item = PurchaseRequestItem.objects.create(
                purchase_request=purchase_request,
                product=tbl_product,
                quantity_requested=suggested_quantity,
                status='pending',
                notes=f"Auto-created from inventory purchase request. Current stock: {product.quantity}"
            )
            
            print(f"DEBUG: Created PurchaseRequestItem: ID={item.id}, Product={tbl_product.product_id}, Request={purchase_request.request_number}")
            
            # Verify the item was created and is properly associated with the request
            items = list(PurchaseRequestItem.objects.filter(purchase_request=purchase_request))
            print(f"DEBUG: Request {purchase_request.request_number} has {len(items)} items")
            for i, itm in enumerate(items):
                print(f"DEBUG: Item {i+1}: ID={itm.id}, Product={itm.product.product_id}, Quantity={itm.quantity_requested}")
            
        except TblProducts.DoesNotExist:
            # If we couldn't find a match by exact product_id, try to find a match by name
            print(f"ERROR: Could not find TblProducts record for Product ID: {product_id}")
            
            try:
                # First try looking for a similar product ID
                similar_products = TblProducts.objects.filter(product_id__icontains=product_id)
                if similar_products.exists():
                    tbl_product = similar_products.first()
                    print(f"DEBUG: Found product with similar ID: {tbl_product.product_id}")
                else:
                    # Try to find a product with a similar name
                    product_name = product.name
                    name_matches = TblProducts.objects.filter(product_name__icontains=product_name)
                    
                    if name_matches.exists():
                        tbl_product = name_matches.first()
                        print(f"DEBUG: Found product with similar name: {tbl_product.product_name}, ID: {tbl_product.product_id}")
                    else:
                        # If all else fails, just get the first product (for testing)
                        tbl_product = TblProducts.objects.all().first()
                        print(f"DEBUG: Using first available product as fallback: {tbl_product.product_id}")
                
                # Create the item with the matched product
                suggested_quantity = 1  # Default quantity
                
                # Create a purchase request item with our best guess at the matching product
                item = PurchaseRequestItem.objects.create(
                    purchase_request=purchase_request,
                    product=tbl_product,
                    quantity_requested=suggested_quantity,
                    status='pending',
                    notes=f"Auto-created from inventory purchase request for product {product.name} (ID: {product.product_id})"
                )
                
                print(f"DEBUG: Created PurchaseRequestItem using similar product match: ID={item.id}, Product={tbl_product.product_id}")
            
            except Exception as e:
                print(f"ERROR: Failed to create item with similar product match: {str(e)}")
                
                # Let's try using a direct SQL query as a last resort to check for the product
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT product_id, product_name FROM Tbl_Products WHERE product_id = %s", [product_id])
                        result = cursor.fetchone()
                        if result:
                            print(f"DEBUG: Found product in raw SQL: {result}")
                        else:
                            print(f"DEBUG: Product not found even with raw SQL")
                except Exception as sql_err:
                    print(f"ERROR during SQL query: {str(sql_err)}")
        except Exception as e:
            # Catch any other exceptions during the item creation process
            print(f"ERROR creating purchase request item: {str(e)}")
