# Module 5 — Find the Price Levels Worth Watching
## Teaching manuscript · First production pass

> **Production status:** Draft for editorial review.
>
> **Teaching approach:** Introduce volume-at-price as a map of where activity occurred, then interpret it through acceptance, rejection and changing value. The structure draws on the market-profile/auction perspective in Dalton and the broader volume-analysis treatment in Dormeier, while distinguishing profile measures from ordinary volume bars. This is original instructional synthesis.

---

## Lesson 5.1 — Where Has the Market Traded Most? Introducing Volume Profile

### Learning objective
Explain the difference between volume through time and volume at price, and read a basic profile without treating it as an automatic support/resistance system.

### Outline and timing
- **0:00–1:00 — Why a histogram beneath candles cannot answer every question.**
- **1:00–3:00 — Volume through time versus volume distribution by price.**
- **3:00–5:00 — What a profile represents and how the period is selected.**
- **5:00–7:30 — High-activity and low-activity areas.**
- **7:30–10:30 — ChartLab: read a simple profile.**
- **10:30–11:00 — Recap.**

### Full narration script
So far, we have mainly studied volume through time: a bar tells us how much activity was recorded during a particular interval. That is useful for asking what happened as price moved. But another question matters too: at which prices did the market conduct more or less activity over a chosen period? Volume Profile is a way of visualising that distribution.

On a conventional chart, volume bars usually sit beneath the candles. The horizontal position of each bar tells you when activity occurred. A volume profile is oriented differently: it groups activity by price level and displays it horizontally. The resulting shape lets you see where more volume was associated with trading, and where less was associated with trading, during the selected period and under that platform's calculation rules.

The distinction is important. A tall volume bar at 10:30 says activity was high during that time interval. A wide profile row around a particular price says more activity was assigned to that price level over the selected profile period. These are related but different questions. One describes activity through time; the other describes its distribution across price.

The profile depends on settings. You need to know whether you are looking at a session profile, a fixed-range profile drawn across a chosen period, or a composite profile that combines multiple sessions. You also need to know which instrument and volume field the tool uses. Profiles built from exchange-traded volume have a different data basis from profiles derived from tick data or broker-specific feeds. The histogram is a model of the selected data and period, not a complete map of everyone's orders or beliefs.

A simple profile commonly shows wider areas where more activity occurred and thinner areas where less activity occurred. The wider regions are often called high-volume nodes; thinner regions are called low-volume nodes. These terms describe the shape, not a guaranteed future reaction. A high-volume area may be associated with extensive two-sided trade and acceptance during the measured period. A low-volume area may represent price levels the market moved through quickly, but the meaning depends on the path and market conditions.

Think of an auction. A price level where many transactions occur has had more activity than a price level the market crossed quickly. Traders sometimes interpret the first as an area of agreement or balance, and the second as an area where the auction found less sustained activity. That is an explanatory model, not proof that every participant agreed on a single fair value. Prices can return to former low-volume areas; high-volume areas can be crossed decisively when conditions change.

How should a beginner use this? Begin by selecting a relevant period and asking where the profile is concentrated. Where is the widest region? Are there thinner sections between broader areas? How does current price relate to the profile? Is price inside a region of past activity, testing its edge, or moving away from it? Then return to ordinary price analysis: what do the candles, swings and volume-through-time say at that location?

Avoid drawing too much from a profile that covers an arbitrary period. A profile from the last five sessions tells a different story from one that includes several months. A profile from a single news-driven session may be distorted by temporary conditions. The selection must relate to the question. For a breakout analysis, a profile of the range that preceded the breakout may be useful. For broader context, a longer composite may be worth examining. State your selection and keep it consistent for the exercise.

In a chart review, do not begin with a claim like “price must bounce at this node.” Begin with the map: “This profile has a concentration of activity around the marked zone, and current price is approaching its upper edge.” Then describe the response as price arrives. Does it stall, rotate, break through, or accept beyond it? That is how the profile becomes part of a decision process rather than a collection of lines.

Volume Profile answers where activity was concentrated in a particular period. It does not, by itself, tell you whether the next move will rise or fall. Its value is in mapping the context in which price will be interpreted. Use it to frame the question, and use current price behaviour to assess the answer.

### Knowledge check
1. What question does volume through time answer, and what question does Volume Profile answer?
2. Why must the selected profile period be stated?
3. Why is a high-volume node not automatically support or resistance?

<!-- ASSET: Create a teaching graphic with the same synthetic price series shown once with vertical volume bars (activity by time) and once with a horizontal volume profile (activity by price). Label selected period and data source. -->
<!-- CHARTLAB: Learner chooses a stated profile window, identifies two concentration areas and one thinner area, then describes current price location without predicting a bounce or breakout. Ask what additional price evidence is needed. -->

---

## Lesson 5.2 — Finding the Market's Reference Point: Point of Control and Value Area

### Learning objective
Define the Point of Control and Value Area as profile statistics, explain their dependence on settings, and use them as context rather than fixed trade signals.

### Outline and timing
- **0:00–1:00 — Why the profile needs reference points.**
- **1:00–3:00 — Point of Control: the price row with the most assigned volume.**
- **3:00–5:00 — Value Area: a platform-defined range containing a chosen share of volume.**
- **5:00–7:30 — Interaction with current price.**
- **7:30–10:30 — ChartLab: compare two profiles.**
- **10:30–11:00 — Recap.**

### Full narration script
Once a profile is visible, traders often want a few reference points to help describe its structure. Two commonly used terms are Point of Control and Value Area. They are useful, but only if we know exactly what they represent and avoid treating them as magical prices.

The Point of Control, or POC, is generally the price row with the greatest volume assigned to it within the selected profile. In everyday language, it is the profile's largest concentration row. This makes it a useful reference for where the most activity occurred in that period. It does not automatically mean that the market will return to that price, that it represents a universally agreed fair value, or that it must act as support or resistance.

The Value Area is a range that contains a specified percentage of profile volume according to the platform's method. Many platforms use a convention such as 70 percent, but the percentage and calculation method should be checked rather than assumed. The upper and lower boundaries are commonly called Value Area High and Value Area Low. They outline a central region of activity under that calculation. The area is descriptive: it summarises where volume was concentrated during the chosen period.

These reference points depend on the profile settings. Change the period and the POC may move. Change the data source or row size and the shape can change. A session profile may tell a different story from a composite profile spanning several weeks. The numbers should therefore be used consistently and their origin noted. If you are comparing profiles, do not change the settings midway through the comparison without acknowledging it.

How can these levels inform chart reading? Suppose price is currently inside a value area formed during a multi-session range. That may help you recognise that current price remains within a region of past activity. If price moves above Value Area High and holds outside the area, it may be evidence that the market is exploring prices beyond the earlier concentration. If it repeatedly returns inside, the breakout or acceptance hypothesis is less compelling. The key is what price does around the boundary—not simply whether it is above or below the line.

The POC can be useful as a reference during rotations. If price is trading away from the POC and later returns toward it, you can observe whether activity and price stabilise around the area or pass through it quickly. A return is not guaranteed. Markets can trend away from a previous concentration when information or conditions change. Likewise, the POC can be crossed repeatedly and have little practical significance if the selected period is poorly chosen.

A beginner mistake is to treat Value Area High as resistance and Value Area Low as support in all contexts. Those levels can be reference points, but they are not walls. When a market is balanced, the value-area boundaries may help frame tests and rotations. When a market is trending, the previous value area may be left behind, and its relevance can change. Ask whether the market is currently rotating within a distribution or developing away from it.

Combine the profile with the price structure. Mark the profile period, POC, Value Area High and Value Area Low. Then mark the current swing structure and any obvious prior range boundaries. If the profile and price structure point to the same zone, that overlap can be worth watching. It is not a mathematical guarantee that the zone is stronger; it simply gives the analyst a coherent reason to pay attention.

In the ChartLab, two profiles will be built from different periods of the same synthetic market. The POC and value boundaries will differ. The learner must explain why both can be valid descriptions of their respective windows and why neither can be used as a stand-alone prediction. This helps demonstrate that a profile is contextual information, not an immutable property of the instrument.

Your takeaway is to define these levels correctly before interpreting them. POC tells you the profile's largest concentration row. The Value Area marks a range containing a chosen share of volume under a stated calculation. Their practical meaning comes from the selected period, the wider structure and the market's response when price interacts with them.

### Knowledge check
1. What exactly does the Point of Control identify?
2. Why can two valid profile windows produce different POCs and Value Areas?
3. What price behaviour would help you evaluate acceptance outside the Value Area?

<!-- ASSET: Produce a single profile diagram labelling POC, Value Area High/Low and the chosen volume percentage. Add a second panel with a different selected range to show the reference points can change. -->
<!-- CHARTLAB: Learners mark POC and value boundaries on two profiles using the same synthetic price series but different windows. They answer “What can this tell me?” and “What can it not tell me?” before seeing price continuation. -->

---

## Lesson 5.3 — Where Price May Stall — or Move Quickly: High- and Low-Volume Nodes

### Learning objective
Interpret high- and low-volume nodes as areas of prior activity concentration or relative thinness, then construct conditional scenarios around them.

### Outline and timing
- **0:00–1:00 — Profile shape as a map, not a forecast.**
- **1:00–3:00 — High-volume nodes and concentrated activity.**
- **3:00–5:00 — Low-volume nodes and thinner activity.**
- **5:00–7:30 — Current interaction and alternative outcomes.**
- **7:30–10:30 — ChartLab: map a potential path.**
- **10:30–11:00 — Recap.**

### Full narration script
A profile often contains broad bulges and thinner sections. The broad bulges are commonly described as high-volume nodes; the thinner sections are commonly described as low-volume nodes. Their value is not that one means “bounce” and the other means “break through.” Their value is that they summarise how activity was distributed over a particular period and give you useful context for observing current price behaviour.

A high-volume node is a price area where the profile assigns relatively more volume. During the profile period, the market conducted more activity there than at neighbouring price areas. One interpretation is that the market spent time doing business around that zone, perhaps rotating repeatedly as participants were willing to transact there. Such a zone may become an area of attention when price returns. It may slow, rotate, pass through, or reject. None is guaranteed.

A low-volume node represents a relatively thinner area in the distribution. It may have formed where price moved through a region quickly or where less activity was recorded. Some traders watch these areas because price can sometimes move rapidly through relatively thin regions until it reaches a broader concentration. But a low-volume node is not an empty space, and it does not guarantee acceleration. New information, orders or liquidity conditions can change the response entirely.

The profile also needs a time context. A high-volume node that formed months ago may not matter as much to current intraday decisions as one formed in a recent, relevant balance. Conversely, a major composite profile may remain useful for broader structure. The relevance depends on the question and timeframe. Use a profile window that corresponds to the event you are investigating, and do not stack so many profiles that every price becomes surrounded by a supposed node.

Consider current price approaching the upper edge of a high-volume node after a trend move. One scenario is rotation back through the area if the market returns to prior balance. Another is rejection from the node's edge and continuation away. A third is a clean break through the area followed by sustained trade beyond it. The node itself does not choose the scenario. Price behaviour as it enters, travels through and exits the region provides the next evidence.

Now consider a low-volume node between two broad areas. If price enters the thin region with a wide directional bar and continues to make progress, movement may be relatively quick. But if price stalls, creates overlapping bars and fails to leave the region, the expected “fast move” is not happening. Update the hypothesis. You should never keep predicting a rapid traverse simply because a profile is thin where price currently sits.

A helpful framework is to observe four things. First, the profile structure: where does the node begin and end? Second, the approach: is price arriving with strong directional progress or in a compressed range? Third, the response within the node: is price accepted, rejected or moving through? Fourth, the next area: what would be the logical reference if price exits the node? This avoids treating profile lines in isolation and makes your chart notes actionable.

There is another subtlety: the node is a summary of past activity, not a display of current resting orders. It does not tell you that there are still buyers waiting at a high-volume node or that no orders remain in a low-volume node. Some traders confuse historical trade distribution with order-book depth. They are different forms of information. A profile shows past activity according to its data and calculation rules; it does not reveal every current order or participant's intent.

For a ChartLab, use a profile with two high-volume nodes connected by a low-volume area. Freeze price before it enters the low-volume region. Ask the learner to define a scenario if directional progress continues, and an alternative if price stalls. Then show one path where price moves rapidly through and another where it does not. This exercise reinforces that profile shape offers a map of historical activity, not a promise about the future.

High- and low-volume nodes can help you organise the chart and identify areas that deserve attention. Their interpretation must remain conditional. Let the profile define the area and let current price action determine whether the market appears to be rotating, rejecting or moving through it.

### Knowledge check
1. What does a high-volume node describe?
2. Why might a low-volume node be crossed quickly, and why is that not guaranteed?
3. How does a profile differ from a live order book?

<!-- ASSET: Draw a two-bulge profile with a low-volume connection and an overlaid synthetic price path. Create two alternate outcomes: rapid traversal and failed traversal. -->
<!-- CHARTLAB: Before revealing the outcome, learners identify node boundaries, write a continuation scenario and a stall/rejection alternative, then list observable evidence that would favour each. Debrief the limits of historical volume distribution. -->

---

## Lesson 5.4 — When the Market's Focus Shifts: Reading Changes in Value

### Learning objective
Compare profiles across periods and describe value migration as evidence of changing activity concentration without treating it as an automatic directional signal.

### Outline and timing
- **0:00–1:00 — Markets can move their area of activity.**
- **1:00–3:00 — Compare profile periods consistently.**
- **3:00–5:00 — Value moving higher, lower or remaining balanced.**
- **5:00–7:30 — Combine migration with price behaviour.**
- **7:30–10:30 — ChartLab: identify developing change.**
- **10:30–11:00 — Recap.**

### Full narration script
A market's most active price area does not have to remain fixed. As price moves and trading activity develops, a new profile can form at higher or lower prices. Traders who use Market Profile or Volume Profile often pay attention to this change because it can describe whether activity is being concentrated somewhere different from the previous period. The important point is to treat it as a description of changing behaviour, not as a signal that automatically predicts the next move.

Imagine a market spends the morning trading around one price region. Later, price breaks upward and the afternoon's activity becomes concentrated at higher prices. Compared with the morning profile, the centre of activity has migrated upward. That may be consistent with the market accepting higher prices during the later period. But the conclusion is limited: it describes where activity occurred, not whether the price increase is permanent or fundamentally justified. A later session may return to the earlier region.

Value migration requires comparable periods. If you compare a two-hour profile with a full-day profile, the difference might reflect the length of the window rather than a meaningful shift. Try comparing adjacent sessions or consistent intraday segments and record the profile settings. Beware of a new profile that is still forming; its POC and boundaries can move while the session develops. A developing reference is not the same thing as a completed one.

Describe the pattern in neutral terms. “The POC has shifted higher over three comparable sessions, and each session has spent more activity in a higher range” is a useful observation. “Buyers have permanently taken control” is an unsupported conclusion. To assess the bullish interpretation, look at the price structure: are swing highs and lows advancing? Does price hold above the prior value area? Do pullbacks find acceptance at higher prices or return to the previous distribution? This provides context for what the migrating profile may mean.

Downward migration works similarly. If successive profiles concentrate at lower prices, that may be consistent with the market conducting more activity lower over time. Yet value can move lower during a broad range rotation, a temporary event, or an orderly pullback within a larger uptrend. The timeframe matters. A lower intraday value area does not automatically negate a higher-timeframe uptrend. Make sure your conclusion matches the horizon you are analysing.

What if the POC moves but the overall profile overlaps heavily with the previous session? That may be a small shift within an otherwise balanced environment rather than a decisive change in character. Conversely, a profile that develops well outside the prior value area and holds there may be more meaningful, especially if price structure supports the shift. There is no universal threshold for what counts as a significant migration. Define a consistent comparison method and test it against the instrument and timeframe.

Value migration can also be incomplete or mixed. The POC may shift up while the Value Area overlaps with the prior period. Or price can move sharply higher but activity later concentrates back lower. Rather than forcing a simple bullish/bearish label, describe what each measure says. Ask whether the market is trending, balancing at a new area, or rotating back into a previous region. The ability to say “mixed evidence” is an analytical skill, not a failure.

In the ChartLab, show three consecutive synthetic session profiles. The first concentrates around a lower range, the second overlaps and extends higher, and the third either continues higher or rotates back. Have learners compare POC, value boundaries, overlap and price swing structure. Reveal two endings so students see that a migrating profile can precede further movement or temporary failure.

Value migration helps answer: where is the market doing more business now relative to before? It can support a reading of acceptance at different prices when combined with structure, but it does not predict future movement by itself. Keep the comparison consistent and let actual price behaviour determine whether the change persists.

### Knowledge check
1. What does a rising POC across comparable sessions describe?
2. Why should profile periods and settings be comparable?
3. What price behaviour would support the interpretation that higher prices are being accepted?

<!-- ASSET: Three comparable session profiles with POC and value boundaries; create upward-migration, downward-migration and overlapping/balanced variants. -->
<!-- CHARTLAB: Learners compare sessions by recording POC movement, value-area overlap, price swings, and whether price stayed outside prior value. They must distinguish observation (“value shifted”) from thesis (“market may be accepting higher/lower prices”). -->

---

## Lesson 5.5 — Putting It Together: Combining Volume Profile, VWAP and Price Action

### Learning objective
Explain what Volume Profile and VWAP each measure, use them as complementary context, and avoid treating confluence as automatic confirmation.

### Outline and timing
- **0:00–1:00 — Different tools, different questions.**
- **1:00–3:00 — Profile distribution versus average price weighted by volume.**
- **3:00–5:00 — Select a relevant timeframe and context.**
- **5:00–7:30 — Confluence and conflicting information.**
- **7:30–10:30 — ChartLab: build a combined level map.**
- **10:30–11:00 — Recap.**

### Full narration script
Volume Profile and VWAP often appear together on trading charts, but they measure different things. Volume Profile maps how activity was distributed across price over a selected period. VWAP, or Volume Weighted Average Price, calculates an average price weighted by volume over a defined period. One describes a distribution; the other provides a volume-weighted reference average. Treating them as interchangeable can lead to confused analysis.

A profile might show that the largest concentration of activity occurred around a particular price zone, with thinner areas above and below. VWAP gives you a running average that changes as more data enters the chosen period. Intraday traders often use session VWAP as a reference for where current price sits relative to the session's volume-weighted average. Other implementations may anchor VWAP to a chosen event or swing. Settings matter. Know whether the tool resets each session, uses a custom anchor, or follows another platform-specific convention.

Neither tool tells you what should happen next. Price above session VWAP does not guarantee an advance; price below it does not guarantee decline. A high-volume node does not guarantee a bounce, and a low-volume node does not guarantee acceleration. Their value is in helping describe the environment in which current price action is unfolding.

Imagine price is approaching a prior range high that also aligns with the upper edge of a recent profile's high-activity area. Session VWAP sits below price. One possible interpretation is that price has moved upward and is testing a significant area above the session average. The next question is whether the market can remain beyond the boundary. If price breaks and holds above the area, the combined map may help you identify a reference for a retest. If price rejects the boundary and returns into the range, the same alignment helps you understand where the failed attempt occurred. The tools help organise the chart; price response decides which scenario gains evidence.

Confluence is often misunderstood. When support from several tools overlaps, it can provide a clearer area to watch. But it is not necessarily three independent pieces of evidence. A profile, VWAP and moving average may all be derived from the same price-and-volume history. Their overlap may be useful, but stacking indicators does not automatically multiply the probability of success. You need to understand the role of each tool and whether it adds genuinely new information to the decision.

Start by selecting one primary structure: trend, range or transition. Mark the most relevant swing levels and boundaries. Add one profile suited to the question—perhaps the range before a breakout, the current session, or a clearly defined composite. Identify the POC, value boundaries and any meaningful nodes. Then add VWAP with its anchor stated. Finally, observe current price: is it accepted above a level, rejected from it, or moving through without much pause? Note where the evidence conflicts.

An example of conflicting evidence might be price above session VWAP while approaching the upper edge of a high-volume node and failing to make further progress. A simplistic system might say “above VWAP, bullish.” A structured reader recognises that price is above the average but at a location where progress has stalled. Both facts matter. The correct action may be to wait for a resolution rather than choose whichever indicator agrees with the desired trade.

The other crucial issue is timeframe alignment. A session VWAP is an intraday reference; a multi-week composite profile is broader context. They can both be displayed, but do not assume they answer the same question. Explain why each is on the chart and how it should affect the scenario. If you cannot state its purpose, remove it. A compact chart with one clear profile and a relevant VWAP is often more useful than a crowded chart with many overlapping references.

The ChartLab should ask learners to build a level map and write a conditional scenario—not issue an immediate buy/sell verdict. For example: “Price is above session VWAP but has stalled at the prior range edge near the top of a high-activity area. A sustained hold above the range would support an acceptance hypothesis; return inside and a failed reclaim would support a rejection hypothesis.” This is useful because it respects all the information without pretending the tools can eliminate uncertainty.

Your goal is to make the tools work for the analysis, not to make the analysis obey the tools. Volume Profile tells you where activity was concentrated. VWAP tells you how current price compares with a volume-weighted average over a specified period. Price structure and follow-through show how the market is responding now. Together they can improve context, but the complete trading decision still requires a defined thesis, invalidation and risk plan.

### Knowledge check
1. How do Volume Profile and VWAP differ?
2. Why is confluence not automatically independent confirmation?
3. What should you do when price is above VWAP but fails at an important profile/structure area?

<!-- ASSET: Create a clean chart with one stated profile window, POC, value boundaries, one VWAP line with session/anchor identified, and price structure. Include an alternate outcome where confluence fails. -->
<!-- CHARTLAB: Learners build a five-layer map: regime, key structure, profile period, profile references, VWAP anchor. They then write bullish and bearish conditional scenarios and one invalidation for each. Discourage “three indicators agree, so enter” reasoning. -->

---

## Module 5 instructor notes

- Always state profile period, data source and value-area settings.
- Explain historical profile activity versus current resting liquidity; these are different data types.
- Do not describe POC, value boundaries, nodes or VWAP as guaranteed support/resistance.
- Reference themes: Dalton and colleagues on market-generated information, balance and initiative/responsive activity; Dormeier on broader volume analysis and volume-based tools.
