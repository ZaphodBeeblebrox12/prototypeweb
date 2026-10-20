# TradeThesis micro-course template — Django integration handoff

**Status:** Approved source-of-truth contract; Django integration is the next implementation task.  
**Website/content repository:** `ZaphodBeeblebrox12/prototypeweb`, branch `my-new-branch`.  
**Canonical preview:** [Content-rich Bollinger Bands Learning Room](../course-source/understand-bollinger-bands/preview/first-pass/index.html).  
**Template rules:** [Course Template Standard](../course-source/COURSE_TEMPLATE_STANDARD.md).  
**Django runtime:** `backend/` in `ZaphodBeeblebrox12/prototypeweb`, branch `my-new-branch`. The external `test` / `feature/tradethesis-academy` repository is the earlier source/rollback snapshot, not the default code target.

## Goal

Make the approved course template the reusable foundation for every future TradeThesis micro-course. The goal is rapid, repeatable course deployment—not manually rebuilding a standalone HTML page for each topic.

The production flow should be:

**Course Markdown + manifest + owned assets → validated preview → idempotent Django import/update → administrator review/edit → authorised learner delivery.**

The active repo contains the Django Academy runtime under `backend/` on `my-new-branch`. Implement model, view, URL, permission and template changes there after verifying the current staging commit; do not modify the external source/rollback snapshot by default.

## Canonical template rules

Use `course-source/understand-bollinger-bands/preview/first-pass/index.html` as the canonical content-rich visual/interaction reference. Preserve the useful lesson flow, full-content treatment, figures, exercises, chart interactions, tabs and notebook behaviour during integration. `preview/template-reference/index.html` is an earlier design iteration, not the active reference.

- Keep the compact, light TradeThesis visual language: warm paper surfaces, muted green/gold accents, editorial serif headings, readable sans-serif body copy, restrained borders, clear hierarchy and mobile-ready spacing.
- Preserve the course overview to Learning Room journey, lesson outline, compact lesson header, integrated underline-style lesson tabs, readable article surface, figure count, figure enlargement where relevant, and clear lesson completion/progress actions.
- Keep the **Your Trading Notebook** callout pattern. Adapt the questions to each subject; do not blindly reuse Bollinger-specific text in unrelated courses.
- Do **not** reintroduce the green **“By the end, you can”** objective card. The current canonical source has it removed.
- Use the site's real Django base template, sitewide navigation and approved logo. Do not copy the preview's standalone shell into production in a way that creates a second header, inconsistent logo, skip-link styling defects, or another login/page shell.
- Course-specific titles, lesson text, figures, study time, practice and review content must come from structured course content, not hard-coded into the shared Django layout.
- Preserve existing course access and product boundaries. A shared template does not mean shared enrolment, pricing, drip schedule or entitlements.

## Source-of-truth rules

1. `course-source/COURSE_TEMPLATE_STANDARD.md` defines the reusable standard.
2. `course-source/understand-bollinger-bands/preview/first-pass/index.html` is the current concrete, content-rich visual/interaction reference—not the final Django template. The Markdown lessons and manifest remain the course authoring/structure sources. Extract shared layout and interactions; do not ship the preview shell or its preview-only editing controls.
3. Each course's authored lesson Markdown, architecture and asset register are its authoring source. Generated lesson-data JavaScript and static preview files are outputs; regenerate them rather than editing them as the content authority.
4. A course manifest (or compatible existing manifest format) defines stable course/module/lesson slugs, ordering, display metadata, duration, source paths and asset IDs. Reuse existing formats where possible; do not create competing manifests.
5. Django's persisted course content and media records become the production runtime authority after import. Import/update must be repeatable and idempotent and must not wipe learner progress, enrolments, offer relations or other live state.

## Implementation approach

### 1. Audit before editing

Inspect the active `backend/` Academy runtime on `prototypeweb/my-new-branch` first. Read its current models, migrations, URLs, views, templates, static asset conventions, admin registrations, permissions, tests, settings and existing course import/seed process. Confirm which models already represent courses, modules, lessons, lesson content, progress and media. Verify the current staging commit, route names and access checks from code instead of inventing routes.

Do not create a second Django runtime elsewhere, create a generic page builder, or introduce parallel course models until the audit proves a specific gap.

### 2. Extract a reusable Learning Room

Build the production design into shared Django template(s)/partials and shared static CSS/JS. Keep the site's actual base template and global navigation outside the course-specific component. Render modules, lessons, tabs, figures and practice/review sections from context backed by existing Academy models.

The current standalone HTML is a reference implementation and still contains preview-only behaviour and some preview-specific content. Do not ship it wholesale as a production page. Separate template/layout code from each course's manifest and lesson content so future micro-courses use the same page with data, not copied HTML.

### 3. Establish the fast course import/update workflow

Create or adapt one idempotent management command/import service that reads the approved course manifest and authored sources, validates the package, and creates/updates the existing Course → Module → Lesson records. Reconcile stable slugs, order values and source identifiers before importing. Report missing files/assets, duplicate slugs/order values, unknown references and invalid content instead of silently skipping them.

Preserve primary keys, progress, enrolments, offer/access relationships and audit history when updating an existing course. Generated preview data should not be imported as a second source if the original Markdown or structured manifest is available. Document the exact commands to validate, preview and import a new micro-course.

### 4. Administrator-only text and image editing

Only administrators may change published lesson text or images. Do not grant editing access to learners, instructors or ordinary staff. Do not use `is_staff` alone as authorisation; use the existing superuser/admin policy or dedicated content/media-edit permissions granted only to administrators, and check permission on every write request.

The first usable editing route must save shared content through Django and display that persisted result to learners after an authorised refresh. Use the existing Django Admin where it fits the current model design. If inline editing on the lesson page is retained, it must use the same administrator-only server policy and dedicated permission checks.

For text:
- Use stable IDs based on persisted lesson/content records, not the preview's tag-order-generated IDs.
- Whitelist editable fields/content block types and sanitise allowed markup server-side. Reject scripts, event handlers, unsafe URLs, iframes and arbitrary executable markup.
- Save transactionally and keep a minimal revision/audit record with editor and timestamp.
- Keep structure, navigation labels, styles, lesson ordering and JavaScript behaviour developer-controlled unless a separate requirement explicitly approves editing them.

For images:
- Give each shared asset a stable database ID, alt text, persistent storage path, associated course/lesson references and updated-by/updated-at audit fields.
- Restrict uploads to administrator-only permissions and CSRF-protected POST requests. Validate the actual decoded file server-side; allow JPEG/PNG/WebP, use safe generated filenames, enforce a file-size limit and do not accept user-supplied SVG.
- Replacing an asset should update every use of that asset ID, use a cache-safe/versioned URL, and retain the previous file long enough to recover if verification fails.
- Do not rely on hidden buttons, localStorage, Data URLs or `TRADETHESIS_MEDIA_PREVIEW_ONLY` as production security or persistence.

### 5. Access and rendering safety

Use the existing Academy authentication, entitlement and lesson access checks. Never rely on the client to decide if a course/lesson is unlocked or if a person is an administrator. Paid lesson bodies and private course assets must not become publicly accessible through the static site, generated preview, guessed URLs or an unprotected media endpoint.

Keep text/media editing separate from learner progress and quiz submissions. A content update must not reset learner progress or grant access. A draft, in-development, published or archived course state must come from trusted backend data and affect catalogue visibility consistently.

## Acceptance checklist

- The production course page uses the existing sitewide Django header, navigation and correct TradeThesis logo.
- The page visually matches the canonical source without a redesign, including the notebook callout and absence of the removed objective card.
- Course-specific content is data-driven; a second sample micro-course can use the same layout without duplicating its HTML/CSS/JS.
- A management command can import/update an approved source package repeatedly without duplicate records or destructive updates.
- An administrator can update lesson text and replace an image; changes persist and are visible to an authorised learner.
- An ordinary staff user without the dedicated admin permission, an instructor, a learner and an anonymous visitor cannot update course content or media.
- Tests cover CSRF, invalid/sanitisation payloads, permission denial, upload type/size/storage failures, revision/audit fields, stable asset reuse, learner access and persistence after refresh.
- Existing login, enrolment, course access, lesson progress, pricing/offer and mobile flows still work.
- Relevant tests, migration checks and browser smoke tests pass. Report what was actually run; do not call the work deployed or production-ready without evidence.

## Copy-ready prompt for the next implementation chat

```text
Continue the existing TradeThesis micro-course and Django Academy work. Do not restart or rebuild the project from scratch.

SOURCE OF TRUTH
- Website/content repository: https://github.com/ZaphodBeeblebrox12/prototypeweb/tree/my-new-branch
- Course template standard: course-source/COURSE_TEMPLATE_STANDARD.md
- Canonical content-rich visual/interaction reference: course-source/understand-bollinger-bands/preview/first-pass/index.html
- Django integration notes: docs/architecture/FRONTEND_BACKEND_INTEGRATION.md
- Admin text contract: docs/architecture/COURSE_CONTENT_EDITOR.md
- Admin image contract: docs/architecture/INSTRUCTIONAL_IMAGE_REPLACEMENT.md
- This handoff: course-integration/MICROCOURSE_TEMPLATE_DJANGO_HANDOFF.md
- Django runtime: `backend/` in `ZaphodBeeblebrox12/prototypeweb`, branch `my-new-branch`. Earlier source snapshot: `ZaphodBeeblebrox12/test`, `feature/tradethesis-academy`. Verify the deployed commit and active feature-branch state before editing.

GOAL
Integrate the approved TradeThesis course template into the existing Django Academy so all future micro-courses can be added quickly from approved Markdown/content manifests and assets, while sharing one reusable Learning Room instead of copying a monolithic HTML page for every course.

FIRST: inspect the active `backend/` runtime on `my-new-branch`. Read its models, migrations, views, URLs, templates, static assets, admin setup, permissions, tests and import commands. Report actual state before editing. Reuse existing Academy models; do not create a second Academy app or modify the external rollback/source snapshot by default.

DESIGN CONTRACT
Use the canonical content-rich first-pass HTML as the approved concrete design and interaction reference, not as a production page to paste in wholesale. Preserve its rich lesson flow, light TradeThesis look, typography, spacing, course navigation, readable lesson body, figures, exercises, chart interactions, tabs and progress/completion interaction. Keep the “Your Trading Notebook” callout style but make its wording course-specific. Do not reintroduce the removed green “By the end, you can” objective card. Use the real sitewide Django base template, navigation and correct logo; do not create a second header, old login route or separate site shell.

RAPID COURSE DEPLOYMENT
Make the page layout reusable and drive course-specific content from the existing Academy models and an approved manifest/source package. Keep authored Markdown as the source content and treat generated preview JS/HTML as build output. Add/adapt one validated, idempotent import/update command that preserves stable IDs, progress, enrolments, offers and access relationships. Document how to create, preview, validate and import the next micro-course. Do not manually fork the full Bollinger HTML per course.

ADMIN-ONLY EDITING — CRITICAL
Only administrators may modify shared lesson text or images. Do not expose edit/upload capability to learners, instructors or ordinary staff. Do not rely on a hidden button, client-side flag or is_staff alone. Use the app's real admin policy or dedicated content/media permissions assigned only to administrators, checked server-side on every save/upload. Keep Django Admin as the reliable first editing route; inline lesson-page editing is optional and must obey the same checks.

Text changes must persist in the existing course-content model/database, use stable database-backed content IDs, whitelist supported fields/block types, sanitise HTML, enforce CSRF, save transactionally and keep a basic before/after audit record. Image replacement must use a persistent shared media record/storage, stable asset IDs, alt text, file-type/size validation, safe generated names, CSRF, administrator-only permission checks and cache-safe URLs. Replacing one asset must update every use of that asset ID. Do not enable localStorage/Data-URL preview behaviour or preview-only flags in production.

SECURITY AND REGRESSION
Reuse existing authentication, entitlement and lesson-access checks. Never make paid lesson content or media public accidentally. Content edits must not reset course progress or grant enrolment/access. Test permission denials, anonymous access, CSRF, unsafe HTML, invalid/oversized images, storage/database failures, persistence after refresh, repeated import idempotency and existing login/enrolment/progress paths. Test desktop and mobile rendering.

WORKING RULES
- Work in the existing development branch after verifying it; do not work on or merge into main.
- Do not commit, merge, deploy, or change branch targets until I explicitly approve.
- Do not claim a test, browser check or deployment succeeded unless you actually ran it and saw the result.
- Do not make unrelated redesigns or product/pricing/entitlement changes.
- Before making changes, report the current state and a short file-by-file implementation plan. Then proceed in small, reviewable steps and checkpoint progress in the conversation.
```
