from .default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

SITE_ID = 1

CORS_ORIGIN_WHITELIST = ('localhost:8000','localhost:9000')
CORS_ALLOW_CREDENTIALS = True

ROUTER_PROTOCOL = 'http'
