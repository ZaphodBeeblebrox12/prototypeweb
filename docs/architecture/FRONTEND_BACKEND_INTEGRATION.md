# Frontend / Django Backend Integration — TradeThesis

**Target repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Working branch:** `my-new-branch`  
**Status:** Integration map for the existing UI and Django Academy implementation. Not a claim that the backend has been deployed or connected.

## 1. Verified current state

### This repository: the product and content source

The branch contains the static TradeThesis website, course-room prototype, learner resources, brand assets, micro-course source and Support & Resistance production package. Relevant entry points include:

- Public-site review: `site/00_OPEN_INTERACTIVE_PREVIEW.html` and `site/MOBILE_PREVIEW.html`.
- Public pages: `site/index.html`, `site/courses.html`, `site/trading-path.html`, `site/construct.html`, `site/live-class.html`.
- Current member UI prototypes: `site/member-access.html` and `site/member-area.html`.
- Trading Path curriculum source (legacy folder name): `course-source/starter-drip-course/`.
- CONSTRUCT source: `course-source/construct/`.
- Volume Price Analysis source: `course-source/volume-price-analysis/`.
- Support & Resistance course: `course-content/support-resistance/`.
- Existing curriculum metadata: `course-integration/curriculum.json`.

The Django runtime is now consolidated under `backend/` on `prototypeweb/my-new-branch`. The public member screens remain static design previews; authenticated account, checkout, and course access must be validated through the Django runtime before being treated as production flows.

### Django runtime and rollback source

The runnable Django application is now under `backend/` in this repository, on `prototypeweb/my-new-branch`. It was copied from `ZaphodBeeblebrox12/test` / `feature/tradethesis-academy` at source commit `e7bef974e1227f094c7c7044c0d64785c17b2fdd`.

The source repository and its feature branch remain unchanged as the rollback/source reference until staging verification is complete. Do not merge this work into `main`.

Runtime paths now live under `backend/`: `manage.py`, `config/`, `apps/`, migrations, templates, static assets, dependencies, and tests. Key Academy routes include:

- `/learn/` — authenticated learning home;
- `/learn/course/<course_slug>/` — course overview and access state;
- `/learn/course/<course_slug>/lesson/<lesson_uuid>/` — authorized lesson detail;
- `/learn/lesson/<lesson_uuid>/progress/` — authenticated POST for progress;
- `/accounts/login/` and `/accounts/signup/` — Django Allauth pages.

Render's existing staging services still need to be pointed at `my-new-branch` after CI validation. The consolidation workflow does not alter Render configuration or deploy services.

## Reusable micro-course template and Django handoff

The approved concrete design reference is [the Understand Bollinger Bands first-pass Learning Room](../../course-source/understand-bollinger-bands/preview/first-pass/index.html), governed by [the shared course-template standard](../../course-source/COURSE_TEMPLATE_STANDARD.md). The implementation-specific notes and copy-ready prompt are in [MICROCOURSE_TEMPLATE_DJANGO_HANDOFF.md](../../course-integration/MICROCOURSE_TEMPLATE_DJANGO_HANDOFF.md).

When integrating the template, extract a reusable Django Learning Room that inherits the real sitewide base template/navigation/logo. Do not ship the static preview as-is or duplicate its entire HTML for each micro-course. Course content must be driven by the existing Academy records and validated source manifest; lesson Markdown is authoring source and generated preview payloads are outputs.

**Only administrators may edit shared lesson text or images.** Re-check a dedicated administrator content/media permission on every save or upload; do not treat hidden controls, client-side configuration or `is_staff` alone as authorization. Persistent text/media updates, audit trail, storage and CSRF checks are backend work, not capabilities supplied by the static preview.

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
| Free Trading Path | One published Course with 30 lessons, checkpoint metadata and free permanent course entitlement | All lessons are available immediately. The optional 30-day study plan is guidance only, not a server-enforced drip schedule. No community or trading-bot access is included. Do not promise Telegram lesson delivery unless that delivery path has passed end-to-end acceptance. |
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
6. **Staged release:** where a product uses scheduled lesson releases (for example, CONSTRUCT), eligibility is computed by the backend. The Trading Path is self-paced with all 30 lessons available immediately. The front end must never unlock a staged lesson by changing JavaScript or DOM state.
7. **Media and charts:** preserve readability and zoom/open controls. Any confidential reference/answer state must be separately protected at delivery time; CSS-only hiding is not permission enforcement.
8. **Sitewide UX:** verify public site, login/signup/recovery, member home, course overview, lesson, checkout, locked lesson, progress/error states and mobile view as one continuous journey.

## 5. Backend and release gates

- Keep payment confirmation, entitlement grants, refunds/chargebacks and progress writes server-side and idempotent.
- Do not reuse subscription/bot permissions as Academy course access.
- Confirm one-time pricing, geo-pricing, checkout evidence/terms, provider webhooks and refund/dispute behaviour end to end.
- Ensure course entitlement and community entitlement rules are distinct where required.
- Choose private storage/delivery for paid lesson bodies and protected reference material before learner launch.
- Seed and validate products from source manifests; reject missing lessons, unstable slugs, duplicated order positions or references to absent assets.
- Add acceptance coverage for logged-out access, unpaid user, active entitlement, expired/revoked entitlement, drip-locked lesson, progress save/retry, duplicate payment events and refund/dispute state.
- Run a complete staging journey with test payment credentials before launch; no live payment credentials belong in code or this repository.

## 6. Work order

1. Preserve the product/content source and improve the existing frontend UX continuously.
2. Confirm hosting and same-origin route strategy, then select the actual Django runtime repository/deployment artifact. Do not duplicate a partial Django app into this static repository and call it a runnable backend.
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
- Do not merge or deploy to `main` without explicit approval.


## Sitewide instructional-image replacement hook

The shared frontend hook and backend contract are documented in INSTRUCTIONAL_IMAGE_REPLACEMENT.md. The hook is included in the Trading Path, Support & Resistance, and Bollinger Bands course-room templates but intentionally shows no button in the current static preview. Persistent replacement requires server-rendered staff permission, stable media records, a CSRF-protected Django media endpoint and shared storage; the frontend hook is not an active upload backend.
