# TradeThesis Support & Resistance — Course Production Source

This directory is the canonical working source for the 18-lesson Support & Resistance course.

## Start here in a new chat

1. Read `CONTINUATION_HANDOFF.md` first. It preserves decisions, current state, next action and outstanding dependencies.
2. Read `curriculum/master_curriculum_blueprint.md` for the teaching architecture and all lesson objectives.
3. Read the lesson scripts under `scripts/` in lesson order.
4. Read `production/coursewide_production_blueprint.md`, then the facilitator and developer handoffs.
5. Use `production/current_build_status.csv`, `production/release_gate_tracker.csv` and `production/second_pass_review_register.md` to continue without starting the full second pass early.
6. Use `chart_assets/asset_manifest.csv` and `chart_assets/dataset_manifest.csv` to identify the required visuals and data.

## Directory map

- `curriculum/`: master curriculum blueprint.
- `scripts/`: all 18 lessons, grouped exactly as available in the source packs.
- `student/`: course orientation, course map, workbook, learner activities and student-facing knowledge checks.
- `production/`: facilitator/producer runbook, developer handoff, learning-room spec, activity maps, feedback bank, answer keys, cue sheets, content manifest, release gates, QA validations and second-pass tracker.
- `chart_assets/`: visual/data manifests, asset audit and internal answer/reference notes.

## Status and constraints

This is a first-pass production source checkpoint, not a publication-ready course. The current Git tree contains 246 chart render files (123 PNG and 123 SVG), 49 synthetic illustrative OHLC CSV datasets, the chart-build Python source, manifests and `SHA256SUMS.txt`. The earlier 242 renders (121 PNG and 121 SVG) passed the recorded remote-byte SHA-256 comparison on 2026-10-15. The four new Lesson 13 render files and its new dataset are present in Git and listed in the checksum inventory, but their independent byte-for-byte verification is still outstanding. See `production/BINARY_ASSET_TRANSFER_STATUS.md` and the recording-media review notes for verification boundaries.

Do not claim the learning room, authenticated progress, secure reveal authorization, cross-device persistence, or runtime tests are implemented. The acceptance matrix is a test plan; all runtime tests remain pending until implementation.

The authentic instructor cases for Lessons 9, 16 and 17 remain outstanding. Never fabricate those records. Lesson 18 uses an unfamiliar final assessment chart, not the instructor's trade as the sole assessment.

## Fixed teaching decisions

- Lesson 9 is the first instructor-chart micro-case; hide annotations and outcome until learner response.
- Lessons 16 and 17 need genuine instructor records (reaction-based case and failed/invalidated thesis, losing trade or no-trade case).
- Lesson 18 final assessment uses an unfamiliar chart and preserves answer reveal until after submission.
- ChartLab order: Clear W (Lesson 5), Uneven Lows (Lesson 8), Wider Neckline (Lesson 14); no extra ChartLab activities.
- Teach observation → interpretation → conditional scenario → invalidation/reconsideration.
- “Inconclusive” and “stand aside” are valid answers. No guaranteed outcomes, no pixel-perfect grading, no inference of hidden institutional intent from the chart alone.
- Second-pass editorial review is deferred until the full first pass is complete; record exact locations in the register instead of stopping to polish now.
