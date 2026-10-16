# Pilot asset package — M01-L01

**Lesson:** What Candlesticks Don't Tell You: Reading the Volume Behind Price  
**Asset ID:** VPA-M01-L01-01  
**Status:** The three-level pilot and responsive mobile variants are implemented. The committed HTML now shows the Level 3 breakout attempt first and keeps continuation/failure charts hidden until the learner submits an initial reading. The page has explicit stage navigation, feedback, a restart control, focus handling and reduced-motion-aware scrolling. The source/data/path checks pass. Earlier fixture tests covered a prior interaction build, not this exact final HTML. Exact-page browser rendering, assistive-technology testing and beginner usability testing remain open.

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
- The four single-chart mobile variants use a shorter viewBox and card height, placing the volume summary closer to the histogram and avoiding excess blank space on phones.
- The mobile charts use larger headings, axis labels, bar numbers and baseline labels to improve readability at phone scale.
- `data/vpa-m01-l01-candle-context-data.csv` — 72 synthetic OHLCV rows covering Level 1, both Level 2 comparison panels, the initial Level 3 breakout and both alternate endings.
- `alt-text/vpa-m01-l01-candle-context-alt.md` — alt text, extended descriptions and provenance notes.
- `lab-specs/vpa-m01-l01-candle-context-lab.html` — standalone responsive three-level practice page.
- `lab-specs/vpa-m01-l01-candle-context-lab.md` — teaching logic, model responses, acceptable alternatives, feedback, rubric and validation checklist.

## Source-data consistency

The CSV contains the underlying bars for every staged visual. The six-bar Level 1 exercise has a five-bar volume baseline of 238 and candidate volume 280 (1.18×). The Level 2 comparison uses A: 185 vs 157 (1.18×), and B: 420 vs 225 (1.87×). The Level 3 breakout uses 410 vs 184 (2.23×); its continuation and failure versions share the same initial 12 bars and candidate before diverging.

## Changes from the first pilot

- Both comparison panels use a common vertical price scale, so the matching candidate candles render at equivalent dimensions.
- Volume bars are neutral grey rather than inheriting candle colour; only the candidate bar is highlighted.
- The comparison chart displays candidate volume, its baseline and the relative multiple.
- The exercise progresses from a simple recognition check to a guided comparison, then a new breakout case with later bars withheld.
- Two alternate outcomes are revealed only after the learner records an initial reading and two possible paths.
- Stage 2 fixes correct encoded headings/annotations in all three Stage 3 charts and their exports; unlocked progress buttons now navigate, the active-step indicator follows navigation, focus moves to newly revealed content, restart returns focus to the first stage, and scripted scrolling respects reduced-motion preferences.
- Five reflowed mobile SVG variants were added and connected with `<picture>`/`<source media="(max-width: 720px)">`; the comparison case stacks its panels instead of shrinking the two-column desktop visual.
- Level 2 feedback now makes clear that response length is not an automatic assessment of reasoning quality.
- After submission and outcome reveal, learners can open a model-reading disclosure comparing the visible breakout evidence, continuation/failure scenarios and the follow-through that distinguishes them.
- The Stage 3 outcome reveal now includes an optional model-reading section: it restates the visible volume/baseline comparison, gives continuation and failure as competing scenarios, and explains that later price response—not the initial volume spike—distinguishes them.
- The responsive layout includes visible stage labels and a progress cue; text stays in the open page and is not uploaded or persistently stored.
- The lesson script, asset brief, editorial language guide and Q&A bank now specify the same easy-to-harder progression for every lesson.

## Remaining validation

- Open the committed HTML in a browser and verify all real desktop and mobile SVGs render. A separate Chromium fixture passed the interaction smoke checks, but it used stand-in images and is not proof that the committed page renders correctly.
- Test correct/incorrect retries, stage unlocks, outcome reveal and restart.
- Check keyboard/focus order, zoom, screen-reader semantics, contrast and mobile layout.
- Run a beginner usability test and revise unclear instructions or visuals.
- Do not mark the pilot approved or scale it to all lessons until those checks are complete.
