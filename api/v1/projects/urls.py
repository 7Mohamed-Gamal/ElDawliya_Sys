"""
Projects API URLs
روابط API المشاريع
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for Projects ViewSets
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'meetings', views.MeetingViewSet, basename='meeting')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'time-entries', views.TimeEntryViewSet, basename='time_entry')

app_name = 'projects_api'

urlpatterns = [
    # Project management endpoints
    path('projects/templates/', views.ProjectTemplatesView.as_view(), name='project_templates'),
    path('projects/gantt/', views.ProjectGanttView.as_view(), name='project_gantt'),
    path('projects/timeline/', views.ProjectTimelineView.as_view(), name='project_timeline'),
    
    # Task management endpoints
    path('tasks/assign/', views.TaskAssignmentView.as_view(), name='task_assignment'),
    path('tasks/bulk-update/', views.BulkTaskUpdateView.as_view(), name='bulk_task_update'),
    path('tasks/dependencies/', views.TaskDependenciesView.as_view(), name='task_dependencies'),
    path('tasks/kanban/', views.TaskKanbanView.as_view(), name='task_kanban'),
    
    # Meeting management endpoints
    path('meetings/schedule/', views.MeetingScheduleView.as_view(), name='meeting_schedule'),
    path('meetings/calendar/', views.MeetingCalendarView.as_view(), name='meeting_calendar'),
    path('meetings/minutes/', views.MeetingMinutesView.as_view(), name='meeting_minutes'),
    
    # Document management endpoints
    path('documents/upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('documents/versions/', views.DocumentVersionsView.as_view(), name='document_versions'),
    path('documents/share/', views.DocumentSharingView.as_view(), name='document_sharing'),
    
    # Time tracking endpoints
    path('time/start/', views.StartTimeTrackingView.as_view(), name='start_time_tracking'),
    path('time/stop/', views.StopTimeTrackingView.as_view(), name='stop_time_tracking'),
    path('time/reports/', views.TimeReportsView.as_view(), name='time_reports'),
    
    # Reports and analytics
    path('reports/dashboard/', views.ProjectsDashboardView.as_view(), name='projects_dashboard'),
    path('reports/analytics/', views.ProjectsAnalyticsView.as_view(), name='projects_analytics'),
    path('reports/performance/', views.ProjectPerformanceView.as_view(), name='project_performance'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]