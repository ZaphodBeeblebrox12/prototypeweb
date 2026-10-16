# ChartLab — The Same Candle, Different Context

**Asset ID:** VPA-M01-L01-LAB-01  
**Linked lesson:** Module 1, Lesson 1.1 — What Candlesticks Don't Tell You: Reading the Volume Behind Price  
**Estimated learner time:** 5–7 minutes inside the full lesson  
**Status:** Three-level prototype implemented. Structural checks pass. Browser rendering, keyboard/screen-reader review and a novice usability pilot are still required.

## Learning target
Describe a candle's price outcome and relative volume separately, compare similar-looking candles in different price contexts, and use later price action to test a hypothesis without treating a volume event as a guaranteed signal.

## Required progression
Each level adds a reasoning demand. Do not make the learner handle multiple unknowns before they understand the first observation.

### Level 1 — Observe one chart (easy)
**Asset:** `vpa-m01-l01-candle-context-panel-a.svg`  
Learner describes the prior move, the candidate candle and its volume relative to the displayed baseline. No interpretation is required in the first sentence. Use this to establish the habit of describing evidence before naming a pattern.

**Expected elements:** prior advance and pullback; green candidate candle during recovery; volume 185 versus a prior-five-bar baseline of 157 (about 1.18×). Avoid saying that the pullback must be over.

### Level 2 — Compare two contexts (medium)
**Asset:** `vpa-m01-l01-candle-context-compare.svg`  
Learner compares candle shape, earlier price structure, location and relative activity. The two panels use the same vertical scale increment, so candidate candle bodies/ranges display at the same visual size.

**Expected elements:** Panel A follows a controlled pullback; Panel B follows a longer advance into a prior-high area. Relative volume differs (about 1.18× versus 1.87×). One possible reading and one alternative should be offered; neither context gives certainty.

### Level 3 — Transfer to new outcomes (challenge)
**Asset:** `vpa-m01-l01-candle-context-outcomes.svg`  
Both outcome paths start with the same high-volume candidate event. Learner identifies what happens next in each path and explains why that additional evidence changes the reading.

**Expected elements:** continuation path holds above the prior-high zone and makes upward progress; failure path returns below the zone and continues lower. The volume spike alone could not distinguish these outcomes.

## Learner instructions
1. Complete each level before continuing. Responses are kept only in this local page and are not sent to a server.
2. Level 1: record observations before interpretation.
3. Level 2: explain what changed between the two contexts and provide one alternative reading.
4. Level 3: identify the later price behaviour that distinguishes the two outcomes.
5. At the end, compare the work with the model answer and use the self-check rubric.

## Model answer
**Level 1:** Price first advanced, pulled back from a prior swing high and then printed a green candle during a recovery. Candidate volume is 185 compared with a baseline of 157, about 1.18 times that baseline. This is a description; it does not prove the pullback has ended.

**Level 2:** Panel A shows a recovery after a pullback with volume only modestly above its baseline. Panel B shows a similar-size candle after a longer advance into a prior-high area, with volume 420 against a baseline of 225, about 1.87 times that baseline. The second event deserves attention because location and relative activity differ. Neither chart proves a reversal or identifies participants.

**Level 3:** In the continuation path, price stays above the prior-high zone and makes further upward progress. In the failure path, price returns below the zone and continues lower. The initial high-volume candle is the same, so it cannot by itself determine which path occurs. A strong answer names the follow-through that supports each reading and states what would change the interpretation.

## Acceptable alternatives and instructor feedback
A learner may describe the first panel as a possible continuation attempt, or simply state that a green candle appears during a recovery that has not yet resolved. In the second panel, it is acceptable to say that activity near the prior-high area deserves attention while the outcome remains uncertain.

- If the learner only says “bullish” or “bearish,” ask: “Which visible facts support that claim, and what else could explain them?”
- If the learner describes volume but not price, ask: “How far did price move, where did it close, and where did this occur?”
- If the learner gives a direction without a next condition, ask: “What price behaviour would make you change your mind?”
- If the learner claims institutional buying/selling, ask: “Can this chart identify the participants, or does it only show reported activity and price?”
- If the learner identifies the correct outcome but cannot describe the sequence, credit the outcome label only partially and ask them to point to the evidence.

## Self-check rubric (0–2 each)
1. **Observation:** describes prior structure and candidate candle accurately.
2. **Relative activity:** uses the stated baseline rather than an absolute number alone.
3. **Context:** explains why the two panels are not the same situation.
4. **Alternative:** gives a plausible competing explanation.
5. **Next evidence:** names observable behaviour that could strengthen or weaken the reading.

Score: 0 = absent/unsupported; 1 = partly present; 2 = clear and evidence-based. A strong response scores at least 8/10, with no zero in Observation or Next evidence. This is practice feedback, not a trading rule.

## Implementation note
The HTML checks that each response contains text, but it does **not** grade analytical meaning. The model answer is available only after Level 3 is completed. Do not describe answers as saved: this prototype has no backend or account storage.
