# TradeThesis Support & Resistance — Learning-Room Implementation Specification v1

**Status:** First-pass product specification; not a code change and not a release sign-off.  
**Purpose:** Turn the existing 18 lesson scripts, workbook and draft chart assets into one coherent learner experience.  
**Workflow:** Complete first pass, log issues, conduct one course-wide second pass later.  
**Scope control:** This document does not authorise changes or commits to the website repository.

## 1. Product intent

The learning room should feel like a calm, editorial trading publication with a working chart—not a generic SaaS dashboard and not a signal terminal. Learners are guided through a deliberate sequence: **observe → describe → interpret → construct conditional scenarios → define invalidation → review**. The learning experience teaches judgement and process rather than promising a prediction.

The lesson script remains the canonical source of teaching copy. This specification defines how that copy and its assets are presented and gated. Where script language and this spec differ, do not silently rewrite the teaching claim; log a second-pass note and use the script/master curriculum as the content source of truth until reconciled.

## 2. Primary navigation and page hierarchy

### Course home
- Course title, concise outcome statement and a clear “Continue learning” action.
- Six modules in the established order, each with lesson titles and brief skill descriptions.
- Progress should indicate orientation, not performance status or social rank.
- Display estimated course duration as a guide, not a completion guarantee.

### Module overview
- One short explanation of the module’s job in the larger learning sequence.
- Ordered lesson list with current/complete/locked-or-not-started states, using plain labels rather than attention-grabbing badges.
- Show prerequisite/handoff in language the learner understands: what they practised previously and what this lesson adds.

### Lesson room
Use one shared template so the learner learns the interface once:
1. **Orientation:** lesson title, learning objective and brief handoff.
2. **Learn:** video or text/narration transcript using the canonical script; controls for captions/transcript when video is present.
3. **Look:** chart state or example, with labels and a concise prompt.
4. **Try:** a decision, note or drawing task. The learner is asked to commit to a view before seeing the reference.
5. **Reveal:** staged example or answer rationale, only after the required submission point.
6. **Check:** knowledge-check questions with explanations after submission.
7. **Carry forward:** one-sentence takeaway and a short note field / workbook prompt.
8. **Next:** explicit next-lesson action; do not automatically jump away before the learner can review feedback.

Not every lesson needs all eight blocks as separate visual cards. Keep the structure consistent but the page compact; let chart/practice take visual priority.

## 3. Core interaction contract

### Standard staged chart activity

Required states:
- `not_started`: prompt and student-safe chart state available.
- `in_progress`: learner can draw, choose, or enter a response.
- `submitted`: freeze or snapshot the response and establish the submission timestamp/state.
- `reveal_unlocked`: only after submission is recorded, show the next chart state/reference or next stage.
- `feedback_seen`: learner has access to the explanation and accepted alternatives.
- `complete`: required response and knowledge check satisfied according to lesson rule.

Rules:
- Do not show answer/reference asset URLs, DOM data, or controls in a way that makes the answer retrievable before submission. Hiding an image with CSS is not adequate protection if the asset is publicly addressable and the requirement is confidential answer content; prefer separate access-controlled payloads/routes for internal references.
- Preserve learner marks/notes through submission and reveal. The reference must be an overlay or a separate comparison state so the learner can see their own original response.
- Do not make a geometric match the only grading criterion. Feedback should assess stated rationale, uncertainty, and evidence where the interface can support them.
- If the response is empty, provide a gentle prompt to enter an answer or explicitly choose “unclear / stand aside”; do not force a directional conclusion.
- If a learner navigates away, clearly indicate whether work is unsaved, locally retained, or account-saved. Do not state “saved” until the actual save succeeds.
- Every activity must have a no-reveal “back” path only where it does not violate reveal integrity; after submission, the original submitted answer remains accessible.

### Free-response and written reasoning

- Use text areas with prompts that distinguish **observation**, **interpretation**, **alternative explanation**, **what would change the view**, and **invalidation**.
- Accept short, plain-language responses; the lesson is chart-reading, not an English-writing assessment.
- Avoid AI-personalised judgement unless implemented, tested and separately approved. In the first implementation, use authored sample responses and transparent feedback rules.

### Knowledge check

- Require learner submission before revealing answer explanations.
- Explain why the most defensible answer fits the lesson and why common alternatives are weaker; don't merely show a green tick/red cross.
- Where a question tests uncertainty, permit “not enough evidence yet” when supported by the source lesson.
- Scoring should reflect a check for comprehension, not forecast skill or trading profitability.

## 4. Chart asset and content-access rules

### Student-facing states
Use only the clean/prompt/intermediate states required by the activity. The chart manifest identifies each asset and its state. Synthetic charts must retain the label **“Illustrative chart — not historical market data.”** Do not label synthetic prices with a real instrument, exchange, date, or claimed instructor trade.

### Instructor-only states
Reference images, internal answer-key content, rubric detail and authenticated personal-trade source records must not ship inside the student-facing page payload before they are allowed to be revealed. The Lesson 18 reference assets `L18-A-02-reference-internal` and `L18-B-02-retry-reference-internal` are explicitly internal-only.

### Progressive reveal
- Lesson 10: reveal reaction/follow-through evidence one stage at a time.
- Lesson 11: reveal the zone timeline chronologically.
- Lesson 12: initial crossing first, then return/follow-through/mixed continuation.
- Lesson 14: the “before the break” state must not show the later failure.
- Lesson 18: keep reference/answer files inaccessible until final submission.

### Accessibility fallback
Every chart activity must have meaningful alt text from `asset_manifest.csv`, plus a text alternative for the task. Where free drawing is not keyboard-accessible, provide a structured alternative (for example, choose/describe candidate areas and explain the boundary) that measures the same reasoning. Color must not be the only carrier of meaning.

## 5. Lesson-by-lesson build map

The machine-readable companion is `production/lesson_activity_map_v1.csv`. It maps each lesson/activity to available `asset_id` values and explicitly marks authentic case dependencies.

| Lesson | Primary learning-room pattern | Required chart/activity states | Notes / dependency |
|---|---|---|---|
| 01 | Observe, then label | Clean lower/upper reactions; band/label reveals; clearer and ambiguous practice | Include uncertainty as a legitimate response. |
| 02 | Structure classification | Rising, falling, range, transition timeline, independent chart | Ask for structure before zones. |
| 03 | Swing selection | Clean → candidate turns → reference points → simplified view; separate practice | Accept defensible alternate swing selections. |
| 04 | Boundary comparison | Broad bracket, too narrow, defensible, too broad and independent practice | Keep scale consistent across comparison states. |
| 05 | Selection/editing + ChartLab | Overmarked chart → candidate IDs → reduced reference; **ChartLab 1: Clear W** | Do not introduce another lab. |
| 06 | Boundary rationale | Reaction points, wick/body guides, narrow/defensible/broad examples, practice | Request rationale, not exact price matching. |
| 07 | Edit for explanatory value | Overmarked → merged redundancies → contextual omissions → clean final + practice | No ChartLab. |
| 08 | Qualitative evaluation + ChartLab | Crossings vs interpretable reactions; **ChartLab 2: Uneven Lows** | No magic numeric zone score. |
| 09 | Approach observation | Synthetic directional/overlapping cases + practice; instructor micro-case slot | **Authentic chart and original rationale needed.** Do not replace it with synthetic content. |
| 10 | Progressive reaction/acceptance | First interaction → close away/follow-through; crossing/follow-through/mixed; four practices | Permit inconclusive classification. |
| 11 | Timeline/evidence log | First reaction → second visit → deeper test → move through | Ask what evidence changed and when. |
| 12 | Breakout versus penetration | First crossing followed by return inside, follow-through, or mixed evidence | First view must not leak later bars. |
| 13 | Retest / possible role reversal | Break beyond → return; compare holds versus failure | Never present retest as mandatory or guaranteed. |
| 14 | Failed breakout + ChartLab | Area before break → first move beyond → return through; pullback holds; **ChartLab 3: Wider Neckline** | Keep only the three specified ChartLabs in the course. |
| 15 | Conditional scenario card | Between-two-areas chart, zone reveal, scenario prompt, independent practice | Include alternatives, invalidation, available space, stand-aside. |
| 16 | Chronological authentic trade case | Context, thesis, trigger/risk, management, exit, review stages | **Authentic trade records needed; no fictional trade substitute.** |
| 17 | Failed thesis / no-trade case | Initial thesis, planned invalidation, new evidence, decision and review stages | **Authentic case needed; distinguish thesis failure from process failure.** |
| 18 | Final assessment + retry | Unseen assessment and separate parallel retry; reference assets gated | Unseen status and scoring require second-pass pilot. |

## 6. Learning record and progress model

Minimum conceptual records (not a required database technology):
- `Course`: title, version, modules, access entitlement.
- `Lesson`: stable ID, title, canonical content source, estimated duration, completion rule.
- `LessonBlock`: type (`text`, `video`, `chart`, `question`, `response`, `reflection`), display order, content reference.
- `ChartAsset`: asset ID, dataset ID, state, audience (`student` or `internal`), alt text, reveal gate.
- `ActivityAttempt`: activity ID, attempt number, response snapshot/notes, submitted-at state, reveal state, completion state.
- `KnowledgeCheckAttempt`: selected responses, score if used, explanation-seen state.
- `Progress`: lesson/module completion state and last visited activity.

The first-pass spec does not assume a persistence system. Decide actual storage only after inspecting the website architecture under an approved implementation scope. If the first implementation cannot save to an account, say so in the UI and provide a practical copy/download route only if that route is actually implemented.

### Suggested completion rules

- A reading-only lesson: canonical content viewed or acknowledged plus required knowledge check submitted.
- A chart practice lesson: response submitted before reference reveal plus required knowledge check submitted.
- A ChartLab lesson: mark/response submitted, reference compared, reflection captured; preserve drawing throughout.
- Lesson 18: all assessment sections submitted before final reference; proposed 70/100 threshold and no-zero rule remain provisional pending pilot; don't use result language that implies trading competence or profitability.

These are implementation proposals and must be reconciled with the lesson scripts in the second pass, not treated as already implemented behaviour.

## 7. Visual / responsive direction

- Editorial hierarchy: clear lesson title, one-line purpose, chart/prompt, then supporting copy.
- Wide desktop work area; compact navigation; no oversized decorative hero inside lesson pages.
- Mobile: collapsible module navigation, chart scales to width, no horizontal page scrolling, buttons and drawing tools remain reachable without covering candle evidence.
- For drawing tasks, enable zoom/pan without making annotation coordinates drift; support undo/clear with confirmation where needed.
- Show one obvious primary action at a time (“Submit response”, “Reveal next stage”, “Continue”). Avoid multiple competing calls to action.
- Use restrained progress indicators; do not make badges or gamification more prominent than the learning task.

## 8. Errors, saves and learner trust

- If asset loading fails, display a clear recovery state; do not silently swap to a different chart.
- If submission fails, retain the learner's local draft and clearly state whether it was successfully recorded.
- If an answer reveal cannot be loaded, keep the submitted work visible and provide a retry action rather than unlocking an unrelated reference.
- If progress is not persistent across devices, do not imply that it is.
- Avoid recording real open positions, broker credentials, or other unnecessary sensitive trading data. The worksheets do not require a learner to disclose an open trade.

## 9. Authoring / data conventions

- Use stable IDs from the current asset manifest; do not derive asset URLs from untrusted user input.
- Author a content manifest that maps each lesson block to its canonical lesson/script source and appropriate asset ID.
- Keep reference/answer assets in a separate internal namespace or protected service response; no answer keys inside publicly accessible static metadata.
- Store content as structured blocks so one course shell can host short text, video, chart, choice, free response and reflection without creating 18 bespoke page layouts.
- Each chart block should define: student asset, prompt, input type, required submission, unlock condition, reference asset, rationale, acceptable alternatives, alt text, worksheet destination and completion effect.

## 10. Implementation sequence after first-pass content assembly

This is a proposal for when code scope is explicitly approved; it is not authority to begin code changes now.

1. **Content shell:** module/lesson navigation, shared lesson template and content manifest for Lessons 1–4.
2. **Chart activity primitive:** prompt/response/submission/reveal/reference/feedback state machine; use one Lesson 1 or 4 activity to exercise the full path.
3. **Workbook and reflection:** implement fields in the student workbook and ensure response survives reveal.
4. **Expand lessons:** wire synthetic asset maps for Lessons 1–15 and 18, with the three ChartLabs retaining their exact course positions.
5. **Authentic-case slots:** implement stage templates for Lessons 9, 16 and 17, but leave content clearly waiting until real evidence is provided.
6. **Assessment:** implement Lesson 18 submission and retry gates; keep internal references protected.
7. **Persistence and progress:** choose storage and explicit save/resume behaviour based on the actual site architecture.
8. **Second pass:** process `production/SECOND_PASS_REVIEW_REGISTER.md`, pilot the assessment and perform full journey/accessibility QA.

## 11. Items to log for the second pass

- **SP-19:** Cross-check this specification and `production/lesson_activity_map_v1.csv` against each canonical script and the actual site architecture before any implementation. Exact location: this file, Sections 2–10; activity map, all rows. Why: avoid silently making product decisions unsupported by the source scripts and avoid choosing a data/persistence design before inspecting the repo.
- Keep SP-10 and SP-11 open until implemented interactions are tested. A specification or prototype screenshot is not an end-to-end test.
- Keep SP-06 through SP-08 waiting for authentic user-supplied evidence.
- Keep SP-09 and SP-16 open until the unseen/retry charts and assessment rubric have been reviewed and piloted.

## 12. Non-goals

- This spec does not create a broker-connected tool, trading signal, entry recommendation or trade-sizing calculator.
- It does not claim automatic interpretation of learner drawings.
- It does not claim account saving, cross-device resume, analytics or course access logic are already implemented.
- It does not authorise repository edits, commits, or deployment.