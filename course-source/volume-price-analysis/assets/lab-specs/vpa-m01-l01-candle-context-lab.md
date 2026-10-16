# ChartLab — The Same Candle, Different Context

**Asset ID:** VPA-M01-L01-LAB-01  
**Linked lesson:** Module 1, Lesson 1.1 — What Candlesticks Don't Tell You: Reading the Volume Behind Price  
**Estimated learner time:** 4–6 minutes as a segment inside the delivered lesson  
**Status:** Pilot package — instructor-ready specification, plus a standalone HTML practice prototype. It has not been tested with external novice learners.

## Learning target
Describe a candle's price outcome and its relative volume separately, use chart context to compare two similar-looking candles, and name what price behaviour you would watch next.

## Learner instructions
1. Look at both panels before reading the model answer.
2. Describe the prior price pattern in each panel in plain English.
3. Describe the candidate candle itself: direction, range/close behaviour and where it appears.
4. Compare the final volume bar with the dashed line. The line is the average of the five bars immediately before the candidate candle.
5. Write one possible interpretation for each panel and one alternative. Do not guess who traded or claim a reversal/continuation is guaranteed.
6. Say what visible follow-through would strengthen or weaken each interpretation.

## Response prompts
- Panel A: What was price doing before the candidate candle? What does the candle show? How does its volume compare with the baseline?
- Panel B: What was price doing before the candidate candle? What does the candle show? How does its volume compare with the baseline?
- Compare: why is the same candle shape not the same trading situation?
- Next evidence: what would you watch in each panel before becoming more confident in a continuation or failure scenario?

## Instructor model answer
**Panel A:** Price first advanced, then pulled back from a prior swing high. The candidate candle is green and appears during a recovery from that pullback. Its volume is only modestly above the average of the previous five bars. One possible reading is that the pullback may be pausing; an alternative is that the recovery will fail and price will continue lower. The chart does not yet decide between them. A learner could watch whether price regains a nearby short-term high, holds the pullback area or instead breaks lower.

**Panel B:** Price advanced for a longer sequence and is testing an area near prior highs. The candidate candle is also green and similarly proportioned, but its volume is clearly above the five-bar baseline. This may show more activity around a location where price previously struggled. Continued upward progress and holding beyond the prior-high area would support one scenario; a stall, return below the area and failed attempt to regain it would support another. High volume alone does not establish a top or prove who is selling.

**Comparison:** The candle bodies are similar, but the price locations and relative activity differ. Candle shape is a useful observation, not a stand-alone signal. The next bars and the way price behaves around the marked area supply additional evidence.

## Acceptable alternative answers
A learner may describe Panel A as a possible continuation attempt, or simply as a green candle in a pullback that has not yet resolved. For Panel B, a learner may say that elevated activity near the prior high deserves attention, while the outcome remains uncertain. Accept other language if it stays grounded in visible evidence, includes an alternative and does not overstate certainty.

## Feedback guidance
- If the answer only says “A is bullish, B is bearish,” ask: “Which visible facts support that claim, and what else could explain them?”
- If the learner describes volume but not price, ask: “How far did price move, where did it close, and where did this occur?”
- If the learner gives a direction but no next condition, ask: “What price behaviour would make you change your mind?”
- If the learner claims institutional buying/selling, ask: “Can this chart identify the participants, or does it only show reported activity and price?”

## Self-check rubric (0–2 each)
1. **Observation:** Correctly describes prior structure and candidate candle.
2. **Relative activity:** Uses the marked baseline rather than an absolute number alone.
3. **Context:** Explains why location differs between the panels.
4. **Alternative:** Gives at least one plausible competing explanation.
5. **Next evidence:** Names an observable behaviour that could strengthen or weaken the reading.

Score: 0 = absent/unsupported; 1 = partly present; 2 = clear and evidence-based. A strong response scores at least 8/10 with no zero in Observation or Next evidence. This is a practice guide, not an automated trading decision.

## Counterexample and staged reveal
After learners submit their first reading, show a second sequence in which the high-volume candidate candle near the prior high is followed by price holding above that area and continuing upward. Ask what evidence changed. This prevents the learner from treating high volume near a high as an automatic reversal. A complementary failure sequence can show price returning below the area and failing to reclaim it.

## Data
Use `vpa-m01-l01-candle-context-data.csv`. All bars are synthetic, with 12 bars per panel. Baseline is the mean of bars 7–11 for the candidate bar at bar 12.
