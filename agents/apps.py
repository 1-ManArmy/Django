"""
Agents app configuration for OneLastAI Platform.
"""

from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agents'
    verbose_name = 'AI Agents'
    
    def ready(self):
        """Initialize the agents app."""
        # Import signal handlers
        try:
            import agents.signals  # noqa: F401
        except ImportError:
            pass
        
        # Initialize agent manager
        try:
            from agents.engines import agent_manager  # noqa: F401
        except ImportError:
            pass