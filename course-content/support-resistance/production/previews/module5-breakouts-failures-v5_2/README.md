# TradeThesis — Breakouts & Failures · Chart-Led Review Edition v5.2

**Status:** Standalone internal teaching-review package. No GitHub or canonical website changes have been made. This is not yet a published course, member-account learning room or secure answer-delivery system.

## What this edition changes

The main improvement is not simply friendlier writing: the learner now sees the real chart evidence beside the question being asked. Each lesson's applied historical example begins with its first-stage chart inside the reading. The learner can inspect the prior structure, answer a specific question and move to the staged evidence exercise. Later candles remain hidden until the learner has recorded a reasoned response.

The teaching sequence is: **read the idea → inspect the first chart state → record an initial view → reveal later evidence → compare and revise → use the model answer and self-check.**

## Lessons in this package

- **Lesson 12 — Breakout or Temporary Penetration? (30–35 min):** define the prior structure; distinguish wick, close, time/distance outside and follow-through; compare confirmation rules; understand what volume does and does not add. It now includes a related-course card for the **Volume** course in the TradeThesis catalogue and plain-English definitions of spot FX, CFDs and tick volume.
- **Lesson 13 — Retests and Role Reversal (38–45 min):** begin with simple break/return/response diagrams, then examine the first NIFTY 50 chart state before revealing the return and later response. Covers no retest, shallow/deep return, close inside, cross-through, reclaim and repeated overlap.
- **Lesson 14 — Failed Breakouts and Alternate Outcomes (55–65 min including Wider Neckline):** an expanded taxonomy including range-edge upthrust, spring-like downside failure, trendline penetration/reclaim, prior-swing failure tests, continuation-pause failures, later-pullback failures, neckline failures, gaps/wide bars, reclaims and process-versus-outcome review. This is the only lesson where a hypothetical structural stop is shown—and only on failed-breakout examples.

Estimated guided time across the three lessons: **123–145 minutes**. These are editorial estimates, not validated completion-time claims; measure them with learners before using them in public marketing.

## Open the interactive preview

1. Extract the ZIP into an ordinary folder.
2. Open `index.html` in a desktop browser.
3. Choose Lessons 12, 13 and 14 from the left outline.
4. Read the explanation and inspect the first-stage historical chart beside the relevant question.
5. Use the chart card's **Record your reading in the chart exercise** control, or open **Examine the evidence**.
6. Record a reasoned response at each stage to unlock the next view. The gate is for learning order only; it is not secure answer delivery.
7. Use the lesson-specific **Field notes** and complete the knowledge check after recording all three stages: 7 questions in Lesson 12, 7 in Lesson 13 and 8 in Lesson 14. Automated explanations appear after submission. Each lesson also includes model answers and a short self-check rubric.

Notes and progress are saved in this browser only. They are not saved to a member account or carried to another device.

## Visual and interaction components

- `assets/figures/` contains 26 original schematic teaching figures, FIG00–FIG25.
- `charts/` contains nine staged historical NIFTY 50 daily-OHLC chart views; `data/` contains three corresponding CSV excerpts.
- The first stage of each historical case is also shown inline beside its first-read question. The later stages remain in the staged interaction to preserve the learning sequence.
- The reusable `caseChart` block renders a historical chart, a stage-specific question and a jump to the evidence exercise.
- The reusable `relatedCourse` block can signpost a related course, as Lesson 12 does for **Volume** in the TradeThesis catalogue.
- `FIG19` and `FIG20` are the simpler v2 retest diagrams and appear before more complex illustrations in Lesson 13.
- `FIG21_failed_breakout_structural_stop.png` is the only figure with explicit stop-loss markers. It belongs only to Lesson 14's hypothetical failed-breakout section.

## Teaching rules preserved

- The lessons maintain a calm teacher-to-student voice and explain advanced terms when needed.
- Named author attribution stays in `BREAKOUTS_FAILURES_AUTHOR_RESEARCH.md`, not learner-facing prose.
- Lesson 12 contains exactly one dedicated volume section. The historical NIFTY 50 example is a price-only index chart with no volume bars, so volume is not used to explain its outcome.
- A failed breakout weakens the stated continuation idea; it does not guarantee an opposite move.
- No chart-only statement claims institutional intent, deliberate stop hunting or hidden motive.
- Exactly three ChartLabs remain in the full course: Clear W (Lesson 5), Uneven Lows (Lesson 8) and Wider Neckline (Lesson 14). This package adds no ChartLab.

## Historical data caveat

The nine NIFTY 50 chart images and CSV excerpts are temporary internal teaching examples. The upstream dataset's redistribution licence has not been verified. The user intends to replace these with their own charts later. **Do not publish these chart assets or include them in paid-course delivery until the data is replaced with user-owned/authorised material or rights are confirmed.** Candidate zones are instructional choices, not official index levels.

## Reusable depth method for future modules

`MODULE_DEPTH_WORKING_NOTES.md` records the method built during Module 5: chart-led explanation, observation before interpretation, plain-English first-use definitions, staged examples, model answers, self-study scaffolding, balanced knowledge checks and a separate template pass. Use it as a working standard for the remaining modules, adapting the sequence to the concept rather than copying Module 5 mechanically.

## Next work — separate template pass

`NEXT_PASS_EDITORIAL_AND_TEMPLATE_NOTES.md` records the remaining work. The overall lesson-template audit is deliberately deferred: compare Module 5 with TradeThesis Trading Path for teaching depth, hierarchy, transitions, visual rhythm, reusable blocks and practice flow. The aim is to make later courses faster to build without flattening the teaching.

## QA status

- Reader/content/interaction JavaScript syntax checks pass.
- Mock-DOM interaction suite passed **36/36 assertions**.
- Full browser-level desktop/tablet/mobile visual and accessibility testing remains outstanding. See `INTERACTION_QA.md`.
- This package has not been committed to GitHub or integrated into the website Learning Room.
