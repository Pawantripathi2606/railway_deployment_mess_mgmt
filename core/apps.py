from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Import signal handlers when app is ready"""
        import core.signals  # User profile signals
        import core.password_reset_signals  # Password reset confirmation emails

