from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from administrator.models import Department, Module

class Command(BaseCommand):
    help = 'Initialize default departments, modules, and permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of departments even if they already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Check if departments already exist
        if Department.objects.exists() and not force:
            self.stdout.write(self.style.WARNING('Departments already exist. Use --force to recreate them.'))
            return
            
        # Create default groups if they don't exist
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        hr_group, _ = Group.objects.get_or_create(name='HR')
        warehouse_group, _ = Group.objects.get_or_create(name='Warehouse')
        meetings_group, _ = Group.objects.get_or_create(name='Meetings')
        
        # Default departments with their modules
        departments = [
            {
                'name': 'الموارد البشرية',
                'icon': 'fa-user-tie',
                'url_name': 'hr',
                'description': 'إدارة شؤون الموظفين',
                'order': 1,
                'groups': [admin_group, hr_group],
                'modules': [
                    {
                        'name': 'إدارة الموظفين',
                        'icon': 'fa-users',
                        'url': '/Hr/dashboard/',
                        'bg_color': '#ff6b6b',
                        'order': 1,
                    },
                    {
                        'name': 'سجل الموظفين',
                        'icon': 'fa-id-card',
                        'url': '/Hr/employees/',
                        'bg_color': '#ff6b6b',
                        'order': 2,
                    },
                    {
                        'name': 'بحث الموظفين',
                        'icon': 'fa-search',
                        'url': '/Hr/employees/search/',
                        'bg_color': '#ff6b6b',
                        'order': 3,
                    },
                ]
            },
            {
                'name': 'المخزن',
                'icon': 'fa-warehouse',
                'url_name': 'warehouse',
                'description': 'إدارة مخزن قطع الغيار',
                'order': 2,
                'groups': [admin_group, warehouse_group],
                'modules': [
                    {
                        'name': 'لوحة تحكم المخزن',
                        'icon': 'fa-tachometer-alt',
                        'url': '/inventory/dashboard/',
                        'bg_color': '#1abc9c',
                        'order': 1,
                    },
                    {
                        'name': 'قطع الغيار',
                        'icon': 'fa-box',
                        'url': '/inventory/products/',
                        'bg_color': '#1abc9c',
                        'order': 2,
                    },
                    {
                        'name': 'الفواتير',
                        'icon': 'fa-file-invoice',
                        'url': '/inventory/invoices/',
                        'bg_color': '#1abc9c',
                        'order': 3,
                    },
                ]
            },
            {
                'name': 'الاجتماعات',
                'icon': 'fa-handshake',
                'url_name': 'meetings',
                'description': 'إدارة الاجتماعات',
                'order': 3,
                'groups': [admin_group, meetings_group],
                'modules': [
                    {
                        'name': 'قائمة الاجتماعات',
                        'icon': 'fa-calendar-alt',
                        'url': '/meetings/list/',
                        'bg_color': '#f1c40f',
                        'order': 1,
                    },
                    {
                        'name': 'إنشاء اجتماع',
                        'icon': 'fa-plus',
                        'url': '/meetings/create/',
                        'bg_color': '#f1c40f',
                        'order': 2,
                    },
                ]
            },
            {
                'name': 'المهام',
                'icon': 'fa-tasks',
                'url_name': 'tasks',
                'description': 'إدارة المهام',
                'order': 4,
                'groups': [admin_group, hr_group, warehouse_group, meetings_group],
                'modules': [
                    {
                        'name': 'قائمة المهام',
                        'icon': 'fa-tasks',
                        'url': '/tasks/list/',
                        'bg_color': '#e67e22',
                        'order': 1,
                    },
                ]
            },
            {
                'name': 'مدير النظام',
                'icon': 'fa-cogs',
                'url_name': 'sysadmin',
                'description': 'إدارة النظام والصلاحيات',
                'require_admin': True,
                'order': 100,
                'groups': [admin_group],
                'modules': [
                    {
                        'name': 'لوحة تحكم مدير النظام',
                        'icon': 'fa-cogs',
                        'url': '/administrator/admin_dashboard/',
                        'bg_color': '#3f51b5',
                        'order': 1,
                        'require_admin': True,
                    },
                    {
                        'name': 'إدارة الأقسام',
                        'icon': 'fa-building',
                        'url': '/administrator/departments/',
                        'bg_color': '#3f51b5',
                        'order': 2,
                        'require_admin': True,
                    },
                    {
                        'name': 'إعدادات النظام',
                        'icon': 'fa-sliders-h',
                        'url': '/administrator/settings/',
                        'bg_color': '#3f51b5',
                        'order': 3,
                        'require_admin': True,
                    },
                ]
            },
        ]
        
        # Clear existing departments if using --force
        if force:
            Department.objects.all().delete()
        
        # Create departments with their modules
        for dept_data in departments:
            groups = dept_data.pop('groups', [])
            modules_data = dept_data.pop('modules', [])
            
            # Create department
            dept = Department.objects.create(**dept_data)
            
            # Add groups to department
            for group in groups:
                dept.groups.add(group)
                
            # Create modules for department
            for module_data in modules_data:
                module = Module.objects.create(department=dept, **module_data)
                
                # Add same groups as department to module
                for group in groups:
                    module.groups.add(group)
            
            self.stdout.write(self.style.SUCCESS(f'Created department: {dept.name} with {len(modules_data)} modules'))
            
        self.stdout.write(self.style.SUCCESS('Successfully initialized departments'))
