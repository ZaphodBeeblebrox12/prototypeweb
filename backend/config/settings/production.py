"""
Production settings — used on Render (and any real deployment).

Overrides base with security hardening, env-driven hosts, Postgres via
DATABASE_URL (handled in base), and whitenoise manifest storage.
"""
import json
from urllib.parse import urlsplit

from .base import *

DEBUG = env("DEBUG", default=False)

# Staging-only login escape hatch for test learners. This never changes
# production verification policy: the flag is effective only when SITE_BASE_URL
# is the exact Academy staging hostname. Emails remain unverified; this only
# avoids an outbound confirmation email blocking staging sign-in.
ACADEMY_STAGING_UNVERIFIED_LOGIN_ENABLED = False
_allow_staging_unverified_login = env.bool(
    "ACADEMY_STAGING_ALLOW_UNVERIFIED_LOGIN", default=False
)
_configured_site_host = (
    urlsplit(str(SITE_BASE_URL or "")).hostname or ""
).lower()
_expected_academy_staging_host = str(
    ACADEMY_STAGING_PAYMENT_SIMULATOR_HOST
).strip().lower()
if (
    _allow_staging_unverified_login
    and _configured_site_host == _expected_academy_staging_host
):
    ACADEMY_STAGING_UNVERIFIED_LOGIN_ENABLED = True
    ACCOUNT_EMAIL_VERIFICATION = "optional"
else:
    # Hosted environments remain strict unless the exact staging gate passes.
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"

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

# Email verification remains mandatory on production and on every hosted
# service by default. Only the exact Academy staging hostname can opt into
# optional verification using ACADEMY_STAGING_ALLOW_UNVERIFIED_LOGIN=true.
# Hosted deployments default to the Resend HTTPS backend because Render Free
# blocks outbound SMTP. Configure a valid Resend key and verified sender before
# relying on confirmation mail for customer-facing production registration.
