# Accessibility and source notes — M02-L01

**Figure number:** Figure 2.1; interactive panels use Figure 2.1a–Figure 2.1e.
**Linked lesson:** Who's Pushing Price? Reading Buying and Selling Pressure
**Purpose:** Describe directional progress and how much price retains it across a sequence.
**Data:** Synthetic OHLCV created for instruction, not historical market data, a forecast or trading signal.

## What the chart shows
The main sequence contains upward progress interrupted by a pullback, then another advance. The highlighted area gives context for judging whether gains were retained across the sequence.

The visual has a price pane with candle bodies and high/low wicks above volume bars for the same intervals. Green means the candle closed above its open; red means it closed below its open. A dashed line shows the average volume of recent bars. The shaded/dashed price zone is **Recent swing area**, a context marker rather than a guaranteed reaction point. Values for all stages are in the matching CSV.

## Suggested alt text
“Who's Pushing Price? Reading Buying and Selling Pressure. Synthetic price-and-volume chart. The main sequence contains upward progress interrupted by a pullback, then another advance. The highlighted area gives context for judging whether gains were retained across the sequence. Read the price result with activity, location and later behaviour; the chart does not establish participant identity or guarantee the next move.”

## Validation limits
- Synthetic sample, not historical prices.
- Relative volume depends on the selected sample baseline.
- Text answers are not semantically graded by the standalone lab.
- Browser rendering, keyboard navigation, zoom, screen-reader behaviour and novice comprehension require manual testing.
