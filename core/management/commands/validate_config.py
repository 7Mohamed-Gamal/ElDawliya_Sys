"""
Management command to validate ElDawliya system configuration.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ElDawliya_sys.settings.config import config_manager


class Command(BaseCommand):
    """Command class"""
    help = 'Validate ElDawliya system configuration'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--fix-warnings',
            action='store_true',
            help='Show suggestions to fix configuration warnings',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed configuration information',
        )

    def handle(self, *args, **options):
        """handle function"""
        self.stdout.write(
            self.style.SUCCESS('🔍 Validating ElDawliya System Configuration...\n')
        )

        # Validate configuration
        validation_results = config_manager.validate_configuration()

        if validation_results['valid']:
            self.stdout.write(
                self.style.SUCCESS('✅ Configuration validation passed!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Configuration validation failed!')
            )

        # Show errors
        if validation_results['errors']:
            self.stdout.write(
                self.style.ERROR('\n🚨 Configuration Errors:')
            )
            for error in validation_results['errors']:
                self.stdout.write(f'  • {error}')

        # Show warnings
        if validation_results['warnings']:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Configuration Warnings:')
            )
            for warning in validation_results['warnings']:
                self.stdout.write(f'  • {warning}')

        # Show configuration details if verbose
        if options['verbose']:
            self._show_configuration_details()

        # Show fix suggestions if requested
        if options['fix_warnings'] and validation_results['warnings']:
            self._show_fix_suggestions()

        # Exit with error code if validation failed
        if not validation_results['valid']:
            raise CommandError('Configuration validation failed')

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Configuration is ready!')
        )

    def _show_configuration_details(self):
        """Show detailed configuration information."""
        self.stdout.write(
            self.style.HTTP_INFO('\n📋 Configuration Details:')
        )

        # Database configuration
        db_config = settings.DATABASES['default']
        self.stdout.write(f'  🗄️  Database: {db_config["NAME"]} @ {db_config["HOST"]}:{db_config["PORT"]}')

        # Cache configuration
        cache_config = settings.CACHES['default']
        self.stdout.write(f'  💾 Cache: {cache_config["BACKEND"]} @ {cache_config["LOCATION"]}')

        # Email configuration
        self.stdout.write(f'  📧 Email: {settings.EMAIL_BACKEND}')
        if hasattr(settings, 'EMAIL_HOST'):
            self.stdout.write(f'      Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')

        # API configuration
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            self.stdout.write(f'  🤖 AI: Gemini API configured')
        else:
            self.stdout.write(f'  🤖 AI: Not configured')

        # HR Settings
        if hasattr(settings, 'HR_SETTINGS'):
            hr_settings = settings.HR_SETTINGS
            self.stdout.write(f'  👥 HR: Employee prefix {hr_settings["EMPLOYEE_NUMBER_PREFIX"]}, {hr_settings["DEFAULT_WORK_HOURS_PER_DAY"]}h/day')

    def _show_fix_suggestions(self):
        """Show suggestions to fix configuration warnings."""
        self.stdout.write(
            self.style.HTTP_INFO('\n💡 Fix Suggestions:')
        )

        if not config_manager.get_optional('GEMINI_API_KEY'):
            self.stdout.write(
                '  • To enable AI features, set GEMINI_API_KEY in your .env file'
            )
            self.stdout.write(
                '    Get your API key from: https://makersuite.google.com/app/apikey'
            )

        if not config_manager.get_optional('EMAIL_HOST_USER'):
            self.stdout.write(
                '  • To enable email notifications, configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD'
            )

        if not config_manager.get_optional('FIELD_ENCRYPTION_KEY'):
            self.stdout.write(
                '  • To encrypt sensitive data, generate and set FIELD_ENCRYPTION_KEY:'
            )
            self.stdout.write(
                '    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )

        if not config_manager.get_optional('SENTRY_DSN'):
            self.stdout.write(
                '  • For production error tracking, configure SENTRY_DSN'
            )
            self.stdout.write(
                '    Sign up at: https://sentry.io/'
            )