import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-organbridge-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'widget_tweaks',
    # Local apps
    'accounts',
    'profiles',
    'matches',
    'ml_model',
    'bias_dashboard',
]

JAZZMIN_SETTINGS = {
    'site_title': 'OrganBridge Admin',
    'site_header': 'OrganBridge',
    'site_brand': 'OrganBridge',
    'welcome_sign': 'Welcome to OrganBridge Admin',
    'copyright': 'OrganBridge',
    'show_sidebar': True,
    'navigation_expanded': True,
    'order_with_respect_to': ['accounts', 'profiles', 'matches', 'bias_dashboard', 'ml_model'],
    'icons': {
        'auth.user': 'fas fa-user',
        'accounts.customuser': 'fas fa-user-md',
        'profiles.donorprofile': 'fas fa-hand-holding-heart',
        'profiles.recipientprofile': 'fas fa-procedures',
        'matches.organmatch': 'fas fa-link',
        'matches.matchmessage': 'fas fa-comments',
        'matches.matchpreference': 'fas fa-sliders-h',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'organBridge.urls'

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
        },
    },
]

WSGI_APPLICATION = 'organBridge.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/profiles/dashboard/'
LOGOUT_REDIRECT_URL = '/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

ML_MODEL_PATH = BASE_DIR / 'ml_model' / 'trained_models'


# Production settings
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DEBUG = False
    ALLOWED_HOSTS = ['*']

    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }

    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
