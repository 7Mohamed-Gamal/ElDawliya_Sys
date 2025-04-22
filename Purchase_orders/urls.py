from django.urls import path
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

    # API endpoints
    path('api/transfer-product/', views.transfer_product_to_purchase_request, name='transfer_product_to_purchase_request'),
    path('api/check-product/<str:product_id>/', views.check_product_in_purchase_request, name='check_product_in_purchase_request'),
]