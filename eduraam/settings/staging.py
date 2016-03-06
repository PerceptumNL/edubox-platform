from .default import *

DEBUG = bool(int(os.environ.get('DEBUG_FLAG', '0')))

ADMINS = (
    ('Sander', 'sander@perceptum.nl'),
)

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {"default": dj_database_url.config()}

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
STATIC_ROOT = 'staticfiles'
# Try to prevent collisions with other django apps that are routed.
STATIC_URL = '/static5bec552b27/'

if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ.get('SECRET_KEY')

if 'SITE_ID' in os.environ:
    SITE_ID = int(os.environ.get('SITE_ID'))

if 'APPSTATIC' in os.environ:
    APPSTATIC = os.environ.get('APPSTATIC')

EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST= 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
SERVER_EMAIL = 'edbx@perceptum.nl'

CORS_ORIGIN_WHITELIST = ('staging.codecult.nl')
CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_DOMAIN = ".codecult.nl"

DEFAULT_CODE_ORG_TEACHER = os.environ.get('DEFAULT_CODE_ORG_TEACHER')
