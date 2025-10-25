"""
URLs for Employees
"""

from django.urls import path
# Ensure we import from the refactored employee_views
from ..views import employee_views

# app_name is defined in the main urls.py inclusion, so it's not strictly needed here
# but can be kept for clarity.
app_name = 'employees'

urlpatterns = [
    # Employee list and creation
    path('', employee_views.employee_list, name='list'),
    path('create/', employee_views.employee_create, name='create'),
    
    # AJAX endpoints
    # path('ajax/', employee_views.employee_list_ajax, name='list_ajax'), # This was removed in refactoring

    # Employee detail and actions
    # The employee identifier is now a string (employee_id), not an integer.
    path('<str:employee_id>/', employee_views.employee_detail, name='detail'),
    path('<str:employee_id>/edit/', employee_views.employee_edit, name='edit'),
    path('<str:employee_id>/delete/', employee_views.employee_delete, name='delete'),
    # path('<str:employee_id>/print/', employee_views.employee_print, name='print'), # This was removed

    # Standalone pages
    path('search/', employee_views.employee_search, name='search'),
    path('export/', employee_views.employee_export, name='export'),
]
