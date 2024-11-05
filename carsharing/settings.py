import json
from pathlib import Path

from environ import Env

env = Env()

BASE_DIR = Path(__file__).resolve().parent.parent

env.read_env(BASE_DIR / '.env')

SECRET_KEY = env.str('SECRET_KEY')

DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

GOOGLE_SHEETS_SERVICE_ACCOUNT_CREDENTIALS_FILE_PATH = (
        BASE_DIR / 'google_sheets_service_account_credentials.json'
)

GOOGLE_SHEETS_SERVICE_ACCOUNT_CREDENTIALS = json.loads(
    GOOGLE_SHEETS_SERVICE_ACCOUNT_CREDENTIALS_FILE_PATH.read_text(
        encoding='utf-8',
    )
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_standardized_errors',
    'rest_framework',
    'django_celery_beat',
    'corsheaders',
    'google_sheets',
    'core',
    'staff',
    'economics',
    'car_washes',
    'shifts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'carsharing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'carsharing.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler"
}
DRF_STANDARDIZED_ERRORS = {
    "EXCEPTION_FORMATTER_CLASS": "core.exceptions.ExceptionFormatter",
}

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_TASK_REJECT_ON_WORKER_LOST = False
CELERY_TASK_ACKS_LATE = True  # Acknowledge task after completion
CELERY_TASK_RETRY_POLICY = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.6,
}

TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
