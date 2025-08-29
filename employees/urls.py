from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.employee_list, name='list'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('<int:emp_id>/', views.employee_detail, name='detail'),
    path('<int:emp_id>/edit/', views.edit_employee, name='edit'),
    path('<int:emp_id>/delete/', views.delete_employee, name='delete'),
]

