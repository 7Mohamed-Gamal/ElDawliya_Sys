"""
URLs for Departments
"""

from django.urls import path
# Correctly import from the new department_views module
from ..views import department_views as views

app_name = 'departments'

urlpatterns = [
    # Department list and creation
    path('', views.department_list, name='list'),
    path('create/', views.department_create, name='create'),

    # Department detail and actions using the primary key (pk)
    path('<int:pk>/', views.department_detail, name='detail'),
    path('<int:pk>/edit/', views.department_edit, name='edit'),
    path('<int:pk>/delete/', views.department_delete, name='delete'),
]
