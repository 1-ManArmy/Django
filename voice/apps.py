"""
Voice app configuration for OneLastAI Platform.
"""

from django.apps import AppConfig


class VoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voice'
    verbose_name = 'Voice Services'