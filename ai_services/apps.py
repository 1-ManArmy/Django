"""
AI Services app configuration for OneLastAI Platform.
"""

from django.apps import AppConfig


class AiServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_services'
    verbose_name = 'AI Services'
    
    def ready(self):
        """Initialize the AI services app."""
        # Import signal handlers
        try:
            import ai_services.signals  # noqa: F401
        except ImportError:
            pass
        
        # Initialize AI service manager
        try:
            from ai_services.services import ai_service_manager  # noqa: F401
        except ImportError:
            pass