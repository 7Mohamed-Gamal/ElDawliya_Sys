"""
Hierarchical Permission Service
خدمة الصلاحيات الهرمية

This service provides comprehensive permission checking and management
for the hierarchical permissions system.
"""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Set, Any, Union
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from ..models.permissions import (
    Module, Permission, Role, UserRole, ObjectPermission,
    ApprovalWorkflow, ApprovalStep, PermissionCache
)

User = get_user_model()
logger = logging.getLogger(__name__)


class HierarchicalPermissionService:
    """
    Service for managing hierarchical permissions
    خدمة إدارة الصلاحيات الهرمية
    """
    
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.cache_timeout = getattr(settings, 'PERMISSION_CACHE_TIMEOUT', 3600)  # 1 hour
        self.enable_caching = getattr(settings, 'ENABLE_PERMISSION_CACHING', True)
    
    def has_permission(self, permission_codename: str, obj: Any = None) -> bool:
        """
        Check if user has a specific permission
        التحقق من وجود صلاحية معينة للمستخدم
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if self.user.is_superuser:
            return True
        
        # Check object-level permission first if object is provided
        if obj is not None:
            if self._has_object_permission(permission_codename, obj):
                return True
        
        # Check role-based permissions
        return self._has_role_permission(permission_codename)
    
    def has_module_permission(self, module_name: str, action: str, obj: Any = None) -> bool:
        """
        Check if user has permission for a module action
        التحقق من صلاحية المستخدم لإجراء في وحدة
        """
        permission_codename = f"{module_name}.{action}"
        return self.has_permission(permission_codename, obj)
    
    def _has_role_permission(self, permission_codename: str) -> bool:
        """
        Check role-based permissions with caching
        التحقق من الصلاحيات القائمة على الأدوار مع التخزين المؤقت
        """
        if not self.enable_caching:
            return self._compute_role_permission(permission_codename)
        
        # Generate cache key
        cache_key = f"user_permission_{self.user.id}_{permission_codename}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Compute permission
        has_perm = self._compute_role_permission(permission_codename)
        
        # Cache result
        cache.set(cache_key, has_perm, self.cache_timeout)
        
        return has_perm
    
    def _compute_role_permission(self, permission_codename: str) -> bool:
        """
        Compute role-based permission
        حساب الصلاحية القائمة على الأدوار
        """
        try:
            # Parse permission codename
            if '.' not in permission_codename:
                return False
            
            module_name, action = permission_codename.split('.', 1)
            
            # Get module
            try:
                module = Module.objects.get(name=module_name, is_active=True)
            except Module.DoesNotExist:
                return False
            
            # Get permission
            try:
                permission = Permission.objects.get(
                    module=module,
                    codename=action,
                    is_active=True
                )
            except Permission.DoesNotExist:
                return False
            
            # Get user's active roles
            user_roles = UserRole.objects.filter(
                user=self.user,
                is_active=True,
                role__is_active=True
            ).select_related('role')
            
            # Check if any role has the permission
            for user_role in user_roles:
                if user_role.is_valid():
                    role_permissions = user_role.role.get_all_permissions()
                    if permission in role_permissions:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error computing role permission {permission_codename}: {e}")
            return False
    
    def _has_object_permission(self, permission_codename: str, obj: Any) -> bool:
        """
        Check object-level permissions
        التحقق من الصلاحيات على مستوى الكائن
        """
        try:
            # Parse permission codename
            if '.' not in permission_codename:
                return False
            
            module_name, action = permission_codename.split('.', 1)
            
            # Get content type for the object
            content_type = ContentType.objects.get_for_model(obj)
            
            # Get permission
            try:
                module = Module.objects.get(name=module_name, is_active=True)
                permission = Permission.objects.get(
                    module=module,
                    codename=action,
                    is_active=True
                )
            except (Module.DoesNotExist, Permission.DoesNotExist):
                return False
            
            # Check object permission
            object_permission = ObjectPermission.objects.filter(
                user=self.user,
                permission=permission,
                content_type=content_type,
                object_id=str(obj.pk),
                is_active=True
            ).first()
            
            if object_permission and object_permission.is_valid():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking object permission {permission_codename}: {e}")
            return False
    
    def get_user_permissions(self) -> Dict[str, Dict[str, bool]]:
        """
        Get comprehensive summary of user permissions
        جلب ملخص شامل لصلاحيات المستخدم
        """
        if not self.user or not self.user.is_authenticated:
            return {}
        
        # Generate cache key
        permissions_hash = self._generate_permissions_hash()
        
        if self.enable_caching:
            # Try to get from cache
            cached_permissions = PermissionCache.get_user_permissions(
                self.user, permissions_hash
            )
            if cached_permissions:
                return cached_permissions
        
        # Compute permissions
        permissions = self._compute_user_permissions()
        
        if self.enable_caching:
            # Cache the result
            PermissionCache.set_user_permissions(
                self.user, permissions_hash, permissions, self.cache_timeout
            )
        
        return permissions
    
    def _compute_user_permissions(self) -> Dict[str, Dict[str, bool]]:
        """
        Compute all user permissions
        حساب جميع صلاحيات المستخدم
        """
        permissions = {}
        
        # Get all active modules
        modules = Module.objects.filter(is_active=True).prefetch_related('permissions')
        
        for module in modules:
            module_permissions = {}
            
            for permission in module.permissions.filter(is_active=True):
                module_permissions[permission.codename] = self.has_permission(
                    permission.full_codename
                )
            
            permissions[module.name] = module_permissions
        
        return permissions
    
    def _generate_permissions_hash(self) -> str:
        """
        Generate hash for user's current permission state
        توليد هاش لحالة صلاحيات المستخدم الحالية
        """
        # Get user's role assignments with timestamps
        user_roles = UserRole.objects.filter(
            user=self.user,
            is_active=True
        ).values('role_id', 'granted_at', 'expires_at')
        
        # Create hash input
        hash_input = {
            'user_id': self.user.id,
            'is_superuser': self.user.is_superuser,
            'is_staff': self.user.is_staff,
            'roles': list(user_roles),
            'timestamp': timezone.now().strftime('%Y-%m-%d-%H')  # Hour-level granularity
        }
        
        # Generate hash
        hash_string = json.dumps(hash_input, sort_keys=True, default=str)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def assign_role(self, target_user: User, role: Role, expires_at: Optional[timezone.datetime] = None, 
                   notes: str = '') -> UserRole:
        """
        Assign role to user with approval workflow if needed
        تعيين دور للمستخدم مع سير عمل الموافقة إذا لزم الأمر
        """
        # Check if role assignment requires approval
        if role.is_system_role or role.role_type == 'system':
            return self._create_approval_workflow_for_role_assignment(
                target_user, role, expires_at, notes
            )
        
        # Direct assignment
        return self._assign_role_direct(target_user, role, expires_at, notes)
    
    def _assign_role_direct(self, target_user: User, role: Role, expires_at: Optional[timezone.datetime] = None,
                           notes: str = '') -> UserRole:
        """
        Directly assign role to user
        تعيين الدور مباشرة للمستخدم
        """
        with transaction.atomic():
            # Check if role can accept more users
            if not role.can_assign_more_users():
                raise ValueError(f"Role {role.name} has reached maximum user limit")
            
            # Create or update user role
            user_role, created = UserRole.objects.update_or_create(
                user=target_user,
                role=role,
                defaults={
                    'granted_by': self.user,
                    'expires_at': expires_at,
                    'is_active': True,
                    'notes': notes
                }
            )
            
            # Invalidate permission cache
            self._invalidate_user_cache(target_user)
            
            # Log the assignment
            logger.info(f"Role {role.name} assigned to user {target_user.username} by {self.user.username}")
            
            return user_role
    
    def _create_approval_workflow_for_role_assignment(self, target_user: User, role: Role,
                                                    expires_at: Optional[timezone.datetime] = None,
                                                    notes: str = '') -> ApprovalWorkflow:
        """
        Create approval workflow for role assignment
        إنشاء سير عمل الموافقة لتعيين الدور
        """
        workflow_data = {
            'target_user_id': target_user.id,
            'role_id': role.id,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'notes': notes
        }
        
        workflow = ApprovalWorkflow.objects.create(
            workflow_type='role_assignment',
            title=f"تعيين دور {role.display_name} للمستخدم {target_user.username}",
            description=f"طلب تعيين دور {role.display_name} للمستخدم {target_user.username}",
            requested_by=self.user,
            target_user=target_user,
            data=workflow_data
        )
        
        # Create approval steps based on role sensitivity
        self._create_approval_steps_for_role(workflow, role)
        
        return workflow
    
    def _create_approval_steps_for_role(self, workflow: ApprovalWorkflow, role: Role):
        """
        Create approval steps based on role requirements
        إنشاء خطوات الموافقة بناءً على متطلبات الدور
        """
        # For system roles, require admin approval
        if role.is_system_role:
            admin_users = User.objects.filter(is_superuser=True, is_active=True)
            
            step = ApprovalStep.objects.create(
                workflow=workflow,
                level=1,
                name="موافقة المدير العام",
                requires_all=False
            )
            step.approvers.set(admin_users)
        
        # For department roles, require department head approval
        elif role.role_type == 'department':
            # This would need to be implemented based on your department structure
            pass
    
    def grant_object_permission(self, target_user: User, permission: Permission, obj: Any,
                              expires_at: Optional[timezone.datetime] = None) -> ObjectPermission:
        """
        Grant object-level permission to user
        منح صلاحية على مستوى الكائن للمستخدم
        """
        content_type = ContentType.objects.get_for_model(obj)
        
        with transaction.atomic():
            object_permission, created = ObjectPermission.objects.update_or_create(
                user=target_user,
                permission=permission,
                content_type=content_type,
                object_id=str(obj.pk),
                defaults={
                    'granted_by': self.user,
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            
            # Invalidate permission cache
            self._invalidate_user_cache(target_user)
            
            logger.info(f"Object permission {permission.name} granted to user {target_user.username}")
            
            return object_permission
    
    def revoke_role(self, target_user: User, role: Role) -> bool:
        """
        Revoke role from user
        إلغاء دور من المستخدم
        """
        try:
            user_role = UserRole.objects.get(
                user=target_user,
                role=role,
                is_active=True
            )
            
            user_role.is_active = False
            user_role.save()
            
            # Invalidate permission cache
            self._invalidate_user_cache(target_user)
            
            logger.info(f"Role {role.name} revoked from user {target_user.username} by {self.user.username}")
            
            return True
            
        except UserRole.DoesNotExist:
            return False
    
    def revoke_object_permission(self, target_user: User, permission: Permission, obj: Any) -> bool:
        """
        Revoke object-level permission from user
        إلغاء صلاحية على مستوى الكائن من المستخدم
        """
        try:
            content_type = ContentType.objects.get_for_model(obj)
            
            object_permission = ObjectPermission.objects.get(
                user=target_user,
                permission=permission,
                content_type=content_type,
                object_id=str(obj.pk),
                is_active=True
            )
            
            object_permission.is_active = False
            object_permission.save()
            
            # Invalidate permission cache
            self._invalidate_user_cache(target_user)
            
            logger.info(f"Object permission {permission.name} revoked from user {target_user.username}")
            
            return True
            
        except ObjectPermission.DoesNotExist:
            return False
    
    def _invalidate_user_cache(self, user: User):
        """
        Invalidate all cached permissions for a user
        إلغاء صحة جميع الصلاحيات المخزنة مؤقتاً للمستخدم
        """
        if self.enable_caching:
            # Clear Django cache
            cache_pattern = f"user_permission_{user.id}_*"
            # Note: This is a simplified implementation
            # In production, you might want to use Redis pattern matching
            
            # Clear permission cache entries
            PermissionCache.objects.filter(user=user).delete()
    
    def get_user_roles(self, include_expired: bool = False) -> List[UserRole]:
        """
        Get user's assigned roles
        جلب الأدوار المعينة للمستخدم
        """
        if not self.user:
            return []
        
        queryset = UserRole.objects.filter(user=self.user).select_related('role')
        
        if not include_expired:
            queryset = queryset.filter(is_active=True)
        
        return list(queryset)
    
    def get_user_object_permissions(self, content_type: ContentType = None) -> List[ObjectPermission]:
        """
        Get user's object-level permissions
        جلب صلاحيات المستخدم على مستوى الكائن
        """
        if not self.user:
            return []
        
        queryset = ObjectPermission.objects.filter(
            user=self.user,
            is_active=True
        ).select_related('permission', 'content_type')
        
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        return list(queryset)
    
    def can_manage_user(self, target_user: User) -> bool:
        """
        Check if current user can manage target user
        التحقق من إمكانية إدارة المستخدم المستهدف
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        # Superusers can manage anyone
        if self.user.is_superuser:
            return True
        
        # Users cannot manage superusers unless they are superusers themselves
        if target_user.is_superuser:
            return False
        
        # Check if user has user management permission
        if self.has_permission('administration.manage_users'):
            return True
        
        # Check if user can manage users in their department
        # This would need to be implemented based on your organizational structure
        
        return False


# Decorator for permission checking
def require_permission(permission_codename: str, obj_param: str = None):
    """
    Decorator to require specific permission for a view
    مُزخرف لطلب صلاحية معينة للعرض
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            permission_service = HierarchicalPermissionService(request.user)
            
            obj = None
            if obj_param and obj_param in kwargs:
                # Get object from view kwargs
                obj = kwargs[obj_param]
            
            if not permission_service.has_permission(permission_codename, obj):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("ليس لديك صلاحية للوصول لهذه الصفحة")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_module_permission(module_name: str, action: str):
    """
    Decorator to require module permission for a view
    مُزخرف لطلب صلاحية وحدة للعرض
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            permission_service = HierarchicalPermissionService(request.user)
            
            if not permission_service.has_module_permission(module_name, action):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("ليس لديك صلاحية للوصول لهذه الصفحة")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator