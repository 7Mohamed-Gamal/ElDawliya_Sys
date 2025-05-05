from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EmployeeTasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee_tasks'
    verbose_name = _('مهام الموظفين')

    def ready(self):
        """
        تهيئة التطبيق عند بدء التشغيل
        """
        # استيراد إشارات التطبيق
        import employee_tasks.signals
