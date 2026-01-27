"""
Projects API URLs.
"""

from django.urls import path, include
from django.views.generic import RedirectView

app_name = 'projects'

urlpatterns = [
    # Sub-apps
    path('tasks/', include('apps.projects.tasks.urls')),
    path('meetings/', include('apps.projects.meetings.urls')),
    
    # Aliases/Redirects to support dashboard links
    # Redirect 'tasks' to tasks dashboard to support {% url 'projects:tasks' %}
    path('tasks-redirect/', RedirectView.as_view(pattern_name='projects:tasks:dashboard', permanent=False), name='tasks'),
    
    # Redirect 'meetings' to meetings list to support {% url 'projects:meetings' %}
    path('meetings-redirect/', RedirectView.as_view(pattern_name='projects:meetings:list', permanent=False), name='meetings'),
    
    # Redirect 'list' to tasks list to support dashboard link
    path('list/', RedirectView.as_view(pattern_name='projects:tasks:list', permanent=False), name='list'),
]