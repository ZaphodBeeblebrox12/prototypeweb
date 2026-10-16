# Understand Bollinger Bands — First-Pass Production Checkpoint

**Branch:** `my-new-branch`  
**Current state as of 16 October 2026:** initial course preview checkpointed; not merged or deployed.

## Checkpoints saved

1. `course-source/COURSE_TEMPLATE_STANDARD.md` — the shared TradeThesis course template is now the adopted standard for all new courses and the migration target for existing courses.
2. `course-source/understand-bollinger-bands/preview/first-pass/index.html` — a self-contained 2,614-line first-pass interactive course preview built with the updated Learning Room presentation.

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
- No remote image `src` is required by the preview; its teaching visuals are embedded locally in the HTML.
- The chart zoom modal, lesson tabs, lesson outline, learner response area and completion action are present in source.
- A full browser screenshot smoke test has not completed in this environment. Downloading third-party historical chart binaries also remains blocked by outbound network/DNS restrictions; the internal source index records candidate pages without pretending their images are local files.


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
