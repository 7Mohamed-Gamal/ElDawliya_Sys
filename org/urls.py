from django.urls import path
from . import views

app_name = 'org'

urlpatterns = [
    path('', views.index, name='index'),
]

