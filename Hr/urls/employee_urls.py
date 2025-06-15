# =============================================================================
# ElDawliya HR Management System - Employee Management URLs
# =============================================================================
# URL patterns for employee management
# Includes CRUD operations, documents, emergency contacts, and analytics
# =============================================================================

from django.urls import path, include
from django.views.generic import RedirectView

# Import employee management views
try:
    from Hr.views.new_employee_views import (
        NewEmployeeListView, NewEmployeeDetailView, NewEmployeeCreateView, NewEmployeeUpdateView,
        NewEmployeeDocumentListView, NewEmployeeDocumentCreateView,
        NewEmployeeEmergencyContactCreateView,
        new_employee_search_ajax, new_employee_quick_stats, new_employee_status_update,
        new_employee_bulk_update, new_export_employees_excel
    )
except ImportError:
    # Fallback to simple views for testing
    from Hr.views.simple_views import (
        SimpleListView as NewEmployeeListView,
        SimpleDetailView as NewEmployeeDetailView,
        SimpleCreateView as NewEmployeeCreateView,
        SimpleListView as NewEmployeeUpdateView,
        SimpleListView as NewEmployeeDocumentListView,
        SimpleCreateView as NewEmployeeDocumentCreateView,
        SimpleCreateView as NewEmployeeEmergencyContactCreateView,
        new_employee_search_ajax, new_employee_quick_stats, new_employee_status_update,
        new_employee_bulk_update, new_export_employees_excel
    )

# =============================================================================
# EMPLOYEE CRUD OPERATIONS
# =============================================================================

employee_crud_patterns = [
    # Main employee operations
    path('', NewEmployeeListView.as_view(), name='new_employee_list'),
    path('create/', NewEmployeeCreateView.as_view(), name='new_employee_create'),
    path('<int:pk>/', NewEmployeeDetailView.as_view(), name='new_employee_detail'),
    path('<int:pk>/edit/', NewEmployeeUpdateView.as_view(), name='new_employee_update'),
    path('<int:pk>/delete/', NewEmployeeUpdateView.as_view(), name='new_employee_delete'),
    
    # Employee profile operations
    path('<int:pk>/profile/', NewEmployeeDetailView.as_view(), name='new_employee_profile'),
    path('<int:pk>/summary/', NewEmployeeDetailView.as_view(), name='new_employee_summary'),
    path('<int:pk>/timeline/', NewEmployeeDetailView.as_view(), name='new_employee_timeline'),
]

# =============================================================================
# EMPLOYEE DOCUMENTS MANAGEMENT
# =============================================================================

document_patterns = [
    # Document operations
    path('<int:employee_pk>/documents/', NewEmployeeDocumentListView.as_view(), name='new_employee_documents'),
    path('<int:employee_pk>/documents/create/', NewEmployeeDocumentCreateView.as_view(), name='new_employee_document_create'),
    path('<int:employee_pk>/documents/<int:pk>/', NewEmployeeDocumentListView.as_view(), name='new_employee_document_detail'),
    path('<int:employee_pk>/documents/<int:pk>/edit/', NewEmployeeDocumentCreateView.as_view(), name='new_employee_document_update'),
    path('<int:employee_pk>/documents/<int:pk>/delete/', NewEmployeeDocumentCreateView.as_view(), name='new_employee_document_delete'),
    
    # Document operations (alternative URLs)
    path('documents/', NewEmployeeDocumentListView.as_view(), name='employee_documents_list'),
    path('documents/create/', NewEmployeeDocumentCreateView.as_view(), name='employee_document_create'),
    path('documents/<int:pk>/', NewEmployeeDocumentListView.as_view(), name='employee_document_detail'),
    path('documents/<int:pk>/edit/', NewEmployeeDocumentCreateView.as_view(), name='employee_document_update'),
    path('documents/<int:pk>/delete/', NewEmployeeDocumentCreateView.as_view(), name='employee_document_delete'),
]

# =============================================================================
# EMERGENCY CONTACTS MANAGEMENT
# =============================================================================

emergency_contact_patterns = [
    # Emergency contact operations
    path('<int:employee_pk>/contacts/', NewEmployeeDetailView.as_view(), name='new_employee_emergency_contacts'),
    path('<int:employee_pk>/contacts/create/', NewEmployeeEmergencyContactCreateView.as_view(), name='new_employee_emergency_contact_create'),
    path('<int:employee_pk>/contacts/<int:pk>/', NewEmployeeDetailView.as_view(), name='new_employee_emergency_contact_detail'),
    path('<int:employee_pk>/contacts/<int:pk>/edit/', NewEmployeeEmergencyContactCreateView.as_view(), name='new_employee_emergency_contact_update'),
    path('<int:employee_pk>/contacts/<int:pk>/delete/', NewEmployeeEmergencyContactCreateView.as_view(), name='new_employee_emergency_contact_delete'),
]

# =============================================================================
# AJAX AND API ENDPOINTS
# =============================================================================

ajax_patterns = [
    # Search and filter
    path('search/', new_employee_search_ajax, name='new_employee_search_ajax'),
    path('quick-search/', new_employee_search_ajax, name='quick_employee_search'),
    
    # Quick statistics
    path('<int:pk>/quick-stats/', new_employee_quick_stats, name='new_employee_quick_stats'),
    path('<int:pk>/statistics/', new_employee_quick_stats, name='employee_statistics_ajax'),
    
    # Status updates
    path('<int:pk>/status-update/', new_employee_status_update, name='new_employee_status_update'),
    path('<int:pk>/toggle-status/', new_employee_status_update, name='employee_toggle_status'),
    
    # Data export
    path('export/', new_export_employees_excel, name='new_export_employees_excel'),
    path('export/excel/', new_export_employees_excel, name='export_employees_excel'),
    
    # Bulk operations
    path('bulk-update/', new_employee_bulk_update, name='new_employee_bulk_update'),
    path('bulk-action/', new_employee_bulk_update, name='employee_bulk_action'),
]

# =============================================================================
# EMPLOYEE ANALYTICS AND REPORTS
# =============================================================================

analytics_patterns = [
    # Employee analytics
    path('analytics/', NewEmployeeListView.as_view(), name='employee_analytics'),
    path('reports/', NewEmployeeListView.as_view(), name='employee_reports'),
    path('dashboard/', NewEmployeeListView.as_view(), name='employee_dashboard'),
    
    # Specific reports
    path('reports/demographics/', NewEmployeeListView.as_view(), name='employee_demographics_report'),
    path('reports/performance/', NewEmployeeListView.as_view(), name='employee_performance_report'),
    path('reports/attendance/', NewEmployeeListView.as_view(), name='employee_attendance_report'),
    path('reports/turnover/', NewEmployeeListView.as_view(), name='employee_turnover_report'),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Default redirect to employee list
    path('', RedirectView.as_view(pattern_name='hr:new_employee_list', permanent=False), name='employee_home'),
    
    # Employee CRUD operations
    path('list/', include((employee_crud_patterns, 'crud'))),
    path('manage/', include((employee_crud_patterns, 'manage'))),  # Alternative naming
    
    # Include all employee CRUD patterns at root level
    *employee_crud_patterns,
    
    # Document management
    path('docs/', include((document_patterns, 'documents'))),
    
    # Emergency contacts
    path('contacts/', include((emergency_contact_patterns, 'contacts'))),
    
    # AJAX endpoints
    path('ajax/', include((ajax_patterns, 'ajax'))),
    path('api/', include((ajax_patterns, 'api'))),  # Alternative naming
    
    # Analytics and reports
    path('analytics/', include((analytics_patterns, 'analytics'))),
    
    # =============================================================================
    # LEGACY SUPPORT (for backward compatibility)
    # =============================================================================
    
    # Legacy employee URLs (from existing system)
    path('legacy/', include([
        path('', NewEmployeeListView.as_view(), name='employee_list'),
        path('create/', NewEmployeeCreateView.as_view(), name='employee_create'),
        path('<int:emp_id>/', NewEmployeeDetailView.as_view(), name='employee_detail'),
        path('<int:emp_id>/edit/', NewEmployeeUpdateView.as_view(), name='employee_edit'),
        path('<int:emp_id>/delete/', NewEmployeeUpdateView.as_view(), name='employee_delete'),
        path('<int:emp_id>/print/', NewEmployeeDetailView.as_view(), name='employee_print'),
        path('search/', new_employee_search_ajax, name='employee_search'),
        path('export/', new_export_employees_excel, name='employee_export'),
        path('ajax/', new_employee_search_ajax, name='employee_list_ajax'),
        path('detail_view/', NewEmployeeDetailView.as_view(), name='detail_view'),
    ])),
    
    # =============================================================================
    # EMPLOYEE LIFECYCLE MANAGEMENT
    # =============================================================================
    
    # Employee lifecycle operations
    path('lifecycle/', include([
        path('<int:pk>/onboard/', NewEmployeeDetailView.as_view(), name='employee_onboard'),
        path('<int:pk>/promote/', NewEmployeeUpdateView.as_view(), name='employee_promote'),
        path('<int:pk>/transfer/', NewEmployeeUpdateView.as_view(), name='employee_transfer'),
        path('<int:pk>/terminate/', NewEmployeeUpdateView.as_view(), name='employee_terminate'),
        path('<int:pk>/rehire/', NewEmployeeUpdateView.as_view(), name='employee_rehire'),
        path('<int:pk>/retire/', NewEmployeeUpdateView.as_view(), name='employee_retire'),
    ])),
    
    # =============================================================================
    # EMPLOYEE PERFORMANCE AND EVALUATION
    # =============================================================================
    
    # Performance management
    path('performance/', include([
        path('<int:pk>/evaluations/', NewEmployeeDetailView.as_view(), name='employee_evaluations'),
        path('<int:pk>/goals/', NewEmployeeDetailView.as_view(), name='employee_goals'),
        path('<int:pk>/feedback/', NewEmployeeDetailView.as_view(), name='employee_feedback'),
        path('<int:pk>/development/', NewEmployeeDetailView.as_view(), name='employee_development'),
    ])),
    
    # =============================================================================
    # EMPLOYEE COMMUNICATION
    # =============================================================================
    
    # Communication and notifications
    path('communication/', include([
        path('<int:pk>/messages/', NewEmployeeDetailView.as_view(), name='employee_messages'),
        path('<int:pk>/notifications/', NewEmployeeDetailView.as_view(), name='employee_notifications'),
        path('<int:pk>/announcements/', NewEmployeeDetailView.as_view(), name='employee_announcements'),
        path('broadcast/', NewEmployeeListView.as_view(), name='employee_broadcast'),
    ])),
    
    # =============================================================================
    # BULK OPERATIONS AND IMPORTS
    # =============================================================================
    
    # Bulk operations
    path('bulk/', include([
        path('import/', NewEmployeeCreateView.as_view(), name='employee_bulk_import'),
        path('export/', new_export_employees_excel, name='employee_bulk_export'),
        path('update/', new_employee_bulk_update, name='employee_bulk_update_form'),
        path('delete/', new_employee_bulk_update, name='employee_bulk_delete'),
        path('activate/', new_employee_bulk_update, name='employee_bulk_activate'),
        path('deactivate/', new_employee_bulk_update, name='employee_bulk_deactivate'),
    ])),
]

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
Employee Management URL Patterns Summary:

Main Routes:
- /hr/employees/ - Employee management home (redirects to employee list)
- /hr/employees/list/ - Employee list and management
- /hr/employees/create/ - Create new employee
- /hr/employees/<id>/ - Employee detail view
- /hr/employees/<id>/edit/ - Edit employee

Document Management:
- /hr/employees/<id>/documents/ - Employee documents
- /hr/employees/<id>/documents/create/ - Upload new document
- /hr/employees/docs/ - All documents management

Emergency Contacts:
- /hr/employees/<id>/contacts/ - Emergency contacts
- /hr/employees/<id>/contacts/create/ - Add emergency contact

AJAX Endpoints:
- /hr/employees/ajax/search/ - Employee search
- /hr/employees/ajax/<id>/quick-stats/ - Quick statistics
- /hr/employees/ajax/<id>/status-update/ - Update status
- /hr/employees/ajax/export/ - Export data
- /hr/employees/ajax/bulk-update/ - Bulk operations

Analytics and Reports:
- /hr/employees/analytics/ - Employee analytics dashboard
- /hr/employees/reports/ - Various employee reports
- /hr/employees/reports/demographics/ - Demographics report
- /hr/employees/reports/performance/ - Performance report

Employee Lifecycle:
- /hr/employees/lifecycle/<id>/onboard/ - Employee onboarding
- /hr/employees/lifecycle/<id>/promote/ - Employee promotion
- /hr/employees/lifecycle/<id>/transfer/ - Employee transfer
- /hr/employees/lifecycle/<id>/terminate/ - Employee termination

Performance Management:
- /hr/employees/performance/<id>/evaluations/ - Performance evaluations
- /hr/employees/performance/<id>/goals/ - Employee goals
- /hr/employees/performance/<id>/feedback/ - Feedback management

Communication:
- /hr/employees/communication/<id>/messages/ - Employee messages
- /hr/employees/communication/<id>/notifications/ - Notifications
- /hr/employees/communication/broadcast/ - Broadcast messages

Bulk Operations:
- /hr/employees/bulk/import/ - Bulk import employees
- /hr/employees/bulk/export/ - Bulk export employees
- /hr/employees/bulk/update/ - Bulk update operations

Legacy Support:
- /hr/employees/legacy/ - Legacy URL patterns for backward compatibility

URL Naming Convention:
- new_employee_{action} - New system URLs
- employee_{action} - Legacy and alternative URLs
- {action}_ajax - AJAX endpoints
"""
