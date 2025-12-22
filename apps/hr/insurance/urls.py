from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Health Insurance Providers
    path('providers/', views.provider_list, name='provider_list'),
    path('providers/add/', views.add_provider, name='add_provider'),
    path('providers/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('providers/<int:provider_id>/edit/', views.edit_provider, name='edit_provider'),
    path('providers/<int:provider_id>/delete/', views.delete_provider, name='delete_provider'),

    # Employee Health Insurance
    path('health/', views.health_insurance_list, name='health_insurance_list'),
    path('health/add/', views.add_health_insurance, name='add_health_insurance'),
    path('health/<int:insurance_id>/', views.health_insurance_detail, name='health_insurance_detail'),
    path('health/<int:insurance_id>/edit/', views.edit_health_insurance, name='edit_health_insurance'),
    path('health/<int:insurance_id>/delete/', views.delete_health_insurance, name='delete_health_insurance'),

    # Employee Social Insurance (GOSI)
    path('social/', views.social_insurance_list, name='social_insurance_list'),
    path('social/add/', views.add_social_insurance, name='add_social_insurance'),
    path('social/<int:insurance_id>/', views.social_insurance_detail, name='social_insurance_detail'),
    path('social/<int:insurance_id>/edit/', views.edit_social_insurance, name='edit_social_insurance'),
    path('social/<int:insurance_id>/delete/', views.delete_social_insurance, name='delete_social_insurance'),

    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_insurance, name='export_insurance'),
    path('reports/expiry-alerts/', views.insurance_expiry_alerts, name='insurance_expiry_alerts'),

    # Employee Portal
    path('my-insurance/', views.my_insurance, name='my_insurance'),

    # AJAX endpoints
    path('ajax/check-status/<int:emp_id>/', views.check_insurance_status, name='check_insurance_status'),

    # Bulk operations
    path('bulk/renew/', views.bulk_renew_insurance, name='bulk_renew_insurance'),
    path('bulk/import/', views.bulk_import_insurance, name='bulk_import_insurance'),

    # Analytics
    path('analytics/', views.insurance_analytics, name='insurance_analytics'),
]
