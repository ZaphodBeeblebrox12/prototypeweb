# Module 2 Audit and Research-Integration Map

**Module:** 2 — Find the important areas  
**Lessons:** 3–5  
**Status:** Lessons 3–5 are integrated in the learning-room preview and browser-tested. Lesson 5 includes an incremental clutter-edit activity and the embedded Clear W two-zone ChartLab. Responses/progress are local to the browser session, not member-account persistence.  
**Working standard:** `production/MODULE_DEPTH_WORKING_NOTES.md`  
**Template redesign:** Deferred; not part of this pass.

## Executive finding

The canonical scripts for Lessons 3–5 provide the teaching sequence, reveal plans, model-answer guidance and assessment intent. Lessons 3–4 expose staged explanations, learner gates and three formative checks each. Lesson 5 now adds a seven-candidate Keep/Combine/Leave-out/Not-sure activity, three incremental edit views, a worked reduction, then the Clear W drawing lab with sequential support/resistance submission, reference feedback and two post-lab checks.

The corrected asset pack now contains 27 specified Lesson 3–5 / Clear W PNG chart states and their SVG counterparts, including candidate-ID practice for Lesson 3 and two incremental Lesson 5 editing states. Lessons 3–4 use three formative questions each; Clear W includes the two post-lab questions specified in its standalone answer key. The remaining work is a separate keyboard/screen-reader audit and later editorial/template passes—not the core Lesson 5 interaction.

## 1. Lesson-by-lesson gap matrix

| Lesson | Keep | Deepen in the learner experience | Add / implement only where required |
|---|---|---|---|
| **3 — Identify meaningful swing points** | The three judgement filters: relative prominence, structural role and relevance to the current question. Keep this qualitative—not a numeric “swing strength” score—and accept evidence-based alternatives. | Implemented as 10 staged views: unmarked path, neutral candidate IDs, three reasoning filters, a four-point reference, simplified view, independent clean/candidate states and an alternative-tolerant model answer with field-note transfer. The four-point reference set was regenerated to match the explicit exercise constraint. | The accessible candidate buttons allow up to four selections; rationale is required before reveal unless the learner explicitly chooses “I am not sure yet.” Selection and notes are browser-local. Desktop and 360px mobile browser QA passed. Keyboard-only/screen-reader testing remains a separate check. |
| **4 — Zones, not perfect lines** | Keep the distinction between related reactions as an area and one exact price. Wicks, bodies and closes inform boundary decisions; none is a universal rule. Keep this as boundary judgement, not a ChartLab. | Implemented as 11 staged views: lower reactions, broad bracket, too-narrow band, defensible band, too-broad band and same-scale comparison; upper-side transfer; and independent practice/reference with field-note transfer. | Each fresh practice view requires a new attempt. The boundary sequence explicitly teaches what each band includes/excludes and does not use pixel-perfect scoring. The three formative checks per lesson are wired with explanatory feedback. Desktop and 360px mobile browser QA passed. |
| **5 — Choose the right areas and reduce clutter** | Keep the transition from editing a crowded chart to a first full two-zone drawing. Keep the “three or four primary areas” limit as an exercise constraint, not a universal maximum. | Implemented as six staged views: unclassified clutter, candidate IDs with incremental Keep/Combine/Leave-out/Not-sure classification, remove one minor mark, combine nearby bands, show the worked two-area edit, then hand off to Clear W. | The editing form requires a classification for each of seven candidates plus a short rationale before revealing the model edit. Clear W is embedded from the existing self-contained ChartLab prototype. The learner draws/submits support, which locks; draws/submits resistance while support remains visible; only then sees reference comparison and tailored feedback. The two post-lab questions and a completion gate are active. Browser QA passed the complete desktop flow and mobile overflow checks. This remains a preview, not account-backed progress or secure server-side assessment. |

### Existing asset sequences to wire in

**Lesson 3 — ten views**
- `L03-A-01-clean` → `L03-A-02-candidate-turns` → `L03-A-03-reference-points` → `L03-A-04-simplified`
- Separate practice: `L03-B-01-practice` → `L03-B-01-candidate-turns` → `L03-B-02-reference`

**Lesson 4 — eleven views**
- Lower reactions: `L04-A-01-clean` → `L04-A-02-broad-bracket` → `L04-A-03-too-narrow` → `L04-A-04-defensible-zone` → `L04-A-05-too-broad` → `L04-A-06-compare`
- Upper-side transfer: `L04-B-01-clean` → `L04-B-02-zone` → `L04-B-03-resistance`
- Separate practice: `L04-C-01-practice` → `L04-C-02-reference`

**Lesson 5 — three editing views plus the four Clear W states**
- Editing: `L05-A-01-overmarked` → `L05-A-02-candidate-ids` → `L05-A-03-reduced-reference`
- Clear W: `CL01-01-clean` → `CL01-02-support-reference` → `CL01-03-resistance-reference` → `CL01-04-combined-reference`

The file manifest calls these synthetic illustrative OHLC charts. They must remain labelled illustrative, not be passed off as historical market data. Their presence in the repository is not evidence that each reveal, mobile crop, selection interaction or ChartLab submission flow is implemented.

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
3. **Completed — formative checks and browser QA:** integrated three formative checks for each lesson; automated desktop browser flow and 360px mobile layout checks passed. Keyboard-only/screen-reader testing and live learner editorial review remain outstanding.
4. **Completed — Lesson 5:** added the Keep/Combine/Leave-out/Not-sure interaction and stepwise chart edits, then embedded the existing Clear W drawing prototype. Support must be submitted and locked before resistance; both must be submitted before reference reveal; both knowledge checks must be completed before the parent lesson completion action unlocks.
5. **Next:** run the keyboard-only/screen-reader audit, then the learner-language and chart-led editorial passes. The separate site-template comparison remains deferred.

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
- [x] Desktop reveal/drawing flow, two-question completion gate and 360px mobile overflow checks passed automated browser QA; keyboard-only and screen-reader QA remain outstanding.

**Decision:** Build from the existing scripts/assets. The primary gap is learner-room integration and specific interaction behaviour—not a lack of source material and not a need for a new template.
