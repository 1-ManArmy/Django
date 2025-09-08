"""
Accounts app configuration for OneLastAI Platform.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User Accounts'
    
    def ready(self):
        """Initialize the accounts app."""
        # Import signal handlers
        try:
            import accounts.signals  # noqa: F401
        except ImportError:
            pass