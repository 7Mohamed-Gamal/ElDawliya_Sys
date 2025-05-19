from django.apps import AppConfig


class AdministratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administrator'
    verbose_name = 'إدارة النظام'

    def ready(self):
        # Import models to register signals
        import administrator.models

        # Import audit models
        try:
            import administrator.models_audit
        except ImportError:
            pass

        # Import permission group models
        try:
            import administrator.models_permission_groups
        except ImportError:
            pass
