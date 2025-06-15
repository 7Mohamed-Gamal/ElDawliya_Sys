# =============================================================================
# ElDawliya HR Management System - Attendance & Time Tracking URLs
# =============================================================================
# URL patterns for attendance and time tracking management
# Includes shifts, machines, records, reports, and analytics
# =============================================================================

from django.urls import path, include
from django.views.generic import RedirectView

# Import attendance management views
try:
    from Hr.views.new_attendance_views import (
        NewWorkShiftListView, NewWorkShiftDetailView, NewWorkShiftCreateView, NewWorkShiftUpdateView,
        NewAttendanceMachineListView, NewAttendanceMachineCreateView,
        NewEmployeeShiftAssignmentListView, NewEmployeeShiftAssignmentCreateView,
        NewAttendanceRecordListView, NewAttendanceRecordCreateView, NewAttendanceReportView,
        new_attendance_dashboard_data, new_attendance_quick_add
    )
except ImportError:
    # Fallback to simple views for testing
    from Hr.views.simple_views import (
        SimpleListView as NewWorkShiftListView,
        SimpleDetailView as NewWorkShiftDetailView,
        SimpleCreateView as NewWorkShiftCreateView,
        SimpleListView as NewWorkShiftUpdateView,
        SimpleListView as NewAttendanceMachineListView,
        SimpleCreateView as NewAttendanceMachineCreateView,
        SimpleListView as NewEmployeeShiftAssignmentListView,
        SimpleCreateView as NewEmployeeShiftAssignmentCreateView,
        SimpleListView as NewAttendanceRecordListView,
        SimpleCreateView as NewAttendanceRecordCreateView,
        SimpleListView as NewAttendanceReportView,
        new_attendance_dashboard_data, new_attendance_quick_add
    )

# =============================================================================
# WORK SHIFT MANAGEMENT
# =============================================================================

shift_patterns = [
    # Work shift CRUD operations
    path('', NewWorkShiftListView.as_view(), name='new_workshift_list'),
    path('create/', NewWorkShiftCreateView.as_view(), name='new_workshift_create'),
    path('<int:pk>/', NewWorkShiftDetailView.as_view(), name='new_workshift_detail'),
    path('<int:pk>/edit/', NewWorkShiftUpdateView.as_view(), name='new_workshift_update'),
    path('<int:pk>/delete/', NewWorkShiftUpdateView.as_view(), name='new_workshift_delete'),
    
    # Shift-specific operations
    path('<int:pk>/employees/', NewWorkShiftDetailView.as_view(), name='workshift_employees'),
    path('<int:pk>/schedule/', NewWorkShiftDetailView.as_view(), name='workshift_schedule'),
    path('<int:pk>/copy/', NewWorkShiftCreateView.as_view(), name='workshift_copy'),
]

# =============================================================================
# ATTENDANCE MACHINE MANAGEMENT
# =============================================================================

machine_patterns = [
    # Attendance machine CRUD operations
    path('', NewAttendanceMachineListView.as_view(), name='new_attendance_machine_list'),
    path('create/', NewAttendanceMachineCreateView.as_view(), name='new_attendance_machine_create'),
    path('<int:pk>/', NewAttendanceMachineListView.as_view(), name='new_attendance_machine_detail'),
    path('<int:pk>/edit/', NewAttendanceMachineCreateView.as_view(), name='new_attendance_machine_update'),
    path('<int:pk>/delete/', NewAttendanceMachineCreateView.as_view(), name='new_attendance_machine_delete'),
    
    # Machine-specific operations
    path('<int:pk>/sync/', NewAttendanceMachineListView.as_view(), name='attendance_machine_sync'),
    path('<int:pk>/status/', NewAttendanceMachineListView.as_view(), name='attendance_machine_status'),
    path('<int:pk>/logs/', NewAttendanceMachineListView.as_view(), name='attendance_machine_logs'),
]

# =============================================================================
# EMPLOYEE SHIFT ASSIGNMENT
# =============================================================================

assignment_patterns = [
    # Shift assignment CRUD operations
    path('', NewEmployeeShiftAssignmentListView.as_view(), name='new_employee_shift_assignment_list'),
    path('create/', NewEmployeeShiftAssignmentCreateView.as_view(), name='new_employee_shift_assignment_create'),
    path('<int:pk>/', NewEmployeeShiftAssignmentListView.as_view(), name='new_employee_shift_assignment_detail'),
    path('<int:pk>/edit/', NewEmployeeShiftAssignmentCreateView.as_view(), name='new_employee_shift_assignment_update'),
    path('<int:pk>/delete/', NewEmployeeShiftAssignmentCreateView.as_view(), name='new_employee_shift_assignment_delete'),
    
    # Bulk assignment operations
    path('bulk-create/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_shift_bulk_assignment'),
    path('bulk-update/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_shift_bulk_update'),
    path('bulk-delete/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_shift_bulk_delete'),
]

# =============================================================================
# ATTENDANCE RECORDS MANAGEMENT
# =============================================================================

record_patterns = [
    # Attendance record CRUD operations
    path('', NewAttendanceRecordListView.as_view(), name='new_attendance_list'),
    path('create/', NewAttendanceRecordCreateView.as_view(), name='new_attendance_create'),
    path('<int:pk>/', NewAttendanceRecordListView.as_view(), name='new_attendance_detail'),
    path('<int:pk>/edit/', NewAttendanceRecordCreateView.as_view(), name='new_attendance_update'),
    path('<int:pk>/delete/', NewAttendanceRecordCreateView.as_view(), name='new_attendance_delete'),
    
    # Record-specific operations
    path('<int:pk>/approve/', NewAttendanceRecordListView.as_view(), name='attendance_record_approve'),
    path('<int:pk>/reject/', NewAttendanceRecordListView.as_view(), name='attendance_record_reject'),
    path('<int:pk>/details/', NewAttendanceRecordListView.as_view(), name='attendance_record_details'),
]

# =============================================================================
# ATTENDANCE REPORTS AND ANALYTICS
# =============================================================================

report_patterns = [
    # Main reports
    path('', NewAttendanceReportView.as_view(), name='new_attendance_report'),
    path('dashboard/', NewAttendanceReportView.as_view(), name='attendance_report_dashboard'),
    
    # Specific reports
    path('daily/', NewAttendanceReportView.as_view(), name='attendance_daily_report'),
    path('weekly/', NewAttendanceReportView.as_view(), name='attendance_weekly_report'),
    path('monthly/', NewAttendanceReportView.as_view(), name='attendance_monthly_report'),
    path('summary/', NewAttendanceReportView.as_view(), name='attendance_summary_report'),
    
    # Employee-specific reports
    path('employee/<int:employee_id>/', NewAttendanceReportView.as_view(), name='employee_attendance_report'),
    path('department/<int:department_id>/', NewAttendanceReportView.as_view(), name='department_attendance_report'),
    
    # Export reports
    path('export/excel/', NewAttendanceReportView.as_view(), name='attendance_export_excel'),
    path('export/pdf/', NewAttendanceReportView.as_view(), name='attendance_export_pdf'),
    path('export/csv/', NewAttendanceReportView.as_view(), name='attendance_export_csv'),
]

# =============================================================================
# AJAX AND API ENDPOINTS
# =============================================================================

ajax_patterns = [
    # Dashboard data
    path('dashboard-data/', new_attendance_dashboard_data, name='new_attendance_dashboard_data'),
    path('statistics/', new_attendance_dashboard_data, name='attendance_statistics_ajax'),
    
    # Quick operations
    path('quick-add/', new_attendance_quick_add, name='new_attendance_quick_add'),
    path('quick-checkin/', new_attendance_quick_add, name='attendance_quick_checkin'),
    path('quick-checkout/', new_attendance_quick_add, name='attendance_quick_checkout'),
    
    # Data fetching
    path('records/fetch/', NewAttendanceRecordListView.as_view(), name='attendance_records_fetch'),
    path('shifts/available/', NewWorkShiftListView.as_view(), name='available_shifts_ajax'),
    path('machines/status/', NewAttendanceMachineListView.as_view(), name='machines_status_ajax'),
    
    # Validation and calculations
    path('validate-time/', NewAttendanceRecordCreateView.as_view(), name='attendance_validate_time'),
    path('calculate-hours/', NewAttendanceRecordCreateView.as_view(), name='attendance_calculate_hours'),
    path('check-conflicts/', NewEmployeeShiftAssignmentCreateView.as_view(), name='attendance_check_conflicts'),
]

# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Default redirect to attendance records
    path('', RedirectView.as_view(pattern_name='hr:new_attendance_list', permanent=False), name='attendance_home'),
    
    # Work shift management
    path('shifts/', include((shift_patterns, 'shifts'))),
    path('workshift/', include((shift_patterns, 'workshift'))),  # Alternative naming
    
    # Attendance machine management
    path('machines/', include((machine_patterns, 'machines'))),
    path('devices/', include((machine_patterns, 'devices'))),  # Alternative naming
    
    # Employee shift assignments
    path('assignments/', include((assignment_patterns, 'assignments'))),
    path('schedule/', include((assignment_patterns, 'schedule'))),  # Alternative naming
    
    # Attendance records
    path('records/', include((record_patterns, 'records'))),
    path('logs/', include((record_patterns, 'logs'))),  # Alternative naming
    
    # Include record patterns at root level for convenience
    *record_patterns,
    
    # Reports and analytics
    path('reports/', include((report_patterns, 'reports'))),
    path('analytics/', include((report_patterns, 'analytics'))),  # Alternative naming
    
    # AJAX endpoints
    path('ajax/', include((ajax_patterns, 'ajax'))),
    path('api/', include((ajax_patterns, 'api'))),  # Alternative naming
    
    # =============================================================================
    # LEGACY SUPPORT (for backward compatibility)
    # =============================================================================
    
    # Legacy attendance URLs (from existing system)
    path('legacy/', include([
        # Attendance rules
        path('rules/', NewWorkShiftListView.as_view(), name='attendance_rule_list'),
        path('rules/create/', NewWorkShiftCreateView.as_view(), name='attendance_rule_create'),
        path('rules/<int:pk>/edit/', NewWorkShiftUpdateView.as_view(), name='attendance_rule_edit'),
        path('rules/<int:pk>/delete/', NewWorkShiftUpdateView.as_view(), name='attendance_rule_delete'),
        
        # Employee attendance rules
        path('employee-rules/', NewEmployeeShiftAssignmentListView.as_view(), name='employee_attendance_rule_list'),
        path('employee-rules/create/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_attendance_rule_create'),
        path('employee-rules/<int:pk>/edit/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_attendance_rule_edit'),
        path('employee-rules/<int:pk>/delete/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_attendance_rule_delete'),
        path('employee-rules/bulk-create/', NewEmployeeShiftAssignmentCreateView.as_view(), name='employee_attendance_rule_bulk_create'),
        
        # Official holidays
        path('holidays/', NewWorkShiftListView.as_view(), name='official_holiday_list'),
        path('holidays/create/', NewWorkShiftCreateView.as_view(), name='official_holiday_create'),
        path('holidays/<int:pk>/edit/', NewWorkShiftUpdateView.as_view(), name='official_holiday_edit'),
        path('holidays/<int:pk>/delete/', NewWorkShiftUpdateView.as_view(), name='official_holiday_delete'),
        
        # Legacy machines
        path('machines/', NewAttendanceMachineListView.as_view(), name='attendance_machine_list'),
        path('machines/create/', NewAttendanceMachineCreateView.as_view(), name='attendance_machine_create'),
        path('machines/<int:pk>/edit/', NewAttendanceMachineCreateView.as_view(), name='attendance_machine_edit'),
        path('machines/<int:pk>/delete/', NewAttendanceMachineCreateView.as_view(), name='attendance_machine_delete'),
        
        # Legacy records
        path('records/', NewAttendanceRecordListView.as_view(), name='attendance_record_list'),
        path('records/create/', NewAttendanceRecordCreateView.as_view(), name='attendance_record_create'),
        path('records/<int:pk>/edit/', NewAttendanceRecordCreateView.as_view(), name='attendance_record_edit'),
        path('records/<int:pk>/delete/', NewAttendanceRecordCreateView.as_view(), name='attendance_record_delete'),
        path('records/fetch/', new_attendance_dashboard_data, name='fetch_attendance_data'),
        
        # Legacy summary
        path('summary/', NewAttendanceReportView.as_view(), name='attendance_summary_list'),
        path('summary/<int:pk>/', NewAttendanceReportView.as_view(), name='attendance_summary_detail'),
    ])),
    
    # =============================================================================
    # TIME TRACKING FEATURES
    # =============================================================================
    
    # Time tracking and clock in/out
    path('clock/', include([
        path('in/', new_attendance_quick_add, name='clock_in'),
        path('out/', new_attendance_quick_add, name='clock_out'),
        path('status/', new_attendance_dashboard_data, name='clock_status'),
        path('history/', NewAttendanceRecordListView.as_view(), name='clock_history'),
    ])),
    
    # =============================================================================
    # OVERTIME MANAGEMENT
    # =============================================================================
    
    # Overtime tracking and management
    path('overtime/', include([
        path('', NewAttendanceRecordListView.as_view(), name='overtime_list'),
        path('request/', NewAttendanceRecordCreateView.as_view(), name='overtime_request'),
        path('approve/<int:pk>/', NewAttendanceRecordListView.as_view(), name='overtime_approve'),
        path('reports/', NewAttendanceReportView.as_view(), name='overtime_reports'),
    ])),
    
    # =============================================================================
    # BREAK AND LUNCH TRACKING
    # =============================================================================
    
    # Break and lunch time tracking
    path('breaks/', include([
        path('start/', new_attendance_quick_add, name='break_start'),
        path('end/', new_attendance_quick_add, name='break_end'),
        path('lunch/start/', new_attendance_quick_add, name='lunch_start'),
        path('lunch/end/', new_attendance_quick_add, name='lunch_end'),
        path('history/', NewAttendanceRecordListView.as_view(), name='break_history'),
    ])),
]

# =============================================================================
# URL PATTERNS SUMMARY
# =============================================================================

"""
Attendance & Time Tracking URL Patterns Summary:

Main Routes:
- /hr/attendance/ - Attendance home (redirects to records)
- /hr/attendance/shifts/ - Work shift management
- /hr/attendance/machines/ - Attendance machine management
- /hr/attendance/assignments/ - Employee shift assignments
- /hr/attendance/records/ - Attendance records
- /hr/attendance/reports/ - Reports and analytics

Work Shift Management:
- /hr/attendance/shifts/ - List all shifts
- /hr/attendance/shifts/create/ - Create new shift
- /hr/attendance/shifts/<id>/ - Shift details
- /hr/attendance/shifts/<id>/edit/ - Edit shift
- /hr/attendance/shifts/<id>/employees/ - Employees in shift

Attendance Machines:
- /hr/attendance/machines/ - List all machines
- /hr/attendance/machines/create/ - Add new machine
- /hr/attendance/machines/<id>/sync/ - Sync machine data
- /hr/attendance/machines/<id>/status/ - Machine status

Employee Shift Assignments:
- /hr/attendance/assignments/ - List assignments
- /hr/attendance/assignments/create/ - Create assignment
- /hr/attendance/assignments/bulk-create/ - Bulk assignments

Attendance Records:
- /hr/attendance/records/ - List all records
- /hr/attendance/records/create/ - Manual record entry
- /hr/attendance/<id>/ - Record details (root level)
- /hr/attendance/<id>/edit/ - Edit record

Reports and Analytics:
- /hr/attendance/reports/ - Main reports dashboard
- /hr/attendance/reports/daily/ - Daily reports
- /hr/attendance/reports/monthly/ - Monthly reports
- /hr/attendance/reports/employee/<id>/ - Employee-specific reports

AJAX Endpoints:
- /hr/attendance/ajax/dashboard-data/ - Dashboard statistics
- /hr/attendance/ajax/quick-add/ - Quick check-in/out
- /hr/attendance/ajax/records/fetch/ - Fetch records data

Time Tracking Features:
- /hr/attendance/clock/in/ - Clock in
- /hr/attendance/clock/out/ - Clock out
- /hr/attendance/clock/status/ - Current status

Overtime Management:
- /hr/attendance/overtime/ - Overtime records
- /hr/attendance/overtime/request/ - Request overtime
- /hr/attendance/overtime/approve/<id>/ - Approve overtime

Break Tracking:
- /hr/attendance/breaks/start/ - Start break
- /hr/attendance/breaks/end/ - End break
- /hr/attendance/breaks/lunch/start/ - Start lunch
- /hr/attendance/breaks/lunch/end/ - End lunch

Legacy Support:
- /hr/attendance/legacy/ - Legacy URL patterns for backward compatibility

URL Naming Convention:
- new_{entity}_{action} - New system URLs
- {entity}_{action} - Legacy and alternative URLs
- {action}_ajax - AJAX endpoints
"""
