"""
Inventory API Views
عروض API المخزون
"""

import logging
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ...permissions import HasAPIAccess, ModulePermission
from ...pagination import StandardResultsSetPagination
from ...throttling import APIKeyRateThrottle
from .serializers import (
    ProductSerializer, CategorySerializer, SupplierSerializer,
    WarehouseSerializer, InventoryMovementSerializer, InventoryAdjustmentSerializer
)

# Import inventory services
from apps.inventory.services.inventory_service import InventoryService
from apps.inventory.services.product_service import ProductService
from apps.inventory.services.supplier_service import SupplierService
from apps.inventory.services.warehouse_service import WarehouseService

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management
    مجموعة عروض إدارة المنتجات
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [APIKeyRateThrottle]

    filterset_fields = ['category', 'supplier', 'is_active', 'warehouse']
    search_fields = ['name', 'sku', 'barcode', 'description']
    ordering_fields = ['created_at', 'name', 'unit_price', 'quantity_in_stock']

    def get_queryset(self):
        """Get products based on user permissions"""
        service = ProductService(user=self.request.user)
        return service.get_accessible_products()

    def perform_create(self, serializer):
        """Create product with service layer"""
        service = ProductService(user=self.request.user)
        product = service.create_product(serializer.validated_data)
        serializer.instance = product

    def perform_update(self, serializer):
        """Update product with service layer"""
        service = ProductService(user=self.request.user)
        product = service.update_product(
            serializer.instance,
            serializer.validated_data
        )
        serializer.instance = product

    @swagger_auto_schema(
        operation_description="Get product stock levels across all warehouses",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'total_stock': openapi.Schema(type=openapi.TYPE_NUMBER),
                'available_stock': openapi.Schema(type=openapi.TYPE_NUMBER),
                'reserved_stock': openapi.Schema(type=openapi.TYPE_NUMBER),
                'warehouse_breakdown': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                ),
            }
        )}
    )
    @action(detail=True, methods=['get'])
    def stock_levels(self, request, pk=None):
        """Get product stock levels"""
        product = self.get_object()
        service = InventoryService(user=request.user)

        stock_data = service.get_product_stock_levels(product.id)
        return Response(stock_data)

    @swagger_auto_schema(
        operation_description="Get product movement history",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def movement_history(self, request, pk=None):
        """Get product movement history"""
        product = self.get_object()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        service = InventoryService(user=request.user)
        history = service.get_product_movement_history(
            product.id, start_date, end_date
        )

        return Response(history)

    @action(detail=True, methods=['get'])
    def suppliers(self, request, pk=None):
        """Get product suppliers"""
        product = self.get_object()
        service = ProductService(user=request.user)

        suppliers = service.get_product_suppliers(product.id)
        return Response(suppliers)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for category management
    مجموعة عروض إدارة الفئات
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get categories based on user permissions"""
        service = ProductService(user=self.request.user)
        return service.get_categories()

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in category"""
        category = self.get_object()
        service = ProductService(user=request.user)

        products = service.get_category_products(category.id)
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get category statistics"""
        category = self.get_object()
        service = ProductService(user=request.user)

        stats = service.get_category_statistics(category.id)
        return Response(stats)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for supplier management
    مجموعة عروض إدارة الموردين
    """
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['is_active', 'country', 'supplier_type']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['created_at', 'name', 'rating']

    def get_queryset(self):
        """Get suppliers based on user permissions"""
        service = SupplierService(user=self.request.user)
        return service.get_accessible_suppliers()

    def perform_create(self, serializer):
        """Create supplier with service layer"""
        service = SupplierService(user=self.request.user)
        supplier = service.create_supplier(serializer.validated_data)
        serializer.instance = supplier

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get supplier products"""
        supplier = self.get_object()
        service = SupplierService(user=request.user)

        products = service.get_supplier_products(supplier.id)
        return Response(products)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get supplier performance metrics"""
        supplier = self.get_object()
        service = SupplierService(user=request.user)

        performance = service.get_supplier_performance(supplier.id)
        return Response(performance)

    @action(detail=True, methods=['post'])
    def evaluate(self, request, pk=None):
        """Evaluate supplier performance"""
        supplier = self.get_object()
        service = SupplierService(user=request.user)

        evaluation_data = request.data
        result = service.evaluate_supplier(supplier.id, evaluation_data)

        return Response(result)


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for warehouse management
    مجموعة عروض إدارة المخازن
    """
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get warehouses based on user permissions"""
        service = WarehouseService(user=self.request.user)
        return service.get_accessible_warehouses()

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get warehouse inventory"""
        warehouse = self.get_object()
        service = WarehouseService(user=request.user)

        inventory = service.get_warehouse_inventory(warehouse.id)
        return Response(inventory)

    @action(detail=True, methods=['get'])
    def capacity(self, request, pk=None):
        """Get warehouse capacity utilization"""
        warehouse = self.get_object()
        service = WarehouseService(user=request.user)

        capacity = service.get_warehouse_capacity(warehouse.id)
        return Response(capacity)


class InventoryMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inventory movements
    مجموعة عروض حركات المخزون
    """
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['product', 'warehouse', 'movement_type', 'created_at']
    ordering_fields = ['created_at', 'quantity', 'unit_cost']

    def get_queryset(self):
        """Get inventory movements based on permissions"""
        service = InventoryService(user=self.request.user)
        return service.get_accessible_movements()

    def perform_create(self, serializer):
        """Create inventory movement with service layer"""
        service = InventoryService(user=self.request.user)
        movement = service.create_movement(serializer.validated_data)
        serializer.instance = movement


class InventoryAdjustmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inventory adjustments
    مجموعة عروض تعديلات المخزون
    """
    serializer_class = InventoryAdjustmentSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'manage')]
    pagination_class = StandardResultsSetPagination

    filterset_fields = ['product', 'warehouse', 'adjustment_type', 'status']
    ordering_fields = ['created_at', 'quantity_adjusted']

    def get_queryset(self):
        """Get inventory adjustments based on permissions"""
        service = InventoryService(user=self.request.user)
        return service.get_accessible_adjustments()

    def perform_create(self, serializer):
        """Create inventory adjustment with approval workflow"""
        service = InventoryService(user=self.request.user)
        adjustment = service.create_adjustment(serializer.validated_data)
        serializer.instance = adjustment

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve inventory adjustment"""
        adjustment = self.get_object()
        service = InventoryService(user=request.user)

        result = service.approve_adjustment(adjustment.id)
        return Response(result)


# Additional API Views

class BulkProductImportView(APIView):
    """
    Bulk import products from Excel/CSV
    استيراد مجمع للمنتجات من Excel/CSV
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'add')]

    def post(self, request):
        """Import products from uploaded file"""
        service = ProductService(user=request.user)

        file_obj = request.FILES.get('file')
        file_format = request.data.get('format', 'excel')

        if not file_obj:
            return Response(
                {'error': 'لم يتم رفع ملف'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = service.bulk_import_products(file_obj, file_format)
        return Response(result)


class ProductExportView(APIView):
    """
    Export products to Excel/CSV
    تصدير المنتجات إلى Excel/CSV
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Export products to specified format"""
        service = ProductService(user=request.user)

        export_format = request.query_params.get('format', 'excel')
        filters = {
            'category': request.query_params.get('category'),
            'supplier': request.query_params.get('supplier'),
            'warehouse': request.query_params.get('warehouse'),
        }

        result = service.export_products(export_format, filters)
        return result


class LowStockProductsView(APIView):
    """
    Get products with low stock levels
    الحصول على المنتجات ذات المستويات المنخفضة من المخزون
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get low stock products"""
        service = InventoryService(user=request.user)

        threshold = request.query_params.get('threshold', 'default')
        warehouse = request.query_params.get('warehouse')

        low_stock_products = service.get_low_stock_products(threshold, warehouse)
        return Response(low_stock_products)


class BarcodeScanView(APIView):
    """
    Scan barcode and get product information
    مسح الباركود والحصول على معلومات المنتج
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def post(self, request):
        """Scan barcode and return product info"""
        service = ProductService(user=request.user)

        barcode = request.data.get('barcode')
        if not barcode:
            return Response(
                {'error': 'الباركود مطلوب'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_info = service.scan_barcode(barcode)
        return Response(product_info)


class ReceiveInventoryView(APIView):
    """
    Receive inventory into warehouse
    استلام المخزون في المخزن
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'add')]

    def post(self, request):
        """Receive inventory"""
        service = InventoryService(user=request.user)

        receive_data = request.data
        result = service.receive_inventory(receive_data)

        return Response(result)


class IssueInventoryView(APIView):
    """
    Issue inventory from warehouse
    إصدار المخزون من المخزن
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'change')]

    def post(self, request):
        """Issue inventory"""
        service = InventoryService(user=request.user)

        issue_data = request.data
        result = service.issue_inventory(issue_data)

        return Response(result)


class TransferInventoryView(APIView):
    """
    Transfer inventory between warehouses
    نقل المخزون بين المخازن
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'change')]

    def post(self, request):
        """Transfer inventory"""
        service = InventoryService(user=request.user)

        transfer_data = request.data
        result = service.transfer_inventory(transfer_data)

        return Response(result)


class StockLevelsView(APIView):
    """
    Get current stock levels across all warehouses
    الحصول على مستويات المخزون الحالية عبر جميع المخازن
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get stock levels"""
        service = InventoryService(user=request.user)

        warehouse = request.query_params.get('warehouse')
        category = request.query_params.get('category')

        stock_levels = service.get_stock_levels(warehouse, category)
        return Response(stock_levels)


class StockValuationView(APIView):
    """
    Get stock valuation report
    الحصول على تقرير تقييم المخزون
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get stock valuation"""
        service = InventoryService(user=request.user)

        valuation_method = request.query_params.get('method', 'fifo')
        as_of_date = request.query_params.get('as_of_date')

        valuation = service.get_stock_valuation(valuation_method, as_of_date)
        return Response(valuation)


class StockAgingView(APIView):
    """
    Get stock aging analysis
    الحصول على تحليل تقادم المخزون
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get stock aging analysis"""
        service = InventoryService(user=request.user)

        aging_periods = request.query_params.get('periods', '30,60,90,180')
        warehouse = request.query_params.get('warehouse')

        aging_analysis = service.get_stock_aging_analysis(aging_periods, warehouse)
        return Response(aging_analysis)


class SupplierPerformanceView(APIView):
    """
    Get supplier performance metrics
    الحصول على مقاييس أداء الموردين
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get supplier performance"""
        service = SupplierService(user=request.user)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        performance = service.get_suppliers_performance(start_date, end_date)
        return Response(performance)


class SupplierEvaluationView(APIView):
    """
    Supplier evaluation and rating
    تقييم وتصنيف الموردين
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'manage')]

    def post(self, request):
        """Submit supplier evaluation"""
        service = SupplierService(user=request.user)

        evaluation_data = request.data
        result = service.submit_supplier_evaluation(evaluation_data)

        return Response(result)


class InventoryDashboardView(APIView):
    """
    Inventory dashboard data
    بيانات لوحة تحكم المخزون
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get inventory dashboard data"""
        service = InventoryService(user=request.user)

        dashboard_data = service.get_inventory_dashboard_data()
        return Response(dashboard_data)


class InventoryAnalyticsView(APIView):
    """
    Inventory analytics and insights
    تحليلات ورؤى المخزون
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get inventory analytics"""
        service = InventoryService(user=request.user)

        analytics = service.get_inventory_analytics()
        return Response(analytics)


class InventoryTurnoverView(APIView):
    """
    Inventory turnover analysis
    تحليل دوران المخزون
    """
    permission_classes = [IsAuthenticated, HasAPIAccess, ModulePermission('inventory', 'view')]

    def get(self, request):
        """Get inventory turnover analysis"""
        service = InventoryService(user=request.user)

        period = request.query_params.get('period', '12')  # months
        category = request.query_params.get('category')

        turnover_analysis = service.get_inventory_turnover_analysis(period, category)
        return Response(turnover_analysis)
