# TradeThesis — Lesson Completion Criteria v1

**Status:** First-pass product/content specification. No website behaviour is implied by this document. Score thresholds are proposed and require pilot testing.

## 1. Separate three states

Do not collapse lesson completion, comprehension and course assessment into one status.

- **Lesson complete:** the learner has completed the required lesson steps and has submitted the required activity/check, with the feedback/reveal made available in the correct sequence.
- **Concept check met:** the learner scores at or above the proposed threshold on that lesson’s formative check. This is a comprehension signal, not an ability-to-trade claim.
- **Course assessment result:** the Lesson 18 chart assessment and its seven-question knowledge check have been submitted, scored against the provisional rubric and reviewed. Treat the proposed 70/100 threshold and no-zero rule as provisional until piloted.

## 2. Standard completion path for Lessons 1–17

A lesson is eligible to be marked complete when all of the following are true:

1. The learner marks the core lesson content as reviewed, after the content is available. Do not use unverified video watch time as a proxy for learning.
2. The required chart/activity response is submitted. If the activity explicitly permits “unclear” or “stand aside,” that counts when the learner records a reason; the interface must not force a directional conclusion.
3. The knowledge check is submitted.
4. The corresponding explanations/feedback are made available and the learner completes the review step.
5. The next-lesson handoff is shown, but navigation does not happen automatically before feedback can be reviewed.

For Lessons 5, 8 and 14, the ChartLab response must be submitted before its reference is revealed. The learner’s submitted drawing/response must be preserved for comparison. These are the only three planned ChartLabs.

## 3. Formative knowledge-check policy (Lessons 1–17)

- Three authored multiple-choice items per lesson, one point per item.
- **Proposed concept-check threshold: 2/3 correct.** This is a first-pass proposal, not a validated standard.
- If the learner scores below 2/3, show explanations for all items and offer a retry. Do not block access to the next lesson solely because of a low score; mark the lesson complete once the required activity/check submission and feedback review are done, but keep “concept check met” as “not yet” until the threshold is reached.
- In the first implementation, retrying the same three items is acceptable as formative reinforcement only if the learner sees explanations first. In second pass, decide whether to author parallel retry forms to reduce answer memorisation.
- Record the attempt score and feedback-reviewed state separately. Do not claim adaptive coaching unless implemented.

## 4. Lesson-specific activity requirements

| Lesson | Activity completion rule |
|---|---|
| 01 | Record a candidate reaction area or explicitly state ambiguity; answer what the zone can and cannot tell you. |
| 02 | Submit a broad structure label plus evidence and uncertainty before drawing zones. |
| 03 | Submit selected swing points and explain why omitted turns are less useful; accept defensible alternatives. |
| 04 | Submit a zone band and evidence for its boundaries; do not require pixel-perfect matching. |
| 05 | Submit the selection/editing decision; preserve the drawing and require submission before Clear W reference reveal. |
| 06 | Submit upper/lower boundary reasoning; grade explanation over exact coordinates. |
| 07 | Submit which marks were merged/removed and why; no ChartLab here. |
| 08 | Submit qualitative zone comparison without a magic score; require submission before Uneven Lows reference reveal. |
| 09 | Complete the synthetic approach observation task. The authentic instructor micro-case must be supplied before final release; never substitute a fabricated personal case. |
| 10 | Submit reaction / possible acceptance / inconclusive classification with evidence. |
| 11 | Complete the evidence log across the staged timeline and state what changed. |
| 12 | Respond at the initial crossing before later candles are revealed; update after subsequent evidence. |
| 13 | Compare a holding return test with a failed return; do not require a retest conclusion when none occurs. |
| 14 | Submit pre-break judgement before later failure is revealed; complete Wider Neckline after submission. |
| 15 | Submit conditional scenario(s), invalidation, next opposing area/available space and alternatives or justified stand-aside. |
| 16 | Chronological authentic case review. Production/release depends on genuine instructor records; no fabricated prices or rationale. |
| 17 | Chronological review of a genuine failed thesis, loss or stand-aside/no-trade example. Clearly distinguish thesis failure from process failure. |
| 18 | Submit the full unfamiliar-chart response and the seven canonical quiz questions; only then unlock the reference analysis and provisional rubric feedback. Retry chart must be different but comparable. |

## 5. ChartLab submission and reveal state machine

`not_started → in_progress → submitted → reveal_unlocked → feedback_seen → complete`

- `submitted` must be persisted before the server releases the reference.
- Keep learner response/drawing visible after reveal.
- If the save or submission fails, show an error and do not say the answer has been saved or unlock the answer.
- Hidden reference images must not be shipped in the initial student payload or be publicly retrievable before the reveal condition.
- Keyboard-accessible structured response is required if free drawing is not accessible.

## 6. Lesson 18 final assessment

The source script proposes a 100-point rubric: structure 15, zone selection 20, boundary rationale 15, behaviour interpretation 15, conditional scenarios 15, invalidation/space 10, reasoning/uncertainty 10. The proposed completion threshold is 70/100 with no zero in zone selection or conditional reasoning. **Do not represent this threshold as validated.** Pilot against multiple defensible answer sets and at least two reviewers before locking the scoring policy. Learners must be able to see how the rubric applies to their response.

## 7. Data and privacy principles

- Keep activity response, drawing/coordinates, quiz answers, attempt score, feedback-reviewed state and completion state as separate data concepts.
- Do not promise cross-device persistence or downloadable results until those behaviours exist and are tested.
- Do not require learners to submit information about a real open trade. Lessons 16/17 should use prepared authentic case materials from the instructor, not ask students to expose confidential trading records.
- Show completion progress as orientation, not leaderboard, social rank or profitability signal.

## 8. Release gate

The criteria above are specifications only. Before release, verify them in the actual learner room on desktop, mobile and keyboard-only navigation. Confirm submission/reveal access controls, refresh/resume behaviour, feedback order, and honest completion labels. Record any change in the Second-Pass Review Register. Do not mark the course release-ready while high-priority blockers remain.