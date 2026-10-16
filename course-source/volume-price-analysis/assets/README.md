# Read Volume. Find Trade Setups. — Student Visual Assets

**Branch:** `my-new-branch`  
**Status:** Source package complete for all 30 lessons; manual browser, accessibility and beginner validation pending.

## Start here

- [All 30 lesson asset packages — index with direct chart, ChartLab, data and alt-text links](STUDENT_ASSET_BUILD_LOG.md)
- [Fillable student worksheet workbook (HTML)](worksheets/volume-price-analysis-student-worksheets.html)
- [Printable student worksheets and worked examples (Markdown)](worksheets/volume-price-analysis-student-worksheets.md)
- [Asset production brief](../ASSET_PRODUCTION_BRIEF.md)
- [Pilot validation checklist for M01-L01](PILOT_VALIDATION_CHECKLIST.md)

## What a student receives

Every one of the 30 lesson plans now links to its own primary chart image, interactive Notice → Compare → Apply ChartLab, source data file and accessible description. The purpose is to show the market structure under discussion, not ask students to imagine what price might have looked like.

- `student-assets/svg/`: editable primary lesson charts, labelled with axes, candles, volume and the level/profile references relevant to the lesson.
- `student-assets/data/`: synthetic OHLCV source records for the original example, comparison case and alternative later outcomes. Profile lessons include price-bin activity and profile references.
- `student-assets/alt-text/`: alt text, extended description, data scope and limitations.
- `chartlabs/`: standalone, responsive practice pages with the chart actually shown, a learner response stage, feedback/model explanation and staged alternate outcomes.
- `worksheets/`: reusable context, evidence, scenario, pre-trade and capstone review templates with worked examples.

Volume Profile lessons use a horizontal activity-by-price histogram aligned to the price scale alongside the candles and time-based volume. Trade-planning lessons illustrate the relationship between setup area, trigger, invalidation and objective where relevant.

## Data and teaching limits

All new example sequences are synthetic learning illustrations, not historical prices or trading signals. Synthetic data is explicitly labelled in the chart. A relative-volume ratio depends on the selected baseline. A profile depends on its period and calculation method. Neither gives certain knowledge of the next market move or the identity/intent of participants.

The free-text interaction gates check that learners have recorded an answer; they do not semantically grade the explanation. The model feedback and worked example are there to help the learner compare their reasoning.

## Validation still required

**Source package complete is not the same as release approved.** The exact standalone HTML pages still need browser rendering checks, small-screen/reflow and 200% zoom checks, keyboard focus and screen-reader review, and testing with true beginners. Lesson duration must be measured through the completed learning experience; these files are not yet marked as browser- or learner-validated.

The earlier M01-L01 pilot package in `lab-specs/` and `exports/` remains a separate pilot/reference package; do not confuse its earlier “in progress” status with the new source packages' status.
