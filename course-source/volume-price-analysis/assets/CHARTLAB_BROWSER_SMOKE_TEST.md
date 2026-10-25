# ChartLab Browser Smoke Test — M01-L01

**Test environment:** Chromium through Playwright in the current execution environment.  
**Test type:** Functional regression fixture using in-memory page content.  
**Scope limitation:** The fixture mirrors the current interaction logic but uses inline stand-in charts. It is not the committed HTML file and does not visually validate the repository's SVG charts.

## Passed checks

- Initial state: Level 1 visible; later levels locked.
- Incorrect Level 1 attempt: feedback shown; progression remains locked.
- Correct Level 1 attempt: Level 2 unlocks and focus moves to the revealed stage.
- Back/forward navigation: active-step indicator follows the visible stage and unlocked stages remain available.
- Level 2 submission: Level 3 unlocks and grading limitation is disclosed.
- Revisiting a lower stage does not relock Level 3.
- Level 3 submission: both alternate outcomes become visible only after submission.
- Source inspection confirms the outcome reveal includes a collapsed optional model-reading disclosure; opening and closing that disclosure still needs direct browser testing on the committed page.
- Reflection: corrective feedback is shown for a response under the minimum length; completion follows a longer response.
- Restart: forms, outcomes and unlock state reset; Level 1 becomes current.
- At 360px viewport width, the rendered fixture has no horizontal overflow.
- Browser reports `prefers-reduced-motion: reduce` when configured.
- No JavaScript page errors occur in the fixture at desktop or mobile sizes.

## Pass 2 — embedded real-chart review build

A separate self-contained Chromium review build used the current five mobile SVG chart exports, inlined as data URLs, with the stage interactions and model-answer reveal. Eleven checks passed:

- All five SVG images decoded to positive natural dimensions and had descriptive alt text.
- Incorrect Level 1 submission remained at Level 1; correct submission unlocked Level 2 and moved focus.
- Back/forward navigation updated the active-step indicator without relocking already unlocked stages.
- Level 2 submission unlocked Level 3 and disclosed that response length is not semantic grading.
- Level 3 submission revealed both outcomes and moved focus to the outcome heading.
- The model-answer disclosure stayed collapsed until outcomes appeared, then opened and closed successfully.
- Reflection, completion and restart worked, with unlock state and focus reset.
- At 360px, the embedded-chart review build had no horizontal overflow.
- No JavaScript page errors occurred during the run.

The review build was reconstructed from a recovered copy of the lesson markup, current committed mobile SVG assets and the checked-in interaction behaviour. It is not a byte-for-byte render of the repository HTML or a test of its actual picture-source selection. This is therefore stronger than the stand-in fixture, but not final acceptance of the exact repository page.
## Actual branch page — still required

- Render the committed `vpa-m01-l01-candle-context-lab.html` with its real SVG assets in a normal browser.
- Verify the five mobile sources are selected at 720px and below, and desktop assets are selected at larger widths.
- Visually inspect all five mobile SVGs, particularly labels, candle bodies, volume bars, baseline callouts and the stacked comparison panels.
- Run keyboard-only and assistive-technology tests, including current-step announcements and focus after reveals/restart.
- Check 200% zoom, actual mobile layout, contrast and chart text size.
- Test with a true beginner without coaching and record confusion, pauses and errors.
- Rehearse the entire narrated lesson and record actual runtime.

The first fixture checks interaction behaviour and basic responsive layout only. Pass 2 additionally checked the embedded current chart assets and model-answer disclosure in a self-contained reconstruction. Neither test establishes that the exact committed page renders correctly at all breakpoints, that assistive technology announces every state correctly, that learner reasoning is semantically graded, or that the course has been validated with novice learners.
