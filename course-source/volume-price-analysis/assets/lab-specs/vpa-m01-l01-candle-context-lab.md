# ChartLab — The Same Candle, Different Context

**Asset ID:** VPA-M01-L01-LAB-01  
**Linked lesson:** Module 1, Lesson 1.1 — What Candlesticks Don't Tell You: Reading the Volume Behind Price  
**Estimated learner time:** 5–7 minutes inside the full lesson  
**Status:** Three-level responsive prototype implemented. Structural checks cover the staged flow, data/baseline consistency and desktop/mobile paths. Exact-page browser rendering, keyboard/screen-reader review and beginner usability remain open.

## Learning target
Describe candle and volume evidence, compare similar-looking candles in different contexts, and test a new breakout reading against later price action without treating volume as a guaranteed signal.

## Level 1 — Notice (easy)
**Visual:** `vpa-m01-l01-stage1-spot-volume.svg`  
Learner identifies the outlined candidate candle's direction, the preceding price movement and whether its volume bar is above or below the dashed five-bar baseline.

**Data:** six synthetic bars in `vpa-m01-l01-candle-context-data.csv`, panel `LEVEL1_SPOT`. The first five volumes are 280, 250, 235, 220 and 205, giving a baseline of 238. Candidate volume is 280 (about 1.18× baseline).

**Expected response:** describe the prior price sequence, state that the candidate candle closed above its open, and note that its volume is above the baseline. No directional forecast is required.

## Level 2 — Compare (guided)
**Visual:** `vpa-m01-l01-candle-context-compare.svg`  
Learner compares the prior structure, candle location and relative activity in two contexts. Both panels use the same vertical price-scale increment, so the candidate candles have equal visual ranges and bodies.

**Data:** panel A candidate volume is 185 vs 157 baseline (about 1.18×); panel B candidate volume is 420 vs 225 baseline (about 1.87×). The candidates have the same OHLC range/body size but occur after different structures.

**Expected response:** A possible reading and an alternative explanation, supported by observations from both price and volume. Neither panel proves that a reversal or continuation will occur.

## Level 3 — Apply (independent transfer)
**Initial visual:** `vpa-m01-l01-stage3-breakout-initial.svg`  
**Later outcome visuals:** `vpa-m01-l01-stage3-outcome-continuation.svg` and `vpa-m01-l01-stage3-outcome-failure.svg`.

The learner sees the initial breakout chart only. Price closes above the marked prior range high of 112–113. Candidate volume is 410 against a baseline of 184, about 2.23×. Before later bars appear, the learner records what is observable, two possible paths, and the evidence needed to distinguish them.

After submission, show the continuation and failure charts. They share the same initial 12 bars and candidate candle, then diverge for three bars:
- **Continuation:** later prices hold above the range high and make further upward progress.
- **Failure:** later prices return below the range high and make further downside progress.

**Expected response:** describe the high-volume breakout attempt without claiming it must succeed; state two possible outcomes and explain which later price behaviour supports each.

## Model answer
**Level 1:** The highlighted candle is green and its volume is above the average of the five preceding bars. Describe the prior candles before interpreting the event. The image is a recognition exercise, not a signal.

**Level 2:** Panel A shows a green candle during a recovery after a pullback. Candidate volume is 185 compared with a baseline of 157, about 1.18 times that average. Panel B shows a similar-size candle after a longer advance into a prior-high area, with volume 420 against a baseline of 225, about 1.87 times that average. Location and relative activity differ, so the questions we ask differ. Neither chart proves a reversal or identifies participants.

**Level 3 initial reading:** Price closed above the prior range-high area. Candidate volume is 410 against a baseline of 184, about 2.23 times the baseline. This is a breakout attempt with elevated recorded activity; it does not prove that price will stay above the boundary.

**Level 3 after reveal:** In the continuation path, price stays above the range high and advances. In the failure path, price returns below the range high and moves lower. The later response helps distinguish the outcomes. The first high-volume candle alone could not determine which path would occur.

## Acceptable alternatives and instructor feedback
A learner may say “the breakout is worth watching but not yet confirmed,” or simply describe the close beyond the boundary and the activity comparison. Accept alternative language when it is grounded in visible evidence, includes uncertainty and states what should be watched next.

- If the learner says “this will break out,” ask: “What can you observe now, and what would you need to see before favouring that path?”
- If the learner describes volume but not the price result, ask: “Where did price close relative to the range high?”
- If the learner chooses an outcome without a condition, ask: “What price behaviour would support the other possibility?”
- If the learner claims institutional buying/selling, ask: “Can this chart identify participants, or does it show price and recorded activity?”
- If the learner identifies the right outcome but cannot describe the sequence, credit the label only partially and ask them to point to the bars that changed the reading.

## Self-check rubric (0–2 each)
1. **Observation:** describes price structure, candidate candle and boundary accurately.
2. **Relative activity:** uses the displayed five-bar baseline.
3. **Context:** explains why the two Level 2 panels differ.
4. **Alternative:** gives a plausible competing scenario.
5. **Next evidence:** names price behaviour that would strengthen or weaken the reading.

Score: 0 = absent/unsupported; 1 = partly present; 2 = clear and evidence-based. A strong response scores at least 8/10, with no zero in Observation or Next evidence. This is practice feedback, not a trading rule.

## Implementation and validation notes
- Desktop and narrow-screen SVGs are paired through `<picture>`/media sources.
- The Level 3 outcome charts are hidden until the learner submits an initial reading.
- The HTML checks whether required text has been written; it does **not** assess the meaning of the answer.
- Responses remain only in the local page. They are not sent to a server and are not persisted.
- Run exact-page browser rendering, keyboard/focus, zoom/contrast, screen-reader and novice usability tests before approval.
