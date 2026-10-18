# TradeThesis Course Template Standard

**Status:** Binding standard for every new TradeThesis micro-course and the migration target for existing courses.  
**Canonical visual/interaction reference:** [TradeThesis Learning Room template (Bollinger Bands reference)](understand-bollinger-bands/preview/template-reference/index.html). This is the approved visual and interaction source of truth. The content-rich `preview/first-pass/index.html` remains a separate course-preview and QA artifact. The template retains the **Your Trading Notebook** treatment and omits the former green **“By the end, you can”** objective card.  
**Design approval checkpoint:** `030e473e33563499d57b1a8836559ce4501c138b` on `my-new-branch` (17 October 2026).  
**Content authority:** Each course's authored Markdown lessons and course architecture; generated preview payloads are build outputs, not editing sources.  
**Django runtime:** Separate Academy repository, currently documented as `ZaphodBeeblebrox12/test` on `feature/tradethesis-academy`; verify the actual branch state before implementation.  
**Implementation branch:** `my-new-branch`. Do not merge to `main` or deploy without explicit approval.

## Decision

Use the updated TradeThesis course template as the default for every new course and as the target layout for every existing course. Course content, figures, exercises and navigation can differ by subject; the core student experience and visual language should feel consistent across the catalogue.

This is a flexible teaching template, not a form with mandatory labels. Reuse the purpose of a section when useful, rename it in student-facing language, combine sections, or omit one when it adds no learning value. Do not force every lesson into identical cards or repeat explanatory text to fill a layout.

## Shared course experience

Course pages use two connected views:

- **Course overview:** clear promise, who the course is for, measurable learning outcomes, curriculum with lesson titles, practical outputs and a clear route into the learning room.
- **Learning room:** searchable or scannable course outline, a distinctive but compact lesson header, concise lesson summary, estimated study time and a brief sense of what the learner will do.
- **Lesson navigation:** use the template's integrated, restrained tabs—**The idea**, **Chart examples**, and **Test your reading**—as the default. Rename only where a subject makes more natural wording clearer.
- **Figure placement:** show the first relevant visual in **The idea** beside the explanation it supports. Put additional figures in **Chart examples** so examples can be compared.
- **Asset count:** show a numerical count beside **Chart examples**, computed from the lesson's actual figure data. Count the lead figure in **The idea**, additional references and the worked chart.
- **Lesson body:** readable editorial article surface with enough text margin, a restrained hierarchy, clear figure sizing and an uncomplicated completion/next action.
- **Responsive use:** course outline and lesson content must remain useful on mobile. Figures must remain readable and have an enlarged view when fine details or annotations require it.

## Visual language

Retain the light, paper-like TradeThesis palette with muted green and gold accents, editorial serif headings, readable sans-serif body text and a compact layout. Use borders, spacing and typography to establish hierarchy before adding more cards. Avoid unnecessary dark-first dashboards, excessive rounded containers, nested navigation cards, decorative clutter and compressed chart annotations.

The latest saved preview's lesson header, integrated underline-style tabs, reading margins, chart-example panels and natural completion bar are the visual reference. The same design intent should be carried across all course pages without requiring every course to share the exact same content composition.

## Flexible lesson teaching pattern

A lesson should normally move through these functions, choosing only those the topic needs:

1. A practical question or common trading decision.
2. A plain-English explanation of the concept and its limits.
3. A worked visual example, with observation separated from interpretation.
4. A contrasting, failed or ambiguous case where it adds insight.
5. A learner decision or short practice task.
6. Model reasoning that explains why, not merely which option is correct.
7. A reusable takeaway, checklist or conditional rule.

Use **Observe → Interpret → Test** as the recurring reasoning habit where it fits the topic. It is an editorial/teaching standard, not a required trio of cards in every lesson. Learning objectives should be concrete and measurable, with no duplicate objective boxes or repetitive boilerplate.

Section functions are reusable, not fixed names:
- A production or editorial note is normally internal; it may become student-facing context only when the content genuinely helps the learner.
- **Do not reintroduce the removed green “By the end, you can” objective card.** State a lesson outcome naturally in the summary or opening explanation if it helps the learner; do not add a duplicate objective box.
- Preserve the current **Your Trading Notebook** editorial callout treatment as the shared reflective/checklist pattern. Adapt its prompts to the course topic rather than forcing Bollinger-specific wording into unrelated subjects.
- Concept and transfer sections should have topic-specific student-facing headings rather than repeatedly showing the same generic labels.
- Internal level labels, production states, build instructions and asset-status notices do not belong in the normal learner view.

## Figure and image standard

- Use local, downloaded or course-owned image files in the finished course—not hot-linked images as a runtime dependency.
- Give figures persistent internal asset IDs in production records and simple student-facing labels such as **Figure 1.1**, **Figure 1.2**, **Figure 2.1**. Number figures by module and keep references in lesson text only when helpful.
- Never place internal asset IDs, difficulty/level labels, “synthetic data” banners or production-state labels inside learner-facing charts. If an image is illustrative or not historical data, explain that in a nearby caption where it matters.
- Keep image-source, copyright/licence, download provenance and replacement notes in an internal asset register, not in the main lesson narrative.
- Give each replaceable image a stable asset ID and a server-authorised replacement route when rendered by Django.
- During first-pass production, externally sourced chart images may be used as temporary visual references when their origin is recorded. They must be replaced with course-owned TradingView captures or images cleared for the intended use before public release. A source URL alone does not satisfy the downloaded-asset requirement.
- Add useful alt text. Keep annotations legible on mobile and when enlarged; use simple static comparisons rather than introducing ChartLab unless explicitly requested.

## Migration rule for existing courses

Every existing course should be migrated to the shared visual and navigation standard, retaining its approved course-specific content and interactions wherever they still make sense. Do not bulk-rewrite course teaching content merely to make it look uniform. Migrate incrementally on `my-new-branch`, preview the result, checkpoint the work in GitHub, and do not merge or deploy without approval.

## Current first-pass target

The initial application pass is **Understand Bollinger Bands**. Its seven-module manuscripts remain the source of truth. The first preview will use the updated Learning Room structure, locally stored visual assets for review, simple module-based figure labels and explicit notes that temporary web-sourced images are placeholders to be replaced by the user's own TradingView captures before release.


## Source-of-truth hierarchy and rapid deployment

Use these layers deliberately; do not let the same lesson text become independently maintained in multiple places.

1. **This standard** defines the reusable teaching, visual, accessibility, image, migration and security rules.
2. **Canonical design reference:** `course-source/understand-bollinger-bands/preview/template-reference/index.html`. It is the selected reference for spacing, typography, overview-to-learning-room flow, lesson navigation, notebook treatment, content width, figure handling and responsive behaviour. Treat it as a reference for extraction into shared Django templates—not as the production Django page to copy wholesale. The content-rich `preview/first-pass/index.html` remains available for its existing course-content and editor QA checks.
3. **Course-specific authoring source:** the course's `README.md`, `COURSE_ARCHITECTURE.md`, lesson Markdown and `ASSET_REGISTER.md`. Markdown lessons are the student-content editing authority unless a course explicitly records a different approved source.
4. **Structured manifest:** each course should have a stable manifest (or the project's existing equivalent) describing course metadata, ordered modules/lessons, stable slugs/IDs, durations, learning outcomes, lesson source paths and asset IDs. Reuse existing manifest formats when compatible; do not create a second competing manifest.
5. **Generated preview output:** generated lesson-data JavaScript and preview HTML/assets are derived artifacts. Regenerate them from their authoritative sources; do not manually patch generated lesson text and then treat it as canonical.
6. **Published Django content:** the database and persistent media storage become the runtime source for what learners actually see. Seed/import from approved source files with a repeatable, idempotent command; editing a published lesson in the approved admin workflow updates shared content, not only a browser-local draft.

### Standard course package

For a new micro-course, follow the nearest existing course's structure and add only what that course needs. The default structure is:

```text
course-source/<course-slug>/
  README.md
  COURSE_ARCHITECTURE.md
  ASSET_REGISTER.md
  lessons/
    MODULE_01_<topic>.md
    ...
  assets/
  preview/
    first-pass/
      index.html              # generated/reviewable preview, not the Django runtime
```

Add a manifest or use the existing project's manifest convention for stable course/module/lesson IDs, ordering, durations, learning outcomes, content source paths, and asset IDs. Keep source figures and provenance in the course asset register. Do not add empty directories or boilerplate files that do not help authoring or production.

### Rapid deployment workflow

1. Define the learner, course promise, scope, course outcomes and module progression in `COURSE_ARCHITECTURE.md`.
2. Write reviewed student-facing lesson Markdown and prepare/record course-owned or rights-cleared images.
3. Validate the manifest against the lesson files, unique slugs/order values and asset register.
4. Build the static preview/data payload from the source files. Preview generation must never overwrite authored Markdown.
5. Run source validation and browser checks at desktop and mobile widths, including lesson switching, all tabs, image enlargement, accessibility/keyboard use and missing-media fallbacks.
6. Import or update Django records idempotently from the manifest. Preserve existing course/lesson primary keys, progress, enrolments, offers and access rules when updating content.
7. Verify the learner sees database-backed current content and the administrator can edit permitted text/images persistently. Only then mark the course ready; publishing and deploy remain separate, explicit actions.

### Django extraction contract

- Extract the canonical Learning Room into reusable Django templates/partials and shared static CSS/JS, using the existing Academy site's real base template, navigation, logo and design tokens. Do not duplicate a header, use the wrong logo, or introduce a parallel login/page shell.
- Keep the core page layout and interactions in code; pass course-specific curriculum, lesson fields, figure metadata and practice/review data through the existing Academy models/context. Never fork the full monolithic Bollinger HTML for every new course.
- Inspect the existing Django models and migrations before proposing schema changes. Extend/reuse the Academy course/module/lesson/content/media models; do not build a general-purpose CMS if existing models can serve.
- The approved notebook pattern is reusable, but text inside it is course/lesson data. The removed green objective card is not part of the template.
- The admin edit/upload controls are **administrator-only**. A client-side flag, hidden button or `is_staff` check by itself is not permission enforcement. Use a dedicated permission or administrator group assigned only to admins and re-check it on every write.
- All shared text saves and image replacements must persist through Django and shared storage, with CSRF protection, server-side validation, stable database-backed content/media IDs and audit history. Preview localStorage/Data-URL behaviour must not be enabled in production.

## Admin editing and Django handoff

The standalone Bollinger preview contains local-only controls for reviewing image replacement and in-place text editing. Text drafts are saved in the current browser; image changes last only for the open preview session. Neither action saves shared course content.

**When this template is included in Django, remove the local-only preview mode.** Render text/image editing controls only for an authenticated administrator who has the dedicated content/media-edit permission. Do not grant this capability to learners, instructors, ordinary staff or all users with `is_staff` by default. Inject server-checked configuration, stable database-backed content IDs, CSRF tokens and save/upload routes. Re-check administrator permission on every write; validate and sanitise content server-side. Text saving must update shared content in the existing course system, while shared images must use persistent media records/storage and retain audit history.

See `docs/architecture/COURSE_CONTENT_EDITOR.md` and `docs/architecture/INSTRUCTIONAL_IMAGE_REPLACEMENT.md`.
