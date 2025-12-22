from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    # This is a placeholder for the main HR dashboard
    context = {
        'title': 'لوحة تحكم الموارد البشرية',
        'welcome_message': f'مرحباً بك يا {request.user.username} في نظام إدارة الموارد البشرية',
        # Add more context data here later for a real dashboard
    }
    return render(request, 'hr_core/dashboard.html', context)
