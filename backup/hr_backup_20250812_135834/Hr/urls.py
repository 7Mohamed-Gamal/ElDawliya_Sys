from django.urls import path, include
from Hr.views import dashboard_views, employee_views, department_views, leave_views, salary_views

app_name = 'Hr'

# This is a refactored and simplified URL configuration.
# It prioritizes the modular url patterns and removes obsolete/conflicting imports.

urlpatterns = [
    # Main Dashboard
    path('dashboard/', dashboard_views.HRDashboardView.as_view(), name='dashboard'),
    path('', dashboard_views.HRDashboardView.as_view(), name='dashboard_alt'), # Root path

    # Employee URLs (Refactored to point to the correct module)
    path('employees/', include('Hr.url_modules.employee_urls', namespace='employees')),

    # Department URLs
    # The department views were consolidated into views.py, so we point there.
    # Creating a dedicated url module for departments for consistency.
    path('departments/', include('Hr.url_modules.department_urls', namespace='departments')),

    # Leave (Requests) URLs
    path('leaves/', include('Hr.url_modules.leave_urls', namespace='leaves')),

    # Salary & Payroll URLs
    path('salary/', include('Hr.url_modules.salary_urls', namespace='salary')),
    
    # Other modules can be added here as they are verified and refactored
    # path('jobs/', include('Hr.url_modules.job_urls', namespace='jobs')),
    # path('analytics/', include('Hr.url_modules.analytics_urls', namespace='analytics')),
    # path('reports/', include('Hr.url_modules.reports_urls', namespace='reports')),
    
]
