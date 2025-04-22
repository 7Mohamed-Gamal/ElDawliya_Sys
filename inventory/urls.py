from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # الشاشة الرئيسية (Dashboard)
    path('', views.dashboard, name='dashboard'),

    # إدارة الأصناف (Products)
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<str:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<str:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # إدارة التصنيفات (Categories)
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # إدارة الفواتير (Invoices)
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/add/', views.InvoiceCreateView.as_view(), name='invoice_add'),
    path('invoices/<str:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('invoices/<str:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('invoices/<str:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),

    # تقارير المخزون
    path('stock/report/', views.StockReportView.as_view(), name='stock_report'),
    path('export/csv/', views.export_to_csv, name='export_csv'),

    # إعدادات النظام
    path('settings/', views.system_settings, name='system_settings'),
]
