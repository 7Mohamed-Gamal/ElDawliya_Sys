from django.urls import path
from django.http import HttpResponse

# Simple dummy view function for URLs that would normally use view classes with missing models
def dummy_view(request, *args, **kwargs):
    return HttpResponse("Placeholder view - minimal URLs are being used to fix migration issues.")

app_name = 'inventory'

# Define expanded URL patterns to cover all the paths referenced in templates
urlpatterns = [
    # Main inventory views
    path('', dummy_view, name='dashboard'),
    path('products/', dummy_view, name='product_list'),
    path('products/add/', dummy_view, name='product_add'),
    path('products/basic-add/', dummy_view, name='basic_product_add'),
    path('products/<str:pk>/edit/', dummy_view, name='product_edit'),
    path('products/<str:pk>/delete/', dummy_view, name='product_delete'),

    # Categories
    path('categories/', dummy_view, name='category_list'),
    path('categories/add/', dummy_view, name='category_add'),
    path('categories/<int:pk>/edit/', dummy_view, name='category_edit'),
    path('categories/<int:pk>/delete/', dummy_view, name='category_delete'),

    # Units
    path('units/', dummy_view, name='unit_list'),
    path('units/add/', dummy_view, name='unit_add'),
    path('units/<int:pk>/edit/', dummy_view, name='unit_edit'),
    path('units/<int:pk>/delete/', dummy_view, name='unit_delete'),

    # Invoice URLs (redirected to dummy views)
    path('invoices/', dummy_view, name='invoice_list'),
    path('invoices/add/', dummy_view, name='invoice_add'),
    path('invoices/<str:pk>/', dummy_view, name='invoice_detail'),
    path('invoices/<str:pk>/edit/', dummy_view, name='invoice_edit'),
    path('invoices/<str:pk>/delete/', dummy_view, name='invoice_delete'),

    # Vouchers
    path('vouchers/', dummy_view, name='voucher_list'),
    path('vouchers/add/', dummy_view, name='voucher_add'),
    path('vouchers/<str:pk>/edit/', dummy_view, name='voucher_edit'),
    path('vouchers/<str:pk>/delete/', dummy_view, name='voucher_delete'),
    path('vouchers/<str:pk>/', dummy_view, name='voucher_detail'),
    path('vouchers/generate-number/', dummy_view, name='generate_voucher_number'),

    # Purchase Requests
    path('purchase-requests/', dummy_view, name='purchase_request_list'),
    path('purchase-requests/create/<str:product_id>/', dummy_view, name='create_purchase_request'),
    path('purchase-requests/<int:pk>/update-status/', dummy_view, name='update_purchase_request_status'),

    # Reports
    path('stock/report/', dummy_view, name='stock_report'),
    path('export/csv/', dummy_view, name='export_csv'),

    # Other
    path('check-low-stock/', dummy_view, name='check_low_stock'),
    path('settings/', dummy_view, name='settings'),
    path('system-settings/', dummy_view, name='system_settings'),  # للتوافق مع الروابط القديمة
]
