# TradeThesis Academy staging and deployment notes

## Centralised environment configuration

- `backend/.env.example` is the safe, complete template for local configuration. Copy it to `backend/.env` and add local values there. The real `.env` file is git-ignored; do not commit credential values.
- The Render staging service consumes the workspace-level Environment Group `tradethesis-academy-staging-config`, which is created and maintained in the Render Dashboard. The root `render.yaml` references that existing group using `fromGroup` rather than declaring a second Blueprint-managed copy. Secret values are entered only in the Render Dashboard.
- Before syncing/creating the Blueprint, create or confirm that group in Render's Environment Groups dashboard and fill in its values. At minimum, staging requires `DATABASE_URL` (a dedicated Supabase PostgreSQL **Session Pooler** URI) and `RESEND_API_KEY`. Keep the remaining Telegram/payment/provisioning fields blank until those integrations are being tested. `SECRET_KEY` must have a strong random value.
- The Supabase project URL and publishable client key are optional for direct PostgreSQL access. Django connects via `DATABASE_URL`; the database password belongs only inside that private connection URI, not in the publishable key or GitHub.
- Keep staging and production values separate. When production is needed, create a separate production Environment Group; never point staging at a production database or payment credentials.


**Current state (17 October 2026):** the Django Academy code is on open draft PR [#4](https://github.com/ZaphodBeeblebrox12/prototypeweb/pull/4), targeting `my-new-branch`. Backend CI on Python 3.11 and 3.12 previously passed at [run 39006601474](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39006601474) with 695 tests passed and 1 skipped per runtime. Since that verified checkpoint, production settings were hardened to reject missing and SQLite database URLs, and regression tests were added; consult PR #4 for the current CI result. No hosted runtime, staging catalogue data, or live checkout-to-lesson journey has been verified.

## Deployment configuration

The repository-root `render.yaml` is the staging Blueprint. It intentionally has automatic deploys turned off and points at `feature/tradethesis-academy` for this review stage. It runs commands from the repository root and changes into `backend/` for Django; this is important because draft importers read course material stored outside the backend directory.

The Blueprint defines a **Free staging web service** and a `/health/` endpoint; automatic deploys are turned off. It does **not** provision PostgreSQL. Supply a dedicated external PostgreSQL connection as `DATABASE_URL` through Render's dashboard before deploying. The `/health/` endpoint is a basic liveness check and does not prove the database is reachable. Do not create or deploy services automatically as part of CI. When the code is approved and integrated into `my-new-branch`, update the service's linked branch deliberately before enabling any automatic deploy behaviour.

The staging Blueprint uses the custom `apps.core.email_backends.ResendEmailBackend`, which sends through the Resend HTTPS API rather than SMTP. In Render's environment settings, provide `RESEND_API_KEY` and a valid `DEFAULT_FROM_EMAIL`; the sender address/domain must be verified with the email provider before sending to ordinary recipients. Keep the API key out of GitHub. Render Free blocks outbound SMTP on ports 25, 465 and 587, and a free Render Postgres database expires 30 days after creation. Payment-provider credentials must be test-mode keys and webhook endpoints/secrets must point to the staging host. Leave integrations that are not being exercised unconfigured. Set `SITE_BASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` to the actual deployed host if its service name or domain differs from the Blueprint default.

The static website's `site/member-access.html` reads `meta[name="academy-base-url"]`; `site/assets/academy-routing.js` uses it to send login, signup, password-reset and learner-dashboard links to Django. The default points to the planned staging hostname, not proof that a live service exists. Update that single meta value once the actual Academy host is known. Navigation is full-page, so no cross-origin API or token-auth layer is needed for the first release.

## Free-tier staging plan

The Render web service remains on the **Free** compute plan. The Blueprint intentionally does not provision Render Postgres, because this workspace already uses its single active free Postgres slot for the separate TradeAdmin database. Do not delete, repurpose, or point Academy at TradeAdmin.

For a no-cost staging trial, create a separate free-tier PostgreSQL project with a provider that supports external connections (for example, Supabase Free) and set its connection URI as the Academy service's `DATABASE_URL` environment variable in Render. The Blueprint marks this value `sync: false`; keep credentials in the hosting dashboard, never in GitHub. Supabase Free currently allows up to two active free projects and 500 MB database storage per project, but inactive projects can pause after a week and the free plan has no automatic database backups. This is suitable for a temporary QA environment, not durable production data. See the [Supabase pricing](https://supabase.com/pricing) and [project pausing](https://supabase.com/docs/guides/platform/free-project-pausing) documentation.

The Blueprint now uses Resend's HTTPS API for account-verification and password-reset messages, so it does not need outbound SMTP ports or a paid Render web-service upgrade. This path is only ready for acceptance testing after `RESEND_API_KEY` is configured and `DEFAULT_FROM_EMAIL` uses a provider-verified sender. Until then, don't count signup/recovery email acceptance as passed. No provider account or paid resource is created by this repository configuration.

## One-time staging catalogue import

The three importers are deliberately create-only and draft-only. They create no pricing Plan or CourseOffer, publish no lessons, and do not provision delivery channels. First validate the whole catalogue without making database changes:

```bash
cd backend
python manage.py seed_academy_catalogue
```

Only after validation passes and the intended dedicated staging database is confirmed, import the complete catalogue **once**:

```bash
python manage.py seed_academy_catalogue --apply
```

This orchestration command preflights the three canonical source importers, refuses to overwrite any of the three course slugs, and imports all three courses in a single database transaction. If the post-import checks fail, the complete batch rolls back. Expected total: 16 unpublished modules, 78 unpublished lessons, and 78 separate instructor-material records, with no course offers created.

Expected draft content: Trading Path (4 modules / 30 lessons), Support & Resistance (6 modules / 18 lessons), and Volume Price Analysis (6 modules / 30 lessons). These are source/importer expectations, not claims that records already exist in a deployed database. The commands refuse to overwrite a course slug that already exists; inspect the current catalogue before retrying after any partial/manual import.

Do not make a course saleable merely because it imported. Review lesson bodies, media and figure readability first. For each approved product, create its own dedicated hidden one-time Plan and CourseOffer, confirm the exact displayed price/currency and provider routing, and only then publish the approved course/modules/lessons and activate its offer. Keep CONSTRUCT's 12-calendar-month community term separate from course access, and add the required channel mappings only when the actual destination IDs are confirmed.

## Staging acceptance sequence

1. Confirm `/health/` returns HTTP 200. Independently confirm the configured database connection from the service shell with `python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor)"`; it must report `postgresql`.
2. Configure and verify signup email, login/logout, email confirmation and password recovery.
3. Inspect all imported draft courses in Django admin; verify lesson count/order, learner-facing content and separate instructor notes/answer keys.
4. Check preview/locked/paid/expired lesson behaviour, Markdown rendering, image zoom on desktop/mobile and saved progress.
5. Use payment-provider test credentials to verify pending checkout, success webhook retries, failures, refund/revocation and replay/idempotency.
6. Verify CONSTRUCT's course entitlement and separate community expiry, plus Telegram/Discord link and channel reconciliation.
7. Test member links from the deployed static site, plus mobile layout and password/checkout redirects.

## Operational notes

- Run migrations via the existing `backend/build.sh`; source imports are separate manual operations and should not run on every deploy.
- Confirm a database backup/restore procedure and persistent media handling before production use.
- Configure a staff account through the hosting provider's secure console.
- Keep PR #4 in draft while these acceptance gates are open. Do not merge or deploy to `main`; the integration target remains `my-new-branch`.
