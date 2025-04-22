from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import transaction

from administrator.models import Department as AdminDepartment, Module, Permission as AdminPermission
from Purchase_orders.decorators import MODULES, DEPARTMENT_NAME

class Command(BaseCommand):
    help = 'Create purchase permissions for all modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating purchase permissions...'))
        
        try:
            with transaction.atomic():
                # 1. Create or get the purchase department
                purchase_department, created = AdminDepartment.objects.get_or_create(
                    name=DEPARTMENT_NAME,
                    defaults={
                        'description': 'قسم طلبات الشراء',
                        'icon': 'fas fa-shopping-cart',
                        'url_name': 'purchase_orders',
                        'order': 4,
                        'is_active': True,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created purchase department: {purchase_department.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing purchase department: {purchase_department.name}'))
                
                # 2. Create modules for each module in MODULES
                for module_key, module_name in MODULES.items():
                    module, created = Module.objects.get_or_create(
                        department=purchase_department,
                        name=module_name,
                        defaults={
                            'description': f'وحدة {module_name}',
                            'url': f'/purchase/{module_key}/',
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
                
                # 4. Create a default purchase group with all permissions
                purchase_group, created = Group.objects.get_or_create(
                    name='Purchase Staff',
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created purchase group: {purchase_group.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing purchase group: {purchase_group.name}'))
                
                # 5. Assign all purchase permissions to the purchase group
                all_purchase_permissions = AdminPermission.objects.filter(module__department=purchase_department)
                
                for perm in all_purchase_permissions:
                    perm.groups.add(purchase_group)
                
                self.stdout.write(self.style.SUCCESS(f'Assigned {all_purchase_permissions.count()} permissions to purchase group'))
                
                self.stdout.write(self.style.SUCCESS('Successfully created purchase permissions'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating purchase permissions: {str(e)}'))
