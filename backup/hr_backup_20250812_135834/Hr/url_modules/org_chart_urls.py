"""
Organization Chart URLs for HR module
"""

from django.urls import path
from Hr.views.org_chart_views import (
    org_chart, org_chart_data, department_org_chart, employee_hierarchy
)

app_name = 'org_chart'

urlpatterns = [
    path('', org_chart, name='org_chart'),
    path('data/', org_chart_data, name='org_chart_data'),
    path('department/<int:dept_id>/', department_org_chart, name='department_org_chart'),
    path('employee/<int:emp_id>/', employee_hierarchy, name='employee_hierarchy'),
]