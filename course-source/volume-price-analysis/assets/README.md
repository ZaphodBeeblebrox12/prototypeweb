# Pilot asset package — M01-L01

**Lesson:** What Candlesticks Don't Tell You: Reading the Volume Behind Price  
**Asset ID:** VPA-M01-L01-01  
**Status:** Stage 2 source-level fixes and responsive mobile chart variants have been added on `my-new-branch`. Stage 3 SVG text is readable; unlocked navigation updates the active-step indicator; focus and reduced-motion handling have been improved; and mobile screens use reflowed SVGs rather than scaled-down desktop charts. A browser fixture passed 12 interaction/responsiveness smoke checks, but it uses stand-in images and is not a full render of the committed page. Actual page rendering, assistive-technology review and beginner usability testing remain open.

## Learning progression shown to the learner

1. **Level 1 — Notice (easy):** identify candidate-candle direction and volume relative to a five-bar baseline.
2. **Level 2 — Compare (guided):** compare two equal-sized candle shapes in different price contexts using a shared vertical scale and neutral volume bars.
3. **Level 3 — Apply (independent):** interpret a new breakout before seeing later bars, state two possible outcomes, then review alternate continuation and failure endings.

The learner sees consistent stage labels **Notice → Compare → Apply** and cannot advance from the easy check until the visible facts are identified. Text length is used only as a completion gate; the prototype does not claim to semantically grade free-text reasoning.

## Files

- `source/vpa-m01-l01-candle-context-compare.svg` — editable master for the two-panel comparison.
- `exports/vpa-m01-l01-candle-context-compare.svg` — comparison chart with a shared price scale, equal-sized candidate candles, neutral volume bars and explicit baseline values.
- `source/vpa-m01-l01-stage1-spot-volume.svg` and `exports/vpa-m01-l01-stage1-spot-volume.svg` — easier recognition chart.
- `source/vpa-m01-l01-stage3-breakout-initial.svg` and `exports/vpa-m01-l01-stage3-breakout-initial.svg` — independent challenge before future price bars appear.
- `source/vpa-m01-l01-stage3-outcome-continuation.svg` and `exports/vpa-m01-l01-stage3-outcome-continuation.svg` — continuation alternative.
- `source/vpa-m01-l01-stage3-outcome-failure.svg` and `exports/vpa-m01-l01-stage3-outcome-failure.svg` — failed-breakout alternative.
- Five `*-mobile.svg` files in `source/` and `exports/` — reflowed narrow-screen versions of the pilot charts. The two-panel context comparison is stacked vertically for phone screens.
- `data/vpa-m01-l01-candle-context-data.csv` — synthetic OHLCV data for the visual stages and alternative endings.
- `alt-text/vpa-m01-l01-candle-context-alt.md` — alt text, extended descriptions and provenance notes.
- `lab-specs/vpa-m01-l01-candle-context-lab.html` — standalone responsive three-level practice page.
- `lab-specs/vpa-m01-l01-candle-context-lab.md` — teaching logic, model responses, acceptable alternatives, feedback, rubric and validation checklist.

## Changes from the first pilot

- Both comparison panels use a common vertical price scale, so the matching candidate candles render at equivalent dimensions.
- Volume bars are neutral grey rather than inheriting candle colour; only the candidate bar is highlighted.
- The comparison chart displays candidate volume, its baseline and the relative multiple.
- The exercise progresses from a simple recognition check to a guided comparison, then a new case with later bars withheld.
- Two alternate outcomes are revealed only after the learner records an initial reading.
- Stage 2 fixes correct encoded headings/annotations in all three Stage 3 charts and their exports; unlocked progress buttons now navigate, the active-step indicator follows navigation, focus moves to newly revealed content, restart returns focus to the first stage, and scripted scrolling respects reduced-motion preferences.
- Five reflowed mobile SVG variants were added and connected with `<picture>`/`<source media="(max-width: 720px)">`; the comparison case stacks its panels instead of shrinking the two-column desktop visual.
- Level 2 feedback now makes clear that response length is not an automatic assessment of reasoning quality.
- The responsive layout includes visible stage labels and a progress cue; text stays in the open page and is not uploaded or persistently stored.
- The lesson script, asset brief, editorial language guide and Q&A bank now specify the same easy-to-harder progression for every lesson.

## Remaining validation

- Open the committed HTML in a browser and verify all real desktop and mobile SVGs render. A separate Chromium fixture passed the interaction smoke checks, but it used stand-in images and is not proof that the committed page renders correctly.
- Test correct/incorrect retries, stage unlocks, outcome reveal and restart.
- Check keyboard/focus order, zoom, screen-reader semantics, contrast and mobile layout.
- Run a beginner usability test and revise unclear instructions or visuals.
- Do not mark the pilot approved or scale it to all lessons until those checks are complete.
