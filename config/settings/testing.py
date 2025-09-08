"""
Testing-specific settings for OneLastAI Platform.
"""

from .development import *  # noqa: F403,F401

# Use in-memory database for faster tests
DATABASES = {  # noqa: F405
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations during testing for speed
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use dummy cache for testing
CACHES = {  # noqa: F405
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery during testing
CELERY_TASK_ALWAYS_EAGER = True  # noqa: F405
CELERY_TASK_EAGER_PROPAGATES = True  # noqa: F405

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'  # noqa: F405

# Disable logging during tests
LOGGING_CONFIG = None

# Mock AI services for testing
MOCK_AI_RESPONSES = True  # noqa: F405
AI_SERVICES_DEBUG = True  # noqa: F405

# Use test payment gateways
STRIPE_TEST_MODE = True  # noqa: F405
PAYPAL_MODE = 'sandbox'  # noqa: F405

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable security features that slow down tests
SECURE_SSL_REDIRECT = False  # noqa: F405
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
