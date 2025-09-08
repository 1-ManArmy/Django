"""
Production-specific settings for OneLastAI Platform.
"""

from .base import *  # noqa: F403,F401

# Production security settings
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())  # noqa: F405

# Database Configuration for Production
DATABASES = {  # noqa: F405
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),  # noqa: F405
        'USER': config('DB_USER'),  # noqa: F405
        'PASSWORD': config('DB_PASSWORD'),  # noqa: F405
        'HOST': config('DB_HOST', default='localhost'),  # noqa: F405
        'PORT': config('DB_PORT', default='5432'),  # noqa: F405
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,
    }
}

# Security Settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)  # noqa: F405,E501
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_TLS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'  # noqa: F405

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Email Configuration for Production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # noqa: F405

# Redis Configuration for Production
REDIS_URL = config('REDIS_URL')  # noqa: F405

CACHES = {  # noqa: F405
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Channel Layers for Production
CHANNEL_LAYERS = {  # noqa: F405
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# Celery Configuration for Production
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=REDIS_URL)  # noqa: F405,E501
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=REDIS_URL)  # noqa: F405,E501

# Static Files - Use Whitenoise with compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # noqa: F405,E501

# Media Files - Use cloud storage in production
DEFAULT_FILE_STORAGE = config(  # noqa: F405
    'DEFAULT_FILE_STORAGE',
    default='django.core.files.storage.FileSystemStorage'
)

# Cloud Storage Configuration (if using)
if 'storages' in INSTALLED_APPS:  # noqa: F405
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')  # noqa: F405
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')  # noqa: F405
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')  # noqa: F405
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')  # noqa: F405
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')  # noqa: F405
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    
    # Cloudinary Configuration (alternative)
    CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')  # noqa: F405
    CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')  # noqa: F405
    CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')  # noqa: F405

# Monitoring and Error Tracking
SENTRY_DSN = config('SENTRY_DSN', default='')  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(auto_enabling_integrations=False),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment=config('ENVIRONMENT', default='production'),  # noqa: F405
    )

# New Relic Configuration
NEW_RELIC_LICENSE_KEY = config('NEW_RELIC_LICENSE_KEY', default='')  # noqa: F405
if NEW_RELIC_LICENSE_KEY:
    NEW_RELIC_APP_NAME = config('NEW_RELIC_APP_NAME', default='OneLastAI')  # noqa: F405

# Production-specific feature flags
FEATURE_FLAGS.update({  # noqa: F405
    'debug_mode': False,
    'test_payments': False,
    'mock_ai_responses': False,
})

# Logging Configuration for Production
LOGGING = {  # noqa: F405
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/onelastai/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'sentry'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'ai_services': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'agents': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Payment Configuration for Production
STRIPE_TEST_MODE = False
PAYPAL_MODE = 'live'  # noqa: F405

# API Rate Limiting for Production (more restrictive)
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {  # noqa: F405
    'anon': '50/day',
    'user': '500/day',
    'premium': '2000/day',
}

# AI Services - Production configuration
AI_SERVICES_DEBUG = False  # noqa: F405
MOCK_AI_RESPONSES = False  # noqa: F405
