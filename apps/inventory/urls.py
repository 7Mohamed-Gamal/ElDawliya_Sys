"""
Inventory API URLs.
"""

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='main_dashboard'),

    # Products
    path('items/', views.ProductListView.as_view(), name='product_list'),
    path('items/list/', views.ProductListView.as_view(), name='items'), # Alias for template

    # Purchase Requests
    path('purchase-orders/', views.PurchaseRequestListView.as_view(), name='purchase_request_list'),
    path('purchase-orders/list/', views.PurchaseRequestListView.as_view(), name='purchase_orders'), # Alias

    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/list/', views.SupplierListView.as_view(), name='suppliers'), # Alias

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/list/', views.CategoryListView.as_view(), name='categories'), # Alias

     # Inventory Count (Placeholder if view missing, but linking to product list for now to prevent crash)
    path('count/', views.ProductListView.as_view(), name='inventory_count'),
]