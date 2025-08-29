from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee URLs
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.employee_list, name='list'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('<int:emp_id>/', views.employee_detail, name='detail'),
    path('<int:emp_id>/edit/', views.edit_employee, name='edit'),
    path('<int:emp_id>/delete/', views.delete_employee, name='delete'),

    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:dept_id>/', views.department_detail, name='department_detail'),
    path('departments/<int:dept_id>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:dept_id>/delete/', views.delete_department, name='delete_department'),
    path('departments/summary/', views.department_summary, name='department_summary'),

    # Job URLs
    path('jobs/', views.job_list, name='job_list'),

    # AJAX URLs
    path('api/departments-by-branch/', views.get_departments_by_branch, name='departments_by_branch'),
    path('api/employees-by-department/', views.get_employees_by_department, name='employees_by_department'),
    path('api/departments/<int:dept_id>/employees/', views.department_employees_ajax, name='department_employees_ajax'),
]

