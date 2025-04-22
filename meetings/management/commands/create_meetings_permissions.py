from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import transaction

from administrator.models import Department as AdminDepartment, Module, Permission as AdminPermission
from meetings.decorators import MODULES, DEPARTMENT_NAME

class Command(BaseCommand):
    help = 'Create meetings permissions for all modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating meetings permissions...'))

        try:
            with transaction.atomic():
                # 1. Create or get the meetings department
                meetings_department, created = AdminDepartment.objects.get_or_create(
                    name=DEPARTMENT_NAME,
                    defaults={
                        'description': 'قسم إدارة الاجتماعات',
                        'icon': 'fas fa-calendar-alt',
                        'url_name': 'meetings_app',
                        'order': 3,
                        'is_active': True,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created meetings department: {meetings_department.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing meetings department: {meetings_department.name}'))

                # 2. Create modules for each module in MODULES
                for module_key, module_name in MODULES.items():
                    module, created = Module.objects.get_or_create(
                        department=meetings_department,
                        name=module_name,
                        defaults={
                            'description': f'وحدة {module_name}',
                            'url': f'/meetings/{module_key}/',
                            'icon': 'fas fa-folder',
                            'order': list(MODULES.keys()).index(module_key) + 1,
                            'is_active': True,
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created module: {module.name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Using existing module: {module.name}'))

                    # 3. Create permissions for each module
                    permission_types = ['view', 'add', 'edit', 'delete', 'print']

                    for perm_type in permission_types:
                        perm, created = AdminPermission.objects.get_or_create(
                            module=module,
                            permission_type=perm_type,
                            defaults={
                                'is_active': True
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created permission: {perm.permission_type} for {module.name}'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Using existing permission: {perm.permission_type} for {module.name}'))

                # 4. Create a default meetings group with all permissions
                meetings_group, created = Group.objects.get_or_create(
                    name='Meetings Staff',
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created meetings group: {meetings_group.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing meetings group: {meetings_group.name}'))

                # 5. Assign all meetings permissions to the meetings group
                all_meetings_permissions = AdminPermission.objects.filter(module__department=meetings_department)

                for perm in all_meetings_permissions:
                    perm.groups.add(meetings_group)

                self.stdout.write(self.style.SUCCESS(f'Assigned {all_meetings_permissions.count()} permissions to meetings group'))

                self.stdout.write(self.style.SUCCESS('Successfully created meetings permissions'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating meetings permissions: {str(e)}'))
