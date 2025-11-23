"""
Management command to set up hierarchical permissions system
أمر إدارة لإعداد نظام الصلاحيات الهرمي
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from core.models.permissions import Module, Permission, Role, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up hierarchical permissions system with default modules, permissions, and roles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing permissions and recreate them',
        )
        parser.add_argument(
            '--create-admin-role',
            action='store_true',
            help='Create admin role and assign to superusers',
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('بدء إعداد نظام الصلاحيات الهرمي...')
        )
        
        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_permissions()
                
                self.create_modules()
                self.create_permissions()
                self.create_default_roles()
                
                if options['create_admin_role']:
                    self.create_admin_role()
                
                self.stdout.write(
                    self.style.SUCCESS('تم إعداد نظام الصلاحيات الهرمي بنجاح!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في إعداد نظام الصلاحيات: {e}')
            )
            raise CommandError(f'Failed to setup permissions: {e}')
    
    def reset_permissions(self):
        """Reset existing permissions"""
        self.stdout.write('إعادة تعيين الصلاحيات الموجودة...')
        
        UserRole.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()
        Module.objects.all().delete()
        
        self.stdout.write(self.style.WARNING('تم حذف جميع الصلاحيات الموجودة'))
    
    def create_modules(self):
        """Create system modules"""
        self.stdout.write('إنشاء وحدات النظام...')
        
        modules_data = [
            # Core modules
            {
                'name': 'administration',
                'display_name': 'الإدارة العامة',
                'description': 'إدارة النظام والمستخدمين والإعدادات',
                'icon': 'fas fa-cogs',
                'order': 1
            },
            {
                'name': 'hr',
                'display_name': 'الموارد البشرية',
                'description': 'إدارة الموظفين والرواتب والحضور',
                'icon': 'fas fa-users',
                'order': 2
            },
            {
                'name': 'inventory',
                'display_name': 'إدارة المخزون',
                'description': 'إدارة المنتجات والمخزون والموردين',
                'icon': 'fas fa-boxes',
                'order': 3
            },
            {
                'name': 'procurement',
                'display_name': 'المشتريات',
                'description': 'إدارة أوامر الشراء والعقود',
                'icon': 'fas fa-shopping-cart',
                'order': 4
            },
            {
                'name': 'projects',
                'display_name': 'إدارة المشاريع',
                'description': 'إدارة المشاريع والمهام والاجتماعات',
                'icon': 'fas fa-project-diagram',
                'order': 5
            },
            {
                'name': 'finance',
                'display_name': 'المالية',
                'description': 'إدارة الحسابات والميزانيات والتقارير المالية',
                'icon': 'fas fa-chart-line',
                'order': 6
            },
            {
                'name': 'reports',
                'display_name': 'التقارير',
                'description': 'إنشاء وعرض التقارير والإحصائيات',
                'icon': 'fas fa-chart-bar',
                'order': 7
            },
            {
                'name': 'api',
                'display_name': 'واجهة برمجة التطبيقات',
                'description': 'الوصول لواجهات برمجة التطبيقات',
                'icon': 'fas fa-code',
                'order': 8
            }
        ]
        
        # Create main modules
        created_modules = {}
        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                name=module_data['name'],
                defaults=module_data
            )
            created_modules[module.name] = module
            
            if created:
                self.stdout.write(f'  ✓ تم إنشاء وحدة: {module.display_name}')
            else:
                self.stdout.write(f'  - وحدة موجودة: {module.display_name}')
        
        # Create sub-modules for HR
        hr_submodules = [
            {
                'name': 'hr_employees',
                'display_name': 'الموظفين',
                'description': 'إدارة بيانات الموظفين',
                'parent': created_modules['hr'],
                'order': 1
            },
            {
                'name': 'hr_attendance',
                'display_name': 'الحضور والانصراف',
                'description': 'تتبع حضور الموظفين',
                'parent': created_modules['hr'],
                'order': 2
            },
            {
                'name': 'hr_payroll',
                'display_name': 'الرواتب',
                'description': 'إدارة رواتب الموظفين',
                'parent': created_modules['hr'],
                'order': 3
            },
            {
                'name': 'hr_leaves',
                'display_name': 'الإجازات',
                'description': 'إدارة إجازات الموظفين',
                'parent': created_modules['hr'],
                'order': 4
            },
            {
                'name': 'hr_evaluations',
                'display_name': 'التقييمات',
                'description': 'تقييم أداء الموظفين',
                'parent': created_modules['hr'],
                'order': 5
            }
        ]
        
        for submodule_data in hr_submodules:
            submodule, created = Module.objects.get_or_create(
                name=submodule_data['name'],
                defaults=submodule_data
            )
            if created:
                self.stdout.write(f'    ✓ تم إنشاء وحدة فرعية: {submodule.display_name}')
    
    def create_permissions(self):
        """Create permissions for modules"""
        self.stdout.write('إنشاء الصلاحيات...')
        
        # Standard permission types
        standard_permissions = [
            ('view', 'عرض', 'global', False),
            ('add', 'إضافة', 'global', False),
            ('change', 'تعديل', 'global', False),
            ('delete', 'حذف', 'global', True),
            ('export', 'تصدير', 'global', False),
            ('import', 'استيراد', 'global', True),
            ('print', 'طباعة', 'global', False),
        ]
        
        # Special permissions for specific modules
        special_permissions = {
            'administration': [
                ('manage_users', 'إدارة المستخدمين', 'global', True),
                ('manage_roles', 'إدارة الأدوار', 'global', True),
                ('manage_permissions', 'إدارة الصلاحيات', 'global', True),
                ('system_config', 'تكوين النظام', 'global', True),
                ('view_audit_logs', 'عرض سجلات التدقيق', 'global', True),
            ],
            'hr': [
                ('approve_leave', 'موافقة الإجازات', 'department', True),
                ('calculate_salary', 'حساب الرواتب', 'department', True),
                ('view_salary_reports', 'عرض تقارير الرواتب', 'department', True),
                ('manage_attendance', 'إدارة الحضور', 'department', False),
            ],
            'inventory': [
                ('approve_orders', 'موافقة الطلبات', 'global', True),
                ('adjust_stock', 'تعديل المخزون', 'global', True),
                ('view_cost_reports', 'عرض تقارير التكلفة', 'global', True),
            ],
            'procurement': [
                ('approve_purchase', 'موافقة الشراء', 'global', True),
                ('create_contracts', 'إنشاء العقود', 'global', True),
                ('manage_suppliers', 'إدارة الموردين', 'global', False),
            ],
            'projects': [
                ('manage_projects', 'إدارة المشاريع', 'team', False),
                ('assign_tasks', 'تعيين المهام', 'team', False),
                ('view_time_reports', 'عرض تقارير الوقت', 'team', False),
            ],
            'finance': [
                ('approve_budgets', 'موافقة الميزانيات', 'global', True),
                ('view_financial_reports', 'عرض التقارير المالية', 'global', True),
                ('manage_accounts', 'إدارة الحسابات', 'global', True),
            ],
            'reports': [
                ('create_reports', 'إنشاء التقارير', 'global', False),
                ('schedule_reports', 'جدولة التقارير', 'global', False),
                ('share_reports', 'مشاركة التقارير', 'global', False),
            ],
            'api': [
                ('access_api', 'الوصول للـ API', 'global', False),
                ('manage_api_keys', 'إدارة مفاتيح API', 'global', True),
                ('view_api_logs', 'عرض سجلات API', 'global', True),
            ]
        }
        
        # Create standard permissions for all modules
        modules = Module.objects.filter(parent__isnull=True)  # Only main modules
        
        for module in modules:
            for perm_code, perm_name, scope, is_sensitive in standard_permissions:
                permission, created = Permission.objects.get_or_create(
                    module=module,
                    codename=perm_code,
                    defaults={
                        'permission_type': perm_code,
                        'name': f'{perm_name} {module.display_name}',
                        'description': f'{perm_name} في وحدة {module.display_name}',
                        'scope': scope,
                        'is_sensitive': is_sensitive
                    }
                )
                
                if created:
                    self.stdout.write(f'  ✓ {permission.name}')
        
        # Create special permissions
        for module_name, permissions in special_permissions.items():
            try:
                module = Module.objects.get(name=module_name)
                
                for perm_code, perm_name, scope, is_sensitive in permissions:
                    permission, created = Permission.objects.get_or_create(
                        module=module,
                        codename=perm_code,
                        defaults={
                            'permission_type': 'manage' if 'manage' in perm_code else 'approve' if 'approve' in perm_code else 'view',
                            'name': perm_name,
                            'description': f'{perm_name} في وحدة {module.display_name}',
                            'scope': scope,
                            'is_sensitive': is_sensitive,
                            'requires_approval': is_sensitive
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'  ✓ {permission.name}')
                        
            except Module.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'وحدة غير موجودة: {module_name}')
                )
    
    def create_default_roles(self):
        """Create default system roles"""
        self.stdout.write('إنشاء الأدوار الافتراضية...')
        
        roles_data = [
            {
                'name': 'system_admin',
                'display_name': 'مدير النظام',
                'description': 'مدير النظام مع جميع الصلاحيات',
                'role_type': 'system',
                'is_system_role': True,
                'permissions': 'all'
            },
            {
                'name': 'hr_manager',
                'display_name': 'مدير الموارد البشرية',
                'description': 'مدير الموارد البشرية مع صلاحيات كاملة في HR',
                'role_type': 'department',
                'permissions': ['hr.*', 'reports.view', 'reports.create_reports']
            },
            {
                'name': 'hr_employee',
                'display_name': 'موظف الموارد البشرية',
                'description': 'موظف في قسم الموارد البشرية',
                'role_type': 'department',
                'permissions': ['hr.view', 'hr.add', 'hr.change', 'hr_employees.view', 'hr_attendance.view']
            },
            {
                'name': 'inventory_manager',
                'display_name': 'مدير المخزون',
                'description': 'مدير المخزون مع صلاحيات كاملة',
                'role_type': 'department',
                'permissions': ['inventory.*', 'procurement.view', 'reports.view']
            },
            {
                'name': 'project_manager',
                'display_name': 'مدير المشاريع',
                'description': 'مدير المشاريع والمهام',
                'role_type': 'department',
                'permissions': ['projects.*', 'reports.view', 'reports.create_reports']
            },
            {
                'name': 'employee',
                'display_name': 'موظف',
                'description': 'موظف عادي مع صلاحيات أساسية',
                'role_type': 'custom',
                'permissions': ['projects.view', 'hr_attendance.view', 'reports.view']
            },
            {
                'name': 'api_user',
                'display_name': 'مستخدم API',
                'description': 'مستخدم لديه صلاحية الوصول للـ API',
                'role_type': 'custom',
                'permissions': ['api.access_api']
            }
        ]
        
        for role_data in roles_data:
            permissions_list = role_data.pop('permissions')
            
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if created or not role.permissions.exists():
                # Assign permissions
                if permissions_list == 'all':
                    # Assign all permissions
                    all_permissions = Permission.objects.filter(is_active=True)
                    role.permissions.set(all_permissions)
                else:
                    # Assign specific permissions
                    permissions_to_assign = []
                    
                    for perm_pattern in permissions_list:
                        if '.*' in perm_pattern:
                            # Module wildcard
                            module_name = perm_pattern.replace('.*', '')
                            module_permissions = Permission.objects.filter(
                                module__name=module_name,
                                is_active=True
                            )
                            permissions_to_assign.extend(module_permissions)
                        else:
                            # Specific permission
                            if '.' in perm_pattern:
                                module_name, perm_code = perm_pattern.split('.', 1)
                                try:
                                    permission = Permission.objects.get(
                                        module__name=module_name,
                                        codename=perm_code,
                                        is_active=True
                                    )
                                    permissions_to_assign.append(permission)
                                except Permission.DoesNotExist:
                                    self.stdout.write(
                                        self.style.WARNING(f'صلاحية غير موجودة: {perm_pattern}')
                                    )
                    
                    role.permissions.set(permissions_to_assign)
                
                if created:
                    self.stdout.write(f'  ✓ تم إنشاء دور: {role.display_name}')
                else:
                    self.stdout.write(f'  ↻ تم تحديث صلاحيات دور: {role.display_name}')
    
    def create_admin_role(self):
        """Create admin role and assign to superusers"""
        self.stdout.write('تعيين دور المدير للمستخدمين المديرين...')
        
        try:
            admin_role = Role.objects.get(name='system_admin')
            superusers = User.objects.filter(is_superuser=True, is_active=True)
            
            for user in superusers:
                user_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role=admin_role,
                    defaults={
                        'granted_by': user,  # Self-assigned for superusers
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  ✓ تم تعيين دور المدير للمستخدم: {user.username}')
                else:
                    self.stdout.write(f'  - دور موجود للمستخدم: {user.username}')
                    
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('دور المدير غير موجود. تأكد من إنشاء الأدوار أولاً.')
            )