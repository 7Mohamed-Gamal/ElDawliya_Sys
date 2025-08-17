"""
URLs خاصة بالوظائف
"""

from django.urls import path
from ..views.job_views import (
    job_list, job_create, job_detail, job_edit, job_delete, get_next_job_code
)

app_name = 'jobs'

urlpatterns = [
    # Job patterns
    path('', job_list, name='job_list'),
    path('create/', job_create, name='job_create'),
    path('<int:jop_code>/', job_detail, name='job_detail'),
    path('<int:jop_code>/edit/', job_edit, name='job_edit'),
    path('<int:jop_code>/delete/', job_delete, name='job_delete'),
    path('next_code/', get_next_job_code, name='get_next_job_code'),
]