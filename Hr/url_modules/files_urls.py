"""
URLs لملفات الموظفين
"""
from django.urls import path
from ..views.file_views import (
    employee_file_list,
    employee_file_create,
    employee_file_detail,
    employee_file_edit,
    employee_file_delete,
    employee_file_download,
)

app_name = 'files'

urlpatterns = [
    path('', employee_file_list, name='list'),
    path('create/', employee_file_create, name='create'),
    path('<int:pk>/', employee_file_detail, name='detail'),
    path('<int:pk>/edit/', employee_file_edit, name='edit'),
    path('<int:pk>/delete/', employee_file_delete, name='delete'),
    path('<int:pk>/download/', employee_file_download, name='download'),
]

