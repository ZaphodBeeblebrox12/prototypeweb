# Understand Bollinger Bands — First-Pass Production Checkpoint

**Branch:** `my-new-branch`  
**Current state as of 17 October 2026:** all 30 lesson manuscripts deepened and connected to the first-pass Learning Room; not merged into `main` or integrated into served course pages.

## Checkpoints saved

1. `course-source/COURSE_TEMPLATE_STANDARD.md` — the shared TradeThesis course template is now the adopted standard for all new courses and the migration target for existing courses.
2. `course-source/understand-bollinger-bands/preview/first-pass/index.html` plus `course-source/understand-bollinger-bands/assets/bollinger-lessons-data.js` — the first-pass Learning Room and its generated student-facing manuscript payload.

## GitHub checkpoint trail

The following work is committed on `my-new-branch`, in sequence:

- `a0278203f177744a94285bf0def4deae38035409` — adopt the shared course template standard.
- `292ad165691b47311ebc24a6eb16e54d65dfe67a` — save the standalone first-pass course preview.
- `5d22a057805a100b28c2e698a97fd62e0c058750` — add this production checkpoint.
- `a0900916d3c2a344f38ac426e268fc3d095548e6` — connect the reusable course creation method to the standard.
- `da3b77cf16d58751713bcbea69fd96d597e644cc` — link the Bollinger README to the standard and preview.
- `92b4346129d1b497872df1d65853ed625b53e915` — record an updated web-source shortlist and clearly mark download status.

Each saved point remains on `my-new-branch`; none is merged or deployed.
- `02bcd3f94503654b1d535a31131fc8160b5ed025` — remove the visible “SYNTHETIC DATA” label from the course preview fallback and add module/lesson-based figure numbering inside generated chart illustrations.

## Inline visualization runtime fix — 16 October 2026

- `e163d1c606d0b03da084a9260fcdcf8433327aad` — fixed `practiceCases()` indexing in `preview/first-pass/index.html`. The object stores examples by module IDs 1–7, but the previous lookup used `cases[mId - 1]`; Module 1 therefore received `undefined`, and the lesson renderer failed when calling `.map()`.
- Corrected lookup: `return cases[mId];`
- Browser smoke test with Chromium/Playwright: **passed**. Loaded the standalone HTML, navigated all 30 lessons through the lesson-rendering path, checked the practice panel and SVG chart for every lesson, and opened/closed the chart zoom modal. Zero page errors and zero console errors after the fix.

## Focused source checks

- The checkpointed preview contains the seven-module / 30-lesson curriculum.
- Inline teaching-chart SVGs are generated locally by the preview, but reference-image figures may use temporary remote source URLs and are not all local assets.
- The chart zoom modal, lesson tabs, lesson outline, learner response area and completion action are present in source.
- A full browser screenshot smoke test has not completed in this environment. Downloading third-party historical chart binaries also remains blocked by outbound network/DNS restrictions; the internal source index records candidate pages without pretending their images are local files.


## Lesson-depth and Learning Room integration — 17 October 2026

### What changed

- Expanded all 30 Markdown lesson manuscripts with lesson-specific worked comparisons. The 24 shorter lessons in Modules 1–4 and 6–7 now contain a second worked comparison in addition to the first; Module 5 retains its longer method/setup instruction and historical case discussions.
- Added `assets/bollinger-lessons-data.js`, generated from the Markdown manuscripts. It carries the full student-facing content into the preview's three existing tabs, **The idea**, **Chart examples**, and **Test your reading**. The Markdown lesson files remain the content source of truth.
- Updated `preview/first-pass/index.html` to load that generated file, render the fuller lesson copy, show lesson-specific chart examples and exercise content, and use one unique knowledge-check question per lesson.
- Increased main lesson paragraph text from 11px to 13px and added rendering for lists, block quotes and Markdown tables. Removed the stale Volume & Price Analysis fallback copy from the initial lesson panels; the explicit related-course cross-link remains where intended.
- Updated `tools/qa/check_bollinger_preview.py` to verify the data binding, all 30 lesson records, unique quiz prompts, populated idea/example/practice tabs, and a minimum lesson-content size.

### Checkpoint commits

- `d28ee10b886b0688c8f9a4634463cd650848594d`, `9ca95350f475463817a030cf111f13381cf11bf7`, `4d52e2f480c361e5af675663e9612b71017d1d32`, `befb1ebc61529c1d9a68fa2c84564d88fe585828`, `d718d3f528d6e48ae9cedcfe08be589c03d76848`, `e8562c9e602b6ab857c4367b8284d05eee554923` — second worked comparisons added across Modules 1–4 and 6–7.
- `d1d5b122a7b48068e6ab304d0b5b9d618de6651a` — regenerate the 30-lesson payload from the expanded manuscripts.
- `b2a00d497cc988e21dbd577caf8418b07b62c579` — connect full manuscripts to the Learning Room and replace its stale fallback panels.
- `d83e5bcd7806be27069934c520b3ee6c6fda301d`, `9dcb4d3e72f08c4c6e14287411e63c9ce09f16b4` — extend the source QA checks and correct the word-count assertion.

### Validation status

A source-level JavaScript syntax/data check passed after the rendering change: both inline preview scripts and the generated content script compile; the data parses to 30 lessons with 30 distinct quiz questions; each lesson has non-empty idea, chart-example and practice content. The current generated lesson content ranges from approximately 907 to 1,503 words across the three tabs.

**Important:** the previous Chromium/Playwright smoke test was run before this manuscript-rendering change. A fresh browser smoke test and screenshot review have **not** yet been run on the new Learning Room content. Image references also remain provisional. This checkpoint records source validation, not a claim that the new browser UI is fully release-tested.

The repository's separate `Deploy TradeThesis preview` workflow is triggered by changes under `tools/qa/**`, but its upload step packages only the `site/` directory. It does not package this `course-source/understand-bollinger-bands/` preview or the generated lesson-data asset.


## First-pass target

The preview follows the seven-module Understand Bollinger Bands manuscript, uses the paper-like TradeThesis look, integrates the lesson navigation, and includes local inline chart illustrations so it does not depend on hot-linked images to render. The visual learning pattern is flexible; the template's section labels are not mandatory boilerplate.

## Image status — important

The current preview's embedded chart illustrations are **provisional teaching visuals**, not the final downloaded historical/source charts requested for the course. Network access from the working container failed when tested against the existing external chart URL, so this pass has not yet downloaded historical web images into the repository. Do not describe the current visuals as downloaded website assets.

Next asset pass:
- Find useful visual examples for relevant Bollinger concepts and methods.
- Download each usable image as a local repository asset rather than leave it hot-linked in lesson content.
- Record original source URL, source/page title, access date, image filename, and replacement status in the internal image index.
- Use these only as temporary review/reference images; replace them with the user's own TradingView captures before public release.
- Keep student-facing labels at Figure 1.1, 1.2, etc., by module; remove any internal production/level labels from displayed images.
- Re-run broken-reference and responsive image/zoom checks after assets have been placed.

## Teaching/content requirements

- Preserve the seven-module course architecture and its current 30-lesson manuscript.
- Keep student-facing language natural and practical for intermediate traders.
- Use Observe → Interpret → Test as a reasoning habit, not a rigid three-card layout.
- Clearly distinguish author/source trigger rules from course-designed execution and risk-management options.
- No ChartLab for this course; use supplied static visuals and learner reasoning tasks.
- No merge to `main`, no deployment, and no production website integration without the user's explicit approval.
