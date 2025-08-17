# Export available viewsets; some modules may be optional in this repo state
try:
    from .employee_viewsets import *  # type: ignore
except Exception:
    pass
try:
    from .attendance_viewsets import *  # type: ignore
except Exception:
    pass
try:
    from .leave_viewsets import *  # type: ignore
except Exception:
    pass
try:
    from .payroll_viewsets import *  # type: ignore
except Exception:
    pass
try:
    from .core_viewsets import *  # type: ignore
except Exception:
    pass
try:
    from .analytics_viewsets import *  # type: ignore
except Exception:
    pass