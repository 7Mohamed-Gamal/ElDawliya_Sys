from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.AuditLogListView.as_view(), name='audit_list'),
    path('<int:pk>/', views.AuditLogDetailView.as_view(), name='audit_detail'),
    path('export/', views.export_audit_logs, name='audit_export'),
]
