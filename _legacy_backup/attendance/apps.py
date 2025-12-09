from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AttendanceConfig(AppConfig):
    """AttendanceConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    verbose_name = _('Attendance Management')

    def ready(self):
        """ready function"""
        import apps.hr.attendance.signals
