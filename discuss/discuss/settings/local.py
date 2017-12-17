from .base import *  # NOQA

DEBUG = env.bool('DJANGO_DEBUG', False)

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += ['debug_toolbar']
INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'discuss.urls.local'
