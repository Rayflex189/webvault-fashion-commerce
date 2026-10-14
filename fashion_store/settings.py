"""
Django settings for fashion_store project.
"""

from pathlib import Path
import os

# ─────────────────────────────────────────
# ENVIRONMENT VARIABLES (must be first!)
# ─────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')  # <-- THE MISSING PIECE


# ─────────────────────────────────────────
# CORE SECURITY
# ─────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    "django-insecure-0vihpxuvaz%ap!1l^+4g$oz=x0rz0-ga(ymza7-kmopsos=fi5"
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.app.github.dev',
    'https://*.githubpreview.dev',
    'http://localhost:8000',
    'https://localhost:8000',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
]


# ─────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # WebVault Apps
    'core',
    'campaigns',
    'products',
    'orders',
    'payments',
    'delivery',
    'accounts',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fashion_store.urls"

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
                'core.context_processors.store_settings',
                'orders.context_processors.cart_counter',
            ],
        },
    },
]

WSGI_APPLICATION = "fashion_store.wsgi.application"


# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ─────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────
# STATIC & MEDIA
# ─────────────────────────────────────────
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────
# SITE URL (used for links in emails)
# ─────────────────────────────────────────
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')


# ─────────────────────────────────────────
# EMAIL CONFIGURATION (Django 6.1 MAILERS)
# ─────────────────────────────────────────
# Single, correct MAILERS block — replaces the duplicates.
_email_host = os.environ.get('EMAIL_HOST', '').strip()

if _email_host:
    # SMTP mode — used when EMAIL_HOST is set in .env
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": _email_host,
                "port": int(os.environ.get('EMAIL_PORT', 587)),
                "use_tls": os.environ.get('EMAIL_USE_TLS', 'True') == 'True',
                "username": os.environ.get('EMAIL_HOST_USER', ''),
                "password": os.environ.get('EMAIL_HOST_PASSWORD', ''),
            },
        },
    }
else:
    # Dev fallback — prints emails to terminal
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.console.EmailBackend",
        },
    }

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@webvault.store')


# ─────────────────────────────────────────
# JAZZMIN CONFIGURATION
# ─────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "show_ui_builder": False,
    "custom_css": "css/admin_custom.css",
    "site_title": "WebVault Admin",
    "site_header": "WebVault",
    "site_brand": "WebVault Fashion",
    "welcome_sign": "Welcome to your store dashboard",
    "copyright": "WebVault",
    "search_model": ["auth.User", "orders.Order"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Visit Store", "url": "/", "new_window": True},
    ],
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "orders",
        "products",
        "delivery",
        "core",
        "auth",
    ],
}
