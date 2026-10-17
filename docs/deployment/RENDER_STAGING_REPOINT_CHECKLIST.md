# Render staging repoint — handoff checklist

**Status (2026-10-17): Academy staging is live and healthy on the Supabase PostgreSQL URL supplied by the linked environment group. The six corrective schema migrations were applied successfully. Auth email templates are deployed. The one-time admin bootstrap is disabled again because the required username value was empty/missing; admin sign-in and course/media workflows remain to be verified.**

## Current verified deployment

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
- Current live commit: `bd192e6cd699a03194509c755f7ca8818b9c7da0`
- Latest successful deployment: `dep-db9r053rjlhs73frrt6g` — status `live`; its runtime was healthy after rollout.
- Prior migration deployment: `dep-db9qualg1s2s739nqj20` — status `live`; deployed commit `bd192e6cd699a03194509c755f7ca8818b9c7da0`.
- Build command: `cd backend && bash build.sh`
- Start command: `cd backend && gunicorn config.wsgi:application --workers 2 --threads 4 --timeout 120`
- Health check path: `/health/`
- Runtime health: logs show repeated `GET /health/ HTTP/1.1` with status `200` from the replacement instance after both successful deployments.
- Database: `DATABASE_URL` is provided via the linked Render environment group `tradethesis-academy-staging-config`. The user observed a Supabase pooler hostname with path `/postgres` (region appears to be ap-northeast-1). Do not copy the full URL into chat or Git. Database connectivity is proven by the successful migrations and database-aware `/health/` checks. Render service is in Oregon; Supabase region is likely Tokyo, which works but adds cross-region latency.
- Auto-deploy: off (manual deploy only)
- Plan: Free; one instance.

## Schema migrations — deployed successfully

GitHub Actions run [39052768361](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39052768361) passed on Python 3.11 and 3.12. Both migration checks reported `No changes detected`; each complete test suite reported 671 passed, 1 skipped, 188 warnings, and 4 subtests passed.

The following generated migrations have been applied to the configured Supabase PostgreSQL database, each logged as `OK` by Render:

- `apps/accounts/migrations/0010_rename_accounts_se_user_ts_accounts_se_user_id_7c771c_idx_and_more.py`
- `apps/disputes/migrations/0004_rename_disputes_d_status_disputes_di_status_124397_idx_and_more.py`
- `apps/evidence/migrations/0004_rename_evidence_cr_sub_ts_evidence_ca_subscri_6f5bed_idx_and_more.py`
- `apps/policies/migrations/0005_rename_policies_pa_user_ts_policies_po_user_id_d175c7_idx_and_more.py`
- `apps/subscriptions/migrations/0019_alter_geoplanprice_interval_alter_planprice_interval.py`
- `apps/support/migrations/0005_rename_support_tm_ticket_ts_support_tic_ticket__0cd9bd_idx.py`

Operations are index renames plus the `card_fingerprint` field update and subscription interval-choice updates. The CI workflow now requires `python manage.py makemigrations --check --dry-run`.

## Authentication email templates — fixed and deployed

Render logs from an earlier deployment recorded HTTP 500 for a login attempt involving an unverified account because Allauth could not find custom confirmation email subject/body templates. The following are committed on `my-new-branch` and included in the live build:

- `backend/templates/account/email/email_confirmation_message_subject.txt`
- `backend/templates/account/email/email_confirmation_message.txt`
- `backend/templates/account/email/email_confirmation_signup_subject.txt`
- `backend/templates/account/email/email_confirmation_signup.txt`
- Regression test: `backend/tests/test_email_confirmation_templates.py`

GitHub Actions run [39052070511](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39052070511) passed both Python versions with 671 passed, 1 skipped, 188 warnings, and 4 subtests passed; template regression tests passed. Manually testing login and confirmation on the live service remains outstanding.

Email delivery is separately configured: base settings default to Django's console email backend and production requires email verification. Configure a real SMTP/email provider in Render before relying on signup/verification emails. Never store secrets in Git or paste them into chat.

## Staging admin bootstrap — outstanding

The guarded bootstrap in `backend/build.sh` requires all four non-empty service-level variables:

- `BOOTSTRAP_STAGING_ADMIN`
- `STAGING_ADMIN_USERNAME`
- `STAGING_ADMIN_EMAIL`
- `STAGING_ADMIN_PASSWORD`

A deploy was triggered with `BOOTSTRAP_STAGING_ADMIN=true`, but it failed before creating the admin because Render's build log reported `STAGING_ADMIN_USERNAME is required for admin bootstrap`. The user-facing environment page previously showed masked rows for the four variables, but the username value reaching the build was empty or absent; this must be corrected directly in the **Academy web service's Environment Variables**, not by sharing values in chat.

Recovery already completed:
- `BOOTSTRAP_STAGING_ADMIN` was set back to `false`.
- The resulting deployment `dep-db9r053rjlhs73frrt6g` succeeded and is Live.
- The code/schema deployment remains healthy; no new migration work is needed.
- No superuser creation was confirmed.

Next:
1. In Academy service Environment (not just the linked config group), edit the service-level variables and enter a non-empty, intended username, email, and a strong password. Keep them private.
2. Set `BOOTSTRAP_STAGING_ADMIN=true` only after the three values are populated.
3. Save/trigger deployment and confirm the build log says `Staging superuser created.` or `requested superuser already exists`. If it fails, do not keep repeatedly redeploying; inspect the precise error.
4. Sign in at `https://tradethesis-academy-staging.onrender.com/admin/` using the chosen credentials.
5. Only after successful login, remove all four bootstrap variables (or at minimum disable the flag and remove the credentials), save, and deploy again.

## Next workflow tests

After admin login is verified:
1. Test updating lesson text in Academy admin.
2. Add several URL-backed lesson images, then replace one with an uploaded file; verify preview/learning room renders the selected images only in the intended tab.
3. Test protected media access while logged out and with a user lacking entitlement.
4. Decide on durable private-media storage. Academy runs on Render Free, and uploaded files on its container filesystem are not durable across restarts/redeployments. Use object storage or a suitable persistent hosting setup while preserving private-media access controls.
5. Both staging services have auto-deploy off and need manual deploys. Leave the existing `tradeadmin` service untouched on `ZaphodBeeblebrox12/test` / `main`.

## Existing application to leave unchanged

- Service: `tradeadmin`
- Service ID: `srv-darvg4navr4c738cmtl0`
- Dashboard: https://dashboard.render.com/web/srv-darvg4navr4c738cmtl0
- Repository/branch: `ZaphodBeeblebrox12/test` / `main`
- Auto-deploy: on

Do not repoint or redeploy this service as part of staging consolidation.

## Security notes

- No database URL, password, API key, or bootstrap password was committed to Git or copied into this checkpoint.
- The `DATABASE_URL` should remain in the linked Render environment group; don't unlink the group or paste its secret value into chat.
