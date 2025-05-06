"""
هذا الملف موجود للتوافق مع الإصدارات السابقة. يرجى استخدام 'permissions.py' للتطوير المستقبلي.
(This file exists for backward compatibility. Please use 'permissions.py' for future development.)
"""

from django import template
from administrator.templatetags.permissions import (
    has_rbac_permission,
    check_rbac_permission
)

register = template.Library()

# Re-register the imported filters and tags
register.filter('has_rbac_permission', has_rbac_permission)
register.simple_tag(check_rbac_permission)
