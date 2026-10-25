# Understand Bollinger Bands — Static-Image Asset Register

**Status:** Initial visual inventory. These are briefs, not finished or QA-approved assets.  
**Rule:** One numbered figure is a purposeful teaching aid, not decoration. Use static annotated charts, side-by-side panels, or simple diagrams. No ChartLab or interactive assets.

## Figure and asset conventions

- Internal asset IDs use BB-M[module]-F[number], for example BB-M1-F01.
- Student-facing labels use Figure [module].[figure], for example Figure 1.1.
- Expected image path: `assets/student-assets/svg/bb-m01-f01.svg` for BB-M1-F01; manuscript embeds use `../assets/student-assets/svg/bb-m01-f01.svg`. Use lowercase, zero-padded module and figure numbers for all assets.
- Do not print internal asset IDs on the image itself.
- Never print “synthetic data” or production labels inside a figure. If an illustrative chart needs clarification, say so in the nearby lesson caption.
- Make price and band lines visually distinct and labels large enough to read on mobile and at 200% zoom. Avoid tiny annotations, unnecessary indicators, crowded legends, and colour-only distinctions.
- Where charts are illustrative, they must not be presented as actual historical data. Keep construction/provenance notes in the course source and figure caption.
- Every final asset should include meaningful alt text and, for complex comparisons, a longer description.
- Design each figure to support a clear learner action: observe a visible fact, compare plausible interpretations, or identify the evidence/condition that would test a reading. Where practical, comparative panels should make the difference in evidence easy to see.

## Module 1 — What Bollinger Bands Actually Tell You

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M1-F01 | Figure 1.1 | Clean price chart with middle line, upper band, lower band; two marked areas where the band width changes. Three short callouts only. | 1.1 |
| BB-M1-F02 | Figure 1.2 | Two side-by-side chart panels: upper-band touch inside a range versus upper-band interaction during a rising trend. Same band style and similar-sized labels. | 1.2 |
| BB-M1-F03 | Figure 1.3 | One chart separated into quiet, expanding, and wide-band phases; aligned beneath it with a simple width sketch, not an extra technical indicator. | 1.3 |
| BB-M1-F04 | Figure 1.4 | Four short panels showing (a) band touch then reversal, (b) band touch then continuation, (c) close outside then continuation, and (d) close outside then failure. Add small “what we know / what we do not know” captions outside the chart. | 1.4 |

## Module 2 — Read the Bands and Their Measurements

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M2-F01 | Figure 2.1 | Simple, accessible construction diagram: price average in the middle; spread around the average; upper/lower bands at the selected distance. Include default 20 and 2 settings without a long formula block. | 2.1 |
| BB-M2-F02 | Figure 2.2 | Same price history viewed through three settings: common 20/2, shorter period, longer period. Labels must state exact settings and warn in caption that the comparison is visual, not proof of which setting is best. | 2.2 |
| BB-M2-F03 | Figure 2.3 | %B number line from below 0 through 0, 0.5, 1 to above 1, paired with a single band diagram and matching price positions. | 2.3 |
| BB-M2-F04 | Figure 2.4 | Price chart with narrow, widening, and wide bands paired with a BandWidth line aligned in time. Mark the low-width section; do not imply direction from it. | 2.4 |

## Module 3 — Read the Market Before Reading the Signal

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M3-F01 | Figure 3.1 | Three independent chart panels: clear rising trend, clear range, and mixed/transitioning structure. Call out swings and boundaries; do not make the mixed case artificially obvious. | 3.1 |
| BB-M3-F02 | Figure 3.2 | Side-by-side upper-band walk and lower-band walk, each with continued price progress. Add one isolated band touch as contrast. | 3.2 |
| BB-M3-F03 | Figure 3.3 | Two diagrams: (A) BandWidth falls to a low relative reading; (B) Bollinger Bands sit inside Keltner Channels. Label as different definitions of compression and keep their visual conventions distinct. | 3.3 |
| BB-M3-F04 | Figure 3.4 | Three separate outcomes after similar quiet conditions: break upward, break downward, and initial break that fails. The pre-breakout section should look similar across panels to teach directional uncertainty. | 3.4 |

## Module 4 — Read Bollinger's Signature Patterns

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M4-F01 | Figure 4.1 | Two-panel W-bottom comparison. Candidate example: first low reaches/breaches lower band, second has a different relationship to the band; comparison example remains incomplete or lacks chosen confirmation. Label the key swings, not every candle. | 4.1 |
| BB-M4-F02 | Figure 4.2 | Two-panel M-top comparison with upper-band relationship, intervening reaction low, and different follow-through. Avoid presenting either shape as a certain short signal. | 4.2 |
| BB-M4-F03 | Figure 4.3 | Price pane and %B or one independently justified indicator pane showing a divergence-like mismatch. Add an alternative continuation outcome in a second panel. | 4.3 |
| BB-M4-F04 | Figure 4.4 | Four compact, legible pattern states: candidate, confirmed under an explicitly stated course rule, failed, and unclear. Show the decision point, not only the completed history. | 4.4 |

## Module 5 — Build and Trade Bollinger Setups

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M5-F01 | Figure 5.1 | Three-panel setup comparison: (A) squeeze then close above the upper band, (B) squeeze then close below the lower band, (C) first move fails before a later resolution. Show BandWidth relative to its own history and the exact breakout bar. Do not suggest the squeeze picks direction. | 5.1 |
| BB-M5-F02 | Figure 5.2 | Three panels for Bollinger Method II: (A) %B > 0.8 and MFI(10) > 80 long; (B) %B < 0.2 and MFI(10) < 20 short; (C) near-miss where one input fails the threshold. Display %B and MFI labels clearly. | 5.2 |
| BB-M5-F03 | Figure 5.3 | Method III long and short examples pairing band tags with an independently chosen volume indicator. Include one positive lower-band alert, one negative upper-band alert, a price-confirmation bar, and one failed/unsupported alert. State which indicator variant each panel uses. | 5.3 |
| BB-M5-F04 | Figure 5.4 | Four labelled panels comparing one outside-band close with two consecutive outside closes, then trending ADX versus non-trending ADX. Show the Method IV classification: trend-following in stronger ADX conditions and potential opposite-direction reversal in weaker ADX conditions. Keep the threshold stated as the implementation's chosen value, not a universal constant. | 5.4 |
| BB-M5-F05 | Figure 5.5 | Side-by-side W-bottom and M-type top. For W: first low at/outside lower band, relatively higher second low inside, volume softer on retest, then strong up day with above-average range/volume. For M/top: repeated upward pushes with a later weaker band relationship and a clear sign-of-weakness example. Include a failed pattern. | 5.5 |
| BB-M5-F06 | Figure 5.6 | TTM Squeeze: show Bollinger Bands inside Keltner Channels, the release when bands move outside, and a positive/rising versus negative/falling momentum histogram. Include a release that fails. Keep visual conventions separate from the BandWidth-based Bollinger Squeeze in Figure 5.1. | 5.6 |

## Module 6 — Recognise Failed Setups and Know When to Wait

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M6-F01 | Figure 6.1 | Breakout head-fake sequence: initial close outside the band and range, return inside, then later outcome. Mark where the original idea weakens; do not label the reverse trade as automatic. | 6.1 |
| BB-M6-F02 | Figure 6.2 | Side-by-side persistent band walk versus band walk with weakening structure. Keep the visual point on the differences that matter; don't add extra indicators merely to make the answer obvious. | 6.2 |
| BB-M6-F03 | Figure 6.3 | Two range-boundary cases: a false poke that re-enters and a genuine range break with follow-through. Mark the original range premise and its invalidation. | 6.3 |
| BB-M6-F04 | Figure 6.4 | Four skip candidates: late expanded move, conflicting evidence, low-liquidity/gap-risk illustration, and poor room to target relative to stop. Each panel includes a short observable reason to wait. | 6.4 |

## Module 7 — Manage Risk and Review the Process

| Asset ID | Figure | Brief and required elements | Used in |
|---|---|---|---|
| BB-M7-F01 | Figure 7.1 | Clear numerical example linking entry, stop, cash risk allowance, and position size. Include a second example with a wider stop and smaller position. Add note that gaps/slippage can increase realised loss. | 7.1 |
| BB-M7-F02 | Figure 7.2 | Trade-management path diagram showing planned target, invalidation, and unresolved progress. Every branch leads to a pre-written action rather than a new discretionary guess. | 7.2 |
| BB-M7-F03 | Figure 7.3 | Simple review table across several conditions: trend, range, failed break, and unclear context. Columns record setup, trigger, stop/exit rule, outcome, rule adherence, and limitation. | 7.3 |
| BB-M7-F04 | Figure 7.4 | Three capstone cases: a disciplined losing trade, an undisciplined winning trade, and a defensible no-trade decision. Show only information available at the decision point first; later outcome can be shown in a separate panel. | 7.4 and final assignment |

## Temporary web references for Module 5

The setup manuscript currently embeds 32 remote historical chart examples to support private research and lesson design. Their source URLs and method-by-method notes are stored in [`assets/reference-examples/IMAGE_SOURCE_INDEX.md`](assets/reference-examples/IMAGE_SOURCE_INDEX.md). They are not the final course assets; replace them with approved local TradingView captures or other rights-cleared images before public release.

## Visual quality checklist

- [ ] Main chart or diagram communicates one teaching point.
- [ ] Text is legible on desktop, on mobile, and at 200% zoom.
- [ ] Figure number uses the exact module convention.
- [ ] Price levels, bands, callouts, and axes are not crowded or overlapping.
- [ ] The student can see the event named in the lesson without searching.
- [ ] Colours are supplemented with labels or shapes.
- [ ] The figure does not accidentally reveal the answer before the task when staged reasoning is needed.
- [ ] Alt text explains the point of the figure; complex figures also have a longer description.
- [ ] Source, asset master, and any construction notes are stored with production files.
- [ ] No internal authoring labels or “synthetic data” banners appear inside the image.
- [ ] An illustrative chart is not presented as historical evidence.
- [ ] Rendered output has been visually inspected; file existence alone does not count as QA.

## First-pass source asset state — 19 October 2026

The 30 numbered figure paths now have first-pass, TradeThesis-authored SVG diagrams under `assets/student-assets/svg/`. These are original conceptual teaching drawings, not historical market charts. Each SVG includes title and description metadata and is constrained to a safe, static SVG subset by the Academy source importer.

**Release status remains review-only.** Browser visual review at desktop/mobile widths and 200% zoom is still required before publishing. The 32 remote historical examples in Module 5 remain temporary references and must be replaced with course-owned TradingView captures or rights-cleared local chart images in the Academy import review before publication is permitted.