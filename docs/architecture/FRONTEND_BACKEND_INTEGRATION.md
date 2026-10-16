# Frontend / Django Backend Integration — TradeThesis

**Target repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Working branch:** `my-new-branch`  
**Status:** Django Academy is imported on draft PR #4, which targets `my-new-branch`. The latest verified CI run passed on Python 3.11 and 3.12 (666 passed, 1 skipped per runtime); all three source-course validators, the Support & Resistance browser smoke test and the integration-target guard also passed. These are isolated checks, not a staging or production sign-off. Catalogue records have not been seeded, public-to-Django routing is not deployed, and the end-to-end learner journey remains unverified.

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

The draft integration PR now includes a self-contained Django project under `backend/` (`backend/manage.py`, `backend/config/`, app code, migrations and tests). Django account and learning templates exist, and `site/member-access.html` links to the real authentication routes rather than accepting credentials in a static form. However, until routing is integrated and deployed, public member screens do not reach the Django runtime and remain previews. The runtime has not yet been verified in staging.

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
| CONSTRUCT | Its own Course/offer and curriculum, using `course-source/construct/` as source of truth | ₹17,000 core offer and included 12-month community access are separate entitlements/business rules. CourseOffer/CourseEntitlement now model the community term in calendar months independently of course expiry; access-target and dashboard tests cover grant, expiry and refund revocation. Before sale, still seed the dedicated hidden one-time Plan, CourseOffer and channel mappings, then verify purchase/refund/reconciliation in staging. |
| Six-week live classroom | Separate offer/enrolment path, not a synonym for CONSTRUCT | Do not represent cohort dates, sessions or fulfilment as available until the real delivery workflow is configured. |
| Future micro-courses | Each course gets its own stable slug, published modules/lessons and explicit offer if sold separately | Catalogue cards, enrolment and access must use backend records, not client-side price or access flags. |

The mapping above is the proposed implementation model; it does not mean these products have been seeded or verified in Django yet. Before seeding, reconcile each source's current lesson manifest and offer rules to the actual course catalogue and confirm any product naming/pricing changes.

## 4. Frontend changes required

1. **Member access:** `site/member-access.html` now links to Django login, sign-up and password-reset routes instead of collecting passwords in a static form. Still verify the routes, redirects and recovery flow on the chosen host.
2. **Member area:** the authenticated `/learn/` page renders courses, progress and separate community access from backend state. `site/member-area.html` remains a prototype until hosting/navigation routes members to Django.
3. **Course catalogue:** importers validate the Trading Path (30 lessons/four levels), Support & Resistance (18 lessons/six modules) and Volume Price Analysis (30 lessons/six modules). They have not been applied to the database; create-only `--apply` imports remain draft-only and do not create offers.
4. **Checkout:** the course detail template submits to the server-side payment-start route using a selected active one-time CourseOffer. Real offers, provider/webhook configuration and the staging payment-to-entitlement journey are still unverified.
5. **Lesson progress:** the authenticated Django progress endpoint applies server-side access checks, and the lesson page reports the response. Verify save/error/retry in the hosted journey with real session and CSRF configuration.
6. **Drip release:** release eligibility is computed by the backend. The front end presents release state but cannot unlock a lesson by changing JavaScript or DOM state.
7. **Media and charts:** preserve readability and zoom/open controls. Required charts/interactive ChartLab assets are not all connected to the Academy records yet. Confidential source, answers and downloads also require private source/storage and delivery.
8. **Sitewide UX:** still run one hosted desktop/mobile journey across public site, login/signup/recovery, member home, course overview, lesson, checkout, locked lesson and progress/error states.

## 5. Backend and release gates

- Keep payment confirmation, entitlement grants, refunds/chargebacks and progress writes server-side and idempotent.
- Do not reuse subscription/bot permissions as Academy course access.
- Confirm one-time pricing, geo-pricing, checkout evidence/terms, provider webhooks and refund/dispute behaviour end to end.
- Ensure course entitlement and community entitlement rules are distinct where required.
- Choose private storage/delivery for paid lesson bodies and protected reference material before learner launch.
- **Repository privacy blocker:** the current GitHub repository is public and contains paid course source plus internal instructional/reference material. A private Django route does not make copies already committed to a public repository private. Before selling any course, change the source repository's visibility or move confidential course bodies, answer keys and protected assets into a private repository/storage location; verify only appropriate public pages/assets are deployed.
- Seed and validate products from source manifests; reject missing lessons, unstable slugs, duplicated order positions or references to absent assets.
- Unit/regression coverage now exercises protected lesson access, progress, duplicate payment activation, course refund revocation and the separate community term. It does not substitute for hosted acceptance checks for logged-out access, unpaid users, expired/revoked access, drip release, progress save/retry and provider webhook retries.
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
