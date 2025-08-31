from django.urls import path
from . import views

app_name = 'org'

urlpatterns = [
    path('', views.index, name='index'),

    # Departments
    path('departments/', views.departments, name='departments'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:dept_id>/', views.department_detail, name='department_detail'),
    path('departments/<int:dept_id>/edit/', views.department_edit, name='department_edit'),

    # Jobs
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/add/', views.job_add, name='job_add'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),

    # Branches
    path('branches/', views.branches, name='branches'),
    path('branches/add/', views.branch_add, name='branch_add'),
    path('branches/<int:branch_id>/', views.branch_detail, name='branch_detail'),
]

