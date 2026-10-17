# Render staging repoint — handoff checklist

**Status: current Academy runtime is live and healthy; code tests and migration-state checks pass. The latest schema migrations are committed but deliberately not deployed until the actual database configuration is verified. Admin and course/media workflows still need live validation.**

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
- Current live commit: `121a81b65cf964d6163404d9eee6ee495b1d5cb7` — auth-template fix and staging checkpoint.
- Current live deployment ID: `dep-db9ql4m1egvs73897700`; status `live`; deploy event succeeded at 2026-10-17 17:06 UTC.
- Latest Git branch commit at this checkpoint: `40e4d123c8f5bf310661a7a7b8e2edf579f02d12`. It includes six migration files and the now-required CI migration check; those migration changes are not yet deployed to Render.
- Build command: `cd backend && bash build.sh`
- Start command: `cd backend && gunicorn config.wsgi:application --workers 2 --threads 4 --timeout 120`
- Health check path: `/health/`
- Health verification: Render logs on the current live deployment showed repeated `GET /health/ HTTP/1.1` responses with status `200` after the new instance started.
- The previous live build applied `academy.0002_course_import_review_workflow` and `academy.0003_course_asset_original_url`.
- Auto-deploy: off (manual deploy only)
- Plan: Free; one instance.

## Authentication email templates — fixed and deployed

Render logs from the earlier deployment recorded HTTP 500 for a login attempt involving an unverified account because Allauth could not find custom confirmation email subject/body templates. The following have now been added on `my-new-branch` and included in the live commit `121a81b`:

- `backend/templates/account/email/email_confirmation_message_subject.txt`
- `backend/templates/account/email/email_confirmation_message.txt`
- `backend/templates/account/email/email_confirmation_signup_subject.txt`
- `backend/templates/account/email/email_confirmation_signup.txt`
- Regression test: `backend/tests/test_email_confirmation_templates.py`

GitHub Actions run [39052070511](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39052070511) passed on Python 3.11 and 3.12 with 671 passed, 1 skipped, 188 warnings, and 4 subtests passed. The confirmation template regression tests passed. A user login/confirmation flow has not yet been manually re-tested on the live site.

Email delivery itself is still a separate configuration requirement: base settings default to Django's console email backend and production makes email verification mandatory. Configure a real SMTP/email provider in Render before relying on signup/verification emails. Never store secrets in Git or paste them into chat.

## Django migration drift — corrected in Git, waiting for safe deployment

Render's build warned that model changes were missing migrations in six apps. A GitHub Actions diagnostic captured the exact Django-generated migrations, and these have been added to `my-new-branch`:

- `apps/accounts/migrations/0010_rename_accounts_se_user_ts_accounts_se_user_id_7c771c_idx_and_more.py`
- `apps/disputes/migrations/0004_rename_disputes_d_status_disputes_di_status_124397_idx_and_more.py`
- `apps/evidence/migrations/0004_rename_evidence_cr_sub_ts_evidence_ca_subscri_6f5bed_idx_and_more.py`
- `apps/policies/migrations/0005_rename_policies_pa_user_ts_policies_po_user_id_d175c7_idx_and_more.py`
- `apps/subscriptions/migrations/0019_alter_geoplanprice_interval_alter_planprice_interval.py`
- `apps/support/migrations/0005_rename_support_tm_ticket_ts_support_tic_ticket__0cd9bd_idx.py`

The generated operations consist of index renames plus an explicit `card_fingerprint` field update and billing interval-choice updates. The CI workflow now requires `python manage.py makemigrations --check --dry-run` (no longer advisory).

GitHub Actions run [39052768361](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39052768361) succeeded on Python 3.11 and 3.12. Both migration checks reported `No changes detected`, and each complete test suite reported 671 passed, 1 skipped, 188 warnings, and 4 subtests passed. The migration files are committed and tested but should not be deployed until Academy's `DATABASE_URL` is confirmed.

## Next required checks

1. **Confirm database identity before deploying the new migrations.** In Academy staging's Render Environment page, check that `DATABASE_URL` exists and is sourced from the intended durable PostgreSQL database. Do not share or commit the value. If absent, the code falls back to SQLite under the backend directory, which is not a reliable database on an ephemeral service.
2. The Render workspace currently lists one PostgreSQL instance, `tradeadmin-db`, on the Free plan, with expiry shown as 2026-10-26. Do not assume Academy uses it until the service's `DATABASE_URL` is checked. A read-only query through the connected Render integration was blocked because the DB IP allowlist is empty; do not weaken the allowlist just for this check.
3. After database configuration is verified, deploy the latest `my-new-branch` commit manually to Academy staging, watch the six new migrations apply, then recheck `/health/` and deploy status.
4. Test `/admin/` login on Academy staging and test login for an unverified account after the template fix is live. Do not assume a superuser exists. If necessary, use the guarded one-time bootstrap described in `backend/build.sh`; set the required variables privately, confirm the admin exists, then remove the bootstrap variables immediately.
5. Test admin editing/upload of lesson images, preview, protected-media access, and entitlement denial before treating this as production-ready.
6. Decide on durable private-media storage. Academy staging runs on Render Free and files saved on the container filesystem are not durable across restarts/redeploys. Use object storage or an appropriate persistent hosting setup while preserving private media access controls.
7. Both staging services currently have auto-deploy off, so new commits need a manual deploy. The existing `tradeadmin` service must remain untouched on `ZaphodBeeblebrox12/test` / `main`.

## Existing application to leave unchanged

- Service: `tradeadmin`
- Service ID: `srv-darvg4navr4c738cmtl0`
- Dashboard: https://dashboard.render.com/web/srv-darvg4navr4c738cmtl0
- Repository/branch: `ZaphodBeeblebrox12/test` / `main`
- Auto-deploy: on

Do not repoint or redeploy this service as part of staging consolidation.

## Current deployment notes

- Both public-site and Academy deploys have been triggered manually.
- The production settings fix uses `env.list()` for comma-separated host/origin settings instead of calling `.split()` on the list returned by django-environ.
- No secrets were read into the checkpoint, added to Git, or printed into the logs.
