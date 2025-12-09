from django.urls import path
from django.views.generic import TemplateView
from .views import (
    dashboard_views,
    product_views,
    category_views,
    unit_views,
    supplier_views,
    customer_views,
    department_views,
    voucher_views,
    purchase_request_views,
    report_views,
    api_views,
    settings_views,
    utility_views,
    api_functions,
    product_movement_views
)

app_name = 'inventory'

urlpatterns = [
    # الشاشة الرئيسية (Dashboard)
    path('', dashboard_views.dashboard, name='dashboard'),
    path('check-low-stock/', dashboard_views.check_low_stock, name='check_low_stock'),

    # إدارة الأصناف (Products)
    path('products/', product_views.ProductListView.as_view(), name='product_list'),
    path('products/add/', product_views.ProductCreateView.as_view(), name='product_add'),
    path('products/basic-add/', utility_views.basic_product_add, name='basic_product_add'),
    path('products/<str:pk>/edit/', product_views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<str:pk>/delete/', product_views.ProductDeleteView.as_view(), name='product_delete'),

    # إدارة التصنيفات (Categories)
    path('categories/', category_views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', category_views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/add-ajax/', category_views.category_add_ajax, name='category_add_ajax'),
    path('categories/<int:pk>/edit/', category_views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', category_views.CategoryDeleteView.as_view(), name='category_delete'),

    # إدارة وحدات القياس (Units)
    path('units/', unit_views.UnitListView.as_view(), name='unit_list'),
    path('units/add/', unit_views.UnitCreateView.as_view(), name='unit_add'),
    path('units/add-ajax/', unit_views.unit_add_ajax, name='unit_add_ajax'),
    path('units/<int:pk>/edit/', unit_views.UnitUpdateView.as_view(), name='unit_edit'),
    path('units/<int:pk>/delete/', unit_views.UnitDeleteView.as_view(), name='unit_delete'),

    # إدارة الموردين (Suppliers)
    path('suppliers/', supplier_views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', supplier_views.SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', supplier_views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', supplier_views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # إدارة العملاء (Customers)
    path('customers/', customer_views.CustomerListView.as_view(), name='customer_list'),
    path('customers/add/', customer_views.CustomerCreateView.as_view(), name='customer_add'),
    path('customers/<int:pk>/edit/', customer_views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('customers/<int:pk>/delete/', customer_views.CustomerDeleteView.as_view(), name='customer_delete'),

    # إدارة الأقسام (Departments)
    path('departments/', department_views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', department_views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/<int:pk>/edit/', department_views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', department_views.DepartmentDeleteView.as_view(), name='department_delete'),

    # إدارة الأذونات (Vouchers)
    path('vouchers/', voucher_views.VoucherListView.as_view(), name='voucher_list'),
    path('vouchers/add/', voucher_views.VoucherCreateView.as_view(), name='voucher_add'),
    path('vouchers/<str:pk>/', voucher_views.VoucherDetailView.as_view(), name='voucher_detail'),
    path('vouchers/<str:pk>/edit/', voucher_views.VoucherUpdateView.as_view(), name='voucher_edit'),
    path('vouchers/<str:pk>/delete/', voucher_views.VoucherDeleteView.as_view(), name='voucher_delete'),
    path('api/generate-voucher-number/', voucher_views.generate_voucher_number, name='generate_voucher_number'),

    # إدارة طلبات الشراء (Purchase Requests)
    path('purchase-requests/', purchase_request_views.PurchaseRequestListView.as_view(), name='purchase_request_list'),
    path('purchase-requests/add/', purchase_request_views.PurchaseRequestCreateView.as_view(), name='purchase_request_add'),
    path('purchase-requests/<int:pk>/edit/', purchase_request_views.PurchaseRequestUpdateView.as_view(), name='purchase_request_edit'),
    path('purchase-requests/<int:pk>/delete/', purchase_request_views.PurchaseRequestDeleteView.as_view(), name='purchase_request_delete'),
    path('purchase-requests/<int:pk>/complete/', purchase_request_views.mark_purchase_request_as_completed, name='purchase_request_complete'),
    path('purchase-requests/create/<str:product_id>/', purchase_request_views.create_purchase_request, name='create_purchase_request'),

    # تقارير المخزون
    path('reports/stock/', report_views.stock_report, name='stock_report'),
    path('reports/movement/', report_views.movement_report, name='movement_report'),
    path('reports/vouchers/', report_views.voucher_report, name='voucher_report'),

    # حركات الأصناف (Product Movements)
    path('product-movements/', product_movement_views.ProductMovementListView.as_view(), name='product_movement_list'),
    path('product-movements/<str:product_id>/', product_movement_views.ProductMovementView.as_view(), name='product_movements'),

    # واجهة برمجة التطبيقات (API)
    path('api/search-products-get/', api_views.search_products, name='search_products'),  # GET endpoint for search
    path('api/product-details/<str:product_id>/', api_views.get_product_details, name='get_product_details'),  # GET endpoint for product details
    path('api/product-details/', api_functions.product_details_api, name='product_details_api'),  # POST endpoint for product details
    path('api/search-products/', api_functions.search_products_api, name='search_products_api'),  # POST endpoint for search
    path('api/products-search/', api_functions.search_products_api, name='products_search_api'),  # Alias for the modal search
    path('api/categories/', api_functions.get_categories_api, name='categories_api'),  # For the modal category filter
    path('api/units/', api_functions.get_units_api, name='units_api'),  # For the modal unit filter
    path('api/get-categories/', api_views.get_categories, name='get_categories'),
    path('api/get-units/', api_views.get_units, name='get_units'),
    path('api/get-suppliers/', api_views.get_suppliers, name='get_suppliers'),
    path('api/get-customers/', api_views.get_customers, name='get_customers'),
    path('api/get-departments/', api_views.get_departments, name='get_departments'),
    path('api/check-product-exists/', utility_views.check_product_exists, name='check_product_exists'),
    path('api/check-product-quantity/', utility_views.check_product_quantity, name='check_product_quantity'),

    # إعدادات النظام
    path('settings/', settings_views.settings_view, name='settings'),
    path('settings/reset/', settings_views.reset_settings, name='reset_settings'),
    path('system-settings/', settings_views.system_settings, name='system_settings'),  # للتوافق مع الروابط القديمة

    # صفحات التشخيص والاختبار
    path('debug/', utility_views.debug_view, name='debug'),
    path('test-form/', TemplateView.as_view(template_name='inventory/test_form.html'), name='test_form'),

    # للتوافق مع الروابط القديمة
    path('invoices/', voucher_views.VoucherListView.as_view(), name='invoice_list'),
    path('invoices/add/', voucher_views.VoucherCreateView.as_view(), name='invoice_add'),
    path('invoices/<str:pk>/edit/', voucher_views.VoucherUpdateView.as_view(), name='invoice_edit'),
    path('invoices/<str:pk>/delete/', voucher_views.VoucherDeleteView.as_view(), name='invoice_delete'),
    path('invoices/<str:pk>/', voucher_views.VoucherDetailView.as_view(), name='invoice_detail'),
]
