from django.urls import path
from django.http import HttpResponse

# Simple dummy view function for minimal URL setup
def dummy_view(request, *args, **kwargs):
    return HttpResponse("Placeholder view - minimal URLs are being used to fix migration issues.")

app_name = 'accounts'

urlpatterns = [
    path('login/', dummy_view, name='login'),
    path('logout/', dummy_view, name='logout'),
    path('dashboard/', dummy_view, name='dashboard'),
    path('home/', dummy_view, name='home'),
    path('users/create/', dummy_view, name='create_user'),
    path('users/<int:user_id>/edit-permissions/', dummy_view, name='edit_user_permissions'),
    path('access-denied/', dummy_view, name='access_denied'),
]
