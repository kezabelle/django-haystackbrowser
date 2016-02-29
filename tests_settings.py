# -*- coding: utf-8 -*-
import os


DEBUG = os.environ.get('DEBUG', 'on') == 'on'
SECRET_KEY = os.environ.get('SECRET_KEY', 'TESTTESTTESTTESTTESTTESTTESTTEST')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,testserver').split(',')
BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    # need sessions for Client.login() to work
    'django.contrib.sessions',
    'django.contrib.admin',
    'haystack',
    'haystackbrowser',
]

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

STATIC_URL = '/__static__/'
MEDIA_URL = '/__media__/'
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True


ROOT_URLCONF = 'tests_urls'

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STATIC_ROOT = os.path.join(BASE_DIR, 'tests_collectstatic')
MEDIA_ROOT = os.path.join(BASE_DIR, 'tests_media')

TEMPLATE_DIRS = ()
USE_TZ = True


OLD_HAYSTACK = bool(int(os.getenv('OLD_HAYSTACK', '0')))

if OLD_HAYSTACK is True:
    HAYSTACK_SITECONF = 'tests_search_sites'
    HAYSTACK_SEARCH_ENGINE = 'whoosh'
    HAYSTACK_WHOOSH_PATH = os.path.join(BASE_DIR, 'whoosh_lt25_index')
else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(BASE_DIR, 'whoosh_gt25_index'),
        },
        'other': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(BASE_DIR, 'whoosh_gt25_index'),
        },
    }
