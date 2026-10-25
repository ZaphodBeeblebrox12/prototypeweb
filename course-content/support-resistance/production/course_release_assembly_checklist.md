# TradeThesis Support & Resistance — Course Release & Assembly Checklist v1

**State: first-pass production control document. Not a declaration that the course is release-ready.**

This checklist is deliberately evidence-based. A file existing is not the same as the file being reviewed, recorded, implemented, or tested. The agreed workflow remains **build first, review second**: routine editorial and visual refinements can stay in the second-pass register, but known hard dependencies and release blockers must be resolved before public launch.

## Status vocabulary

- **Draft exists** — an artifact is present, but its correctness or suitability has not been approved.
- **Ready for second pass** — assembled enough for the planned course-wide review.
- **Waiting on instructor material** — cannot be completed honestly without real user-supplied evidence.
- **Implementation required** — specification/content exists, but the software behaviour has not been built or verified.
- **Verified** — the named acceptance evidence exists and has been recorded.
- **Blocked** — a required release gate is not satisfied.

Do not mark a gate Verified solely because a related markdown file, CSV, manifest entry, screenshot, or prototype exists.

## A. Canonical content and course structure

- [ ] **REL-01 — Source of truth:** confirm the master curriculum and six canonical script files in `scripts/` are the versions intended for production; record a version/date for the freeze.
- [ ] **REL-02 — 18-lesson coverage:** confirm lessons 1–18 appear once, in the intended order, and titles/module boundaries agree across scripts, course map, activities, completion criteria, cues, and manifest.
- [ ] **REL-03 — No hidden course gaps:** reconcile every cue and learner activity against the canonical script; mark missing chart states or missing copy rather than inventing them silently.
- [ ] **REL-04 — Teaching principles:** preserve observation → interpretation → conditional scenario → invalidation/reconsideration; uncertainty and stand-aside remain legitimate; no zone is described as a guarantee.
- [ ] **REL-05 — ChartLab scope:** verify exactly three prescribed ChartLabs: Clear W (Lesson 5), Uneven Lows (Lesson 8), and Wider Neckline (Lesson 14). No extra lab is introduced accidentally.
- [ ] **REL-06 — Student/instructor split:** identify which files are student-facing, instructor-only, production-only, or internal answer material. The manifest is not security; the actual delivery boundary must enforce this split.

## B. Real instructor cases (hard dependencies)

- [ ] **REL-07 — Lesson 9 micro-case:** receive the genuine chart/export and actual rationale; make a learner-first crop before the relevant interaction and a separate controlled reveal. Do not infer contemporaneous thoughts from hindsight.
- [ ] **REL-08 — Lesson 16 reaction-based trade:** receive the genuine chart/context, thesis, alternatives, trigger, risk, management, exit, and review. Label reconstructions and evidence gaps honestly.
- [ ] **REL-09 — Lesson 17 failed thesis / loss / no-trade case:** receive the authentic case and candid review. Preserve chronology, original invalidation and what was known at each stage; separate process quality from outcome.
- [ ] **REL-10 — Authenticity review:** for all three cases, verify chronology and source evidence and confirm no fabricated prices, dates, annotations, outcomes or recollections have slipped into narration.

These dependencies do not stop unrelated first-pass work, but they do block publication of the affected lesson as though its authentic case were complete.

## C. Chart library and activities

- [ ] **REL-11 — Asset integrity:** compare `chart_assets/asset_manifest.csv` and `dataset_manifest.csv` with actual files; check every required PNG/SVG/data source exists and opens.
- [ ] **REL-12 — Fictional data labelling:** retain the label **“Illustrative chart — not historical market data”** on synthetic chart states and in any page/recording context where viewers could mistake them for live historical charts.
- [ ] **REL-13 — Sequence and reveal:** check clean, staged, practice, and reference states are shown in the intended order. Before submission, do not expose a later outcome, teacher marks, internal reference, or answer rationale.
- [ ] **REL-14 — Defensible alternatives:** every reference overlay is presented as a reasoned example, not the sole acceptable boundary. Avoid pixel matching as the grading rule.
- [ ] **REL-15 — Lessons 16–17:** do not substitute synthetic charts for the required authentic examples; only use them as clearly labelled practice if the canonical script explicitly calls for that.
- [ ] **REL-16 — Lesson 18 unseen/retry:** confirm both assessment and retry charts were not used in teaching/ChartLab, that they test comparable skills without being trivially duplicated, and that reference material remains internal.
- [ ] **REL-17 — Chart usability:** inspect every state at intended desktop/mobile widths, make axes/text legible, and provide chart descriptions/alternative text and keyboard/touch instructions for interactive assets.

## D. Learner materials, quiz and feedback

- [ ] **REL-18 — Workbook fit:** verify worksheet fields match what each lesson asks the learner to observe, explain, conditionally anticipate, and invalidate/reconsider.
- [ ] **REL-19 — Activities and feedback:** match each learner activity to its feedback IDs and states. Check each trigger is fair and that feedback values evidence-based reasoning, not lucky directional guesses.
- [ ] **REL-20 — Knowledge checks:** source-check every question, ensure one defensible answer for each multiple-choice item, and make distractors test intended misconceptions without turning nuance into rigid rules.
- [ ] **REL-21 — Completion policy:** verify lesson completion, concept-check outcome, retry and final assessment are separate states. Keep thresholds provisional until pilot data supports them.
- [ ] **REL-22 — Lesson 18 rubric pilot:** pilot the proposed 70/100 threshold and no-zero rule; review sample submissions, score consistency, and reasonable alternative reasoning before adopting them.
- [ ] **REL-23 — Feedback limitations:** do not claim automatic free-text evaluation unless a real evaluator has been implemented and tested. Authored feedback messages alone do not constitute evaluation.

## E. Recording and assembly

- [ ] **REL-24 — Cue/source alignment:** reconcile all 153 cue rows to current canonical lesson scripts, asset filenames, exact reveal points, voice-over, on-screen copy and pause duration.
- [ ] **REL-25 — Script freeze and recording:** freeze the reviewed spoken copy, record voice-over/on-camera material, capture clean chart states, then assemble edits in cue order.
- [ ] **REL-26 — Captions and transcript:** create and proofread captions/transcripts from the final recording, including meaningful non-speech information and chart action descriptions.
- [ ] **REL-27 — Visual continuity:** standardise title/lower-third/illustrative-chart labels and audio levels without making the course feel like generic SaaS training or adding hype.
- [ ] **REL-28 — Export QA:** check each final video for clipping, audio pops, stale annotations, wrong chart state, accidental future-state reveal, caption timing, export resolution and mobile legibility.

## F. Learning-room implementation and access control

- [ ] **REL-29 — Approved scope:** before editing the website/repository, present the file-level implementation plan and wait for explicit approval. This production pack does not grant repository-change approval.
- [ ] **REL-30 — Lesson end-to-end:** in the actual learning room, test open → study → answer → submit → feedback → retry/reveal → completion. Test refresh, navigation, resume and error states according to implemented behaviour.
- [ ] **REL-31 — ChartLab end-to-end:** for each of the three labs, test untouched → draw/mark → submit → drawing lock/preservation → reveal → feedback → completion on desktop and mobile.
- [ ] **REL-32 — Internal data isolation:** inspect served payloads, routes and direct asset URLs to ensure answer keys, reference overlays, teacher annotations, feedback internals and instructor records are not delivered to a learner before the permitted state. Hiding with CSS is not access control.
- [ ] **REL-33 — Progress and entitlement:** confirm the intended course entitlement, purchase/unlock path, learner progress semantics, and access revocation/support handling match the actual product configuration. Do not assume these are implemented by the content manifest.

## G. Final pre-release review and sign-off

- [ ] **REL-34 — Second-pass register closed or explicitly waived:** review SP-01 onward systematically; each item has evidence and disposition. Do not silently drop an open high-priority item.
- [ ] **REL-35 — Accessibility and device testing:** test keyboard-only, focus order, contrast, screen reader basics, zoom, touch targets, small-screen charts and captions/transcripts.
- [ ] **REL-36 — Full new-learner run:** a tester unfamiliar with the course completes the entire 18-lesson route without instructor intervention, including all labs and the final assessment; note friction and recovery.
- [ ] **REL-37 — Educational and product copy:** verify disclaimers and scope; remove language implying guaranteed results, signals, certainty about institutional intent, or unimplemented features.
- [ ] **REL-38 — Release sign-off:** record build/version, date, responsible reviewer, outstanding known issues, go/no-go decision and rollback plan. Publish only after all stop-ship gates are Verified or formally resolved.

## Stop-ship conditions

Do **not** describe the course as release-ready while any of the following are true:

1. The affected Lesson 9, 16 or 17 is represented as a complete authentic case without the required real material.
2. A correct answer, outcome, reference overlay or internal answer key can be accessed before submission/reveal.
3. A required lesson, lab or final assessment fails its critical end-to-end flow.
4. The synthetic/historical distinction is missing where a synthetic chart could be mistaken for market data.
5. The final assessment has not been piloted but its proposed threshold is presented as validated.
6. A high-priority second-pass item is open with no documented resolution or accepted release exception.

## Current state at this first-pass checkpoint

The content/production artifacts exist as **drafts** and the package has a written learning-room specification. The live learner experience, secure answer gating, interactive ChartLab flows, authentic cases for Lessons 9/16/17, recording exports, and end-to-end QA are **not verified by this pack**. Keep building; do not infer that a release gate has passed from a document or asset existing.

## Evidence log template

For every gate marked Verified, record:

- Gate ID:
- Reviewer:
- Date/build:
- Evidence (file, screenshot, test run, or pilot record):
- Outcome:
- Follow-up / known limitation:

## H. Facilitator and implementation handoff

- [ ] **REL-39 — Facilitator/producer runbook alignment:** rehearse `production/FACILITATOR_PRODUCER_RUNBOOK_v1.md` against canonical scripts, lesson cues and activity assets. Record the version and discrepancies; do not silently substitute missing states.
- [ ] **REL-40 — Developer handoff reconciled:** after the actual site architecture is inspected and the user approves the file-level implementation plan, reconcile `production/DEVELOPER_IMPLEMENTATION_HANDOFF_v1.md` to the real routing, access, entitlement and persistence patterns.
- [ ] **REL-41 — Runtime test matrix executed:** run `production/implementation_acceptance_test_matrix_v1.csv` in the actual staging/runtime environment, attach evidence, and update the tracker for every applicable test. Static documentation/package validation does not count as end-to-end evidence.

REL-39 is an internal assembly/review deliverable. REL-40 and REL-41 remain open until scoped implementation and runtime testing are explicitly authorised and performed.
