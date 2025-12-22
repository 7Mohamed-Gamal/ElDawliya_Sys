from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list, name='list'),
    path('create/', views.company_create, name='create'),
    path('<int:pk>/', views.company_detail, name='detail'),
    path('<int:pk>/edit/', views.company_edit, name='edit'),
    path('<int:pk>/delete/', views.company_delete, name='delete'),
]

