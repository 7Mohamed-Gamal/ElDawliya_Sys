"""
هذا الملف موجود للتوافق مع الإصدارات السابقة. يرجى استخدام 'permissions.py' للتطوير المستقبلي.
(This file exists for backward compatibility. Please use 'permissions.py' for future development.)
"""

from django import template
from administrator.templatetags.permissions import (
    has_op_perm,
    has_pg_perm,
    show_if_has_op_perm,
    show_if_has_pg_perm
)

register = template.Library()

# Re-register the imported filters and tags
register.simple_tag(has_op_perm, takes_context=True)
register.simple_tag(has_pg_perm, takes_context=True)
register.filter('show_if_has_op_perm', show_if_has_op_perm)
register.filter('show_if_has_pg_perm', show_if_has_pg_perm)
