from .base import *

DEBUG = True

# Development-specific settings
INSTALLED_APPS += [
    # Add any development-specific apps here
]

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Use console email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
