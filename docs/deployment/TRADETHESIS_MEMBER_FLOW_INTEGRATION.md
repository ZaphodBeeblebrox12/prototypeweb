# TradeThesis member-flow integration and legacy cleanup

## Scope and route ownership

- Public marketing, courses overview and editorial pages are served by the static TradeThesis site in `site/`.
- Academy root (`/`) redirects to `TRADETHESIS_PUBLIC_SITE_URL`, defaulting to `https://tradethesis-public-staging.onrender.com/`. The legacy TradeAdmin landing page is no longer a route target.
- Django/allauth owns login, signup, password reset, email verification and sessions. The login/signup routes explicitly use `auth/tradethesis_login.html` and `auth/tradethesis_signup.html`.
- The protected `/dashboard/` route renders `accounts/member_desk.html` using authenticated user data: the published Academy catalogue, active course entitlements, saved lesson progress, account subscriptions, payment records and notifications.
- The static `site/member-area-preview.html` is visual-only and contains sample data; it is not the live dashboard.

## Legacy cleanup

Removed the retired TradeAdmin landing page and its pricing tests, duplicate old root template, old Bootstrap member dashboard, previous split-layout login/signup templates and stylesheet, duplicate allauth login/signup templates, and the superseded dashboard design preview. The active email verification, password reset, account management, Academy, payment, billing, support, legal/policy, admin and API functionality is retained.

The former `index` URL name is preserved for backwards-compatible URL reversing, but delegates to the public-site redirect. The `landing` name also redirects and is no longer a Django-rendered marketing page.

## Staging deployment and validation record

- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Public static-site service and Django Academy service are configured for manual deployment (auto-deploy disabled).
- Deployment remains a separate explicit action; do not touch the separate legacy `tradeadmin` service on `ZaphodBeeblebrox12/test` / `main`.

Update this section with the final commit, CI results, deployment IDs and verified public/auth/dashboard paths after rollout. Do not describe browser login as verified unless a real login journey was tested.
