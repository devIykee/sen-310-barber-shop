import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "a-long-development-key-that-must-be-replaced-in-production-123456")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [host for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",") if host]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "booking",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "freshfade.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
 "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "freshfade.wsgi.application"
DATABASES = {"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600)}
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"}, {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}]
LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ = "en-gb", "Africa/Lagos", True, True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
