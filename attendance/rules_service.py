from typing import Optional, Dict, Any
from django.db import transaction


def _use_modern() -> bool:
    """_use_modern function"""
    from django.conf import settings
    return getattr(settings, 'ATTENDANCE_USE_MODERN_RULES', False)


def list_rules() -> Any:
    """list_rules function"""
    if _use_modern():
        from .models import AttendanceRule
        return AttendanceRule.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('name')
    else:
        from .models import AttendanceRules
        return AttendanceRules.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('rule_name')


def get_rule(rule_id: int) -> Any:
    """get_rule function"""
    if _use_modern():
        from .models import AttendanceRule
        return AttendanceRule.objects.get(id=rule_id)
    else:
        from .models import AttendanceRules
        return AttendanceRules.objects.get(pk=rule_id)


@transaction.atomic
def create_rule(data: Dict[str, Any]) -> Any:
    """create_rule function"""
    if _use_modern():
        from .models import AttendanceRule
        obj = AttendanceRule.objects.create(
            name=data.get('rule_name') or data.get('name') or '',
            description=data.get('description', ''),
            is_active=True,
        )
        return obj
    else:
        from .models import AttendanceRules
        obj = AttendanceRules.objects.create(
            rule_name=data.get('rule_name'),
            shift_start=data.get('shift_start'),
            shift_end=data.get('shift_end'),
            late_threshold=data.get('late_threshold'),
            early_threshold=data.get('early_threshold'),
            overtime_start_after=data.get('overtime_start_after'),
            week_end_days=data.get('week_end_days'),
            is_default=data.get('is_default', False),
        )
        return obj


@transaction.atomic
def update_rule(rule_id: int, data: Dict[str, Any]) -> Any:
    """update_rule function"""
    if _use_modern():
        from .models import AttendanceRule
        obj = AttendanceRule.objects.get(id=rule_id)
        obj.name = data.get('rule_name') or data.get('name') or obj.name
        obj.description = data.get('description', obj.description)
        obj.save()
        return obj
    else:
        from .models import AttendanceRules
        obj = AttendanceRules.objects.get(pk=rule_id)
        for field in ['rule_name','shift_start','shift_end','late_threshold','early_threshold','overtime_start_after','week_end_days','is_default']:
            if field in data:
                setattr(obj, field, data[field])
        obj.save()
        return obj


@transaction.atomic
def delete_rule(rule_id: int) -> None:
    """delete_rule function"""
    if _use_modern():
        from .models import AttendanceRule
        AttendanceRule.objects.filter(id=rule_id).prefetch_related()  # TODO: Add appropriate prefetch_related fields.delete()
    else:
        from .models import AttendanceRules
        AttendanceRules.objects.filter(pk=rule_id).prefetch_related()  # TODO: Add appropriate prefetch_related fields.delete()


@transaction.atomic
def set_default_rule(rule_id: int) -> Optional[Any]:
    """set_default_rule function"""
    if _use_modern():
        # Modern rules do not have is_default; no-op
        return None
    else:
        from .models import AttendanceRules
        AttendanceRules.objects.update(is_default=False)
        obj = AttendanceRules.objects.get(pk=rule_id)
        obj.is_default = True
        obj.save()
        return obj