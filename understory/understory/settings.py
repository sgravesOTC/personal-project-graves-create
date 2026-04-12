"""
Django settings for the Understory project.

UNDERSTORY - A community platform for mushroom foraging enthusiasts.

This Django project contains four main apps:
1. newshroom - Blog/articles about mushrooms and fungi (educational content)
2. sporeprint - User collections of mushroom specimens (field notes/citizen science)
3. fairy_ring - User authentication and social profiles
4. mycelium - Activity logging and user action tracking

For more information on Django settings, see:
https://docs.djangoproject.com/en/6.0/topics/settings/
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ================== SECURITY SETTINGS ==================
# WARNING: These settings are for development only
# For production, use environment variables and secure credentials

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7x9jjfjsipg@b)6rir(s&_ov@(_jf7=zxjdv_o#f11z$lw$ndz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# ================== INSTALLED APPS ==================
# newshroom: Blog articles about mushrooms
# sporeprint: User mushroom specimen collections
# fairy_ring: User authentication and profiles
# mycelium: Activity tracking for action logging
# taggit: Flexible tagging system for articles
# easy_thumbnails: Image thumbnail generation
# sites: Django sites framework (required for sitemaps)
# sitemaps: XML sitemaps for SEO

SITE_ID = 2
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taggit',
    'easy_thumbnails',
    'newshroom.apps.NewshroomConfig',
    'sporeprint.apps.SporeprintConfig',
    'fairy_ring.apps.FairyRingConfig',
    'mycoguide.apps.MycoguideConfig',
    'basket.apps.BasketConfig',
    'mycelium.apps.MyceliumConfig',
    'django.contrib.sites',
    'django.contrib.sitemaps',
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

ROOT_URLCONF = 'understory.urls'

# ================== TEMPLATES ==================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # Look for templates/ in each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'understory.wsgi.application'


# ================== DATABASE CONFIGURATION ==================
# Uses PostgreSQL for full-text search capabilities
# Credentials loaded from .env file using decouple

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL enables advanced search
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        }
    }


# ================== AUTHENTICATION & PASSWORD VALIDATION ==================
# Standard Django password validators for security

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


# ================== INTERNATIONALIZATION ==================
# Set to Chicago Central Time and US English

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_TZ = True
# ================== STATIC & MEDIA FILES ==================
# Static files: CSS, JavaScript, images (collected with 'collectstatic')
# Media files: User uploads (profiles, articles, specimens)

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ================== EMAIL CONFIGURATION ==================
# Gmail SMTP for sending password reset and newsletter emails
# Credentials loaded from .env file for security

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Gmail address
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # Gmail app password
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# ================== AUTHENTICATION REDIRECTS ==================
# Where users are redirected after login/logout
# Configured to stay within the fairy_ring (profile) section

LOGIN_REDIRECT_URL = '/fairy_ring/'
LOGIN_URL = '/fairy_ring/login/'
LOGOUT_URL = '/fairy_ring/logout/'

# Media

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'fairy_ring.authentication.EmailAuthBackend',
]

# Thumbnail Settings

THUMBNAIL_ALIASES = {}

# Basket

BASKET_SESSION_ID = 'foraging_basket'