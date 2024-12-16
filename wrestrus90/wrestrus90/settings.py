import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY =  os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'competition.apps.CompetitionConfig',
    'event.apps.EventConfig',
    'api.apps.ApiConfig',
    'core.apps.CoreConfig',
    'main_page.apps.MainPageConfig',
    'rest_framework',
    'django_extensions',
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

ROOT_URLCONF = 'wrestrus90.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'base_templates',
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth', # передает в шаблон user
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.get_menu_context', # контекстный процессор
            ],
        },
    },
]

WSGI_APPLICATION = 'wrestrus90.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         # Меняем настройку Django: теперь для работы будет использоваться
#         # бэкенд postgresql
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'django'),
#         'USER': os.getenv('POSTGRES_USER', 'django'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', ''),
#         'PORT': os.getenv('DB_PORT', 5432)
#     }
# }


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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
# STATICFILES_DIRS = [
#     BASE_DIR / 'static',
# ]

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

#
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # стандартный авторизация по логин
    'users.authentication.EmailAuthBackend', # авторизация по email
]

# начало настройка почтового сервера
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# EMAIL_HOST = "smtp.yandex.ru"
# EMAIL_PORT = 465
# EMAIL_HOST_USER = "djangocourse@yandex.ru"
# EMAIL_HOST_PASSWORD = "bnufhkwcripaunvu"
# EMAIL_USE_SSL = True

# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# SERVER_EMAIL = EMAIL_HOST_USER
# EMAIL_ADMIN = EMAIL_HOST_USER
# конец настройка почтового сервера


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#задает URL-адрес, на который следует перенаправлять пользователя после успешной авторизации;
LOGIN_REDIRECT_URL = 'home'
#определяет URL-адрес, на который следует перенаправить неавторизованного пользователя при попытке посетить закрытую страницу сайта;
LOGIN_URL = '/'
#  задает URL-адрес, на который перенаправляется пользовате  ль после выхода.
LOGOUT_REDIRECT_URL = '/'

DEFAULT_USER_IMAGE = MEDIA_URL + 'users/default.png'
