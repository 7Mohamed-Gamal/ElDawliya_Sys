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
    # Assuming 'projects:list' should go to task list or we need a main project list view if it exists. 
    # Since we don't have a top-level project list view, we'll route to tasks list for now to prevent crash, 
    # or better, route to tasks list as the "main" project view.
    # Redirect 'list' to tasks list to support dashboard link
    path('list/', include('apps.projects.tasks.urls')), 
    path('overview/', RedirectView.as_view(pattern_name='projects:tasks:list', permanent=False), name='list'),
]