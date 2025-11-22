#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Default to development settings if not specified
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.development')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Show which settings module is being used
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if len(sys.argv) > 1 and sys.argv[1] not in ['help', '--help', '-h']:
        environment = settings_module.split('.')[-1] if settings_module else 'unknown'
        print(f"🚀 ElDawliya System - Using {environment} environment")
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
