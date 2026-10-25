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

Every one of the 30 lesson plans links to its own primary chart image, interactive ChartLab, source data file and accessible description. The purpose is to show the market structure under discussion, not ask students to imagine what price might have looked like.

- `student-assets/svg/`: editable primary lesson charts with readable price axes, candles, volume and only the relevant level/profile references.
- `student-assets/data/`: illustrative OHLCV source records for the original example, comparison case and alternate later outcomes. Profile lessons include price-bin activity and profile references.
- `student-assets/alt-text/`: alt text, extended description, data scope and interpretation limitations.
- `chartlabs/`: standalone practice pages with the chart displayed, learner response stages, feedback/model explanation and staged alternative outcomes.
- `worksheets/`: reusable context, evidence, scenario, pre-trade and capstone review templates with worked examples.

Volume Profile lessons use an actual horizontal activity-by-price histogram aligned to the price scale alongside the candles and time-based volume. Trade-planning lessons illustrate setup area, trigger, invalidation and objective where those distinctions matter.

## Figure numbering and student-facing labels

All primary lesson figures use publication-style numbering by module and lesson: **Figure 1.1–1.5**, **Figure 2.1–2.5**, and so on through **Figure 6.1–6.5**. Related panels inside a ChartLab use a letter suffix (for example, Figure 3.2a–e). The manuscripts refer to their corresponding figure at the relevant lesson.

Student interfaces use natural task headings such as “Look closely at the evidence”, “Compare the cases” and “Try a new case”. “Level 1/2/3”, “easy/guided/independent” and similar labels are internal planning scaffolds, not student-facing teaching language.

Figures themselves do not carry a repeated “synthetic data” banner. This keeps the visual clean and leaves the instructional figure title/number easy to find. The accompanying lesson or source/alt-text notes identify examples as illustrative rather than historical market evidence; the actual data CSVs preserve the synthetic-data provenance. Do not mistake an example for a real market event.

## Data and teaching limits

The example sequences are illustrative, not historical prices, forecasts or trading signals. A relative-volume ratio depends on the chosen baseline. A profile depends on its selected period and calculation method. Neither provides certainty about the next market move or the identity/intent of participants.

The free-text interaction checks confirm that learners have recorded an answer; they do not semantically grade the explanation. Model feedback is there to help learners compare their reasoning with the evidence.

## Validation still required

**Source package complete is not the same as release approved.** The exact standalone HTML pages still need browser rendering checks, small-screen/reflow and 200% zoom checks, keyboard focus and screen-reader review, and testing with true beginners. Lesson duration must be measured through the completed learning experience; these files are not yet marked as browser- or learner-validated.

The earlier M01-L01 pilot package in `lab-specs/` and `exports/` remains a separate pilot/reference package. It has now been brought in line with the figure-numbering and student-facing-label conventions; its browser and learner validation is still open.
