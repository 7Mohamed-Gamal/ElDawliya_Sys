import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "hgslduhgfwdv"
TIMEOUT = 30

def test_product_listing_in_inventory():
    # Authenticate with basic token (basic HTTP auth in this case)
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    url = f"{BASE_URL}/api/v1/products/"
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=TIMEOUT)
        # Validate status code
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

        # Validate content type
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected JSON response but got {content_type}"

        data = response.json()
        # Validate that response is a list or dict with products
        assert isinstance(data, list) or (isinstance(data, dict) and "results" in data), "Response JSON structure unexpected"

        # Define products list from response (pagination may return dict with 'results')
        products = data if isinstance(data, list) else data.get("results", [])

        # Validate each product has required fields: id, name, stock, supplier
        required_fields = {"id", "name", "stock", "supplier"}

        for product in products:
            assert isinstance(product, dict), "Each product must be a dictionary"
            missing_fields = required_fields - product.keys()
            assert not missing_fields, f"Product missing fields: {missing_fields}"

            # Validate stock is a non-negative integer
            stock = product.get("stock")
            assert isinstance(stock, int) and stock >= 0, f"Invalid stock value: {stock}"

            # Validate supplier info is present and valid (dict with at least id and name)
            supplier = product.get("supplier")
            assert isinstance(supplier, dict), "Supplier information must be a dictionary"
            assert "id" in supplier and "name" in supplier, "Supplier missing id or name"

    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_product_listing_in_inventory()