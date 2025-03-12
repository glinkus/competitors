import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "0b6#8bvn=jt__=2q7ebp!oj86!%al%^o8f6yv)!4#jk775%8g#"

DEBUG = True
ALLOWED_HOSTS = ["*"]
X_FRAME_OPTIONS = "SAMEORIGIN"

# Applications.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "modules.analysis",
    "modules.competitors_scraper",
    "core.uauth",
    "parea",
    "rarea",
    "modules.demo",
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

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"
ASGI_APPLICATION = "main.asgi.application"

#os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# Database.

BASE_DIRECT = os.path.dirname(os.path.abspath(__file__))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "osomcodex.db"),
    }
}


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Login flow.
LOGIN_URL = "parea:index"
LOGIN_REDIRECT_URL = "rarea:index"
LOGOUT_REDIRECT_URL = "parea:index"

# Password validation.
AUTH_PASSWORD_VALIDATORS = []

# Internationalization.
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Vilnius"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (BASE_DIR / "locale",)

# Static files & uploads.
STATIC_URL = "/pub/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "pub"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Loggers.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        },
    },
    "handlers": {
        "console": {
            "formatter": "colored",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "codex": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

#Scraper settings
SCRAPY_PROJECT_PATH = os.path.join(BASE_DIR, 'modules', 'competitors_scraper')
sys.path.append(SCRAPY_PROJECT_PATH)
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'competitors_scraper.settings')