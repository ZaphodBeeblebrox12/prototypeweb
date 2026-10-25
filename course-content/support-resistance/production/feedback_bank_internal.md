# TradeThesis — Support & Resistance
## Internal Learner Feedback Bank v1

**Access:** internal production material. Do not publish this file, rubric notes or reference answer assets directly to learners. Only expose feedback that is intentionally triggered after the relevant learner action; keep reference analyses gated until submission.

**Status:** first-pass draft. Messages are authored feedback patterns, not evidence of an implemented automated evaluator. In production, these messages must be connected to explicit form states or reviewed by an instructor; do not claim free-text understanding is automatically graded unless that feature is built and tested.

## Feedback design rules

- Praise observable evidence and clear reasoning, not a prediction that later happens to be right.
- Distinguish observation from interpretation and both from conditional scenario.
- Treat “inconclusive,” alternate boundaries and stand-aside conclusions as valid when justified.
- Do not infer participant identity, institutional intent, or motives from price alone.
- Do not unlock references or later candles before the script says they are allowed.
- Lessons 9, 16 and 17 need real instructor material; feedback must never imply a fictional case is the instructor’s own.

## Triggered message bank

### Lesson 01 — What support and resistance actually tell you

#### `FB-L01-EVIDENCE_LED` — Learner describes a repeated/related reaction area without predicting

**Trigger:** Learner describes a repeated/related reaction area without predicting.

**Message to learner:**

> You have identified behaviour that is visible in the chart. Keep the description tied to the history shown; the area does not guarantee another reaction.

**Next action:** Continue to the terminology reveal.

#### `FB-L01-OVERCLAIM` — Learner says price must bounce or must break

**Trigger:** Learner says price must bounce or must break.

**Message to learner:**

> That goes further than the chart supports. Rephrase it as a prior reaction area and state what remains unknown about the next move.

**Next action:** Ask for one observation and one uncertainty.

#### `FB-L01-TOO_PRECISE` — Learner insists on one exact price before boundary lesson

**Trigger:** Learner insists on one exact price before boundary lesson.

**Message to learner:**

> For now, focus on the broad area containing the related reactions. We will work on defensible boundaries later.

**Next action:** Continue; avoid grading exact coordinates.

#### `FB-L01-UNCERTAIN` — Learner says unsure or sees no clear area

**Trigger:** Learner says unsure or sees no clear area.

**Message to learner:**

> It is fine not to force a mark. What part of the chart made the area unclear—or what additional context would help?

**Next action:** Allow “unclear” as a legitimate response.


### Lesson 02 — Read structure before drawing

#### `FB-L02-EVIDENCE_LED` — Learner labels structure and cites swings

**Trigger:** Learner labels structure and cites swings.

**Message to learner:**

> Your structure label is supported by the swing sequence you named. Keep the label broad enough to allow transitions and mixed evidence.

**Next action:** Reveal candidate turning points.

#### `FB-L02-OVERCLAIM` — Learner draws zones before describing structure

**Trigger:** Learner draws zones before describing structure.

**Message to learner:**

> Pause the zone drawing and start with the overall path. Is price generally rising, falling, ranging, transitioning, or not clear?

**Next action:** Return to clean chart.

#### `FB-L02-TOO_LOCAL` — Learner relies on one short candle run only

**Trigger:** Learner relies on one short candle run only.

**Message to learner:**

> One short run may not describe the broader structure. Point to the sequence of turns across the visible excerpt, then state any limitation.

**Next action:** Prompt evidence across the chart.

#### `FB-L02-UNCERTAIN` — Learner selects transitional/unclear with rationale

**Trigger:** Learner selects transitional/unclear with rationale.

**Message to learner:**

> That can be a sound read when the evidence is mixed. Name the specific features preventing a cleaner label.

**Next action:** Accept justified uncertainty.


### Lesson 03 — Identify meaningful swing points

#### `FB-L03-EVIDENCE_LED` — Learner selects consequential swings and explains omissions

**Trigger:** Learner selects consequential swings and explains omissions.

**Message to learner:**

> You have prioritised turns that help explain the path rather than marking every fluctuation. The reference set is one defensible reading, not the only possible set.

**Next action:** Compare with reference points.

#### `FB-L03-OVERMARK` — Learner marks nearly every local turn

**Trigger:** Learner marks nearly every local turn.

**Message to learner:**

> More marks do not automatically create a better explanation. Remove one minor turn and check whether the broader structure remains understandable.

**Next action:** Prompt simplification.

#### `FB-L03-UNDEREXPLAINED` — Learner marks points with no reason

**Trigger:** Learner marks points with no reason.

**Message to learner:**

> For each selected point, say what changes there in the visible path—direction, range, or a meaningful local swing.

**Next action:** Ask for evidence per mark.

#### `FB-L03-ALTERNATIVE` — Learner chooses a different but defensible swing set

**Trigger:** Learner chooses a different but defensible swing set.

**Message to learner:**

> A different selection can work if it captures consequential turns and keeps the chart readable. Explain what your set emphasises and what it leaves out.

**Next action:** Accept coherent alternatives.


### Lesson 04 — Zones, not perfect lines

#### `FB-L04-EVIDENCE_LED` — Learner chooses a band anchored to reactions

**Trigger:** Learner chooses a band anchored to reactions.

**Message to learner:**

> Your boundaries connect to the reactions you named. A defensible zone covers useful evidence without claiming more precision than the chart offers.

**Next action:** Reveal narrow/broad comparison.

#### `FB-L04-TOO_NARROW` — Learner draws a hairline that misses related reactions

**Trigger:** Learner draws a hairline that misses related reactions.

**Message to learner:**

> Check whether the band captures the range of related responses. If not, explain why those excluded prices should be ignored—or widen the area.

**Next action:** Compare same-scale alternatives.

#### `FB-L04-TOO_BROAD` — Learner includes unrelated movement

**Trigger:** Learner includes unrelated movement.

**Message to learner:**

> The band may be covering behaviour that does not belong to the same reaction area. Which part is essential, and what can be left outside?

**Next action:** Ask for a narrower rationale.

#### `FB-L04-ALTERNATIVE` — Learner chooses boundaries differing from reference

**Trigger:** Learner chooses boundaries differing from reference.

**Message to learner:**

> Do not aim to match the reference pixel for pixel. Explain what evidence each boundary includes, and acknowledge the trade-off created by your width.

**Next action:** Score explanation over coordinates.


### Lesson 05 — Choose the right areas and reduce clutter

#### `FB-L05-EVIDENCE_LED` — Learner keeps distinct explanatory areas and removes redundancy

**Trigger:** Learner keeps distinct explanatory areas and removes redundancy.

**Message to learner:**

> The simplified chart is doing a clearer job when each remaining mark contributes distinct information. Explain any mark you kept that could still be redundant.

**Next action:** Proceed to Clear W lab after submission.

#### `FB-L05-OVERMARK` — Learner keeps almost every candidate

**Trigger:** Learner keeps almost every candidate.

**Message to learner:**

> Try comparing marks that sit on the same reaction cluster or tell the same story. Which ones can be combined without losing useful context?

**Next action:** Prompt merge/remove pass.

#### `FB-L05-OVERPRUNE` — Learner removes all but one mark without explanation

**Trigger:** Learner removes all but one mark without explanation.

**Message to learner:**

> A clean chart is not necessarily a useful chart if relevant context disappears. Which removed area explained a distinct reaction or opposing context?

**Next action:** Ask what information was lost.

#### `FB-L05-UNCERTAIN` — Learner explains trade-offs and leaves a candidate undecided

**Trigger:** Learner explains trade-offs and leaves a candidate undecided.

**Message to learner:**

> You do not have to force every candidate into a permanent keep/remove decision. State what context would help you decide whether it adds value.

**Next action:** Record as reconsider, not automatically wrong.


### Lesson 06 — Set defensible zone boundaries

#### `FB-L06-EVIDENCE_LED` — Learner explains upper and lower boundary features

**Trigger:** Learner explains upper and lower boundary features.

**Message to learner:**

> Your boundary explanation is traceable to visible reactions and a consistent use of wick/body evidence. Other conventions can also be defensible when applied clearly.

**Next action:** Reveal comparison examples.

#### `FB-L06-TOO_NARROW` — Zone excludes repeated relevant tails/closes without explanation

**Trigger:** Zone excludes repeated relevant tails/closes without explanation.

**Message to learner:**

> Look at the reactions near each edge. Are you excluding a repeated part of the interaction, or is there a reason that feature should not define the area?

**Next action:** Ask for boundary trade-off.

#### `FB-L06-TOO_BROAD` — Zone includes unrelated turns

**Trigger:** Zone includes unrelated turns.

**Message to learner:**

> What visible evidence justifies the outer edge? If it does not explain the same reaction area, narrow or split your reasoning.

**Next action:** Use too-broad reference.

#### `FB-L06-RIGID_RULE` — Learner says all zones must use wicks or bodies exclusively

**Trigger:** Learner says all zones must use wicks or bodies exclusively.

**Message to learner:**

> There is no universal wick-only or body-only rule established here. Tell us what your chosen convention is intended to represent and apply it consistently.

**Next action:** Accept documented convention.


### Lesson 07 — Keep the chart readable

#### `FB-L07-EVIDENCE_LED` — Learner removes redundant marks and preserves key context

**Trigger:** Learner removes redundant marks and preserves key context.

**Message to learner:**

> The chart reads more clearly because each remaining area has a distinct job. Your notes make the simplification decision understandable.

**Next action:** Show final reference.

#### `FB-L07-REDUNDANT` — Learner keeps overlapping marks that explain same reaction

**Trigger:** Learner keeps overlapping marks that explain same reaction.

**Message to learner:**

> Ask whether both marks communicate different information. If not, consider merging them or keeping the clearer representation.

**Next action:** Prompt one merge.

#### `FB-L07-OVERPRUNE` — Learner removes context without checking purpose

**Trigger:** Learner removes context without checking purpose.

**Message to learner:**

> Before deleting a mark, ask whether it provides distinct context or explains an important prior reaction. Simplicity should not erase the chart’s story.

**Next action:** Compare with context-omission view.

#### `FB-L07-UNCERTAIN` — Learner leaves a mark pending due to context

**Trigger:** Learner leaves a mark pending due to context.

**Message to learner:**

> Mark it as uncertain and state what would make it useful. Leaving a choice provisional is better than inventing a reason.

**Next action:** Accept provisional note.


### Lesson 08 — Evaluate a zone without inventing a magic score

#### `FB-L08-EVIDENCE_LED` — Learner compares interpretability and context, not count alone

**Trigger:** Learner compares interpretability and context, not count alone.

**Message to learner:**

> You have evaluated how price behaved around the area, not just how often it was touched. Keep the judgement qualitative and tied to the shown evidence.

**Next action:** Continue to Uneven Lows lab.

#### `FB-L08-TOUCH_COUNT` — Learner ranks solely by number of visits

**Trigger:** Learner ranks solely by number of visits.

**Message to learner:**

> Touch count alone cannot determine quality. Compare the nature of the interactions, the wider structure, and whether the area remains interpretable.

**Next action:** Ask learner to compare behaviour.

#### `FB-L08-MAGIC_SCORE` — Learner asks for a universal numeric zone score

**Trigger:** Learner asks for a universal numeric zone score.

**Message to learner:**

> This lesson does not provide a universal score. Explain the qualitative evidence that helps you keep, downgrade or question the area.

**Next action:** No number should be required.

#### `FB-L08-UNCERTAIN` — Learner says neither area clearly preferable

**Trigger:** Learner says neither area clearly preferable.

**Message to learner:**

> That can be a defensible conclusion. Name what is mixed or missing, and avoid forcing a ranking the chart does not support.

**Next action:** Accept reasoned inconclusive answer.


### Lesson 09 — Read the approach to a zone

#### `FB-L09-EVIDENCE_LED` — Learner describes direction, overlap, nearby structure and context

**Trigger:** Learner describes direction, overlap, nearby structure and context.

**Message to learner:**

> You are describing how price reached the area without claiming to know what will happen there. That distinction is the point of this exercise.

**Next action:** Keep future candles hidden; then invite the unknowns response.

#### `FB-L09-PREDICTION` — Learner says directional approach guarantees break/rejection

**Trigger:** Learner says directional approach guarantees break/rejection.

**Message to learner:**

> The approach describes the route taken so far, not the result at the zone. Rephrase the observation, then give at least one alternative outcome.

**Next action:** Ask one observed fact + one unknown.

#### `FB-L09-PARTICIPANTS` — Learner claims institutional action from candles alone

**Trigger:** Learner claims institutional action from candles alone.

**Message to learner:**

> The chart alone does not establish who acted or why. Describe the visible movement—direction, overlap and swings—without assigning unseen motives.

**Next action:** Replace motive claim with observation.

#### `FB-L09-CASE_MISSING` — Authentic instructor micro-case is unavailable

**Trigger:** Authentic instructor micro-case is unavailable.

**Message to learner:**

> This controlled chart is a practice illustration, not the instructor’s personal example. The authentic micro-case will be inserted when the original material is supplied.

**Next action:** Do not show a fabricated substitute.


### Lesson 10 — Rejection versus acceptance

#### `FB-L10-EVIDENCE_LED` — Learner updates classification after follow-through

**Trigger:** Learner updates classification after follow-through.

**Message to learner:**

> Your interpretation became better supported because you considered the sequence, not just the first candle. Keep the conclusion conditional: later price can still change the picture.

**Next action:** Proceed to next staged reveal.

#### `FB-L10-SINGLE_CANDLE_CERTAINTY` — Learner calls one wick proof of rejection/acceptance

**Trigger:** Learner calls one wick proof of rejection/acceptance.

**Message to learner:**

> A wick or single close is one piece of evidence, not universal proof. Describe where the candle traded and closed, then say what the next candles would clarify.

**Next action:** Offer revise-after-next-candle action.

#### `FB-L10-FALSE_BINARY` — Learner forces rejection or acceptance in mixed sequence

**Trigger:** Learner forces rejection or acceptance in mixed sequence.

**Message to learner:**

> “Inconclusive so far” is a valid classification when the evidence conflicts. State what supports each interpretation and what remains unresolved.

**Next action:** Select inconclusive and explain.

#### `FB-L10-OBSERVATION_INTERPRETATION` — Learner confuses close location with conclusion

**Trigger:** Learner confuses close location with conclusion.

**Message to learner:**

> Separate the observable fact (“closed back inside/beyond”) from the interpretation (“consistent with rejection/possible acceptance”). The second is not automatically proved by the first.

**Next action:** Prompt two distinct text fields.


### Lesson 11 — How a zone’s significance changes

#### `FB-L11-EVIDENCE_LED` — Learner identifies what changed across timeline

**Trigger:** Learner identifies what changed across timeline.

**Message to learner:**

> You have tracked new evidence and explained how it affects the current read. Keep the earlier assessment visible so the change in judgement can be compared.

**Next action:** Continue to final stage.

#### `FB-L11-TOUCH_COUNT` — Learner says more touches always increase significance

**Trigger:** Learner says more touches always increase significance.

**Message to learner:**

> A visit is not automatically supporting evidence. Consider the quality and outcome of each interaction, including crossings or failure to move away.

**Next action:** Compare each timeline stage.

#### `FB-L11-NO_UPDATE` — Learner repeats initial assessment unchanged without explanation

**Trigger:** Learner repeats initial assessment unchanged without explanation.

**Message to learner:**

> An unchanged conclusion can be reasonable, but state why the new evidence does not change it—or identify what evidence would.

**Next action:** Require explicit unchanged rationale.

#### `FB-L11-OVERFINAL` — Learner treats latest stage as permanent truth

**Trigger:** Learner treats latest stage as permanent truth.

**Message to learner:**

> The latest stage updates the present reading; it does not make the zone permanently valid or tell you every future interaction.

**Next action:** Use current, provisional wording.


### Lesson 12 — Breakout or temporary penetration?

#### `FB-L12-EVIDENCE_LED` — Learner revises after seeing return/follow-through

**Trigger:** Learner revises after seeing return/follow-through.

**Message to learner:**

> You used later evidence to update the earlier read. Make clear what was knowable at the first crossing and what only became visible afterward.

**Next action:** Compare first-state and final-state response.

#### `FB-L12-HINDSIGHT` — Learner describes the first crossing as obviously failed/confirmed after reveal

**Trigger:** Learner describes the first crossing as obviously failed/confirmed after reveal.

**Message to learner:**

> That conclusion uses information unavailable at the first stage. Return to the initial state and write only what could be observed then.

**Next action:** Replay the first crossing state.

#### `FB-L12-CROSSING_EQUALS_BREAKOUT` — Learner treats any penetration as decisive breakout

**Trigger:** Learner treats any penetration as decisive breakout.

**Message to learner:**

> A crossing is an event to investigate. Check what follows: return inside, sustained action beyond, or mixed evidence.

**Next action:** Reveal sequence progressively.

#### `FB-L12-UNCERTAIN` — Learner says evidence remains insufficient

**Trigger:** Learner says evidence remains insufficient.

**Message to learner:**

> That is valid when the sequence does not settle clearly. Explain what further observable development would help update your read.

**Next action:** Accept “not enough evidence yet.”


### Lesson 13 — Retests and role reversal

#### `FB-L13-EVIDENCE_LED` — Learner compares hold and failure cases conditionally

**Trigger:** Learner compares hold and failure cases conditionally.

**Message to learner:**

> You have treated role reversal as a possibility and named evidence that could support or weaken it. Keep the alternative outcome open.

**Next action:** Proceed to comparison.

#### `FB-L13-MANDATORY_RETEST` — Learner says every breakout must retest

**Trigger:** Learner says every breakout must retest.

**Message to learner:**

> A retest is one possible path, not a requirement. Price may continue without returning, or a return may fail.

**Next action:** Ask for no-retest alternative.

#### `FB-L13-GUARANTEED_ROLE_REVERSAL` — Learner claims former resistance must become support

**Trigger:** Learner claims former resistance must become support.

**Message to learner:**

> The former area may play a different role, but that is not guaranteed. Use the actual return behaviour to assess the possibility.

**Next action:** Compare holding and failed return.

#### `FB-L13-NO_CONDITIONS` — Learner describes retest outcome without evidence conditions

**Trigger:** Learner describes retest outcome without evidence conditions.

**Message to learner:**

> What observable behaviour would support the hold? What would weaken it? A useful interpretation explains what could change your mind.

**Next action:** Require one supporting and one weakening condition.


### Lesson 14 — Failed breakouts and alternate outcomes

#### `FB-L14-EVIDENCE_LED` — Learner preserves chronological stages and alternative outcomes

**Trigger:** Learner preserves chronological stages and alternative outcomes.

**Message to learner:**

> You have separated the pre-break view from later information and kept an alternative path in mind. That is essential for avoiding hindsight.

**Next action:** Continue to Wider Neckline lab.

#### `FB-L14-HINDSIGHT` — Learner uses later return-through to claim initial failure was obvious

**Trigger:** Learner uses later return-through to claim initial failure was obvious.

**Message to learner:**

> At the pre-break stage, that later evidence was not available. Describe the initial condition on its own, then update after each reveal.

**Next action:** Replay staged chart sequence.

#### `FB-L14-ONE_PATH` — Learner assumes all breaks fail or all follow through

**Trigger:** Learner assumes all breaks fail or all follow through.

**Message to learner:**

> The lesson compares alternate paths precisely because the first move beyond an area does not settle the final outcome. State what each path would need to show.

**Next action:** Compare Chart C and D.

#### `FB-L14-LAB_PREMATURE` — Learner requests reference before submission

**Trigger:** Learner requests reference before submission.

**Message to learner:**

> Complete your own mark and record your boundary reasoning first. The reference unlocks after submission so you can compare decisions rather than copy the drawing.

**Next action:** Hold reference until submission.


### Lesson 15 — From zones to conditional scenarios

#### `FB-L15-EVIDENCE_LED` — Learner gives conditional scenarios and invalidation

**Trigger:** Learner gives conditional scenarios and invalidation.

**Message to learner:**

> Your scenarios are tied to observable developments, alternatives and a reconsideration point. That is more useful than a confident forecast.

**Next action:** Review space and opposing area.

#### `FB-L15-PREDICTION_ONLY` — Learner writes a single certain direction

**Trigger:** Learner writes a single certain direction.

**Message to learner:**

> Turn the forecast into an if/then statement. What specific evidence must appear, and what alternative would change the interpretation?

**Next action:** Prompt conditional rewrite.

#### `FB-L15-NO_INVALIDATION` — Learner gives scenario without what would weaken it

**Trigger:** Learner gives scenario without what would weaken it.

**Message to learner:**

> Name an observable development that would make the original interpretation less plausible. Invalidation is a condition for reconsidering the idea, not a price you have to invent.

**Next action:** Require invalidation field.

#### `FB-L15-SPACE_IGNORED` — Learner names no next opposing area or space

**Trigger:** Learner names no next opposing area or space.

**Message to learner:**

> Look for the next meaningful opposing area if it can be identified. If the excerpt does not provide enough context, say so and explain the limitation.

**Next action:** Accept “cannot identify from this excerpt.”


### Lesson 16 — Case study: a trade based on a reaction

#### `FB-L16-PROCESS_LED` — Learner separates chronology, thesis, risk and outcome

**Trigger:** Learner separates chronology, thesis, risk and outcome.

**Message to learner:**

> Keep each decision anchored to the record available at that stage. Then evaluate process separately from whether the trade made or lost money.

**Next action:** Reveal next stage only after response.

#### `FB-L16-HINDSIGHT` — Learner evaluates entry using outcome already shown

**Trigger:** Learner evaluates entry using outcome already shown.

**Message to learner:**

> Return to the pre-entry view. What evidence was available then? Later success or failure cannot be used as if it had been known at entry.

**Next action:** Delay/rewind outcome reveal.

#### `FB-L16-PROCESS_EQUALS_PROFIT` — Learner calls profitable outcome proof of a good process

**Trigger:** Learner calls profitable outcome proof of a good process.

**Message to learner:**

> A profitable result does not automatically validate the decision process. Check whether the stated thesis, risk and invalidation were coherent and followed.

**Next action:** Require process evidence.

#### `FB-L16-CASE_MISSING` — Authentic trade record is not supplied

**Trigger:** Authentic trade record is not supplied.

**Message to learner:**

> Do not fill this slot with a fictional trade. Keep the case shell ready and request the genuine chart and decision chronology before recording this lesson.

**Next action:** Pause personal-case recording only.


### Lesson 17 — When the thesis fails, or you stay out

#### `FB-L17-PROCESS_LED` — Learner distinguishes thesis failure from process failure

**Trigger:** Learner distinguishes thesis failure from process failure.

**Message to learner:**

> A thesis can fail even when the decision process was followed. Identify whether the evidence invalidated the idea, whether the process departed from its rules, or both.

**Next action:** Continue the chronological review.

#### `FB-L17-OUTCOME_SHAME` — Learner treats a loss alone as proof of poor process

**Trigger:** Learner treats a loss alone as proof of poor process.

**Message to learner:**

> The outcome by itself does not establish process quality. Review the original evidence, stated invalidation and actions taken as the evidence changed.

**Next action:** Separate outcome from decision quality.

#### `FB-L17-MISSED_NO_TRADE` — Learner assumes stand-aside means fear or missed opportunity

**Trigger:** Learner assumes stand-aside means fear or missed opportunity.

**Message to learner:**

> A no-trade decision can be defensible when evidence is unclear or the plan is incomplete. Explain what was missing and what would have changed the decision.

**Next action:** Use stand-aside alternative if authentic.

#### `FB-L17-CASE_MISSING` — Authentic failed thesis/loss/no-trade record is unavailable

**Trigger:** Authentic failed thesis/loss/no-trade record is unavailable.

**Message to learner:**

> This lesson needs a real example. Do not invent a losing trade or retrofit an explanation to an outcome; keep the shell and gather the original record.

**Next action:** Leave case as unpopulated dependency.


### Lesson 18 — Final chart review and knowledge check

#### `FB-L18-EVIDENCE_LED` — Learner connects structure, zones, interpretation and conditional scenarios

**Trigger:** Learner connects structure, zones, interpretation and conditional scenarios.

**Message to learner:**

> Your response explains both the evidence and the limits of what can be concluded. A reference drawing is a comparison point, not the only acceptable layout.

**Next action:** Record submission before revealing reference.

#### `FB-L18-DRAWING_MISMATCH` — Learner zones differ from the reference but are reasoned

**Trigger:** Learner zones differ from the reference but are reasoned.

**Message to learner:**

> Do not aim for a pixel match. Explain which reactions your boundaries include, what you omitted, and the trade-off created by your choice.

**Next action:** Score rationale and coverage.

#### `FB-L18-PREDICTION_ONLY` — Learner supplies a confident single direction without conditions

**Trigger:** Learner supplies a confident single direction without conditions.

**Message to learner:**

> Add the observable development your idea depends on, one alternative, and a condition that would make you reconsider.

**Next action:** Use conditional-scenario field.

#### `FB-L18-STAND_ASIDE` — Learner stands aside with a reason tied to ambiguity/space

**Trigger:** Learner stands aside with a reason tied to ambiguity/space.

**Message to learner:**

> A justified stand-aside can demonstrate disciplined analysis. Make the uncertainty or constraint explicit rather than leaving the response blank.

**Next action:** Score reasoned response per rubric.


## Implementation and review notes

- Use these messages as contingent feedback, not as one generic “correct/incorrect” label.
- Where a response is free text, a human or a specifically implemented and tested evaluation component must interpret it. The current files do not implement that evaluator.
- For binary/multiple-choice checks, map choices to the relevant trigger but retain an “other / not sure” path where the lesson supports uncertainty.
- The feedback bank does not contain the hidden final-assessment reference analysis or scoring key; those remain in the internal Lesson 18 script and reference materials.
- Second pass: verify every trigger against the lesson script, ensure no message leaks a future event, and test acceptable alternatives (SP-23, SP-24).
- Authentic case feedback for Lessons 9, 16 and 17 must be reconciled after the user provides records. Generic process feedback is ready; case-specific assertions are not.