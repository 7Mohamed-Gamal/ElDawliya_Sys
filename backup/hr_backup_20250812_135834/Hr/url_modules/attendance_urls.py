"""
URLs خاصة بالحضور
"""

from django.urls import path
from ..views.attendance_views import (
    attendance_rule_list, attendance_rule_create, attendance_rule_edit, attendance_rule_delete,
    employee_attendance_rule_list, employee_attendance_rule_create, employee_attendance_rule_edit,
    employee_attendance_rule_delete, employee_attendance_rule_bulk_create,
    official_holiday_list, official_holiday_create, official_holiday_edit, official_holiday_delete,
    attendance_machine_list, attendance_machine_create, attendance_machine_edit, attendance_machine_delete,
    attendance_record_list, attendance_record_create, attendance_record_edit, attendance_record_delete,
    fetch_attendance_data, attendance_summary_list, zk_device_connection,
    test_zk_connection, fetch_zk_records_ajax, save_zk_records_to_db
)

app_name = 'attendance'

urlpatterns = [
    # Attendance rules
    path('rules/', attendance_rule_list, name='attendance_rule_list'),
    path('rules/create/', attendance_rule_create, name='attendance_rule_create'),
    path('rules/<int:rule_id>/edit/', attendance_rule_edit, name='attendance_rule_edit'),
    path('rules/<int:rule_id>/delete/', attendance_rule_delete, name='attendance_rule_delete'),
    
    # Employee attendance rules
    path('employee-rules/', employee_attendance_rule_list, name='employee_attendance_rule_list'),
    path('employee-rules/create/', employee_attendance_rule_create, name='employee_attendance_rule_create'),
    path('employee-rules/<int:rule_id>/edit/', employee_attendance_rule_edit, name='employee_attendance_rule_edit'),
    path('employee-rules/<int:rule_id>/delete/', employee_attendance_rule_delete, name='employee_attendance_rule_delete'),
    path('employee-rules/bulk-create/', employee_attendance_rule_bulk_create, name='employee_attendance_rule_bulk_create'),
    
    # Official holidays
    path('holidays/', official_holiday_list, name='official_holiday_list'),
    path('holidays/create/', official_holiday_create, name='official_holiday_create'),
    path('holidays/<int:holiday_id>/edit/', official_holiday_edit, name='official_holiday_edit'),
    path('holidays/<int:holiday_id>/delete/', official_holiday_delete, name='official_holiday_delete'),
    
    # Attendance machines
    path('machines/', attendance_machine_list, name='attendance_machine_list'),
    path('machines/create/', attendance_machine_create, name='attendance_machine_create'),
    path('machines/<int:machine_id>/edit/', attendance_machine_edit, name='attendance_machine_edit'),
    path('machines/<int:machine_id>/delete/', attendance_machine_delete, name='attendance_machine_delete'),
    
    # Attendance records
    path('records/', attendance_record_list, name='attendance_record_list'),
    path('records/create/', attendance_record_create, name='attendance_record_create'),
    path('records/<int:record_id>/edit/', attendance_record_edit, name='attendance_record_edit'),
    path('records/<int:record_id>/delete/', attendance_record_delete, name='attendance_record_delete'),
    
    # Attendance summary and data
    path('summary/', attendance_summary_list, name='attendance_summary_list'),
    path('zk-device/', zk_device_connection, name='zk_device_connection'),
    path('fetch-data/', fetch_attendance_data, name='fetch_attendance_data'),
    
    # AJAX endpoints
    path('ajax/test-zk-connection/', test_zk_connection, name='test_zk_connection'),
    path('ajax/fetch-zk-records/', fetch_zk_records_ajax, name='fetch_zk_records_ajax'),
    path('ajax/save-zk-records/', save_zk_records_to_db, name='save_zk_records_to_db'),
]