# Course Builder & Learning Room Deep-Pass Handoff

Updated: 21 October 2026
Working branch: my-new-branch
Canonical visual reference: course-source/understand-bollinger-bands/preview/first-pass/index.html
Course under inspection: Understand Bollinger Bands (7 modules, 30 lessons)

## User's goal

The Course Builder and the published/admin lesson views must use the agreed content-rich TradeThesis template, not a simplified Markdown rendering. The approved design includes the editorial lesson header, large serif lesson title, module/lesson tags, the study-time and “In this lesson” panel, reusable three-tab layout, purposeful figures with their own header/title/caption, and responsive mobile treatment.

The author must be able to write text, insert a figure between paragraphs, then continue writing after it. The insertion position must persist through draft saves and reopening on another computer. A figure must carry stable asset identity, a display title, accessible alt text, and an explanatory caption. Multiple figures per lesson must work.

## Guardrails

- Work only on my-new-branch.
- Do not merge to main, deploy production, change production data, or publish any draft.
- User explicitly asked to keep progress notes in the repository.
- Prefer sequential, small commits and re-fetch the current file SHA before every write.
- Do not claim a test has passed unless a real test run confirms it.
- Preserve existing manuscript text, media IDs, draft IDs, review/publish workflow, learner access gates, quiz/privacy rules, and shared-database persistence.
- The canonical HTML preview is the visual source of truth; avoid creating an unrelated parallel design.

## Confirmed findings

1. The canonical first-pass template has .lesson-header-depth and a deliberate “In this lesson” study panel.
2. The real Learning Room uses backend/templates/academy/lesson.html and backend/templates/academy/partials/lesson_tabs.html; the unpublished source preview uses backend/templates/academy/course_import_website_preview.html. They should share the same lesson header and figure styles.
3. backend/apps/academy/content_rendering.py currently uses a heading regex that only matches H3-H6; build_lesson_sections() converts detected headings to H3, which loses an authored H4/H5/H6 level and uses broad keyword heuristics to assign tabs.
4. render_safe_markdown() supports Markdown images and turns an image followed by the next paragraph into a basic figure, but doesn't render the custom title bar shown in the approved reference.
5. backend/apps/academy/course_builder_preview.html has image upload and image metadata controls. Its active insert-figure handler is cursor-aware, but it inserts ordinary Markdown and the metadata contract is not reliably represented in the imported lesson JSON. An earlier handler still appends a figure to the end, creating conflicting behavior. The builder JS includes several layered function overrides; modify cautiously.
6. backend/apps/academy/course_builder_api.py _clean_image_payload() computes stable UUIDs (assetUuid) and saves image asset specs. _build_import_payload() replaces asset://<builder id> with asset://<stable UUID>, and adds image captions as plain adjacent paragraphs. content_json presently has asset_ids but no structured figures metadata map.
7. Published, locked-lesson admin preview and imported-course admin preview already use build_lesson_sections(). This is the correct shared renderer seam.
8. Staging is the Academy Render service (manual deploy; auto-deploy disabled), but do not deploy until code changes are ready and safely verified. Existing deployment work before this deep pass was at 508da6674ce129b80d0935fab336591ac6df1ffe.
9. Initial investigations and patch preparation did not change any files in this deep pass. The previous attempt encountered scripting/tool errors before writing. The latest branch HEAD at the start of this note was 508da6674ce129b80d0935fab336591ac6df1ffe.

## Intended sequence

### A. Make the shared renderer safe and lossless
- Add a backward-compatible optional figure_metadata argument to render_safe_markdown() and build_lesson_sections().
- Pass content_json["figures"] from published lesson, locked admin preview, and unpublished source preview views.
- Before Markdown rendering, identify Markdown image tokens ![alt](asset://<uuid>), fetch their metadata by UUID, and replace each image token with a safe escaped semantic figure frame using placeholders (to avoid Markdown stripping the figure).
- Render the canonical figure header, title, image with alt text, caption, and explicit missing-asset fallback. Keep surrounding paragraphs in their authored order.
- Preserve image-plus-adjacent-caption legacy content and all lesson-reference tokens.
- Fix heading handling so levels remain H1-H6; keep tab grouping driven by explicit tab headings first and use only carefully scoped backward-compatible legacy rules.

### B. Fix the authoring metadata/persistence contract
- Normalize and persist title, alt, caption, assetUuid, and checksum in the builder's image metadata.
- Insert image Markdown at the current cursor, not at the lesson end.
- Preserve the figure metadata in content_json["figures"], keyed by the same stable asset UUID present in the rewritten Markdown and asset list.
- Keep support for multiple images and old drafts with a single image field.
- Remove/disable the conflicting append-only handler; ensure remove/reorder works against the inline Markdown image token and retains surrounding text.
- Avoid unsafe raw HTML: metadata should be escaped by the server renderer.

### C. Align visual templates
- Reuse the header pattern from the canonical .lesson-header-depth, including study panel.
- Add structured figure CSS to backend/static/academy/learning-room.css; use it in learner and unpublished preview paths.
- Ensure the source-preview path uses the same CSS and lesson partials as the published/admin Learning Room.
- Keep mobile design responsive at narrow widths.

### D. Tests and verification
- Add unit tests for heading-level preservation, figure title/alt/caption, proper placement between text, XSS escaping, legacy Markdown image/caption, and asset references.
- Add API tests that saving a draft preserves figure metadata and rewrites IDs consistently.
- Run targeted Django tests if an executable test environment is available, followed by the applicable backend and Learning Room workflows.
- Deploy only to Academy staging after reviewed code and tests, then inspect actual rendered pages at desktop/mobile widths and test the draft workflow. No production deploy.

## Acceptance criteria

- A full authored heading is visible and remains at the correct level.
- Figure output looks like the agreed example: tinted header, title, “Purpose-built teaching aid” label, image, caption.
- Text-before / figure / text-after order is identical before and after saving/reloading a draft.
- Multiple figures and their metadata survive a save/reopen cycle across devices.
- The Course Builder preview, unpublished admin preview, locked-lesson admin preview and learner lesson view share the same presentation rules.
- No answer keys or draft content leak to learners; no learner progress is changed by admin preview.
- Test/deploy status is reported honestly.

## Current status (updated 20 October 2026)

Implementation is underway on my-new-branch. Recent changes are committed; no production deploy or merge has occurred.

### Implemented in this pass

- Shared renderer now accepts optional figure metadata and a figure prefix, renders uploaded image references as a safe, titled semantic figure frame, preserves legacy image-plus-caption Markdown, and keeps the authored heading markers for H3-H6 instead of flattening them to H3. H6 is included in the safe Markdown allowlist.
- Builder asset normalization persists title, alt text, caption, stable asset UUID and digest. The import payload stores an asset-UUID-keyed figures map in content_json and no longer appends captions as stray adjacent paragraphs.
- Published lesson, locked-lesson admin preview and unpublished CourseImport website preview pass figure metadata into the same renderer.
- The learner and unpublished website preview share the content-rich lesson header: module/lesson labels, large serif title, summary, study-time panel and “In this lesson” steps. Shared Learning Room CSS includes responsive header and figure-frame styling.
- Course Builder's “Preview course” action saves the shared draft and opens the server-returned, administrator-only Academy website preview in a new tab.
- Removed a legacy image-insertion handler that appended figures at the end of the lesson. The active builder has multi-image metadata fields and cursor-based image insertion.
- Added native editable comparison-card teaching figures using a stable teaching-figure token. Cards have kicker, title and body fields plus an overall title/note; default content mirrors the accepted three-card “What changing the settings changes” example. The shared renderer and builder's local preview both understand these blocks.
- Added API regression coverage for stable uploaded-image metadata and website-preview URL, and created shared-rendering tests for heading hierarchy, structured figure placement, metadata escaping and legacy figure compatibility.
- Durable notes remain in this file; the supporting handoff itself is committed at docs/course-template/COURSE_BUILDER_DEEP_PASS_HANDOFF.md.

### Current verification (20 October 2026 — completed on revision e74dcb09556ddba8cf64ff5cf8d041b7cb563996)

- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39462398438): **success on Python 3.11 and 3.12**. Each full-suite job reports `863 passed, 36 subtests passed`; focused image-slot regressions report `19 passed, 4 subtests passed`.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39462398417): **success on Python 3.11 and 3.12**. Each backend regression suite reports `863 passed, 302 warnings, 36 subtests passed`; coverage artifacts uploaded.
- Both workflows passed Render build-script syntax checks, migration-state checks, Ruff, Black, mypy and static collection before the test steps.
- An earlier revision failed three new rendering-test assertions because the fixtures used literal backslash-n strings rather than paragraph breaks, and one XSS assertion was broader than the security condition it needed to check. The fixture/test assertions were corrected; the later revision passed both test workflows.
- Manual deployment to Academy staging was triggered after both test workflows passed. Render build `bld-dbbq8ron3acc73c8jat0` succeeded at 17:28:12 UTC and deploy `dep-dbbq8ron3acc73c8jasg` was confirmed `live` at 17:29:09 UTC on 20 October 2026. The service health endpoint repeatedly returned HTTP 200. Staging logs show the administrator website-preview route returning HTTP 200 with a 35,862-byte HTML response, and the builder admin-preview route was also requested successfully. No warning/error-level logs were found for the deployment window. Remaining acceptance work: visually inspect authenticated desktop/mobile layout, compare the header to the agreed Bollinger Bands reference, and verify image/caption placement and native comparison-card figures. This tool session cannot access the authenticated browser UI directly, so do not claim visual acceptance until an authenticated browser inspection is performed. Production is out of scope; do not merge to main or publish the draft.

### Follow-up: Inline image placement and draft-save slug collision (20 October 2026)

The author's latest staging screenshots exposed two separate regressions:

- In the builder's local “Learner preview”, the inline figure renderer inserted literal backslash-n text around its figure tokens. This prevented Markdown block parsing, leaked `TTFIGURETOKEN` placeholders into the page, and made nearby headings look like raw Markdown. The renderer now inserts actual paragraph separators, so repeated references to the same asset render at the reference positions.
- The “unplaced image” fallback checked only the transient builder asset ID. If the body referenced that ID but the image metadata also carried a different stable asset UUID, the preview could treat a placed image as unplaced and append another copy at the bottom. The fallback now checks both IDs.
- Draft save rejected a course slug before checking whether the request was re-saving its own existing CourseImport draft. The API now allows the collision only when the request includes a valid `serverDraftId` that resolves to a draft with the same slug. It still returns HTTP 409 for a genuinely new draft trying to use a slug already owned by an Academy Course. If the author is making a new course and has no matching saved draft, the URL slug must be changed to an unused one; this preserves the existing-course uniqueness rule.

Regression coverage was added for inline preview token separators and ID-aware fallback, re-saving an existing draft alongside a same-slug Course row, and rejecting a new draft that conflicts with an existing Course row.

Verification on revision `776e1d2900b99d5230c82366dd7305bc66054918` completed successfully:
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39468574740): Python 3.11 and 3.12 jobs passed focused regressions, linting, formatting, type checks, migration-state checks and the full test suite.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39468574843): Python 3.11 and 3.12 backend regression jobs passed.

The fixes are committed on `my-new-branch`. Manual staging deploy `dep-dbbqilg473hc738g88l0` for commit `a68d28fd276bc0e687cf4515fc772e6c2c89f587` completed successfully and Render marked it `live` at 17:49:53 UTC on 20 October 2026. The new instance returned HTTP 200 for `/health/`. The authenticated visual result has not yet been inspected directly in this tool session; reload the builder in the browser to exercise the new client renderer.

After the new instance started, the active browser continued receiving HTTP 409 from `/staff/course-builder/api/` for the same slug collision. This indicates the current browser state is not carrying a matching saved `CourseImport` draft ID for that slug. If this is a new course, open **Course details → Course URL slug** and give it a unique value before saving (for example, `new-micro-course-draft11-inline-test`); if the slug is meant to belong to an existing course, edit that course instead of creating a second one. This collision does not prevent testing the local Learner preview after refreshing, but the real server-backed website preview requires a successful save.

No merge to `main`, production deployment, course publication or database content mutation is authorized by this work. Render auto-deploy remains disabled.

### Follow-up: Named, grouped image figures (20 October 2026)

The author requested grouping two or more uploaded images beneath one user-entered title, matching the reference layout with a small “TRADETHESIS · LEARNING ROOM” line, the active module label, and a large serif group title. The uploaded filename must not be promoted into the title and the previous “Purpose-built teaching aid” badge was removed from all shared-renderer image/comparison figures.

Implemented on `my-new-branch`:
- Course Builder Images tab now includes “Create image group from first two images” after multiple images are uploaded. The group has an editable title, checkboxes for member images, an optional group note, and “Insert group at cursor” / “Remove group” actions. A group requires at least two uploaded images.
- Each image remains separately editable for its own title, alt text and caption. Filenames are no longer used as the visible title; missing titles render as “Chart”.
- Group data is stored in builder state and saved as an `image-group` entry under the stable figure metadata map. Member assets are included in `content_json.asset_ids`, keeping them reachable by the same private, permission-checked asset delivery logic.
- Shared renderer handles `[[image-group:<id>]]` as one figure, renders the chosen images side by side in a responsive grid, and uses the actual module name with the manually entered group title. The same header style is used for existing uploaded-image figures and native comparison-card figures.
- The local learner preview recognises group members as placed, so it will not append copies of grouped images at the bottom of the preview. Mobile styles stack the module/header labels and the image grid.
- Added renderer and API regression tests for title/module branding, image/caption placement, stable asset identities, group persistence, filename suppression, and duplicate fallback behaviour. Course Builder inline JavaScript syntax was also checked by parsing the script with the JavaScript runtime.

Verification on revision `4cf4cb2e9832e24eb2bfe73012ce656e64545dd3`:
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39473218565) passed on Python 3.11 and 3.12, including focused image-slot regressions, migration-state checks, linting, formatting/type checks and the full test suites.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39473218729) passed on Python 3.11 and 3.12.

Next step: deploy to Academy staging only, then visually confirm the new Image groups UI and real website preview using an authenticated browser session. The visual review has not been done in this tool session. Do not merge into `main`, deploy production or publish any course.

### Follow-up: Durable lesson-image storage hardening (20 October 2026)

The builder previously defaulted to private local filesystem storage when neither remote provider was usable. Render's service disk is ephemeral unless a persistent disk is explicitly configured, so that fallback could make uploaded lesson images disappear on restart/redeploy. This has been hardened on `my-new-branch` before staging rollout.

Implemented:
- Production/hosted settings default `ACADEMY_REQUIRE_DURABLE_ASSETS=True`; local development explicitly defaults it to false so development fixtures and local imports can still use local files.
- When Google Drive and GitHub durable storage are both unavailable, hosted image writes now fail closed with a safe, actionable error rather than silently writing a new file to ephemeral disk.
- Added environment-variable compatibility for the previously used unprefixed `GOOGLE_DRIVE_*` and `GITHUB_TOKEN`/`GH_TOKEN` names, while preferring the canonical `ACADEMY_*` names. Blank canonical values do not mask a configured legacy alias.
- Google Drive auth is now considered active only when complete service-account credentials or complete OAuth credentials plus a refresh token are available. Partial/stale OAuth credentials can fall back to another configured durable provider; credential details are not exposed in UI errors.
- The authenticated Course Builder API reports the active storage mode (Google Drive, private GitHub repository, or local filesystem), whether it is durable, and whether writes are enabled. The builder notice reflects the server's status instead of showing a fixed ephemeral-storage warning.
- Existing local-only assets are now distinguished from remote assets. On save, when a durable provider is configured, the API attempts to migrate an accessible legacy local file to that provider instead of mistaking the local fallback for a remote copy. If the local source has already disappeared, the save asks the author to re-upload the missing image instead of claiming it is safely stored.
- Added tests for hosted fail-closed writes, provider-status reporting, incomplete Drive authorization, remote-only existence checks, and local-to-durable asset migration.

Verification at code revision `52d89489e8ef6434c89a8058fb85e50bda1a9320`:
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39477719586) succeeded on Python 3.11 and 3.12, including lint/type/migration checks, focused image regressions and both full test suites.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39477719675) succeeded on Python 3.11 and 3.12.

Important verification boundary: this CI validates the storage logic, but the live staging provider can only be confirmed after deployment by reading the authenticated builder's `asset_storage` response/log entry and checking that it reports a durable provider. If staging has no usable Drive credentials, stored Drive credential, or GitHub write token, hosted uploads will remain blocked; do not override the fail-closed guard or claim assets are durable. The next step is to pin `ACADEMY_REQUIRE_DURABLE_ASSETS=True` on the staging service, deploy the current branch to Academy staging only, verify the deployment is live and the health check returns HTTP 200, then inspect the provider-status log on the next authenticated Course Builder load. If the provider reports local filesystem or writes disabled, configure the existing Google Drive OAuth/service-account connection or a GitHub contents-write token before treating image upload as ready.

No merge to `main`, production deployment, publication or edits to live course catalogue content are part of this task. Render auto-deploy remains disabled.

Staging rollout result: set Render env var `ACADEMY_REQUIRE_DURABLE_ASSETS=True` (merge-only environment update; no secrets were read or changed). Render deployed commit `0d07630d8c43ac79379a0200374e6be1497c793d` as deploy `dep-dbbrgrjl9sls739cqh60`; Render marked it `live` at 18:54:32 UTC on 20 October 2026. The build event succeeded and the new instance's `/health/` endpoint returned HTTP 200 repeatedly.

Live-provider verification remains pending: Render logs show no authenticated `GET /staff/course-builder/api/` since that deployment, so the new admin-only `asset_storage` response has not yet been emitted in logs. Ask the author to refresh the Course Builder while signed in; then inspect the `Course Builder asset storage configured: backend=... durable=... writes_enabled=...` log entry and on-screen banner. Do not report Drive/GitHub storage as verified until that entry confirms a durable provider. If it reports local filesystem or writes disabled, image uploads will be blocked by design; configure Google Drive OAuth/service-account credentials/folders or a GitHub contents-write token in Render before relying on images.


### Follow-up: Course deletion blocked by Course Media Asset permission (20 October 2026)

The user hit Django Admin's cascade deletion confirmation error:
> Deleting the selected courses would result in deleting related objects, but your account doesn't have permission to delete the following types of objects: course media asset

Root cause:
- `CourseAdmin.has_delete_permission` correctly allows content admins to delete courses.
- `CourseMediaAssetAdmin.has_delete_permission` intentionally returns `False` to prohibit deleting individual assets.
- `CourseMediaAsset.course` used `on_delete=PROTECT`, which blocks deletion of a course while owned media records exist.

Fix committed on `my-new-branch`:
- Changed `CourseMediaAsset.course` to `on_delete=CASCADE`, with migration `0008_course_media_asset_cascade.py`, so course-owned media records are removed only when the owning course is deleted.
- CourseAdmin's `get_deleted_objects` now removes the child media model's permission from the delete-confirmation blocker only for a user who passes `is_course_content_admin`. Other protected relations and deletion permissions remain unchanged.
- Direct deletion of a `CourseMediaAsset` from its own admin remains denied.
- Added `test_course_deletion.py` regression tests for delete-confirmation permissions and owned asset cleanup. CI needed several test-import formatting corrections; the final tested branch revision is `81fcbb96943b5f5a9e86ec5347a539379bcdd99b`.
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39484413882) and [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39484413991) both succeeded.

Staging deployment:
- Manually deployed Academy staging service `tradethesis-academy-staging` only, deploy ID `dep-dbbs84nf3r2c73bl272g`, deployed commit `ea8a3159fb6428fab9caec52cc963c0d620bcce7` (handoff update on top of the tested code) at 19:43:56 UTC on 20 October 2026.
- Render confirmed status `live`; the deployment event reported success and the new instance returned HTTP 200 from `/health/`.
- No production deployment, main-branch merge or course publication occurred.

Observed during handover: the browser made requests to `/learn/course/new-micro-course-draft11/lesson/8a6835cd-f150-424a-a903-b07769b1aa28/admin-preview/` which returned HTTP 404 after deploy. This appeared to be an existing/stale draft-preview URL; it does not affect the health check or deployment status, but if the author reports preview navigation problems, confirm the saved draft/lesson identifiers and preview route before diagnosing further.

### Remaining

1. Add test coverage for native comparison-card teaching figures: stable token, title, cards, note, authored placement and escaping.
2. Review Actions result for the current commit; resolve any regressions, then rerun after the comparison-card test is added.
3. Ensure native comparison-card data survives save/reopen through the shared builder API, and check old single-image draft compatibility.
4. Verify actual authenticated administrator website preview at desktop and mobile sizes, including a locked lesson and the unpublished Bollinger Bands course.
5. Deploy to Academy staging only after the above checks. No production deployment, merge to main or course publication without explicit approval.


### Follow-up: Verify live image-storage provider and grouped-image test status (21 October 2026)

Repository and staging were inspected after the durable-storage rollout. Work remained on `my-new-branch`; no merge, production deployment, or course publication was performed.

Verified against the live Render service **tradethesis-academy-staging** (`srv-db9ioke1egvs73feb8ag`):
- Active deployment `dep-dbbrgrjl9sls739cqh60` is `live`, built from commit `0d07630d8c43ac79379a0200374e6be1497c793d`. The Render service is configured to track `my-new-branch`, with auto-deploy disabled.
- Render log entry at `2026-10-20T18:58:40.447Z`: `Course Builder asset storage configured: backend=google_drive durable=True writes_enabled=True`.
- The corresponding authenticated request to `GET /staff/course-builder/api/` returned HTTP 200 (14,598-byte response), referring from `/staff/course-builder/`. This confirms **Google Drive is the active durable image-storage provider**. Private GitHub storage remains the fallback provider in code, not the active backend reported by staging.
- Both relevant workflows completed successfully on source commit `52d89489e8ef6434c89a8058fb85e50bda1a9320`: [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39477719586) and [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39477719675). These passed before the staging deployment was recorded.
- Current branch head subsequently advanced to `bdd407cd15f6bc03fcf6b49ef009a9903ab65a68` to record the deployment/provider-verification handoff. Staging intentionally remains on deployed commit `0d07630d8c43ac79379a0200374e6be1497c793d`; the handoff-only commit did not change runtime code.

Grouped-image implementation was inspected in `backend/apps/academy/course_builder_preview.html`, `backend/apps/academy/course_builder_api.py`, `backend/apps/academy/content_rendering.py`, and `backend/apps/academy/storage.py`:
- Builder supports multi-file JPEG/PNG/WebP uploads, individually authored image title/alt/caption fields, image groups with a typed title and editable membership of two or more assets, optional group note, and insertion at the lesson editor caret.
- Saving maps temporary builder IDs to stable asset UUIDs; figure/group metadata is stored alongside the draft content, including group member UUIDs in the asset list. The shared server renderer emits the titled, module-branded image-group frame with responsive grid, per-image titles/captions and escaped text. Authenticated asset delivery remains permission checked.
- The live provider-status line proves configuration, but **does not prove a new file can be uploaded, persisted, read back, and rendered**. Render logs show no image-upload POST or asset-delivery GET associated with an end-to-end upload test in the inspected interval. Thus the live upload/round-trip and desktop/mobile visual acceptance tests remain pending; do not mark them passed.

### Exact manual acceptance sequence still required

Using the authenticated Course Builder at https://tradethesis-academy-staging.onrender.com/staff/course-builder/:

1. Reload the page and confirm the notice says lesson images use durable private storage via **Google Drive**.
2. Use an existing saved draft or a new uniquely-slugged test draft (do not publish or submit for review). In one lesson, upload two small test images. Give each a distinct manually typed title, alt text, and caption; use filenames that are deliberately unhelpful (e.g. `upload-a.png`) to check that filenames are not used as display titles.
3. Type a paragraph, place the caret after it, switch to Images, create a group, change its title to a phrase such as “Compare the two test charts,” choose the two uploaded images, add a note, and use **Insert group at cursor**. Add a second paragraph after the token.
4. Save draft, reload the draft (or reopen it from another browser/device), and verify that the group title, selected members, per-image captions, and text-before/group/text-after order survive.
5. Confirm the server-backed website preview renders one group frame with the entered group title, both images, image titles/captions and group note; filenames should not be the visible figure title and no “Purpose-built teaching aid” label should appear.
6. Inspect desktop and a narrow mobile viewport: both images should be side by side when space permits and stack responsively on mobile; neither should be duplicated at the bottom. Verify images are readable after the page reload, confirming retrieval from persistent storage rather than browser-only data.
7. In Render logs, confirm the save and asset requests succeed without image-storage errors. Do not click **Submit for review** or publish the course as part of this validation.

No code/runtime changes or new deployment were made in this follow-up because authenticated browser automation is not available in this tool session. The provider verification is complete; actual upload persistence and visual grouped-rendering acceptance need the above browser session. Keep production, main branch, and course publication untouched.


### Follow-up: Deep visual-parity pass against the approved Bollinger Bands template (21 October 2026)

Source of truth reviewed:
- User-provided full HTML: `course-source/understand-bollinger-bands/preview/first-pass/index.html` (same canonical reference noted at top of this file).
- Runtime learner template: `backend/templates/academy/lesson.html` and `backend/templates/academy/partials/lesson_tabs.html`.
- Unpublished admin website preview: `backend/templates/academy/course_import_website_preview.html`.
- Shared lesson styling: `backend/static/academy/learning-room.css`.
- Authoring workbench/local learner preview: `backend/apps/academy/course_builder_preview.html`.

Diagnosis: The canonical reference is a much more fully art-directed learning experience than the editor UI, so copying its entire standalone document into Django would be incorrect. The standalone HTML includes a public course overview, interactions and a self-contained example learning room; the production-like Django templates already supply shared navigation, auth/entitlement, administrator-only preview, actual course data, structured lesson sections and safe server-rendered figures. The correct integration seam is to bring the shared learner-facing visual language closer to the reference without replacing that Django/runtime contract.

Visual gaps targeted:
- The learner heading, module tags, study-time panel and “In this lesson” section existed but were smaller/flatter, with less generous rhythm and card depth than the approved reference.
- Course outline and lesson content region were too tight; tab and heading hierarchies did not sufficiently carry the reference's larger editorial typography and generous reading line-height.
- Figures and group figures existed structurally, but headers/body spacing, image size and frame treatment were more restrained than the reference. Image groups needed to feel like intentional chart comparison panels, not small generic cards.
- The builder's local Learner preview has its own inline CSS distinct from the Django website-preview styles; improving only the shared stylesheet would leave the in-editor preview visibly behind. This pass styles both surfaces separately.

Changes prepared on `my-new-branch`:
- `backend/static/academy/learning-room.css`: append scoped reference-parity overrides for paper/cream surfaces, deep TradeThesis green and muted gold, larger editorial title/summary, more spacious lesson header and study panel, stronger outline navigation, clearer active tabs, more readable Markdown hierarchy, improved notebook/practice/navigation panels, and substantially richer structured figure/image-group/comparison-card frames. Mobile breakpoints remain explicit, with the outline and groups stacking at narrow sizes. Overrides are scoped under `.tt-learning-room` to minimise impact on unrelated admin/course pages.
- `backend/apps/academy/course_builder_preview.html`: append separate CSS-only overrides for the local learner preview and authoring workbench typography, editor card spacing, form controls, preview header/body, figure frames, grouped-image panels, comparison cards, and mobile layout. Existing JavaScript, save APIs, stable asset IDs, draft flow, and publish/review buttons are unchanged.

Review boundary:
- This is a visual styling pass, not a full rewrite of the template. The later information-table follow-up changes rendering semantics narrowly so Markdown pipe tables display in both previews.
- No lesson/course content, storage provider configuration, learner permissions, auth rules, question-answer handling, draft IDs, or publication workflow were changed.
- Do not deploy automatically. Staging has auto-deploy disabled. The API-triggered staging deployment at commit `ea8a3159fb6428fab9caec52cc963c0d620bcce7` included the information-table support; the alignment normalisation below still requires CI and explicit approval before another deployment.
- The styling/table changes are committed on the feature branch and the table fix has reached staging, but desktop/mobile side-by-side screenshot review against the canonical file remains outstanding. Do not claim pixel parity or visual acceptance without screenshots.


### Follow-up: Visual parity pass validation snapshot (21 October 2026)

- Feature branch head after CSS work: `be8b68cc30241f5d34f81525ae38f015c3eeeb2e`. The commit is `be8b68cc30241f5d34f81525ae38f015c3eeeb2e` (“Align Course Builder and Learning Room styling to approved template”). Only `backend/static/academy/learning-room.css`, `backend/apps/academy/course_builder_preview.html`, and this handoff changed.
- CSS-only review: the builder template retains exactly one opening and closing script tag, retains its style terminator, and its existing JavaScript/API/save/publish logic was left unchanged. New style rules include explicit tablet/mobile breakpoints for reading layout, outline, figures, image groups, and comparison cards.
- CI run [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39481529214) and [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39481529290) were still running at the latest check. Both workflows had passed setup, migration/configuration validation, lint, formatting/type checks (where applicable), static collection/catalogue and draft-import smoke checks; their full regression suites were still running. Do not mark CI passed until GitHub reports terminal success.
- Staging service inspection confirms Academy staging tracks `my-new-branch` with auto-deploy disabled. No deployment was triggered. Staging therefore remains on the last verified deployment commit until CI passes and an explicitly approved staging deploy is requested.
- Visual acceptance is still outstanding: no browser screenshots were taken in this tool session, so there is no claim of pixel parity. After CI success and staging deployment approval, compare the real saved-draft website preview to the canonical first-pass reference at wide desktop, tablet, and narrow mobile widths, then adjust any observed mismatches. Include figures with long titles/captions, two- and three-image groups, and the native comparison-card figure.

## Follow-up audit — information tables (21 October 2026)

A targeted comparison against the approved Bollinger Bands reference exposed one functional gap that the preceding styling pass did not catch: the table styling existed, but the Course Builder's client-side Markdown renderer did not parse pipe tables. The backend renderer already uses Python-Markdown's `tables` extension, while its sanitizer stripped the reference's `div.lesson-table-wrap` wrapper. On small screens this meant the builder preview could show raw pipe syntax instead of a table, and runtime tables lost the reference's horizontal-scroll treatment.

This pass addresses the gap in both views:

- The Course Builder's learner preview now recognises pipe tables, renders semantic `thead`/`tbody` markup and alignment, and places them in an accessible, horizontally scrollable `lesson-table-wrap`.
- The server-side Learning Room wraps rendered Markdown tables in the same pattern and permits only safe wrapper attributes through sanitisation; no styles, scripts, event handlers or arbitrary attributes were added to the allowlist.
- Both previews now use the reference's framed header row, fine dividers, readable cell spacing and narrow-screen scrolling.
- The Markdown help section explicitly documents information-table authoring.
- Added regression tests cover table HTML, accessibility wrapper attributes, and builder-preview table support.

No course content, authentication, billing, saving, review or publishing logic was changed. The core table wrapper is included in the staging deployment noted below. Browser-level visual acceptance remained pending; inspect a three-column/long-cell table at desktop and mobile widths. The follow-up alignment-normalisation change described below is not deployed pending CI and approval.

### Follow-up: Fix Django Admin course deletion blocked by Course Media Asset (20 October 2026)

The author reported Django Admin's “Cannot delete courses” message naming `course media asset`. The Academy content-admin permission policy allows a role=`admin` user to delete a Course, but `CourseMediaAssetAdmin.has_delete_permission` intentionally returns false; Django's delete confirmation therefore treats the related media record as a missing permission. The model's course FK also used `PROTECT`, so course-owned media records would continue blocking deletion even if the permission message were bypassed.

Implemented on `my-new-branch`:
- Changed `CourseMediaAsset.course` from `on_delete=PROTECT` to `CASCADE` and added migration `0008_course_media_asset_cascade.py`. Course-owned media metadata records are now deleted with their parent course.
- Overrode `CourseAdmin.get_deleted_objects()` to waive only the `CourseMediaAsset` child-permission item when a course-content admin deletes the owning Course. Direct deletion of an individual Course Media Asset remains disabled in its own admin page.
- Other protected course relationships are unchanged. Courses with protected offers or entitlements may still be blocked from hard deletion; archive such courses rather than bypassing those safeguards.
- Added `test_course_deletion.py` regression tests covering the confirmation permission list, cascade deletion of the owned media record, and continued denial of direct asset deletion.

CI at current tested revision `81fcbb96943b5f5a9e86ec5347a539379bcdd99b` is green:
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39484413882) passed on Python 3.11 and 3.12; each full suite reported 881 passed and 36 subtests passed.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39484413991) passed on Python 3.11 and 3.12.
- Migration state, Ruff, Black, focused image regressions and the full suite passed.

Staging was subsequently deployed successfully at `ea8a3159fb6428fab9caec52cc963c0d620bcce7` and Render marked that deploy live. Do not trigger another deployment for the later table-alignment change until CI is green and the user explicitly approves it. If deletion verification remains necessary, use only a disposable draft course with a media asset; do not delete live/published courses. No merge to `main`, production deployment or course publication is authorized.
  
### Follow-up: Preserve information-table alignment through sanitisation (21 October 2026)

The first table test exposed that Python-Markdown emits table alignment using a `style="text-align: …"` attribute, which the sanitiser correctly strips. The table remained safe and readable, but author-specified left/centre/right alignment was lost in the live Learning Room even though the Course Builder preview retained it.

The renderer now translates only the Markdown table extension's exact `left`, `center` or `right` table-cell alignment style into an `align` attribute before sanitisation. The existing allowlist already permits `align` on `th` and `td`; the change does not allow inline CSS. Regression tests now assert all three alignments survive sanitisation. This correction was committed on `my-new-branch` in `db113e4fc95ab088445046b28f3bd83de8d97f68` and both CI workflows are green. It has not been deployed.

The initial table fix and test correction passed at `81fcbb96943b5f5a9e86ec5347a539379bcdd99b`:
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39484413882): Python 3.11 and 3.12 full suites passed, with 881 tests and 36 subtests per version.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39484413991): both Python versions passed.

The alignment-normalisation follow-up at `db113e4fc95ab088445046b28f3bd83de8d97f68` is also green:
- [Academy backend CI](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39486735236): Python 3.11 and 3.12 each passed 881 tests and 36 subtests.
- [Verify Django Academy backend](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39486735125): Python 3.11 and 3.12 each passed 881 tests and 36 subtests; each job reported 306 warnings, with no failures.

Staging was confirmed live at commit `ea8a3159fb6428fab9caec52cc963c0d620bcce7`, which includes the information-table renderer and both style files. A file-SHA comparison confirms the staged `learning-room.css` and `course_builder_preview.html` match the branch; the staged `content_rendering.py` does not contain the new table-alignment normalisation yet. Browser screenshot comparison is still outstanding; deployment status and green CI do not prove visual acceptance.

## Follow-up audit — video field in website preview (21 October 2026)

A further end-to-end audit found a non-styling mismatch: the Course Builder editor and its local preview support a lesson `videoUrl`, and `course_builder_api.py` correctly persists that value as `content_json.video_url`. The normal learner lesson page renders this field, but the real administrator-only website preview used by the builder did not. An author could therefore see a video locally and then lose it when checking the same draft in the website template.

Implemented on `my-new-branch`:
- The website-preview view now reads `content_json.video_url`, accepts only HTTP(S) URLs, and identifies supported `.mp4`, `.webm`, and `.ogg` files as native-player media.
- The website-preview template renders the video block before lesson tabs, matching the real lesson page. File URLs use the native player; non-file URLs use a clearly labelled external link.
- Added regression coverage for native file playback, external video destinations, ordering before the lesson tabs, and rejection of unsafe URL schemes.
- The existing shared `.tt-video-lesson` styles are reused. No authentication, course-access, media-storage, submission, or publication rules were loosened.

This video-parity change is awaiting its own CI run. It has not been deployed. Keep it separate from the live staging revision until CI succeeds and the user explicitly approves the next staging deployment. Browser screenshot acceptance remains outstanding.

## Follow-up visual pass — compact header and figure spacing (21 October 2026)

The user's screenshots showed visible wasted space around the lesson header and chart figures. A source-to-runtime comparison found a structural mismatch, not only oversized CSS: the canonical first-pass template puts the lesson header inside the main lesson column beside the outline, while the Django learner and admin preview templates had placed the header before the two-column grid. That made the banner consume full-page width and left the outline starting below it.

This pass corrects the structure and aligns sizing with the canonical preview:

- Moved the lesson header inside `tt-lesson-main` in both the real lesson template and administrator website preview, so the outline sits beside the header on desktop.
- Reduced the header from `30–54px` padding and `42–64px` title sizing to the canonical `19–28px` padding and `34–47px` title scale. Reduced the title-to-summary, study-card, tag-row and header-to-content gaps.
- Reduced figure frames to `20px` vertical margins, smaller figure headings and inner padding, and a `470px` max height rather than `620px` for single figures. Image groups and comparison cards use similarly tighter spacing.
- Removed the administrator preview's `900px` article cap so lesson content can use the available main-column width instead of leaving a blank strip.
- The same audit also found that selected related-course references were stored but omitted from the admin website preview. That preview now shows only existing published courses; the references remain read-only and do not grant access.
- Regression tests cover header/grid placement, native and external video, unsafe video URLs and published-only related courses.

No course body, access/entitlement logic, answer keys, billing or publish state was changed. This pass is committed to `my-new-branch` and has not been deployed. CI must pass on the latest branch head before any staging deployment is considered. Browser screenshots at wide desktop, compact desktop, tablet and mobile widths are still required to verify the visual result against the source file.
