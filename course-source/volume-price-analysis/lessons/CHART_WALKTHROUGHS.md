# Chart Walkthrough and ChartLab Design Briefs — 30 Lessons
## Internal production reference for Read Volume. Find Trade Setups.

These are **design briefs for building student-facing chart experiences**, not narration scripts and not text for students to read. The module files are the source of the teaching explanation. Use this document to decide what each visual should show, what the learner should do with it, and what feedback should explain.

## Shared design rules

- Keep the chart central and the lesson text beside it where the layout allows. Use the site's light, editorial style and readable annotations; do not make chart information depend on colour alone.
- Use synthetic OHLCV data unless real data has appropriate rights. Clearly label invented examples as synthetic in the delivered experience.
- Keep instrument, timeframe, profile window, feed and volume baseline visible when they affect the exercise.
- Present one main distinction per screen. Do not add decorative indicators, extra lines or unlabelled jargon.
- Where later bars affect the interpretation, freeze the initial chart until the learner records an observation and an initial reading. Then reveal a contrasting outcome and explain what changed.
- Give the learner feedback on reasoning: visible evidence, location, alternative interpretation and the next condition. Do not score a directional prediction as correct merely because it matched the outcome.
- For each lesson, create a chart visual, a learner prompt, feedback/model answer and a contrasting case where listed. Verify on desktop and small screens, at 200% zoom and with keyboard navigation before approval.
- The three practice stages should be visible to learners: **Notice**, **Compare**, **Apply**. These are interaction levels, not headings that replace real instruction.

---

# Module 1 — Read the Market Behind the Candles

## 1.1 — What Candlesticks Don't Tell You: Reading the Volume Behind Price
**Visual:** Pair two similar-sized green candles in separate contexts, with the same price-scale increment. Show prior structure, candle range/close and relative volume (for example, 1.18× versus 1.87×).  
**Learner action:** Notice the facts first; compare how location and activity differ; then read a new breakout attempt frozen before its later outcome.  
**Reveal and feedback:** Show one continuation and one failure path from the same initial event. Explain why the initial observation was the same but follow-through changed the interpretation.

## 1.2 — Is This Move Significant? Spotting Unusual Volume
**Visual:** Twenty comparable bars and a candidate bar. Show the baseline calculation and relative-volume multiple. Add a second spike at a different time of day.  
**Learner action:** Identify the baseline, compute the multiple, and name one reason the comparison could be misleading.  
**Reveal and feedback:** Show the same spike in surrounding price context. Reinforce that unusual volume tells the learner where to investigate, not whether to buy or sell.

## 1.3 — Read the Story Inside a Candle: Wicks, Range and Closing Price
**Visual:** Label open, high, low, close, body, upper/lower wick and range on one candle. Add two comparison candles with different close locations.  
**Learner action:** Annotate the parts, calculate close position where appropriate, and separate objective description from inferred meaning.  
**Reveal and feedback:** Place the candles at a range boundary and show different later outcomes. Explain why a wick records an excursion but does not prove the identity or intent of a participant.

## 1.4 — When Price Moves on Low Volume: Opportunity or Warning Sign?
**Visual:** Show a trend impulse followed by a low-activity pullback near a prior boundary. Prepare a second case with a similar start that breaks the boundary and continues against the trend.  
**Learner action:** Describe the activity and price progress; decide what evidence is still missing.  
**Reveal and feedback:** Compare the two paths. The learner should recognise that low activity can be consistent with a pause but does not guarantee continuation.

## 1.5 — Which Volume Can You Trust? Understanding Data Across Different Markets
**Visual:** Three labelled data-source examples: exchange-traded volume, retail FX tick activity and a venue-specific crypto series. Include source, instrument, timeframe and what the field measures.  
**Learner action:** Complete a comparison of what each source records, what it does not represent and which baseline is appropriate.  
**Reveal and feedback:** Compare the model responses. Emphasise that a source limitation should qualify the claim, not be hidden in a footnote.

---

# Module 2 — Spot Buying and Selling Pressure

## 2.1 — Who's Pushing Price? Reading Buying and Selling Pressure
**Visual:** Compare an upward sequence that retains gains with a high-activity, narrow-range sequence. Add prior swing structure.  
**Learner action:** Classify the progress as upward, downward, limited or unresolved and point to the evidence.  
**Reveal and feedback:** Add subsequent bars. Reinforce that pressure is shorthand for achieved price progress, not a claim about the identities of buyers or sellers.

## 2.2 — When Volume Supports a Move: Recognising Evidence of Strength
**Visual:** Pair a breakout with elevated activity and follow-through against a similarly active bar that returns inside the range.  
**Learner action:** Compare price result, relative activity, location and later progress.  
**Reveal and feedback:** The model explanation should give greater weight to retained progress than to the initial volume ratio alone.

## 2.3 — Heavy Volume, Little Progress: What Is Happening Behind the Move?
**Visual:** Freeze an unusually active, narrow-range candle near a marked boundary. Build two later outcomes: failure from the level and later continuation through it.  
**Learner action:** Record three observable facts, two possible explanations and the next discriminator.  
**Reveal and feedback:** Explain that absorption is one possible interpretation, not something the candle conclusively proves.

## 2.4 — Is the Move Losing Steam? Reading Signs of Weakening Pressure
**Visual:** Compare successive advances with shrinking progress against a second case that pauses and then resumes. Mark closes, range and relevant swing levels.  
**Learner action:** Identify the first sign of slowing, then separately identify whether a meaningful structural change has occurred.  
**Reveal and feedback:** Explain the difference between weakening progress and a confirmed change in direction.

## 2.5 — When Price and Volume Disagree: Finding Clues Others May Overlook
**Visual:** Include a marginal new high on lower activity and an elevated-volume bar with limited price progress. Give each at least two plausible endings.  
**Learner action:** State the mismatch, a primary reading, an alternative and an observable next condition.  
**Reveal and feedback:** Reward conditional reasoning. The learner should not treat disagreement as an automatic reversal signal.

---

# Module 3 — Find Trade Setups at the Levels That Matter

## 3.1 — Stop Chasing Price: Finding Potential Setups in an Established Trend
**Visual:** Show an extended impulse with a late entry location, then mark a prior breakout zone and meaningful pullback area.  
**Learner action:** Separate setup area, trigger and invalidation. Compare one pullback that holds with one that breaks structure.  
**Reveal and feedback:** Evaluate the clarity of the conditions, not whether the learner guessed the profitable path.

## 3.2 — Is the Pullback Running Out of Steam? Reading Moves Against the Trend
**Visual:** Two similar trend impulses followed by pullbacks with different depth, range, relative activity and structural outcome.  
**Learner action:** Classify each pullback as supportive, challenging or unresolved using the evidence available before the later bars.  
**Reveal and feedback:** Show both endings and review whether the first interpretation was defensible without hindsight.

## 3.3 — Trading Near Support and Resistance: What to Look for Before Entry
**Visual:** One clearly justified upper zone and lower zone. Build three outcomes at a zone: turn away, sustained trade beyond, and unresolved overlap.  
**Learner action:** For each outcome, define what it would mean for the current scenario and which condition would weaken the idea.  
**Reveal and feedback:** Reinforce that a level is an area of interest, not an instruction to enter.

## 3.4 — Finding Opportunities at the Edges of a Trading Range
**Visual:** Show a range with boundaries derived from prior swings. Add an upper-edge failed break, a sustained breakout and a lower-edge rotation.  
**Learner action:** Identify whether the market is at an edge or in the middle, then state what evidence is needed for rotation versus breakout.  
**Reveal and feedback:** Treat wait/no-trade as a valid response when price overlaps without clear progress.

## 3.5 — Before You Enter: Separating Promising Setups From Weak Ones
**Visual:** Three candidate situations: a defined pullback near a meaningful level, a candle pattern in the range middle, and an extended breakout close to the next opposing zone.  
**Learner action:** Use the same readiness checklist: context, location, evidence, trigger, invalidation and practical risk. Mark each as ready, wait or reject with a short reason.  
**Reveal and feedback:** Show a model review that explains why an attractive candle is not enough when the trigger or risk structure is missing.

---

# Module 4 — Spot False Breakouts Before You Chase Them

## 4.1 — Is the Breakout Real? What Volume Can Tell You
**Visual:** Mark a prior range boundary, freeze after the first close beyond it, and prepare one path that holds outside and one that returns inside.  
**Learner action:** Describe the first event, note relative activity and write the conditions that would support or weaken continuation.  
**Reveal and feedback:** Compare the two paths, making clear that the initial candle did not settle the question.

## 4.2 — Breakout or Trap? Reading the Signs of a Failed Move
**Visual:** Stage the sequence: cross the boundary, return inside, attempt reclaim, then either fail and break nearby structure or reclaim successfully.  
**Learner action:** At every stage, record what new evidence appeared and how it changes the thesis. Preserve the first note.  
**Reveal and feedback:** Make clear that “trap” does not prove deliberate manipulation; assess a failed move relative to the plan that existed before it.

## 4.3 — When Volume Explodes at Market Extremes: Understanding Climax Activity
**Visual:** Show an extended trend, an unusually active bar and two contrasting outcomes: structural reversal and resumed continuation.  
**Learner action:** Describe relative activity, price result and location before the outcome is revealed. Name the evidence not yet available.  
**Reveal and feedback:** Explain that a climax label describes exceptional activity; the later price response helps judge its significance.

## 4.4 — Springs and Upthrusts: Recognising Failed Moves at Range Boundaries
**Visual:** Mirror a range-low excursion that returns inside with an upper excursion that returns inside. Provide follow-through and failure variants for each.  
**Learner action:** Mark the original boundary, label the event only after describing it, and state what would weaken the interpretation.  
**Reveal and feedback:** The term describes the event; it does not guarantee a reversal. Include the case where price remains outside the boundary.

## 4.5 — Before Calling a Reversal: What to Look for After the Breakout
**Visual:** Stage an initial extreme, a return inside, a possible failed reclaim and a structural break. Include an alternate outcome where the original trend resumes.  
**Learner action:** Distinguish warning, failed breakout and stronger evidence of changed structure.  
**Reveal and feedback:** Explain why a rejected excursion is not the same claim as a confirmed reversal.

---

# Module 5 — Find the Price Levels Worth Watching

## 5.1 — Where Has the Market Traded Most? Introducing Volume Profile
**Visual:** Use the same synthetic data to show time-based volume bars and a horizontal price-based profile. Keep the price scale aligned; then change the profile window to show the dependency on the selected period.  
**Learner action:** Identify what each view answers, and describe broad and thin areas without forecasting price.  
**Reveal and feedback:** Explain “when activity occurred” versus “how activity was distributed by price.”

## 5.2 — Finding the Market's Reference Point: Point of Control and Value Area
**Visual:** Mark the profile's POC and platform-defined value-area high/low. Show a second profile period with different references and label the method/settings.  
**Learner action:** State what the three references measure and what the current price location does—or does not—establish.  
**Reveal and feedback:** Emphasise that values depend on the selected window and platform rules; they are not guaranteed support or resistance.

## 5.3 — Where Price May Stall—or Move Quickly: High- and Low-Volume Nodes
**Visual:** A profile has a broad concentration and a thin area. Show price entering the thin area and prepare both a quick traversal and a stall.  
**Learner action:** Describe the profile area and create a conditional expectation, then update it when the current response differs.  
**Reveal and feedback:** Reinforce that historical activity does not expose current resting orders or guarantee a fast move.

## 5.4 — When the Market's Focus Shifts: Reading Changes in Value
**Visual:** Three comparable session profiles side by side using the same row size and settings. Show higher migration, lower migration and substantial overlap.  
**Learner action:** Report profile movement separately from price structure and follow-through.  
**Reveal and feedback:** Show how price returning to previous value weakens a directional interpretation based only on the latest POC.

## 5.5 — Putting It Together: Reading Volume Profile Alongside Price Action
**Visual:** A clean price chart with a stated profile period, a POC, value-area boundaries and a single broad/thin area. Show price approaching the same area with different outcomes.  
**Learner action:** Write two conditional scenarios using price structure, profile location and current volume evidence.  
**Reveal and feedback:** Explain that profile sets context while current price behaviour tests the scenario; avoid adding unrelated indicators.

---

# Module 6 — Put It All Together: Build a Complete Trading Plan

## 6.1 — Start With the Bigger Picture: What Is the Market Doing?
**Visual:** Begin with a cluttered chart, remove unjustified lines and unrelated indicators, and retain only swings, a few explained zones, the volume field and a relevant profile reference.  
**Learner action:** Complete a context note with market state, structure, recent event, data limitation and unresolved question.  
**Reveal and feedback:** Compare against a model note that justifies each retained level instead of adding more lines.

## 6.2 — Read the Evidence: What Are Price and Volume Telling You?
**Visual:** Freeze on an ambiguous high-volume event near a boundary. Provide fields for event, close/range, relative volume/baseline, location, primary reading and alternative.  
**Learner action:** Complete the initial evidence sheet before revealing two additional bars and a retest.  
**Reveal and feedback:** Require the student to preserve the observation and update only the interpretation as new evidence appears.

## 6.3 — Build Your Trade Scenario: What Needs to Happen Next?
**Visual:** Show two scenario cards beside a frozen breakout attempt: continuation beyond the level and return into the range. Each card needs trigger, invalidation and no-trade condition.  
**Learner action:** Complete both cards before the outcomes are revealed.  
**Reveal and feedback:** Compare the scenarios without marking the eventual winner as automatically the better original analysis.

## 6.4 — Plan the Trade Before You Take It
**Visual:** A fictional pre-trade ticket with trigger, structural invalidation, stop logic, position-size calculation inputs, costs/slippage, objective and management rules. Include an example where the target is too close or execution costs alter the plan.  
**Learner action:** Check the construction sequence: thesis first, risk rules next, position size after risk per unit is known.  
**Reveal and feedback:** Do not prescribe a universal risk percentage. Explain why the setup must not override a predetermined risk policy.

## 6.5 — The Complete Walkthrough: From Chart Analysis to Trade Plan
**Visual:** Use a staged capstone chart. Ask for context before the event, evidence notes after the first event, two scenarios before the retest, and a complete trade ticket before revealing an outcome. Prepare two endings: a valid trigger that later loses and a disciplined no-trade that misses a later favourable move.  
**Learner action:** Complete each stage in order and retain the original notes.  
**Reveal and feedback:** Review reasoning, rule adherence and how evidence changed—not just profit/loss or whether the final move matched the learner's guess.

---

## Shared QA checklist

- [ ] Each chart has one clear teaching purpose.
- [ ] Data is synthetic or appropriately licensed and labelled.
- [ ] Instrument, timeframe, feed, period and baseline are stated where relevant.
- [ ] Text, axes, candles, price levels and volume labels remain legible on small screens and at 200% zoom.
- [ ] Feedback explains the reasoning and its limitations.
- [ ] A plausible alternative or counterexample is included where it teaches an important distinction.
- [ ] Learners are not asked to infer hidden participant intent from a chart.
- [ ] The exercise works without an instructor narrating the instructions aloud.
- [ ] Keyboard access, focus order, screen-reader description and colour-independent cues are reviewed.
