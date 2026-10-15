# TradeThesis — Illustrated Module 5: Breakouts & Failures

**Status:** Internal review package. This is a standalone teaching/interaction prototype, not the canonical website or production course.

## What this version is trying to do

This is a deeper, illustrated module for traders who want to understand breakouts and failed breakouts rather than simply memorise a candle pattern. The main sequence is:

- **Lesson 12 — Breakout or Temporary Penetration?** Explain the prior boundary, distinguish wick/close/follow-through, understand confirmation-filter trade-offs and recognise why even a consistent filter can fail.
- **Lesson 13 — Retests and Role Reversal** Separate the break, the return and the response. Compare hold-like, failure-like and inconclusive outcomes; a retest is not compulsory and role reversal is not guaranteed.
- **Lesson 14 — Failed Breakouts and Alternate Outcomes** Identify contradictory evidence, revise the original thesis without hindsight and consider alternatives without turning failure into an automatic reverse-trade signal. The existing Wider Neckline ChartLab remains here.

The long-form readings contain ten original schematic teaching figures, inline at the points they explain. The historic NIFTY 50 chart stages remain on the separate **Examine the evidence** tab, so later price bars are not shown in the long reading before the learner makes a written attempt.

## Open the interactive preview

1. Extract this ZIP to a normal folder.
2. Open `index.html` in a desktop browser.
3. Choose Lessons 12, 13 and 14 from the left outline.
4. Read the explanation and its illustrations, then open **Examine the evidence**.
5. Record at least 18 characters of reasoning to unlock the next historical chart stage.
6. After all stages, read the recap and open the knowledge check. Use **Field notes** to record observation, interpretation, alternative and revision condition.

Notes and progress are saved in this browser only. This is not an account-backed course system.

## Contents

- `LESSON_12_BREAKOUT_OR_TEMPORARY_PENETRATION.md`, `LESSON_13_RETESTS_AND_ROLE_REVERSAL.md`, `LESSON_14_FAILED_BREAKOUTS_AND_ALTERNATE_OUTCOMES.md` — fuller lesson manuscripts with inline figure references, staged historic chart references, field-note prompts, model recaps and knowledge checks.
- `assets/module5-deep-content.js` — content data generated from the student-facing conceptual sections of the three Markdown manuscripts for the offline reader.
- `assets/module5.js`, `assets/module5.css` — staged chart interaction, notes, quiz and styling.
- `assets/figures/` — ten original schematic teaching diagrams. They are explanatory diagrams, not market data.
- `charts/` — nine progressively revealed historical NIFTY 50 daily-OHLC views.
- `data/` — small OHLC excerpts retained so dates and candle geometry can be audited.
- `CHART_INVENTORY.csv` — historical chart-state inventory and reveal cut-offs.
- `FIGURE_INVENTORY.csv` — figure inventory and intended teaching purpose.
- `BREAKOUTS_FAILURES_AUTHOR_RESEARCH.md`, `SOURCES_AND_DATA_PROVENANCE.md` — source-backed instructional rationale and data caveat.
- `INTERACTION_QA.md` — static asset checks and local interaction smoke-test results.
- `SHA256SUMS.txt` — checksums for package files (excluding the checksum file itself).

## Author-inspired teaching principles

1. **Context before label:** identify the prior area and market state before interpreting the crossing.
2. **Evidence, not magic confirmation:** wick, close, distance, time outside, volume and follow-through are distinct kinds of evidence with different trade-offs.
3. **The response is part of the event:** compare hold, return, move back through, no retest and inconclusive sequences.
4. **Failure revises the thesis; it does not dictate a trade:** contradictory evidence weakens the original interpretation, but does not mandate a reverse trade.
5. **Preserve the earlier judgement:** record what was believed before the later candles appear, then identify what evidence caused a revision.

## Temporary historical-chart status

The user approved the NIFTY 50 daily OHLC examples as temporary internal teaching material and plans to replace them with their own charts later. The chart bars use the source's recorded Open/High/Low/Close values; the selected horizontal areas are instructional annotations, not official levels. The upstream repository's redistribution licence remains unverified. Keep this package for internal review and do not publish or use the chart images/raw extracts in the paid course until rights are confirmed or the examples are replaced with user-owned/authorised data.

## Scope boundaries

- Keep the 18-lesson / six-module curriculum intact.
- Clear W remains Lesson 5; Uneven Lows remains Lesson 8; Wider Neckline remains Lesson 14.
- This module does not prescribe universal volume or two-close rules, a breakout entry, or an automatic opposite-side trade.
- The package has not been committed to GitHub or integrated into the site's Learning Room.
