from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Dashboard and Main Views
    path('', views.attendance_dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='main_dashboard'),
    
    # Attendance Records
    path('records/', views.AttendanceRecordListView.as_view(), name='record_list'),
    path('records/add/', views.add_record, name='add_record'),
    path('records/<int:record_id>/', views.record_detail, name='record_detail'),
    path('records/<int:record_id>/edit/', views.edit_record, name='edit_record'),
    path('records/<int:record_id>/delete/', views.delete_record, name='delete_record'),
    
    # Attendance Rules
    path('rules/', views.rules_list, name='rules_list'),
    path('rules/add/', views.add_rule, name='add_rule'),
    path('rules/<int:rule_id>/', views.get_rule, name='get_rule'),
    path('rules/<int:rule_id>/edit/', views.update_rule, name='update_rule'),
    path('rules/<int:rule_id>/delete/', views.delete_rule, name='delete_rule'),
    path('rules/<int:rule_id>/set-default/', views.set_default_rule, name='set_default_rule'),
    
    # Quick Attendance Actions
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('record-attendance/', views.record_attendance, name='record_attendance'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('mark/', views.mark_attendance, name='mark'),
    
    # Employee Profile and Personal Views
    path('profile/', views.profile, name='profile'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    
    # Reports and Analytics
    path('reports/', views.reports, name='reports'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    path('reports/employee/<int:emp_id>/', views.employee_attendance_report, name='employee_report'),
    path('export/', views.export_attendance, name='export_attendance'),
    path('analytics/', views.attendance_analytics, name='analytics'),
    
    # Time Tracking
    path('time-tracking/', views.time_tracking, name='time_tracking'),
    path('overtime/', views.overtime_records, name='overtime_records'),
    path('calculate-overtime/', views.calculate_overtime, name='calculate_overtime'),
    
    # Bulk Operations
    path('bulk/import/', views.bulk_import_attendance, name='bulk_import'),
    path('bulk/export/', views.bulk_export_attendance, name='bulk_export'),
    path('bulk/approve/', views.bulk_approve_attendance, name='bulk_approve'),
    
    # Attendance Summaries
    path('summaries/', views.attendance_summaries, name='attendance_summaries'),
    path('summaries/generate/', views.generate_attendance_summary, name='generate_summary'),
    
    # Leave Balances
    path('leave-balances/', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),
    
    # AJAX Views
    path('ajax/status/<int:emp_id>/', views.get_attendance_status, name='ajax_attendance_status'),
    path('ajax/work-hours/', views.calculate_work_hours, name='ajax_work_hours'),
    path('ajax/summary/<int:emp_id>/', views.attendance_summary, name='ajax_summary'),
    
    # ================================================================
    # ZK DEVICE MANAGEMENT
    # ================================================================
    
    # ZK Devices CRUD
    path('zk/devices/', views.zk_devices_list, name='zk_devices_list'),
    path('zk/devices/add/', views.zk_device_create, name='zk_device_create'),
    path('zk/devices/<int:device_id>/edit/', views.zk_device_edit, name='zk_device_edit'),
    path('zk/devices/<int:device_id>/delete/', views.zk_device_delete, name='zk_device_delete'),
    path('zk/devices/<int:device_id>/info/', views.zk_device_info, name='zk_device_info'),
    
    # ZK Device Operations
    path('zk/devices/<int:device_id>/test/', views.zk_device_test, name='zk_device_test'),
    path('zk/devices/<int:device_id>/sync/', views.zk_device_sync, name='zk_device_sync'),
    path('zk/sync-all/', views.zk_sync_all_devices, name='zk_sync_all'),
    
    # ZK Raw Data and Processing
    path('zk/raw-data/', views.zk_raw_data, name='zk_raw_data'),
    path('zk/processing-logs/', views.zk_processing_logs, name='zk_processing_logs'),
    
    # ZK Employee Mapping
    path('zk/mapping/', views.zk_employee_mapping, name='zk_employee_mapping'),
    path('zk/mapping/add/', views.zk_create_mapping, name='zk_create_mapping'),
    path('zk/mapping/<int:mapping_id>/edit/', views.zk_edit_mapping, name='zk_edit_mapping'),
    path('zk/mapping/<int:mapping_id>/delete/', views.zk_delete_mapping, name='zk_delete_mapping'),
    
    # ZK AJAX Operations
    path('zk/ajax/device-status/<int:device_id>/', views.ajax_zk_device_status, name='ajax_zk_device_status'),
    path('zk/ajax/process-record/<int:raw_id>/', views.ajax_process_raw_record, name='ajax_process_raw_record'),
    
    # ================================================================
    # LEGACY COMPATIBILITY (for existing system)
    # ================================================================
    
    # Original attendance rules (schema-specific)
    path('attendance-rules/', views.attendance_rules_list, name='attendance_rules_list'),
    path('attendance-rules/create/', views.attendance_rules_create, name='attendance_rules_create'),
    path('attendance-rules/<int:pk>/edit/', views.attendance_rules_edit, name='attendance_rules_edit'),
    path('attendance-rules/<int:pk>/delete/', views.attendance_rules_delete, name='attendance_rules_delete'),
    
    # Original employee attendance (schema-specific)
    path('employee-attendance/', views.employee_attendance_list, name='employee_attendance_list'),
    path('employee-attendance/create/', views.employee_attendance_create, name='employee_attendance_create'),
    path('employee-attendance/<int:pk>/edit/', views.employee_attendance_edit, name='employee_attendance_edit'),
    path('employee-attendance/<int:pk>/delete/', views.employee_attendance_delete, name='employee_attendance_delete'),
]
