from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_dashboard, name='dashboard'),
    path('records/', views.AttendanceRecordListView.as_view(), name='record_list'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('leave-balances/', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),

    # Rules
    path('rules/', views.attendance_rules_list, name='rules_list'),
    path('rules/create/', views.attendance_rules_create, name='rules_create'),
    path('rules/<int:pk>/edit/', views.attendance_rules_edit, name='rules_edit'),
    path('rules/<int:pk>/delete/', views.attendance_rules_delete, name='rules_delete'),

    # Employee Attendance
    path('emp-att/', views.employee_attendance_list, name='emp_att_list'),
    path('emp-att/create/', views.employee_attendance_create, name='emp_att_create'),
    path('emp-att/<int:pk>/edit/', views.employee_attendance_edit, name='emp_att_edit'),
    path('emp-att/<int:pk>/delete/', views.employee_attendance_delete, name='emp_att_delete'),
]
