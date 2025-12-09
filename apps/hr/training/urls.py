from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    # Dashboard
    path('', views.training_dashboard, name='dashboard'),
    path('home/', views.training_dashboard, name='home'),

    # Training Providers
    path('providers/', views.provider_list, name='provider_list'),
    path('providers/create/', views.provider_create, name='provider_create'),
    path('providers/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('providers/<int:provider_id>/edit/', views.provider_update, name='provider_update'),
    path('providers/<int:provider_id>/delete/', views.provider_delete, name='provider_delete'),

    # Training Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),

    # Employee Training Enrollments
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:enrollment_id>/', views.enrollment_detail, name='enrollment_detail'),
    path('enrollments/<int:enrollment_id>/edit/', views.enrollment_update, name='enrollment_update'),
    path('enrollments/<int:enrollment_id>/delete/', views.enrollment_delete, name='enrollment_delete'),

    # Employee Training History
    path('employee/<int:emp_id>/history/', views.employee_training_history, name='employee_training_history'),
]

