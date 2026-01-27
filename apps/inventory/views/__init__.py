"""
Views package for the inventory application.
This file imports all views from their respective modules to maintain backward compatibility.
"""

from .dashboard_views import dashboard
from .product_views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView
from .purchase_request_views import PurchaseRequestListView
from .supplier_views import SupplierListView
from .category_views import CategoryListView
from .voucher_views import VoucherListView
