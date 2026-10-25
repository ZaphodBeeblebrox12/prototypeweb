# TradeThesis Support & Resistance — Developer Implementation Handoff v1

**Status:** implementation-ready handoff draft, not implemented or approved repository scope. This document describes expected behaviours; it is not evidence that the current site provides them.

## 1. Purpose and boundaries

This handoff turns the course manifest, learner activities, feedback bank, cue sheets, completion criteria and release checklist into a framework a developer can inspect against the existing website. It is stack-neutral by design. The first implementation step is to inspect the approved site architecture and propose a file-level change plan; do not infer permission to modify or commit the repository from this document.

The course is an educational chart-reading toolkit. It is not a signal feed, broker-connected tool, trade-sizing calculator, or evaluator of trading profitability. The product must not imply guaranteed outcomes or certainty about market participant intent.

## 2. Source of truth and artifacts

| Concern | Canonical artifact | Intended use |
|---|---|---|
| Curriculum order, modules and learning outcomes | `curriculum/master_curriculum_blueprint.md` and `production/course_content_manifest_v1.json` | Course structure; second-pass reconcile any conflict before code wiring. |
| Exact narration/prompt/reveal order | `scripts/*production_script*.md` and `production/recording_assembly_cue_sheets_v1.md` | Lesson rendering and recording assembly. |
| Student activities and reusable responses | `student/learner_activity_pack_v1.md`, `student/student_workbook_v1.md`, `production/learner_activities_v1.csv` | Activity content and learner response schema. |
| Chart assets | `chart_assets/asset_manifest.csv`, `chart_assets/dataset_manifest.csv`, `chart_assets/charts/`, `chart_assets/data/` | Stable asset references; use audience/reveal rules in manifest and this contract. |
| Feedback and check content | `production/feedback_bank_internal_v1.md`, `production/activity_feedback_map_v1.csv`, `student/knowledge_checks_v1.md`, `production/knowledge_check_bank_v1.csv`, `production/knowledge_check_answer_key_v1.md` | Student feedback is content; internal keys stay protected. Authored patterns are not automated free-text evaluation. |
| Completion semantics | `production/lesson_completion_criteria_v1.md` and `.csv` | Draft policy; pilot thresholds before adoption. |
| Test/release status | `production/COURSE_RELEASE_ASSEMBLY_CHECKLIST_v1.md`, `production/release_gate_tracker_v1.csv`, `production/SECOND_PASS_REVIEW_REGISTER.md` | Evidence and release gates. |

If a filename in an external working directory differs from the canonical package path above, reconcile it during the second pass; do not silently choose two competing canonical versions.

## 3. Learner-facing route

Use one reusable lesson template rather than 18 bespoke pages. Each lesson block may contain a short text/video segment, staged chart, single/multiple-choice check, free response, reflection, or ChartLab embed. Navigation should keep the module and lesson context clear without overwhelming the chart work area.

Minimum lesson route:

1. Open lesson and render its learner-safe initial content.
2. Show the question/instruction and only the initial chart state permitted at that point.
3. Capture the learner's selected answer, written response or drawing as a draft.
4. Submit; record a durable submission event or clearly state that it was not saved.
5. Only after the required submission, authorize the next reference/reveal state.
6. Preserve and display the learner's original response beside/against the reference; do not overwrite it.
7. Provide authored feedback and any explanation after submission.
8. Let the learner inspect the feedback and complete the required knowledge check/reflection.
9. Mark activity, concept-check and lesson-completion states independently according to the approved completion policy.
10. Proceed to the next lesson without declaring an unimplemented save/resume feature.

“Reveal” is a server-authorized state transition, not just a front-end button or CSS class. The page may announce a reveal action only when the relevant submission is accepted by the authoritative implementation.

## 4. State machine contract

The following is the minimum logical model. Names can be adapted to the codebase, but behaviour should remain equivalent.

| State | Meaning | Allowed next step |
|---|---|---|
| `not_started` | No active attempt for this activity. | `in_progress` |
| `in_progress` | Learner can view permitted content and edit the response/drawing. | `in_progress`, `submitted`, `save_error` |
| `submitted` | A response snapshot was accepted; it is immutable for that submission. | `reference_available` when policy permits; feedback/check steps |
| `reference_available` | Authorized reference stage is available after the submission gate. | `reviewed` |
| `reviewed` | Learner has had the opportunity to compare and review feedback; if an explicit acknowledgement is needed, record it. | `complete` or an allowed retry |
| `complete` | Required lesson activities/checks are completed under current policy. | next lesson; retry only if policy allows |
| `save_error` | Submission/save failed; the learner draft must remain visible and retryable. | `in_progress` or `submitted` after confirmed recovery |

Do not mark `submitted` merely because the learner clicked a button. The authoritative service must confirm receipt and return a stable attempt identifier or equivalent acknowledgement. If the project intentionally offers only local unsaved work, label it honestly; never describe it as saved to an account or resumable across devices.

Retry policy must be explicit. A retry may create a new attempt, but must not silently overwrite the first response or expose the retry reference before its own submission gate.

## 5. Protected asset and reveal rules

Apply access control at the authoritative server/API/storage boundary:

- The initial lesson response includes only assets allowed in the current learner state.
- Internal reference overlays, correct answers, answer rationales, instructor notes, hidden future chart states, Lesson 18 assessment references and retry references are not present in initial student page data or publicly discoverable metadata.
- A private route should authorize a specific learner/activity attempt and state before returning the next reference asset. Guess-resistant IDs are not a substitute for authorization.
- A CSS-hidden element, unlinked URL or client-side boolean is not access control.
- Do not bundle answer keys or private reference assets in a public static JavaScript bundle, source map, or unrestricted CDN directory.
- Keep separate learner-safe and internal asset namespaces/buckets/manifests. Treat the public learner preview ZIP as a content-curation aid, not as proof of live runtime security.
- For Lesson 18, assessment and retry charts remain unseen until used in their intended stage; internal reference overlays are only available after the appropriate submission/reveal authorization.
- For Lessons 9, 16 and 17, the course must render an explicit instructor-case-pending state until real material is supplied and approved. Do not auto-populate fictional personal stories.

## 6. Chart and drawing behaviour

- Use the manifest's stable `asset_id`; do not derive file paths from learner input.
- Provide meaningful alt text and a learner-readable synthetic-data label whenever a fictional chart could be mistaken for historical market data.
- If the interaction is a drawing task, keep the learner's mark coordinates stable as the chart scales/zooms, unless the implementation deliberately uses another accessible input that achieves the same goal.
- Provide undo/clear with usable keyboard and touch interaction; where clearing is destructive, confirm it or provide a reliable undo.
- Reveal must not replace or clear the submitted learner drawing. Show reference and learner response in a way that supports comparison without suggesting pixel matching.
- If an asset fails to load, show a retry/recovery state and retain the learner draft. Do not silently swap in a different chart or reference.
- If no automated interpretation of a free-text answer or drawing exists, feedback should be authored/human-triggered or based on transparent objective rules. Do not claim AI or automatic chart-drawing evaluation.

## 7. Knowledge checks, scoring and completion

- Keep student question payloads free of correct-answer keys, private rationales and instructor notes until the response submission is confirmed.
- Return explanation/feedback only after the intended submission gate.
- Keep these states distinct: activity submitted, knowledge-check result, lesson complete, and Lesson 18 final-assessment result.
- Proposed 2/3 formative score and Lesson 18 proposed 70/100 plus no-zero rule remain provisional until pilot data and reviewed sample scoring justify them. Store thresholds as configuration/content policy rather than hard-coding assumptions through the UI.
- Grade Lesson 18 using the documented rubric and defensible reasoning. Do not pixel-match the reference zone or use a lucky directional guess as the success criterion. Accept reasonable alternative boundaries/scenarios when supported.
- Do not imply “trading proficiency”, profitability, or a predictive advantage from a quiz threshold or course completion.

## 8. Minimum data concepts

Adapt names to the actual project; do not choose a database or persistence technology until the existing architecture has been inspected and approved.

- `Course` / `Module` / `Lesson`: stable IDs, order, title, access policy and canonical content reference.
- `ContentBlock`: order, block type, learner copy, activity/asset link, reveal policy and completion effect.
- `ChartAsset`: stable asset ID, dataset/source, state, audience, alt text and authorization gate.
- `ActivityAttempt`: learner/activity/attempt ID, draft/submission snapshot, timestamps/status and reveal authorization state.
- `KnowledgeCheckAttempt`: selected answers, submission state, score/result when relevant and explanation-seen state.
- `Progress`: latest visited lesson and explicit completion states; save/resume availability must match actual implementation.
- `AccessGrant` or existing entitlement concept: course access determined by the current product/payment architecture; do not invent a new billing model in this content handoff.

Avoid collecting unnecessary sensitive information. Learners should not need to enter brokerage credentials or disclose a live/open trade to complete the workbook.

## 9. Implementation order

1. Inspect the current website architecture, routing, authentication, member-area navigation, asset hosting and entitlement rules.
2. Deliver a file-level implementation plan for explicit approval before modifying site/repository code.
3. Wire course/module/lesson navigation and a shared lesson shell using the structured manifest; validate the source IDs before importing all lessons.
4. Implement one full vertical slice first (a non-sensitive early lesson): initial chart → draft response → confirmed submit → server-authorized reference → feedback → completion.
5. Add protected chart/reference delivery and prove direct-URL/payload access tests pass before populating remaining lesson content.
6. Expand the reusable lesson primitive to Lessons 1–15 and 18. Keep Lessons 9/16/17 in explicitly pending slots until authentic material is supplied.
7. Integrate only the three prescribed ChartLabs at Lessons 5, 8 and 14.
8. Add quiz/check completion rules, state the save/resume guarantees accurately, and integrate with the site's actual membership/entitlement approach.
9. Run the implementation test matrix in `production/implementation_acceptance_test_matrix_v1.csv`, then update the release tracker with evidence.
10. Run the course-wide second pass; pilot knowledge checks and Lesson 18 rubric; complete responsive/accessibility and full new-learner tests; record go/no-go evidence.

## 10. Acceptance criteria (summary)

Implementation is not accepted until each applicable test in `production/implementation_acceptance_test_matrix_v1.csv` has a recorded pass/fail result and evidence. At minimum:

- No private answer/reference/future-state data is available to the learner before the gate, including by direct URL or inspection of served payloads.
- Every response submit has a truthful, confirmed result; failed submissions preserve user work.
- Reveals preserve the submitted response/drawing and occur in script-defined sequence.
- The three ChartLabs complete the whole interaction on desktop and mobile.
- Lesson 18 uses an unfamiliar chart, gates the reference, and routes eligible learners to a separate comparable retry when policy says so.
- Lesson 9, 16 and 17 cannot be mistaken for completed authentic case content while their evidence dependencies remain open.
- Access and progress behaviour reflect the real configured product; no unimplemented save, sync, evaluator or access feature is claimed.
- Accessibility, mobile and end-to-end test evidence is recorded before release.

## 11. Deferred review items

- **SP-35:** Verify this handoff against the inspected website architecture and obtain explicit approval for a file-level code plan before implementation. Location: this document, Sections 1–10; actual website repository and entitlement model. Reason: the handoff is stack-neutral and cannot establish current routes/storage/security.
- **SP-36:** Execute all cases in `production/implementation_acceptance_test_matrix_v1.csv` after implementation and attach evidence to `production/release_gate_tracker_v1.csv`. Reason: documentation and static archive tests cannot prove runtime access controls or persisted state transitions.
- Continue SP-10, SP-11, SP-13, SP-15, SP-18, SP-19, SP-20, and SP-33 as open until actual scoped implementation and tests exist.

## 12. Explicit non-goals

This handoff does not implement the website, authorise repository edits/commits/deployment, promise account sync or resume, create automatic interpretation of drawings/free text, generate signals, or fill the authentic instructor-case dependencies.