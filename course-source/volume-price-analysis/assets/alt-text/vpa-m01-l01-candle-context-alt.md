# Accessibility, source and progression notes — M01-L01

**Asset ID:** VPA-M01-L01-01  
**Purpose:** Teach that a similar candle can occur in different price contexts, and that later price behaviour matters.  
**Source:** Synthetic OHLCV data; not historical market data.

## Core comparison chart — alt text
Two side-by-side synthetic candlestick charts show similar green candidate candles. Both price panels use the same scale increment, so the candidate candle bodies and ranges are visually the same size. Panel A shows a green candle during a recovery after a controlled pullback; its volume is 185 against a prior-five-bar average of 157, or about 1.18 times that average. Panel B shows a similar candle after a longer advance near a prior-high area; its volume is 420 against a prior-five-bar average of 225, or about 1.87 times that average. Volume bars are neutral grey, with the candidate highlighted separately. The comparison shows why candle shape alone is not enough to interpret a move.

## Level 1 — Panel A alt text
One synthetic price chart shows an advance, a pullback from a previous swing high, and a green candidate candle during a recovery. Neutral volume bars sit below the candle chart. The candidate volume is 185; the average of the five bars immediately before it is 157. This may be a pause in the pullback, but the chart alone does not establish that the recovery will continue.

## Level 2 — Panel B alt text
One synthetic price chart shows a longer advance into a prior-high area, followed by a green candidate candle similar in size to the Panel A candle. Candidate volume is 420 versus a prior-five-bar average of 225, or about 1.87 times the baseline. The higher activity near the prior-high area deserves attention, but it does not prove a top or identify participants.

## Level 3 — Follow-through outcomes alt text
Two synthetic price paths begin with the same high-volume candidate candle near the prior-high zone. In the continuation path, price holds above the zone and makes further upward progress. In the failure path, price returns below the zone and continues lower. The initial candle and its volume are the same; later price behaviour distinguishes the outcomes.

## Extended description
All bars are synthetic and use illustrative price units. In the initial comparison, both price panels use 32 price units across the plotted vertical range, with the same grid spacing of eight price units. The panels are independently positioned to show different surrounding structures while preserving the same candle-scale increment. The dashed volume line is the average of the five bars immediately before the candidate. Earlier volume bars are neutral grey; the candidate bar uses a separate muted gold highlight, not a bullish/bearish colour.

The Level 3 chart shows only the shared candidate candle and four following bars in each path. A shaded band marks the prior-high area from 131 to 133. The continuation path remains above the zone and rises overall. The failure path returns below the zone and continues lower. The example demonstrates conditional interpretation, not a forecast.

## Teaching point
Describe price structure, candle outcome and volume comparison separately. Then combine them into a possible interpretation and identify what future price behaviour would support or weaken that interpretation. Volume does not reveal each participant's identity or motive.

## Data and licensing
- Synthetic OHLCV teaching data created for this exercise; not historical market data.
- 12 base bars each for panels A and B, plus two alternate follow-through paths extending panel B to bar 16.
- The comparison chart uses the same vertical price-scale increment in both panels.
- Baseline is the arithmetic mean of the five bars immediately before the candidate.
- Source data: `../data/vpa-m01-l01-candle-context-data.csv`.
- No broker, exchange, real instrument or real trade is represented.
- Editable masters: `../source/vpa-m01-l01-candle-context-compare.svg`, `../source/vpa-m01-l01-candle-context-panel-a.svg`, `../source/vpa-m01-l01-candle-context-panel-b.svg`, and `../source/vpa-m01-l01-candle-context-outcomes.svg`.

## Use cautions
Do not publish these charts as historical trades, entry signals or forecasts. The outlined candle identifies the candidate event for teaching; it is not an entry marker.
