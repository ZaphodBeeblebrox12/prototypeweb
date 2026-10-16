# Pilot asset package — M01-L01

**Lesson:** What Candlesticks Don't Tell You: Reading the Volume Behind Price  
**Asset ID:** VPA-M01-L01-01  
**Status:** Pass 1 package created; structural checks passed for file presence, chart/data consistency and relative asset paths. A novice usability test, rendered-browser check and formal accessibility review have not yet been run.

## Contents

- `source/vpa-m01-l01-candle-context-compare.svg` — editable 1920×1080 vector chart master.
- `exports/vpa-m01-l01-candle-context-compare.svg` — web/video-ready SVG export derived from the master.
- `data/vpa-m01-l01-candle-context-data.csv` — synthetic OHLCV rows for 12 bars in each panel, with five-prior-bar volume baseline and relative-volume values.
- `alt-text/vpa-m01-l01-candle-context-alt.md` — alt text, extended description, teaching point and source note.
- `lab-specs/vpa-m01-l01-candle-context-lab.html` — standalone interactive practice prototype with learner response fields, self-check and a model-answer reveal. No backend; answers are not saved or automatically graded.
- `lab-specs/vpa-m01-l01-candle-context-lab.md` — instructor notes, model response, acceptable alternatives, feedback prompts and scoring rubric.

## Teaching objective

Help the learner compare two similar green candles while separating:
1. the prior price pattern;
2. the candle's price outcome;
3. volume relative to a stated local baseline;
4. possible interpretations and the next evidence needed.

Panel A presents a recovery after a controlled pullback; candidate volume is modestly above its recent baseline. Panel B presents a similar candle near a prior-high area after an extended advance; candidate volume is clearly above baseline. Neither panel predicts the next move or identifies participant intent.

## Reproduction and use

The SVG source is editable directly. Both SVG files are vector masters at 1920×1080. The HTML links to the export using a relative path and can be previewed locally; the CSV preserves every synthetic OHLCV bar used to draw the two panels. Re-export the SVG if the source is changed; do not edit only the export and leave the source stale.

## Limitations / next gate

The HTML is a local prototype, not integrated into the public website, member area or assessment database. The response checks verify completion only—not whether a learner's interpretation is correct. Instructor feedback remains guided by the rubric in the lab specification. Run a screen-reader/accessibility check and a true beginner pilot before marking the package fully approved.
