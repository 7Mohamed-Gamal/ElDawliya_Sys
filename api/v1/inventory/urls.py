"""
Inventory API URLs
روابط API المخزون
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for Inventory ViewSets
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'warehouses', views.WarehouseViewSet, basename='warehouse')
router.register(r'movements', views.InventoryMovementViewSet, basename='movement')
router.register(r'adjustments', views.InventoryAdjustmentViewSet, basename='adjustment')

app_name = 'inventory_api'

urlpatterns = [
    # Product management endpoints
    path('products/bulk-import/', views.BulkProductImportView.as_view(), name='bulk_product_import'),
    path('products/export/', views.ProductExportView.as_view(), name='product_export'),
    path('products/low-stock/', views.LowStockProductsView.as_view(), name='low_stock_products'),
    path('products/barcode-scan/', views.BarcodeScanView.as_view(), name='barcode_scan'),

    # Inventory movement endpoints
    path('movements/receive/', views.ReceiveInventoryView.as_view(), name='receive_inventory'),
    path('movements/issue/', views.IssueInventoryView.as_view(), name='issue_inventory'),
    path('movements/transfer/', views.TransferInventoryView.as_view(), name='transfer_inventory'),

    # Stock management endpoints
    path('stock/levels/', views.StockLevelsView.as_view(), name='stock_levels'),
    path('stock/valuation/', views.StockValuationView.as_view(), name='stock_valuation'),
    path('stock/aging/', views.StockAgingView.as_view(), name='stock_aging'),

    # Supplier management endpoints
    path('suppliers/performance/', views.SupplierPerformanceView.as_view(), name='supplier_performance'),
    path('suppliers/evaluation/', views.SupplierEvaluationView.as_view(), name='supplier_evaluation'),

    # Reports and analytics
    path('reports/dashboard/', views.InventoryDashboardView.as_view(), name='inventory_dashboard'),
    path('reports/analytics/', views.InventoryAnalyticsView.as_view(), name='inventory_analytics'),
    path('reports/turnover/', views.InventoryTurnoverView.as_view(), name='inventory_turnover'),

    # ViewSet URLs
    path('', include(router.urls)),
]
