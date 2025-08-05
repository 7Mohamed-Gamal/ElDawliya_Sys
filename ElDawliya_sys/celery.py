"""
إعدادات Celery للمهام غير المتزامنة
"""

import os
from celery import Celery
from django.conf import settings

# تعيين متغير البيئة لإعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')

# إنشاء تطبيق Celery
app = Celery('ElDawliya_sys')

# تحميل الإعدادات من Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# إعدادات Celery المتقدمة
app.conf.update(
    # إعدادات الوسيط (Broker)
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/4'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/5'),
    
    # إعدادات التسلسل
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Riyadh',
    enable_utc=True,
    
    # إعدادات المهام
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 دقيقة
    task_soft_time_limit=25 * 60,  # 25 دقيقة
    task_max_retries=3,
    task_default_retry_delay=60,  # دقيقة واحدة
    
    # إعدادات العامل (Worker)
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    worker_enable_remote_control=True,
    
    # إعدادات النتائج
    result_expires=3600,  # ساعة واحدة
    result_persistent=True,
    result_compression='gzip',
    
    # إعدادات المراقبة
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # إعدادات الأمان
    worker_hijack_root_logger=False,
    worker_log_color=False,
    
    # إعدادات الطوابير
    task_routes={
        'Hr.tasks.calculate_payroll': {'queue': 'payroll'},
        'Hr.tasks.generate_report': {'queue': 'reports'},
        'Hr.tasks.send_notification': {'queue': 'notifications'},
        'Hr.tasks.process_attendance': {'queue': 'attendance'},
        'Hr.tasks.backup_data': {'queue': 'maintenance'},
        'Hr.tasks.sync_external_data': {'queue': 'integration'},
        'Hr.tasks.cleanup_files': {'queue': 'maintenance'},
        'Hr.tasks.send_email': {'queue': 'notifications'},
        'Hr.tasks.generate_analytics': {'queue': 'analytics'},
    },
    
    # إعدادات الجدولة
    beat_schedule={
        # مهام يومية
        'daily-attendance-summary': {
            'task': 'Hr.tasks.generate_daily_attendance_summary',
            'schedule': 60.0 * 60.0 * 24.0,  # كل 24 ساعة
            'options': {'queue': 'reports'}
        },
        'daily-backup': {
            'task': 'Hr.tasks.create_daily_backup',
            'schedule': 60.0 * 60.0 * 24.0,  # كل 24 ساعة
            'options': {'queue': 'maintenance'}
        },
        'cleanup-temp-files': {
            'task': 'Hr.tasks.cleanup_temp_files',
            'schedule': 60.0 * 60.0 * 6.0,  # كل 6 ساعات
            'options': {'queue': 'maintenance'}
        },
        
        # مهام أسبوعية
        'weekly-payroll-calculation': {
            'task': 'Hr.tasks.calculate_weekly_payroll',
            'schedule': 60.0 * 60.0 * 24.0 * 7.0,  # كل أسبوع
            'options': {'queue': 'payroll'}
        },
        'weekly-performance-report': {
            'task': 'Hr.tasks.generate_weekly_performance_report',
            'schedule': 60.0 * 60.0 * 24.0 * 7.0,  # كل أسبوع
            'options': {'queue': 'reports'}
        },
        
        # مهام شهرية
        'monthly-analytics': {
            'task': 'Hr.tasks.generate_monthly_analytics',
            'schedule': 60.0 * 60.0 * 24.0 * 30.0,  # كل شهر
            'options': {'queue': 'analytics'}
        },
        'monthly-archive': {
            'task': 'Hr.tasks.archive_old_data',
            'schedule': 60.0 * 60.0 * 24.0 * 30.0,  # كل شهر
            'options': {'queue': 'maintenance'}
        },
        
        # مهام كل ساعة
        'sync-attendance-devices': {
            'task': 'Hr.tasks.sync_attendance_devices',
            'schedule': 60.0 * 60.0,  # كل ساعة
            'options': {'queue': 'integration'}
        },
        'check-document-expiry': {
            'task': 'Hr.tasks.check_document_expiry',
            'schedule': 60.0 * 60.0,  # كل ساعة
            'options': {'queue': 'notifications'}
        },
        
        # مهام كل 15 دقيقة
        'process-pending-notifications': {
            'task': 'Hr.tasks.process_pending_notifications',
            'schedule': 60.0 * 15.0,  # كل 15 دقيقة
            'options': {'queue': 'notifications'}
        },
        'monitor-system-health': {
            'task': 'Hr.tasks.monitor_system_health',
            'schedule': 60.0 * 15.0,  # كل 15 دقيقة
            'options': {'queue': 'maintenance'}
        },
    },
)

# اكتشاف المهام تلقائياً
app.autodiscover_tasks()

# إعدادات إضافية للبيئة المحلية
if settings.DEBUG:
    app.conf.update(
        task_always_eager=False,  # تشغيل المهام بشكل غير متزامن حتى في التطوير
        task_eager_propagates=True,
        worker_log_level='DEBUG',
    )

# دالة لاختبار Celery
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return 'Celery is working!'

# دالة لمراقبة صحة النظام
@app.task
def health_check():
    """فحص صحة النظام"""
    import psutil
    import time
    
    return {
        'timestamp': time.time(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'status': 'healthy'
    }

# إعدادات مخصصة للطوابير
QUEUE_CONFIGS = {
    'payroll': {
        'priority': 9,
        'max_workers': 2,
        'time_limit': 1800,  # 30 دقيقة
        'soft_time_limit': 1500,  # 25 دقيقة
    },
    'reports': {
        'priority': 7,
        'max_workers': 3,
        'time_limit': 900,  # 15 دقيقة
        'soft_time_limit': 720,  # 12 دقيقة
    },
    'notifications': {
        'priority': 8,
        'max_workers': 5,
        'time_limit': 300,  # 5 دقائق
        'soft_time_limit': 240,  # 4 دقائق
    },
    'attendance': {
        'priority': 6,
        'max_workers': 2,
        'time_limit': 600,  # 10 دقائق
        'soft_time_limit': 480,  # 8 دقائق
    },
    'maintenance': {
        'priority': 3,
        'max_workers': 1,
        'time_limit': 3600,  # ساعة واحدة
        'soft_time_limit': 3300,  # 55 دقيقة
    },
    'integration': {
        'priority': 5,
        'max_workers': 2,
        'time_limit': 600,  # 10 دقائق
        'soft_time_limit': 480,  # 8 دقائق
    },
    'analytics': {
        'priority': 4,
        'max_workers': 1,
        'time_limit': 1800,  # 30 دقيقة
        'soft_time_limit': 1500,  # 25 دقيقة
    },
}

# دالة لبدء العامل مع إعدادات مخصصة
def start_worker(queue_name='default', concurrency=1):
    """بدء عامل Celery مع إعدادات مخصصة"""
    
    if queue_name in QUEUE_CONFIGS:
        config = QUEUE_CONFIGS[queue_name]
        concurrency = config.get('max_workers', concurrency)
    
    command = [
        'celery',
        '-A', 'ElDawliya_sys',
        'worker',
        '-Q', queue_name,
        '-c', str(concurrency),
        '--loglevel=info',
        f'--hostname=worker-{queue_name}@%h'
    ]
    
    return command

# دالة لبدء المجدول
def start_beat():
    """بدء مجدول Celery"""
    
    command = [
        'celery',
        '-A', 'ElDawliya_sys',
        'beat',
        '--loglevel=info',
        '--scheduler=django_celery_beat.schedulers:DatabaseScheduler'
    ]
    
    return command

# دالة لمراقبة المهام
def start_monitor():
    """بدء مراقب Celery"""
    
    command = [
        'celery',
        '-A', 'ElDawliya_sys',
        'flower',
        '--port=5555',
        '--broker=redis://127.0.0.1:6379/4'
    ]
    
    return command

# إعدادات التسجيل
CELERY_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/celery.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# تطبيق إعدادات التسجيل
import logging.config
logging.config.dictConfig(CELERY_LOGGING)