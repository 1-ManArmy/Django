"""
Development-specific settings for OneLastAI Platform.
"""

from .base import *

# Override debug for development
DEBUG = True

# Database for development (PostgreSQL preferred for production parity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Development-specific installed apps
INSTALLED_APPS += [
    'debug_toolbar',
]

# Development-specific middleware
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# Debug Toolbar Configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Disable SSL requirement for development
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
USE_TLS = False

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Less strict CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Cache (use local memory for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session storage for development
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery (use synchronous processing for development)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# AI Services - Use test keys or mock responses in development
AI_SERVICES_DEBUG = True
MOCK_AI_RESPONSES = config('MOCK_AI_RESPONSES', default=False, cast=bool)

# Payment gateways - Use sandbox/test mode
STRIPE_TEST_MODE = True
PAYPAL_MODE = 'sandbox'

# Logging - More verbose in development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['ai_services']['level'] = 'DEBUG'
LOGGING['loggers']['agents']['level'] = 'DEBUG'

# Development-specific feature flags
FEATURE_FLAGS.update({
    'debug_mode': True,
    'test_payments': True,
    'mock_ai_responses': MOCK_AI_RESPONSES,
})

# Allow all hosts in development (be careful in production)
ALLOWED_HOSTS = ['*']

# Static files in development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
