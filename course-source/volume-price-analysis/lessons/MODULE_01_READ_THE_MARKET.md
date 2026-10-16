# Module 1 — Read the Market Behind the Candles
## Student lessons

This module establishes the course's first habit: **describe what price did, describe the activity your data source recorded, and only then consider what the combination might mean.** A candle is evidence, not a complete explanation of the market.

By the end of this module, you should be able to describe candle shape in plain language, compare activity with a sensible baseline, recognise when a volume reading is unreliable, and state what you do and do not know from a chart.

---

## Lesson 1.1 — What Candlesticks Don't Tell You: Reading the Volume Behind Price

### The question

Two candles are green and similar in size. Does that mean they tell the same story?

Not necessarily. A candlestick summarises price during a chosen interval. It shows the open, high, low and close. It does not show the full sequence of orders, identify every participant, or explain why the market moved. Volume adds another piece of evidence: the amount of activity recorded by the particular data source during that interval.

### Begin with the facts

Consider these two **synthetic examples**. They use the same hypothetical instrument and timeframe so that the comparison is meaningful.

| Measure | Candle A | Candle B |
|---|---:|---:|
| Open | 100.0 | 100.0 |
| High | 104.0 | 105.0 |
| Low | 99.0 | 99.5 |
| Close | 103.0 | 104.0 |
| Recorded volume | 520 | 1,800 |
| Recent comparable-bar average | 480 | 600 |
| Volume relative to baseline | 1.08× | 3.00× |

Both candles closed above their opens. Candle B travelled slightly farther and recorded much more activity relative to its recent baseline. Those are observations. Saying “large buyers entered Candle B” would be a guess: the chart does not identify who traded or why.

The useful question is: **what did price achieve while this amount of activity was recorded?** That question connects price outcome with volume without pretending volume reveals hidden intent.

### A simple reading method

Use these steps whenever a candle catches your attention:

1. **Describe the price result.** Did price rise or fall from open to close? How wide was the high-to-low range? Where did it close within that range?
2. **Describe the activity.** Was recorded volume higher or lower than a stated baseline? How did you choose that baseline?
3. **Add location.** Did the candle occur at a prior swing, range boundary or other meaningful area, or in the middle of nowhere?
4. **Keep the interpretation conditional.** State one possible reading and what future behaviour would support or weaken it.

The order matters. If you start with “this is accumulation” or “buyers are trapped”, you may unconsciously select only the evidence that supports your first guess.

### Worked example

Candle B recorded three times the average volume of its recent comparable bars and closed in the upper part of its range. One reasonable observation is that substantial recorded activity accompanied an upward price result. If this occurred during a move through a well-established range high, it would be worth examining whether price could hold beyond that boundary.

That still does **not** confirm a breakout. The next bars may hold above the boundary, return inside the range, or overlap without resolving the question. The first candle gives you a reason to pay attention; the later behaviour helps you judge which explanation fits better.

### Worked comparison — same colour, different evidence

Compare two hypothetical green candles at the same scale. Candle A rises from 100 to 103 on 1.1× relative volume and occurs after a quiet pullback. Candle B rises from 100 to 104, records 3× relative volume and appears after an extended advance near the prior high. Both closed up. B had more recorded activity and slightly more progress, but its location makes the unresolved test different: can price sustain itself above the high, or does it return inside? The example is deliberately inconclusive until follow-through appears.

### Level 1 — Notice (easy)

**Task:** Using Candle B's table, identify the candle direction and relative-volume multiple.

**Feedback:** It closed above its open and recorded 3.00× its stated baseline. Those are facts; they do not identify who traded.

### Level 2 — Compare (guided)

**Task:** Compare Candles A and B. Which facts differ, and what is the strongest conclusion the data supports?

**Feedback:** B had slightly more price progress and much higher relative volume. The sound conclusion is that more recorded activity accompanied the upward close.

### Level 3 — Apply (independent)

**Task:** A new green candle closes near its high at a prior range boundary on 1.6× relative volume. Give two possible readings and one future discriminator.

**Model response:** It may be a breakout attempt or a temporary excursion. A hold above the boundary supports continuation; a return inside and failed reclaim supports the alternative.
### Common mistake

**Mistake:** Treating a green candle as proof of strong demand.

**Correction:** A green candle shows that the close was above the open. Its significance depends on the range, close location, activity, prior structure and what happens next.

### Keep this

> **Price shows the outcome. Volume describes recorded activity. Context helps you decide what the combination may mean.**

---

## Lesson 1.2 — Is This Move Significant? Spotting Unusual Volume

### The question

Is a volume reading of 900 high? The number alone cannot answer. It depends on the instrument, timeframe, session and activity that is normal for the comparison period.

A useful first measure is **relative volume**: current volume divided by a chosen baseline.

\[
\text{Relative volume}=\frac{\text{Current volume}}{\text{Baseline volume}}
\]

If a bar records 900 contracts and the average of the 20 preceding comparable bars is 600, relative volume is 900 ÷ 600 = **1.5×**. That means the bar recorded 50% more volume than the selected baseline. It does not mean that buying pressure was 50% stronger.

### Choose a fair comparison

A baseline is useful only if its bars are comparable. Consider:
- **Instrument:** do not compare the absolute volume of two different instruments as though the numbers mean the same thing.
- **Timeframe:** a 5-minute bar should not casually be compared with a daily bar.
- **Session:** the opening period may normally be more active than a quiet midday period.
- **Data source:** exchange-traded volume, tick volume and broker-specific volume are not interchangeable.
- **Outliers:** one exceptional bar can distort a simple average. If the history has extreme spikes, compare with the median or inspect the baseline before trusting one ratio.

There is no universally correct lookback length. A 20-bar average can be a sensible starting point, but the right comparison depends on the market and question. State the method so another person can understand your reading.

### A volume spike is not a direction signal

Suppose a bar records 2.5× its baseline. That tells you activity is unusually high against that baseline. Now compare two possible price outcomes:

| Event | Price result | What the activity helps you ask |
|---|---|---|
| A | Wide candle closes near its high | Did the move make progress and retain it? Does later price action continue to hold that progress? |
| B | Wide candle leaves a long upper wick and closes back inside a range | Why did substantial activity accompany limited retained upside progress? Is the event unresolved or did price fail to hold beyond the boundary? |

High activity occurs in both cases. The price outcome differs. Volume cannot replace the reading of the candle and its location.

### Worked example

A bar closes above a range high on 1.8× its 20-bar average. Record three things: the close is above the boundary; activity was elevated relative to the stated baseline; the event occurred where the market previously stalled. A continuation interpretation is possible, but acceptance outside the range is not yet established. A later close back inside and failure to reclaim the boundary would weaken that interpretation.

### Worked comparison — a spike needs a fair baseline

A volume bar of 1,500 appears large. Against a baseline of 500, it is 3×. Against a baseline of 1,300, it is only about 1.15×. The bar did not change; the comparison did. This is why you should inspect whether the baseline uses comparable bars and whether a session-opening burst is normal. Relative volume is a measure built from a choice, so record the choice as part of the analysis.

### Level 1 — Notice (easy)

**Task:** A bar records 900 units and its baseline is 600. Calculate relative volume.

**Feedback:** 900 ÷ 600 = 1.5×, or 50% above the chosen baseline.

### Level 2 — Compare (guided)

**Task:** Two bars both show 1.5× relative volume, but one appears at the open and one at midday. Can you assume they are equally unusual?

**Feedback:** Not without checking the usual activity at those times. The calculation may be correct while the baseline remains poorly matched.

### Level 3 — Apply (independent)

**Task:** An up bar records 0.8× the baseline after a long advance. Write a neutral note and one thing to check next.

**Model response:** Price closed above its open with below-baseline activity. Check the location, session, source quality and follow-through before deciding whether the low reading matters.
### Common mistake

**Mistake:** Treating “high volume” as a complete interpretation.

**Correction:** Name the baseline, state the price result and locate the event before offering an explanation.

### Keep this

> When you call volume unusual, show the comparison that makes it unusual.

---

## Lesson 1.3 — Read the Story Inside a Candle: Wicks, Range and Closing Price

A candle contains more information than its colour, but it still does not tell the whole story. To read it consistently, separate three features: **range, close location and wicks**.

### 1. Range: how far price travelled

The range is the distance between the high and low.

\[
\text{Range}=\text{High}-\text{Low}
\]

A candle with a high of 104 and a low of 96 has a range of 8. Compare that with the recent bars on the same timeframe. An 8-point range may be large on one instrument and tiny on another.

### 2. Close location: where the bar finished

The close can be near the high, near the low or somewhere in between. One way to describe its position is:

\[
\text{Close position}=\frac{\text{Close}-\text{Low}}{\text{High}-\text{Low}}\times100\%
\]

Imagine a bar with high 104, low 96 and close 102. Its close position is (102 − 96) ÷ (104 − 96) = 75%. The bar closed three-quarters of the way up its range. That is more precise than simply calling it “strong”.

If high and low are identical, the range is zero and this calculation is undefined; describe the bar directly instead.

### 3. Wicks: where price travelled but did not finish

An upper wick means price traded above the close but did not finish at the high. A lower wick means price traded below the close but did not finish at the low. This can be useful evidence of a move that did not fully hold.

But a wick does not prove that a level was rejected by a particular group of traders. It could arise in different contexts, including brief volatility, two-sided trade or a response to new information. The location and follow-through matter.

### Work through the candle

Use this **synthetic** bar:

| Open | High | Low | Close | Volume vs baseline |
|---:|---:|---:|---:|---:|
| 100 | 104 | 96 | 102 | 1.4× |

- The close is above the open, so the candle closed up.
- The total range is 8.
- The close sits 75% of the way from the low to the high.
- There is an upper wick because the high is above the close, and a lower wick because the low is below the open.
- Recorded volume was 1.4× the chosen baseline.

These facts suggest a wide bar with an upward close in the upper part of the range, but with movement on both sides of the open. The volume shows elevated activity. Whether this matters depends on whether the bar occurred at a relevant level, inside a range, during a trend or in unusual market conditions.

### Worked comparison — same range, different close

Two bars both range from 90 to 100. One closes at 99; the other at 92. Their ranges are identical, but the first close is 90% of the way from low to high and the second is only 20%. The close location describes how much of the range was retained by the end of the interval. Neither number alone says whether the next bar will rise or fall; location and subsequent price behaviour still matter.

### Level 1 — Notice (easy)

**Task:** For Open 100, High 104, Low 96, Close 102, calculate the range and close position.

**Feedback:** The range is 8; close position is (102 − 96) ÷ 8 = 75%.

### Level 2 — Compare (guided)

**Task:** Compare that candle with one using the same high and low but closing at 97. What changed?

**Feedback:** The second close is near the low rather than the upper part of the range. The total range is unchanged, and neither bar identifies participant motives.

### Level 3 — Apply (independent)

**Task:** A wide candle at resistance has a long upper wick and elevated volume. Give an objective description, a possible interpretation and an alternative.

**Model response:** Price traded above its close but did not finish at the high; activity was elevated. A failed attempt is possible, but a pause before another attempt is also possible.
### Common mistake

**Mistake:** Memorising “long upper wick means selling” and “long lower wick means buying.”

**Correction:** Describe the journey and closing result first. Treat any explanation as a hypothesis that needs context and follow-through.

### Keep this

> A candle is a record of a price interval, not a verdict on what comes next.

---

## Lesson 1.4 — When Price Moves on Low Volume: Opportunity or Warning Sign?

Low volume is often described as though it has a fixed meaning: a quiet pullback is “healthy”, or a move on low activity is “weak”. Neither statement is reliable without context.

The first question is whether the low reading is unusual **for this instrument, timeframe and session**. Once that is established, ask what price achieved while the activity was relatively low.

### Two situations that can look similar

**Situation A — A pullback in a rising market.** Price has made an upward advance, then moves back towards a prior breakout area. The pullback candles are relatively small and activity declines against recent comparable bars. This may fit the idea that the move against the trend is meeting less participation than the earlier advance. It does not prove that the upward trend will resume: the pullback can continue, or new information can change the market.

**Situation B — Price travels quickly through a thin area.** Price moves through a region where little recent trading occurred, and recorded activity is modest. It may move quickly because there is little two-sided business at those prices. That does not make the move safe or durable. Price can accelerate in either direction and later reverse.

Now compare both with a third possibility: the data source is incomplete or the time period is normally quiet. A low figure caused by a feed limitation or expected session lull should not be mistaken for meaningful market behaviour.

### What to compare

| Question | Why it matters |
|---|---|
| Is the low activity unusual against a fair baseline? | Prevents interpreting a normal quiet period as a signal. |
| How far did price move? | Distinguishes low activity with little progress from low activity with substantial travel. |
| Where did the move occur? | A pullback to a prior boundary differs from movement in the middle of a range. |
| What happened on the next test? | Helps judge whether the move held, stalled or was reversed. |
| Is the volume feed appropriate? | A proxy or partial feed can create a misleading comparison. |

### Worked example

An instrument rises from 100 to 110 on expanding activity, then pulls back from 110 to 107 on lower activity. The old breakout area is around 106.5–107.0. A reasonable hypothesis is that the pullback is currently less active than the advance and has reached an area worth watching.

Do not call this an entry yet. If price stabilises around the area and then retakes a nearby short-term swing high, the continuation idea gains evidence. If price pushes through 106.5 with expanding downside range and fails to reclaim the area, the idea weakens. If price simply overlaps between 107 and 108, the situation may be unresolved.

### Worked comparison — low activity, different outcomes

Two pullbacks both show falling volume. In the first, price retreats from 110 to 107, holds a prior breakout zone near 106–107 and later reclaims a short-term high. In the second, price slips through the zone, breaks a meaningful swing low and fails to reclaim it. The starting clue—lower activity—was similar. The structural result differed. A volume-only rule would miss that distinction and could encourage a trade before price has shown what the pullback means.

### Level 1 — Notice (easy)

**Task:** A market rises from 100 to 110, then pulls back to 107 on below-baseline volume. List three observations.

**Feedback:** The advance covered 10 points, the pullback covered 3, and pullback volume is below the selected baseline. Whether the zone holds is unknown.

### Level 2 — Compare (guided)

**Task:** Compare this with a low-volume pullback that breaks a meaningful swing low and continues lower. Why is low volume not enough to call a pullback healthy?

**Feedback:** The price-structure outcome differs. Volume needs to be read alongside progress and location.

### Level 3 — Apply (independent)

**Task:** A quiet pullback reaches a prior breakout area without producing a trigger. State the next evidence to watch and one event that weakens continuation.

**Model response:** A hold followed by a reclaim of a short-term swing high may support continuation. A break below the pullback low and failed reclaim weakens it.
### Common mistake

**Mistake:** Treating low volume as proof that the opposing side is absent.

**Correction:** Lower recorded activity tells you about the data in that interval, not which participants are present or what they intend.

### Keep this

> Low activity is a clue to investigate alongside price progress and location. It is not a direction by itself.

---

## Lesson 1.5 — Which Volume Can You Trust? Understanding Data Across Different Markets

Volume is not measured in exactly the same way across every market. A reading can only be interpreted responsibly when you know what the feed represents.

### Different markets, different data

**Exchange-traded shares and futures:** The feed may report transactions on a defined exchange or set of venues. Confirm which contract or listing you are studying and whether the data is complete for your intended comparison.

**Spot foreign exchange:** The global spot FX market is decentralised. Many retail feeds report tick volume, which counts price updates rather than the total number of units traded across the market. Tick activity can still be useful for comparisons within the same feed, but it is not a universal count of global FX turnover.

**Contracts for difference (CFDs):** Volume can be broker-specific or derived from the provider's feed. A different provider may produce a different series.

**Cryptocurrency:** Trading is split across exchanges, products and markets. Volume from one spot exchange is not automatically representative of all spot venues or futures activity. Check whether the chart is showing spot, perpetual futures, dated futures or an aggregate.

The point is not that one category is always good and another is always useless. It is that each series has a scope. Interpret it within that scope.

### The comparison rule

Avoid making a claim such as “volume today is twice normal” until you know what “normal” means for that data series. Keep the instrument, timeframe, venue or feed, and session consistent. For intraday comparisons, time of day can matter. When a futures contract changes or rolls, its activity profile may change too.

If you switch feed, broker or instrument, reassess your baseline. Do not carry a numerical threshold from one data source into another without checking that the meaning and scale remain comparable.

### A practical data note

Before interpreting a volume pattern, be able to complete this sentence:

> “This chart uses ______ volume for ______ instrument, on the ______ timeframe, from ______ feed/venue. I compare it with ______ comparable bars over ______ period.”

If you cannot complete the sentence, your analysis may still describe the price behaviour, but its volume claims need qualification.

### Worked comparison — the data source changes the claim

Suppose a currency chart's tick activity is twice its own recent baseline. That supports the statement “tick activity on this feed is unusually high.” It does not establish that total global FX turnover doubled. Similarly, a crypto venue's reported volume describes that venue/instrument series, not every market where the asset trades. A credible note names the feed and keeps the conclusion within what the data actually measures.

### Level 1 — Notice (easy)

**Task:** A retail FX feed says its volume measure counts tick updates. What does this series measure?

**Feedback:** It measures tick activity on that feed, not total traded quantity across the global FX market.

### Level 2 — Compare (guided)

**Task:** Compare retail FX tick activity with exchange-reported futures volume. Why should you not compare their raw numbers directly?

**Feedback:** They may count different things and cover different markets; baselines and numeric thresholds are not automatically transferable.

### Level 3 — Apply (independent)

**Task:** Write a data note for a crypto pair shown on one exchange.

**Model response:** State the venue, instrument, timeframe and method, and clarify that the data does not represent every spot and derivatives venue. Compare activity within that defined series.
### Common mistake

**Mistake:** Comparing raw volume numbers from two feeds as if they were measured on the same basis.

**Correction:** Compare like with like. When the source changes, revisit your interpretation and baseline.

### Module 1 review

You now have a repeatable first pass for reading a bar:

1. Describe its price range, close and wicks.
2. Compare recorded activity with a stated baseline.
3. Place the event in the surrounding structure.
4. State an interpretation as a possibility, not as a fact.
5. Name the next behaviour that would strengthen or weaken it.
6. Record any limitation in the volume data.

### Quick check

**1. What does relative volume measure?**  
The current reading compared with a specified baseline. It does not directly measure directional pressure.

**2. Does a long wick prove rejection?**  
No. It records a price excursion that was not retained at the close. Location and later behaviour are needed to interpret it.

**3. Why identify the feed before using volume?**  
Because the feed may represent traded quantity, tick activity or venue-specific volume. The meaning and comparability depend on the source.

**Transfer task:** Choose a chart you follow. Write three separate notes: one visible price fact, one volume fact with its baseline, and one uncertainty. Do not write an entry or a forecast. Your goal is to practise accurate observation before interpretation.
