from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API Application'

    def ready(self):
        """Initialize API configurations when Django starts"""
        pass
