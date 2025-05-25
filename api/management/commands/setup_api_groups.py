from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Setup API user groups and permissions'

    def handle(self, *args, **options):
        # Create API user groups
        groups_data = [
            {
                'name': 'API_Users',
                'description': 'Users who can access the API'
            },
            {
                'name': 'HR_Users',
                'description': 'Users who can access HR data via API'
            },
            {
                'name': 'Inventory_Users',
                'description': 'Users who can access inventory data via API'
            },
            {
                'name': 'Meeting_Users',
                'description': 'Users who can access meeting data via API'
            },
            {
                'name': 'AI_Users',
                'description': 'Users who can use AI features'
            }
        ]

        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name']
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created group: {group_data["name"]}'
                    )
                )
            else:
                self.stdout.write(
                    f'Group already exists: {group_data["name"]}'
                )

        # Setup permissions for API models
        try:
            from api.models import APIKey, GeminiConversation, GeminiMessage, APIUsageLog
            
            # Get API Users group
            api_users_group = Group.objects.get(name='API_Users')
            
            # Add permissions for API models
            api_content_types = [
                ContentType.objects.get_for_model(APIKey),
                ContentType.objects.get_for_model(GeminiConversation),
                ContentType.objects.get_for_model(GeminiMessage),
                ContentType.objects.get_for_model(APIUsageLog),
            ]
            
            for content_type in api_content_types:
                permissions = Permission.objects.filter(content_type=content_type)
                for permission in permissions:
                    api_users_group.permissions.add(permission)
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully setup API permissions'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error setting up permissions: {str(e)}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                'API groups setup completed successfully!'
            )
        )
