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

## Staging admin login recovery — reset completed; login test pending

The intended staging admin username already exists and is a Django superuser. The prior one-time bootstrap skipped existing superusers and did not change their password. The website login uses email authentication, and the custom adapter relies on allauth `EmailAddress` records for verification. The existing admin had to be recovered so both the account password and verified primary email would be aligned.

### Code and validation

A separate guarded recovery path was added to `backend/build.sh` on `my-new-branch`, commit `9e4570aa36f5d66802c7ce4d5a6cfedcfc38d197`:

- Runs only when `RESET_STAGING_ADMIN_PASSWORD=true`.
- Only modifies the named account if it already exists as an active superuser.
- Refuses the reset if the supplied email belongs to another Django User.
- Updates the existing account password from `STAGING_ADMIN_PASSWORD`, synchronizes the User email, and creates/marks the matching allauth EmailAddress as verified and primary.
- Does not log credentials.

GitHub Actions run [39056557130](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39056557130) passed on Python 3.11 and 3.12, including `bash -n build.sh`, `makemigrations --check --dry-run`, focused Academy regressions and the full test suites.

### Reset performed in Render

- Reset-enabled deployment: `dep-db9rj8gm7kps73eg1rh0`; it reached Live.
- Build log explicitly confirmed: `Staging admin password reset and email verification completed.`
- Reset-disabled cleanup deployment: `dep-db9rk4brjlhs73fu28o0`; status `live` as of 2026-10-17 18:12:18 UTC.
- The cleanup instance returned HTTP 200 for `/health/`.
- `RESET_STAGING_ADMIN_PASSWORD` has been set back to `false`. `BOOTSTRAP_STAGING_ADMIN` remains `false`.
- No credential values were read into Git, logs, or chat.

### Next

1. Test the website login at `https://tradethesis-academy-staging.onrender.com/accounts/login/` using `STAGING_ADMIN_EMAIL` and the password now stored in `STAGING_ADMIN_PASSWORD` in Render. Do not paste either value into chat.
2. For Django's direct admin login at `/admin/`, use `STAGING_ADMIN_USERNAME` with that same reset password.
3. If sign-in works, remove `STAGING_ADMIN_USERNAME`, `STAGING_ADMIN_EMAIL`, and `STAGING_ADMIN_PASSWORD` from Academy's Render service variables. Keep both one-time flags false. Save the change and allow the resulting deployment to finish.
4. If the website login still fails, record only the on-screen error text; do not repeat the reset unless logs show the reset action failed.


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
