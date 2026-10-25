# TradeThesis — Support & Resistance
## Course-wide production blueprint and build register

**Status:** Working production document  
**Scope:** Turn the 18 lesson scripts into a consistent, testable course experience.  
**Format:** Markdown-first. This document tracks content and production requirements; it does not authorize repository changes.

---

## 1. Production decision

The course should now move from **lesson writing** to **course assembly and production**. The 18 lessons form a clear progression, but lesson scripts alone are not a complete course. The build needs the student-facing workbook, approved chart assets, model responses and feedback, a consistent learning-room experience, and the real instructor material explicitly reserved by the curriculum.

The production rule is: **do not mark a component complete because a script describes it.** A chart specification is not a chart asset; a lesson handoff is not a working interaction; and a planned instructor case is not evidence until the actual records are supplied and reviewed.

### Completion standard

The course is ready for pilot only when:

1. Every lesson's narration, prompts, knowledge check, and feedback are consistent with the master curriculum.
2. Every chart used in the learner experience has a recorded source, instrument/context, timeframe, crop/reveal plan, and approved annotation/reference state.
3. The three ChartLab exercises work end-to-end and preserve learner work through the reveal.
4. Student worksheets are usable on screen and printable/exportable without requiring students to share a real open trade.
5. Lessons 9, 16, and 17 use truthful instructor examples. Any reconstruction is clearly labelled.
6. Lesson 18 has an unseen assessment chart and a distinct parallel retry chart.
7. Mobile, keyboard, accessibility, feedback, resume behaviour, and lesson completion have been tested.
8. Any completion score or threshold is pilot-tested before being represented as validated.

---

## 1A. Agreed workflow — complete the first pass before deep review

The course will be built continuously from beginning to end before the detailed review pass. Do not stop after each lesson or chart to polish it while the rest of the course is unfinished.

**First pass:** assemble all course content and required draft assets; create working learner materials and implementation specifications; record open questions, mismatches and items needing verification in `production/SECOND_PASS_REVIEW_REGISTER.md`. Treat the chart/answer set as a draft, not as implicitly approved. The first pass may continue around missing instructor evidence, but the affected case itself must remain clearly marked as waiting for authentic material.

**Second pass:** after the first-pass course is assembled, work through the register across the whole course. For every item, keep the exact file/lesson location, record the decision or change, and mark it complete only after the check has actually happened. Items involving the real instructor cases remain open until authentic materials are supplied. Implementation checks remain open until the learner-facing behaviour exists and can be tested.

The second-pass register is the source of truth for deferred review. Do not duplicate review notes as disconnected TODOs in lesson files; add a register ID when a local note is needed. Repository/site code still requires explicit approval before changes or commits.

---

## 2. Course map — canonical sequence

| Module | Lesson | Skill the learner is building | Principal practice |
|---|---|---|---|
| 1. Understand | 01 — What support and resistance actually tell you | Interpret zones as areas of possible response, not promises | Observe before explanation |
| 1. Understand | 02 — Read structure before drawing | Distinguish rising, falling, ranging, transitioning, or unclear structure | Structure labelling |
| 2. Find | 03 — Identify meaningful swing points | Select consequential swings without labelling every turn | Swing selection |
| 2. Find | 04 — Zones, not perfect lines | Represent areas where price responses cluster | Boundary comparison |
| 2. Find | 05 — Choose the right areas and reduce clutter | Prioritise useful areas and remove noise | **ChartLab 1: Clear W** |
| 3. Draw and evaluate | 06 — Set defensible zone boundaries | Explain zone width and placement consistently | Boundary practice |
| 3. Draw and evaluate | 07 — Keep the chart readable | Remove marks that do not improve the explanation | Chart editing |
| 3. Draw and evaluate | 08 — Evaluate a zone without inventing a magic score | Review quality contextually instead of relying on a single number | **ChartLab 2: Uneven Lows** |
| 4. Read behaviour | 09 — Read the approach to a zone | Describe approach behaviour before the zone is reached | First short instructor-chart micro-case |
| 4. Read behaviour | 10 — Rejection versus acceptance | Distinguish a reaction, sustained movement beyond an area, and inconclusive evidence | Progressive candle reveal |
| 4. Read behaviour | 11 — How a zone's significance changes | Update a zone assessment as evidence accumulates or weakens | Timeline/evidence log |
| 5. Breakouts and failures | 12 — Breakout or temporary penetration? | Separate a brief crossing from more sustained evidence | Staged breakout sequences |
| 5. Breakouts and failures | 13 — Retests and role reversal | Treat a retest/role reversal as possible, not mandatory | Compare holding and failed returns |
| 5. Breakouts and failures | 14 — Failed breakouts and alternate outcomes | Assess failure without hindsight or certainty | **ChartLab 3: Wider Neckline** |
| 6. Apply and review | 15 — From zones to conditional scenarios | Build if/then scenarios, state invalidation, consider available space | S/R Scenario Card |
| 6. Apply and review | 16 — Case study: a trade based on a reaction | Follow a real decision chronologically from context to review | Authentic instructor trade case |
| 6. Apply and review | 17 — When the thesis fails, or you stay out | Reassess a failed thesis or a justified no-trade decision | Authentic instructor case/post-mortem |
| 6. Apply and review | 18 — Final chart review and knowledge check | Independently apply the full method to an unfamiliar chart | Unseen assessment + parallel retry |

**Learning principle throughout:** observation → interpretation → conditional scenario → invalidation/reconsideration. A reasoned “unclear,” “wait,” or “stand aside” remains an acceptable conclusion.

---

## 3. Current material inventory

These source documents are present in the working materials:

- `tradethesis_support_resistance_curriculum_blueprint.md`
- `tradethesis_sr_lesson01_production_script.md`
- `tradethesis_sr_lessons02-04_production_scripts.md`
- `tradethesis_sr_lesson05_production_script.md`
- `tradethesis_sr_lesson06_production_script.md`
- `tradethesis_sr_lesson07_production_script.md`
- `tradethesis_sr_lesson08_production_script.md`
- `tradethesis_sr_lessons05-08_production_scripts.md`
- `tradethesis_sr_lesson09_production_script.md`
- `tradethesis_sr_lessons09-12_production_scripts.md`
- `tradethesis_sr_lesson13_production_script.md`
- `tradethesis_sr_lessons13-17_production_scripts.md`
- `tradethesis_sr_lesson18_production_script.md`

The lesson scripts are distributed across packs, with some standalone copies. Before publication, designate one canonical version per lesson and verify that any standalone copy matches its pack. Do not edit one version and leave a conflicting duplicate behind.

### Status definitions

- **Specified:** the script/blueprint explains what is needed.
- **Drafted:** the written content exists.
- **Built:** the actual learner-facing file or interaction exists.
- **Verified:** the built item has been tested against the specification.

A status must not be promoted from “specified” to “built” merely because production notes are detailed.

---

## 4. Production register

| Workstream | Current state | Remaining work | Gate to call it complete |
|---|---|---|---|
| Curriculum and lesson scripts | **Drafted** across Lessons 1–18 | Cross-lesson editorial pass; reconcile standalone files with pack versions; standardise terminology, lesson headers, durations, and knowledge-check formatting | One canonical source per lesson, all 18 reviewed against the curriculum |
| Shared student workbook | **Drafted v1** | Cross-check worksheets against canonical lesson prompts during second pass; refine only where gaps are found | Tested against real lesson prompts and clear enough to use without instructor clarification |
| Controlled chart assets | **Drafted: 121 states / 48 synthetic OHLC datasets** | Second-pass visual/instructional review, reveal sequencing, mobile readability and answer-alternative check; track in SP-03–SP-05 | Every required chart exported, source documented, crop/reveal sequence checked at actual display size |
| Market-data chart sources | **To verify per asset** | For any historical chart, record instrument, venue/source, timeframe, date range and permissions | Source and context are recorded; learner-visible claim matches available evidence |
| Lesson 9 instructor micro-case | **Blocked on authentic material** | Supply one real chart before the zone interaction, original rationale and separate later context; hide markings/outcome in learner-first crop | The initial chart is genuinely pre-outcome; the instructor's contemporaneous judgement is distinguished from retrospective analysis |
| Lesson 16 real reaction-based trade | **Blocked on authentic material** | Collect pre-trade/context, marked zone, thesis/alternative, trigger, risk, management chronology, exit and review | Every reveal is supported by original records or explicitly labelled reconstruction; no rationale invented to tidy the story |
| Lesson 17 failed thesis / loss / no-trade case | **Blocked on authentic material** | Choose a genuine example, document initial thesis/invalidation, changing evidence, actual response and candid review | Case teaches process, not hindsight; missing contemporaneous evidence is disclosed |
| ChartLab 1 — Clear W | **Prototype/related assets exist; course integration unverified** | Validate final lab data, instructions, submission, reference overlay, feedback and resume behaviour | Full learner path works on desktop and mobile; no reveal before submission |
| ChartLab 2 — Uneven Lows | **Prototype/related assets exist; course integration unverified** | Same integration and QA, with emphasis on defensible boundary alternatives | Learner work can be compared with a reference without treating all alternate boundaries as wrong |
| ChartLab 3 — Wider Neckline | **Specified in Lesson 14; integration unverified** | Confirm the activity is the third and final ChartLab; implement the complete flow | All required states and feedback work; no extra ChartLab is added elsewhere |
| Lesson 18 assessment chart | **Drafted: unseen assessment and parallel retry charts** | Second-pass novelty/fairness review; pilot-test rubric and threshold; keep reference analysis internal | Neither chart appeared earlier; reasonable alternative interpretations are documented; no future outcome leakage |
| Learning-room course shell | **Design/prototype materials exist; production integration unverified** | Map modules, persistent progress, lesson states, chart canvas, mobile navigation, downloads and restart/resume flow | Tested course path from first lesson to completion, including browser refresh and mobile layouts |
| Captions/transcripts | **To finalise after script freeze** | Prepare accessible captions, transcript text, meaningful chart descriptions and keyboard instructions | Caption timing, chart labels and spoken content agree; visual information is not conveyed by colour alone |
| Quality assurance and pilot | **Not yet complete** | Run learner walkthroughs, scoring calibration, technical tests and ambiguity review | Pilot findings recorded and resolved; proposed Lesson 18 threshold retained only if evidence supports it |

---

## 5. Shared learner materials — drafted v1, to cross-check in second pass

The following assets should serve multiple lessons rather than being reinvented each time.

### A. Chart Reading Notes

A repeatable evidence log. Fields: chart/context; structure; zones selected; areas intentionally omitted; boundary rationale; observations; interpretation; alternative explanation; condition that would change the view; invalidation; next opposing area/available space; decision (continue observing, scenario plausible, wait, stand aside); what changed after later evidence.

### B. Zone Review Sheet

A qualitative checklist, not a score that claims predictive precision. It should ask whether the zone is anchored to meaningful structure, whether the reactions are readable, whether the boundaries are defensible, what has happened since, what contradicts the current view and whether the zone still helps explain current price behaviour.

### C. S/R Scenario Card

- Context
- Relevant zone and reason for selecting it
- Scenario A: “If …, then … becomes more plausible”
- Scenario B or defensible stand-aside alternative
- Evidence that would support further consideration
- Invalidation / what would make the thesis less plausible
- Next opposing zone and available space
- What remains unknown

This card is an analysis aid, not an entry signal, risk-size calculator or trade recommendation.

### D. Case-study review sheet

Keep separate fields for the original thesis, planned invalidation, actual new evidence, decision/action, execution/process quality, outcome and one improvement. A winning result must not validate a poor process by itself; a losing result must not condemn an otherwise coherent process by itself.

### E. Assessment response sheet

Give learners a way to save their structure description, zone drawings/rationale, observations versus interpretations, conditional scenarios, invalidation and next opposing area before the answer reveal. Do not place the reference answer or scoring key in student-facing downloads before submission.

---


### F. Lesson-level learner activities and feedback (first-pass v1)
- `student/learner_activity_pack_v1.md` — student-facing prompts and response fields for all 18 lessons; excludes reference answers.
- `production/learner_activities_v1.csv` — structured activity map for implementation handoff.
- `production/feedback_bank_internal_v1.md` — internal contingent feedback messages; not a live automatic evaluator.
- `production/activity_feedback_map_v1.csv` — mapping from lesson activity IDs to feedback triggers and reveal rules.
- Second-pass checks: alignment with canonical scripts, alternative reasoning, reveal timing and access control (SP-22–SP-24).

## 6. Chart asset rules

### Controlled / illustrative charts

- Label them **“Illustrative chart — not historical market data.”**
- Use synthetic candles or clearly controlled examples; do not attach invented prices or dates to a real instrument.
- Save an editable source for candles/annotations as well as final images.
- Create a clean state, each intermediate reveal, learner prompt state, and final reference state as needed.
- Use consistent price scale within a comparison unless the lesson explicitly teaches scale differences.
- Keep axes, timeframe and annotation legible on mobile.
- Do not use colours as the only distinction; provide labels/line styles or text equivalents.

### Historical charts

- Record instrument, market/venue if relevant, timeframe, date window, source and rights/permission status.
- Preserve the original chart image separately from instructor markings.
- Separate what was visible at the time from later candles and hindsight notes.
- If the screenshot is reconstructed, mark it as a reconstruction.
- Do not claim that the instructor had a thought, rule or annotation at the time unless supported by their contemporaneous notes/record.

### Reference answers

Reference drawings are one reasoned example, not a unique correct answer. Each activity needs an answer rationale and a short policy for acceptable alternatives. Feedback should explain the quality of reasoning rather than only show a red/green verdict.

---

## 7. Learning-room interaction contract

Any progressive-reveal activity should define its state transitions before implementation:

1. Untouched chart / prompt
2. Learner draws or enters an answer
3. Submission confirmed
4. Next stage unlocked
5. Reference analysis revealed
6. Feedback explains the learner's reasoning/answer where supported
7. Knowledge check completed
8. Activity/lesson marked complete

The implementation must preserve a submitted drawing when moving to the next stage. Refresh/resume behaviour must be explicit. Do not promise permanent saving, account synchronisation, export, or feedback personalised to a student's exact drawing until that behaviour exists and is verified.

### Shared design direction

- Calm, editorial learning room; chart and task take priority over decorative UI.
- Desktop: compact persistent module/lesson navigation and a wide working canvas.
- Mobile: collapsible navigation; chart controls and submission remain usable without horizontal scrolling.
- One clear primary action for each step.
- Progress supports orientation; badges and completion effects should not overshadow the practice.
- Keep student-facing material separate from instructor-only production and reference content.

---

## 8. Editorial consistency pass

Run this across all 18 lessons before recording or implementation:

- Is the lesson's purpose distinct from the lessons directly before and after it?
- Does the opening pose a concrete chart-reading question rather than begin with definitions alone?
- Does every reveal preserve the learner's opportunity to judge before seeing the answer?
- Are observation, interpretation and conditional inference explicitly distinguished?
- Are alternate but defensible drawings accepted where the visible evidence supports them?
- Are “rejection,” “acceptance,” “breakout,” “retest,” “role reversal,” and “invalidation” used consistently and with appropriate uncertainty?
- Does any prompt imply that one candle, a touch count, or the zone alone guarantees a future move?
- Does each quiz have a correct answer and a brief explanation for why it is best supported?
- Are asset specs, model answers, accessibility notes and website handoff present?
- Do instructor examples accurately distinguish contemporaneous records from retrospective reconstruction?
- Are public preview and paid lesson content separated appropriately?
- Do worksheet fields and chart labels use the same terms as the lesson scripts?

---

## 9. Recommended build sequence — first pass, then second pass

### First pass — assemble without stopping for local polish

1. Keep the 18 canonical lesson sources assembled in their current pack structure and build the reusable workbook and chart assets against them.
2. Draft all synthetic lesson and assessment assets, staged states and reference notes required to cover the curriculum. Keep the final assessment separate from teaching examples.
3. Draft the course shell/interaction specification and map activity states without claiming the features are implemented.
4. Mark Lesson 9, Lesson 16 and Lesson 17 instructor examples as waiting for authentic material; continue all work that does not depend on those records.
5. Record discrepancies and open questions in `production/SECOND_PASS_REVIEW_REGISTER.md` using an ID and exact location. Do not derail the first pass for non-blocking polish.

### Second pass — whole-course review after assembly

1. Reconcile script versions and cross-lesson terminology; align the workbook to the canonical scripts.
2. Review every chart state and its data/alt text; verify reveal sequencing, acceptable alternatives and answer rationales.
3. Review the real instructor cases when authentic records are available and document any reconstructions or evidence gaps.
4. Test ChartLab and all progressive reveal interactions in the implemented learning room, including no-early-reveal, saving/resume and mobile use.
5. Pilot Lesson 18 and calibrate the rubric before setting a firm completion threshold.
6. Complete captions, accessibility and public-versus-paid/instructor-only content checks.
7. Update every register entry with the decision/evidence and status. Do not mark the course release-ready while a high-priority item remains unresolved.

### Change control

Any repository or website code changes require a proposed file-level scope and explicit user approval before editing or committing. Building these standalone Markdown/chart assets does not authorize code changes.

---

## 10. Instructor material intake — exactly what will be needed later

### Lesson 9 — short micro-case

1. Original chart screenshot/export before the interaction with the zone, if available.
2. Instrument/market, timeframe, date/session and source.
3. What you actually observed and thought at that time, including uncertainty.
4. Your original zone/annotations as a separate layer or image.
5. A later chart only if needed to show context; hide outcome and trade details in the first reveal.

### Lesson 16 — genuine reaction-based trade

1. Pre-trade chart and any higher-timeframe chart actually used.
2. Entry-time screenshot or an honest reconstruction if no contemporaneous image exists.
3. Original zone, thesis, at least one alternative, trigger and planned invalidation.
4. Actual entry, risk/stop, management decisions, exit and outcome.
5. Chronological management screenshots/notes.
6. Brief candid review: what was sound, what was a mistake, and what remains uncertain.
7. Confirmation of what can be shown publicly and masking needs.

### Lesson 17 — genuine failed thesis, losing trade, or no-trade decision

1. Pre-decision chart before the outcome is visible.
2. Original zone and thesis, including what would have invalidated it.
3. The first evidence that changed or challenged the thesis.
4. What you actually did and why.
5. Subsequent chart/exit/outcome if applicable.
6. Candid process review, including genuine mistakes and missing evidence.
7. What must be redacted before publication.

---

## 11. Release gates

Do not call the course production-ready until the following are all true:

- [ ] One canonical and reviewed script exists for each of the 18 lessons.
- [ ] Student workbook has been cross-checked against the scripts.
- [ ] All planned charts exist as built assets, with source and reveal metadata.
- [ ] Each knowledge check includes an answer and concise rationale.
- [ ] All three ChartLab activities have passed end-to-end QA.
- [ ] Lesson 9 micro-case is authentic and correctly staged.
- [ ] Lessons 16 and 17 use authentic instructor records or explicitly labelled reconstructions.
- [ ] Lesson 18 assessment and retry charts are unseen and separate from lesson examples.
- [ ] Captions/transcripts and chart text alternatives are complete.
- [ ] Desktop/mobile/keyboard and refresh/resume tests pass.
- [ ] Pilot feedback and scoring calibration are recorded.
- [ ] Paid-course boundaries and public preview have been reviewed.
- [ ] No unpublished answer keys, trade records or instructor-only notes leak into student-facing views.
- [ ] Repository changes, if any, were separately reviewed and explicitly approved.

---

## 12. Current first-pass deliverables and deferred reviews

The student workbook and synthetic chart set have been drafted and assembled alongside the 18 canonical lesson scripts. The next work should continue filling first-pass gaps across the course rather than restarting local reviews. The authoritative list of deferred checks is `production/SECOND_PASS_REVIEW_REGISTER.md`; it identifies the exact file/lesson location and why each check is needed. The authentic Lesson 9, 16 and 17 examples are evidence dependencies, not permission to invent substitutes.


## Course orientation and module handoffs — first-pass draft

- Learner welcome: `student/course_orientation_v1.md`.
- Compact course map: `student/course_map_v1.md`.
- Module openers/exits and production notes: `production/orientation_module_handoff_scripts_v1.md`.

These remain first-pass drafts. SP-28 and SP-29 cover alignment, pacing and repetition in the second pass. They do not imply that the recording or course navigation UI is implemented.