# Accessibility and data notes — M01-L01 progression assets

All files contain synthetic teaching data, not historical market data.

## Main comparison chart
**Alt text:** Two side-by-side candlestick charts use the same vertical price scale and show equal-sized candidate candles. Panel A follows a pullback with candidate volume of 185 against a five-bar baseline of 157; Panel B is near a prior-high area after a longer rise, with candidate volume of 420 against a baseline of 225. Volume bars are neutral grey and the candidate bars are highlighted.

**Extended description:** Both candidate candles have identical OHLC dimensions: a body of 3 illustrative price units and a full high-to-low range of 5. Panel A shows an advance, pullback and recovery, with candidate volume about 1.18 times the preceding-five-bar average. Panel B shows a longer advance into a marked prior-high area, with candidate volume about 1.87 times its baseline. The price axis is shared so equal price ranges occupy equal visual space. Neither case proves who traded or predicts what happens next.

## Level 1 — Notice
**Alt text:** A simple six-candle sequence with volume bars below. The final candidate candle is outlined, its volume bar is highlighted, and a dashed line marks the average volume of the previous five bars. The learner identifies the candle's direction and whether its volume is above or below the baseline.

## Level 3 — Apply, before outcome reveal
**Alt text:** A synthetic price series has closed above a prior range high. The candidate breakout candle is outlined and has high volume relative to the average of the previous five bars. No later bars are visible, so the learner must record an initial reading before the outcome is revealed.

## Alternate endings
- **Continuation:** After the same initial breakout, later candles hold above the prior range high and make further upward progress.
- **Failed breakout:** After the same initial breakout, later candles close back below the prior range high and make further downward progress.

## Data and provenance
- Source data: `../data/vpa-m01-l01-candle-context-data.csv`.
- OHLCV rows are synthetic, in illustrative price and volume units.
- Candidate baselines use the arithmetic mean of the five immediately preceding volume bars.
- Main comparison: Panel A candidate volume = 185, baseline = 157, ratio = 1.18×; Panel B candidate = 420, baseline = 225, ratio = 1.87×.
- Level 3 candidate volume = 410; pre-event baseline = 184; ratio = 2.23×.
- No broker, exchange or real instrument is represented.
- Chart files are vector SVGs, editable as text/shapes and designed to scale to the intended export size.
