from django.urls import path
from django.shortcuts import render

app_name = 'loans'

# Temporary under construction view
def under_construction_view(request):
    return render(request, 'under_construction_app.html', {
        'app_name': 'نظام القروض',
        'app_description': 'نظام إدارة قروض الموظفين قيد التطوير'
    })

urlpatterns = [
    path('', under_construction_view, name='dashboard'),
    path('home/', under_construction_view, name='home'),
]

