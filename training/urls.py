from django.urls import path
from django.shortcuts import render

app_name = 'training'

# Temporary under construction view
def under_construction_view(request):
    return render(request, 'under_construction_app.html', {
        'app_name': 'نظام التدريب',
        'app_description': 'نظام إدارة برامج التدريب والتطوير قيد التطوير'
    })

urlpatterns = [
    path('', under_construction_view, name='dashboard'),
    path('home/', under_construction_view, name='home'),
]

