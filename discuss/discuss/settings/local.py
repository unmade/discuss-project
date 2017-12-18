from .base import *  # NOQA

DEBUG = env.bool('DJANGO_DEBUG', False)

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += ['debug_toolbar']

ROOT_URLCONF = 'discuss.urls.local'


def show_toolbar(request):
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'discuss.settings.local.show_toolbar',
}
