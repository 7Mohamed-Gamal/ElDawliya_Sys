from django.urls import path
from django.shortcuts import render

app_name = 'tickets'

urlpatterns = [
    path('', lambda r: render(r, 'under_construction_app.html'), name='home'),
]

