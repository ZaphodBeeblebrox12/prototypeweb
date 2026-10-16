# Understand Bollinger Bands

**Course status:** Draft student-facing manuscripts written; static assets and review remain  
**Working branch:** my-new-branch  
**Location:** course-source/understand-bollinger-bands/  
**Audience:** Intermediate market participants who want a clearer, more practical understanding of Bollinger Bands.

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

The course now has a seven-module architecture and draft student-facing text for all 30 lessons, saved as one Markdown manuscript per module. The lessons include figure references, worked explanations, static-image tasks, model reasoning, common mistakes, transfer prompts, and source notes. The content uses plain language for intermediate traders and now centres the setup module on Bollinger's three named book methods, his later Method IV, his W/M pattern setups, and Carter's separate TTM Squeeze. Source-defined entry conditions are distinguished from course-level risk and execution decisions.

The referenced core SVG paths follow the agreed naming scheme, but final course-owned figure assets have **not** been created or visually tested yet. Module 5 now includes 32 temporary historical chart image embeds across six setup lessons, with the image/source map kept in the internal reference index. These are remote embeds, not local image copies, and are intended for replacement before release. The manuscripts are drafts and still need a source-attribution/duplication pass, actual image production, mobile/zoom review, and learner timing/comprehension checks. This work has not been integrated into the public course pages or deployed.

Next: verify exact author-specific pattern details against the book edition, replace the temporary Module 5 web images with course-owned TradingView captures, produce the remaining core figures in a sensible batch workflow, render the manuscripts with the figures, and run a focused readability/content review.