"""
Production settings — used on Render (and any real deployment).

Overrides base with security hardening, env-driven hosts, Postgres via
DATABASE_URL (handled in base), and whitenoise manifest storage.
"""
import json

from .base import *

DEBUG = env("DEBUG", default=False)

# Env is configured in base.py with ALLOWED_HOSTS cast to list, so env()
# already returns a list here. Use env.list() consistently for comma-separated
# host/origin settings instead of calling .split() on the parsed list.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[".onrender.com"])

# CSRF trusted origins are also provided as a comma-separated environment
# variable. Keep the default as a list to match Django's expected setting.
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["https://*.onrender.com"]
)

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

_asset_storage_backend_class = env("ACADEMY_ASSET_STORAGE_BACKEND_CLASS", default="").strip()
if _asset_storage_backend_class:
    if not ACADEMY_ASSET_STORAGE_ALIAS or ACADEMY_ASSET_STORAGE_ALIAS in {"default", "staticfiles"}:
        raise ValueError("ACADEMY_ASSET_STORAGE_ALIAS must be a dedicated non-default storage alias.")
    try:
        _asset_storage_options = json.loads(env("ACADEMY_ASSET_STORAGE_OPTIONS", default="{}"))
    except (TypeError, ValueError) as exc:
        raise ValueError("ACADEMY_ASSET_STORAGE_OPTIONS must be a JSON object.") from exc
    if not isinstance(_asset_storage_options, dict):
        raise ValueError("ACADEMY_ASSET_STORAGE_OPTIONS must be a JSON object.")
    STORAGES[ACADEMY_ASSET_STORAGE_ALIAS] = {
        "BACKEND": _asset_storage_backend_class,
        "OPTIONS": _asset_storage_options,
    }

# Keep DB connections warm across requests (gunicorn workers).
CONN_MAX_AGE = 60

# Public URL of this deployment — Stripe/Razorpay success/cancel redirects
# and Telegram/email links all build from SITE_BASE_URL (base.py).
# Set SITE_BASE_URL in Render env vars to your https://<app>.onrender.com.

# NOTE: ACCOUNT_EMAIL_VERIFICATION is "mandatory" (base.py). Without SMTP
# credentials users cannot complete signup. Configure EMAIL_* env vars on
# Render (e.g. Gmail app password, SendGrid, Mailgun) BEFORE opening
# registration, or override ACCOUNT_EMAIL_VERIFICATION here for launch.
