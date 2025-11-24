from django.apps import AppConfig


class HrConfig(AppConfig):
    """HrConfig class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = 'نظام الموارد البشرية'

    def ready(self):
        """تشغيل إعدادات إضافية عند بدء التطبيق"""
        pass
