# Module 5 — Find the Price Levels Worth Watching
## Teaching manuscript · First production pass

> **Production status:** Draft for editorial review.
>
> **Teaching approach:** Introduce volume-at-price as a map of where activity occurred, then interpret it through acceptance, rejection and changing value. The structure draws on the market-profile/auction perspective in Dalton and the broader volume-analysis treatment in Dormeier, while distinguishing profile measures from ordinary volume bars. This is original instructional synthesis.

---

## Lesson 5.1 — Where Has the Market Traded Most? Introducing Volume Profile

### Learning objective
Explain the difference between volume through time and volume at price, and read a basic profile without treating it as an automatic support/resistance system.

**Beginner checkpoint:** The learner can explain the main idea in everyday words, point to the evidence on a chart, and say what could change their mind.

**Target delivered duration:** 12–16 minutes normally; hard minimum 10 minutes, usual upper limit 20 unless the concept requires more. Include narration, a narrated chart walkthrough, progressive learner practice, feedback and recap. Rehearse and time the complete lesson; outline timings are targets, not proof of runtime.

### Outline and timing
- **0:00–1:00 — Why a histogram beneath candles cannot answer every question.**
- **1:00–3:00 — Volume through time versus volume distribution by price.**
- **3:00–5:00 — What a profile represents and how the period is selected.**
- **5:00–7:30 — High-activity and low-activity areas.**
- **7:30–10:30 — ChartLab: read a simple profile.**
- **10:30–11:00 — Recap.**

### Full narration script
So far, we have mainly studied volume through time: a bar tells us how much activity was recorded during a particular interval. That is useful for asking what happened as price moved. But another question matters too: at which prices did the market conduct more or less activity over a chosen period? Volume Profile is a way of showing that distribution. It uses a horizontal shape so you can see which prices had more or less recorded activity during the time period you chose.

On a conventional chart, volume bars usually sit beneath the candles. The horizontal position of each bar tells you when activity occurred. A volume profile is oriented differently: it groups activity by price level and displays it horizontally. The resulting shape lets you see where more volume was associated with trading, and where less was associated with trading, during the time period you chose and under that platform's calculation rules.

The distinction is important. A tall volume bar at 10:30 says activity was high during that time interval. A wide profile row around a particular price says more activity was assigned to that price level over the selected profile period. These are related but different questions. One describes activity through time; the other describes its distribution across price.

The profile depends on settings. You need to know whether you are looking at a session profile, a fixed-range profile drawn across a chosen period, or a composite profile that combines multiple sessions. You also need to know which instrument and volume field the tool uses. Profiles built from exchange-traded volume have a different data basis from profiles derived from tick data or broker-specific feeds. The histogram is a model of the selected data and period, not a complete map of everyone's orders or beliefs.

A simple profile commonly shows wider areas where more activity occurred and thinner areas where less activity occurred. The wider regions are often called high volume nodes; thinner regions are called low volume nodes. These terms describe the shape, not a guaranteed future reaction. A high volume area may be associated with extensive two-sided trade and acceptance (price staying beyond a level instead of quickly coming back) during the measured period. A low volume area may represent price levels the market moved through quickly, but the meaning depends on the path and market conditions.

Think of an auction. A price level where many transactions occur has had more activity than a price level the market crossed quickly. Traders sometimes interpret the first as an area of agreement or balance, and the second as an area where the auction found less sustained activity. That is an explanatory model, not proof that every participant agreed on a single fair value. Prices can return to former low volume areas; high volume areas can be crossed decisively when conditions change.

How should a beginner use this? Begin by selecting a relevant period and asking where the profile is concentrated. Where is the widest region? Are there thinner sections between broader areas? How does current price relate to the profile? Is price inside a region of past activity, testing its edge, or moving away from it? Then return to ordinary price analysis: what do the candles, swings and volume-through-time say at that location?

Avoid drawing too much from a profile that covers an arbitrary period. A profile from the last five sessions tells a different story from one that includes several months. A profile from a single news-driven session may be distorted by temporary conditions. The selection must relate to the question. For a breakout analysis, a profile of the range that preceded the breakout may be useful. For broader context, a longer composite may be worth examining. State your selection and keep it consistent for the exercise.

In a chart review, do not begin with a claim like “price must bounce at this node.” Begin with the map: “This profile has a concentration of activity around the marked zone, and current price is approaching its upper edge.” Then describe the response as price arrives. Does it stall, rotate, break through, or accept beyond it? That is how the profile becomes part of a decision process rather than a collection of lines.

Volume Profile answers where activity was concentrated in a particular period. It does not, by itself, tell you whether the next move will rise or fall. Its value is in mapping the context in which price will be interpreted. Use it to frame the question, and use current price behaviour to assess the answer.

### Extended spoken case analysis — additional narration

A profile must be read as the result of a selected data series and a selected window. To make that concrete, put the same synthetic price path on screen and build a profile over the first half, then over the entire path. The shapes differ because the question and period differ. Neither is wrong; they describe different sets of activity. Ask students to write the window in the chart note. If they cannot tell what bars were included, they cannot interpret the profile responsibly. Explain the difference between a high-activity price region and a resting-order map: the profile summarises completed activity according to the tool's rules, whereas a live order book, where available, describes currently displayed orders and has its own limitations. The learner should return to price after identifying a node. Does price currently sit within that region, approach its edge, or travel through it? The response matters more than the node's shape alone. This exercise makes the profile a contextual map rather than a forecast machine and prevents the mistake of assuming every broad region must become future support or resistance.

### Learner progression — Notice → Compare → Apply

**Level 1 — Notice (easy):** Identify which display shows activity by time and which shows activity by price.

**Level 2 — Compare (guided):** Mark one broad and one thin area in a stated profile window; explain where more or less activity was recorded.

**Level 3 — Apply (independent):** Use a new profile with price arriving at one area and construct two possible reactions, making clear that the historical profile cannot guarantee either outcome.

**Reveal rule:** Keep later bars or the model outcome hidden until the learner has recorded the initial evidence and next condition.

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

**Beginner checkpoint:** The learner can explain the main idea in everyday words, point to the evidence on a chart, and say what could change their mind.

**Target delivered duration:** 12–16 minutes normally; hard minimum 10 minutes, usual upper limit 20 unless the concept requires more. Include narration, a narrated chart walkthrough, progressive learner practice, feedback and recap. Rehearse and time the complete lesson; outline timings are targets, not proof of runtime.

### Outline and timing
- **0:00–1:00 — Why the profile needs reference points.**
- **1:00–3:00 — Point of Control: the price row with the most assigned volume.**
- **3:00–5:00 — Value Area: a platform-defined range containing a chosen share of volume.**
- **5:00–7:30 — Interaction with current price.**
- **7:30–10:30 — ChartLab: compare two profiles.**
- **10:30–11:00 — Recap.**

### Full narration script
Once a profile is visible, traders often want a few reference points to help describe its structure. Two commonly used terms are Point of Control (the price row with the most recorded activity) and Value Area. They are useful, but only if we know exactly what they represent and avoid treating them as magical prices.

The Point of Control, or POC, is generally the price row with the greatest volume assigned to it within the selected profile. In everyday language, it is the profile's largest concentration row. This makes it a useful reference for where the most activity occurred in that period. It does not automatically mean that the market will return to that price, that it represents a universally agreed fair value, or that it must act as support or resistance.

The Value Area is a range that contains a specified percentage of profile volume according to the platform's method. Many platforms use a convention such as 70 percent, but the percentage and calculation method should be checked rather than assumed. The upper and lower boundaries are commonly called Value Area High and Value Area Low. They outline a central region of activity under that calculation. The area is descriptive: it summarises where volume was concentrated during the chosen period.

These reference points depend on the profile settings. Change the period and the POC may move. Change the data source or row size and the shape can change. A session profile may tell a different story from a composite profile spanning several weeks. The numbers should therefore be used consistently and their origin noted. If you are comparing profiles, do not change the settings midway through the comparison without acknowledging it.

How can these levels inform chart reading? Suppose price is currently inside a value area formed during a multi-session range. That may help you recognise that current price remains within a region of past activity. If price moves above Value Area High and holds outside the area, it may be evidence that the market is exploring prices beyond the earlier concentration. If it repeatedly returns inside, the breakout or acceptance (price staying beyond a level instead of quickly coming back) possible explanation is less compelling. The key is what price does around the boundary—not simply whether it is above or below the line.

The POC can be useful as a reference during rotations. If price is trading away from the POC and later returns toward it, you can observe whether activity and price stabilise around the area or pass through it quickly. A return is not guaranteed. Markets can trend away from a previous concentration when information or conditions change. Likewise, the POC can be crossed repeatedly and have little practical significance if the time period you chose is poorly chosen.

A beginner mistake is to treat Value Area High as resistance and Value Area Low as support in all contexts. Those levels can be reference points, but they are not walls. When a market is balanced, the value-area boundaries may help frame tests and rotations. When a market is trending, the previous value area may be left behind, and its relevance can change. Ask whether the market is currently rotating within a distribution or developing away from it.

Combine the profile with the the pattern made by recent highs and lows. Mark the profile period, POC, Value Area High and Value Area Low. Then mark the current swing structure and any obvious prior range boundaries. If the profile and the pattern made by recent highs and lows point to the same zone, that overlap can be worth watching. It is not a mathematical guarantee that the zone is stronger; it simply gives the analyst a coherent reason to pay attention.

In the ChartLab, two profiles will be built from different periods of the same synthetic market. The POC and value boundaries will differ. The learner must explain why both can be valid descriptions of their respective windows and why neither can be used as a stand-alone prediction. This helps demonstrate that a profile is contextual information, not an immutable property of the instrument.

Your takeaway is to define these levels correctly before interpreting them. POC tells you the profile's largest concentration row. The Value Area marks a range containing a chosen share of volume under a stated calculation. Their practical meaning comes from the time period you chose, the wider structure and what happens next when price interacts with them.

### Extended spoken case analysis — additional narration

The POC and Value Area are reference statistics, not universal fair-value markers. The POC answers which row has the highest assigned volume in the selected profile. The Value Area summarises a chosen share of the profile's total activity under a platform's method. If the profile period, row size, volume data or chosen percentage changes, the references may change too. This makes consistency important during study. In the lab, ask learners to compare two periods and explain why their POCs differ. It may be because the market did more business at a different price during the second period, or because the profile window includes new activity. The learner should not immediately infer that the market must revisit one POC or reject the other. Instead, observe the interaction: did price hold beyond the prior value area, return inside it, or move through the POC region without much pause? Keep the focus on how the market is behaving now. The profile provides a set of reference points based on past activity; it does not dictate what future participants will do.

### Learner progression — Notice → Compare → Apply

**Level 1 — Notice (easy):** Point out the Point of Control and Value Area on a labelled profile.

**Level 2 — Compare (guided):** Mark these references on two profiles created from different windows and identify what changed.

**Level 3 — Apply (independent):** Explain how the selected window and platform method affect a new profile reading; justify whether two profiles are comparable.

**Reveal rule:** Keep later bars or the model outcome hidden until the learner has recorded the initial evidence and next condition.

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

**Beginner checkpoint:** The learner can explain the main idea in everyday words, point to the evidence on a chart, and say what could change their mind.

**Target delivered duration:** 12–16 minutes normally; hard minimum 10 minutes, usual upper limit 20 unless the concept requires more. Include narration, a narrated chart walkthrough, progressive learner practice, feedback and recap. Rehearse and time the complete lesson; outline timings are targets, not proof of runtime.

### Outline and timing
- **0:00–1:00 — Profile shape as a map, not a forecast.**
- **1:00–3:00 — High-volume nodes and concentrated activity.**
- **3:00–5:00 — Low-volume nodes and thinner activity.**
- **5:00–7:30 — Current interaction and alternative outcomes.**
- **7:30–10:30 — ChartLab: map a potential path.**
- **10:30–11:00 — Recap.**

### Full narration script
A profile often contains broad bulges and thinner sections. The broad bulges are commonly described as high volume nodes; the thinner sections are commonly described as low volume nodes. Their value is not that one means “bounce” and the other means “break through.” Their value is that they summarise how activity was distributed over a particular period and give you useful context for observing current price behaviour.

A high volume node is a price area where the profile assigns relatively more volume. During the profile period, the market conducted more activity there than at neighbouring price areas. One interpretation is that the market spent time doing business around that zone, perhaps rotating repeatedly as participants were willing to transact there. Such a zone may become an area of attention when price returns. It may slow, rotate, pass through, or reject. None is guaranteed.

A low volume node represents a relatively thinner area in the distribution. It may have formed where price moved through a region quickly or where less activity was recorded. Some traders watch these areas because price can sometimes move rapidly through relatively thin regions until it reaches a broader concentration. But a low volume node is not an empty space, and it does not guarantee acceleration. New information, orders or liquidity (how easily a trade can be made without moving price much) conditions can change the response entirely.

The profile also needs a time context. A high volume node that formed months ago may not matter as much to current intraday decisions as one formed in a recent, relevant balance. Conversely, a major composite profile may remain useful for broader structure. The relevance depends on the question and timeframe. Use a profile window that corresponds to the event you are investigating, and do not stack so many profiles that every price becomes surrounded by a supposed node.

Consider current price approaching the upper edge of a high volume node after a trend move. One scenario is rotation back through the area if the market returns to prior balance. Another is rejection (price failing to stay beyond a level and moving back) from the node's edge and continuation away. A third is a clean break through the area followed by sustained trade beyond it. The node itself does not choose the scenario. Price behaviour as it enters, travels through and exits the region provides the next evidence.

Now consider a low volume node between two broad areas. If price enters the thin region with a wide directional bar and continues to make progress, movement may be relatively quick. But if price stalls, creates overlapping bars and fails to leave the region, the expected “fast move” is not happening. Update the possible explanation. You should never keep predicting a rapid traverse simply because a profile is thin where price currently sits.

A helpful framework is to observe four things. First, the profile structure: where does the node begin and end? Second, the approach: is price arriving with strong directional progress or in a compressed range? Third, the response within the node: is price accepted, rejected or moving through? Fourth, the next area: what would be the logical reference if price exits the node? This avoids treating profile lines in isolation and makes your chart notes actionable.

There is another subtlety: the node is a summary of past activity, not a display of current resting orders. It does not tell you that there are still buyers waiting at a high volume node or that no orders remain in a low volume node. Some traders confuse historical trade distribution with order-book depth. They are different forms of information. A profile shows past activity according to its data and calculation rules; it does not reveal every current order or participant's intent.

For a ChartLab, use a profile with two high volume nodes connected by a low volume area. Freeze price before it enters the low volume region. Ask the learner to define a scenario if directional progress continues, and an alternative if price stalls. Then show one path where price moves rapidly through and another where it does not. This exercise reinforces that profile shape offers a map of historical activity, not a promise about the future.

High- and low volume nodes can help you organise the chart and identify areas that deserve attention. Their interpretation must remain conditional. Let the profile define the area and let current price action determine whether the market appears to be rotating, rejecting or moving through it.

### Extended spoken case analysis — additional narration

A high-volume node can behave differently depending on whether price arrives from above, below or the middle of the profile. If price approaches from below with sustained upward progress, it may pass through the node and create a new region of activity above it. If it enters with little progress and overlapping bars, it may rotate within the node. If it approaches after a sharp decline, participants may respond differently again. The node itself has no direction. A low-volume area is similar: it can be crossed quickly if directional progress continues, but it can also become a place of hesitation once conditions change. In the exercise, have the learner draw the expected path lightly but not commit to it; then reveal the actual response and ask what evidence required an update. This is a useful place to discuss selection bias: if we look backward across many profile levels, we can usually find a node that appears to explain a past reaction. Before using a level, explain why it was relevant before the outcome. That is how we distinguish a usable reference from an attractive story assembled after the fact.

### Learner progression — Notice → Compare → Apply

**Level 1 — Notice (easy):** Identify one high-volume area and one low-volume area on a profile.

**Level 2 — Compare (guided):** Compare two price paths through a low-volume area: rapid traversal and a pause/rejection.

**Level 3 — Apply (independent):** Write continuation and stall/rejection scenarios for a new node test, with visible conditions that would favour each.

**Reveal rule:** Keep later bars or the model outcome hidden until the learner has recorded the initial evidence and next condition.

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

**Beginner checkpoint:** The learner can explain the main idea in everyday words, point to the evidence on a chart, and say what could change their mind.

**Target delivered duration:** 12–16 minutes normally; hard minimum 10 minutes, usual upper limit 20 unless the concept requires more. Include narration, a narrated chart walkthrough, progressive learner practice, feedback and recap. Rehearse and time the complete lesson; outline timings are targets, not proof of runtime.

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

value migration (the main area of activity moving over time) requires comparable periods. If you compare a two-hour profile with a full-day profile, the difference might reflect the length of the window rather than a meaningful shift. Try comparing adjacent sessions or consistent intraday segments and record the profile settings. Beware of a new profile that is still forming; its POC and boundaries can move while the session develops. A developing reference is not the same thing as a completed one.

Describe the pattern in neutral terms. “The POC has shifted higher over three comparable sessions, and each session has spent more activity in a higher range” is a useful observation. “Buyers have permanently taken control” is an unsupported conclusion. To assess the bullish interpretation, look at the the pattern made by recent highs and lows: are swing highs and lows advancing? Does price hold above the prior value area? Do pullbacks find acceptance (price staying beyond a level instead of quickly coming back) at higher prices or return to the previous distribution? This provides context for what the migrating profile may mean.

Downward migration works similarly. If successive profiles concentrate at lower prices, that may be consistent with the market conducting more activity lower over time. Yet value can move lower during a broad range rotation, a temporary event, or an orderly pullback within a larger uptrend. The timeframe matters. A lower intraday value area does not automatically negate a higher-timeframe uptrend. Make sure your conclusion matches the horizon you are analysing.

What if the POC moves but the overall profile overlaps heavily with the previous session? That may be a small shift within an otherwise balanced environment rather than a decisive change in character. Conversely, a profile that develops well outside the prior value area and holds there may be more meaningful, especially if the pattern made by recent highs and lows supports the shift. There is no universal threshold for what counts as a significant migration. Define a consistent comparison method and test it against the instrument and timeframe.

Value migration can also be incomplete or mixed. The POC may shift up while the Value Area overlaps with the prior period. Or price can move sharply higher but activity later concentrates back lower. Rather than forcing a simple bullish/bearish label, describe what each measure says. Ask whether the market is trending, balancing at a new area, or rotating back into a previous region. The ability to say “mixed evidence” is an analytical skill, not a failure.

In the ChartLab, show three consecutive synthetic session profiles. The first concentrates around a lower range, the second overlaps and extends higher, and the third either continues higher or rotates back. Have learners compare POC, value boundaries, overlap and price swing structure. Reveal two endings so students see that a migrating profile can precede further movement or temporary failure.

Value migration helps answer: where is the market doing more business now relative to before? It can support a reading of acceptance at different prices when combined with structure, but it does not predict future movement by itself. Keep the comparison consistent and let actual price behaviour determine whether the change persists.

### Extended spoken case analysis — additional narration

Value migration is best understood through repeated, comparable observations rather than one moving line. In the three-session example, record POC, value-area overlap, and the price swing structure. A POC shift higher may suggest that the concentration of activity has moved upward, but if the sessions overlap heavily and price remains in a broad range, the change may be modest. If price moves beyond the prior value area and subsequent activity develops there, the evidence for acceptance at higher prices becomes more coherent. Even then, it can reverse. A profile is a record of what occurred during the period; a developing profile may shift before the session closes. Teach learners to distinguish provisional, developing references from completed-session references. Ask them to narrate the chart in neutral language: “The next session's activity is concentrating higher and price has held above prior value,” rather than “the market is definitely bullish.” Then ask what would contradict the reading: return into prior value, failure to hold a higher low, or a fresh range that overlaps the old distribution.

### Learner progression — Notice → Compare → Apply

**Level 1 — Notice (easy):** Mark the Point of Control and Value Area on one session profile.

**Level 2 — Compare (guided):** Compare profiles from equal-length periods and record whether their value areas overlap or migrate.

**Level 3 — Apply (independent):** Assess a three-session sequence, separating the observed profile shift from a hypothesis about market acceptance and stating the contrary evidence you would watch for.

**Reveal rule:** Keep later bars or the model outcome hidden until the learner has recorded the initial evidence and next condition.

### Knowledge check
1. What does a rising POC across comparable sessions describe?
2. Why should profile periods and settings be comparable?
3. What price behaviour would support the interpretation that higher prices are being accepted?

<!-- ASSET: Three comparable session profiles with POC and value boundaries; create upward-migration, downward-migration and overlapping/balanced variants. -->
<!-- CHARTLAB: Learners compare sessions by recording POC movement, value-area overlap, price swings, and whether price stayed outside prior value. They must distinguish observation (“value shifted”) from thesis (“market may be accepting higher/lower prices”). -->

---

## Lesson 5.5 — Putting It Together: Reading Volume Profile Alongside Price Action

### Learning objective
Use a simple Volume Profile to mark areas where trading activity took place in the past, then read what price does when it reaches those areas again. The profile helps you ask better questions; it does not predict the answer.

**Beginner checkpoint:** The learner can point to a profile area, describe the current candles around it, and explain what would support or weaken each possible reading.

**Target delivered duration:** 12–16 minutes normally; hard minimum 10 minutes, usual upper limit 20 unless the concept requires more. Rehearse the narrated chart, progressive practice and feedback together; outline timings are targets, not proof of runtime.

### Outline and timing
- **0:00–1:00 — A profile is a map of past activity, not a forecast.**
- **1:00–3:00 — Review the profile period, Point of Control, Value Area and nodes.**
- **3:00–5:00 — Bring current candles and recent highs/lows back into view.**
- **5:00–7:30 — Read three responses: price pauses, turns away, or moves through.**
- **7:30–10:30 — ChartLab: mark useful areas and write two possible scenarios.**
- **10:30–11:30 — Recap and knowledge check.**

### Full narration script
This lesson brings two things together: Volume Profile and ordinary price reading. We are not adding another tool. We are practising one useful habit: use the profile to see where activity happened in the past, then watch what price does when it reaches those areas again.

First, remember what a profile shows. It groups recorded trading activity by price over a time period you choose. The wide parts show prices where more activity took place. The thin parts show prices where less activity was recorded. The Point of Control is the price row with the most recorded activity. The Value Area is a range that contains a chosen share of the profile's activity, based on your platform's settings. These are descriptions of the period you selected. They do not tell you what the market must do next.

Before using the profile, write down the period it covers. A profile of yesterday's session can tell a different story from a profile covering a full week. Neither is automatically better. Choose the period that fits your question and keep it the same while you study the example. If you change the period, the profile shape and its reference points may change too.

Now look at current price. Imagine price is moving up toward a broad area on the profile where a lot of trading took place. Do not immediately write “resistance.” Instead, ask what price actually does when it reaches the area. There are three simple possibilities. Price may pause and move sideways. It may turn away and move back down. Or it may travel through the area and continue higher. Your job is to observe which behaviour is developing.

Let's walk through the first case. Price approaches the broad area from below. The candles become smaller and several overlap. Price is not moving through the area easily. That is what we can see: the move has slowed. One possible explanation is that buyers and sellers are doing a lot of business around these prices. But we cannot conclude from the profile alone that the market will turn down. Price may pause and then break through. We need to watch the next candles.

In the second case, price approaches the same area and then moves back down. The candles close away from their highs, and price cannot return to the area on the next attempt. This is evidence that the market struggled to remain above the area. It may support the idea that higher prices were rejected in that moment. It still does not guarantee a larger decline. The wider chart and the next important low matter as well.

In the third case, price moves through the broad area with several strong closes and then stays above it. The profile did not act as a barrier. It showed us where past activity had been concentrated; current price has now moved through that area. A good reader updates their view instead of insisting that the old high-activity area must hold.

The same thinking applies to a thin part of the profile. Price sometimes moves quickly through an area where little past activity was recorded. But it can also slow down or turn around. Treat the thin area as a place to pay attention, not a promise that price will race through it. If the market starts to overlap and stops making progress, update your view.

For a practical chart map, use only a few marks. Write down the profile period. Mark the Point of Control, the Value Area boundaries if your platform shows them, and one or two clear wide or thin areas that matter to current price. Then mark the recent swing highs and lows. Do not cover the chart in lines. Each mark needs a reason: it shows where price may be worth watching, not where price must turn.

Now write two possible scenarios. For example: “If price stays above this high-activity area and continues to make higher highs, the move through the area may be holding.” The other scenario might be: “If price falls back below the area and cannot climb back through it, the attempt to move higher may have failed.” Notice that both statements describe something you can see. Neither says that you must place a trade.

Before acting on either scenario, ask the same questions you have used throughout the course. What is the wider pattern made by the recent highs and lows? What did the candles do as price reached the area? Was the recent volume unusual compared with similar bars? What would show that my preferred idea is wrong? Is there a clear entry condition and a sensible place to exit if the idea fails? The profile adds context, but it does not make these decisions for you.

The main lesson is straightforward. Volume Profile tells you where trading activity was concentrated during a chosen past period. Candles and recent highs and lows show how the market is behaving now. Read them together, describe what you see, and wait for the market to provide the evidence your plan requires.

### Learner progression — Notice → Compare → Apply

**Level 1 — Notice (easy):** Locate current price relative to the profile's broad and thin areas.

**Level 2 — Compare (guided):** Read the candles and recent swing structure as price approaches one profile area; write an observation before an interpretation.

**Level 3 — Apply (independent):** Build two if/then scenarios around a new profile area and update them after seeing pause, rejection or move-through alternatives.

**Reveal rule:** Keep later bars or the model outcome hidden until the learner has recorded the initial evidence and next condition.

### Knowledge check
1. What does Volume Profile show that the volume bars under candles do not?
2. What are three things price might do when it reaches a high-activity area?
3. Why should a profile area not be treated as a guaranteed turning point?

<!-- ASSET: Use one clean synthetic chart with the profile period, Point of Control, Value Area and one broad plus one thin profile area clearly marked. Create three alternate price paths: pause, turn away, and move through. Do not add unrelated indicators. -->
<!-- CHARTLAB: Learners mark at most three useful profile areas, then write two “if/then” scenarios around the area nearest current price. Reveal later bars showing a pause, a turn away, or a move through. Learners update their reading using the new evidence. Score the reasoning, not the direction guessed. -->


## Module 5 instructor notes

- Always state profile period, data source and value-area settings.
- Explain historical profile activity versus current resting liquidity; these are different data types.
- Do not describe POC, value boundaries or profile nodes as guaranteed support/resistance.
- Reference themes: Dalton and colleagues on market-generated information, balance and initiative/responsive activity; Dormeier on broader volume analysis and volume-based tools.
