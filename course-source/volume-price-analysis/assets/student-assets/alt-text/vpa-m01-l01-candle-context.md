# Accessibility and source notes — M01-L01

**Linked lesson:** What Candlesticks Don't Tell You: Reading the Volume Behind Price
**Asset purpose:** Compare a candle's price result with recorded activity and context.
**Data:** Synthetic OHLCV generated for instruction. Not historical market data, not a forecast and not a trading signal.

## Primary chart: What Candlesticks Don't Tell You: Reading the Volume Behind Price
Two similar green candles can occur in different contexts. What can you actually observe, and what remains an interpretation?

The chart has a labelled price pane above a volume pane. Each candle shows an open/close body and high/low wick; green candles close above their open and red candles close below their open. Volume bars align with the corresponding price bar. A dashed horizontal line shows an average of recent bars; the shaded dashed range identifies Prior range / swing area. Exact values are available in the matching CSV.

## Chart reading notes
The early bars decline, then recover toward the marked reference area. The focus event is an upward close accompanied by recorded activity. A similar-looking candle after a longer advance could raise a different question; neither candle alone proves continuation.

## Suggested alt text
“What Candlesticks Don't Tell You: Reading the Volume Behind Price. Synthetic candlestick and volume chart. The early bars decline, then recover toward the marked reference area. The focus event is an upward close accompanied by recorded activity. A similar-looking candle after a longer advance could raise a different question; neither candle alone proves continuation. The shaded zone is a reference area, not a guaranteed reaction point. Price and volume must be interpreted together. Later-outcome variants share the same initial bars and then diverge.”

## Limits and learner guidance
- Data is synthetic and created only to illustrate the stated concept.
- Relative volume is a comparison with recent bars in this sample; it does not identify traders or predict the next move.
- The HTML exercise reveals two alternative outcomes only after the learner records an initial reading.
- Free-text fields enforce completion length only and do not semantically grade the student's response.
- Check visual rendering, small-screen layout, 200% zoom, keyboard focus, screen-reader output and novice comprehension before release.
