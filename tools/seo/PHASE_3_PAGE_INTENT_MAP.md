# Phase 3 — public-site search intent map

**Audit date:** 5 November 2026  
**Branch:** `feature/seo-phase-3-content-discovery`  
**Scope:** public static site, course catalogue, and the hand-off to Academy course overview pages.

This is an editorial search-intent map, not a search-volume report. The phrases below are hypotheses to validate with Search Console and real search data after the permanent public domain is selected. No ranking or traffic estimate is implied.

## Positioning guardrail

TradeThesis teaches traders to observe price, construct a thesis, define risk, manage a trade and review the decision. It is an education product, not a signal service, tip feed or promise of returns.

Use search language that describes the actual learning outcome. Avoid keyword stuffing, claims of consistent profits, “guaranteed” results, or implying that live classes provide calls to copy. Add India/NIFTY/Indian-market phrasing only on pages whose visible curriculum genuinely covers that context; do not append it to every page merely for reach.

## Public page-to-intent map

| Public route | Primary intent to own | Supporting language to test | Page role and boundaries |
|---|---|---|---|
| `/` | Trading education | learn trading with a structured process; trading education for independent traders | Brand and category entry point. Explain the TradeThesis method and guide visitors to a suitable next page. Do not try to rank this page for every course topic. |
| `/courses.html` | Trading courses and micro-courses | online trading courses; trading courses for chart reading, risk and technical analysis | Catalogue and comparison page. Help a visitor choose; keep individual topic explanations on their own course overview pages. |
| `/trading-path.html` | Beginner trading course | learn trading basics; self-paced trading course; chart-reading course | Entry-level learning path: market mechanics, chart reading, trade planning, risk, psychology and review. Do not position it as an advanced strategy course. |
| `/construct.html` | Trade construction and management course | build a trading plan; trade management course; guided trading program | Next step for learners who know basic chart language and want to construct, test and defend a complete process. Keep its 70-day guided format distinct from the live classroom. |
| `/live-class.html` | Live trading education classes | live trading classroom; live trade-planning lessons; guided trading workshops | Six live weekend sessions with worksheets and a personal playbook. Explicitly distinguish education and chart exercises from real-time trade calls or recommendations. |
| `/community.html` | Trading education community | trading community for discussion and review; discuss trade theses and risk | Community and learning-support page. Emphasize perspective, questions and review—not copied calls, performance claims or unverified member-count claims. |

The public static-site SEO builder currently treats these six pages as the public sitemap set. The page titles and descriptions have been aligned to these distinct roles in this phase.

## Course-topic intent map

The static catalogue currently defines nine micro-course records. These topics should each have a distinct primary topic **only when there is a real, published Academy course overview page to receive search traffic**.

| Catalogue course | Topic intent to test | Content boundary |
|---|---|---|
| Support & Resistance | support and resistance in trading; drawing support and resistance zones | Focus on selecting meaningful areas, reactions, breaks and invalidation—not guaranteed reversals. |
| Understand Bollinger Bands | how to read Bollinger Bands; Bollinger Bands indicator | Explain volatility, expansion/contraction and context. Avoid framing every band touch or squeeze as a signal. |
| Volume & Price Analysis | volume price analysis; reading volume with price | Explain what activity and price achievement can show; do not imply volume alone confirms direction. |
| Candlestick Patterns | candlestick patterns in trading; reading candle formations | Keep formations contextual: location, sequence and invalidation matter. |
| Risk Management Basics | trading risk management; position sizing; trade invalidation | Prioritize exposure, sizing and predefined risk rather than promising loss avoidance. |
| Moving Averages | moving averages in technical analysis; trend context | Explain what averages summarize and their limitations; avoid crossover-as-signal positioning. |
| Options Basics | options trading basics; option premium and expiry | Make instrument mechanics and risk explicit; do not make return claims. |
| Market Structure | market structure in trading; trend and range; swing highs and lows | Focus on describing structure and alternative interpretations. |
| Understanding ADX | ADX indicator; using ADX to assess trend strength | Explain what ADX measures and what it does not establish. |

Do not create thin pages just to target these phrases. A course overview should be published only when it has a meaningful explanation, a clear learning outcome, accurate status and a stable URL. Hidden, preview-only and in-development material must stay out of the public sitemap.

## Internal-linking plan

1. **Homepage → catalogue and learning routes.** Keep one clear route to the catalogue and contextual links to the Trading Path, CONSTRUCT and live classroom. The current homepage already has these links; preserve them.
2. **Catalogue → exact course overview.** The catalogue is hydrated from the Academy catalogue API. Preserve the current publication gate: expose a direct course link only when the Academy record is published and supplies an `academyUrl`; keep “coming soon” items informational and hidden records out of the catalogue. Each available course card should lead to its own canonical Academy overview, not a generic dashboard or an ambiguous modal-only destination.
3. **Learning progression → relevant next step.** Trading Path can point to CONSTRUCT for deeper guided practice; CONSTRUCT can point to the live classroom only as a different learning format. Explain the distinction rather than repeating the same CTA everywhere.
4. **Course overview → related learning.** Link to one or two genuinely complementary topics and back to the catalogue. Use descriptive link text such as “learn the foundations of chart structure,” not repeated “click here” labels.
5. **Community → learning context.** Link to the relevant learning route without presenting community discussion as a substitute for a course or individualized financial advice.

## Structured-data and indexation findings

- The static builder currently includes six public routes in `PUBLIC_PAGES`; its sitemap should remain limited to those routes until the route inventory changes deliberately.
- Its catalogue `ItemList` currently describes the three flagship offers. The visible catalogue data also contains nine micro-course records. Reconcile this before expanding the schema: include only offers that are visibly represented, have a stable public destination and are genuinely published. Do not invent destination URLs or mark a “coming soon” course as an available offer.
- Catalogue cards are hydrated client-side from the Academy catalogue API; their direct destinations are supplied by published Academy records rather than hard-coded in the static course data. Preserve that source of truth when improving crawlability.
- Academy course overview pages are the correct place for course-specific metadata and Course structured data once the Phase 1–2 changes are merged and the corresponding course is published and indexable.
- The browser-only Support & Resistance Learning Room, member access, member-area preview, admin/editor previews and other review pages are not public acquisition pages. Keep them `noindex, nofollow` and out of the sitemap.
- The staging robots file currently has no sitemap declaration and the sitemap is empty. Keep `TRADETHESIS_SEO_INDEXABLE=false` on staging. Do not change canonical base URLs or enable indexing until the permanent public domain is confirmed.

## Validation and next decisions

**Implemented in this phase**
- Distinct title and description copy for each of the six public pages.
- A regression test requiring every indexable public page to have a distinct title and a concise meta description.

**Do after the public domain is selected**
1. Verify the final canonical URLs, robots response and sitemap in production before enabling indexing.
2. Create/verify Google Search Console ownership and submit the final sitemap.
3. Use actual query impressions, clicks and landing-page data to refine this map. Do not infer demand from the phrase list alone.
4. Revisit course-topic targets when Academy overview URLs and publication states are confirmed.
5. Reconcile the course catalogue ItemList schema with the actual public course destinations; add breadcrumb structured data only if the rendered page hierarchy supports it.

**Not included:** deploying, switching staging to indexable, selecting a domain, creating thin course pages, or changing public course claims/pricing.
