"""
URLs for Leaves (Leave Types and Employee Leaves)
"""

from django.urls import path
from ..views import leave_views

app_name = 'leaves'

urlpatterns = [
    # Employee Leave main list and creation
    path('', leave_views.employee_leave_list, name='employee_leave_list'),
    path('create/', leave_views.employee_leave_create, name='employee_leave_create'),
    
    # Analytics
    path('analytics/', leave_views.leave_analytics, name='analytics'),

    # Employee Leave actions
    path('<int:pk>/', leave_views.employee_leave_detail, name='employee_leave_detail'),
    path('<int:pk>/edit/', leave_views.employee_leave_edit, name='employee_leave_edit'),
    path('<int:pk>/delete/', leave_views.employee_leave_delete, name='employee_leave_delete'),
    path('<int:pk>/approve/', leave_views.employee_leave_approve, name='employee_leave_approve'),
    path('<int:pk>/reject/', leave_views.employee_leave_reject, name='employee_leave_reject'),

    # Leave Type management
    path('types/', leave_views.leave_type_list, name='leave_type_list'),
    path('types/create/', leave_views.leave_type_create, name='leave_type_create'),
    path('types/<int:pk>/', leave_views.leave_type_detail, name='leave_type_detail'),
    path('types/<int:pk>/edit/', leave_views.leave_type_edit, name='leave_type_edit'),
    path('types/<int:pk>/delete/', leave_views.leave_type_delete, name='leave_type_delete'),
]
