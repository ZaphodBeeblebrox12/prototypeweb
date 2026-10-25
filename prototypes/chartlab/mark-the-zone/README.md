# TradeThesis ChartLab 01 — Mark the Zone (review build v4)

Standalone, self-contained HTML prototype. Open `index.html` in a modern browser.

## Three practice examples

1. **Clear W** — mark support around the repeated troughs, then resistance around the intervening swing high / neckline.
2. **Uneven lows** — the second low probes deeper; the support reference has been checked to include that variation without swallowing unrelated price action.
3. **Wider neckline** — the recovery stalls across a broader area; the reference is a zone rather than an exact wick price.

Each study uses a two-stage drawing sequence. The learner draws and submits support (which locks), draws and submits resistance, and then sees their submitted marks beside a reasoned reference. Each example supplies a specific explanation. The short knowledge check reinforces that zones describe previous price behaviour; they do not guarantee a reversal, breakout or trade.

## v4 changes

- Styled practice-set selector with a clear selected state and responsive layout.
- Fixed mobile layout reflow: expanding instructions used to push the chart during a drag. Instructions now appear below the chart on mobile; the drawing surface stays stationary while zone controls appear.
- Kept the numeric-edge controls' space available through the transition from locked support to resistance, preventing layout changes while drawing the second zone.
- Corrected the progress sequence so the Compare step is active after both zones are submitted; Check becomes complete after answering the knowledge check.
- Updated the chart title/subtitle for each example and corrected the Uneven Lows reference band to include its deeper wick.

## Test notes

Browser-tested with Chromium at 1365×1000, 390×844, and 320×720. At each viewport, all three examples were selected and taken through support draw/submit, resistance draw/submit, comparison, correct knowledge-check answers and activity completion. No browser page/console errors were recorded; horizontal overflow was zero. An additional mobile test confirmed the chart's position does not shift when the zone controls appear during a drag.

## Deliberate limitations

- All candles are illustrative teaching data, not live or historical instrument data.
- The feedback uses zone overlap and width heuristics to guide reflection; it is not a universal grading rule for all valid support/resistance interpretations. Reference bands were checked against the sample OHLC wicks so the explanation and plotted areas agree.
- Completion exists only in the current prototype session. There is no account authentication, persistence, course enrolment, or member-dashboard sync.
- No repository files are changed by opening this prototype.
