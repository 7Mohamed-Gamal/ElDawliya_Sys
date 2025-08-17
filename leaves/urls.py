from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Leave requests
    path('requests/', views.leave_list, name='leave_list'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:leave_id>/', views.leave_detail, name='leave_detail'),
    path('requests/<int:leave_id>/edit/', views.edit_leave, name='edit_leave'),
    path('requests/<int:leave_id>/delete/', views.delete_leave, name='delete_leave'),
    path('requests/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('requests/<int:leave_id>/reject/', views.reject_leave, name='reject_leave'),

    # Leave types
    path('types/', views.leave_types, name='leave_types'),
    path('types/add/', views.add_leave_type, name='add_leave_type'),
    path('types/<int:type_id>/', views.get_leave_type, name='get_leave_type'),
    path('types/<int:type_id>/edit/', views.update_leave_type, name='update_leave_type'),
    path('types/<int:type_id>/delete/', views.delete_leave_type, name='delete_leave_type'),
    path('types/<int:type_id>/stats/', views.leave_type_stats, name='leave_type_stats'),

    # Balance reports
    path('balance/', views.balance_report, name='balance_report'),
    path('balance/<int:emp_id>/', views.employee_balance, name='employee_balance'),

    # Holidays
    path('holidays/', views.holidays, name='holidays'),
    path('holidays/add/', views.add_holiday, name='add_holiday'),

    # Employee portal
    path('my-leaves/', views.my_leaves, name='my_leaves'),
    path('my-balance/', views.my_balance, name='my_balance'),
    path('request/', views.request_leave, name='request_leave'),

    # Reports
    path('reports/', views.leave_reports, name='leave_reports'),
    path('export/', views.export_leaves, name='export_leaves'),

    # AJAX endpoints
    path('ajax/check-balance/<int:emp_id>/<int:type_id>/', views.check_leave_balance, name='check_leave_balance'),
    path('ajax/calculate-days/', views.calculate_leave_days, name='calculate_leave_days'),

    # Bulk operations
    path('bulk/approve/', views.bulk_approve_leaves, name='bulk_approve_leaves'),
    path('bulk/reject/', views.bulk_reject_leaves, name='bulk_reject_leaves'),
]

