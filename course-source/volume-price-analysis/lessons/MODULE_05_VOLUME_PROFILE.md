# Module 5 — Find the Price Levels Worth Watching
## Student lessons

The first four modules focused mainly on volume through time: how much activity a data source recorded during each bar. Volume Profile asks a different question: **at which prices was activity concentrated during a selected period?**

The profile gives you a map of past activity. It does not forecast what price must do next. Use it with price structure and current behaviour, and always know which period and data source the profile represents.

---

## Lesson 5.1 — Where Has the Market Traded Most? Introducing Volume Profile

### Two views of activity

A conventional volume histogram places a bar beneath each candle. Each bar represents the activity recorded during that time interval. The horizontal axis is time.

A Volume Profile reorganises activity by price. It groups recorded volume into price levels or bins for a selected period and displays the distribution horizontally. A broad row means more activity was assigned to that price area than to narrower rows within that same profile. It does not mean all trades happened at one exact price or that price will return there.

### What the profile depends on

Before interpreting a profile, identify:
- **Instrument and data source:** which market or feed was used?
- **Profile period:** one session, several sessions, or a fixed range chosen on the chart?
- **Calculation rules:** how does the platform assign volume to price levels, and what bin size is being used?
- **Comparison:** are you comparing profiles with similar periods and settings?

A session profile and a profile drawn across a month answer different questions. Changing the start/end points can change the shape and its reference levels. Treat the profile as a view of a chosen dataset, not a timeless map of the market.

### Read the shape before naming its parts

Look first for broad concentrations and thin areas. Where was activity comparatively concentrated during the chosen period? Where was less activity recorded? Do not start by trying to trade every profile feature. First describe the distribution in ordinary language.

Suppose a three-session profile shows most activity between 104 and 108, with less activity from 108 to 111. A reasonable observation is that recorded activity was more concentrated in the lower area than in the thinner band above it for those three sessions. This says nothing definite about whether current price will rise or fall.

### Compare time and price

Imagine two events:
- At 10:30, the time-based volume bar is the largest of the morning.
- In the selected session profile, the widest rows sit near 105.

The first tells you *when* activity was unusually high. The second tells you *where* activity was concentrated over the selected period. These observations can be combined, but they should not be confused.

### Worked comparison — the profile question changes with the window

A one-session profile may show a POC at 105, while a five-session composite shows its POC at 102 because earlier sessions added more activity below. Neither profile must be wrong. The question is different: the session profile summarises one session; the composite summarises the selected group of sessions. Label the period and avoid mixing references from different windows without explaining why both are relevant.

### Level 1 — Notice (easy)

**Task:** What does a conventional volume histogram arrange activity by, and what does a Volume Profile arrange it by?

**Feedback:** The conventional histogram shows activity by time interval; the profile distributes activity across price levels for the chosen period and method.

### Level 2 — Compare (guided)

**Task:** Change a profile from a one-session window to five sessions and observe a different shape. Does that by itself mean one profile is wrong?

**Feedback:** No. They describe different selected periods. State the window before interpreting or comparing references.

### Level 3 — Apply (independent)

**Task:** A broad row sits at price 200. State what you may say and what you cannot infer.

**Model response:** More activity was assigned to that row during the chosen period than to narrower rows. You cannot infer a required bounce, universal agreement or current resting orders.
### Common mistake

**Mistake:** Moving the profile start and end points until the shape supports a preferred trade.

**Correction:** Choose the period for a stated reason, record it and interpret the result in that context. If you change the period, recognise that you have changed the question.

### Keep this

> Volume bars describe activity through time. Volume Profile describes how activity was distributed by price over a selected period.

---

## Lesson 5.2 — Finding the Market's Reference Point: Point of Control and Value Area

Once you understand the profile's shape, three commonly used references can help you describe it: the Point of Control, the Value Area High and the Value Area Low.

### Point of Control (POC)

The **Point of Control (POC)** is the price level with the greatest volume assigned to it in the selected profile, under the platform's calculation rules. It marks the profile's widest row. It is a reference to past activity—not a guarantee that price will revisit it or turn there.

### Value Area (VA), VAH and VAL

A **Value Area** is a range of prices containing a selected percentage of the profile's volume. Many platforms use a default around 70%, but settings and calculation details can differ. Check your platform rather than assuming every profile uses the same rule.

- **Value Area High (VAH):** the top of the selected value-area range.
- **Value Area Low (VAL):** the bottom of that range.
- **POC:** the price level with the most volume assigned to it.

These terms describe a calculated profile, not a guarantee of fair value or an official boundary accepted by every market participant.

### Work through a simple profile

Imagine a profile has:
- VAH = 112
- POC = 108
- VAL = 104

This tells you that, under the chosen settings and period, the selected value area extends from 104 to 112, with the greatest assigned volume at 108.

It does **not** tell you that price must rise from 104, fall from 112 or return to 108. It gives you a consistent set of reference points to compare with current price action. The next question is how price behaves when it approaches, trades through or remains beyond these areas.

### Use the period that fits the question

A session profile can help you review one session. A composite profile that includes several sessions can provide a broader view. A fixed-range profile can focus on a specific advance, decline or consolidation. These are not interchangeable. A POC from yesterday's session answers a different question from a POC across a month-long range.

When comparing value areas, keep the profile method and periods in view. Moving from a one-session profile to a multi-week profile can shift the references simply because the underlying dataset changed.

### Worked comparison — profile references are calculated, not universal

Two platforms or settings may draw a different value area because the selected percentage, row size or calculation rule differs. If the value area contains a selected share of profile volume—often around 70% by default—the boundaries depend on the chosen method. Before treating VAH or VAL as a reference, record the platform/window settings. Price interacting with the line is observable; calling the line “fair value” or guaranteed support is a stronger claim.

### Level 1 — Notice (easy)

**Task:** A profile shows VAH 112, POC 108 and VAL 104. Define each using the platform's chosen settings.

**Feedback:** VAH/VAL mark the high/low of the selected value area; POC is the row with most assigned activity. All depend on period and calculation rules.

### Level 2 — Compare (guided)

**Task:** Compare a one-session profile with a multi-week composite whose POC is elsewhere. Which one is correct?

**Feedback:** Neither is universally correct; they answer different questions about different windows. Choose the period that fits the analysis and state it.

### Level 3 — Apply (independent)

**Task:** Price trades above the VAH. Create one scenario for holding outside and one for returning inside.

**Model response:** Holding beyond the VAH and progressing supports sustained trade outside prior value; a return inside and failed reclaim weakens that view. Current location alone does not require a return.
### Common mistake

**Mistake:** Treating the POC as a magnetic price or VAH/VAL as hard support and resistance.

**Correction:** Use them as historical references. The current response determines whether the area is relevant to the present question.

### Keep this

> POC identifies the profile's highest-volume price level; VAH and VAL mark the selected value-area boundaries. None guarantees the next move.

---

## Lesson 5.3 — Where Price May Stall—or Move Quickly: High- and Low-Volume Nodes

A profile often contains broad concentrations and thin sections. These are commonly called **High-Volume Nodes (HVNs)** and **Low-Volume Nodes (LVNs)**.

An HVN is an area where the profile shows relatively high activity. An LVN is an area where relatively less activity was recorded. They are descriptions of the profile's shape; interpreting them requires price context.

### What broad and thin areas can help you ask

An HVN can be associated with a period when considerable trading occurred around that price area. When price revisits the region, it may overlap or spend time there again—but it can also pass through quickly. There is no rule that every HVN must attract price.

An LVN represents a relatively thin area within the chosen profile. Price may travel through a thin area quickly if the market moves through it again, but that is not guaranteed. Fresh orders, news, a change in volatility or the selected profile period can all alter the response.

### Do not turn the profile into a map of guaranteed reactions

A profile is a summary of past activity. It does not show every resting order or guarantee how much liquidity will be available at a future moment. A thin area does not automatically mean “no sellers” or “no buyers”. A broad area does not automatically mean a wall will stop price.

Use the node to frame a question:
- If price enters the area, does it slow, overlap or pass through?
- If price leaves the area, does it retain the progress?
- Is the node aligned with a prior swing or range boundary?
- Does current volume through time support a meaningful observation, or does the data introduce uncertainty?

### Worked example

A selected profile shows an HVN between 150 and 154, with a thinner LVN from 155 to 157. Price rallies from 154 to 158 in two broad bars.

One possible reading is that price travelled quickly through the thin area. That is a description of the path, not proof of the cause. If price later returns to 155–157 and passes through again, the thin-area interpretation is consistent with another quick move. If it stalls there and builds a new area of activity, the earlier profile is no longer a reliable description of the newly developing market. Profile context should be updated when the market adds new evidence.

### Worked comparison — a thin area can still stall price

A profile shows an LVN from 155 to 157. Price travels quickly through it during one move. On a later return, price overlaps in the same region for several bars. The historical profile did not change, but the current behaviour did. A thin section may be associated with faster travel in some conditions; it is not a permanently empty road. Current price action tests, rather than obeys, the historical map.

### Level 1 — Notice (easy)

**Task:** Identify a broad node and a thin area in the profile and describe them without forecasting.

**Feedback:** An HVN is relatively concentrated recorded activity; an LVN is a relatively thin area within the selected profile.

### Level 2 — Compare (guided)

**Task:** Price crosses an LVN quickly in one case but stalls there in another. How should the reading change?

**Feedback:** The profile records historical thinness, but current response takes priority. A stall means the area is not acting as a fast path in this instance.

### Level 3 — Apply (independent)

**Task:** An HVN sits at 150–154. Price enters and overlaps for several bars, then closes above 154. What would support sustained trade above it?

**Model response:** A later hold above 154, a retest that does not fall back into the area and further progress would support that reading. The HVN itself guarantees nothing.
### Common mistake

**Mistake:** Calling HVNs permanent barriers and LVNs guaranteed fast lanes.

**Correction:** Use the profile to locate questions and then read the current interaction. Past concentration is context, not a contract.

### Keep this

> Nodes describe where past activity was concentrated or thin. Current price behaviour tells you how the market is interacting with those areas now.

---

## Lesson 5.4 — When the Market's Focus Shifts: Reading Changes in Value

A single profile describes activity over one selected period. Comparing profiles can show how the areas of greatest activity and the value range are changing. This can help you describe whether the market is building value higher, lower or around a similar area.

### Compare like with like

Compare profiles with periods that make sense for the question—for example, consecutive sessions using the same session definition and similar settings. If you compare one session with a profile spanning two weeks, differences may mostly reflect the period selected rather than a new change in behaviour.

Record the POC, VAH, VAL and overall shape, but avoid relying on one value alone. The meaning depends on current price structure and how price behaves around the developing reference areas.

### Three broad patterns

**Value building higher:** a later comparable profile is centred higher than the prior profile. If price is also making upward progress and holding above prior value, that can support a reading of upward development. If price falls back into the older range, the interpretation needs revision.

**Value building lower:** the later profile's main concentration and value range have shifted down. If price is also making lower highs and lower lows, the profiles are consistent with a downward development. They do not guarantee further decline.

**Value overlapping:** profiles occupy much of the same range. The market may be balanced or rotating in a similar area. A directional move can still occur, but it should be evidenced by price behaviour rather than assumed from the overlap.

### Worked example

Session A has a POC near 100 and value from 96 to 104. Session B has a POC near 103 and value from 100 to 107. The later profile is positioned higher. During Session B, price also holds above 104 and makes a higher swing high.

These facts fit a hypothesis that the market is developing higher. Now consider an alternate outcome: the next session falls below 100 and remains inside Session A's value area. That would weaken the idea that higher value had become established. Both the profile comparison and the price response should be retained in the analysis.

### What changed—and what did not?

A shift in profile shape is not a standalone trade trigger. Before using it, ask:
- Were the profile periods comparable?
- Did price structure move in the same direction?
- Did price hold outside the earlier value area or return into it?
- Did activity and price outcome change around the new references?
- Are there session, news or feed factors that complicate the comparison?

### Worked comparison — value migration versus one shifting POC

Session B's POC sits higher than Session A's, but most of their value areas overlap and price remains inside the same broad range. It would be too strong to call this a confirmed upward trend from the POC alone. If successive comparable profiles shift higher, price holds above prior value and swing structure also advances, the wider case for higher development is stronger. Compare the full shape, period and price behaviour rather than isolating one number.

### Level 1 — Notice (easy)

**Task:** Session A has POC 100/value 96–104; Session B has POC 103/value 100–107. What shifted, and how much overlap remains?

**Feedback:** The POC and value area moved higher; the areas overlap from 100 to 104.

### Level 2 — Compare (guided)

**Task:** Compare that with a lower POC but nearly fully overlapping value areas and no directional price progress. Which claim is safer?

**Feedback:** Report the POC change but do not declare a new trend from it alone. Overlap and lack of sustained price progress limit the interpretation.

### Level 3 — Apply (independent)

**Task:** A later profile is centred higher, but price returns to prior value and breaks a nearby swing low. Update the higher-value idea.

**Model response:** The profile's concentration shifted, but price did not sustain the new area. Returning to prior value and breaking structure weakens the idea that higher value is established.
### Common mistake

**Mistake:** Interpreting a POC move as a directional signal without comparing the full value area and price structure.

**Correction:** Describe what shifted, compare the profile periods and check whether price actually held the new area.

### Keep this

> A developing profile helps describe where activity is building. Price must still show whether that change is being sustained.

---

## Lesson 5.5 — Putting It Together: Reading Volume Profile Alongside Price Action

Volume Profile is most useful when it adds a clear location to the price-volume question. It becomes less useful when every profile feature is treated as a signal.

### A repeatable sequence

**1. State the profile period.** For example: “This is a profile of the last five completed sessions on the selected futures feed.”

**2. Mark only the references relevant to the question.** These might include POC, value-area boundaries, a clear HVN/LVN or a previous range boundary. Too many lines make it difficult to decide which event matters.

**3. Describe current price behaviour.** Is price approaching the area, passing through it, holding outside it or returning inside?

**4. Compare effort and result.** What did the candles achieve? How does recorded volume compare with its stated baseline? The profile and the time-based volume answer different questions.

**5. Create at least two possible scenarios.** State what would support each one. If both remain plausible and no trigger is present, “wait” is a legitimate conclusion.

### Worked case

The selected five-session profile shows:
- POC around 410;
- a value area from 405 to 416;
- a broad activity concentration around 408–412;
- a thinner section above 416.

Price is currently at 417 after a wide upward bar on elevated time-based volume.

**Observation:** Price has moved above the selected value-area high and is trading in a relatively thin section of the historical profile. The breakout bar showed elevated activity against the chosen volume baseline.

**Scenario A — continued progress:** Price holds above 416 on a retest and makes further progress. That would support the idea that the market is sustaining trade beyond the earlier value range.

**Scenario B — return into value:** Price falls back below 416 and cannot reclaim it, then moves towards the prior concentration. That would weaken the continuation case and suggest the outside move was not sustained.

**What is missing?** The current bar alone does not tell us which scenario will occur. A trigger, invalidation condition and assessment of the practical risk would be required before considering an actual trade plan.

This is the right role for profile: it adds context to an evidence-based scenario, rather than replacing the analysis.

### Worked comparison — profile and candle volume answer different questions

Price moves above the profile's VAH while the time-based volume bar is 1.8× its baseline. The profile tells you that price is outside the selected period's prior value area; the volume bar tells you activity was elevated during this interval. Those facts complement one another but are not duplicates. A sustained hold above VAH supports continuation; a return inside and failed reclaim supports the alternative. If price overlaps around the boundary, there may be no trigger yet.

### Level 1 — Notice (easy)

**Task:** State the profile window, POC/value references and current price location before interpreting the chart.

**Feedback:** A useful observation specifies the period and relevant calculation/data context. “Price is at support” does not describe what the profile measures.

### Level 2 — Compare (guided)

**Task:** Price pauses at the POC in one case, turns away in another and moves through it in a third. What profile rule guarantees a response?

**Feedback:** None. The POC marks the highest-volume row in the selected period. The current response shows whether price is holding, crossing or moving away now.

### Level 3 — Apply (independent)

**Task:** Price is above the VAH in a thin profile area after elevated activity. Define continuation, return-to-value and no-trade conditions.

**Model response:** Continuation requires a hold above VAH and further progress; return-to-value requires a sustained move inside and failed reclaim. If price overlaps without either, wait.
### Common mistake

**Mistake:** Drawing POC, VAH, VAL and every visible node, then treating each one as a potential trade.

**Correction:** Choose references because they answer a specific question. Remove levels that do not materially change your analysis.

### Module 5 review

You can now distinguish volume through time from volume at price; read POC, VAH and VAL; interpret high- and low-volume nodes cautiously; compare the development of value; and combine profile context with current price behaviour.

### Quick check

**1. What does a POC identify?**  
The price level with the greatest volume assigned to it in the chosen profile under the platform's calculation rules.

**2. What does an LVN guarantee?**  
Nothing about the future. It identifies a relatively thin area in the selected historical profile. Current price may pass quickly or behave differently.

**3. When is a profile comparison meaningful?**  
When the selected periods and settings are understood and comparable, and the findings are considered alongside current price structure.

**Transfer task:** Choose one profile period. Write its data source and time window, mark two or three references that matter, and create two price scenarios with a clear condition that would favour each one. If no event currently separates the scenarios, state what you would wait to observe.
