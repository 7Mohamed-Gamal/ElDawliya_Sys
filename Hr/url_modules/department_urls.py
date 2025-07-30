"""
URLs خاصة بالأقسام
"""

from django.urls import path
from ..views.department_views_updated import (
    department_list, department_create, department_edit,
    department_delete, department_performance, department_detail
)

app_name = 'departments'

urlpatterns = [
    # Department patterns
    path('', department_list, name='department_list'),
    path('create/', department_create, name='department_create'),
    path('<int:dept_code>/', department_detail, name='department_detail'),
    path('<int:dept_code>/edit/', department_edit, name='department_edit'),
    path('<int:dept_code>/delete/', department_delete, name='department_delete'),
    path('<int:dept_code>/performance/', department_performance, name='department_performance'),
]