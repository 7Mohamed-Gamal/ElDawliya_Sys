import secrets
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from api.models import APIKey

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an API key for a user'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Username for which to create the API key'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Default API Key',
            help='Name for the API key'
        )
        parser.add_argument(
            '--expires-days',
            type=int,
            help='Number of days until the API key expires'
        )

    def handle(self, *args, **options):
        username = options['username']
        key_name = options['name']
        expires_days = options.get('expires_days')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        # Generate API key
        api_key = secrets.token_urlsafe(32)

        # Set expiration date if provided
        expires_at = None
        if expires_days:
            from datetime import datetime, timedelta
            expires_at = datetime.now() + timedelta(days=expires_days)

        # Create API key
        api_key_obj = APIKey.objects.create(
            user=user,
            name=key_name,
            key=api_key,
            expires_at=expires_at
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created API key for user "{username}"'
            )
        )
        self.stdout.write(f'API Key: {api_key}')
        self.stdout.write(f'Key Name: {key_name}')
        if expires_at:
            self.stdout.write(f'Expires: {expires_at}')
        
        self.stdout.write(
            self.style.WARNING(
                'Please save this API key securely. It will not be shown again.'
            )
        )
