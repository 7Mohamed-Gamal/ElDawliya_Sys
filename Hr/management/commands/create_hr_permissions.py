from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from administrator.models import Department as AdminDepartment, Module, Permission as AdminPermission
from Hr.decorators import MODULES, DEPARTMENT_NAME

class Command(BaseCommand):
    help = 'Create HR permissions for all modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating HR permissions...'))

        try:
            with transaction.atomic():
                # 1. Create or get the HR department
                hr_department, created = AdminDepartment.objects.get_or_create(
                    name=DEPARTMENT_NAME,
                    defaults={
                        'description': 'قسم الموارد البشرية',
                        'icon': 'fas fa-user-tie',
                        'url_name': 'hr',
                        'order': 1,
                        'is_active': True,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created HR department: {hr_department.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing HR department: {hr_department.name}'))

                # 2. Create modules for each module in MODULES
                for module_key, module_name in MODULES.items():
                    module, created = Module.objects.get_or_create(
                        department=hr_department,
                        name=module_name,
                        defaults={
                            'description': f'وحدة {module_name}',
                            'url': f'/hr/{module_key}/',
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

                # 4. Create a default HR group with all permissions
                hr_group, created = Group.objects.get_or_create(
                    name='HR Staff',
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created HR group: {hr_group.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing HR group: {hr_group.name}'))

                # 5. Assign all HR permissions to the HR group
                all_hr_permissions = AdminPermission.objects.filter(module__department=hr_department)

                for perm in all_hr_permissions:
                    perm.groups.add(hr_group)

                self.stdout.write(self.style.SUCCESS(f'Assigned {all_hr_permissions.count()} permissions to HR group'))

                self.stdout.write(self.style.SUCCESS('Successfully created HR permissions'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating HR permissions: {str(e)}'))
