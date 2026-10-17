# Render staging repoint — handoff checklist

**Status: staging runtime is live; email-template fix has been committed and is being deployed; database identity and admin/course workflows still need validation.**

## Current verified deployment (2026-10-17)

### Public website staging

- Service: `tradethesis-public-staging`
- Service ID: `srv-db9j72m1egvs73ffpfkg`
- Dashboard: https://dashboard.render.com/static/srv-db9j72m1egvs73ffpfkg
- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Live commit observed: `00821b6a62cf62334ce7e6a8952d624067c0c073`
- Publish path: `./site`
- Auto-deploy: off (manual deploy only)

### Django Academy staging

- Service: `tradethesis-academy-staging`
- Service ID: `srv-db9ioke1egvs73feb8ag`
- Dashboard: https://dashboard.render.com/web/srv-db9ioke1egvs73feb8ag
- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Previously live commit: `6c1ac5c100f58dd185eb2b1e7ca9fb9bc3345bed` — production host/origin parsing fix.
- Branch now includes allauth confirmation email template fixes through commit `ec2eb240ba9c440b052ac5f07dfacbab0b847fb8`; deploy separately because auto-deploy is off.
- Build command: `cd backend && bash build.sh`
- Start command: `cd backend && gunicorn config.wsgi:application --workers 2 --threads 4 --timeout 120`
- Health check path: `/health/`
- Health verification on the previously live commit: Render logs recorded repeated `GET /health/ HTTP/1.1` responses with status `200` after startup.
- Migrations logged as applied on the previous live deployment: `academy.0002_course_import_review_workflow` and `academy.0003_course_asset_original_url`.
- Auto-deploy: off (manual deploy only)
- Plan: Free; one instance.

## Authentication issue found and fixed in code

Render logs from the previous deployment show login attempts for unverified accounts failing with HTTP 500 because these custom allauth mail templates were missing:

- `account/email/email_confirmation_message_subject.txt`
- `account/email/email_confirmation_message.txt`
- `account/email/email_confirmation_signup_subject.txt`
- `account/email/email_confirmation_signup.txt`

They have now been added on `my-new-branch`, along with `backend/tests/test_email_confirmation_templates.py`. A new Render deployment is required before confirming the runtime fix.

Email delivery itself is still a separate configuration requirement: base settings default to Django's console email backend and production makes email verification mandatory. Configure a real SMTP/email provider in Render before relying on signup/verification emails. Never store secrets in Git or paste them into chat.

## Next required checks

1. **Confirm database identity before relying on persistent data.** In the Academy service's Render Environment page, verify that `DATABASE_URL` exists and is sourced from the intended durable PostgreSQL database. Do not share or commit its value. If absent, the code falls back to SQLite under the backend directory, which is not a reliable production database on an ephemeral service.
2. The Render workspace currently lists one PostgreSQL instance, `tradeadmin-db`, on the Free plan, with expiry shown as 2026-10-26. Do not assume Academy uses it until `DATABASE_URL` is checked. A read-only query through the connected Render integration was blocked because the database IP allowlist is empty; do not weaken the allowlist just for this check.
3. Test `/admin/` login on Academy staging and test login for an unverified account after the template fix is live. Do not assume a superuser exists. If necessary, use the guarded one-time bootstrap described in `backend/build.sh`; set the required variables privately, confirm the admin exists, then remove the bootstrap variables immediately.
4. Test admin editing/upload of lesson images, preview, protected-media access, and entitlement denial before treating this as production-ready.
5. Decide on durable private-media storage. Academy staging runs on Render Free and files saved on the container filesystem are not durable across restarts/redeploys. Use object storage or an appropriate persistent hosting setup while preserving private media access controls.
6. Both staging services currently have auto-deploy off, so new commits need a manual deploy. The existing `tradeadmin` service must remain untouched on `ZaphodBeeblebrox12/test` / `main`.

## Existing application to leave unchanged

- Service: `tradeadmin`
- Service ID: `srv-darvg4navr4c738cmtl0`
- Dashboard: https://dashboard.render.com/web/srv-darvg4navr4c738cmtl0
- Repository/branch: `ZaphodBeeblebrox12/test` / `main`
- Auto-deploy: on

Do not repoint or redeploy this service as part of staging consolidation.

## Current deployment notes

- The public-site deployment and the first Academy deployment were triggered manually.
- The production settings fix uses `env.list()` for comma-separated host/origin settings instead of calling `.split()` on the list returned by django-environ.
- No secrets were read into the checkpoint, added to Git, or printed into the logs.
