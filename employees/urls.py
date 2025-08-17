from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.employee_list, name='employee_list'),
]

