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

CORS_ORIGIN_WHITELIST = ('platform.codecult.local:9000', 'codecult.local:9000')
CORS_ALLOW_CREDENTIALS = True

LOGIN_REDIRECT_URL = "http://platform.codecult.local:9000"
ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL

ROUTER_PROTOCOL = 'http'
ROUTER_DOMAIN = 'codecult.local:5000'
SESSION_COOKIE_DOMAIN = ".codecult.local"
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
