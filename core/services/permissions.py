"""
خدمة الصلاحيات والأدوار
Permissions and Roles Service
"""
from django.contrib.auth.models import User
from django.db.models import Q
from core.models.permissions import Module, Permission, Role, UserRole, ObjectPermission
from .base import BaseService


class PermissionService(BaseService):
    """
    خدمة إدارة الصلاحيات والأدوار
    Service for managing permissions and roles
    """
    
    def create_module(self, data):
        """
        إنشاء وحدة جديدة
        Create a new system module
        """
        self.check_permission('core.add_module')
        
        required_fields = ['name', 'display_name']
        self.validate_required_fields(data, required_fields)
        
        try:
            module = Module.objects.create(
                **data,
                created_by=self.user,
                updated_by=self.user
            )
            
            self.log_action(
                action='create',
                resource='module',
                content_object=module,
                new_values=data,
                message=f'تم إنشاء وحدة جديدة: {module.display_name}'
            )
            
            return self.format_response(
                data=module,
                message='تم إنشاء الوحدة بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'create', 'module', data)
    
    def create_permission(self, data):
        """
        إنشاء صلاحية جديدة
        Create a new permission
        """
        self.check_permission('core.add_permission')
        
        required_fields = ['module_id', 'permission_type', 'codename', 'name']
        self.validate_required_fields(data, required_fields)
        
        try:
            # Get module
            module = Module.objects.get(id=data['module_id'])
            
            permission = Permission.objects.create(
                module=module,
                permission_type=data['permission_type'],
                codename=data['codename'],
                name=data['name'],
                description=data.get('description', ''),
                created_by=self.user,
                updated_by=self.user
            )
            
            self.log_action(
                action='create',
                resource='permission',
                content_object=permission,
                new_values=data,
                message=f'تم إنشاء صلاحية جديدة: {permission.name}'
            )
            
            return self.format_response(
                data=permission,
                message='تم إنشاء الصلاحية بنجاح'
            )
            
        except Module.DoesNotExist:
            return self.format_response(
                success=False,
                message='الوحدة المحددة غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'create', 'permission', data)
    
    def create_role(self, data):
        """
        إنشاء دور جديد
        Create a new role
        """
        self.check_permission('core.add_role')
        
        required_fields = ['name', 'display_name']
        self.validate_required_fields(data, required_fields)
        
        try:
            permissions = data.pop('permissions', [])
            
            role = Role.objects.create(
                **data,
                created_by=self.user,
                updated_by=self.user
            )
            
            # Add permissions to role
            if permissions:
                role.permissions.set(permissions)
            
            self.log_action(
                action='create',
                resource='role',
                content_object=role,
                new_values=data,
                message=f'تم إنشاء دور جديد: {role.display_name}'
            )
            
            return self.format_response(
                data=role,
                message='تم إنشاء الدور بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'create', 'role', data)
    
    def assign_role_to_user(self, user_id, role_id, expires_at=None, reason=None):
        """
        تعيين دور لمستخدم
        Assign role to user
        """
        self.check_permission('core.add_userrole')
        
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            
            # Check if assignment already exists
            existing = UserRole.objects.filter(
                user=user,
                role=role,
                is_active=True,
                revoked_at__isnull=True
            ).first()
            
            if existing:
                return self.format_response(
                    success=False,
                    message='المستخدم لديه هذا الدور بالفعل'
                )
            
            user_role = UserRole.objects.create(
                user=user,
                role=role,
                granted_by=self.user,
                expires_at=expires_at,
                reason=reason,
                created_by=self.user,
                updated_by=self.user
            )
            
            self.log_action(
                action='create',
                resource='user_role_assignment',
                content_object=user_role,
                details={
                    'user_id': user_id,
                    'role_id': role_id,
                    'expires_at': expires_at.isoformat() if expires_at else None,
                    'reason': reason
                },
                message=f'تم تعيين دور {role.display_name} للمستخدم {user.username}'
            )
            
            return self.format_response(
                data=user_role,
                message='تم تعيين الدور بنجاح'
            )
            
        except User.DoesNotExist:
            return self.format_response(
                success=False,
                message='المستخدم غير موجود'
            )
        except Role.DoesNotExist:
            return self.format_response(
                success=False,
                message='الدور غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'assign_role', 'user_role', {
                'user_id': user_id,
                'role_id': role_id
            })
    
    def revoke_user_role(self, user_role_id, reason=None):
        """
        إلغاء دور المستخدم
        Revoke user role assignment
        """
        self.check_permission('core.change_userrole')
        
        try:
            user_role = UserRole.objects.get(id=user_role_id)
            
            if user_role.is_revoked:
                return self.format_response(
                    success=False,
                    message='هذا الدور ملغي بالفعل'
                )
            
            user_role.revoke(revoked_by=self.user, reason=reason)
            
            self.log_action(
                action='update',
                resource='user_role_revocation',
                content_object=user_role,
                details={
                    'user_role_id': user_role_id,
                    'reason': reason
                },
                message=f'تم إلغاء دور {user_role.role.display_name} من المستخدم {user_role.user.username}'
            )
            
            return self.format_response(
                message='تم إلغاء الدور بنجاح'
            )
            
        except UserRole.DoesNotExist:
            return self.format_response(
                success=False,
                message='تعيين الدور غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'revoke_role', 'user_role', {
                'user_role_id': user_role_id
            })
    
    def get_user_permissions(self, user_id=None):
        """
        الحصول على صلاحيات المستخدم
        Get user permissions from roles and direct assignments
        """
        user = User.objects.get(id=user_id) if user_id else self.user
        
        if not user:
            return []
        
        # Get permissions from active roles
        role_permissions = Permission.objects.filter(
            roles__user_assignments__user=user,
            roles__user_assignments__is_active=True,
            roles__user_assignments__revoked_at__isnull=True,
            roles__is_active=True,
            is_active=True
        ).distinct()
        
        # Get direct object permissions
        object_permissions = Permission.objects.filter(
            object_assignments__user=user,
            object_assignments__is_active=True,
            is_active=True
        ).distinct()
        
        # Combine and return unique permissions
        all_permissions = (role_permissions | object_permissions).distinct()
        
        return list(all_permissions.values(
            'id', 'module__name', 'permission_type', 'codename', 'name'
        ))
    
    def check_user_permission(self, user, permission_codename, module_name=None, obj=None):
        """
        فحص صلاحية المستخدم
        Check if user has specific permission
        """
        if user.is_superuser:
            return True
        
        # Check role-based permissions
        role_permission_exists = UserRole.objects.filter(
            user=user,
            is_active=True,
            revoked_at__isnull=True,
            role__is_active=True,
            role__permissions__codename=permission_codename,
            role__permissions__is_active=True
        )
        
        if module_name:
            role_permission_exists = role_permission_exists.filter(
                role__permissions__module__name=module_name
            )
        
        if role_permission_exists.exists():
            return True
        
        # Check object-level permissions if object is provided
        if obj:
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(obj)
            
            object_permission_exists = ObjectPermission.objects.filter(
                user=user,
                is_active=True,
                permission__codename=permission_codename,
                content_type=content_type,
                object_id=str(obj.pk)
            )
            
            if module_name:
                object_permission_exists = object_permission_exists.filter(
                    permission__module__name=module_name
                )
            
            return object_permission_exists.exists()
        
        return False
    
    def get_user_roles(self, user_id=None):
        """
        الحصول على أدوار المستخدم
        Get user active roles
        """
        user = User.objects.get(id=user_id) if user_id else self.user
        
        if not user:
            return []
        
        user_roles = UserRole.objects.filter(
            user=user,
            is_active=True,
            revoked_at__isnull=True
        ).select_related('role').order_by('role__level', 'role__display_name')
        
        return [{
            'id': ur.id,
            'role_id': ur.role.id,
            'role_name': ur.role.name,
            'role_display_name': ur.role.display_name,
            'granted_at': ur.granted_at,
            'expires_at': ur.expires_at,
            'is_expired': ur.is_expired,
        } for ur in user_roles]
    
    def get_modules_hierarchy(self):
        """
        الحصول على التسلسل الهرمي للوحدات
        Get modules hierarchy for permission management
        """
        modules = Module.objects.filter(is_active=True).order_by('order', 'display_name')
        
        # Build hierarchy
        module_dict = {}
        root_modules = []
        
        for module in modules:
            module_data = {
                'id': module.id,
                'name': module.name,
                'display_name': module.display_name,
                'description': module.description,
                'icon': module.icon,
                'order': module.order,
                'parent_id': module.parent_module_id,
                'children': [],
                'permissions': []
            }
            
            # Add permissions
            permissions = module.permissions.filter(is_active=True).order_by('permission_type', 'name')
            module_data['permissions'] = [{
                'id': p.id,
                'permission_type': p.permission_type,
                'codename': p.codename,
                'name': p.name,
                'description': p.description,
            } for p in permissions]
            
            module_dict[module.id] = module_data
            
            if not module.parent_module_id:
                root_modules.append(module_data)
        
        # Build children relationships
        for module_data in module_dict.values():
            if module_data['parent_id']:
                parent = module_dict.get(module_data['parent_id'])
                if parent:
                    parent['children'].append(module_data)
        
        return root_modules
    
    def setup_default_permissions(self):
        """
        إعداد الصلاحيات الافتراضية
        Setup default system permissions
        """
        self.check_permission('core.add_module')
        
        # Default modules and permissions
        default_setup = [
            {
                'module': {
                    'name': 'hr',
                    'display_name': 'الموارد البشرية',
                    'description': 'إدارة الموظفين والرواتب والحضور',
                    'icon': 'fas fa-users',
                    'order': 1
                },
                'permissions': [
                    {'type': 'view', 'name': 'عرض بيانات الموظفين'},
                    {'type': 'add', 'name': 'إضافة موظف جديد'},
                    {'type': 'change', 'name': 'تعديل بيانات الموظف'},
                    {'type': 'delete', 'name': 'حذف موظف'},
                    {'type': 'manage', 'name': 'إدارة كاملة للموارد البشرية'},
                ]
            },
            {
                'module': {
                    'name': 'inventory',
                    'display_name': 'المخزون',
                    'description': 'إدارة المخزون والمنتجات',
                    'icon': 'fas fa-boxes',
                    'order': 2
                },
                'permissions': [
                    {'type': 'view', 'name': 'عرض المخزون'},
                    {'type': 'add', 'name': 'إضافة منتج'},
                    {'type': 'change', 'name': 'تعديل المنتج'},
                    {'type': 'delete', 'name': 'حذف منتج'},
                    {'type': 'manage', 'name': 'إدارة كاملة للمخزون'},
                ]
            },
            # Add more modules as needed
        ]
        
        created_modules = []
        created_permissions = []
        
        for setup_data in default_setup:
            # Create module
            module_data = setup_data['module']
            module, created = Module.objects.get_or_create(
                name=module_data['name'],
                defaults={
                    **module_data,
                    'created_by': self.user,
                    'updated_by': self.user
                }
            )
            
            if created:
                created_modules.append(module)
            
            # Create permissions
            for perm_data in setup_data['permissions']:
                codename = f"{perm_data['type']}_{module.name}"
                permission, created = Permission.objects.get_or_create(
                    module=module,
                    codename=codename,
                    defaults={
                        'permission_type': perm_data['type'],
                        'name': perm_data['name'],
                        'created_by': self.user,
                        'updated_by': self.user
                    }
                )
                
                if created:
                    created_permissions.append(permission)
        
        self.log_action(
            action='create',
            resource='default_permissions_setup',
            details={
                'modules_created': len(created_modules),
                'permissions_created': len(created_permissions)
            },
            message='تم إعداد الصلاحيات الافتراضية'
        )
        
        return self.format_response(
            data={
                'modules_created': len(created_modules),
                'permissions_created': len(created_permissions)
            },
            message='تم إعداد الصلاحيات الافتراضية بنجاح'
        )