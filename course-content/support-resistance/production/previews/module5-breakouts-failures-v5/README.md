# TradeThesis — Breakouts & Failures · Illustrated Instructor Edition v5

**Status:** Standalone internal teaching review package. No GitHub or canonical website changes were made for this edition. It is not a published course, not a member-account learning room and not a secure answer-delivery system.

## What this edition is for

Module 5 should feel like a compact, worthwhile workshop rather than a sequence of screens. This edition combines instructor-led long-form reading, carefully staged evidence, simple-to-complex illustrations, a wider failed-signal taxonomy, and notes that preserve what the learner believed before later candles appeared.

The teaching sequence is: **read the concept → examine a simple map → inspect a fuller sequence → record a view before later evidence → compare, revise and explain.**

## Lessons in this package

- **Lesson 12 — Breakout or Temporary Penetration? (30–35 min):** define the prior structure; distinguish wick, close, time/distance outside and follow-through; understand confirmation-filter trade-offs; use one dedicated volume section as context, not a verdict.
- **Lesson 13 — Retests and Role Reversal (38–45 min):** begin with the simple three-panel break/return/response picture from v2, then move through return depth, closing location, hold-like/failure-like/inconclusive responses, and fuller v3 comparisons. Includes no retest, shallow/deep return, close inside, cross-through, reclaim and repeated overlap.
- **Lesson 14 — Failed Breakouts and Alternate Outcomes (55–65 min including Wider Neckline):** an expanded taxonomy including range-edge upthrust, spring-like downside failure, trendline penetration/reclaim, a prior swing break quickly surrendered, a continuation pause that breaks the wrong way, a later pullback that fails, neckline failures, gaps/wide bars, volume context, reclaims and process-versus-outcome review. This is the only lesson where a hypothetical structural stop is shown—and only on failed-breakout examples.

Estimated guided time across the three lessons: **123–145 minutes**. These are editorial estimates, not validated completion-time claims; measure them with learners before using them in public marketing.

## Open the interactive preview

1. Extract the ZIP into an ordinary folder.
2. Open `index.html` in a desktop browser.
3. Choose Lessons 12, 13 and 14 from the left outline.
4. Read each lesson's longer explanation and figures before opening **Examine the evidence**.
5. Record a reasoned response at each historical chart stage to unlock the next view. The gate is for learning order only; it is not secure answer delivery.
6. Use the lesson-specific **Field notes**. They are stored in the current browser only and can be exported as JSON.
7. Complete the five-question knowledge check after recording all three stages.

If browser-local storage is blocked, the preview will show a save warning. Do not assume browser-local notes are available on another device or saved to a member account.

## Visual system

- `assets/figures/` contains 26 original schematic teaching figures, FIG00–FIG25.
- `FIGURE_OVERVIEW.png` is the 26-figure contact sheet.
- FIG19 and FIG20 are the simpler v2 retest/response diagrams and deliberately appear before the more detailed v3 retest graphics in Lesson 13.
- FIG22–FIG25 are additional purpose-drawn figures for the false upside break, downside reclaim, prior-pivot failure test and continuation-pause outcomes.
- `FIG21_failed_breakout_structural_stop.png` is the **only** figure with explicit stop-loss markers. It belongs solely to Lesson 14's hypothetical failed-breakout section.
- `charts/` holds nine staged historical NIFTY 50 daily-OHLC chart views. `data/` holds three corresponding source excerpts.

## Teaching rules preserved

- The student-facing prose is an original, direct instructor voice. Named author attribution is contained only in `BREAKOUTS_FAILURES_AUTHOR_RESEARCH.md`.
- There is exactly one dedicated volume section in Lesson 12. The repeated second volume section from the earlier draft is not present; subsequent Lesson 12 sections from the v3 sequence remain.
- A failed breakout weakens a stated continuation idea; it does not guarantee an opposite move.
- No chart-only statement infers institutional intent, deliberate stop hunting or a hidden motive.
- Stops appear only in the hypothetical failed-breakout examples in Lesson 14. There is no SL marking on ordinary breakout, retest or role-reversal charts.
- Exactly three ChartLabs remain in the full course: Clear W (Lesson 5), Uneven Lows (Lesson 8), and Wider Neckline (Lesson 14). This package adds no ChartLab.

## Historical data caveat

The nine historical NIFTY 50 chart images and CSV excerpts are temporary internal teaching examples. The upstream dataset's redistribution licence has not been verified. The user intends to replace these with their own charts later. **Do not publish, upload as public course assets or include in paid-course delivery until the data is replaced with user-owned/authorised material or rights are confirmed.** The candidate horizontal zones are instructional choices, not official levels.

## QA and package tooling

- `INTERACTION_QA.md` records completed static/interaction checks and the remaining browser QA limitation.
- `SHA256SUMS.txt` covers all package files except itself and `PACKAGE_MANIFEST.json`.
- `tools/build_v5_figures.py` draws the four added schematic figures.
- `tools/prepare_v5_content.py` prepares the updated deep-content source.
- `tools/build_learner_manuscripts.py` exports the three reading manuscripts using `tools/lesson_interactions.json`.
- `tools/qa_smoke_test_mock_dom.cjs` exercises the local preview interactions.

Full browser-level desktop/mobile visual and accessibility testing is still needed. The package has not been committed to GitHub or integrated into the website Learning Room.
