# Frontend / Django Backend Integration — TradeThesis

**Target repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Working branch:** `my-new-branch`  
**Status:** Django Academy is imported on draft PR #4, which targets `my-new-branch`. Routes, catalogue seed, public-to-backend routing and the end-to-end learner journey are not yet deployed or verified.

## 1. Verified current state

### This repository: the product and content source

The branch contains the static TradeThesis website, course-room prototype, learner resources, brand assets, micro-course source and Support & Resistance production package. Relevant entry points include:

- Public-site review: `site/00_OPEN_INTERACTIVE_PREVIEW.html` and `site/MOBILE_PREVIEW.html`.
- Public pages: `site/index.html`, `site/courses.html`, `site/trading-path.html`, `site/construct.html`, `site/live-class.html`.
- Current member UI prototypes: `site/member-access.html` and `site/member-area.html`.
- Starter drip course source: `course-source/starter-drip-course/`.
- CONSTRUCT source: `course-source/construct/`.
- Volume Price Analysis source: `course-source/volume-price-analysis/`.
- Support & Resistance course: `course-content/support-resistance/`.
- Existing curriculum metadata: `course-integration/curriculum.json`.

The draft integration PR now includes a self-contained Django project under `backend/` (`backend/manage.py`, `backend/config/`, app code, migrations and tests). Until that PR is integrated and deployed, the member screens on `my-new-branch` remain static previews rather than secure account pages. The imported runtime itself is not yet connected to the public pages or verified in a staging deployment.

### Django Academy implementation imported on a draft feature PR

The source implementation remains in `ZaphodBeeblebrox12/test`, branch `feature/tradethesis-academy`. A copy has been imported into this repository's `backend/` on draft [PR #4](https://github.com/ZaphodBeeblebrox12/prototypeweb/pull/4), targeting `my-new-branch`. It includes Academy models, protected learner views, course-offer/payment hooks, progress handling and templates. Its route set includes:

- `/learn/` — authenticated learning home;
- `/learn/course/<course_slug>/` — course overview and access state;
- `/learn/course/<course_slug>/lesson/<lesson_uuid>/` — authorized lesson detail;
- `/learn/lesson/<lesson_uuid>/progress/` — authenticated POST for progress;
- `/accounts/login/` and `/accounts/signup/` — existing Django Allauth pages.

The learner views are server-rendered Django pages, not a published public JSON API. Their URL names and same-origin CSRF/session behaviour should be used rather than guessing API endpoints from static HTML.

## Catalogue lifecycle and future expansion

The catalogue is intentionally still in development and should grow as additional courses become ready. Do not design it as a fixed set of hard-coded products. The current static content file `site/assets/course-catalogue-data.js` separates course data from reusable display templates, which is a useful prototype pattern; in production, published course/offer data should come from the authoritative backend/catalogue records.

Represent lifecycle states deliberately (at minimum draft, in development, published/available, and archived). Draft and in-development material should not be represented as purchasable or enrolled course content. The public page now communicates that development is ongoing; keep this status statement accurate and revise it only when the product owner changes the message.

When adding a course:
1. Create its own stable identifier/slug and course/module/lesson records from the approved source manifest.
2. Verify the course summary, learning outcomes, estimated time, course level, offer price, one-time/subscription semantics, access duration, included community or support, delivery mode and availability state.
3. Keep curriculum and entitlements separate from other course products unless an explicit bundle relationship has been implemented and tested.
4. Include it in the public catalogue only when the intended preview/published state allows it; derive category filters and counts from available catalogue data rather than fixed numbers.
5. Check desktop/mobile presentation, search/filter behaviour, empty states and all affected member/checkout journeys.
6. Add the new product to admin workflows and regression fixtures so future additions do not require a site redesign.

## 2. Proposed integration approach

Prefer full-page navigation for the first release; do not add cross-origin token authentication or build a new frontend API layer unless the deployment requires it.

**Preferred topology:** serve public marketing pages and Django learner/authentication routes from the same origin, using Django URL routing or a reverse proxy so `/learn/`, `/accounts/`, checkout and required media routes reach Django. If the final host cannot provide that arrangement, use a dedicated learning host with ordinary browser navigation and explicitly configure session/security boundaries. The hosting/domain choice remains a deployment decision, not something inferred from this static repository.

The public-site design system should be retained when turning member/auth/academy pages into production routes. Reuse the light TradeThesis palette, typography, content width, navigation and responsive behaviour; do not replace the current product design with an unrelated generic dashboard.

## 3. Product and content mapping

Create explicit Course/Module/Lesson records from the approved source metadata. The source files and manifests are authoring material; they are not a reason to copy every paid lesson body into public static HTML.

| Product / content source | Intended backend representation | Important rule |
|---|---|---|
| ₹999 Trading Path / starter drip | One Course with the 30 ordered daily lessons, checkpoint metadata and its own CourseOffer | One-time payment grants course entitlement only; lifetime access must not imply bot access. Keep drip pacing separate from expiry. |
| Support & Resistance | One Course, six modules and 18 lessons mapped from `course-content/support-resistance/production/course_content_manifest.json` | Preserve the three approved ChartLab placements. Instructor answer keys and internal feedback must not be added to learner payloads. |
| Volume Price Analysis | Separate Course and ordered modules/lessons from `course-source/volume-price-analysis/` | Keep it distinct from Support & Resistance and the Trading Path; do not merge curricula just because they share the member area. |
| CONSTRUCT | Its own Course/offer and curriculum, using `course-source/construct/` as source of truth | ₹17,000 core offer and included 12-month community access are separate entitlements/business rules. The current one-course CourseOffer does not by itself model an included community bundle; add explicit bundle/community entitlement support before selling through this integration. |
| Six-week live classroom | Separate offer/enrolment path, not a synonym for CONSTRUCT | Do not represent cohort dates, sessions or fulfilment as available until the real delivery workflow is configured. |
| Future micro-courses | Each course gets its own stable slug, published modules/lessons and explicit offer if sold separately | Catalogue cards, enrolment and access must use backend records, not client-side price or access flags. |

The mapping above is the proposed implementation model; it does not mean these products have been seeded or verified in Django yet. Before seeding, reconcile each source's current lesson manifest and offer rules to the actual course catalogue and confirm any product naming/pricing changes.

## 4. Frontend changes required

1. **Member access:** replace the preview form behaviour with ordinary links/forms to the real Django login, sign-up and account-recovery routes. Do not display a success message unless the server confirms the action.
2. **Member area:** replace hard-coded preview enrolments/progress with the authenticated `/learn/` page. Keep the screen orientation and brand language; render courses/progress from backend state.
3. **Course cards and detail pages:** public pages may preview course names, summaries and public offer metadata. Paid lesson bodies, answer keys, learner submissions and private downloads must only be delivered after server-side permission checks.
4. **Checkout:** link each CTA to a server-resolved active offer. Never trust an amount/discount supplied by the browser or grant access from a success-return URL alone. Course access follows verified provider payment processing and an idempotent entitlement grant.
5. **Lesson progress:** use the Django lesson/progress routes with same-origin session and CSRF protection. Show “saved” only after a successful response; preserve a visible error/retry state on failure.
6. **Drip release:** release eligibility is computed by the backend. The front end presents release state but cannot unlock a lesson by changing JavaScript or DOM state.
7. **Media and charts:** preserve readability and zoom/open controls. Any confidential reference/answer state must be separately protected at delivery time; CSS-only hiding is not permission enforcement.
8. **Sitewide UX:** verify public site, login/signup/recovery, member home, course overview, lesson, checkout, locked lesson, progress/error states and mobile view as one continuous journey.

## 5. Backend and release gates

- Keep payment confirmation, entitlement grants, refunds/chargebacks and progress writes server-side and idempotent.
- Do not reuse subscription/bot permissions as Academy course access.
- Confirm one-time pricing, geo-pricing, checkout evidence/terms, provider webhooks and refund/dispute behaviour end to end.
- Ensure course entitlement and community entitlement rules are distinct where required.
- Choose private storage/delivery for paid lesson bodies and protected reference material before learner launch.
- **Repository privacy blocker:** the current GitHub repository is public and contains paid course source plus internal instructional/reference material. A private Django route does not make copies already committed to a public repository private. Before selling any course, change the source repository's visibility or move confidential course bodies, answer keys and protected assets into a private repository/storage location; verify only appropriate public pages/assets are deployed.
- Seed and validate products from source manifests; reject missing lessons, unstable slugs, duplicated order positions or references to absent assets.
- Add acceptance coverage for logged-out access, unpaid user, active entitlement, expired/revoked entitlement, drip-locked lesson, progress save/retry, duplicate payment events and refund/dispute state.
- Run a complete staging journey with test payment credentials before launch; no live payment credentials belong in code or this repository.

## 6. Work order

1. Preserve the product/content source and improve the existing frontend UX continuously.
2. Confirm hosting and same-origin route strategy, then verify the imported `backend/` runtime in staging. The presence of code in the draft PR is not evidence of a working deployment.
3. Reconcile the complete course catalogue and each product's entitlement rules, especially CONSTRUCT's included community access.
4. Integrate the branded login/member/learning screens with the authenticated server routes.
5. Import course content from manifests and implement secure lesson/progress delivery.
6. Validate purchase → entitlement → course/lesson → progress → refund/revocation.
7. Build the friendly admin dashboard near the end, after course models, catalogue, payment/access workflows and routine staff tasks are stable.
8. Run the final sitewide desktop/mobile UX pass and production release checks.

## 7. Guardrails

- Work from `prototypeweb/my-new-branch` for website/product/content changes.
- All feature branches and pull requests target `my-new-branch`; any approved merge goes into `my-new-branch` only. Do not merge into `main`. A CI guard fails PR checks targeting another base branch; repository settings must require that check for a hard merge block. This policy is not approval to merge an individual draft PR.
- Preserve existing micro-course source and its product boundaries.
- Do not wire static UI to guessed endpoints or fabricate logged-in, payment-success or saved-progress states.
- Do not mark a route, feature, test or deployment as production-ready without actual runtime evidence.
- Keep this integration PR in draft while CI is red or release gates are outstanding; a passing syntax check is not a substitute for a staging purchase-to-progress test.
- Do not merge or deploy to `main` without explicit approval.


## Draft content integration added on `feature/tradethesis-academy`

- The learner lesson page now renders Markdown tables, headings, lists and code with a sanitizer allowlist; arbitrary script/event attributes are stripped before output.
- `python manage.py seed_trading_path` validates the 30 Trading Path lesson sources and makes **no database changes**. `python manage.py seed_trading_path --apply` creates the course, four modules, 30 lessons and separate instructor answer/media notes. It is intentionally create-only, draft-only, marks all modules and lessons unpublished, and creates no Plan or CourseOffer.
- Quiz answer keys and chart-production notes are split out of the learner body. This import does not publish the course, provision Telegram delivery, attach missing chart assets, or configure checkout. The import is not a launch approval.
- `python manage.py seed_support_resistance` validates the canonical six-module, 18-lesson Support & Resistance map. With `--apply`, it creates six unpublished modules and 18 draft lessons and stores explicitly marked answer/instructor material separately. The agreed ChartLab ordering is recorded but its assessment/reveal interactions and required charts still need verification.
- `python manage.py seed_volume_price_analysis` validates the six-module, 30-lesson Volume Price Analysis manuscripts. With `--apply`, it creates six unpublished modules and 30 draft lessons. Learner-controlled native feedback disclosures are used for existing **Feedback** notes; instructor/answer blocks remain separate. Neither importer creates an offer/Plan or publishes course content.
- These importers preserve the working branch's existing learner-oriented Markdown where present; they do not overwrite an existing course. Run the default validation commands before applying them to a database.
- Included community access is recorded in calendar months separately from lesson/course access. Both the community-access dashboard state and desired Telegram/Discord permissions use the same active-entitlement rule, and the learner home shows current bundled community access even if course access has a different expiry.
