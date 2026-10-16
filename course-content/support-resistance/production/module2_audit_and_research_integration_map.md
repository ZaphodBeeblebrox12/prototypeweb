# Module 2 Audit and Research-Integration Map

**Module:** 2 — Find the important areas  
**Lessons:** 3–5  
**Status:** Lessons 3–5 are integrated in the learning-room preview. The learner-language and chart-led editorial passes for this Module 2 slice are complete and their changes passed isolated browser QA. Shared lesson tabs and the Clear W task have targeted automated keyboard coverage. Four axe-core scans (Lesson 5 initial/classification and Clear W initial/comparison) reported zero violations in the accessibility-focused run. Manual screen-reader/assistive-technology testing, a broader manual keyboard review and real-learner usability/timing remain outstanding. Learner responses and progress are browser-local, not member-account persistence.  
**Working standard:** `production/MODULE_DEPTH_WORKING_NOTES.md`  
**Template redesign:** Deferred; not part of this pass.

## Executive finding

The canonical scripts for Lessons 3–5 provide the teaching sequence, reveal plans, model-answer guidance and assessment intent. Lessons 3–4 expose staged explanations, learner gates and three formative checks each. Lesson 5 now adds a seven-candidate Keep/Combine/Leave-out/Not-sure activity, two incremental edit states, a worked reduction, then the Clear W drawing lab with sequential support/resistance submission, reference feedback and two post-lab checks.

The asset pack contains the specified Lesson 3–5 / Clear W PNG chart states and SVG counterparts, including Lesson 3 candidate-ID practice and the incremental Lesson 5 edit states. Lesson 4 now follows observation-before-terminology: learners compare the differing lowest prices first, then receive a plain-language definition of wick, body and close on the next revealed view. Clear W describes its two lows and intervening swing high in plain language, labels its candles as synthetic without an invented timeframe, and provides a side-by-side visual comparison without pretending to score the learner's reasoning. The dedicated learner-language and chart-led passes are complete for this slice; the wider template comparison remains deferred.

## 1. Lesson-by-lesson gap matrix

| Lesson | Keep | Deepen in the learner experience | Add / implement only where required |
|---|---|---|---|
| **3 — Identify meaningful swing points** | The three judgement filters: relative prominence, structural role and relevance to the current question. Keep this qualitative—not a numeric “swing strength” score—and accept evidence-based alternatives. | Implemented as 10 staged views: unmarked path, neutral candidate IDs, three reasoning filters, a four-point reference, simplified view, independent clean/candidate states and an alternative-tolerant model answer with field-note transfer. The four-point reference set was regenerated to match the explicit exercise constraint. | The accessible candidate buttons allow up to four selections; rationale is required before reveal unless the learner explicitly chooses “I am not sure yet.” Selection and notes are browser-local. Desktop and 360px mobile browser QA passed. Automated keyboard testing verified lesson selection, Tab/Space candidate toggles, the four-point cap, rationale entry and the gated reveal. Manual screen-reader/assistive-technology testing remains outstanding. |
| **4 — Zones, not perfect lines** | Keep the distinction between related reactions as an area and one exact price. Wicks, bodies and closes inform boundary decisions; none is a universal rule. Keep this as boundary judgement, not a ChartLab. | Implemented as 11 staged views: lower reactions, broad bracket, too-narrow band, defensible band, too-broad band and same-scale comparison; upper-side transfer; and independent practice/reference with field-note transfer. | Each fresh practice view requires a new attempt. The opening state asks learners to compare the lowest prices before introducing wick/body/close terminology in the next reveal. Width comparisons use the same candles and do not depend on pixel-perfect scoring. The three formative checks have explanatory feedback. Browser automation verifies the staged wording order; the individual Lesson 4 quiz has not been exercised end-to-end by keyboard. Manual screen-reader/assistive-technology review remains outstanding. |
| **5 — Choose the right areas and reduce clutter** | Keep the transition from editing a crowded chart to a first full two-zone drawing. The two-area result is the worked reference for this synthetic example only; it is not a universal target or maximum. | Implemented as six staged views: unclassified clutter, candidate IDs with incremental Keep/Combine/Leave-out/Not-sure classification, remove one minor mark, combine nearby bands, show the worked two-area edit, then hand off to Clear W. | The editing form requires a classification for each of seven candidates plus a short rationale before revealing the model edit. Clear W is embedded from the existing self-contained ChartLab prototype. Its synthetic data is not assigned an unsupported real timeframe. Its keyboard-accessible upper/lower price fields provide a pointer-free way to set a zone. Automated keyboard QA verifies ordered support submission/locking, resistance submission, reference gating, comparison focus, two post-lab checks and completion. The comparison asks the learner to examine both drawings; it does not score written reasoning or assign an overlap percentage. Manual screen-reader/assistive-technology review and real-learner usability remain open. This remains a preview, not account-backed progress or secure server-side assessment. |

### Existing asset sequences to wire in

**Lesson 3 — ten views**
- `L03-A-01-clean` → `L03-A-02-candidate-turns` → `L03-A-03-reference-points` → `L03-A-04-simplified`
- Separate practice: `L03-B-01-practice` → `L03-B-01-candidate-turns` → `L03-B-02-reference`

**Lesson 4 — eleven views**
- Lower reactions: `L04-A-01-clean` → `L04-A-02-broad-bracket` → `L04-A-03-too-narrow` → `L04-A-04-defensible-zone` → `L04-A-05-too-broad` → `L04-A-06-compare`
- Upper-side transfer: `L04-B-01-clean` → `L04-B-02-zone` → `L04-B-03-resistance`
- Separate practice: `L04-C-01-practice` → `L04-C-02-reference`

**Lesson 5 — five clutter-chart states leading into the interactive Clear W exercise**
- Editing: `L05-A-01-overmarked` → `L05-A-02-candidate-ids` → `L05-A-04-minor-removed` → `L05-A-05-nearby-combined` → `L05-A-03-reduced-reference`
- Clear W reference assets: `CL01-01-clean` → `CL01-02-support-reference` → `CL01-03-resistance-reference` → `CL01-04-combined-reference`. These images accompany the exercise; they do not replace its sequential drawing interaction.

The asset manifest labels these as synthetic illustrative OHLC charts. Keep the illustrative/not-historical distinction visible. Lesson 5's reveals, real drawing/submission flow, mobile comparison layout and completion gate were tested separately; evidence and the remaining limitations are recorded in §6.

## 2. Research and curriculum integration

The existing `curriculum/master_curriculum_blueprint.md` and lesson scripts already contain the source rationale. Reuse that work rather than attach famous titles as decoration.

| Source contribution | What the existing source notes support | TradeThesis synthesis for Module 2 | Learner outcome |
|---|---|---|---|
| **John J. Murphy — *Technical Analysis of the Financial Markets*** | Broad conventional technical-analysis terminology, including support/resistance and prior highs/lows. This is foundational framing, not evidence of one exclusive drawing method. | Use familiar chart vocabulary, then require the learner to explain their selection and boundaries in plain language. | Explain why a turn or reaction is being used without treating a textbook convention as a universal rule. |
| **Jack D. Schwager and Mark Etzkorn — *A Complete Guide to the Futures Market*, Chapters 7–8** | The publisher chapter summaries cover trading ranges, range boundaries, major prior highs/lows and support/resistance concepts. They do not imply that every past high or low must be marked. | In Lesson 3, distinguish structural turns from minor fluctuations. In Lesson 5, evaluate whether each mark adds useful information to the current reading. | Select a smaller explainable set of turns/areas and justify what was omitted. |
| **Adam Grimes — *The Art and Science of Technical Analysis*, especially Chapters 4–6** | The existing research map highlights the complexity of support/resistance, range behaviour and uncertain transitions between trends and ranges. It is a critical counterweight to treating conventional markings as automatically predictive. | Use the narrow/defensible/broad comparison to teach boundary trade-offs, not a formula. Allow uncertainty and reasonable alternatives where the chart supports them. | Defend a boundary by describing what it includes and excludes; acknowledge where precision would exceed the evidence. |
| **Carol L. Osler — FX support/resistance/order research** | The cited research concerns particular FX firms, currency pairs, time periods and order data. It can inform evidence literacy, but it does not validate every manually drawn zone or a universal retail rule. | No new empirical detour is needed in Lessons 3–5. Do not use this research to claim that a selected swing or hand-drawn band predicts a future outcome. | Separate a visible chart observation from a causal claim or a prediction. |
| **Brian Shannon — *Technical Analysis Using Multiple Timeframes*** | A supplementary perspective on higher-timeframe context, not a universal hierarchy. | Leave multiple-timeframe workflows out of this module; they are not needed to teach swing selection, zone width or chart editing. | Focus on the chart and question in front of the learner. |

### Source limits and attribution

The previous source-integration work drew on publisher/author summaries, tables of contents and selected chapter abstracts, rather than exhaustive reading of every page of every book. Keep that limitation visible in instructor notes. In the learner room, explain these ideas in original TradeThesis wording and use the project's own charts. Do not imply that the three swing-selection filters, the keep/combine/leave-out choices or the narrow/defensible/broad visual comparison are a formula prescribed or empirically validated by any named author. They are original instructional scaffolds.

### TradeThesis catalogue cross-reference

The current catalogue contains **Market Structure**, but its topic substantially overlaps the foundational structure taught within this course. No cross-link is recommended in Lessons 3–5 for this pass: learners need these skills to progress through the current course, and sending them away is unlikely to resolve a distinct learning need. Reassess only if the final course-boundary review establishes a genuinely complementary topic. Do not invent a destination URL.

## 3. Current learner-room implementation check

| Requirement | Current status |
|---|---|
| Lesson 3 staged charts / selectable swing points | Implemented and browser-tested: 10 views, selectable candidate IDs, four-point exercise cap, rationale/uncertainty gate, independent practice and reference. |
| Lesson 4 boundary comparisons / upper-side transfer / independent practice | Implemented and browser-tested: 11 views, same-scale width comparisons, upper-side transfer, independent practice and reference. |
| Lesson 5 keep/combine/leave-out interaction | Implemented and browser-tested: seven candidate classifications, a short rationale, and staged remove/combine/omit/reduction reveals. This is a reasoning exercise, not a strict score. |
| Clear W drawing and submission state machine | Implemented and browser-tested inside the learning room using the standalone ChartLab prototype: support locks first; resistance is drawn second; the first mark stays visible; reference comparison and feedback wait until both are submitted. |
| Formative question set | Lessons 3 and 4 each show three multiple-choice checks with feedback. Clear W shows its two post-lab checks and reports session completion back to the parent lesson. |
| Answer/reveal security and persistence | Still preview-grade. Responses, selections and progress are browser-local, not account-backed or secured against direct inspection of static reference assets. |

## 4. Recommended implementation order

1. **Completed — Lesson 3:** wired the staged charts and accessible candidate selection, capped the exercise at four points, added rationale/uncertainty handling and revealed an independent practice/reference pair. The reference chart set was regenerated and checksums updated.
2. **Completed — Lesson 4:** wired all 11 existing views, the same-scale boundary comparisons, upper-side transfer and independent practice/reference.
3. **Completed — formative checks and browser QA:** integrated three formative checks for each of Lessons 3 and 4; automated desktop and 360px mobile checks passed. Targeted keyboard automation is green for lesson-tab navigation, Lesson 3 candidate selection, Lesson 4's observe-before-define sequence, and the complete Clear W flow. The latest learner-language and chart-led assertions passed in QA run #13.
4. **Completed — Lesson 5:** added the Keep/Combine/Leave-out/Not-sure interaction and stepwise chart edits, then embedded the existing Clear W drawing prototype. Support must be submitted and locked before resistance; both must be submitted before reference reveal; both knowledge checks must be completed before the parent lesson completion action unlocks.
5. **Next:** complete manual screen-reader/assistive-technology testing, broader manual keyboard review (especially Lesson 4's individual quiz), and a real-learner timing/usability check. The separate site-template comparison remains deferred.

## 5. Acceptance checklist for Module 2

- [x] Lesson 3 explains why selected and omitted turns matter and accepts an evidence-based alternative.
- [x] Lesson 3's four-point limit is explicitly an exercise constraint, not a universal market rule.
- [x] Lesson 4 compares boundary widths against the same underlying candles and discusses what each includes/excludes.
- [x] Lesson 4 accepts defensible alternative widths and does not use pixel-perfect matching as the sole score.
- [x] Lesson 5 editing rationales are integrated and match the synthetic chart geometry; seven candidate classifications gate the worked edit.
- [x] Clear W preserves the first submitted zone while the second is drawn, and reference comparison stays gated until both are submitted.
- [x] Three formative knowledge checks and explanatory feedback are integrated for each of Lessons 3 and 4.
- [x] The preview labels synthetic charts accurately and does not claim production-secured ChartLab or account persistence.
- [x] No numeric swing/zone-strength score or universal touch-count/zone-width rule is introduced.
- [x] Desktop reveal/drawing flow, two-question completion gate and 360px mobile overflow checks passed automated browser QA; targeted keyboard-only tests cover lesson tabs, Lesson 3 candidate selection, Lesson 4 observe-before-define ordering and Clear W through completion.
- [x] Learner-language editorial pass completed for this slice: first-use terminology is defined in context, staged wording follows the teaching sequence, and the Clear W instructions name visible chart features plainly.
- [x] Chart-led editorial pass completed for this slice: the five Lesson 5 clutter views match the documented edits, Clear W uses synthetic/not-historical labeling without a fabricated timeframe, and comparison feedback is descriptive rather than a numerical reasoning score.


## 6. Verification record — 16 October 2026

**Latest interaction and chart-led QA:** [Temporary Lesson 5 Clear W workflow, run #13](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/38855666755) passed on the isolated QA branch. The temporary workflow is for verification only and is not promoted into the normal development branch.

The run passed the Lesson 5 staged sequence, all seven candidate classifications and rationale gate, pointer-driven support/resistance drawing, sequential submission and locking, reference gating, both post-lab questions, and the parent lesson completion gate. It also ran keyboard interaction checks for the Lesson 3 selector, lesson tabs, the Lesson 4 first-observe/second-explain sequence, and the pointer-free Clear W price-entry route. The tests assert no browser JavaScript page errors and no HTTP responses at or above 400. This is automated Playwright evidence, not proof of a manual screen-reader audit.

**Lesson 4 teaching sequence:** the first view now asks the learner to compare the three lowest prices without defining wick/body/close. The second view defines the terms in plain language and connects them to the same chart. The browser test verifies the response gate and stage order.

**Clear W chart-led accuracy:** the synthetic candles are not labelled as a real timeframe. The introduction describes support around the two lows and resistance around the intervening swing high (the neckline). After both zones are submitted, the learner's locked zones are shown beside one defensible reference. Feedback asks the learner to compare coverage and boundaries; it explicitly states that it does not score written reasoning and does not show a percentage score. The later move visible in the synthetic sequence is not a prediction or a promise of continuation.

**360px mobile check:** the parent document measured 360px viewport / 360px scroll width, with a 302px-wide embedded ChartLab. Inside the iframe, viewport and document scroll width both measured 302px; the submitted comparison was visible and both comparison SVGs measured 270px wide. No horizontal overflow was detected by the assertions.

**Asset integrity:** the manifest has exactly one row each for `L05-A-04-minor-removed` and `L05-A-05-nearby-combined`. The current regenerated SVGs and their PNG counterparts have one current checksum entry each. The PNGs were visually inspected: A04 removes D only, and A05 combines B/C and E/F while retaining A and distant G. The edits use the same synthetic candles and scale, labelled “Illustrative chart — not historical market data.”

**Automated accessibility check — [isolated QA run](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/38857318478):** The run scanned four states with axe-core against WCAG 2 A/AA and WCAG 2.1 A/AA tags: Lesson 5 initial, Lesson 5 candidate-classification, Clear W initial, and Clear W comparison. Each returned `violationCount: 0`. The same run passed an automated keyboard smoke test for lesson-tab arrow navigation, numeric zone creation, support-before-resistance lock order, comparison focus, quiz, and completion. Browser JavaScript and HTTP error assertions also passed. These results are bounded to the tested states and automated checks; they do not establish full WCAG conformance and do not replace a manual keyboard review, screen-reader/assistive-technology testing, or real-learner usability/timing.

**Editorial status:** the learner-language and chart-led passes are complete for the Lesson 3–5 implementation described here. They do not constitute a full-course editorial closeout or replace a real learner test.

**Still outstanding:** real screen-reader/assistive-technology testing; a broader manual keyboard-navigation review, especially Lesson 4's individual quiz; real-learner timing/usability testing; and the separate course-template comparison. Automated browser checks do not substitute for those reviews.

**Persistence and assessment limits:** learner answers and completion remain local to the browser/prototype; there is no member-account progress persistence or server-secured assessment storage. The reference charts are static assets, not protected answer keys. The synthetic sample is illustrative, not historical data.

**Decision:** Build from the existing scripts/assets. The primary gap is learner-room integration and specific interaction behaviour—not a lack of source material and not a need for a new template.
