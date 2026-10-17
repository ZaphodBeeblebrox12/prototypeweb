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
- The deeper functional acceptance pass is still the next milestone: test the seven-section navigation and mobile layout, verify course access/lesson progress/resume against a real learner account, and confirm account connection, billing, profile, support and logout actions work as intended. Keep payment/provider behaviour truthful; do not treat a visible CTA as proof that a payment or external integration completed.
