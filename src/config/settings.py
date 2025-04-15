# config/settings.py
import logging
from os import environ, makedirs
from os.path import join, exists
from pathlib import Path

from adjango.utils.common import is_celery
from dotenv import load_dotenv

env = environ.get
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=join(BASE_DIR.parent, '.env'))
MAIN_PROCESS = True if env('RUN_MAIN') != 'true' else False
DEV = bool(int(env('DEV', 0)))
DEBUG = bool(int(env('DEBUG', 0)))
HTTPS = bool(int(env('HTTPS')))
SITE_ID = int(env('SITE_ID'))
MAIN_DOMAIN = env('MAIN_DOMAIN', 'localhost')
DOMAIN_URL = f'http{"s" if HTTPS else ""}://{MAIN_DOMAIN}{":8000" if DEV or DEBUG else ""}'
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'web',
    MAIN_DOMAIN,
]
ALLOWED_HOSTS += env('ALLOWED_HOSTS', '').split(',')

POSTGRES_USE = bool(int(env('POSTGRES_USE')))
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_CODE = 'en-us'
ROOT_URLCONF = 'apps.core.routes.root'
WSGI_APPLICATION = 'config.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR.parent / 'static'
MEDIA_ROOT = BASE_DIR.parent / 'media'

IS_CELERY = is_celery()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'adjango',
    'rest_framework',
    'django_celery_beat',

    'apps.operator_by_phone',
]

# ЗАГЛУШКА Очевидно проксировать статику нужно в S3 какое-нибудь
# Из простого рекомендую MinioS3
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# DB
if POSTGRES_USE:
    DATABASES = {'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }}
else:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': [] if DEV else [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '200/minute',
        'user': '500/minute',
    }
}

# Redis
REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = int(env('REDIS_PORT'))
REDIS_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
REDIS_CACHE_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'

# Celery
timezone = TIME_ZONE
CELERY_BROKER_URL = REDIS_BROKER_URL
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 86400 * 30}
result_backend = REDIS_BROKER_URL
accept_content = ['application/json']
task_serializer = 'json'
result_serializer = 'json'
task_default_queue = 'default'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True

# Logging
LOGS_DIR = join(BASE_DIR, 'logs')
LOGUI_URL_PREFIX = 'logui/'
if not exists(LOGS_DIR): makedirs(LOGS_DIR)
LOGUI_REQUEST_RESPONSE_LOGGER_NAME = 'global'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime}: {message}',
            'datefmt': '%d-%m %H:%M:%S',
            'style': '{',
        },
        'request': {
            'format': '{levelname} {asctime}: {message} - {method} {url} {status}',
            'style': '{',
        },
    },
    'handlers': {
        'daily_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': join(LOGS_DIR, 'django.log'),
            'when': 'midnight',  # Ротация происходит в полночь
            'interval': 1,  # Интервал ротации — 1 день
            'backupCount': 356,  # Хранить логи за последний год
            'formatter': 'simple',
            'encoding': 'utf8',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'global': {
            'handlers': ['daily_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Operator By Phone
REGISTER_OF_NUMBERING = [
    "https://opendata.digital.gov.ru/downloads/ABC-3xx.csv",
    "https://opendata.digital.gov.ru/downloads/ABC-4xx.csv",
    "https://opendata.digital.gov.ru/downloads/ABC-8xx.csv",
    "https://opendata.digital.gov.ru/downloads/DEF-9xx.csv"
]

# Other
COPY_PROJECT_CONFIGURATIONS = BASE_DIR / 'utils' / 'copy_configuration.py'

log = logging.getLogger('global')

log.info('#####################################')
log.info('########## Server Settings ##########')
log.info('#####################################')
log.info(f'{IS_CELERY=}')
log.info(f'{BASE_DIR=}')
log.info(f'{DOMAIN_URL=}')
log.info(f'{HTTPS=}')
log.info(f'{TIME_ZONE=}')
log.info(f'{POSTGRES_USE=}')
log.info(f'{REDIS_HOST=}')
log.info(f'{REDIS_PORT=}')
log.info(f'{ALLOWED_HOSTS=}')
log.info(f'{DEBUG=}')
log.info(f'{DEV=}')
log.info(f'{WSGI_APPLICATION=}')
log.info(f'{STATIC_URL=}')
log.info(f'{MEDIA_URL=}')
log.info(f'{STATIC_ROOT=}')
log.info(f'{MEDIA_ROOT=}')
log.info('#####################################')
log.info('#####################################')
log.info('#####################################')
