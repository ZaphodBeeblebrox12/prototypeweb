# Understand Bollinger Bands

**Course status:** All 30 student-facing lesson manuscripts deepened and wired into the first-pass Learning Room; visuals and final review remain  
**Working branch:** my-new-branch  
**Location:** course-source/understand-bollinger-bands/  
**Audience:** Intermediate market participants who want a clearer, more practical understanding of Bollinger Bands.

**Shared template:** [TradeThesis Course Template Standard](../COURSE_TEMPLATE_STANDARD.md). This course and all future revisions should use the updated Learning Room template; lesson sections remain flexible, not boilerplate.

**Production checkpoint:** [PRODUCTION_CHECKPOINT.md](PRODUCTION_CHECKPOINT.md) tracks current preview and image replacement status. [First-pass preview source](preview/first-pass/index.html) is a review artifact, not deployed website code.

## Purpose

Create a student-first self-study course that teaches traders how to interpret Bollinger Bands in context, build conditional trade plans, recognise failed ideas, and decide when not to trade.

The course follows the principles in [the reusable TradeThesis course-creation method](../COURSE_CREATION_METHOD_VOLUME_PRICE_ANALYSIS.md). It uses plain, natural language without sacrificing accuracy or depth.

## Documents

- [Course architecture](COURSE_ARCHITECTURE.md) — course promise, progression, lesson map, practice design, source map, and release criteria.
- [Static-image asset register](ASSET_REGISTER.md) — figure labels, internal asset IDs, image briefs, and lesson references.
- [Module 5 temporary image source index](assets/reference-examples/IMAGE_SOURCE_INDEX.md) — internal provenance and replacement map for the historical chart examples embedded in the setup lessons.
- [Module 1 manuscript](lessons/MODULE_01_WHAT_BOLLINGER_BANDS_TELL_YOU.md) — the mental model and limits of the bands.
- [Module 2 manuscript](lessons/MODULE_02_READ_THE_BANDS_AND_MEASUREMENTS.md) — construction, settings, %B and BandWidth.
- [Module 3 manuscript](lessons/MODULE_03_READ_MARKET_CONTEXT.md) — trend/range context, band walks and squeeze types.
- [Module 4 manuscript](lessons/MODULE_04_BOLLINGER_SIGNATURE_PATTERNS.md) — W-bottoms, M-tops and confirmation.
- [Module 5 manuscript](lessons/MODULE_05_BUY_AND_SELL_PLANS.md) — Bollinger Methods I–IV, W/M pattern setups, and Carter's TTM Squeeze.
- [Module 6 manuscript](lessons/MODULE_06_FAILED_SETUPS_AND_NO_TRADE.md) — failure cases and when to wait.
- [Module 7 manuscript](lessons/MODULE_07_RISK_AND_REVIEW.md) — position sizing, management, testing and final assignment.

## Agreed production rules

- Assume learners know basic candles, trends, support/resistance, entries, stops, and trading risk. Do not reteach the basics of financial markets.
- Explain Bollinger-specific terms in everyday language when students first need them.
- Use short, clear sentences and intuitive examples. Avoid academic phrasing and unexplained jargon.
- Most lessons target 10–20 minutes. The six setup lessons in Module 5 target 25–28 minutes because they include more detailed trade planning and multiple historical chart comparisons.
- Use supplied static charts and diagrams only. No ChartLab, interactive chart tasks, coding, or tasks that require students to find their own charts. The current Module 5 galleries are temporary external image references and must be replaced with course-owned/rights-cleared local images before public release.
- Give each figure a persistent asset ID and a student-facing module figure label such as Figure 1.1. Keep labels large, simple, and readable when zoomed or viewed on mobile.
- Do not put internal production labels such as “synthetic data” on figures. Explain illustrative examples in nearby lesson text or captions when needed.
- Separate John Bollinger's documented guidance from course-designed trading frameworks and contributions from other authors.
- Use **Observe → Interpret → Test** as the recurring student-facing reasoning habit: record the facts, consider a plausible meaning and alternative, then identify evidence or a condition that would strengthen or weaken the reading.
- Treat no-trade and wait-for-more-evidence decisions as valid outcomes.
- Keep student-facing titles free of internal level labels and production notes.
- Do not change the website course integration or deploy this research package as part of this phase.

## Research guardrails

The primary source is John Bollinger's official rules and *Bollinger on Bollinger Bands*. The research must preserve important details: band tags are not signals; prices can walk a band in a trend; closes outside the bands are initially continuation rather than reversal signals; %B describes price relative to the bands; and BandWidth measures band width. The bands do not imply a normal distribution or guarantee a particular outcome.

The course will clearly distinguish Bollinger's BandWidth / low-volatility concepts from John Carter's TTM Squeeze, which compares Bollinger Bands with Keltner Channels and adds a momentum component.

## Current checkpoint

The seven-module course contains 30 student-facing Markdown lessons, with the first-pass Learning Room now reading its visible lesson content from a generated data asset: [`assets/bollinger-lessons-data.js`](assets/bollinger-lessons-data.js). The Markdown manuscripts remain the source of truth; the JavaScript file is generated output for the static preview, not a second editing system.

The Learning Room preserves the three tabs: **The idea**, **Chart examples**, and **Test your reading**. It presents the full lesson text, an appropriate Bollinger Bands figure, worked comparisons, lesson-specific practice, model reasoning, and a unique knowledge-check question for each lesson. The initial Volume & Price Analysis placeholder has been removed from the default lesson panels; its contextual related-course card remains a separate, explicitly in-development cross-link where relevant.

The current generated content has approximately 907–1,503 words per lesson across the three tabs. All 24 shorter lessons in Modules 1–4 and 6–7 now have a second worked comparison in addition to their earlier worked case. The six Module 5 setup lessons retain their deeper setup rules and multiple case discussions. These are content-depth estimates, not measured stopwatch timings; a fresh learner timing and comprehension pass is still required.

The first-pass page and generated content are **review artifacts on `my-new-branch` only**. They have not been integrated into the served course pages or merged to `main`. The separate `Deploy TradeThesis preview` workflow uploads only the `site/` directory; it does not include this `course-source/understand-bollinger-bands/` preview or its generated lesson data.

## Remaining before release

- Complete the source-attribution and duplication review, and verify author-specific rule details against the relevant book/manual editions.
- Produce or select course-owned/rights-cleared chart assets. The core final SVG set has not been created or visually tested. Some reference figures still use temporary remote source images and may fail to load; replace them before public release.
- Run a fresh browser smoke test of all 30 lessons after the manuscript-loader change, including chart zoom, the three tabs, mobile layout, and image fallback behaviour.
- Check actual learner timing, question clarity and model reasoning with representative lessons before treating the planned durations as measured results.
- Keep all remaining work on `my-new-branch`; no public integration, merge or deployment without explicit approval.
