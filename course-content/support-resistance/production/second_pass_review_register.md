# TradeThesis — Second-Pass Review Register

**Purpose:** Park review and refinement work until the first-pass course build is assembled. This register is not a release sign-off. Nothing listed here should interrupt forward progress unless its status is explicitly marked **true blocker**.

**Workflow rule:** First pass = build the course-wide materials and working drafts, record assumptions, and mark gaps honestly. Second pass = review the assembled course end-to-end, fix inconsistencies, validate the learner experience, and record outcomes here. Do not polish each lesson in isolation while other lessons and assets are still being built.

**Status key:**
- `PARKED — second pass`: intentionally deferred until the first-pass build is complete.
- `WAITING — user material`: requires authentic instructor material; draft the surrounding structure now, but do not invent the evidence.
- `BLOCKER — implementation`: cannot be verified until the learning-room/ChartLab implementation exists.
- `DONE`: reviewed and decision recorded; only use after evidence is attached or location is stated.

## Register

| ID | Priority | Status | Exact location | What needs the second pass | Why it matters / review action |
|---|---|---|---|---|---|
| SP-01 | High | PARKED — second pass | `scripts/lesson01_production_script.md`; `scripts/lessons02-04_production_scripts.md`; `scripts/lessons05-08_production_scripts.md`; `scripts/lessons09-12_production_scripts.md`; `scripts/lessons13-17_production_scripts.md`; `scripts/lesson18_production_script.md`; `curriculum/master_curriculum_blueprint.md` | Cross-course script consistency and canonical source audit | Check lesson titles, learning progression, durations, terminology, duplicated/standalone versions, knowledge checks, learner prompts and handoffs against the master. Fix contradictions once, in canonical sources. |
| SP-02 | High | PARKED — second pass | `student/student_workbook_v1.md`; all lesson scripts in `scripts/` | Workbook-to-lesson alignment | Confirm worksheet fields appear when needed, use course terminology, and never ask students to reveal a real open trade. Remove fields that are unused or add those required by tasks. |
| SP-03 | High | PARKED — second pass | `chart_assets/asset_manifest.csv`; `chart_assets/dataset_manifest.csv`; `chart_assets/charts/`; `chart_assets/data/`; `chart_assets/source/build_chart_assets.py` | Chart visuals, data fidelity, scale, labels and alt text | Compare every exported image with its CSV and manifest. Check wick/body geometry, clipping, synthetic-data labels, axis/context labels, mobile legibility and meaningful alt text. File presence alone is not approval. |
| SP-04 | High | PARKED — second pass | `chart_assets/charts/L01-*` through `L15-*`; `chart_assets/charts/L18-*` | Reveal sequencing and hindsight leakage | Walk states in intended lesson order. Ensure answers/annotations/future candles are absent until their proper reveal. Special attention: Lesson 9 initial approach, Lesson 14 pre-break sequence and both Lesson 18 unseen charts. |
| SP-05 | High | PARKED — second pass | `chart_assets/ANSWER_KEY_AND_REVIEW_NOTES.md`; `chart_assets/charts/*reference*`; Lesson 5 Clear W; Lesson 8 Uneven Lows; Lesson 14 Wider Neckline | Answer rationale and acceptable alternatives | Check that reference drawings are examples, not unique solutions. Document what makes alternatives defensible; avoid arbitrary exact-price or pixel-match grading. Verify ChartLab sequence remains exactly three labs. |
| SP-06 | High | WAITING — user material | `scripts/lessons09-12_production_scripts.md` — Lesson 9; `production/SECOND_PASS_REVIEW_REGISTER.md` | Authentic Lesson 9 instructor micro-case | Await original pre-zone/pre-interaction chart and actual observation/rationale. Create learner-first crop and separate later reveal; do not infer contemporaneous thoughts from hindsight. Synthetic supporting charts may be built meanwhile. |
| SP-07 | High | WAITING — user material | `scripts/lessons13-17_production_scripts.md` — Lesson 16 | Authentic Lesson 16 reaction-based trade | Await real chart/context, thesis, alternative, trigger, risk, management, exit and review. Clearly label reconstructions and missing contemporaneous evidence. Do not write a tidy fictional trade story. |
| SP-08 | High | WAITING — user material | `scripts/lessons13-17_production_scripts.md` — Lesson 17 | Authentic Lesson 17 failed thesis / loss / no-trade case | Await an actual example and candid process review. Preserve thesis/invalidation chronology; distinguish process failure from outcome; disclose evidence gaps. |
| SP-09 | High | PARKED — second pass | `chart_assets/charts/L18-A-*`; `chart_assets/charts/L18-B-*`; `chart_assets/data/L18_A_final_unseen_assessment.csv`; `chart_assets/data/L18_B_parallel_retry.csv`; Lesson 18 script; internal answer notes | Assessment fairness, unseen status, retry equivalence and scoring rubric | Check neither assessment chart appears in prior teaching content; ensure retry measures the same skills without duplicating chart structure too closely; calibrate the provisional 70/100 threshold and no-zero rule in a pilot. Keep reference files instructor-only. |
| SP-10 | High | BLOCKER — implementation | Learning-room course shell (not yet wired in this pack); `prototypes/chartlab/mark-the-zone/` in the website repository; scripts' activity-state specifications | Submission/reveal gates, drawing preservation, persistence and resume | Test actual interactions, not a written specification. Verify learner work survives reveal/navigation/refresh according to implemented behaviour, and reference answers cannot be opened before submission. Requires scoped implementation and explicit approval before repository edits. |
| SP-11 | High | BLOCKER — implementation | ChartLab prototypes in `prototypes/chartlab/mark-the-zone/`; planned Clear W, Uneven Lows and Wider Neckline lesson handoffs | End-to-end ChartLab integration | Run each lab through untouched → mark → submit → reveal → feedback → completion, on desktop and mobile. Check learner marks persist, alternative boundaries are handled fairly, and no additional ChartLab is introduced. |
| SP-12 | Medium | PARKED — second pass | All 18 scripts; `student/student_workbook_v1.md`; chart `alt_text` column in `chart_assets/asset_manifest.csv`; eventual learning-room build | Accessibility package | Finalise captions/transcripts after script freeze; add meaningful chart descriptions and keyboard instructions; inspect colour contrast, non-colour distinctions, focus order, touch targets and reading order. |
| SP-13 | High | PARKED — second pass | `README.md`; `production/coursewide_production_blueprint.md`; eventual public preview and course shell | Student-facing versus instructor-only content boundary | Verify answer keys, internal reference images, instructor trade records and production notes are never exposed in student/public views. Review what appears before purchase versus inside the paid course. |
| SP-14 | Medium | PARKED — second pass | `chart_assets/README.md`; `chart_assets/ASSET_AUDIT.md`; `production/current_build_status.csv`; top-level pack README | Production metadata and counts | Reconcile lesson coverage, chart-state/data counts, version wording and status language after the first-pass asset set stabilises. Do not describe generated drafts as approved or interactive. |
| SP-15 | High | PARKED — second pass | Eventual learning-room implementation; `production/current_build_status.csv`; release gates in `production/coursewide_production_blueprint.md` | Desktop/mobile/keyboard/resume and full learner-journey QA | Walk a new learner from Lesson 1 through the final assessment. Check refresh/resume, progress states, mobile chart sizing, keyboard interaction, errors and completion policy. No claim of persistence or personalised drawing feedback until tested. |
| SP-16 | Medium | PARKED — second pass | Lesson 18 assessment response sheet in `student/student_workbook_v1.md`; Lesson 18 quiz/rubric in `scripts/lesson18_production_script.md` | Rubric calibration and response feedback | Use pilot responses to test score consistency and whether defensible alternate reasoning earns credit. Treat 70/100 as a proposal until pilot evidence supports it. |
| SP-17 | High | PARKED — second pass | All student-facing copy in scripts/workbook and eventual public landing/course pages | Educational scope and no-hype language | Remove claims that a zone guarantees a move, that price alone proves institutional intent, or that examples are signals. Keep observation, interpretation, conditional scenario and invalidation distinct. |
| SP-18 | High | PARKED — second pass | Any proposed source/repo changes; website repository branch used for course integration | Scope approval and change-control review | Before changing site/repo code, show the proposed file-level change set and wait for explicit approval. Course content/artifact creation does not grant permission to commit code. |
| SP-19 | High | PARKED — second pass | `production/learning_room_implementation_spec_v1.md`; future learning-room code | Learning-room specification against actual site architecture | Confirm each proposed interaction maps cleanly to the existing site and that progress/save semantics are explicit. This is a design verification, not evidence of implementation. |
| SP-20 | High | PARKED — second pass | `production/course_content_manifest_v1.json`; `production/CONTENT_MANIFEST_VALIDATION_v1.md`; future access-control code | Manifest integrity and access enforcement | Reconcile lesson/activity/asset mapping with canonical sources and verify that hidden answer assets cannot be served in learner states. |
| SP-21 | High | PARKED — second pass | `production/recording_assembly_cue_sheets_v1.md`; `.csv`; canonical scripts and chart assets | Cue/source alignment, runtime and reveal sequencing | Check all 153 cues against the canonical scripts, resolve missing practice assets or timing discrepancies, and verify no cue leaks future information. |
| SP-22 | High | PARKED — second pass | `student/learner_activity_pack_v1.md`; `production/learner_activities_v1.csv`; `scripts/` | Learner activity alignment and readability | Verify all 18 activities match their canonical scripts, chart states, worksheet fields and reveal order; check mobile/readability load and remove duplicate prompts. |
| SP-23 | High | PARKED — second pass | `production/feedback_bank_internal_v1.md`; `production/activity_feedback_map_v1.csv`; all lesson scripts | Trigger accuracy and feedback calibration | Check every feedback trigger against the scripted interaction, validate acceptable alternatives, and confirm feedback praises evidence/reasoning rather than lucky predictions. |
| SP-24 | High | PARKED — second pass | `production/feedback_bank_internal_v1.md`; `production/course_content_manifest_v1.json`; future learning-room access controls | Feedback and answer-key exposure | Test that internal messages are only served in the correct state, and that reference analyses/future chart states remain hidden until submission/reveal conditions are satisfied. |



## Revisit order at the second-pass checkpoint

1. SP-01 and SP-02: lock source-of-truth scripts and workbook alignment.
2. SP-03 through SP-05: approve the assembled chart sequences and answer rationale.
3. SP-06 through SP-08: close or explicitly disclose authentic instructor-material gaps.
4. SP-09 and SP-16: check the assessment, retry and rubric together.
5. SP-10 through SP-13, SP-15 and SP-18: review the implemented learner experience, access boundaries and change control.
6. SP-14 and SP-17: final metadata, wording and release checks.

**Do not mark the course release-ready while any high-priority item remains unresolved.** The point of this register is to postpone review, not to waive it.


| SP-25 | High | PARKED — second pass | `student/knowledge_checks_v1.md`; `production/knowledge_check_bank_v1.csv`; canonical scripts | Knowledge check source alignment and distractor quality | Verify every question is supported by its lesson, one answer is defensible, distractors test likely misconceptions, and wording does not turn nuanced concepts into rigid rules. Confirm Lesson 18 remains the canonical seven-question check. |
| SP-26 | High | PARKED — second pass | `production/lesson_completion_criteria_v1.md`; `.csv`; eventual learner-room UI | Completion, retry and scoring policy | Pilot the proposed 2/3 formative threshold, feedback-before-retry order, completion state versus concept mastery, Lesson 18's proposed 70/100/no-zero rubric, and ensure low formative scores do not block all progress. |
| SP-27 | High | PARKED — second pass | `production/course_content_manifest_v1.json`; `student/knowledge_checks_v1.md`; `production/knowledge_check_answer_key_v1.md` | Student/internal separation for checks and answers | Verify internal key and correct answers are not exposed before submission. Manifest metadata is not access control; verify actual server/client payload boundaries when implemented. |


| SP-28 | Medium | PARKED — second pass | `student/course_orientation_v1.md`; `student/course_map_v1.md`; `production/orientation_module_handoff_scripts_v1.md`; canonical curriculum and lesson packs | Course orientation and module handoff alignment | Check the learner-facing claims, skill progression, titles, module boundaries and three ChartLab references against the canonical curriculum. Remove promises of features that are not implemented. |
| SP-29 | Medium | PARKED — second pass | `production/orientation_module_handoff_scripts_v1.md`; lesson scripts; eventual recording edits | Narrative repetition, pacing and learner tone | Read/listen to the orientation and all module bridges in sequence. Tighten repeated statements, confirm timing, and ensure bridges do not reveal later chart outcomes or answer states. |


## SP-30 — Release gate accuracy and status integrity
**Priority:** High · **State:** Parked for second pass

**Location:** `production/COURSE_RELEASE_ASSEMBLY_CHECKLIST_v1.md`, `production/release_gate_tracker_v1.csv`, and `production/current_build_status.csv`.

Verify each release gate against the real state of the assets, recordings, interactive implementation, access controls and tests. Distinguish “draft exists” from “verified.” Reconcile hard blockers; do not mark a gate passed on the basis of documentation alone.

## SP-31 — Final go/no-go evidence completeness
**Priority:** High · **State:** Parked for final release

**Location:** `production/release_gate_tracker_v1.csv` and the eventual release evidence log.

Before publication, require evidence for each stop-ship gate, document accepted exceptions, build/version/date, reviewer, known risks and rollback plan. File presence or manifest completeness is not evidence that a learner flow works.


## SP-32 — Student-safe package boundary
**Priority:** High · **State:** Parked — second pass

**Location:** `handoff_packages/tradethesis_sr_learner_safe_preview_v1.zip`, `student/*`, `chart_assets/asset_manifest.csv`, and `handoff_packages/PACKAGE_SEPARATION_AUDIT.md`.

Verify the learner bundle contains only approved student materials and curated first-view charts. Confirm answer keys, reference overlays, raw OHLC data, editable sources, internal IDs, instructor records, future chart stages and the Lesson 18 retry chart are excluded. Reconcile with the canonical scripts before distribution.

## SP-33 — Live access-control and reveal-gating verification
**Priority:** High · **State:** Parked — second pass

**Location:** Eventual learning-room deployment, downloadable assets, network/client payloads and `handoff_packages/PACKAGE_SEPARATION_AUDIT.md`.

Test actual server/CDN/API/browser behaviour. Verify reference answers and future chart stages are not included in learner payloads before submission; confirm only learner-safe downloads are exposed. Static ZIP inspection is not sufficient.

## SP-34 — Facilitator guide alignment and rehearsal
**Priority:** Medium · **State:** Parked — second pass

**Location:** `production/FACILITATOR_PRODUCER_RUNBOOK_v1.md`; all canonical lesson scripts in `scripts/`; `production/recording_assembly_cue_sheets_v1.md`; `production/lesson_activity_map_v1.csv`.

Rehearse the guide against the canonical scripts and cue sheets. Verify title/goal alignment, prompts, chart IDs, reveal timing, module transitions, learner tasks and the three ChartLab placements. Record any missing or mismatched asset rather than substituting content silently.

## SP-35 — Developer handoff against actual site architecture
**Priority:** High · **State:** Parked — implementation scope required

**Location:** `production/DEVELOPER_IMPLEMENTATION_HANDOFF_v1.md`; current website architecture, authentication/member area, asset delivery, entitlement and persistence implementation.

Inspect the actual repository and product architecture; reconcile this stack-neutral contract with current routing, access control, UI conventions, membership entitlement and storage. Before changing site/repository code, present a file-level implementation plan and wait for explicit approval.

## SP-36 — Runtime acceptance test evidence
**Priority:** High · **State:** BLOCKER — implementation/testing

**Location:** `production/implementation_acceptance_test_matrix_v1.csv`; `production/release_gate_tracker_v1.csv`; deployed/staging learning room and protected asset routes.

Execute the matrix after implementation, attach test output/screenshots/network traces and record pass/fail per case. Static package validation is not proof of server-side reveal authorization, drawing persistence, access revocation, or end-to-end ChartLab behaviour. Keep relevant release gates open until evidence exists.


## SP-37 — Module 5 breakout/failure depth, visual assets and lesson-room alignment
**Priority:** High · **State:** PARKED — second pass

**Location:** lessons09-12_production_scripts.md (Lesson 12); lessons13-17_production_scripts.md (Lessons 13–14); course_content_manifest.json (L12–L14); module5_breakouts_author_research.md; and the current site/support-resistance-room.html preview.

Review the expanded reading and author-source attributions against the cited sources; verify that each lesson's field notes, knowledge checks, reveal order and manifest contract agree; test “inconclusive” as a valid response; preserve exactly three ChartLabs with Wider Neckline in Lesson 14; and reconcile the increased lesson timings with the course-wide estimate. Historical NIFTY 50 bands are instructional choices, not official levels, and source redistribution rights are unverified. Replace the provisional chart visuals with user-owned or rights-cleared examples before publication. The Learning Room currently does not render these expanded canonical readings or all lesson-specific note stages; scope and approve that website work separately, then run desktop/mobile accessibility and progressive-reveal QA. Do not mark this item done until source review, asset replacement, timing reconciliation, and end-to-end UI evidence are recorded.

