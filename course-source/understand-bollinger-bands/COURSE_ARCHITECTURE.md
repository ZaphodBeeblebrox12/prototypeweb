# Understand Bollinger Bands — Course Architecture

**Status:** Full-text draft complete; detailed source verification, final figures, and learner testing remain  
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
| 5. Build Buy and Sell Plans | Apply six author-based methods with explicit triggers, entry choices, stops, skip rules, and historical chart comparisons. | 6 |
| 6. Recognise Failed Setups and Know When to Wait | Study the traps that make otherwise attractive setups fail. | 4 |
| 7. Manage Risk and Review the Process | Size, manage, test, journal, and apply the full reasoning process. | 4 |

**Planned lesson count:** 30  
**Expected total learning time:** approximately 8.75–9.25 hours, based on the current lesson estimates below. The estimates sum to about 8 hours 54 minutes; this is a planning estimate, not a measured completion time.

## Teaching and language standards

### The course-wide reasoning habit: Observe → Interpret → Test

Use this as the visible reasoning routine across the course, not as a separate indicator or a rigid form.

- **Observe:** State what the chart shows without guessing at hidden causes. Describe price relative to the bands, band width, swing structure and the sequence of price behaviour.
- **Interpret:** Explain what the evidence may mean in context, then name at least one plausible alternative.
- **Test:** State what further evidence or pre-defined condition would strengthen or weaken the interpretation. When the lesson concerns a trade, translate this into a trigger and an invalidation condition.

“Test” must not imply that a learner can prove the next move. A single chart example illustrates a concept; it does not validate a trading strategy. Strategy testing across a varied set of cases remains a separate activity in Module 7. When evidence is insufficient, “wait” or “no trade” is a complete, reasoned decision.

Every lesson should practise this sequence in a way that fits its topic. Do not mechanically repeat the same three questions or add boilerplate that does not help the learner. The examples, counterexamples, tasks and model answers should collectively make all three steps visible.


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

Timings include reading, inspecting the supplied static figures and the provided case examples, completing the task, and reviewing model reasoning. There is no ChartLab or activity requiring learners to find their own charts. Module 5 currently embeds temporary historical chart references; those must be replaced with course-owned or rights-cleared local images before public release.

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

### Module 5 — Build and Trade Bollinger Setups

*Module purpose:* Make the course's market angle concrete by teaching the methods John Bollinger wrote about, his later official confirmed-breakout extension, and John Carter's distinct TTM Squeeze. Students learn the author's conditions first, then add a clear risk plan without confusing course additions with source rules.

#### 5.1 — Method I: Trade the Volatility Breakout
**Time:** 28 minutes.  
**Outcome:** Identify historically narrow BandWidth conditions and construct long and short plans triggered by a breakout beyond the corresponding band.  
**Author's rule:** The Squeeze is the setup; the first breakout is the directional event. The book warns about head fakes and discusses using a Parabolic-style or opposite-band stop. The later official software implementation uses a 125-period BandWidth low and a recent-squeeze lookback.  
**Figure/task:** Figure 5.1 is paired with a five-chart historical gallery. Students compare earlier, close-confirmed, and retest entries; mark structural stops, nearby obstacles, and head-fake risk.  
**Source:** John Bollinger, *Bollinger on Bollinger Bands*, Chapter 16; official Method I manual.

#### 5.2 — Method II: Follow Strength Confirmed by MFI
**Time:** 28 minutes.  
**Outcome:** Use Bollinger's published %B/MFI conditions to recognise trend-following long and short setups.  
**Author's rule:** Buy when %B is above 0.8 and MFI(10) is above 80; sell/short when %B is below 0.2 and MFI(10) is below 20. The method does not require a squeeze. Bollinger discusses a modified Parabolic stop or an opposite-band tag as exit choices.  
**Figure/task:** Figure 5.2 is paired with six historical %B/MFI cases, including failed and filtered signals. Students mark when both thresholds first agree, compare entry timing, and choose an invalidation level.  
**Source:** John Bollinger, *Bollinger on Bollinger Bands*, Chapter 19; official Method II manual.

#### 5.3 — Method III: Look for Reversal Clues in Volume
**Time:** 28 minutes.  
**Outcome:** Identify Bollinger's band-tag/volume-indicator reversal alert and distinguish it from a confirmed entry.  
**Author's rule:** The book gives examples such as %B below 0.05 with positive Intraday Intensity for a long, and %B above 0.95 with negative Accumulation/Distribution for a short. Bollinger's official software manual also documents a band-tag/Intraday Intensity alert and recommends waiting for a strong up/down price bar. These are documented variants; indicator choice must be stated.  
**Figure/task:** Figure 5.3 is paired with five reversal examples. Students distinguish band alert from price confirmation, specify the indicator variant, and place invalidation beyond the swing extreme.  
**Source:** John Bollinger, *Bollinger on Bollinger Bands*, Chapter 20; official Method III manual.

#### 5.4 — Method IV: Wait for a Confirmed Breakout
**Time:** 27 minutes.  
**Outcome:** Apply the later official Method IV rule: squeeze context, two consecutive closes outside the same band, and ADX to distinguish trend-following from reversal treatment.  
**Author's rule:** Two outside closes confirm the breakout condition. When ADX is above the chosen threshold, the break is treated as trend-following; when ADX is below it, the method treats the outside-band event as a potential reversal in the opposite direction. The threshold is configurable, not universal.  
**Figure/task:** Figure 5.4 is paired with five breakout/head-fake cases. Students independently verify the squeeze, two consecutive closes, and ADX context before calling a case a Method IV signal.  
**Source:** John Bollinger, official Method IV manual (developed after the book).

#### 5.5 — Trade the W-Bottom and M-Top, Not Just the Shape
**Time:** 28 minutes.  
**Outcome:** Apply the author's band-relative pattern rules and identify a price-confirmation event for a potential reversal.  
**Author's rule:** For a classic W-bottom, the first low is usually at/outside the lower band and the retest is relatively higher inside the band; a lower absolute price on the retest does not automatically invalidate it. Bollinger describes buying strength on a rally day with above-average range and volume, with a stop below the right-side low. Tops may take longer and include repeated pushes, with later highs failing to reach the upper band; wait for a sign of weakness and define risk around the pullback.  
**Figure/task:** Figure 5.5 is paired with six W/M chart cases. Students mark the relative swing, confirmation trigger, invalidation level, and a no-trade reason.  
**Source:** John Bollinger, *Bollinger on Bollinger Bands*, Chapters 12–13.

#### 5.6 — Carter's TTM Squeeze: Use Momentum for Direction
**Time:** 25 minutes.  
**Outcome:** Distinguish Carter's two-envelope squeeze from Bollinger's BandWidth squeeze, then read a common TTM release/momentum setup.  
**Source method:** In the common TTM implementation, the squeeze is on when Bollinger Bands fit inside Keltner Channels; it fires when they expand back outside. A positive, rising momentum histogram is the common long-side reading; a negative, falling histogram is the short-side reading. Treat specific settings and histogram exits as an implementation, not universal rules for every platform.  
**Figure/task:** Figure 5.6 is paired with five TTM examples. Students identify squeeze-on, fire, histogram direction, entry trigger, stop boundary, and at least one failed or ambiguous release.  
**Source:** John F. Carter, *Mastering the Trade*, Third Edition; StockCharts TTM Squeeze technical reference.

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

## Setup module: source rules versus course implementation

The setup module is built around author-published methods rather than mostly generic course-created templates. Teach the source rules accurately first, then explain which decisions still need to be made for a trade plan.

| Method | Author/source-defined core | Decisions the student must still make |
|---|---|---|
| Bollinger Method I — Volatility Breakout | A squeeze is the setup; the first upside breakout beyond the upper band or downside break below the lower band provides direction. Bollinger warns about head fakes and describes stop-management approaches. | Define the squeeze lookback implementation, decide how to handle failed first moves, locate structural invalidation, size the position and choose a tested exit. |
| Bollinger Method II — Trend Following | In the book's example, buy when %B > 0.8 and MFI(10) > 80; sell/short when %B < 0.2 and MFI(10) < 20. No squeeze is required. | Choose the source-described exit option, define size/risk, and test the published thresholds rather than assuming they fit every market. |
| Bollinger Method III — Reversals | Band tag plus a volume-based indicator pointing the other way; published examples include %B < 0.05 with positive Intraday Intensity for long, or %B > 0.95 with negative Accumulation/Distribution for short. Later official software describes another Intraday Intensity variant. | State which indicator variant is being used, wait for the source-recommended price confirmation, and define structural invalidation. |
| Bollinger Method IV — Confirmed Breakout | Later official method: squeeze followed by two consecutive closes outside the same band; ADX distinguishes trend-following from reversal treatment. | Use a declared ADX threshold from the implementation being studied, define invalidation, and test the method on the intended market/timeframe. |
| Bollinger W-bottom / M-top | Relative band position clarifies the pattern. The book's W-bottom example buys a strong rally day with above-average range and volume, with a stop below the right-side low. Top formations need evidence of weakness and often take longer. | Decide whether the pattern truly meets the author's description, check space to target, and define an exit/stop plan that fits the instrument. |
| Carter TTM Squeeze | Common implementation: Bollinger Bands contract inside Keltner Channels, then release; the momentum histogram helps choose direction. | Verify platform settings, require the release and stated momentum condition, and define how to manage a failed release. |

**Important:** Published setup conditions are included because they are the point of this course. The fact that an author developed or recommended a method is not independent proof that it remains profitable in every market. Bollinger himself encourages traders to try the methods, customise them to their risk/reward needs and test them on the instruments they trade. Preserve his rules faithfully; then test them honestly.

For each method, keep three layers distinct:
1. **Published method:** what the author specifies.
2. **Trade plan:** entry/confirmation, invalidation, stop, position size and exit chosen for the example.
3. **Evidence of performance:** results from a consistent test on the target market/timeframe, including costs and failures.

## Source map and authority notes

### Primary: John Bollinger
- [Official Bollinger Band Rules](https://www.bollingerbands.com/bollinger-band-rules). Primary source for relative high/low, tags not signals, band walks, outside closes as initially continuation rather than reversal, %B, BandWidth, and the limits of default settings.
- [Official book page](https://www.bollingerbands.com/bollinger-band-book) and [McGraw Hill book listing](https://www.mheducation.com/highered/mhp/product/bollinger-bollinger-bands). *Bollinger on Bollinger Bands*, John Bollinger, McGraw Hill Professional, first edition published 2001. The book has dedicated chapters for W-bottoms, M-tops, walking the bands, the Squeeze, Method I (Volatility Breakout), Method II (Trend Following), and Method III (Reversals).
- [Method I: Volatility Breakout manual](https://www.bollingerbands.com/_files/ugd/58be43_f5e967053af44fa083340cacfc5e6226.pdf). Documents Bollinger's official software implementation and its squeeze/breakout alerts.
- [Method II: Trend Following manual](https://www.bollingerbands.com/_files/ugd/58be43_b120ddf0184540608baf19e2c0ae2019.pdf). Confirms that the method combines strong price action with MFI confirmation.
- [Method III: Reversals manual](https://www.bollingerbands.com/_files/ugd/58be43_377f4254baa04a19aaadb1735b45b6f0.pdf). Documents the band-tag plus Intraday Intensity reversal alerts and the recommendation to wait for price confirmation.
- [Method IV: Confirmed Breakouts manual](https://www.bollingerbands.com/_files/ugd/58be43_d09c50b6e8ea4afd9af0523ef94de876.pdf). Bollinger's later extension of Method I: squeeze context, two consecutive closes outside a band, and ADX-based trend/reversal interpretation.
- The source-specific conditions in the setup lessons are paraphrased from the relevant method descriptions. The course does not reproduce book text.

### Distinct approach: John F. Carter and the TTM Squeeze
- *Mastering the Trade*, John F. Carter, Third Edition. [Publisher page](https://windsorpublishing.com/product/mastering-the-tradethird-edition/).
- [StockCharts TTM Squeeze reference](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ttm-squeeze) explains the commonly used Bollinger Band/Keltner Channel compression test and how momentum histogram direction is interpreted. Attribute exact settings and exit conventions to the documented implementation, not automatically to every edition/platform of Carter's method.

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
