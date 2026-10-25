#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Explicit one-time staging hook: import the canonical Bollinger Bands course
# as a review-only CourseImport. No published learner rows, offer or checkout
# are created by this management command. Keep all database credentials in
# Render environment variables; never put them in source control.
if [[ "${STAGE_BOLLINGER_BANDS_REVIEW_IMPORT:-false}" =~ ^(1|true|TRUE|yes|YES)$ ]]; then
  if [[ "${RENDER_SERVICE_ID:-}" != "srv-db9ioke1egvs73feb8ag" ]]; then
    echo "Refusing Bollinger Bands import: this is not the Academy staging service." >&2
    exit 1
  fi
  if [[ ! "${DATABASE_URL:-}" =~ ^postgres(ql)?:// ]]; then
    echo "Refusing Bollinger Bands import: DATABASE_URL must target PostgreSQL." >&2
    exit 1
  fi

  python manage.py import_microcourse \
    --manifest ../course-source/understand-bollinger-bands/course-manifest.json \
    --dry-run
  python manage.py import_microcourse \
    --manifest ../course-source/understand-bollinger-bands/course-manifest.json
fi

# One-time staging superuser bootstrap for Render Free, which has no service shell.
# Enable only deliberately with BOOTSTRAP_STAGING_ADMIN=true, then remove the
# four bootstrap variables from Render after the account has been created.
if [[ "${BOOTSTRAP_STAGING_ADMIN:-false}" =~ ^(1|true|TRUE|yes|YES)$ ]]; then
  : "${STAGING_ADMIN_USERNAME:?STAGING_ADMIN_USERNAME is required for admin bootstrap}"
  : "${STAGING_ADMIN_EMAIL:?STAGING_ADMIN_EMAIL is required for admin bootstrap}"
  : "${STAGING_ADMIN_PASSWORD:?STAGING_ADMIN_PASSWORD is required for admin bootstrap}"

  python manage.py shell -c '
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["STAGING_ADMIN_USERNAME"].strip()
email = os.environ["STAGING_ADMIN_EMAIL"].strip()
password = os.environ["STAGING_ADMIN_PASSWORD"]

existing = User.objects.filter(username=username).first()
if existing:
    if existing.is_superuser and existing.is_staff:
        print("Staging admin bootstrap skipped: requested superuser already exists.")
    else:
        raise SystemExit(
            "Staging admin bootstrap stopped: username exists but is not a superuser. "
            "Choose a different STAGING_ADMIN_USERNAME."
        )
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Staging superuser created.")
'
fi

# Explicit one-time reset for an existing staging superuser. This is separate
# from the create-only bootstrap above so setting BOOTSTRAP_STAGING_ADMIN=true
# cannot silently overwrite an existing account's password.
if [[ "${RESET_STAGING_ADMIN_PASSWORD:-false}" =~ ^(1|true|TRUE|yes|YES)$ ]]; then
  : "${STAGING_ADMIN_USERNAME:?STAGING_ADMIN_USERNAME is required for password reset}"
  : "${STAGING_ADMIN_EMAIL:?STAGING_ADMIN_EMAIL is required for password reset}"
  : "${STAGING_ADMIN_PASSWORD:?STAGING_ADMIN_PASSWORD is required for password reset}"

  python manage.py shell -c '
import os
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()
username = os.environ["STAGING_ADMIN_USERNAME"].strip()
email = os.environ["STAGING_ADMIN_EMAIL"].strip()
password = os.environ["STAGING_ADMIN_PASSWORD"]

user = User.objects.filter(username=username).first()
if user is None:
    raise SystemExit("Staging admin password reset stopped: requested username does not exist.")
if not (user.is_superuser and user.is_staff and user.is_active):
    raise SystemExit("Staging admin password reset stopped: requested account is not an active superuser.")
if not email or not password:
    raise SystemExit("Staging admin password reset stopped: email/password cannot be empty.")
if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
    raise SystemExit("Staging admin password reset stopped: email belongs to a different account.")

# The project uses email-based allauth login. Keep the custom User email and
# allauth EmailAddress record aligned, verified, and primary for this admin.
user.email = email
user.set_password(password)
user.save(update_fields=["email", "password"])

EmailAddress.objects.filter(user=user).update(primary=False)
address, _ = EmailAddress.objects.get_or_create(
    user=user,
    email=email,
    defaults={"verified": True, "primary": True},
)
address.email = email
address.verified = True
address.primary = True
address.save(update_fields=["email", "verified", "primary"])

print("Staging admin password reset and email verification completed.")
'
fi
