# Course Builder & Learning Room Deep-Pass Handoff

Updated: 20 October 2026
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

## Current status

Research and the target code seams are identified. Implementation commits for this deep pass have not yet been made. Continue from section A and make durable commits as each coherent part is completed.
