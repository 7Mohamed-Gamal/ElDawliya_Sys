from django.urls import path
from . import views

app_name = 'org'

urlpatterns = [
    path('', views.index, name='index'),

    # Departments
    path('departments/', views.departments, name='departments'),
    path('departments/<int:dept_id>/', views.department_detail, name='department_detail'),

    # Jobs
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),

    # Branches
    path('branches/', views.branches, name='branches'),
]

