"""
روابط التكامل مع الأنظمة الخارجية
"""

from django.urls import path
from ..views import integration_views

app_name = 'integrations'

urlpatterns = [
    # لوحة التحكم
    path('', integration_views.integration_dashboard, name='dashboard'),

    # الأنظمة الخارجية
    path('systems/', integration_views.external_systems_list, name='systems_list'),
    path('systems/create/', integration_views.create_external_system, name='create_system'),
    path('systems/<uuid:system_id>/test/', integration_views.test_system_connection, name='test_connection'),
    path('systems/<uuid:system_id>/sync/', integration_views.sync_system, name='sync_system'),
    path('systems/<uuid:system_id>/mappings/', integration_views.integration_mappings, name='integration_mappings'),
    path('systems/status/', integration_views.systems_status, name='systems_status'),

    # مهام المزامنة
    path('jobs/', integration_views.sync_jobs_list, name='jobs_list'),
    path('jobs/create/', integration_views.create_sync_job, name='create_job'),
    path('jobs/<uuid:job_id>/details/', integration_views.job_details, name='job_details'),
    path('jobs/<uuid:job_id>/start/', integration_views.start_job, name='start_job'),
    path('jobs/<uuid:job_id>/cancel/', integration_views.cancel_job, name='cancel_job'),
    path('jobs/running/', integration_views.running_jobs, name='running_jobs'),

    # مفاتيح API
    path('api-keys/', integration_views.api_keys_list, name='api_keys_list'),
    path('api-keys/create/', integration_views.create_api_key, name='create_api_key'),

    # Webhooks
    path('webhook/<uuid:system_id>/', integration_views.webhook_receiver, name='webhook_receiver'),
]