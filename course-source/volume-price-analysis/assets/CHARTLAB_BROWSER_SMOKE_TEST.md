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
- Reflection: corrective feedback is shown for a response under the minimum length; completion follows a longer response.
- Restart: forms, outcomes and unlock state reset; Level 1 becomes current.
- At 360px viewport width, the rendered fixture has no horizontal overflow.
- Browser reports `prefers-reduced-motion: reduce` when configured.
- No JavaScript page errors occur in the fixture at desktop or mobile sizes.

## Actual branch page — still required

- Render the committed `vpa-m01-l01-candle-context-lab.html` with its real SVG assets in a normal browser.
- Verify the five mobile sources are selected at 720px and below, and desktop assets are selected at larger widths.
- Visually inspect all five mobile SVGs, particularly labels, candle bodies, volume bars, baseline callouts and the stacked comparison panels.
- Run keyboard-only and assistive-technology tests, including current-step announcements and focus after reveals/restart.
- Check 200% zoom, actual mobile layout, contrast and chart text size.
- Test with a true beginner without coaching and record confusion, pauses and errors.
- Rehearse the entire narrated lesson and record actual runtime.

The fixture checks interaction behaviour and basic responsive layout only. It does not establish that the actual page and charts render correctly, that learner reasoning is semantically graded, or that the course has been validated with novice learners.
