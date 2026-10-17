# Render staging repoint — handoff checklist

**Status (2026-10-17): Academy staging is healthy on the Supabase PostgreSQL URL supplied by the linked environment group. The six corrective schema migrations were applied successfully. Auth email templates are deployed. The requested staging username already exists as a superuser. The bootstrap flag has been returned to false; admin login and course/media workflows remain to be verified.**

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
- Latest branch commit / deployment commit: `95824385ce64e1b1bd562bb849039fb76eee6d61` — staging checkpoint update.
- Prior live deployment: `dep-db9r53jbc2fs73cugb90` — status `live`; build and runtime were healthy.
- Bootstrap-disabled deployment: `dep-db9r5t7avr4c73f4im40`; build succeeded and the replacement instance repeatedly returned HTTP 200 for `/health/`. Render's deploy API still reported `update_in_progress` at the last check, although the instance was serving health checks.
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

## Staging admin login recovery — code committed, reset not yet run

The intended staging admin username already exists and is a Django superuser. The prior one-time bootstrap explicitly skipped existing superusers and did not change their password. The website login page uses email authentication, and the project's custom adapter checks verification via allauth `EmailAddress` rows. A superuser created by the custom user manager may have no such row, which can block the email-based login path.

A guarded reset/verification path has now been added to `backend/build.sh` on `my-new-branch`, in commit `9e4570aa36f5d66802c7ce4d5a6cfedcfc38d197`:

- It is **separate** from `BOOTSTRAP_STAGING_ADMIN`.
- It runs only when `RESET_STAGING_ADMIN_PASSWORD=true`.
- It will only alter the named account if it already exists and is an active superuser.
- It refuses to reset if the requested email belongs to another User account.
- It sets that account's password from `STAGING_ADMIN_PASSWORD`, synchronizes the User email, and creates/marks the matching allauth EmailAddress as verified and primary.
- It logs only a success/failure message; it does not print credentials.
- CI now validates `bash -n build.sh`; the workflow run for commit `b3eb083` is still in progress at the last check.

Next:
1. Wait for CI on latest commit `b3eb0833c1069199be8d6561f172943bf7e6e68c` to pass before deploying.
2. In the Academy Render web service's **service-level Environment Variables**, add `RESET_STAGING_ADMIN_PASSWORD=true`. Leave `BOOTSTRAP_STAGING_ADMIN=false`. The existing username/email/password values stay private in Render.
3. Save and deploy latest commit manually (auto-deploy is off). Check logs for `Staging admin password reset and email verification completed.`
4. Immediately set `RESET_STAGING_ADMIN_PASSWORD=false` and save, then wait for the cleanup deployment to reach Live.
5. Sign in to `https://tradethesis-academy-staging.onrender.com/admin/` using the configured username/password; for the website login, use the configured email/password.
6. After login is verified, remove `STAGING_ADMIN_USERNAME`, `STAGING_ADMIN_EMAIL`, and `STAGING_ADMIN_PASSWORD` and keep both one-time flags false. Never share or commit their values.

Previous recovery history:
- `BOOTSTRAP_STAGING_ADMIN` is currently false.
- Latest deployment `dep-db9r5t7avr4c73f4im40` is Live and its build succeeded.
- No password reset occurred during the prior bootstrap because the existing superuser was skipped.

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
