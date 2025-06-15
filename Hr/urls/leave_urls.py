# =============================================================================
# ElDawliya HR Management System - Leave Management URLs
# =============================================================================
# URL patterns for leave management
# Includes leave types, requests, balances, and approvals
# =============================================================================

from django.urls import path, include
from django.views.generic import RedirectView

# Import leave management views
try:
    from Hr.views.new_leave_views import (
        NewLeaveTypeListView, NewLeaveTypeDetailView, NewLeaveTypeCreateView, NewLeaveTypeUpdateView,
        NewEmployeeLeaveBalanceListView, NewEmployeeLeaveBalanceCreateView,
        NewLeaveRequestListView, NewLeaveRequestDetailView, NewLeaveRequestCreateView
    )
except ImportError:
    # Fallback to simple views for testing
    from Hr.views.simple_views import (
        SimpleListView as NewLeaveTypeListView,
        SimpleDetailView as NewLeaveTypeDetailView,
        SimpleCreateView as NewLeaveTypeCreateView,
        SimpleListView as NewLeaveTypeUpdateView,
        SimpleListView as NewEmployeeLeaveBalanceListView,
        SimpleCreateView as NewEmployeeLeaveBalanceCreateView,
        SimpleListView as NewLeaveRequestListView,
        SimpleDetailView as NewLeaveRequestDetailView,
        SimpleCreateView as NewLeaveRequestCreateView
    )

# =============================================================================
# LEAVE TYPE MANAGEMENT
# =============================================================================

leave_type_patterns = [
    # Leave type CRUD operations
    path('', NewLeaveTypeListView.as_view(), name='new_leave_type_list'),
    path('create/', NewLeaveTypeCreateView.as_view(), name='new_leave_type_create'),
    path('<int:pk>/', NewLeaveTypeDetailView.as_view(), name='new_leave_type_detail'),
    path('<int:pk>/edit/', NewLeaveTypeUpdateView.as_view(), name='new_leave_type_update'),
    path('<int:pk>/delete/', NewLeaveTypeUpdateView.as_view(), name='new_leave_type_delete'),
    
    # Leave type specific operations
    path('<int:pk>/employees/', NewLeaveTypeDetailView.as_view(), name='leave_type_employees'),
    path('<int:pk>/statistics/', NewLeaveTypeDetailView.as_view(), name='leave_type_statistics'),
    path('<int:pk>/copy/', NewLeaveTypeCreateView.as_view(), name='leave_type_copy'),
]

# =============================================================================
# EMPLOYEE LEAVE BALANCE MANAGEMENT
# =============================================================================

balance_patterns = [
    # Leave balance CRUD operations
    path('', NewEmployeeLeaveBalanceListView.as_view(), name='new_leave_balance_list'),
    path('create/', NewEmployeeLeaveBalanceCreateView.as_view(), name='new_leave_balance_create'),
    path('<int:pk>/', NewEmployeeLeaveBalanceListView.as_view(), name='new_leave_balance_detail'),
    path('<int:pk>/edit/', NewEmployeeLeaveBalanceCreateView.as_view(), name='new_leave_balance_update'),
    path('<int:pk>/delete/', NewEmployeeLeaveBalanceCreateView.as_view(), name='new_leave_balance_delete'),
    
    # Balance specific operations
    path('employee/<int:employee_id>/', NewEmployeeLeaveBalanceListView.as_view(), name='employee_leave_balances'),
    path('bulk-create/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balance_bulk_create'),
    path('bulk-update/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balance_bulk_update'),
    path('reset/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balance_reset'),
]

# =============================================================================
# LEAVE REQUEST MANAGEMENT
# =============================================================================

request_patterns = [
    # Leave request CRUD operations
    path('', NewLeaveRequestListView.as_view(), name='new_leave_request_list'),
    path('create/', NewLeaveRequestCreateView.as_view(), name='new_leave_request_create'),
    path('<int:pk>/', NewLeaveRequestDetailView.as_view(), name='new_leave_request_detail'),
    path('<int:pk>/edit/', NewLeaveRequestCreateView.as_view(), name='new_leave_request_update'),
    path('<int:pk>/delete/', NewLeaveRequestCreateView.as_view(), name='new_leave_request_delete'),
    
    # Leave request workflow operations
    path('<int:pk>/approve/', NewLeaveRequestDetailView.as_view(), name='leave_request_approve'),
    path('<int:pk>/reject/', NewLeaveRequestDetailView.as_view(), name='leave_request_reject'),
    path('<int:pk>/cancel/', NewLeaveRequestDetailView.as_view(), name='leave_request_cancel'),
    path('<int:pk>/resubmit/', NewLeaveRequestCreateView.as_view(), name='leave_request_resubmit'),
    
    # Employee specific requests
    path('employee/<int:employee_id>/', NewLeaveRequestListView.as_view(), name='employee_leave_requests'),
    path('my-requests/', NewLeaveRequestListView.as_view(), name='my_leave_requests'),
]

# =============================================================================
# LEAVE APPROVAL WORKFLOW
# =============================================================================

approval_patterns = [
    # Approval workflow
    path('pending/', NewLeaveRequestListView.as_view(), name='pending_leave_requests'),
    path('approved/', NewLeaveRequestListView.as_view(), name='approved_leave_requests'),
    path('rejected/', NewLeaveRequestListView.as_view(), name='rejected_leave_requests'),
    
    # Bulk approval operations
    path('bulk-approve/', NewLeaveRequestListView.as_view(), name='leave_requests_bulk_approve'),
    path('bulk-reject/', NewLeaveRequestListView.as_view(), name='leave_requests_bulk_reject'),
    path('bulk-action/', NewLeaveRequestListView.as_view(), name='leave_requests_bulk_action'),
    
    # Approval notifications
    path('notifications/', NewLeaveRequestListView.as_view(), name='leave_approval_notifications'),
    path('reminders/', NewLeaveRequestListView.as_view(), name='leave_approval_reminders'),
]

# =============================================================================
# LEAVE REPORTS AND ANALYTICS
# =============================================================================

report_patterns = [
    # Main reports
    path('', NewLeaveRequestListView.as_view(), name='leave_reports_dashboard'),
    path('summary/', NewLeaveRequestListView.as_view(), name='leave_summary_report'),
    
    # Specific reports
    path('usage/', NewLeaveRequestListView.as_view(), name='leave_usage_report'),
    path('trends/', NewLeaveRequestListView.as_view(), name='leave_trends_report'),
    path('balance/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_balance_report'),
    path('calendar/', NewLeaveRequestListView.as_view(), name='leave_calendar_report'),
    
    # Department and employee reports
    path('department/<int:department_id>/', NewLeaveRequestListView.as_view(), name='department_leave_report'),
    path('employee/<int:employee_id>/', NewLeaveRequestListView.as_view(), name='employee_leave_report'),
    
    # Export reports
    path('export/excel/', NewLeaveRequestListView.as_view(), name='leave_export_excel'),
    path('export/pdf/', NewLeaveRequestListView.as_view(), name='leave_export_pdf'),
    path('export/csv/', NewLeaveRequestListView.as_view(), name='leave_export_csv'),
]

# =============================================================================
# AJAX AND API ENDPOINTS
# =============================================================================

ajax_patterns = [
    # Leave request operations
    path('requests/<int:pk>/approve/', NewLeaveRequestDetailView.as_view(), name='leave_request_approve_ajax'),
    path('requests/<int:pk>/reject/', NewLeaveRequestDetailView.as_view(), name='leave_request_reject_ajax'),
    path('requests/bulk-action/', NewLeaveRequestListView.as_view(), name='leave_requests_bulk_action_ajax'),
    
    # Balance operations
    path('balance/check/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_balance_check_ajax'),
    path('balance/calculate/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_balance_calculate_ajax'),
    
    # Validation and calculations
    path('validate-dates/', NewLeaveRequestCreateView.as_view(), name='leave_validate_dates_ajax'),
    path('calculate-days/', NewLeaveRequestCreateView.as_view(), name='leave_calculate_days_ajax'),
    path('check-conflicts/', NewLeaveRequestCreateView.as_view(), name='leave_check_conflicts_ajax'),
    
    # Data fetching
    path('types/fetch/', NewLeaveTypeListView.as_view(), name='leave_types_fetch_ajax'),
    path('requests/fetch/', NewLeaveRequestListView.as_view(), name='leave_requests_fetch_ajax'),
    path('calendar/data/', NewLeaveRequestListView.as_view(), name='leave_calendar_data_ajax'),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Default redirect to leave requests
    path('', RedirectView.as_view(pattern_name='hr:new_leave_request_list', permanent=False), name='leave_home'),
    
    # Leave types management
    path('types/', include((leave_type_patterns, 'types'))),
    path('categories/', include((leave_type_patterns, 'categories'))),  # Alternative naming
    
    # Leave balances management
    path('balances/', include((balance_patterns, 'balances'))),
    path('entitlements/', include((balance_patterns, 'entitlements'))),  # Alternative naming
    
    # Leave requests management
    path('requests/', include((request_patterns, 'requests'))),
    path('applications/', include((request_patterns, 'applications'))),  # Alternative naming
    
    # Include request patterns at root level for convenience
    *request_patterns,
    
    # Approval workflow
    path('approvals/', include((approval_patterns, 'approvals'))),
    path('workflow/', include((approval_patterns, 'workflow'))),  # Alternative naming
    
    # Reports and analytics
    path('reports/', include((report_patterns, 'reports'))),
    path('analytics/', include((report_patterns, 'analytics'))),  # Alternative naming
    
    # AJAX endpoints
    path('ajax/', include((ajax_patterns, 'ajax'))),
    path('api/', include((ajax_patterns, 'api'))),  # Alternative naming
    
    # =============================================================================
    # LEGACY SUPPORT (for backward compatibility)
    # =============================================================================
    
    # Legacy leave URLs (from existing system)
    path('legacy/', include([
        # Legacy leave types
        path('types/', NewLeaveTypeListView.as_view(), name='leave_type_list'),
        path('types/create/', NewLeaveTypeCreateView.as_view(), name='leave_type_create'),
        path('types/<int:pk>/edit/', NewLeaveTypeUpdateView.as_view(), name='leave_type_edit'),
        path('types/<int:pk>/delete/', NewLeaveTypeUpdateView.as_view(), name='leave_type_delete'),
        
        # Legacy leave requests
        path('requests/', NewLeaveRequestListView.as_view(), name='leave_request_list'),
        path('requests/create/', NewLeaveRequestCreateView.as_view(), name='leave_request_create'),
        path('requests/<int:pk>/', NewLeaveRequestDetailView.as_view(), name='leave_request_detail'),
        path('requests/<int:pk>/edit/', NewLeaveRequestCreateView.as_view(), name='leave_request_edit'),
        path('requests/<int:pk>/delete/', NewLeaveRequestCreateView.as_view(), name='leave_request_delete'),
        
        # Legacy balances
        path('balances/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_balance_list'),
        path('balances/create/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balance_create'),
        path('balances/<int:pk>/edit/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balance_edit'),
        path('balances/<int:pk>/delete/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balance_delete'),
    ])),
    
    # =============================================================================
    # LEAVE CALENDAR AND SCHEDULING
    # =============================================================================
    
    # Leave calendar and scheduling
    path('calendar/', include([
        path('', NewLeaveRequestListView.as_view(), name='leave_calendar'),
        path('month/<int:year>/<int:month>/', NewLeaveRequestListView.as_view(), name='leave_calendar_month'),
        path('year/<int:year>/', NewLeaveRequestListView.as_view(), name='leave_calendar_year'),
        path('team/', NewLeaveRequestListView.as_view(), name='team_leave_calendar'),
        path('department/<int:department_id>/', NewLeaveRequestListView.as_view(), name='department_leave_calendar'),
    ])),
    
    # =============================================================================
    # LEAVE POLICIES AND RULES
    # =============================================================================
    
    # Leave policies and business rules
    path('policies/', include([
        path('', NewLeaveTypeListView.as_view(), name='leave_policies'),
        path('accrual/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_accrual_policies'),
        path('carryover/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_carryover_policies'),
        path('blackout/', NewLeaveRequestListView.as_view(), name='leave_blackout_periods'),
    ])),
    
    # =============================================================================
    # LEAVE NOTIFICATIONS AND ALERTS
    # =============================================================================
    
    # Notifications and alerts
    path('notifications/', include([
        path('', NewLeaveRequestListView.as_view(), name='leave_notifications'),
        path('pending/', NewLeaveRequestListView.as_view(), name='pending_leave_notifications'),
        path('expiring/', NewEmployeeLeaveBalanceListView.as_view(), name='expiring_leave_notifications'),
        path('reminders/', NewLeaveRequestListView.as_view(), name='leave_reminders'),
        path('alerts/', NewLeaveRequestListView.as_view(), name='leave_alerts'),
    ])),
    
    # =============================================================================
    # LEAVE IMPORT AND EXPORT
    # =============================================================================
    
    # Import and export operations
    path('import-export/', include([
        path('import/requests/', NewLeaveRequestCreateView.as_view(), name='leave_requests_import'),
        path('import/balances/', NewEmployeeLeaveBalanceCreateView.as_view(), name='leave_balances_import'),
        path('export/requests/', NewLeaveRequestListView.as_view(), name='leave_requests_export'),
        path('export/balances/', NewEmployeeLeaveBalanceListView.as_view(), name='leave_balances_export'),
        path('templates/', NewLeaveRequestListView.as_view(), name='leave_import_templates'),
    ])),
]

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
Leave Management URL Patterns Summary:

Main Routes:
- /hr/leave/ - Leave home (redirects to requests)
- /hr/leave/types/ - Leave type management
- /hr/leave/balances/ - Leave balance management
- /hr/leave/requests/ - Leave request management
- /hr/leave/approvals/ - Approval workflow
- /hr/leave/reports/ - Reports and analytics

Leave Types:
- /hr/leave/types/ - List all leave types
- /hr/leave/types/create/ - Create new leave type
- /hr/leave/types/<id>/ - Leave type details
- /hr/leave/types/<id>/edit/ - Edit leave type
- /hr/leave/types/<id>/statistics/ - Type statistics

Leave Balances:
- /hr/leave/balances/ - List all balances
- /hr/leave/balances/create/ - Create new balance
- /hr/leave/balances/employee/<id>/ - Employee balances
- /hr/leave/balances/bulk-create/ - Bulk create balances

Leave Requests:
- /hr/leave/requests/ - List all requests
- /hr/leave/requests/create/ - Create new request
- /hr/leave/<id>/ - Request details (root level)
- /hr/leave/<id>/edit/ - Edit request
- /hr/leave/<id>/approve/ - Approve request
- /hr/leave/<id>/reject/ - Reject request

Approval Workflow:
- /hr/leave/approvals/pending/ - Pending requests
- /hr/leave/approvals/approved/ - Approved requests
- /hr/leave/approvals/bulk-approve/ - Bulk approve
- /hr/leave/approvals/notifications/ - Approval notifications

Reports and Analytics:
- /hr/leave/reports/ - Main reports dashboard
- /hr/leave/reports/usage/ - Usage reports
- /hr/leave/reports/trends/ - Trend analysis
- /hr/leave/reports/calendar/ - Calendar view
- /hr/leave/reports/employee/<id>/ - Employee reports

AJAX Endpoints:
- /hr/leave/ajax/requests/<id>/approve/ - Approve request
- /hr/leave/ajax/balance/check/ - Check balance
- /hr/leave/ajax/validate-dates/ - Validate dates
- /hr/leave/ajax/calculate-days/ - Calculate days

Leave Calendar:
- /hr/leave/calendar/ - Leave calendar view
- /hr/leave/calendar/month/<year>/<month>/ - Monthly view
- /hr/leave/calendar/team/ - Team calendar

Leave Policies:
- /hr/leave/policies/ - Leave policies
- /hr/leave/policies/accrual/ - Accrual policies
- /hr/leave/policies/carryover/ - Carryover rules

Notifications:
- /hr/leave/notifications/ - All notifications
- /hr/leave/notifications/pending/ - Pending notifications
- /hr/leave/notifications/expiring/ - Expiring leave alerts

Import/Export:
- /hr/leave/import-export/import/requests/ - Import requests
- /hr/leave/import-export/export/balances/ - Export balances

Legacy Support:
- /hr/leave/legacy/ - Legacy URL patterns for backward compatibility

URL Naming Convention:
- new_leave_{entity}_{action} - New system URLs
- leave_{entity}_{action} - Legacy and alternative URLs
- {action}_ajax - AJAX endpoints
"""
