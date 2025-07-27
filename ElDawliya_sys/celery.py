"""
Celery configuration for ElDawliya HR System
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')

app = Celery('ElDawliya_sys')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for HR System
app.conf.beat_schedule = {
    'sync-attendance-records': {
        'task': 'Hr.tasks.sync_attendance_from_devices',
        'schedule': 900.0,  # Every 15 minutes
    },
    'check-document-expiry': {
        'task': 'Hr.tasks.check_document_expiry',
        'schedule': 86400.0,  # Daily
    },
    'calculate-leave-balances': {
        'task': 'Hr.tasks.calculate_monthly_leave_balances',
        'schedule': 2592000.0,  # Monthly (30 days)
    },
    'generate-attendance-summary': {
        'task': 'Hr.tasks.generate_daily_attendance_summary',
        'schedule': 3600.0,  # Hourly
    },
    'send-birthday-notifications': {
        'task': 'Hr.tasks.send_birthday_notifications',
        'schedule': 86400.0,  # Daily
    },
    'backup-hr-data': {
        'task': 'Hr.tasks.backup_hr_data',
        'schedule': 604800.0,  # Weekly
    },
}

app.conf.timezone = settings.TIME_ZONE

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')