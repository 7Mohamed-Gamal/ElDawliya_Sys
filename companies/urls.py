from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list, name='list'),
    path('create/', views.company_create, name='create'),
    path('<int:pk>/', views.company_detail, name='detail'),
    path('<int:pk>/edit/', views.company_edit, name='edit'),
    path('<int:pk>/delete/', views.company_delete, name='delete'),

    # Aliases/Redirects to support dashboard links
    # Redirect 'clients' to companies list (no separate clients functionality yet)
    path('clients/', RedirectView.as_view(pattern_name='companies:list', permanent=False), name='clients'),

    # Redirect 'contacts' to companies list (no separate contacts functionality yet)
    path('contacts/', RedirectView.as_view(pattern_name='companies:list', permanent=False), name='contacts'),
]

