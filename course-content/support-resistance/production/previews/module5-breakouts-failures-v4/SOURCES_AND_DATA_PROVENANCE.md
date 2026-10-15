# Sources and Data Provenance — Illustrated Module 5 v5

## Separation of learner content and research notes

All named author references and source-by-source discussion are kept in `BREAKOUTS_FAILURES_AUTHOR_RESEARCH.md`. The three learner-facing lesson manuscripts and interactive lesson text are written in an original instructor voice and do not name the authors. This file records asset origin, data scope, rights caveats and figure types only.

## Historical price data — temporary internal examples only

- Instrument: NIFTY 50 Index.
- Frequency: daily OHLC.
- Upstream file: `NIFTY 50.csv` from the public GitHub repository `VatsalSin/Stock-Market-Indices-Dataset`.
- Source page: https://github.com/VatsalSin/Stock-Market-Indices-Dataset/blob/main/NIFTY%2050.csv
- The source data spans 2000-01-03 to 2019-12-02. This internal preview uses dated excerpts from 2014, 2016 and 2017–2018.
- The staged chart generator uses recorded Open/High/Low/Close values; it does not randomly alter the historical price bars. The horizontal bands are instructional analytical choices, not official levels.
- The upstream repository did not visibly state a data licence during review. The user approved temporary internal use and intends to replace these examples with their own charts later. **Do not publicly distribute the raw OHLC excerpts or exported historical chart images until rights are confirmed or the cases are replaced with user-owned/authorised data.**

## Figure provenance

- `assets/figures/FIG00_boundary_episode_overview.png` is an AI-generated conceptual overview, labelled as schematic and not market data. The generated source plate is retained in `tools/source_figures/FIG00_generated_overview_source.png`.
- `FIG01` through `FIG25` are original programmatically drawn schematic teaching diagrams. They use deliberately designed candle paths to isolate a concept; they are not backtests, empirical evidence or a forecast.
- `FIG19_simple_break_return_response.png` and `FIG20_simple_retest_outcomes.png` are the simpler v2 instructional diagrams intentionally retained at the beginning of Lesson 13. The more complex v3 diagrams follow them so the learner starts with an uncluttered mental model.
- `FIG21_failed_breakout_structural_stop.png` is the only figure with explicit stop-loss markers. It is restricted to Lesson 14's hypothetical failed-breakout section; no stop markers appear on ordinary breakout or retest diagrams.
- `FIG22` through `FIG25` are new purpose-drawn figures for the v5 lesson expansion: false upside break, downside failure/reclaim, prior swing failure test, and continuation-pause outcomes.
- Preserve each figure caption and this distinction between schematic illustrations and the temporary historical price charts.

## Staged historical reveals

The first chart state hides candles beyond its documented cut-off. Later states add subsequent bars from the same recorded source series. The local preview requires a written response before unlocking the next view. This is an educational interaction, not secure answer delivery or an authenticated course platform.
