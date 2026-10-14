# CONTINUATION HANDOFF — TradeThesis Support & Resistance

**Purpose:** Make it possible to resume in a new ChatGPT conversation without relying on previous chat memory. Read this file first.

## Repository state

- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Working branch: `my-new-branch`
- Course source root: `course-content/support-resistance/`
- This is a source/content checkpoint. No website or course-room implementation was performed by these commits.
- Current work style: continue the first pass; defer full cross-document editorial review to the second pass. Add precise entries to `production/second_pass_review_register.md/.csv` when an issue needs revisiting. Do not interrupt the first pass for general polishing unless it blocks correctness or a downstream task.
- **Accepted pre-launch exposure decision (2026-10-15):** The user accepts answer keys, reference assets, and production notes remaining in the public repository while the course is being developed. Treat this as an accepted, non-blocking project decision. Do not raise it again in routine progress updates. Revisit only if the user changes this decision or a concrete learner-delivery implementation requires a specific access-control decision. This records the user's preference; it does not claim that hosted access controls have been implemented.

## Course scope

18 lessons in six modules; planned guided time approximately 5–6 hours plus practice. The course teaches chart reading and decision reasoning, not a signal service or a complete trading system.

### Module map
1. Understand — Lessons 1–2.
2. Find — Lessons 3–5.
3. Draw and evaluate — Lessons 6–8.
4. Read reactions — Lessons 9–11.
5. Breakouts and failures — Lessons 12–14.
6. Apply and review — Lessons 15–18.

### Teaching principles
- Observe first; name the concept after the learner has seen the evidence.
- Separate visible observation from interpretation and speculation.
- Use conditional scenarios and state what would weaken or invalidate them.
- A support/resistance zone is an area of interest, not a guarantee.
- Do not imply that a wick, close, touch count, breakout or retest alone proves an outcome.
- Do not infer institutional intent from the chart alone.
- Allow ambiguity and “stand aside” as valid conclusions.
- Grade reasoning, not pixel-perfect boundaries or whether the eventual price move matches a forecast.
- Label schematic visuals “Illustrative chart — not historical market data.”
- Do not fabricate historical prices, the instructor's trades, or rationale.

## Critical lesson dependencies

- Lessons 1–8: controlled illustrations only.
- Lesson 9: first authentic instructor-chart micro-case. Need an actual source screenshot/export, market/instrument and timeframe, date/session and source, a pre-zone-interaction crop with future candles and outcome hidden, original annotations on a separate layer, and the instructor's genuine observations, interpretation and alternative. Reveal the rationale only after learner response.
- Lesson 16: genuine reaction-based trade/decision record; reveal chronologically and keep outcome last.
- Lesson 17: genuine failed/invalidated thesis, losing trade, or stand-aside/no-trade example; distinguish thesis failure from process failure.
- Lesson 18: final unseen chart, not an already taught or ChartLab chart. Keep answer key hidden until learner submits. The current script defines 7 questions and a 100-point rubric; the 70-point threshold and no-zero conditions are proposals requiring pilot testing, not validated metrics.

## The only three ChartLabs
1. Clear W — Lesson 5.
2. Uneven Lows — Lesson 8.
3. Wider Neckline — Lesson 14.
Do not add another ChartLab activity or move these without explicit user approval.

## Current content in the repository

### `curriculum/`
- `master_curriculum_blueprint.md`

### `scripts/`
- `lesson01_production_script.md`
- `lessons02-04_production_scripts.md`
- `lessons05-08_production_scripts.md`
- `lessons09-12_production_scripts.md`
- `lessons13-17_production_scripts.md`
- `lesson18_production_script.md`

### `student/`
- `course_orientation.md`
- `course_map.md`
- `student_workbook.md`
- `learner_activity_pack.md`
- `knowledge_checks.md`

### `production/`
- `coursewide_production_blueprint.md`
- `orientation_module_handoff_scripts.md`
- `learner_activities.csv`
- `activity_feedback_map.csv`
- `feedback_bank_internal.md`
- `knowledge_check_answer_key_internal.md`
- `knowledge_check_bank.csv`
- `lesson_completion_criteria.md/.csv`
- `learning_room_implementation_spec.md`
- `developer_implementation_handoff.md`
- `facilitator_producer_runbook.md`
- `facilitator_implementation_handoff_validation.md`
- `recording_assembly_cue_sheets.md/.csv`
- `course_content_manifest.json`
- `content_manifest_validation.md`
- `release_gate_tracker.csv`
- `current_build_status.csv`
- `second_pass_review_register.md/.csv`
- `course_release_assembly_checklist.md`
- `release_checklist_validation.md`
- `implementation_acceptance_test_matrix.csv`
- `package_separation_audit.md`
- `package_separation_validation.md`
- `knowledge_check_validation.md`
- `learner_materials_validation.md`
- `orientation_handoff_validation.md`

### `chart_assets/`
- `asset_manifest.csv`
- `dataset_manifest.csv`
- `asset_audit.md`
- `answer_key_and_review_notes.md`

## Binary/source assets not yet individually committed

The v1.8 production archive contains 242 rendered chart files (121 PNG + 121 SVG), 48 OHLC/source CSV files and `chart_assets/source/build_chart_assets.py`. The GitHub connector used in this workflow can create text blobs and commits, but exposes no direct binary-upload/release-asset operation. The files above contain the chart/data manifests and notes, but **do not pretend that the 242 chart files, 48 datasets and generator source are already in Git**.

See `production/BINARY_ASSET_TRANSFER_STATUS.md`. To complete this part, use a local Git clone with ordinary Git credentials or another verified binary-capable upload method; extract the chart/data/source directories from the verified v1.8 ZIP into `course-content/support-resistance/chart_assets/`, preserve filenames and manifest paths, then commit and verify counts/checksums. Do not replace binary assets with text placeholders. Keep the source archive as a backup until verification is complete.

## Release / implementation status

- The facilitator runbook and developer handoff are planning documents.
- The learning room and chart drawing activities are not thereby implemented.
- Server-side reveal authorization, private answer-key delivery, saved learner drawings, cross-device progress, entitlement checks and retry/recovery behavior need implementation and tests.
- The acceptance test matrix lists 32 planned cases; they must remain “not run” until executed against an implementation.
- Do not mark course publication-ready just because the source pack is complete.
- The source scripts are a first-pass draft; the agreed full second pass is deferred until the first pass is complete.

## Recommended next steps

1. Verify the latest branch head and this handoff commit.
2. Finish committing binary/source chart assets from the v1.8 archive using a local Git push or binary-capable path; verify 121 PNG, 121 SVG, 48 source datasets, and generator source are in Git.
3. Add exact SHA-256 inventory for the v1.8 archive and committed asset set.
4. Continue first-pass course production (asset-by-asset recording/media delivery manifest, mapping each cue to exact asset, narration, caption/transcript status, export name and delivery status).
5. Keep authentic instructor chart/trade intake as explicit dependencies until the user supplies the records.
6. At the end of first pass, run the second-pass register across all 18 lessons, all student materials, chart reveals, assessment, wording consistency and accessibility.
7. Only after approval, begin site implementation; do not change or commit site code without explicit user approval.

## Source references

- John J. Murphy, *Technical Analysis of the Financial Markets*: https://www.penguinrandomhouse.com/books/350647/technical-analysis-of-the-financial-markets-by-john-j-murphy/
- Schwager & Etzkorn, Chapter 7: https://onlinelibrary.wiley.com/doi/10.1002/9781119209713.ch7
- Schwager & Etzkorn, Chapter 8: https://onlinelibrary.wiley.com/doi/10.1002/9781119209713.ch8
- Adam Grimes, *The Art and Science of Technical Analysis*: https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202837
- Osler 2000: https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html
- Osler 2001: https://www.newyorkfed.org/research/staff_reports/sr125.html
- Brian Shannon book listing: https://books.google.com/books/about/Technical_Analysis_Using_Multiple_Timefr.html?id=b-Eo0AEACAAJ

## Do not do
- Do not restart from Lesson 1 or re-plan the curriculum from scratch.
- Do not fabricate instructor trade examples.
- Do not add ChartLab studies.
- Do not start a broad second-pass review before first pass is complete.
- Do not say binary chart assets are in Git until their paths and counts have been verified.
- Do not modify website code or commit site changes without explicit user approval.
