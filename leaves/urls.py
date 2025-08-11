from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    path('', views.leave_type_list, name='leave_types'),
    path('types/create/', views.leave_type_create, name='leave_type_create'),
    path('types/<int:pk>/edit/', views.leave_type_edit, name='leave_type_edit'),
    path('types/<int:pk>/delete/', views.leave_type_delete, name='leave_type_delete'),

    path('employee/', views.employee_leave_list, name='employee_leaves'),
    path('employee/create/', views.employee_leave_create, name='employee_leave_create'),
    path('employee/<int:pk>/edit/', views.employee_leave_edit, name='employee_leave_edit'),
    path('employee/<int:pk>/delete/', views.employee_leave_delete, name='employee_leave_delete'),

    path('holidays/', views.public_holiday_list, name='holidays'),
    path('holidays/create/', views.public_holiday_create, name='holiday_create'),
    path('holidays/<int:pk>/edit/', views.public_holiday_edit, name='holiday_edit'),
    path('holidays/<int:pk>/delete/', views.public_holiday_delete, name='holiday_delete'),
]

