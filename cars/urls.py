from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Car Management
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.add_car, name='add_car'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/<int:car_id>/edit/', views.edit_car, name='edit_car'),
    path('cars/<int:car_id>/delete/', views.delete_car, name='delete_car'),
    
    # Supplier Management
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
    
    # Trip Management
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/add/', views.add_trip, name='add_trip'),
    path('trips/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trips/<int:trip_id>/edit/', views.edit_trip, name='edit_trip'),
    path('trips/<int:trip_id>/delete/', views.delete_trip, name='delete_trip'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_trips, name='export_trips'),
    
    # AJAX endpoints
    path('ajax/calculate-cost/', views.calculate_trip_cost, name='calculate_trip_cost'),
    
    # Analytics
    path('analytics/', views.car_analytics, name='car_analytics'),
]