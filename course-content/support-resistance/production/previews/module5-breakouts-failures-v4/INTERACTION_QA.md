# Interaction and Package QA — Illustrated Module 5 v5

**Scope:** Standalone internal teaching review package. No GitHub or canonical website changes.

## Static checks

- `node --check assets/module5.js`: **passed** for this v5 build.
- `node --check assets/module5-deep-content.js`: **passed** for this v5 build.
- The deep-content JSON contains Lessons 12–14 and 30 total in-reader figure placements using 26 unique schematic figures.
- Lesson 12 has exactly one dedicated volume section. The useful volume explanation is retained before the remainder of the v3 Lesson 12 sequence.
- Lesson 13 puts the simpler v2 break/return/response and three-outcome illustrations before the more detailed retest-depth and three-sequence diagrams.
- Lesson 14 includes individual figures for the range-edge upthrust, downside reclaim, prior swing failure test and continuation-pause outcomes.
- All Markdown figure references resolve to files. All 26 schematic figures, nine historical chart stages and three source CSV excerpts are present.
- Each interactive lesson has five knowledge-check questions; answers unlock after all three staged chart views have been recorded.
- A written response of at least 45 characters is required before the next historical stage is revealed. This is an attempt gate for the local preview, not a measure of analytical quality or a secure access-control feature.
- Field-note labels/prompts differ by lesson and persist locally in that browser.
- The v5 local-storage key prevents cached state from earlier previews being interpreted as the current state.
- Exactly three ChartLabs are preserved in the full curriculum: Clear W, Uneven Lows and Wider Neckline. This package adds no ChartLab.
- Stop-loss markers appear only in FIG21 within Lesson 14. No stop-loss markers occur in Lessons 12 or 13 or on ordinary breakout/retest figures.
- Named author references are kept in `BREAKOUTS_FAILURES_AUTHOR_RESEARCH.md`, not in reader-facing lessons.
- The historical data licence caveat is present in README, source provenance and package manifest.

## Interaction smoke test

Run `node tools/qa_smoke_test_mock_dom.cjs`. The harness checks lesson startup, reading render, stage gating and unlocks, final recap, quiz submission, Lesson 13 simple-to-complex figure order, local note persistence, Lesson 14 taxonomy figures, stop-marker scope, the single Lesson 12 volume section and the author-free reader-facing copy. Record the assertion count and outcome in `QA_SMOKE_OUTPUT.json` after running the script.

The v5 mock-DOM harness passed **24 of 24 assertions** (see `QA_SMOKE_OUTPUT.json`). The package inventory, lesson/figure references, single-volume-section rule, Lesson 13 simple-to-complex ordering, author-name isolation, historical chart counts, and stop-marker scope were also checked. This is an interaction test, not a browser test.

## Browser check status

Full browser-level desktop/mobile screenshot and accessibility QA is still outstanding. A previous headless Chromium run timed out in this environment, so do not treat syntax/static checks or the mock-DOM smoke test as a full visual sign-off. Open `index.html` after extracting the ZIP. Inspect wide desktop, narrower laptop and mobile widths; test keyboard focus, stage advancement, note entry/export, quiz submission, and the simple-to-complex sequence.

## Product boundary

Progress and notes are browser-local only. This is not an authenticated member platform, secure answer-delivery system, server-backed save system, production ChartLab or a published course. Historical chart images/data are for internal review until the source rights are cleared or they are replaced with user-owned/authorised material.
