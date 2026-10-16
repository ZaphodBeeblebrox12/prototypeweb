# Accessibility and source notes — M01-L02

**Figure number:** Figure 1.2; interactive panels use Figure 1.2a–Figure 1.2e.

**Linked lesson:** Is This Move Significant? Spotting Unusual Volume
**Asset purpose:** Compute relative volume and inspect whether the baseline is comparable.
**Data:** Synthetic OHLCV generated for instruction. Not historical market data, not a forecast and not a trading signal.

## Primary chart: Is This Move Significant? Spotting Unusual Volume
A large raw volume number is not enough. Compare it with a stated baseline, then inspect the price result and context.

The chart has a labelled price pane above a volume pane. Each candle shows an open/close body and high/low wick; green candles close above their open and red candles close below their open. Volume bars align with the corresponding price bar. A dashed horizontal line shows an average of recent bars; the shaded dashed range identifies Recent price area. Exact values are available in the matching CSV.

## Chart reading notes
Activity is fairly consistent early, with a sharp volume spike near the marked price area. The price bar makes upward progress but later bars show that the event must be judged with a context-matched baseline and follow-through.

## Suggested alt text
“Is This Move Significant? Spotting Unusual Volume. Synthetic candlestick and volume chart. Activity is fairly consistent early, with a sharp volume spike near the marked price area. The price bar makes upward progress but later bars show that the event must be judged with a context-matched baseline and follow-through. The shaded zone is a reference area, not a guaranteed reaction point. Price and volume must be interpreted together. Later-outcome variants share the same initial bars and then diverge.”

## Limits and learner guidance
- Data is synthetic and created only to illustrate the stated concept.
- Relative volume is a comparison with recent bars in this sample; it does not identify traders or predict the next move.
- The HTML exercise reveals two alternative outcomes only after the learner records an initial reading.
- Free-text fields enforce completion length only and do not semantically grade the student's response.
- Check visual rendering, small-screen layout, 200% zoom, keyboard focus, screen-reader output and novice comprehension before release.
