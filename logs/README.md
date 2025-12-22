# Logs Directory

This directory contains system log files.

## Log Files

- `celery.log` - Celery task queue logs
- `django.log` - Django application logs (auto-created)
- `api.log` - API access logs (auto-created)
- `hr_system.log` - HR system specific logs (auto-created)

## Log Rotation

Log files are automatically rotated to prevent disk space issues:
- Daily rotation for application logs
- Weekly rotation for access logs
- Compressed archives kept for 30 days

## Configuration

Logging configuration is defined in `ElDawliya_sys/settings.py` under the `LOGGING` setting.