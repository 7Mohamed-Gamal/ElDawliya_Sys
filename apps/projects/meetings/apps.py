from django.apps import AppConfig


class MeetingsConfig(AppConfig):
    """
    تكوين تطبيق الاجتماعات
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects.meetings'
    verbose_name = 'نظام الاجتماعات'
