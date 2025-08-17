"""
Employee Training URLs for HR module
"""

from django.urls import path
from django.http import HttpResponse

# Placeholder views - will be implemented later
def training_list(request):
    return HttpResponse("Training List - Coming Soon")

def training_create(request):
    return HttpResponse("Create Training - Coming Soon")

def training_detail(request, training_id):
    return HttpResponse(f"Training Detail {training_id} - Coming Soon")

def training_edit(request, training_id):
    return HttpResponse(f"Edit Training {training_id} - Coming Soon")

def training_delete(request, training_id):
    return HttpResponse(f"Delete Training {training_id} - Coming Soon")

def employee_training_list(request):
    return HttpResponse("Employee Training List - Coming Soon")

def employee_training_assign(request):
    return HttpResponse("Assign Training to Employee - Coming Soon")

def training_report(request):
    return HttpResponse("Training Report - Coming Soon")

app_name = 'employee_training'

urlpatterns = [
    path('', training_list, name='training_list'),
    path('list/', employee_training_list, name='list'),
    path('create/', training_create, name='training_create'),
    path('assign/', employee_training_assign, name='training_assign'),
    path('report/', training_report, name='training_report'),
    path('<int:training_id>/', training_detail, name='training_detail'),
    path('<int:training_id>/edit/', training_edit, name='training_edit'),
    path('<int:training_id>/delete/', training_delete, name='training_delete'),
]