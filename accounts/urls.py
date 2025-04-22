from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('home/', views.home_view, name='home'),
    path('create-user/', views.create_user_view, name='create_user'),
    path('edit-permissions/<int:user_id>/', views.edit_user_permissions_view, name='edit_permissions'),
    path('access-denied/', views.access_denied, name='access_denied'),
]
