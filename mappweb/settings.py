"""
Django settings for mappweb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import os
import mongoengine as mongo

# please use this setting to get core server url... as it will change often
# TODO Determine a more flexible alternative for this url
CORE_API_URL = os.environ.get("CORE_API_URL", "http://127.0.0.1:8000/api/v1")

# url shortner for sharing data viz
BITLY_API = '08f218f02ddf9976b1e7fd57edbf314f860e7b97'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xe_$xy)easj#%*yhbo4$e)qk8x#p(y92xiehp*2l7$7*8vxf%m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not ('PROD' in os.environ)

TEMPLATE_DEBUG = not ('PROD' in os.environ)

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split()


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework_mongoengine',
    'mongoengine.django.mongo_auth',
    'django_nose',
    'django_extensions',
    'mappweb',
    'maps.users',
    'maps.data_import',
    'maps.data_visualization',
    'maps.core',
    'maps.fixtures',
    'maps.org',
    'maps.resources',
    'storages',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEST_RUNNER = 'mappweb.runner.LiveServerTestRunner'
NOSE_ARGS = ['--nologcapture', '--traverse-namespace']

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#MEDIA_URL = '/media/'

# STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'templates', 'assets'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'templates', 'static')

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.csrf',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.YAMLRenderer'
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),

    'PAGINATE_BY': None
}

ROOT_URLCONF = 'mappweb.urls'

WSGI_APPLICATION = 'mappweb.wsgi.application'

SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)
AUTH_USER_MODEL = 'users.MappUser'
MONGOENGINE_USER_DOCUMENT = 'maps.users.models.User'

# Email Settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'hawaiifoodsystem@gmail.com'
EMAIL_HOST_PASSWORD = 'f00dP455word'

CONTACT_FORM_RECIPIENT = ['wayne.tan@softworks.com.my']

# Store session in MongoDB for now, so I don't have to mess with sqlite
# TODO: later this will be migrated to using session from core.usermanagement
MONGODB_HOST = "ec2-54-184-173-12.us-west-2.compute.amazonaws.com"
MONGODB_PORT = None
MONGODB_DATABASE = "Maps"
if 'EC2_HOME' in os.environ:
    MONGODB_HOST = "ec2-54-184-173-12.us-west-2.compute.amazonaws.com"
    MONGODB_PORT = None
    MONGODB_DATABASE = "Maps"
else:
    MONGODB_HOST = "127.0.0.1"
    MONGODB_PORT = None
    MONGODB_DATABASE = "Maps"

SESSION_ENGINE = 'mongoengine.django.sessions'
SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'templates/maps-admin'),
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

USPS_ID = '102SUSTA4250'

# celery
if 'SQS_QUEUE' in os.environ:
    BROKER_TRANSPORT = 'sqs'
    BROKER_USER = os.environ['AWS_ACCESS_KEY_ID']
    BROKER_PASSWORD = os.environ['AWS_SECRET_KEY']
    BROKER_TRANSPORT_OPTIONS = {'region': 'us-west-2'}
    CELERY_DEFAULT_QUEUE = os.environ['SQS_QUEUE']  # 'djangoshop-queue'
    CELERY_QUEUES = {
        CELERY_DEFAULT_QUEUE: {
            'exchange': CELERY_DEFAULT_QUEUE,
            'binding_key': CELERY_DEFAULT_QUEUE,
        }
    }
else:
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_ALWAYS_EAGER = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

try:
    from defaults import *
except ImportError:
    pass

### s3 for static files
AWS_STORAGE_BUCKET_NAME = 'mapp-folder'
AWS_ACCESS_KEY_ID = 'AKIAIFKURSSEMQJIXWOA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
if DEBUG:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
else:
    STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    ### s3 for media files
    MEDIA_URL = AWS_S3_CUSTOM_DOMAIN + '/media/'

try:
    from local_settings import *
except ImportError:
    pass

mongo.connect(host=MONGODB_HOST, db=MONGODB_DATABASE, alias="default")
