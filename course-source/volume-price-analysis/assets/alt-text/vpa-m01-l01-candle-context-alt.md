# Accessibility and source notes — M01-L01

**Asset ID:** VPA-M01-L01-01  
**Purpose:** Teach that similarly shaped candles may appear in different price contexts and with different activity levels.

## Alt text
Two side-by-side synthetic candlestick charts show similar green final candles. In Panel A, the candle appears after a controlled pullback and its volume is near the baseline from the previous five bars. In Panel B, it appears after an extended advance near a prior-high area and volume is well above the same type of baseline. The comparison shows why candle shape alone is insufficient.

## Extended description
Both panels show 12 synthetic candles, with volume bars beneath the price chart. A dashed line in each volume panel marks the average volume of the five bars immediately before the highlighted candidate candle. In Panel A, price rose, pulled back from a prior swing high and then printed a green candle; the last candle's recorded volume is only modestly above the five-bar baseline. In Panel B, price rose for longer into an area near previous highs and printed a similarly proportioned green candle, but the volume bar is much higher than the five-bar baseline. This does not prove buyers or sellers are in control and does not predict the next move. Learners should consider location and subsequent price behaviour.

## Key teaching point
Describe the candle and relative activity separately. Consider chart location and the prior price pattern before forming an interpretation. State what additional price behaviour you would watch for next.

## Data and licensing
- Synthetic OHLCV teaching data, created for this exercise; not historical market data.
- 12 bars per panel. OHLC values are illustrative price units.
- Baseline in the visual: mean volume of bars 7–11 (the five bars immediately before bar 12).
- Source data: `../data/vpa-m01-l01-candle-context-data.csv`.
- No broker, exchange or real instrument is represented.
- Export/master is vector SVG, 1920 × 1080, with editable text, shapes and labels.

## Usage cautions
Do not publish this chart as a historical trade, signal or forecast. The candidate candle is marked for comparison only; the outline is not an entry marker.
