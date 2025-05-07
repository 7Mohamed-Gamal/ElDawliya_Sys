from django.urls import path
from . import views

app_name = 'cars'  # تعريف مساحة الاسم لتطبيق السيارات

urlpatterns = [
    path('', views.home, name='home'),
    
    # Car URLs
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.car_add, name='car_add'),
    path('cars/<int:car_id>/edit/', views.car_edit, name='car_edit'),
    path('cars/<int:car_id>/delete/', views.car_delete, name='car_delete'),
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Trip URLs
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/add/', views.trip_add, name='trip_add'),
    path('trips/<int:trip_id>/edit/', views.trip_edit, name='trip_edit'),
    path('trips/<int:trip_id>/delete/', views.trip_delete, name='trip_delete'),
    
    # Settings URL
    path('settings/', views.settings_edit, name='settings_edit'),
    
    # Average Price Calculation
    path('average-price/', views.average_price_calculation, name='average_price'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    
    # Route Points URLs
    path('cars/<int:car_id>/route-points/', views.route_point_list, name='route_point_list'),
    path('cars/<int:car_id>/route-points/add/', views.route_point_add, name='route_point_add'),
    path('route-points/<int:point_id>/edit/', views.route_point_edit, name='route_point_edit'),
    path('route-points/<int:point_id>/delete/', views.route_point_delete, name='route_point_delete'),
    
    # Car Route Report
    path('cars/<int:car_id>/route-report/', views.car_route_report, name='car_route_report'),
]
