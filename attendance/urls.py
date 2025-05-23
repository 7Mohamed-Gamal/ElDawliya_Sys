from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_dashboard, name='dashboard'),
    path('records/', views.AttendanceRecordListView.as_view(), name='record_list'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('leave-balances/', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),
]
