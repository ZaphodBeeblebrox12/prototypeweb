#!/usr/bin/env bash
# Render build: deps -> static -> migrate (DATABASE_URL is injected by Render)
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# One-time staging admin bootstrap for Render Free, which has no service shell.
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
