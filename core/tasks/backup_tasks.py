"""
Celery Tasks for Automated Backup System
========================================

Scheduled tasks for automatic backup creation and maintenance
"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from core.services.backup_service import backup_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def create_scheduled_backup(self):
    """مهمة إنشاء نسخة احتياطية مجدولة"""

    try:
        logger.info("Starting scheduled backup task")

        # Create full backup
        backup_info = backup_service.create_full_backup()

        if backup_info['status'] == 'completed':
            logger.info("Scheduled backup completed successfully")
            return {
                'status': 'success',
                'backup_info': backup_info,
                'timestamp': timezone.now().isoformat(),
            }
        else:
            logger.error(f"Scheduled backup failed: {backup_info.get('error', 'Unknown error')}")
            raise Exception(f"Backup failed: {backup_info.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Scheduled backup task failed: {e}")

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 60 * (2 ** self.request.retries)  # 1, 2, 4 minutes
            logger.info(f"Retrying backup task in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=e)
        else:
            logger.error("Max retries reached for backup task")
            raise


@shared_task
def cleanup_old_backups():
    """مهمة تنظيف النسخ الاحتياطية القديمة"""

    try:
        logger.info("Starting backup cleanup task")

        cleanup_result = backup_service.cleanup_old_backups()

        if cleanup_result['status'] == 'completed':
            deleted_count = len(cleanup_result['deleted_files'])
            freed_space = backup_service.format_bytes(cleanup_result['freed_space_bytes'])

            logger.info(f"Backup cleanup completed: {deleted_count} files deleted, {freed_space} freed")

            return {
                'status': 'success',
                'deleted_files': deleted_count,
                'freed_space_bytes': cleanup_result['freed_space_bytes'],
                'timestamp': timezone.now().isoformat(),
            }
        else:
            logger.error(f"Backup cleanup failed: {cleanup_result.get('error', 'Unknown error')}")
            raise Exception(f"Cleanup failed: {cleanup_result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Backup cleanup task failed: {e}")
        raise


@shared_task
def verify_backup_integrity():
    """مهمة التحقق من سلامة النسخ الاحتياطية"""

    try:
        logger.info("Starting backup verification task")

        backups = backup_service.list_backups()

        if not backups:
            logger.info("No backups found to verify")
            return {
                'status': 'success',
                'message': 'No backups to verify',
                'timestamp': timezone.now().isoformat(),
            }

        verified_count = 0
        failed_count = 0
        failed_backups = []

        # Verify recent backups (last 7 days)
        cutoff_date = timezone.now() - timedelta(days=7)

        for backup in backups:
            backup_date = backup.get('created')
            if backup_date and backup_date < cutoff_date:
                continue  # Skip old backups

            if backup.get('status') != 'completed':
                continue  # Skip incomplete backups

            try:
                verification_result = backup_service.verify_backup_integrity(backup)

                if verification_result['status'] == 'completed':
                    verified_count += 1
                else:
                    failed_count += 1
                    failed_backups.append({
                        'timestamp': backup.get('timestamp'),
                        'error': verification_result.get('error', 'Verification failed')
                    })

            except Exception as e:
                failed_count += 1
                failed_backups.append({
                    'timestamp': backup.get('timestamp'),
                    'error': str(e)
                })

        logger.info(f"Backup verification completed: {verified_count} passed, {failed_count} failed")

        return {
            'status': 'success',
            'verified_count': verified_count,
            'failed_count': failed_count,
            'failed_backups': failed_backups,
            'timestamp': timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Backup verification task failed: {e}")
        raise


@shared_task
def create_database_backup():
    """مهمة إنشاء نسخة احتياطية لقاعدة البيانات فقط"""

    try:
        logger.info("Starting database backup task")

        # Create database backup only
        backup_result = backup_service.backup_database()

        if backup_result['status'] == 'completed':
            logger.info("Database backup completed successfully")
            return {
                'status': 'success',
                'backup_result': backup_result,
                'timestamp': timezone.now().isoformat(),
            }
        else:
            logger.error(f"Database backup failed: {backup_result.get('error', 'Unknown error')}")
            raise Exception(f"Database backup failed: {backup_result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Database backup task failed: {e}")
        raise


@shared_task
def create_media_backup():
    """مهمة إنشاء نسخة احتياطية للملفات والوسائط"""

    try:
        logger.info("Starting media backup task")

        # Create media backup only
        backup_result = backup_service.backup_media_files()

        if backup_result['status'] == 'completed':
            logger.info("Media backup completed successfully")
            return {
                'status': 'success',
                'backup_result': backup_result,
                'timestamp': timezone.now().isoformat(),
            }
        else:
            logger.error(f"Media backup failed: {backup_result.get('error', 'Unknown error')}")
            raise Exception(f"Media backup failed: {backup_result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Media backup task failed: {e}")
        raise


@shared_task
def send_backup_status_report():
    """مهمة إرسال تقرير حالة النسخ الاحتياطية"""

    try:
        logger.info("Starting backup status report task")

        # Get backup statistics
        stats = backup_service.get_backup_statistics()

        # Get recent backups (last 7 days)
        recent_backups = []
        cutoff_date = timezone.now() - timedelta(days=7)

        for backup in backup_service.list_backups():
            backup_date = backup.get('created')
            if backup_date and backup_date >= cutoff_date:
                recent_backups.append(backup)

        # Create report
        report = {
            'generated_at': timezone.now().isoformat(),
            'statistics': stats,
            'recent_backups': len(recent_backups),
            'successful_recent': sum(1 for b in recent_backups if b.get('status') == 'completed'),
            'failed_recent': sum(1 for b in recent_backups if b.get('status') != 'completed'),
        }

        # Send notification if there are issues
        if report['failed_recent'] > 0 or stats['total_backups'] == 0:
            backup_service.send_backup_notification({
                'status': 'warning',
                'timestamp': timezone.now().isoformat(),
                'message': f"Backup status report: {report['failed_recent']} failed backups in last 7 days",
                'report': report
            })

        logger.info("Backup status report completed")

        return {
            'status': 'success',
            'report': report,
            'timestamp': timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Backup status report task failed: {e}")
        raise


@shared_task
def emergency_backup():
    """مهمة النسخ الاحتياطي الطارئ"""

    try:
        logger.info("Starting emergency backup task")

        # Create emergency backup with minimal components
        backup_info = {
            'timestamp': timezone.now().isoformat(),
            'type': 'emergency',
            'status': 'started',
            'components': {},
        }

        # Always backup database in emergency
        db_result = backup_service.backup_database()
        backup_info['components']['database'] = db_result

        # Backup media if not too large
        try:
            media_result = backup_service.backup_media_files()
            backup_info['components']['media'] = media_result
        except Exception as e:
            logger.warning(f"Emergency backup: Media backup failed: {e}")
            backup_info['components']['media'] = {
                'status': 'failed',
                'error': str(e)
            }

        # Determine overall status
        db_success = backup_info['components']['database']['status'] == 'completed'
        backup_info['status'] = 'completed' if db_success else 'failed'
        backup_info['completed_at'] = timezone.now().isoformat()

        # Save backup info
        backup_service.save_backup_info(backup_info)

        # Send notification
        backup_service.send_backup_notification(backup_info)

        logger.info("Emergency backup completed")

        return {
            'status': 'success',
            'backup_info': backup_info,
            'timestamp': timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Emergency backup task failed: {e}")
        raise


# Periodic task configuration
from celery.schedules import crontab

# Add to your celery beat schedule
CELERY_BEAT_SCHEDULE = {
    # Daily full backup at 2 AM
    'daily-full-backup': {
        'task': 'core.tasks.backup_tasks.create_scheduled_backup',
        'schedule': crontab(hour=2, minute=0),
    },

    # Database backup every 6 hours
    'database-backup-6h': {
        'task': 'core.tasks.backup_tasks.create_database_backup',
        'schedule': crontab(minute=0, hour='*/6'),
    },

    # Media backup daily at 3 AM
    'daily-media-backup': {
        'task': 'core.tasks.backup_tasks.create_media_backup',
        'schedule': crontab(hour=3, minute=0),
    },

    # Cleanup old backups weekly on Sunday at 4 AM
    'weekly-backup-cleanup': {
        'task': 'core.tasks.backup_tasks.cleanup_old_backups',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
    },

    # Verify backup integrity daily at 5 AM
    'daily-backup-verification': {
        'task': 'core.tasks.backup_tasks.verify_backup_integrity',
        'schedule': crontab(hour=5, minute=0),
    },

    # Send backup status report weekly on Monday at 8 AM
    'weekly-backup-report': {
        'task': 'core.tasks.backup_tasks.send_backup_status_report',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}
