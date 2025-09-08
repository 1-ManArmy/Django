"""
Celery configuration for OneLastAI Platform.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('onelastai')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat Schedule
app.conf.beat_schedule = {
    # AI Model Health Check
    'health-check-ai-models': {
        'task': 'ai_services.tasks.health_check_ai_models',
        'schedule': 300.0,  # Every 5 minutes
    },
    # Clean up old conversations
    'cleanup-old-conversations': {
        'task': 'agents.tasks.cleanup_old_conversations',
        'schedule': 3600.0,  # Every hour
    },
    # Generate usage reports
    'generate-daily-usage-report': {
        'task': 'monitoring.tasks.generate_daily_usage_report',
        'schedule': 86400.0,  # Daily at midnight
    },
    # Process payment webhooks
    'process-pending-webhooks': {
        'task': 'payments.tasks.process_pending_webhooks',
        'schedule': 60.0,  # Every minute
    },
    # Update community statistics
    'update-community-stats': {
        'task': 'community.tasks.update_community_statistics',
        'schedule': 1800.0,  # Every 30 minutes
    },
}

# Celery Task Routes
app.conf.task_routes = {
    'ai_services.tasks.*': {'queue': 'ai_processing'},
    'voice.tasks.*': {'queue': 'voice_processing'},
    'payments.tasks.*': {'queue': 'payments'},
    'monitoring.tasks.*': {'queue': 'monitoring'},
}

# Task Time Limits
app.conf.task_time_limit = 300  # 5 minutes
app.conf.task_soft_time_limit = 240  # 4 minutes

# Task Result Configuration
app.conf.result_expires = 3600  # 1 hour

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
