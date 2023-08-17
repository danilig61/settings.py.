"""
Django settings for news_project project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from datetime import timedelta
from pathlib import Path
import logging
from django.conf import settings

logger = logging.getLogger('django')
logger.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s - %(message)s')
security_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s: %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_formatter)

general_file_handler = logging.FileHandler('general.log')
general_file_handler.setLevel(logging.INFO)
general_file_handler.setFormatter(file_formatter)

errors_file_handler = logging.FileHandler('errors.log')
errors_file_handler.setLevel(logging.ERROR)
errors_file_handler.setFormatter(file_formatter)

security_file_handler = logging.FileHandler('security.log')
security_file_handler.setLevel(logging.DEBUG)
security_file_handler.setFormatter(security_formatter)

mail_handler = logging.handlers.SMTPHandler(
    mailhost=settings.EMAIL_HOST,
    fromaddr=settings.DEFAULT_FROM_EMAIL,
    toaddrs=[settings.ADMIN_EMAIL],
    subject='Error Occurred'
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(general_file_handler)
logger.addHandler(errors_file_handler)
logger.addHandler(security_file_handler)
logger.addHandler(mail_handler)

class ConsoleFilter(logging.Filter):
    def filter(self, record):
        return settings.DEBUG

class EmailFileFilter(logging.Filter):
    def filter(self, record):
        return not settings.DEBUG and record.levelno >= logging.ERROR and record.name in ['django.request', 'django.server']

console_handler.addFilter(ConsoleFilter())
general_file_handler.addFilter(EmailFileFilter())
errors_file_handler.addFilter(EmailFileFilter())

logger.addFilter(ConsoleFilter())
logger.addFilter(EmailFileFilter())
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-))f*0c%%i7b7bx0usu0h*z2m^08yxijn&+2g5h75y@r^p_=lwp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'news.templatetags',
    'allauth',
    'allauth.account',
    'allauth.socialaccount.providers.google',
    'django.contrib.sites',
    'allauth.socialaccount',
    'news.apps.NewsConfig',
    'celery',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'censor': 'news.templatetags.censor'
            }
        },
    },
]

WSGI_APPLICATION = 'news_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True
    }
}

ACCOUNT_FORMS = {'signup': 'sign.models.BasicSignupForm'}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGIN_URL = 'account_login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ignatevdaniil161@gmail.com'
EMAIL_HOST_PASSWORD = 'IgRuni19771975'

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'rpc://'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_IMPORTS = [
    'news.tasks',
]

CELERY_TIMEZONE = 'UTC'

CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_ROUTES = {
    'news.tasks.*': {'queue': 'default'},
}

CELERY_TASK_DEFAULT_RETRY_DELAY = 5 * 60

CELERY_BEAT_SCHEDULE = {
    'send-weekly-newsletter': {
        'task': 'news.tasks.schedule_weekly_newsletter',
        'schedule': timedelta(hours=1),
    },
}