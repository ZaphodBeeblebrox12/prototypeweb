# Accessibility, source and progression notes — M01-L01

**Asset ID:** VPA-M01-L01-01  
**Purpose:** Teach the learner to describe candle/volume evidence, compare contexts, then evaluate a new breakout attempt only after recording an initial reading.  
**Source:** All examples are synthetic OHLCV teaching data, not historical market data.

## Level 1 — Notice: alt text
Six synthetic candlesticks appear above their volume bars. The final green candle is outlined as the candidate. Its volume bar is above a dashed line marking the average of the five preceding volume bars. Learners identify the candle direction, the preceding price movement and whether candidate activity is above or below the baseline, without predicting the next move.

## Level 2 — Compare: alt text
Two side-by-side synthetic candlestick charts show similar-size green candidate candles. Both panels use the same vertical price-scale increment, so the candidate candle bodies and ranges are visually equal in size. Panel A shows a green candle during a recovery after a controlled pullback; candidate volume is 185 against a prior-five-bar average of 157, about 1.18 times the baseline. Panel B shows a similar candle after a longer advance near a prior-high area; candidate volume is 420 against a prior-five-bar average of 225, about 1.87 times the baseline. Earlier volume bars are neutral grey and the candidate bars use a separate muted-gold highlight.

## Level 3 — Apply before outcome reveal: alt text
A synthetic price chart shows a green candidate candle closing above a prior range-high area marked 112–113. Candidate volume is 410 against a previous-five-bar average of 184, approximately 2.23 times the baseline. Later bars are not shown. The learner is asked to record what is visible, list two possible outcomes and state what future price behaviour would help distinguish them.

## Level 3 — Outcome A: continuation alt text
After the same initial high-volume breakout candle, price remains above the former range high and makes further upward progress. This supports the possibility that the move is being sustained but does not guarantee what happens next.

## Level 3 — Outcome B: failure alt text
After the same initial high-volume breakout candle, price returns below the former range high and continues lower. This challenges the breakout idea. The initial volume spike alone could not establish which path would occur.

## Extended description
All bars are synthetic and use illustrative price units. In the Level 2 comparison, both price panels use the same vertical scale increment. The panels are independently positioned to show different surrounding structures while preserving the same candle-scale increment. Dashed volume lines mark the average of the five bars immediately before each candidate. Earlier volume bars are neutral grey; candidate bars are highlighted separately rather than using the candle's green/red colour to imply the type of activity.

The Level 3 initial chart shows an attempted breakout and ends at the candidate candle. The prior range high is marked from 112 to 113. Candidate volume is 410 and the five-bar baseline is 184. The continuation and failure charts share the same initial sequence and candidate bar, then diverge. In the continuation version, price holds above the boundary and makes progress. In the failure version, price returns below the boundary and moves lower. The outcome images are revealed only after the learner's initial answer has been submitted.

## Teaching point
Describe price structure, candle outcome and volume comparison separately. Then combine them into a possible interpretation and identify what future price behaviour would support or weaken it. Volume does not reveal each participant's identity or motive, and a breakout candle alone cannot prove that the move will hold.

## Data and licensing
- Synthetic OHLCV teaching data created for this exercise; not historical market data.
- CSV contains 72 data rows: 12 bars for each Level 2 comparison panel (A/B), six bars for Level 1, 12 bars for the initial Level 3 breakout, and 15 bars for each Level 3 alternate ending.
- The Level 2 comparison uses a matched vertical price-scale increment in both panels.
- Baselines use the arithmetic mean of the five bars immediately before the candidate.
- Source data: `../data/vpa-m01-l01-candle-context-data.csv`.
- No broker, exchange, real instrument or real trade is represented.
- Relevant editable masters: `../source/vpa-m01-l01-candle-context-compare.svg`, `../source/vpa-m01-l01-stage1-spot-volume.svg`, `../source/vpa-m01-l01-stage3-breakout-initial.svg`, `../source/vpa-m01-l01-stage3-outcome-continuation.svg`, and `../source/vpa-m01-l01-stage3-outcome-failure.svg`.

## Use cautions
Do not publish these charts as historical trades, entry signals or forecasts. The outlined candle identifies the candidate event for teaching; it is not an entry marker. Outcome charts must not be shown before the learner records the initial Level 3 response.
