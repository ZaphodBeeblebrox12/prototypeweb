"""
Production settings — used on Render (and any real deployment).

Overrides base with security hardening, env-driven hosts, Postgres via
DATABASE_URL (handled in base), and whitenoise manifest storage.
"""
from django.core.exceptions import ImproperlyConfigured

from .base import *

# Production must use persistent PostgreSQL. Render Free's filesystem is
# ephemeral, so SQLite could silently lose user accounts and learning progress.
database_url = env("DATABASE_URL", default="").strip()
if not database_url:
    raise ImproperlyConfigured(
        "DATABASE_URL is required in production. Configure the dedicated "
        "staging PostgreSQL connection before deploying."
    )
if not database_url.lower().startswith(("postgres://", "postgresql://")):
    raise ImproperlyConfigured(
        "DATABASE_URL must use PostgreSQL in production; SQLite is not supported."
    )

DEBUG = env("DEBUG", default=False)

# Hosts: comma-separated env. MUST be a list (Django rejects a plain
# string, and this override replaces base.py's list conversion).
ALLOWED_HOSTS = [
    h.strip() for h in
    env("ALLOWED_HOSTS", default=".onrender.com").split(",")
    if h.strip()
]

# CSRF: same list requirement.
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in
    env("CSRF_TRUSTED_ORIGINS", default="https://*.onrender.com").split(",")
    if o.strip()
]

# --- Security hardening ---------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- Static files: whitenoise compressed+hashed ---------------------------
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Keep DB connections warm across requests (gunicorn workers).
CONN_MAX_AGE = 60

# Public URL of this deployment — Stripe/Razorpay success/cancel redirects
# and Telegram/email links all build from SITE_BASE_URL (base.py).
# Set SITE_BASE_URL in Render env vars to your https://<app>.onrender.com.

# NOTE: ACCOUNT_EMAIL_VERIFICATION is "mandatory" (base.py). For Render Free,
# use the configured HTTPS email API backend and set RESEND_API_KEY plus a
# verified DEFAULT_FROM_EMAIL in the hosting dashboard before opening signup.
# Do not disable verification just to work around missing delivery credentials.
