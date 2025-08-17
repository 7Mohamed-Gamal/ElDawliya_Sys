"""
Leave Balances URLs for HR module
"""

from django.urls import path
from django.http import HttpResponse

# Placeholder views - will be implemented later
def leave_balance_list(request):
    return HttpResponse("Leave Balance List - Coming Soon")

def leave_balance_detail(request, employee_id):
    return HttpResponse(f"Leave Balance Detail for Employee {employee_id} - Coming Soon")

def leave_balance_update(request, employee_id):
    return HttpResponse(f"Update Leave Balance for Employee {employee_id} - Coming Soon")

def leave_balance_report(request):
    return HttpResponse("Leave Balance Report - Coming Soon")

app_name = 'leave_balances'

urlpatterns = [
    path('', leave_balance_list, name='leave_balance_list'),
    path('<int:employee_id>/', leave_balance_detail, name='leave_balance_detail'),
    path('<int:employee_id>/update/', leave_balance_update, name='leave_balance_update'),
    path('report/', leave_balance_report, name='report'),
]