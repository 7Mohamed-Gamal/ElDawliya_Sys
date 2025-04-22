from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),
    path('<int:pk>/', views.meeting_detail, name='detail'),
    path('create/', views.meeting_create, name='create'),
    path('list/', views.meeting_list, name='list'),
    path('<int:pk>/edit/', views.meeting_edit, name='edit'),
    path('<int:pk>/delete/', views.meeting_delete, name='delete'),
    path('<int:pk>/add-attendee/', views.add_attendee, name='add_attendee'),
    path('<int:pk>/remove-attendee/', views.remove_attendee, name='remove_attendee'),
]
