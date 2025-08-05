"""
Leave Requests URLs for HR module
"""

from django.urls import path
# Placeholder views - will be implemented later
from django.shortcuts import render
from django.http import HttpResponse

def leave_request_list(request):
    return HttpResponse("Leave Request List - Coming Soon")

def leave_request_create(request):
    return HttpResponse("Create Leave Request - Coming Soon")

def leave_request_detail(request, request_id):
    return HttpResponse(f"Leave Request Detail {request_id} - Coming Soon")

def leave_request_edit(request, request_id):
    return HttpResponse(f"Edit Leave Request {request_id} - Coming Soon")

def leave_request_delete(request, request_id):
    return HttpResponse(f"Delete Leave Request {request_id} - Coming Soon")

def leave_request_approve(request, request_id):
    return HttpResponse(f"Approve Leave Request {request_id} - Coming Soon")

def leave_request_reject(request, request_id):
    return HttpResponse(f"Reject Leave Request {request_id} - Coming Soon")

def leave_balance_view(request):
    return HttpResponse("Leave Balance - Coming Soon")

def leave_calendar_view(request):
    return HttpResponse("Leave Calendar - Coming Soon")

app_name = 'leave_requests'

def leave_requests_pending(request):
    return HttpResponse("Pending Leave Requests - Coming Soon")

urlpatterns = [
    path('', leave_request_list, name='leave_request_list'),
    path('list/', leave_request_list, name='list'),
    path('pending/', leave_requests_pending, name='pending'),
    path('create/', leave_request_create, name='leave_request_create'),
    path('<int:request_id>/', leave_request_detail, name='leave_request_detail'),
    path('<int:request_id>/edit/', leave_request_edit, name='leave_request_edit'),
    path('<int:request_id>/delete/', leave_request_delete, name='leave_request_delete'),
    path('<int:request_id>/approve/', leave_request_approve, name='leave_request_approve'),
    path('<int:request_id>/reject/', leave_request_reject, name='leave_request_reject'),
    path('balance/', leave_balance_view, name='leave_balance'),
    path('calendar/', leave_calendar_view, name='leave_calendar'),
]