"""
URLs خاصة بمكونات الراتب
"""

from django.urls import path
from ..views.payroll.salary_component_views import (
    component_list,
    component_detail,
    component_create,
    component_edit,
    component_delete,
    component_duplicate,
    component_toggle_status,
    component_search_ajax
)

app_name = 'salary_components'

urlpatterns = [
    # Salary component patterns
    path('', component_list, name='list'),
    path('create/', component_create, name='create'),
    path('<str:component_id>/', component_detail, name='detail'),
    path('<str:component_id>/edit/', component_edit, name='edit'),
    path('<str:component_id>/delete/', component_delete, name='delete'),
    path('<str:component_id>/copy/', component_duplicate, name='copy'),
    path('<str:component_id>/toggle-status/', component_toggle_status, name='toggle_status'),
    path('search/ajax/', component_search_ajax, name='search_ajax'),
]