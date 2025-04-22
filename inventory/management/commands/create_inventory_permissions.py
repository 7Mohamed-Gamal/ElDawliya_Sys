from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import transaction

from administrator.models import Department as AdminDepartment, Module, Permission as AdminPermission
from inventory.decorators import MODULES, DEPARTMENT_NAME

class Command(BaseCommand):
    help = 'Create inventory permissions for all modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating inventory permissions...'))
        
        try:
            with transaction.atomic():
                # 1. Create or get the inventory department
                inventory_department, created = AdminDepartment.objects.get_or_create(
                    name=DEPARTMENT_NAME,
                    defaults={
                        'description': 'قسم مخزن قطع الغيار',
                        'icon': 'fas fa-warehouse',
                        'url_name': 'inventory',
                        'order': 2,
                        'is_active': True,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created inventory department: {inventory_department.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing inventory department: {inventory_department.name}'))
                
                # 2. Create modules for each module in MODULES
                for module_key, module_name in MODULES.items():
                    module, created = Module.objects.get_or_create(
                        department=inventory_department,
                        name=module_name,
                        defaults={
                            'description': f'وحدة {module_name}',
                            'url': f'/inventory/{module_key}/',
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
                
                # 4. Create a default inventory group with all permissions
                inventory_group, created = Group.objects.get_or_create(
                    name='Inventory Staff',
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created inventory group: {inventory_group.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing inventory group: {inventory_group.name}'))
                
                # 5. Assign all inventory permissions to the inventory group
                all_inventory_permissions = AdminPermission.objects.filter(module__department=inventory_department)
                
                for perm in all_inventory_permissions:
                    perm.groups.add(inventory_group)
                
                self.stdout.write(self.style.SUCCESS(f'Assigned {all_inventory_permissions.count()} permissions to inventory group'))
                
                self.stdout.write(self.style.SUCCESS('Successfully created inventory permissions'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating inventory permissions: {str(e)}'))
