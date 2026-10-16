# TradeThesis Academy staging and deployment notes

**Current state:** the Django Academy code is on draft PR #4 targeting `my-new-branch`. Backend CI (Python 3.11 and 3.12), the Support & Resistance browser smoke test, and the integration-target guard passed at `607924fdd73725edf2fbe711aea35044466a353d`. No hosted runtime, staging catalogue data, or live checkout-to-lesson journey has been verified.

## Deployment configuration

The repository-root `render.yaml` is the staging Blueprint. It intentionally has automatic deploys turned off and points at `feature/tradethesis-academy` for this review stage. It runs commands from the repository root and changes into `backend/` for Django; this is important because draft importers read course material stored outside the backend directory.

The Blueprint defines a staging web service, PostgreSQL connection through `DATABASE_URL`, and a `/health/` check. Do not create or deploy the services automatically as part of CI. When the code is approved and integrated into `my-new-branch`, update the service's linked branch deliberately before enabling any automatic deploy behaviour.

Before a hosted staging run, configure SMTP credentials and a provider-supported port for account verification and password recovery. Important Render Free-plan limits: free web services cannot send outbound SMTP traffic on ports 25, 465 or 587, and a free Postgres database expires 30 days after creation. Use a permitted SMTP option or a paid web-service plan for email-verification acceptance; do not treat the free database as durable staging storage. Payment-provider credentials must be test-mode keys and webhook endpoints/secrets must point to the staging host. Leave integrations that are not being exercised unconfigured. Set `SITE_BASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` to the actual deployed host if its service name or domain differs from the Blueprint default.

The static website's `site/member-access.html` reads `meta[name="academy-base-url"]`; `site/assets/academy-routing.js` uses it to send login, signup, password-reset and learner-dashboard links to Django. The default points to the planned staging hostname, not proof that a live service exists. Update that single meta value once the actual Academy host is known. Navigation is full-page, so no cross-origin API or token-auth layer is needed for the first release.

## One-time staging catalogue import

The three importers are deliberately create-only and draft-only. They create no pricing Plan or CourseOffer, publish no lessons, and do not provision delivery channels. First validate all source packages without making database changes:

```bash
cd backend
python manage.py seed_trading_path
python manage.py seed_support_resistance
python manage.py seed_volume_price_analysis
```

Only after those validations pass and the intended staging database is confirmed, run each importer **once** against that database:

```bash
python manage.py seed_trading_path --apply
python manage.py seed_support_resistance --apply
python manage.py seed_volume_price_analysis --apply
```

Expected draft content: Trading Path (4 modules / 30 lessons), Support & Resistance (6 modules / 18 lessons), and Volume Price Analysis (6 modules / 30 lessons). These are source/importer expectations, not claims that records already exist in a deployed database. The commands refuse to overwrite a course slug that already exists; inspect the current catalogue before retrying after any partial/manual import.

Do not make a course saleable merely because it imported. Review lesson bodies, media and figure readability first. For each approved product, create its own dedicated hidden one-time Plan and CourseOffer, confirm the exact displayed price/currency and provider routing, and only then publish the approved course/modules/lessons and activate its offer. Keep CONSTRUCT's 12-calendar-month community term separate from course access, and add the required channel mappings only when the actual destination IDs are confirmed.

## Staging acceptance sequence

1. Confirm `/health/` returns HTTP 200 and the application is connected to its staging PostgreSQL database.
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
