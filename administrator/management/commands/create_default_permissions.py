from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from administrator.rbac_permissions import create_default_permissions, assign_default_admin_permissions


class Command(BaseCommand):
    help = 'Creates default permissions for the RBAC system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--assign-admin',
            action='store_true',
            dest='assign_admin',
            help='Assign all permissions to the admin group',
        )

    def handle(self, *args, **options):
        # Create default permissions
        permissions = create_default_permissions()
        
        # Count total permissions created
        total_permissions = sum(len(perms) for perms in permissions.values())
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_permissions} default permissions'))
        
        # Print permissions by category
        for category, perms in permissions.items():
            self.stdout.write(self.style.SUCCESS(f'Category: {category}'))
            for perm in perms:
                self.stdout.write(f'  - {perm.codename}: {perm.name}')
        
        # Assign permissions to admin group if requested
        if options['assign_admin']:
            # Get or create admin group
            admin_group, created = Group.objects.get_or_create(name='admin')
            
            # Assign all permissions to admin group
            assigned_permissions = assign_default_admin_permissions(admin_group)
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully assigned {len(assigned_permissions)} permissions to admin group'
            ))
