# Understand Bollinger Bands — Course Architecture

**Status:** Working curriculum plan; research and source verification continue  
**Working branch:** my-new-branch  
**Audience:** Intermediate market participants  
**Design reference:** [Reusable Course Creation Method](../COURSE_CREATION_METHOD_VOLUME_PRICE_ANALYSIS.md)

## Course promise

Learn what Bollinger Bands show about price and volatility, how to read them in the market context, how to plan and assess buy and sell scenarios, and how to recognise when the evidence is not good enough to trade.

This course is not about memorising band-touch signals. It teaches students to explain what they see, consider plausible alternatives, identify what would change their view, and make a decision that fits the evidence available.

## Audience, assumptions, and scope

Students already recognise candlesticks, trends, support and resistance, trading ranges, entries, stops, and basic risk. The course should not spend time teaching these market basics from scratch.

Explain Bollinger-specific language as it appears. Avoid sentences that sound academic or require a glossary to follow. Terms such as standard deviation, relative price, volatility contraction, %B, and BandWidth must be explained in intuitive language and then used consistently.

Included: band construction and settings, relative price position, %B, BandWidth, trend and range context, band walks, squeezes, M-tops and W-bottoms, price/indicator confirmation, buy and sell frameworks, failure modes, risk, testing, and review.

Excluded: a full technical-analysis survey, coding, complex statistical derivations, automated strategy construction, options Greeks, extensive macro analysis, a signal service, or claims that an indicator can predict price with certainty.

## Learning outcomes

By the end, students should be able to:

1. Explain what the middle, upper, and lower bands show in plain language.
2. Explain how the default settings work and why defaults should not be treated as universally optimal.
3. Use %B to describe where price sits relative to the bands and BandWidth to compare how narrow or wide the bands are.
4. Distinguish a band tag, a band walk, a squeeze, and a confirmed price move.
5. Read M-top and W-bottom structures without assuming every similar-looking shape is a valid reversal.
6. Build and critique symmetrical buy and sell plans with context, trigger, confirmation, invalidation, stop logic, exits, and position risk.
7. Recognise false breaks, failed mean reversion, late entries, conflicting evidence, and unsuitable conditions.
8. Review trades and test a consistent idea without overfitting settings to a few past examples.

## Course map

| Module | Job in the learning journey | Lessons |
|---|---|---:|
| 1. What Bollinger Bands Actually Tell You | Build the correct mental model: relative price and changing volatility, not prediction. | 4 |
| 2. Read the Bands and Their Measurements | Understand construction, settings, %B, and BandWidth. | 4 |
| 3. Read the Market Before Reading the Signal | Learn trend/range context, band walks, compression, expansion, and directional evidence. | 4 |
| 4. Read Bollinger's Signature Patterns | Understand M-tops and W-bottoms and judge when a pattern is incomplete or ambiguous. | 4 |
| 5. Build Buy and Sell Plans | Turn patterns and market context into practical, symmetrical, testable plans. | 5 |
| 6. Recognise Failed Setups and Know When to Wait | Study the traps that make otherwise attractive setups fail. | 4 |
| 7. Manage Risk and Review the Process | Size, manage, test, journal, and apply the full reasoning process. | 4 |

**Planned lesson count:** 29  
**Expected total learning time:** approximately 7–8 hours, based on lesson estimates below. This is a planning estimate, not a measured completion time.

## Teaching and language standards

Write for an independent learner, not as a presenter script. A lesson should start with a practical question, explain the idea plainly, put the visual evidence in front of the student, walk through the reasoning, compare a different or ambiguous case, give the learner a short task, explain the model reasoning, address a common mistake, and end with a useful takeaway.

A good explanation distinguishes:
- **What can be seen:** the observation.
- **What it might mean:** one interpretation.
- **What else could explain it:** a plausible alternative.
- **What would help decide:** the next evidence to watch.
- **What is justified now:** the decision, including waiting or doing nothing.

The expected reader is an intermediate trader, but language must not be a barrier. Prefer “the bands narrow when recent price movement becomes quieter” before introducing “volatility contraction.” Prefer “price has moved outside the band” before “an external band close.” Use technical terms only when they add precision, explain them when first needed, and avoid stacking jargon.

Do not repeat the same full explanation in later modules. Introduce the concept in its home lesson; later lessons should apply it to a new chart or decision.

## Lesson architecture

Timings include reading, inspecting the supplied figure, completing the task, and reviewing feedback. All tasks use the named static figures; there is no ChartLab or external chart-finding activity.

### Module 1 — What Bollinger Bands Actually Tell You

*Module purpose:* Build an intuitive mental model before students learn formulas or setups.

#### 1.1 — What Are the Bands Showing You?
**Time:** 15 minutes — read 8, inspect 2, task 3, review 2.  
**Outcome:** Explain what the middle line and outer bands show as price moves.  
**Question:** Why do the bands move closer to price in some periods and spread out in others?  
**Teach:** The middle line tracks an average price. The outer bands move with recent price variation, so the frame is adaptive rather than fixed. A band gives context for where price is relative to recent movement; it is not a target or wall that must hold.  
**Figure/task:** Figure 1.1. Ask the learner to identify the middle line, upper band, lower band, and one period where the band width changes.  
**Model reasoning:** The bands are built around a moving average and expand or contract as recent price variation changes. The image shows changing context, not a guaranteed future range.  
**Common mistake:** Treating the outer bands as permanent support and resistance.  
**Transfer:** On the second chart panel, explain in one or two sentences what changed in the bands.  
**Source:** John Bollinger, official rules 1, 9, 12, 14; *Bollinger on Bollinger Bands*.

#### 1.2 — When Price Reaches a Band, What Does It Mean?
**Time:** 14 minutes — read 7, inspect 2, task 3, review 2.  
**Outcome:** Describe a band touch without automatically calling it a buy or sell signal.  
**Question:** If price touches the upper band, should you sell?  
**Teach:** A touch says price is near the high end of its recent range relative to the bands. In a range that may be worth investigating for a possible turn; in a strong uptrend it may show strength. Context changes the interpretation.  
**Figure/task:** Figure 1.2. Compare an upper-band touch during a sideways market with one during a rising trend; choose what each observation supports and what it does not prove.  
**Model reasoning:** Neither touch alone gives an entry. The first is a possible range-edge question; the second may be part of a continuing trend. More context is needed.  
**Common mistake:** “Upper band means sell; lower band means buy.”  
**Transfer:** Explain why the lower-band touch in the downtrend panel is not, by itself, a buy.  
**Source:** Bollinger's official rule 6.

#### 1.3 — Why the Bands Keep Changing
**Time:** 15 minutes — read 8, inspect 2, task 3, review 2.  
**Outcome:** Explain why band width changes as recent price movement changes.  
**Question:** Why can the same instrument have tight bands one week and wide bands the next?  
**Teach:** The bands respond to how much price has varied over the calculation period. Quieter movement tends to narrow them; larger movement tends to widen them. The bands describe recent conditions and update as new prices arrive and older ones leave the calculation window.  
**Figure/task:** Figure 1.3. Match the quiet, expanding, and wide-band chart sections to their visible price behaviour.  
**Model reasoning:** Narrower bands correspond to less recent variation; wider bands correspond to greater recent variation. Neither state provides direction by itself.  
**Common mistake:** Assuming wide bands must soon narrow or narrow bands must break upward.  
**Transfer:** Point to the section that best shows volatility increasing and state the evidence.  
**Source:** Bollinger official rules 9, 18, 19; StockCharts technical reference.

#### 1.4 — What the Bands Cannot Tell You
**Time:** 13 minutes — read 6, inspect 2, task 3, review 2.  
**Outcome:** Separate what the bands measure from what a trader must still determine.  
**Question:** Can the bands tell you the next move or guarantee that price will stay inside them?  
**Teach:** Bands do not give continuous buy/sell advice, guarantee containment, or predict the direction of a move. Price can stay outside or travel along a band. A standard-deviation calculation does not mean price follows a normal distribution.  
**Figure/task:** Figure 1.4. For each panel, mark one claim supported by the picture and one claim that goes too far.  
**Model reasoning:** Band width and price location are observable; the next direction and trade outcome are not known from the bands alone.  
**Common mistake:** Treating a band as a statistical fence that price should quickly return inside.  
**Transfer:** Rewrite “price touched the upper band, so it must reverse” as a cautious observation plus an open question.  
**Source:** Bollinger official rules 7, 8, 14, 22.

### Module 2 — Read the Bands and Their Measurements

*Module purpose:* Explain the few measurements students need without turning the lesson into a mathematics course.

#### 2.1 — How the Bands Are Built
**Time:** 16 minutes — read 8, inspect 3, task 3, review 2.  
**Outcome:** Explain the 20-period average and the role of standard deviation in the outer bands.  
**Question:** What changes when the recent price values are more spread out around their average?  
**Teach:** The common setup uses a 20-period simple moving average as the middle band and places the outer bands two standard deviations above and below it. Explain standard deviation intuitively as a measure of how spread out recent prices are around their average. No formula derivation is required.  
**Figure/task:** Figure 2.1. Match each labelled part of the diagram to its purpose and explain why the outer bands are not fixed distances from price.  
**Model reasoning:** The average provides the centre; standard deviation sets the distance to the bands using recent variation. Greater variation usually creates wider bands.  
**Common mistake:** Thinking the bands are a fixed percentage envelope around price.  
**Transfer:** Describe what would happen to band width if recent prices began moving more sharply.  
**Source:** Bollinger's official rules 9, 12, 14; McGraw Hill book listing.

#### 2.2 — Why 20 and 2 Are Defaults, Not Laws
**Time:** 14 minutes — read 7, inspect 2, task 3, review 2.  
**Outcome:** Explain why settings should be chosen deliberately and kept consistent while evaluating an idea.  
**Question:** Is a chart better because its settings look cleaner on past price action?  
**Teach:** The common settings are a starting point. Changing the average period also changes the standard-deviation window; Bollinger suggests small, coordinated adjustments, giving 50 periods with 2.1 deviations and 10 periods with 1.9 as examples. Do not present these as settings that work best in every market.  
**Figure/task:** Figure 2.2. Compare the same price series under three labelled settings; describe which reacts faster and which smooths more, without selecting a “winner” from hindsight.  
**Model reasoning:** Shorter periods respond more quickly and can be less smooth; longer periods respond more slowly. A visually pleasing fit is not evidence of better future performance.  
**Common mistake:** Repeatedly changing settings until past signals look perfect.  
**Transfer:** State one reason to test a chosen setting across different conditions before adopting it.  
**Source:** Bollinger official rules 9, 11, 12.

#### 2.3 — Use %B to Describe Price Position
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Read %B values as a simple description of price position within or beyond the bands.  
**Question:** How can you compare price position without describing the chart only as “near the top” or “near the bottom”?  
**Teach:** %B puts the price's position into a scale: 0 is the lower band, 0.5 is the middle of the band range, and 1 is the upper band. Readings below 0 or above 1 show price outside the bands. %B describes position; it is not automatically an overbought/oversold signal.  
**Figure/task:** Figure 2.3. Match example %B readings to locations on the chart and flag which reading is outside the bands.  
**Model reasoning:** %B makes location easier to compare. The same value can mean different things in a trend and a range, so context is still needed.  
**Common mistake:** Treating %B above 1 as an automatic sell or below 0 as an automatic buy.  
**Transfer:** Explain how the same %B value could fit a trend continuation in one chart and a different setup question in another.  
**Source:** Bollinger official rules 15–17; StockCharts %B reference.

#### 2.4 — Use BandWidth to See When the Bands Are Narrow or Wide
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Use BandWidth to compare changes in band width and recognise periods of unusually quiet movement.  
**Question:** How do you know whether today's bands are narrow relative to the instrument's recent behaviour?  
**Teach:** BandWidth measures the gap between upper and lower bands, usually scaled by the middle band. Low BandWidth means the bands are narrow relative to price; rising BandWidth means they are widening. Compare it with the instrument's own history rather than assuming one universal value means “squeeze.”  
**Figure/task:** Figure 2.4. Match the BandWidth line to the chart sections and identify the narrowest period in the shown window.  
**Model reasoning:** BandWidth helps compare volatility conditions. It does not say which way the next move will go.  
**Common mistake:** Applying one absolute BandWidth threshold to every instrument.  
**Transfer:** Describe what new evidence you would wait for after spotting a narrow BandWidth reading.  
**Source:** Bollinger official rule 18 and his official squeeze discussion; StockCharts BandWidth reference.

### Module 3 — Read the Market Before Reading the Signal

*Module purpose:* Teach students to ask whether they are looking at a trend or a range before deciding how to read a band interaction.

#### 3.1 — First Decide: Trend or Range?
**Time:** 17 minutes — read 8, inspect 3, task 4, review 2.  
**Outcome:** Identify visible evidence that a market is trending, ranging, or not clear enough to classify.  
**Question:** Why can the same lower-band touch be useful in one chart and dangerous in another?  
**Teach:** In a range, price rotates between boundaries; in a trend, price tends to make progress in one direction. Use swing structure and the middle band as context, not as a standalone crossover system. Some charts are mixed or transitioning; do not force a label.  
**Figure/task:** Figure 3.1. Classify three chart panels as trend, range, or unclear and point to the evidence supporting each choice.  
**Model reasoning:** Directional progress, repeated turning points, and whether boundaries hold can support a provisional reading. An unclear label is acceptable when structure is mixed.  
**Common mistake:** Calling every sideways pause a trading range.  
**Transfer:** Choose which panel is least suitable for a range-fade idea and explain why.  
**Source:** Bollinger official rules 7, 10, 22; course framework for context classification.

#### 3.2 — When Price Walks Along a Band
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Recognise a band walk and explain why it can warn against fading a strong trend.  
**Question:** Why might selling every upper-band touch in an uptrend lead to repeated losses?  
**Teach:** In a strong trend, price can keep moving along the upper band or the lower band for several bars. The middle band and swing structure can help describe the trend, but do not promise a specific pullback.  
**Figure/task:** Figure 3.2. Compare an upper-band walk with an isolated upper-band touch; identify which one gives stronger evidence of persistent directional movement.  
**Model reasoning:** Repeated interaction with the upper band while price continues to progress is more consistent with a strong uptrend than an immediate reversal.  
**Common mistake:** Calling a market overbought and shorting it only because price keeps touching the upper band.  
**Transfer:** Explain why the short-side mirror case—walking down the lower band—also argues for caution when buying every touch.  
**Source:** Bollinger official rule 7.

#### 3.3 — Two Ways Traders Talk About a “Squeeze”
**Time:** 16 minutes — read 8, inspect 3, task 3, review 2.  
**Outcome:** Distinguish Bollinger BandWidth contraction from the TTM Squeeze's comparison of Bollinger Bands with Keltner Channels.  
**Question:** Do all squeeze indicators identify the same condition?  
**Teach:** Bollinger's BandWidth approach looks for unusually narrow bands relative to their recent history. The TTM Squeeze, associated with John Carter, checks whether Bollinger Bands sit inside Keltner Channels and commonly adds a momentum display. Explain this distinction visually; do not turn it into a platform setup tutorial.  
**Figure/task:** Figure 3.3. Match each diagram to its condition and explain why their “squeeze on” states are not interchangeable.  
**Model reasoning:** One is based on the measured width of Bollinger Bands; the other compares two different volatility envelopes. Both concern contraction, but they define it differently.  
**Common mistake:** Treating “Bollinger squeeze” and “TTM Squeeze” as exact synonyms.  
**Transfer:** State what extra information a trader still needs before deciding direction in either case.  
**Source:** Bollinger official rule 19; Carter, *Mastering the Trade*; thinkorswim TTM Squeeze reference.

#### 3.4 — A Squeeze Does Not Choose the Direction
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Wait for price evidence rather than predicting an upward or downward breakout from compression alone.  
**Question:** What should you conclude when the bands are very narrow but price has not broken a clear level?  
**Teach:** A squeeze highlights a quiet period. Price may break upward, break downward, or make an initial move that fails. The first move is evidence to assess, not permission to ignore structure, entry location, and invalidation.  
**Figure/task:** Figure 3.4. Review three continuations from similar compressed conditions and write the evidence that supports each initial response.  
**Model reasoning:** The pre-breakout chart alone does not establish direction. A trader can prepare both scenarios and wait for a defined trigger.  
**Common mistake:** Entering before price resolves the direction simply because the bands are narrow.  
**Transfer:** Write one condition that would support a long plan and one that would cancel it.  
**Source:** Bollinger official rules 8, 19; Carter source distinction above.

### Module 4 — Read Bollinger's Signature Patterns

*Module purpose:* Make M-tops and W-bottoms understandable as structures that need evidence, not shapes to label after the fact.

#### 4.1 — Reading a W-Bottom
**Time:** 17 minutes — read 8, inspect 3, task 4, review 2.  
**Outcome:** Identify the key parts of a possible W-bottom and explain why the second low matters.  
**Question:** When two lows look similar, what would make the second low more informative?  
**Teach:** Introduce Bollinger's W-bottom as a price pattern interpreted with the bands. In the commonly described form, the first low pushes to or beyond the lower band while the second low holds at a more contained relative position. Explain the structure and the need for price confirmation without implying that two lows guarantee a reversal. Exact wording and pattern conditions must be checked against the book edition during final source verification.  
**Figure/task:** Figure 4.1. Compare a well-formed candidate with a similar-looking but incomplete pair of lows; mark the difference that matters.  
**Model reasoning:** The second low's relationship to the band differs, but the structure is only a candidate until price confirms it. Alternatives include continued weakness or a range that has not resolved.  
**Common mistake:** Buying any double bottom without checking context or the intervening swing.  
**Transfer:** State the price event you would wait for before treating the candidate as actionable.  
**Source:** Bollinger official rule 5 and *Bollinger on Bollinger Bands*; verify detailed pattern rule against the book before lesson drafting.

#### 4.2 — Reading an M-Top
**Time:** 17 minutes — read 8, inspect 3, task 4, review 2.  
**Outcome:** Identify a possible M-top and explain why two highs do not prove a reversal.  
**Question:** What is different when the second high fails to show the same relationship to the upper band?  
**Teach:** Introduce Bollinger's M-top as a price pattern read with the bands and any relevant indicator evidence. Explain the two highs, the middle reaction between them, and the need for a meaningful confirmation event. Do not sell the pattern as an automatic short.  
**Figure/task:** Figure 4.2. Compare a candidate M-top with two highs inside a strong uptrend; identify what remains unconfirmed.  
**Model reasoning:** The pattern may suggest weakening relative price action, but price can still break upward. A plan needs a trigger and a clear point where the thesis is wrong.  
**Common mistake:** Shorting the second high before sellers have shown meaningful control.  
**Transfer:** Write a no-trade condition for the M-top case.  
**Source:** Bollinger official rule 5 and *Bollinger on Bollinger Bands*; verify detailed pattern rule against the book before lesson drafting.

#### 4.3 — When Price and an Indicator Tell Different Stories
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Explain what a disagreement between price structure and %B or another independent indicator may add—and what it cannot prove.  
**Question:** If price makes a new high but an indicator does not, should you immediately sell?  
**Teach:** Indicator disagreement can draw attention to a change in momentum or relative position. It is a clue to examine, not proof of reversal. If using more than one indicator, prefer tools that add different information rather than several versions of the same calculation.  
**Figure/task:** Figure 4.3. Mark the visible disagreement, offer two possible explanations, and name what price action could help distinguish them.  
**Model reasoning:** The mismatch suggests the move may be changing, but the trend can continue. The learner should keep alternatives open until price supplies a meaningful discriminator.  
**Common mistake:** Treating divergence as a timing signal without a trigger.  
**Transfer:** Give one example of an indicator pairing that might add different information and explain why it is not guaranteed to help.  
**Source:** Bollinger official rules 3–5, 16–17.

#### 4.4 — Is the Pattern Complete Enough to Trade?
**Time:** 14 minutes — read 7, inspect 2, task 3, review 2.  
**Outcome:** Separate a visible pattern candidate from a confirmed, tradable plan.  
**Question:** At what point does a pattern become more than a shape on a chart?  
**Teach:** A pattern description helps organise observations, but a trading plan still requires context, a trigger, invalidation, risk, and reasonable room to the target. Show incomplete patterns, failed patterns, and cases where the correct answer is to wait.  
**Figure/task:** Figure 4.4. Label each example as candidate, confirmed under the lesson's stated rule, failed, or unclear; explain one evidence point for each label.  
**Model reasoning:** Labels depend on explicit conditions. “Unclear” is reasonable when the needed swing or confirmation is missing.  
**Common mistake:** Using hindsight to see a clean pattern that was not clear at the decision point.  
**Transfer:** Describe what evidence you would need before planning a short from a candidate M-top.  
**Source:** Bollinger official rules 5, 22; any operational confirmation rule is a course-defined framework.

### Module 5 — Build Buy and Sell Plans

*Module purpose:* Translate the earlier reading skills into testable plans. Every setup here is educational, conditional, and not a promise of performance.

#### 5.1 — From Chart Reading to a Trade Plan
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Build a plan with context, trigger, confirmation, invalidation, entry logic, stop, exit, and no-trade criteria.  
**Question:** What must be decided before an appealing chart becomes a planned trade?  
**Teach:** Give students a reusable plan template. Context says what kind of market is present; trigger says what must happen; confirmation adds independent evidence; invalidation says what makes the idea wrong; stop and size keep risk defined; exit logic avoids improvisation.  
**Figure/task:** Figure 5.1. Fill in the missing parts of an incomplete plan and identify which parts are still assumptions.  
**Model reasoning:** A plan is incomplete if it identifies an entry but does not define where the idea fails or how much could be lost.  
**Common mistake:** Choosing the entry first and inventing a stop afterward.  
**Transfer:** Apply the template to the long and short examples in the next lesson.  
**Source:** Framework is course-designed from Bollinger's setup principles; not presented as a verbatim Bollinger system.

#### 5.2 — Plan a Squeeze Breakout in Either Direction
**Time:** 18 minutes — read 8, inspect 4, task 4, review 2.  
**Outcome:** Create symmetrical long and short plans after a period of compression.  
**Question:** How can you prepare for a move without guessing which direction will break?  
**Teach:** Course framework: define the compressed area and a meaningful nearby price boundary; require a closed-bar price break for a trigger; optionally require price to hold the break or use one independent momentum/volume clue; define the nearby structure that invalidates the idea; set the stop beyond that structure; define exit/management before entry. The long and short rules must mirror one another. A close outside the band alone is not an automatic entry.  
**Figure/task:** Figure 5.2. Build a long and short plan from opposite examples, then reject the case where the target is too close to the planned stop.  
**Model reasoning:** The squeeze gives a volatility context, not a direction. The range break provides the candidate direction; the risk/reward and invalidation decide whether a trade is acceptable.  
**Common mistake:** Treating every squeeze release or outside-band close as a trade.  
**Transfer:** State how your plan changes if price breaks the boundary and quickly returns inside the prior range.  
**Source:** Bollinger official rules 8, 18–19; Carter's TTM approach is separate. Trigger/stop/exit details here are a course-defined framework requiring testing.

#### 5.3 — Plan a Range Trade Without Fighting a Trend
**Time:** 18 minutes — read 8, inspect 4, task 4, review 2.  
**Outcome:** Build long and short range-fade plans only when the range is established and risk is acceptable.  
**Question:** When is a move toward an outer band a possible range opportunity rather than a trend signal?  
**Teach:** Require visible range boundaries and repeated evidence that price is rotating rather than trending. A band touch by itself is not the trigger. Course framework: for a long, wait for price to test a range low and show a defined rejection or return into the range; for a short, mirror that at the range high. Place invalidation beyond the structure that would break the range premise; target the middle of the range or the opposite side only when the available reward justifies the risk.  
**Figure/task:** Figure 5.3. Compare one range that stays intact with one that starts breaking into a trend. Select which supports a range trade and state the cancellation condition.  
**Model reasoning:** A range trade depends on the range continuing to hold. If price is accepting outside the boundary or walking a band, the premise may no longer be valid.  
**Common mistake:** Fading the outer band without proving there is a range.  
**Transfer:** Write the mirrored short-side conditions for a valid range high.  
**Source:** Bollinger official rules 6–7; the entry, stop, and target rules are course-designed and must be tested.

#### 5.4 — Plan a Possible W-Bottom or M-Top Reversal
**Time:** 18 minutes — read 8, inspect 4, task 4, review 2.  
**Outcome:** Turn a candidate W-bottom into a conditional long plan and a candidate M-top into a conditional short plan.  
**Question:** What would need to happen before a reversal candidate becomes actionable?  
**Teach:** Revisit the pattern structure without repeating the full lesson. Use a defined confirmation point (for example, a break of the intervening swing) only as a clearly labelled course rule. Identify structural invalidation, set risk from stop distance, and plan an exit before entry. If there is no sensible risk/reward, do not take the pattern simply because the shape looks attractive.  
**Figure/task:** Figure 5.4. Mark candidate trigger, invalidation, a logical target area, and one reason each setup might be skipped.  
**Model reasoning:** A pattern creates a possible scenario. The confirmation point and invalidation turn it into a testable plan; neither makes the outcome certain.  
**Common mistake:** Entering at the second high or low before the pattern has given the chosen confirmation.  
**Transfer:** Reverse the direction and write the equivalent conditions for the opposite pattern.  
**Source:** Bollinger official rule 5 and *Bollinger on Bollinger Bands*; exact confirmation logic is course-defined unless verified as the author's own rule.

#### 5.5 — Which Plan Fits This Chart—or None?
**Time:** 14 minutes — read 6, inspect 3, task 3, review 2.  
**Outcome:** Choose a fitting setup framework or justify standing aside.  
**Question:** Does every chart with Bollinger Bands offer a trade?  
**Teach:** Compare a trend continuation candidate, a clear range candidate, a possible reversal pattern, and an ambiguous chart. Ask students to decide which rule set—if any—matches the visible context.  
**Figure/task:** Figure 5.5. Choose long framework, short framework, or no trade for four supplied panels, then explain the evidence and the missing condition.  
**Model reasoning:** A setup only applies if the required context and trigger exist. Ambiguous context, poor space to target, or missing invalidation can justify no trade.  
**Common mistake:** Forcing every chart into the one setup the learner has just studied.  
**Transfer:** Explain which evidence would make one of the rejected cases worth reviewing again.  
**Source:** Synthesis of Bollinger official rules; selection framework is course-designed.

### Module 6 — Recognise Failed Setups and Know When to Wait

*Module purpose:* Train students to spot how plausible setups fail and react to evidence rather than defend the original idea.

#### 6.1 — The False Start After a Squeeze
**Time:** 16 minutes — read 7, inspect 3, task 4, review 2.  
**Outcome:** Recognise a head-fake and name evidence that would weaken or invalidate the first breakout idea.  
**Question:** What if price breaks upward after a squeeze, then quickly falls back into the prior range?  
**Teach:** Describe the failed initial move and the risk of assuming the first break must continue. Set a clear rule for when the original plan is invalidated. A move in the opposite direction is possible but should not be predicted before evidence appears.  
**Figure/task:** Figure 6.1. Identify the first breakout, the point where the continuation case weakens, and what must happen before considering the opposite direction.  
**Model reasoning:** Re-entry into the prior range weakens the breakout thesis. It does not automatically justify the reverse trade without a new trigger and suitable risk.  
**Common mistake:** Reversing position immediately after a failed break without a new plan.  
**Transfer:** Write the same invalidation logic for an initial downside break.  
**Source:** Bollinger's *Bollinger on Bollinger Bands* discussion of squeeze head-fakes; detail to verify against the edition used.

#### 6.2 — When a Band Walk Traps Reversal Traders
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Explain why repeated band touches in a trend can make a simple mean-reversion trade risky.  
**Question:** What evidence warns you that price may keep moving along the band?  
**Teach:** Use repeated closes near one band, directional swing structure, and a middle band that supports the trend as context clues. These are clues, not an infallible trend test. A reversal idea needs evidence of weakening or a structural change, not just a stretched price.  
**Figure/task:** Figure 6.2. Compare an ongoing band walk with a walk that begins to lose structure; point to the evidence that differs.  
**Model reasoning:** The first chart keeps making progress in the same direction, so fading it is premature. The second may warrant review but still needs a trigger.  
**Common mistake:** Calling price overbought or oversold solely because it is near an outer band.  
**Transfer:** List one piece of evidence that would make you stop considering a short in the first chart.  
**Source:** Bollinger official rule 7.

#### 6.3 — When a Range Trade Stops Being a Range Trade
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Recognise when a range-fade premise is weakening or broken.  
**Question:** If price crosses a range boundary and continues moving away, what happens to a plan that expected a bounce?  
**Teach:** Range strategies rely on range boundaries holding. A sustained move beyond a boundary, expanding bands, and follow-through may suggest the range has broken. A single poke can fail; distinguish that from acceptance beyond the boundary using the pre-defined plan rather than hindsight.  
**Figure/task:** Figure 6.3. Compare a false break with a range that begins to transition into a trend. Mark where the original range-trade idea should be paused or invalidated under the stated rule.  
**Model reasoning:** The range premise must remain true. Once the chosen invalidation condition occurs, the old trade plan no longer applies.  
**Common mistake:** Averaging into a losing range trade because price “should come back.”  
**Transfer:** Explain when a new breakout setup could be considered and why it is separate from the failed fade.  
**Source:** Bollinger official rules 6–8; course-defined scenario rules.

#### 6.4 — Late Entries, Conflicting Evidence, and No-Trade Conditions
**Time:** 16 minutes — read 7, inspect 3, task 4, review 2.  
**Outcome:** Reject trades with poor location, conflicting evidence, unsuitable conditions, or too little reward for the risk.  
**Question:** What if the breakout is real but the move has already travelled a long way?  
**Teach:** Review late entries after expansion, event-driven gaps, thin/illiquid markets, contradictory evidence, unclear structure, and trades where the target is too close relative to invalidation. A good analysis does not require an entry. Avoid universal claims about which sessions or events are safe; the correct filter depends on market and strategy.  
**Figure/task:** Figure 6.4. Mark which of four cases should be skipped and cite the specific reason, not a vague feeling.  
**Model reasoning:** A correct directional view can still be a poor trade if the entry is late, the stop is too far away, liquidity is poor, or the premise is unclear.  
**Common mistake:** Believing that missing a move is worse than entering a low-quality trade.  
**Transfer:** Write a short no-trade checklist with three conditions that would make you wait.  
**Source:** Bollinger official rule 22; risk and execution checks are general course frameworks.

### Module 7 — Manage Risk and Review the Process

*Module purpose:* Turn a chart idea into a controlled decision process and distinguish good reasoning from one lucky or unlucky outcome.

#### 7.1 — Size the Trade From the Point Where the Idea Fails
**Time:** 16 minutes — read 8, inspect 2, task 4, review 2.  
**Outcome:** Calculate a position size from the planned loss limit and distance between entry and stop.  
**Question:** Why should the stop be decided before working out how large the position should be?  
**Teach:** Explain the simple relationship between allowed cash risk, entry-to-stop distance, and position size. Include fees, slippage, and gaps as limitations. Use one worked numeric example, without recommending a universal risk percentage.  
**Figure/task:** Figure 7.1. Complete the missing value in the sizing example and explain how a wider stop changes the size if the planned cash risk stays the same.  
**Model reasoning:** If the stop is farther away, the position generally needs to be smaller to keep the same planned cash risk. Actual loss can exceed the estimate.  
**Common mistake:** Using the same position size regardless of stop distance.  
**Transfer:** Compare two plans with equal cash risk but different stop distances and explain why their quantities differ.  
**Source:** General risk management; Carter's *Mastering the Trade* offers a separate reference on risk control but does not validate one universal sizing rule.

#### 7.2 — Decide How You Will Manage the Trade Before Entry
**Time:** 15 minutes — read 7, inspect 3, task 3, review 2.  
**Outcome:** Match exit and management decisions to the plan's original reason for entry.  
**Question:** If price moves in your favour, how will you know whether to hold, reduce, or exit?  
**Teach:** Explain target-based exits, structure-based trailing, and a rule-based exit if the premise fails. Avoid presenting one management method as best for every setup. A middle-band cross can be a rule to test, not a universal exit signal.  
**Figure/task:** Figure 7.2. Trace the possible paths of a trade through target, invalidation, or unresolved movement and choose the action written in the example plan.  
**Model reasoning:** Consistency comes from deciding the rules before the outcome, not from changing the plan because the latest candle feels uncomfortable.  
**Common mistake:** Changing exits randomly after entry.  
**Transfer:** Pick one exit rule for a sample setup and state one reason it might not fit another setup.  
**Source:** Bollinger principles support context-based decisions; specific management choices in this lesson are course-designed.

#### 7.3 — Test the Idea Without Fitting It to the Past
**Time:** 16 minutes — read 7, inspect 3, task 4, review 2.  
**Outcome:** Evaluate a rule on a varied set of examples without changing its conditions after each outcome.  
**Question:** Does a setup work because it looks convincing on one chart?  
**Teach:** Use a small, consistently labelled review set across trend, range, and failed-breakout conditions. Record the exact context, trigger, stop, exit, result, and whether the rules were followed. Keep settings and rules stable during a review set; separate a new version of a rule from the old one.  
**Figure/task:** Figure 7.3. Compare a cherry-picked group with a more varied sample; identify why the first may give a misleading impression.  
**Model reasoning:** A few attractive examples cannot establish reliability. Consistency and varied conditions help expose weaknesses, though a small sample remains limited evidence.  
**Common mistake:** Repeatedly changing settings until the examples look successful.  
**Transfer:** Name one additional market condition that should be included before trusting the reviewed setup.  
**Source:** Course-designed testing practice; Bollinger's parameter cautions in official rules 9 and 11.

#### 7.4 — Review the Decision, Not Just the Result
**Time:** 18 minutes — read 7, inspect 4, task 5, review 2.  
**Outcome:** Produce a concise trade review that separates the quality of the plan from the eventual outcome.  
**Question:** Can a losing trade still follow a sound process, and can a winning trade still be poorly planned?  
**Teach:** Bring together context, band behaviour, setup, trigger, invalidation, risk, management, result, and what the student learned. Distinguish what was knowable before entry from what became visible later.  
**Figure/task:** Figure 7.4. Complete the supplied review for three cases: a reasonable losing trade, an undisciplined winning trade, and a valid no-trade decision.  
**Model reasoning:** Judge the decision using the evidence and rules available at the time, not only the result. A disciplined no-trade decision may be the strongest response when a required condition is missing.  
**Common mistake:** Judging every decision only by whether it made money.  
**Transfer/capstone:** Use the supplied figure set to write one full long plan, one full short plan, and one no-trade explanation. Include context, trigger, confirmation, invalidation, stop/size logic, exit, and the evidence that would change the view.  
**Source:** Course synthesis; source-specific claims remain mapped to the reference list below.

## Dedicated setup framework: source rules versus course rules

The source author and the course framework must never be blurred together.

| Setup | Source principle | Course-designed implementation to test |
|---|---|---|
| Squeeze breakout long/short | Bollinger describes closes outside the bands as initially continuation signals; BandWidth can identify unusually narrow bands. | Define a compression window and a nearby price boundary; wait for a closed-bar break; optionally require follow-through or independent confirmation; cancel if the break fails the stated rule; position size from invalidation. |
| Range mean reversion long/short | A band tag is not a signal; market context matters. | Only consider fading a boundary after a range is established and price shows a defined rejection/return; cancel the idea if the range premise breaks. |
| W-bottom / M-top reversal | Bollinger explicitly discusses the use of Bands in clarifying M-tops and W-bottoms. | Define a trigger and invalidation for the pattern, with a stop based on price structure and exits specified before entry. Verify exact author-defined pattern rules in the book before presenting any exact rule as Bollinger's. |

No setup should be described as guaranteed or “high probability” without credible evidence. If numeric thresholds are used, label them as a course convention and explain that they require testing across instruments and market conditions.

## Source map and authority notes

### Primary: John Bollinger
- [Official Bollinger Band Rules](https://www.bollingerbands.com/bollinger-band-rules). The best primary reference for the core principles: relative high/low, tags not signals, band walks, closes outside initially treated as continuation rather than reversal, settings as defaults, %B, BandWidth, and cautions about normal-distribution assumptions. Use these rules accurately and cite them in relevant lessons.
- [Bollinger's official book page](https://www.bollingerbands.com/bollinger-band-book) and [McGraw Hill book listing](https://www.mheducation.com/highered/mhp/product/bollinger-bollinger-bands). *Bollinger on Bollinger Bands*, John Bollinger, McGraw Hill Professional, first edition published 2001; print ISBN 978-0-07-137368-5 (eBook ISBN 978-0-07-138673-9). Main source for how the creator develops the use of relative price, price/indicator relationships, patterns, trading systems, and confirmation. Confirm fine-grained chapter and pattern details from the edition used before final lesson drafting.

### Distinct approach: John F. Carter and the TTM Squeeze
- *Mastering the Trade*, John F. Carter, Third Edition, McGraw Hill Professional (2018/2019 listings vary by release/market). [Publisher page](https://www.mheducation.com/highered/mhp/product/mastering-trade-third-edition-proven-techniques-profiting-intraday-swing-trading-setups.html).
- [thinkorswim TTM Squeeze reference](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/T-U/TTM-Squeeze.html) gives a platform-level description: Bollinger Bands relative to Keltner Channels with a momentum component. Use it to explain the indicator family, not to claim every platform uses identical settings or colours.

### Reputable secondary technical references
- [StockCharts: Bollinger Bands](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands) — accessible description of construction and common settings.
- [StockCharts: %B](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/b-indicator) — formula and interpretation of relative position.
- [StockCharts: BandWidth](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/bollinger-bandwidth) — normalised width and contraction/expansion.
These are useful explanatory references, not substitutes for the creator's own source when attributing principles.

## Final assignment

Use only the supplied static figures. The student receives three chart cases with enough surrounding price history to judge context.

For each case:
1. Describe the market as trend, range, transition, or unclear and point to visible evidence.
2. State what the bands and, where shown, %B/BandWidth add to that reading.
3. Choose a long framework, a short framework, or no trade.
4. If proposing a trade, specify the context, trigger, confirmation, invalidation, stop logic, risk/size logic, and planned exit.
5. Name one credible alternative explanation and the evidence that would change the view.
6. Explain one common failure mode that applies to the case.
7. Separate the quality of the decision from the later outcome shown in the case.

**Assessment standard:** evaluate whether the student used visible evidence, considered alternatives, defined invalidation and risk, and made a defensible decision. Do not assess whether the student guessed the future price direction.

## Educational disclaimer

This course is for educational purposes only and is not personal financial advice. Trading involves risk, including the possibility of losing more than expected due to gaps, slippage, and market conditions. Bollinger Bands and other indicators describe market data; they do not predict outcomes with certainty. No setup is guaranteed, and any course-designed trading framework must be tested and adapted before use.

## Production and release checklist

- [ ] Verify author-specific claims and detailed M-top/W-bottom definitions against the actual book edition.
- [ ] Ensure all lesson titles and explanations use plain, natural language for an intermediate trader.
- [ ] Ensure each lesson takes 10–20 minutes including its visual task and review.
- [ ] Check every lesson has a useful question, observable outcome, image task, model reasoning, misconception, and transfer prompt.
- [ ] Confirm no concept is re-taught unnecessarily across modules.
- [ ] Build each figure to a defined teaching need and use the figure labels in ASSET_REGISTER.md.
- [ ] Make all labels readable on mobile and at 200% zoom; provide useful alt text.
- [ ] Do not present illustrative charts as genuine historical market data.
- [ ] Keep source statements separate from course-designed entry, stop, and exit rules.
- [ ] Review all buy and sell frameworks symmetrically and include explicit no-trade criteria.
- [ ] Check sources and links again before full lesson drafting.
- [ ] Do not integrate, publish, or deploy until the content and assets have been reviewed.
