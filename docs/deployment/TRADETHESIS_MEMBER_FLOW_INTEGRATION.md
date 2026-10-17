# TradeThesis member-flow integration and legacy cleanup

## Scope and route ownership

- Public marketing, courses overview and editorial pages are served by the static TradeThesis site in `site/`.
- Academy root (`/`) redirects to `TRADETHESIS_PUBLIC_SITE_URL`, defaulting to `https://tradethesis-public-staging.onrender.com/`. The legacy TradeAdmin landing page is no longer a route target.
- Django/allauth owns login, signup, password reset, email verification and sessions. The login/signup routes explicitly use `auth/tradethesis_login.html` and `auth/tradethesis_signup.html`.
- The protected `/dashboard/` route renders `accounts/member_desk.html` using authenticated user data: the published Academy catalogue, active course entitlements, saved lesson progress, account subscriptions, payment records and notifications. The live template uses the approved light, compact mock-style dashboard, with real account values and functional seven-section navigation; the static preview remains visual-only.
- The static `site/member-area-preview.html` is visual-only and contains sample data; it is not the live dashboard.

## Legacy cleanup

Removed the retired TradeAdmin landing page and its pricing tests, duplicate old root template, old Bootstrap member dashboard, previous split-layout login/signup templates and stylesheet, duplicate allauth login/signup templates, and the superseded dashboard design preview. The active email verification, password reset, account management, Academy, payment, billing, support, legal/policy, admin and API functionality is retained.

The former `index` URL name is preserved for backwards-compatible URL reversing, but delegates to the public-site redirect. The `landing` name also redirects and is no longer a Django-rendered marketing page.

## Staging deployment and validation record

- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Public static-site service and Django Academy service are configured for manual deployment (auto-deploy disabled).
- Deployment remains a separate explicit action; do not touch the separate legacy `tradeadmin` service on `ZaphodBeeblebrox12/test` / `main`.

### Current staging checkpoint — 2026-10-17

- Branch: `my-new-branch`.
- Application code and live member desk template deployed from commit `92dbfed6acd3186bc71df76f0d13d9042413a93d`.
- Academy staging service: `srv-db9ioke1egvs73feb8ag`; deployment `dep-db9t3hrbc2fs73d4nbv0`; status `live`; finished at `2026-10-17T19:53:30Z`.
- Backend CI: [run 39063976526](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39063976526) — successful on Python 3.11 and 3.12, each with 673 passing tests, 187 warnings and 11 subtests passed.
- The Render build collected static files, and post-rollout `/health/` probes returned HTTP 200.
- The public static-site service was not redeployed as part of this dashboard fix. The separate legacy `tradeadmin` service and `main` branch remain untouched.
- **Owner visual acceptance confirmed on 2026-10-18:** the user signed in and confirmed the newly deployed mock-style member dashboard is visible, rather than the legacy dashboard. The authenticated landing/visual acceptance issue is closed.
### Member journey acceptance checkpoint — 2026-10-18

- Latest tested/deployed application revision: `057c372af7e658d5e49f367be717ae1515578ea3` on `my-new-branch`.
- Academy staging service: `srv-db9ioke1egvs73feb8ag`; deployment `dep-db9tf9bbc2fs73d5rchg`; status `live`; finished at `2026-10-17T20:18:22Z`.
- Backend CI: [run 39065727801](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39065727801) — green on Python 3.11 and 3.12, each with 686 passing tests, 200 warnings and 11 subtests passed. Focused Academy regressions report 15 passing tests, 9 warnings and 4 subtests per version.
- Member journey improvements: opening an accessible lesson writes an in-progress resume point; completed progress cannot regress; dashboard and Academy resume links target the most recently visited unfinished lesson the member can access; progress totals exclude unpublished lessons; expired-entitlement denial is covered; Telegram/Discord unlink mutations require POST.
- Render build completed, Gunicorn started at approximately `2026-10-17T20:18:06Z`, and repeated post-rollout `/health/` requests returned HTTP 200.
- The owner has confirmed the new dashboard visual is visible. Automated tests cover the member journey and connection-action security; a final manual spot-check of resume behavior on the owner's own account remains useful. No live payment/provider transaction was performed as part of this milestone.
- Advisory limitation: Black and mypy are `continue-on-error` in CI. The mypy step reports existing typing findings (18 errors in 8 files, including constraint keyword typings, `timezone.timedelta` annotations and Telegram result typing). They do not fail required CI but remain technical debt.
- The public static-site service was not redeployed; `main` and the separate legacy `tradeadmin` service remain untouched.


### Admin Desk staging deployment checkpoint — 2026-10-18

- Admin Desk code passed [backend CI run 39070357094](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39070357094): 699 passed, 213 warnings and 11 subtests passed on each of Python 3.11 and 3.12.
- Render Academy staging service `tradethesis-academy-staging` (`srv-db9ioke1egvs73feb8ag`) is now live on branch head `1329867c081cdd1ac5b96dab833b57d4ce402f69`, deployment `dep-db9uic61egvs738ma45g`. Render recorded the rollout complete at `2026-10-17T21:33:14Z`.
- The new instance started Gunicorn successfully; Render health probes recorded HTTP 200 on `/health/` after rollout. The service log query found no error- or warning-level entries in the checked rollout window.
- Public URL: https://tradethesis-academy-staging.onrender.com. This execution environment could not resolve/access the public Render hostname, so authenticated route rendering for `/staff/admin-desk/`, continued operation of `/staff/ops/`, and Django admin visual acceptance still need a browser check by the owner.
- The separate static-site service was not redeployed. The legacy `tradeadmin` service and `main` branch remain untouched.
