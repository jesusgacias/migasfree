# -*- coding: utf-8 -*-

import os

from .migasfree import *
from .base import *
from .functions import secret_key

# development environment
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
TEMPLATES[0]['APP_DIRS'] = True
LOGGING['loggers']['migasfree']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['file']['level'] = 'DEBUG'

MIGASFREE_PUBLIC_DIR = os.path.join(MIGASFREE_PROJECT_DIR, 'repo')
MIGASFREE_KEYS_DIR = os.path.join(MIGASFREE_APP_DIR, 'keys')

SECRET_KEY = secret_key(MIGASFREE_KEYS_DIR)

STATIC_ROOT = os.path.join(MIGASFREE_APP_DIR, 'static')
MEDIA_ROOT = MIGASFREE_PUBLIC_DIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'migasfree',
        'USER': 'migasfree',
        'PASSWORD': 'migasfree',
        'HOST': '',
        'PORT': '',
    }
}

# python manage.py graph_models -a -o myapp_models.png
INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'template_debug',)
INTERNAL_IPS = ("127.0.0.1",)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': ''
}
