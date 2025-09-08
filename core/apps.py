"""
Core app configuration for OneLastAI Platform.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Application'
    
    def ready(self):
        """Initialize the core app."""
        # Import signal handlers
        try:
            import core.signals  # noqa: F401
        except ImportError:
            pass