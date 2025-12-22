# ElDawliya System Configuration Guide

## Overview

The ElDawliya system uses a modular configuration approach with environment-specific settings files and centralized configuration management.

## Configuration Structure

```
ElDawliya_sys/settings/
├── __init__.py          # Settings package initialization
├── base.py              # Base settings shared across all environments
├── development.py       # Development-specific settings
├── production.py        # Production-specific settings
├── testing.py           # Testing-specific settings
└── config.py            # Configuration management utilities
```

## Environment Configuration

### Setting the Environment

Set the `DJANGO_SETTINGS_MODULE` environment variable to specify which settings to use:

```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.development

# Production
export DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.production

# Testing
export DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.testing
```

### Environment Variables

All configuration is managed through environment variables defined in the `.env` file. Copy `.env.example` to `.env` and configure your values:

```bash
cp .env.example .env
```

## Required Configuration

### Core Django Settings

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration

```env
DB_NAME=ElDawliya_Sys
DB_HOST=localhost
DB_PORT=1433
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### Security Settings

```env
FIELD_ENCRYPTION_KEY=your-32-character-encryption-key
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

## Optional Configuration

### Email Settings

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

### AI Services

```env
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
```

### Caching and Background Tasks

```env
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/4
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/5
```

## HR System Specific Settings

```env
EMPLOYEE_NUMBER_PREFIX=EMP
EMPLOYEE_NUMBER_LENGTH=6
DEFAULT_WORK_HOURS_PER_DAY=8
DEFAULT_WORK_DAYS_PER_WEEK=5
OVERTIME_THRESHOLD_MINUTES=30
LATE_THRESHOLD_MINUTES=15
DOCUMENT_EXPIRY_WARNING_DAYS=30
LEAVE_BALANCE_CALCULATION_METHOD=monthly
PAYROLL_CALCULATION_METHOD=monthly
ATTENDANCE_SYNC_ENABLED=True
ATTENDANCE_SYNC_INTERVAL=300
```

## Configuration Validation

Use the management command to validate your configuration:

```bash
# Basic validation
python manage.py validate_config

# Verbose output with configuration details
python manage.py validate_config --verbose

# Show fix suggestions for warnings
python manage.py validate_config --fix-warnings
```

## Environment-Specific Features

### Development Environment

- Debug toolbar enabled
- Console email backend
- Local memory cache
- Verbose logging
- All security features disabled for easier development

### Production Environment

- All security features enabled (HTTPS, HSTS, secure cookies)
- Redis caching
- SMTP email backend
- Compressed static files
- Error tracking with Sentry (if configured)
- Performance optimizations

### Testing Environment

- In-memory SQLite database
- Dummy cache backend
- Locmem email backend
- Minimal logging
- Fast password hashing
- Migrations disabled

## Security Considerations

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Enable HTTPS with proper SSL certificates
- [ ] Set secure cookie settings
- [ ] Configure proper CORS and CSRF origins
- [ ] Set up field encryption key
- [ ] Configure error tracking (Sentry)
- [ ] Set up proper logging
- [ ] Configure backup strategy

### Sensitive Data

Never commit sensitive data to version control:
- Database passwords
- API keys
- Secret keys
- Email passwords
- Encryption keys

Use environment variables and keep `.env` files out of version control.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in `.env`
   - Check database server is running
   - Verify network connectivity

2. **Missing Environment Variables**
   - Run `python manage.py validate_config` to check configuration
   - Ensure `.env` file exists and is properly formatted

3. **Cache/Redis Errors**
   - Verify Redis server is running
   - Check Redis URL configuration
   - For development, switch to local memory cache

4. **Email Issues**
   - Verify SMTP settings
   - Check email credentials
   - For development, use console backend

### Getting Help

1. Run configuration validation: `python manage.py validate_config --verbose`
2. Check Django settings: `python manage.py diffsettings`
3. Review logs in the `logs/` directory
4. Consult the troubleshooting section in the main documentation

## Migration from Old Configuration

If migrating from the old single `settings.py` file:

1. Copy your current settings to `.env` file
2. Update `DJANGO_SETTINGS_MODULE` to use the new structure
3. Run configuration validation
4. Test all functionality in development environment
5. Deploy to production with proper environment settings

The new configuration system provides better organization, security, and maintainability while preserving all existing functionality.