# TradeThesis Course Template Standard

**Status:** Adopted standard for all new courses and the migration target for every existing course.  
**Design reference:** The saved **TradeThesis Course Template — Updated Learning Room** preview (16 October 2026).  
**Implementation branch:** `my-new-branch`. Do not merge to `main` or deploy without explicit approval.

## Decision

Use the updated TradeThesis course template as the default for every new course and as the target layout for every existing course. Course content, figures, exercises and navigation can differ by subject; the core student experience and visual language should feel consistent across the catalogue.

This is a flexible teaching template, not a form with mandatory labels. Reuse the purpose of a section when useful, rename it in student-facing language, combine sections, or omit one when it adds no learning value. Do not force every lesson into identical cards or repeat explanatory text to fill a layout.

## Shared course experience

Course pages use two connected views:

- **Course overview:** clear promise, who the course is for, measurable learning outcomes, curriculum with lesson titles, practical outputs and a clear route into the learning room.
- **Learning room:** searchable or scannable course outline, a distinctive but compact lesson header, concise lesson summary, estimated study time and a brief sense of what the learner will do.
- **Lesson navigation:** use the template's integrated, restrained tabs—**The idea**, **Chart examples**, and **Test your reading**—as the default. Rename only where a subject makes more natural wording clearer.
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
- An objective can be a brief “By the end, you can…” statement, placed once where it helps.
- Concept and transfer sections should have topic-specific student-facing headings rather than repeatedly showing the same generic labels.
- Internal level labels, production states, build instructions and asset-status notices do not belong in the normal learner view.

## Figure and image standard

- Use local, downloaded or course-owned image files in the finished course—not hot-linked images as a runtime dependency.
- Give figures persistent internal asset IDs in production records and simple student-facing labels such as **Figure 1.1**, **Figure 1.2**, **Figure 2.1**. Number figures by module and keep references in lesson text only when helpful.
- Never place internal asset IDs, difficulty/level labels, “synthetic data” banners or production-state labels inside learner-facing charts. If an image is illustrative or not historical data, explain that in a nearby caption where it matters.
- Keep image-source, copyright/licence, download provenance and replacement notes in an internal asset register, not in the main lesson narrative.
- During first-pass production, externally sourced chart images may be used as temporary visual references when their origin is recorded. They must be replaced with course-owned TradingView captures or images cleared for the intended use before public release. A source URL alone does not satisfy the downloaded-asset requirement.
- Add useful alt text. Keep annotations legible on mobile and when enlarged; use simple static comparisons rather than introducing ChartLab unless explicitly requested.

## Migration rule for existing courses

Every existing course should be migrated to the shared visual and navigation standard, retaining its approved course-specific content and interactions wherever they still make sense. Do not bulk-rewrite course teaching content merely to make it look uniform. Migrate incrementally on `my-new-branch`, preview the result, checkpoint the work in GitHub, and do not merge or deploy without approval.

## Current first-pass target

The initial application pass is **Understand Bollinger Bands**. Its seven-module manuscripts remain the source of truth. The first preview will use the updated Learning Room structure, locally stored visual assets for review, simple module-based figure labels and explicit notes that temporary web-sourced images are placeholders to be replaced by the user's own TradingView captures before release.
