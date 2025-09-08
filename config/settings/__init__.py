"""
Django settings initialization for OneLastAI Platform.
Automatically loads the appropriate settings module based on environment.
"""

import os
from decouple import config

# Determine which settings module to use
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *  # noqa: F403,F401
elif ENVIRONMENT == 'testing':
    from .testing import *  # noqa: F403,F401
else:
    from .development import *  # noqa: F403,F401
