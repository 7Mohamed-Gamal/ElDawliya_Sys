from django.urls import path
from django.views.generic.base import RedirectView
from django.views.generic.base import RedirectView
from . import views

app_name = 'Purchase_orders'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Purchase Requests
    path('requests/', views.PurchaseRequestListView.as_view(), name='purchase_request_list'),
    path('requests/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='purchase_request_detail'),
    path('requests/create/', views.create_purchase_request, name='create_purchase_request'),
    path('requests/<int:pk>/add-item/', views.add_purchase_request_item, name='add_purchase_request_item'),
    path('requests/<int:pk>/approve/', views.approve_purchase_request, name='approve_purchase_request'),
    path('requests/<int:pk>/delete/', views.delete_purchase_request, name='delete_purchase_request'),

    # Request Status Views
    path('requests/pending/', views.pending_approval_list, name='pending_approval'),
    path('requests/approved/', views.approved_requests_list, name='approved_requests'),
    path('requests/rejected/', views.rejected_requests_list, name='rejected_requests'),

    # Vendors
    path('vendors/', views.vendors_list, name='vendors'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # API endpoints
    path('api/transfer-product/', views.transfer_product_to_purchase_request, name='transfer_product_to_purchase_request'),
    path('api/check-product/<str:product_id>/', views.check_product_in_purchase_request, name='check_product_in_purchase_request'),
    path('api/products/', views.get_products_api, name='get_products_api'),

    # Vendor API endpoints
    path('vendors/<int:vendor_id>/edit/', views.get_vendor_details, name='get_vendor_details'),
    path('vendors/create/', views.create_vendor, name='create_vendor'),
    path('vendors/<int:vendor_id>/update/', views.update_vendor, name='update_vendor'),
    path('vendors/<int:vendor_id>/delete/', views.delete_vendor, name='delete_vendor'),

    # Legacy URL redirects
    path('requests/detail/<int:pk>/', RedirectView.as_view(pattern_name='Purchase_orders:purchase_request_detail'), name='legacy_request_detail'),

    # Legacy URL redirects
    path('requests/detail/<int:pk>/', RedirectView.as_view(pattern_name='Purchase_orders:purchase_request_detail'), name='legacy_request_detail'),
]
