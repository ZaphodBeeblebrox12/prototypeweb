# Module 1 Learning-Room Content Map

**Purpose:** Record how the existing production scripts for Lessons 1–2 are represented in the student-facing learning-room preview. This is a production/QA map, not a replacement for the full narration and instructor cues in the lesson scripts.

**Status:** Content integration in browser QA. Template redesign remains out of scope.

## Important distinction

The canonical production scripts contain the fuller instructional design. The learning-room preview previously exposed only a title, summary, outcome, one prompt, a short cue, a simple knowledge check and the chart. The work recorded here adds actual student-facing explanation to the staged chart sequence; it is not just a visual redesign.

The learner-facing copy is intentionally shorter than a voiceover script. Each view should help a self-study learner inspect evidence, understand the interpretation, recognise a limit or alternative, and know what to try next.

All charts in these two lessons are synthetic illustrative OHLC sequences. They are not historical market examples and do not imply a trading outcome.

## Lesson 1 — What Support and Resistance Actually Tell You

| View | Asset | Instructional purpose |
|---|---|---|
| 1 | `L01-A-01-clean.png` | Observe the sequence before a zone or concept label is shown. |
| 2 | `L01-A-02-band.png` | Explain how a broad band groups nearby reactions and why it is not an exact price law. |
| 3 | `L01-A-03-labelled.png` | Separate visible observation from an explanation about hidden participant intent. |
| 4 | `L01-A-04-support-label.png` | Define support as prior behaviour; distinguish it from a guarantee or complete trade signal. |
| 5 | `L01-B-01-clean.png` | Transfer the observe-first method to the upper-side example before naming resistance. |
| 6 | `L01-B-02-band.png` | Show variation across related upper reactions; keep boundary selection provisional. |
| 7 | `L01-B-04-resistance-label.png` | Define resistance and compare it with support using parallel reasoning. |
| 8 | `L01-A-05-breakdown.png` | Use the later crossing as a counterexample: new evidence changes the reading but does not erase earlier reactions. |
| 9 | `L01-PRACTICE-A-01-clean.png` | Learner identifies evidence on a clearer practice example before the reference. |
| 10 | `L01-PRACTICE-A-02-reference.png` | Worked reasoning: repeated visible reactions support a candidate area, not a guaranteed hold. |
| 11 | `L01-PRACTICE-B-01-clean.png` | Learner works with weaker, less clustered evidence. |
| 12 | `L01-PRACTICE-B-02-reference.png` | Model answer explicitly accepts an uncertain reading or a broad candidate area with limits. |

### Key learning distinctions

- Observation: what price visibly did near an area.
- Interpretation: why those reactions may make the area worth watching.
- Limit: a chart excerpt alone does not establish participants' hidden motives or the next move.
- Counterexample: a zone can be crossed without the earlier observation becoming imaginary.
- Alternative: weaker evidence can justify “unclear for now” instead of forced precision.

## Lesson 2 — Read Structure Before Drawing

| View | Asset | Instructional purpose |
|---|---|---|
| 1 | `L02-A-01-clean.png` | Describe the broad path before naming individual turns. |
| 2 | `L02-A-02-turns.png` | Explain swing points as relative turns and why not every fluctuation needs a mark. |
| 3 | `L02-A-03-structure-reference.png` | Worked read of generally higher highs and higher lows; keep the label revisable. |
| 4 | `L02-B-01-clean.png` | Apply the same structural question to a falling sequence. |
| 5 | `L02-B-02-structure-reference.png` | Worked read of generally lower highs and lower lows; explain what could weaken the reading. |
| 6 | `L02-C-01-clean.png` | Recognise back-and-forth behaviour without requiring a perfectly flat range. |
| 7 | `L02-C-02-major-turns.png` | Select a small set of turns that communicates the broad path. |
| 8 | `L02-C-03-range-reference.png` | Treat the range bracket as approximate structure, not a precise trading boundary. |
| 9 | `L02-D-01-early-state.png` | Make a provisional reading using only the early candles. |
| 10 | `L02-D-02-later-state.png` | Compare the later overlap, revise the reading and avoid hindsight. |
| 11 | `L02-E-01-practice.png` | Independently describe a decline becoming less directional. |
| 12 | `L02-E-02-reference.png` | Model an earlier decline followed by overlap; exact transition placement remains interpretive. |

### Key learning distinctions

- A swing high/low is a relative turning point in the surrounding sequence, not a special candle shape.
- Structure is read from relationships between turns, not a count of candle colours.
- Ranges can be uneven; labels and boundaries are approximate descriptions.
- Structure can change gradually. A provisional reading can be reasonable even if later evidence changes it.
- The reference drawing demonstrates defensible reasoning, not a pixel-perfect answer key.

## Interaction and assessment requirements

- A learner must make an attempt before moving past the first unlabelled view.
- Each chart view updates its prompt, instructions, caption and teaching copy together.
- The current stage is stored in the browser, so a learner can return to the view they last reached in that browser.
- The response area remains a practice note, not an automated open-answer grade. The existing multiple-choice knowledge check provides explanatory feedback.
- Mobile checks must confirm that the page itself does not overflow horizontally and that the chart/reveal controls remain usable.

## Source files

- Full Lesson 1 production script: `scripts/lesson01_production_script.md`
- Full Lesson 2 production script: `scripts/lessons02-04_production_scripts.md`
- Chart asset descriptions: `chart_assets/asset_manifest.csv`
- Internal model answers and review notes: `chart_assets/answer_key_and_review_notes.md`
- Teaching-depth standard: `production/MODULE_DEPTH_WORKING_NOTES.md`
