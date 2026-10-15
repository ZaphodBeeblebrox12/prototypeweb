# Module 2 Audit and Research-Integration Map

**Module:** 2 — Find the important areas  
**Lessons:** 3–5  
**Status:** Audit complete; implementation plan only. This document does not rewrite the canonical production scripts or claim the planned interactions already exist.  
**Working standard:** `production/MODULE_DEPTH_WORKING_NOTES.md`  
**Template redesign:** Deferred; not part of this pass.

## Executive finding

The canonical scripts for Lessons 3–5 contain a coherent teaching sequence, example-by-example reveal plans, model-answer guidance and assessment intent. The current learning room renders only a summary, one practice prompt, a static first chart and a single multiple-choice question for each of these lessons. It does not yet expose the richer sequences described in the scripts.

The required chart material is **not missing**. A repository check found all 24 specified Lesson 3–5 / Clear W PNG chart states and their 24 SVG counterparts in `chart_assets/charts/`. The internal knowledge-check bank also contains three checks each for Lessons 3 and 4, plus the two checks intended after the Lesson 5 ChartLab. The next work should integrate these existing materials and add only the interaction mechanics the learning objective truly requires—not invent substitute charts or pad the scripts.

## 1. Lesson-by-lesson gap matrix

| Lesson | Keep | Deepen in the learner experience | Add / implement only where required |
|---|---|---|---|
| **3 — Identify meaningful swing points** | The three judgement filters from the script: relative prominence, structural role and relevance to the current chart question. Keep the explicit rule that this is a qualitative reasoning scaffold, not a numeric “swing strength” score. Keep a separate unseen practice chart and accept defensible alternative point selections. | Show the over-marked chart first; reveal candidate points; teach one filter at a time; then reveal the reference selection sequentially with a reason for each kept point and at least two omitted candidates. The simplification should make the chart easier to explain. Finish with a field note that states which turns were retained, why smaller turns were omitted, and where another reading may be reasonable. | Provide accessible tap-to-select candidate points, a task limit such as “choose up to four” that is explicitly labelled as an exercise constraint, and a short rationale for the selection. Include a keyboard/accessibility equivalent; do not require precise dragging. The current single-chart prompt does not let the learner select points or compare the six existing staged states. |
| **4 — Zones, not perfect lines** | The central distinction: related reactions can occupy an area without sharing one exact price. Wicks, bodies and closes are different views of the same price action; no one reference is universally mandatory. Keep boundary judgement separate from a complete drawing lab. | Keep the candle sequence and scale fixed while comparing a too-narrow band, one defensible band and an overly broad band. Explain what each includes and excludes. Then transfer to the separate upper-reaction chart and an unseen independent-practice chart. Model reasoning rather than pixel-perfect overlap; identify acceptable alternatives. | Use the existing staged assets as a simple comparison/reveal interaction. Add an accessible choice and short written rationale for the independent chart. Do not add arbitrary tick/percentage/ATR width rules, a magic zone score or a fourth ChartLab. The current learning room exposes only the unmarked lower-reaction chart and a single question. |
| **5 — Choose the right areas and reduce clutter** | The progression from editing a cluttered chart to the first complete drawing attempt. Keep ChartLab Study 1 **Clear W** here, after Lessons 1–4. The “three or four primary areas” constraint is a practice aid, never a universal maximum. | On the over-marked chart, reveal keep/combine/leave-out decisions one at a time, each with a reason tied to the actual drawing. Make clear that “leave out for this reading” does not mean “never relevant.” Then hand off to Clear W, with separate reasoning for the lower support area and intervening upper resistance area. | The selection task needs a real Keep / Combine / Leave out / Not sure interaction, an editable first attempt and a submission step. Clear W requires an actual zone-drawing interaction: submit support first, preserve it while drawing resistance, submit the second zone, and only then unlock reference comparison and tailored feedback. The current page merely displays `CL01-01-clean.png`; the “ChartLab” label is not a working drawing lab. Do not simulate this with a static reference image or claim that submission, persistence or secure answer gating exists before it is implemented and tested. |

### Existing asset sequences to wire in

**Lesson 3 — six views**
- `L03-A-01-clean` → `L03-A-02-candidate-turns` → `L03-A-03-reference-points` → `L03-A-04-simplified`
- Separate practice: `L03-B-01-practice` → `L03-B-02-reference`

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
| Lesson 3 staged charts / selectable swing points | Not wired into the learning room. Lesson 3 has a single static chart, one general prompt and one quiz item. |
| Lesson 4 boundary comparisons / upper-side transfer / independent practice | Not wired into the learning room. The initial lower-reaction chart and one quiz item are shown. |
| Lesson 5 keep/combine/leave-out interaction | Not implemented. The over-marked chart states exist but are not connected to the lesson UI. |
| Clear W drawing and submission state machine | Not implemented. The page displays the initial Clear W image and has a single general quiz item. |
| Formative question set | The internal bank already contains three questions for each of Lessons 3 and 4. Lesson 5's production script specifies two checks after ChartLab. The current room's `quiz` field supports only a single question per lesson, so assessment integration needs to account for the existing bank rather than authoring duplicate questions. |
| Answer/reveal security and persistence | Not production-secured. The preview must not be described as account-backed, reliably persisted across devices or secure against reading reference files directly. |

## 4. Recommended implementation order

1. **Lesson 3:** wire the existing staged charts, implement accessible candidate-point selection, capture a short rationale, reveal reference points sequentially, then show the independent practice/reference pair.
2. **Lesson 4:** wire the boundary-comparison states and the upper-side transfer, then add the independent practice/reference. Preserve a constant chart scale for the comparisons.
3. **Lesson 5:** build the keep/combine/leave-out activity first, then implement the actual two-zone Clear W ChartLab with the required submission gates and preserved first drawing. Do not mark Lesson 5 complete because its chart is visible.
4. **Assessment integration:** support the existing three-question bank for Lessons 3–4 and the two post-lab checks for Lesson 5, with explanatory feedback. Keep internal keys separate from the learner experience.
5. **QA:** test desktop, 360px mobile, keyboard/touch operation, back/forward/revisit, submission before reveal, preservation of drawings, image loads, and realistic failure/retry behaviour. Mark anything untested.
6. Only after those checks, run the learner-language and chart-led editorial passes. The separate site-template comparison remains deferred.

## 5. Acceptance checklist for Module 2

- [ ] Lesson 3 teaches why each selected and omitted turn matters, with a defensible alternative accepted.
- [ ] Lesson 3's point limit is visibly a task constraint, not a universal market rule.
- [ ] Lesson 4 compares boundary widths against the same underlying candles and asks what each includes/excludes.
- [ ] Lesson 4 accepts defensible alternative widths and never uses pixel-perfect matching as the sole score.
- [ ] Lesson 5 editing rationales match the actual synthetic chart geometry.
- [ ] Clear W preserves the first submission while the second zone is drawn, and reference comparison stays gated until both have been submitted.
- [ ] The existing knowledge-check questions and feedback are integrated without exposing internal keys early.
- [ ] The preview labels synthetic charts accurately and does not claim a production-secured ChartLab or account persistence.
- [ ] No numeric swing/zone-strength score or universal touch-count/zone-width rule is introduced.
- [ ] Mobile, accessibility and reveal behaviour are tested; no result is reported as tested without evidence.

**Decision:** Build from the existing scripts/assets. The primary gap is learner-room integration and specific interaction behaviour—not a lack of source material and not a need for a new template.
