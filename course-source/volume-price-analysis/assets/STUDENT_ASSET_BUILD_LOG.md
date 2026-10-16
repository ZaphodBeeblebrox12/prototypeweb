# Student Asset Build — Checkpoint Log
## Read Volume. Find Trade Setups.

**Branch:** `my-new-branch`  
**Purpose:** Deliver actual chart visuals, underlying synthetic data, accessible descriptions and independent practice pages for all 30 rewritten lessons. The student must be shown price, candles, volume, relevant levels and the event being discussed; prose alone is not considered a complete asset.

## Asset standard

Each lesson package is intended to contain:
- a standalone editable SVG chart with labelled axes, candlesticks, volume bars, relevant baseline/level annotations and a synthetic-data disclosure;
- the OHLCV CSV used to construct the chart and staged examples;
- alt text, an extended description and the teaching point/limitations;
- a self-contained ChartLab HTML that renders the chart on screen, includes Notice/Compare/Apply stages, asks the learner to respond, reveals model explanations and shows contrasting outcomes after the initial reading is submitted.

All examples use synthetic numbers for instructional purposes; they are not market data or trading signals. Student interaction does not claim to semantically grade free-text reasoning. Browser appearance, assistive-technology compatibility, responsiveness and true-beginner comprehension must be tested separately before release.

## Checkpoints

| Module | Lesson packages | Status | Checkpoint |
|---|---|---|---|
| 1 — Read the Market Behind the Candles | M01-L01–M01-L05 | In progress | — |
| 2 — Spot Buying and Selling Pressure | M02-L01–M02-L05 | Pending | — |
| 3 — Find Trade Setups at the Levels That Matter | M03-L01–M03-L05 | Pending | — |
| 4 — Spot False Breakouts Before You Chase Them | M04-L01–M04-L05 | Pending | — |
| 5 — Find the Price Levels Worth Watching | M05-L01–M05-L05 | Pending | — |
| 6 — Put It All Together: Build a Complete Trading Plan | M06-L01–M06-L05 | Pending | — |

## File layout

- `chartlabs/`: self-contained learner-facing HTML practice pages.
- `student-assets/svg/`: editable primary lesson charts.
- `student-assets/data/`: source OHLCV CSV with labels identifying each stage/case.
- `student-assets/alt-text/`: accessibility descriptions, scope notes and chart interpretation guidance.

A module is marked “source package complete” only when all five lessons have all four file types and the student-facing charts align with the corresponding rewritten lessons. This status does not imply browser QA or course integration.
