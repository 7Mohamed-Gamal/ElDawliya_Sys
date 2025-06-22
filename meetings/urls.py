from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    # لوحة التحكم
    path('', views.dashboard, name='dashboard'),

    # الاجتماعات
    path('list/', views.meeting_list, name='list'),
    path('<int:pk>/', views.meeting_detail, name='detail'),
    path('create/', views.meeting_create, name='create'),
    path('<int:pk>/edit/', views.meeting_edit, name='edit'),
    path('<int:pk>/delete/', views.meeting_delete, name='delete'),
    path('<int:pk>/add-attendee/', views.add_attendee, name='add_attendee'),
    path('<int:pk>/remove-attendee/', views.remove_attendee, name='remove_attendee'),

    # التقويم
    path('calendar/', views.calendar_view, name='calendar'),

    # التقارير
    path('reports/', views.reports, name='reports'),

    # المهام
    path('task/<int:task_id>/', views.meeting_task_detail, name='task_detail'),
]
