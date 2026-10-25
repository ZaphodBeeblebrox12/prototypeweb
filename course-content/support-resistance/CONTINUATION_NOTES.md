# CONTINUATION NOTES — TradeThesis Support & Resistance Course

**Purpose:** This is the durable handoff for continuing work in a fresh ChatGPT conversation. Read this file first, then `README.md`, the master curriculum, the coursewide production blueprint, the current build status, the release-gate tracker, and the second-pass register. Do not rely on chat memory when this file or the source files answer the question.

## Current milestone

- First pass: the written course and production handoff are assembled as a draft.
- Second-pass editorial review: deliberately deferred until the user asks to begin it.
- Repository branch: `my-new-branch`.
- Course materials are under `course-content/support-resistance/`.
- The learning-room/ChartLab production implementation is not complete; acceptance tests are criteria, not test results.
- Authentic instructor examples remain a dependency; do not invent or simulate them.

## Course purpose and voice

An 18-lesson, six-module self-paced course that teaches learners to read structure, choose defensible support/resistance zones, interpret price behaviour, write conditional scenarios, identify invalidation and review decisions without confusing outcome with process quality. It is education, not a signal service or a promise of profitable results.

Voice: calm, warm, professional, specific, honest, low-noise. Avoid hype, forced certainty, institutional-intent stories, and repeated filler. Teach observation → interpretation → conditional scenario → invalidation/reconsideration. “Inconclusive,” “not enough evidence,” and “stand aside” are legitimate outcomes. Do not imply every chart has one uniquely correct drawing. Do not call a zone an unbreakable floor/ceiling, infer institutional intent from a chart alone, or grade pixel-perfect boundaries.

## Curriculum map

1. **Module 1 — Understand:** L1 What support/resistance actually tells you; L2 Read structure before drawing zones.
2. **Module 2 — Find:** L3 Meaningful turning points; L4 Zones rather than perfect lines; L5 Choose relevant areas and reduce clutter. ChartLab Study 1 **Clear W** belongs in L5.
3. **Module 3 — Draw and evaluate:** L6 Defensible boundaries; L7 Keep the chart readable; L8 Evaluate a zone without inventing a magic score. ChartLab Study 2 **Uneven Lows** belongs in L8.
4. **Module 4 — Read reactions:** L9 Approach and first instructor micro-case; L10 Rejection vs acceptance vs inconclusive; L11 How significance evolves with new evidence.
5. **Module 5 — Breakouts and failures:** L12 Crossing vs sustained breakout; L13 Retest and possible role reversal; L14 Failed breakouts and alternate outcomes. ChartLab Study 3 **Wider Neckline** belongs in L14.
6. **Module 6 — Apply and review:** L15 Conditional scenarios; L16 genuine reaction-based instructor case; L17 genuine failed/invalidated thesis, losing trade, or stand-aside/no-trade case; L18 final unfamiliar-chart assessment.

Keep the ChartLab sequence fixed: Clear W (L5), Uneven Lows (L8), Wider Neckline (L14). Do not invent extra ChartLab activities.

## Real instructor examples — hard dependency

- L1–L8: controlled illustrations only.
- L9: first authentic instructor micro-case. Need original screenshot/export and source, instrument/market, timeframe, date/session, pre-zone-interaction crop with future candles/outcome hidden, annotations as separate layer, and the instructor's actual observation, interpretation, alternatives and uncertainty. Do not reveal entry/result in this lesson.
- L16: must use a real reaction-based trade/decision record, revealed chronologically with outcome last. Never fabricate the trade, data or rationale.
- L17: must use a real failed/invalidated thesis, loss, or no-trade/stand-aside decision. Distinguish thesis failure from process failure.
- Ask the user to provide the above when relevant. Until then, preserve clear placeholders and mark the dependency open.

L18 must use an unfamiliar assessment chart not already used in teaching or ChartLab. Do not use a known instructor trade as the sole assessment. Learner submits before reference/answer reveal. The proposed 100-point rubric and 70-point threshold (with non-zero minimums for zone selection and conditional reasoning) require pilot testing; do not present them as validated.

## Chart/data policy

Use original TradeThesis language and charts. Schematic charts must be labelled “Illustrative chart — not historical market data.” Do not invent historical OHLC, trade records, or claim an illustration is the instructor's chart. Each chart needs stable ID, lesson/state, clean and reference variants, alt text, mobile crop, source/rights metadata and reveal rules. Internal reference charts/answer keys must not be exposed to learners. Never leak future candles, reference markings or outcome before learner submission.

The production ZIP v1.8 contains the complete production package, including chart assets and data. The chart asset pack has 242 PNG/SVG chart renders and 48 CSV datasets (plus manifests/source). It is available in the conversation workspace as `/mnt/data/tradethesis_sr_course_production_pack_v1_8.zip` and `/mnt/data/tradethesis_sr_chart_assets_v1.zip`. Those binary archives are **not yet stored in this repository**. The GitHub connector used here exposes text Git objects/trees but no release-asset/binary upload operation. Do not claim the binary images or ZIP are committed. The source generator and datasets should be committed as text/source where possible; the chart images should either be regenerated from committed source/data or uploaded using a real Git/Git LFS/release-asset route. If using GitHub, be careful with repo size and Git LFS policy.

## Production and implementation state

Current committed docs include the master curriculum, lesson scripts, coursewide blueprint, student orientation/map/workbook/activity pack, learner activity CSV, feedback map, knowledge checks and internal answer key, facilitator/developer handoffs, recording cue sheets, content manifest, validation notes, release checklist/gates, build status, second-pass register and acceptance test matrix. Use the repo tree as the source of truth for exact current files.

The learning room is a prototype/specification task, not yet implemented or runtime-tested. Before release, build and test:
- server-side entitlement checks and answer-key/reveal authorization (never rely on hiding a client-side element or URL);
- progressive reveals in the prescribed order;
- save/restore learner drawing and submissions, including retries and failure recovery;
- learner-safe/public package separated from instructor-only answers/reference overlays;
- mobile layout, keyboard/touch accessibility, screen-reader labels and focus behaviour;
- lesson completion and cross-device progress only when backed by real persistence;
- all acceptance matrix cases, explicitly recording pass/fail/not-run.

Do not claim server-side protection, persistence, grading, accessibility or runtime behaviour until implemented and verified.

## Second pass

The user explicitly asked to postpone review until the end of the first pass. Keep adding missing production/build handoff material and update the status/register as required, but do not stop to perform a broad critique or silently rewrite source decisions. Add a second-pass register item for every discovered cross-document conflict or needed review, with the file/section and proposed check. At the end, conduct one coherent review across all 18 lessons, charts, quiz/answer keys, workbook, manifest, recording cues, feedback and implementation requirements.

## Suggested next actions

1. Verify the current GitHub branch head and full `course-content/support-resistance/` tree.
2. Finish uploading any remaining text docs and chart datasets/source that are accessible as standalone files; do not make placeholder files that pretend to contain binary assets.
3. Add a repository-level index/README link to this continuation note, the master curriculum, build status, and production archive manifest.
4. Confirm every L1–L18 script exists in the repo, not merely in chat. Confirm all support docs and test matrices are present.
5. Document the binary asset delivery gap honestly, then select a real upload/rebuild approach.
6. Continue first-pass production tasks. Defer the full editorial second pass until the user explicitly requests it.
7. No website or course-room code changes without the user's explicit approval.

## References

- Master curriculum: `curriculum/master_curriculum_blueprint.md`
- Coursewide production blueprint: `production/coursewide_production_blueprint.md`
- Lesson scripts: `scripts/`
- Build status: `production/current_build_status.csv`
- Release gates: `production/release_gate_tracker.csv`
- Second-pass register: `production/second_pass_review_register.md` and `.csv`
- Acceptance tests: `production/implementation_acceptance_test_matrix.csv`
