"""
Notes URLs for HR module
"""

from django.urls import path
from Hr.views.note_views import (
    employee_notes_dashboard, employee_notes_create, employee_search_ajax,
    employee_notes_list, employee_note_detail, employee_note_edit,
    employee_note_delete, employee_notes_reports
)

app_name = 'notes'

urlpatterns = [
    path('', employee_notes_dashboard, name='employee_notes_dashboard'),
    path('create/', employee_notes_create, name='employee_notes_create'),
    path('search/ajax/', employee_search_ajax, name='employee_search_ajax'),
    path('list/', employee_notes_list, name='employee_notes_list'),
    path('<int:note_id>/', employee_note_detail, name='employee_note_detail'),
    path('<int:note_id>/edit/', employee_note_edit, name='employee_note_edit'),
    path('<int:note_id>/delete/', employee_note_delete, name='employee_note_delete'),
    path('reports/', employee_notes_reports, name='employee_notes_reports'),
]