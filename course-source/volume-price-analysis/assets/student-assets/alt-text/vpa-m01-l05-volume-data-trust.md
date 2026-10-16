# Accessibility and source notes — M01-L05

**Linked lesson:** Which Volume Can You Trust? Understanding Data Across Different Markets
**Asset purpose:** Keep volume claims within the limits of the named market feed.
**Data:** Synthetic OHLCV generated for instruction. Not historical market data, not a forecast and not a trading signal.

## Primary chart: Which Volume Can You Trust? Understanding Data Across Different Markets
A chart field labelled volume may count different things in different markets. First identify the data source and what it measures.

The chart has a labelled price pane above a volume pane. Each candle shows an open/close body and high/low wick; green candles close above their open and red candles close below their open. Volume bars align with the corresponding price bar. A dashed horizontal line shows an average of recent bars; the shaded dashed range identifies Relative activity reference. Exact values are available in the matching CSV.

## Chart reading notes
The chart illustrates an FX-like synthetic price sequence with a tick-activity spike. Its volume bars are relative values for this sample. The exercise emphasises the feed label rather than making a claim about total global turnover.

## Suggested alt text
“Which Volume Can You Trust? Understanding Data Across Different Markets. Synthetic candlestick and volume chart. The chart illustrates an FX-like synthetic price sequence with a tick-activity spike. Its volume bars are relative values for this sample. The exercise emphasises the feed label rather than making a claim about total global turnover. The shaded zone is a reference area, not a guaranteed reaction point. Price and volume must be interpreted together. Later-outcome variants share the same initial bars and then diverge.”

## Limits and learner guidance
- Data is synthetic and created only to illustrate the stated concept.
- Relative volume is a comparison with recent bars in this sample; it does not identify traders or predict the next move.
- The HTML exercise reveals two alternative outcomes only after the learner records an initial reading.
- Free-text fields enforce completion length only and do not semantically grade the student's response.
- Check visual rendering, small-screen layout, 200% zoom, keyboard focus, screen-reader output and novice comprehension before release.
