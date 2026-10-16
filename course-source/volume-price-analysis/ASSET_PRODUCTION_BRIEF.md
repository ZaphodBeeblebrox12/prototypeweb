# Asset Production Brief — Read Volume. Find Trade Setups.
## Course visuals, ChartLabs, worksheets and delivery files

**Status:** Production specification plus one pilot package for M01-L01. The pilot includes an editable SVG chart master/export, synthetic data, accessibility notes, a learner-facing ChartLab prototype, instructor answer notes and a package manifest. The other 29 lesson packages have not yet been produced. No public course pages have been changed.
**Scope:** Six modules, 30 lessons. This brief consolidates the inline `ASSET` and `CHARTLAB` notes in the lesson scripts into a buildable checklist.
**Audience:** People who are new to reading market charts.
**Core promise:** Help learners read recorded volume alongside price, recognise useful context, and construct conditional trade plans. This is not a general-indicator course.

---

## 1. The question every asset must answer

**Does this asset add real learning value, or is it here just because a course usually has images and exercises?**

For every chart, illustration, worksheet or interaction, the production owner must be able to answer: *What will a beginner be able to notice, explain or do because this asset exists?* If that answer is vague, redesign the asset or remove it.

An asset is not finished because it looks attractive. It is finished when it teaches a specific distinction, makes an explanation easier to follow, gives the learner a meaningful practice opportunity, and passes the quality checks below.

## 2. Core deliverables

### Required for teaching production

1. **30 lesson visual packages** — one principal chart, diagram or worksheet visual for each lesson, with alternate cases where specified below. Some lessons require several panels or staged outcomes.
2. **30 ChartLabs** — one exercise per lesson. Each must include a learner prompt, a place to respond or annotate, staged chart reveals where relevant, model answer or answer notes, scoring criteria, and a counterexample.
3. **One reusable chart design system** — consistent candle, volume, level, annotation, label and callout styles.
4. **Source data and editable masters** — synthetic OHLCV data and source files for every invented chart, or permission/source records for licensed data.
5. **Accessibility package** — meaningful alt text, longer descriptions for complex charts, readable labels, and captions/transcripts for recorded teaching.
6. **Learner-facing feedback** — model answers and reasoning notes that explain why an answer is sound, what remains uncertain, and which next observation would change the reading.
7. **Worksheets** — blank and worked versions of the course's context note, evidence sheet, two-scenario thesis canvas, pre-trade ticket and capstone review.

### Required before publishing recorded lessons

- Final chart exports in the required sizes and the editable source used to make each export.
- Captions/subtitles in VTT or SRT format, checked against the final recording.
- A clean lesson transcript or accessible narration text matching the final recording.
- Correct asset credits, data notes, labels and alt text.
- A final check that no illustration implies guaranteed profit, identifies a real trader's motive without evidence, or presents a synthetic example as historical market data.

### Optional, later website-marketing assets

These are useful only when the public course pages are ready; they are not prerequisites for teaching the lessons and should not delay them:
- One course thumbnail/cover.
- Six consistent module thumbnails.
- A course hero illustration or banner.
- Promotional/social crops derived from approved assets.

Do not create all 30 charts and then invent a marketing theme around them. First establish the course's consistent light visual system, then use it for lesson charts and any later thumbnails.

---

## 3. Visual and chart design system

### Visual direction
- Use a **clean, light, editorial style**. It should look like a carefully prepared trading publication, not a broker platform screenshot or a dashboard crowded with indicators.
- Keep the chart itself dominant. As a starting layout, reserve roughly two-thirds of a teaching frame for the chart and the rest for a small number of notes or a focused question.
- Use one visual question per frame. Split a complex explanation into steps instead of shrinking all labels until they are unreadable.
- Use concise plain-English labels. Introduce technical terms next to their everyday explanation.
- Use the same candle shapes, volume bars, line styles, price-zone styles, typography and callout rules across all 30 lessons.
- A green candle means the candle closed above its open; it does **not** automatically mean the market is bullish. Red/green colour must never carry the entire meaning: add labels, position and pattern context.
- Avoid decorative arrows, large buy/sell stamps, profit badges, fake terminal chrome, broker branding and unnecessary indicators.

### Default export and source requirements
- **Teaching master:** 16:9 layout, designed at 1920 × 1080 or as a vector master that scales cleanly to that size.
- **Web delivery:** PNG or WebP for chart-heavy images; SVG for crisp vector diagrams when the hosting stack permits it. Do not export tiny text as a raster image.
- **Editable master:** SVG, source plotting code, or a documented editable design file. The choice may vary by asset, but the team must not end up with only a flattened image.
- **Responsive use:** create a reflowed mobile version when the chart or text becomes illegible on a narrow screen. Do not make the mobile version by blindly shrinking a 16:9 image.
- **Colour and contrast:** meet readable contrast for small labels; distinguish primary evidence, secondary notes and hypothetical alternatives consistently. Never use colour alone to encode a pass/fail or bullish/bearish distinction.
- **Typography:** use one heading style, one chart-label style and one annotation style. Price/time labels and labels used during screen teaching must stay legible at normal playback size.
- **Annotations:** identify what is observed separately from what is an interpretation. Use wording such as “consistent with,” “possible reading,” “evidence still needed,” and “would weaken this idea.”
- **Market context:** state the instrument or synthetic scenario, timeframe, selected date/session or profile period, volume data type and comparison baseline wherever these details affect the lesson.

### Synthetic data, licensing and honest labelling
- Use **synthetic OHLCV data by default**. Make the chart realistic enough to teach structure but simple enough that a learner can follow it.
- Label synthetic examples visibly as **“Synthetic teaching example — not historical market data.”**
- For licensed or historical data, record source/provider, instrument, timeframe, date range, timezone/session, rights/permission, and any edits or omissions. Keep the underlying unedited data if edits are made for teaching.
- Never fabricate broker logos, transaction prints, order-flow details, named institutions or precise historical claims.
- For retail spot-FX tick volume, state that the chart may count price updates from that provider rather than all market trades. For crypto, identify the venue and its data definition. Do not imply that different feeds' volume values are directly interchangeable.
- Where an example relies on a baseline, show the baseline or state how it was chosen. If session timing makes a comparison misleading, demonstrate the limitation.

### Accessibility package for every visual
Every asset must include:
1. **Alt text** (normally one or two sentences) describing the purpose and the most important visible distinction.
2. **Extended description** for a chart with several stages, multiple outcomes or dense annotations.
3. **Text equivalent** of the key lesson: what the learner should observe and what cannot be concluded.
4. **Readable labels and captions**; no meaning communicated only by colour, line thickness or position.
5. **Source/data note** adjacent to the asset or in its linked metadata.

Alt text describes the chart's useful information, not merely “a chart with candles.”

---

## 4. Asset naming and folder structure

Use stable IDs so a chart, its data, its lab and its answer notes can be connected.

**Filename pattern**
`vpa-m{module}-l{lesson}-{short-description}-{type}.{ext}`

Examples:
- `vpa-m01-l01-candle-context-compare.svg`
- `vpa-m01-l01-candle-context-compare.png`
- `vpa-m01-l01-candle-context-data.csv`
- `vpa-m01-l01-candle-context-alt.txt`
- `vpa-m01-l01-candle-context-lab.md`

**Proposed production folder structure**
```text
course-source/volume-price-analysis/
  assets/
    README.md
    source/
    exports/
    data/
    alt-text/
    worksheets/
    lab-specs/
    captions/
    credits/
```

Keep this document as the source specification. When asset creation starts, the assets folder should contain real files—not placeholders named as if they were already complete.

Each asset package must include: stable asset ID, linked module/lesson, teaching purpose, editable source, final export, source/data notes, alt text, extended description when required, and a QA status. For interactive labs add prompt, reveal states, input format, answer notes and scoring rules.

---

## 5. Required lesson visual and ChartLab inventory

Each item below describes both the visual deliverable and the learning task that depends on it. The matching script comments remain the lesson-level reference; this inventory is the consolidated production checklist.

### Module 1 — Read the Market Behind the Candles

| ID | Lesson visual to produce | ChartLab / interaction to build |
|---|---|---|
| M01-L01 | Two-panel comparison: similar-looking candles in different chart locations and with different local volume context. Include candle/volume labels and baseline. | Learner records prior structure, candle result, relative activity and follow-through needed on two snippets. Reveal plausible alternatives rather than a single guaranteed answer. |
| M01-L02 | Relative-volume visual with plain volume bars, a visible baseline, and contrasting examples where an opening spike is normal for that time but unusual against all-day bars. | Give the learner 12 synthetic volume bars and a final candidate bar. Classify it against recent bars, then a time-matched baseline; require two reasons the reading could change. |
| M01-L03 | One clearly labelled candle showing open, high, low, close, body, range, upper/lower wick and close location, with three synthetic candles tested at the same range high. | Learner annotates six unlabeled bars, then records observation, possible meaning and an alternative explanation. Score chart description separately from interpretation. |
| M01-L04 | Two comparable sequences: a quiet pullback that holds a breakout area and a low-activity breakout attempt that returns into the range. | Learner classifies low-volume cases by context (trend pullback, range middle, range boundary, event session), offers two possible explanations and names the next evidence needed. |
| M01-L05 | Three market-data panels: exchange-reported equity/futures volume, retail spot-FX tick volume, and venue-specific crypto volume. Include source/definition cautions. | Learner explains what each measure can and cannot tell them and selects a defensible comparison baseline before interpreting the chart. |

### Module 2 — Spot Buying and Selling Pressure

| ID | Lesson visual to produce | ChartLab / interaction to build |
|---|---|---|
| M02-L01 | Three panels: upward progress retained, high activity with little progress, and downward progress retained. Do not claim to know trader identity or intent. | Label sequences as upward progress, downward progress, limited/conflicting progress or inconclusive; cite visible evidence and an invalidating condition. |
| M02-L02 | Paired range breakouts: one that sustains progress and one that returns inside despite high activity. Show boundaries, close location and a comparable volume baseline. | Audit structure, candle range/close, relative volume and the next 3–5 bars. Conclude “supports,” “challenges,” or “inconclusive” for continuation, with reasons. |
| M02-L03 | High activity with limited progress at resistance and after a decline; show alternative explanations such as two-sided trading, event volatility or data/session problems. | For several high-volume cases, learner fills in observations, possible explanations, evidence still needed and what would invalidate their preferred reading. |
| M02-L04 | Advance where each push gains less distance, closes farther from highs and fails to extend, followed by a structure break; pair it with a pause that later continues. | Identify the first warning, first meaningful structural change and invalidation of the reversal idea. Teach the difference between warning and trigger. |
| M02-L05 | Three case studies: marginal new high on lower volume; high volume with little progress at a boundary; low-volume decline after a selloff. Show subsequent sequences separately. | Learner writes the observed mismatch, two possible explanations and the next price behaviour that would favour each. Reveal later bars only after submission. |

### Module 3 — Find Trade Setups at the Levels That Matter

| ID | Lesson visual to produce | ChartLab / interaction to build |
|---|---|---|
| M03-L01 | Synthetic uptrend with swing highs/lows, impulse, pullback, previous range boundary, candidate setup area and invalidation. Include successful and failed retests. | Mark a setup area but do not allow an entry until the learner writes a trigger and invalidation. Reveal two different outcomes from the same starting structure. |
| M03-L02 | Two similar impulses followed by contrasting pullbacks. Label pullback depth/speed, relative activity, swing structure and retest result. | Pause after the first three pullback bars. Learner records a hypothesis, required trigger and invalidation, then updates only after remaining bars are shown. |
| M03-L03 | A range with meaningful support/resistance zones; show rejection, sustained movement beyond the zone and an ambiguous multi-bar test. Include activity baseline. | Learner draws zones and creates conditional scenarios for each, including the evidence required before entry could be considered. Grade justification rather than eventual direction. |
| M03-L04 | Range with upper/lower zones, repeated tests, a false upside break, a sustained breakout variant and a panel showing a different higher-timeframe context. | Classify upper/lower rejection, ambiguous overshoot, breakout with follow-through and breakout failure. State what evidence is still needed before planning a trade. |
| M03-L05 | One-page setup-quality rubric: context, location, price-volume evidence, alternatives, trigger, invalidation, target area and risk. Pair with three contrasting candidate charts. | Grade three setups using the rubric, including justified “no” and “unknown” answers. Reveal outcomes only after scoring the process. |

### Module 4 — Spot False Breakouts Before You Chase Them

| ID | Lesson visual to produce | ChartLab / interaction to build |
|---|---|---|
| M04-L01 | Three breakouts: close beyond and sustain; wick beyond but close inside; close beyond then quickly return. Mark boundary, relative activity and follow-through. | Freeze immediately after the first breakout bar. Learner writes two scenarios, trigger and invalidation before staged future bars are revealed. |
| M04-L02 | Four-frame story: breakout, return inside, failed attempt to reclaim, downside progress; include a counterexample that reclaims the boundary and continues. | Mark earliest warning, stronger failure evidence and invalidation. Reveal bars one at a time to avoid hindsight-based answers. |
| M04-L03 | Two extreme-activity sequences: late-stage advance with poor retained progress and later structure change; high activity followed by consolidation and continuation. | Learner chooses “possible climax,” “strong continuation,” or “inconclusive,” cites evidence and identifies the next event that would alter the reading. |
| M04-L04 | Matched spring and upthrust diagrams showing range boundary, excursion outside, close back inside, retest and later structure. Include examples where the event fails. | Four short clips: successful-looking and failed springs, successful-looking and failed upthrusts. Learner defines the range first, then records what confirmation is still needed. |
| M04-L05 | Four-stage storyboard: warning event, structure break, retest and resolution. Build both a reversal ending and a prior-trend-resumes ending. | At every reveal, learner logs observation, preferred hypothesis, alternative and invalidation. Assess whether the update uses only information visible at that stage. |

### Module 5 — Find the Price Levels Worth Watching

| ID | Lesson visual to produce | ChartLab / interaction to build |
|---|---|---|
| M05-L01 | Same synthetic price series shown with vertical volume by time and horizontal volume profile by price. Label period and source. | Learner marks two concentrations and one thinner area in a stated window, then describes current price location without predicting a bounce or breakout. |
| M05-L02 | Profile diagram labelling Point of Control, Value Area High/Low and selected profile percentage. A second profile window shows that reference levels can change. | Mark POC and value boundaries on two profiles from the same data with different selected windows. Explain what each level can and cannot establish. |
| M05-L03 | Two-bulge profile with a low-volume connection and synthetic path; show both fast traversal and failed traversal through the thinner area. | Before outcome reveal, learner identifies node boundaries, writes continuation and stall/rejection scenarios, and states observable evidence favouring each. |
| M05-L04 | Three comparable session profiles illustrating upward migration, downward migration and overlap/balance. Label POC and value boundaries. | Record POC movement, value overlap, price swings and whether price stayed outside prior value. Separate the observation of a shift from the hypothesis it may imply. |
| M05-L05 | Clean chart with profile period, POC, Value Area, one broad and one thin area, and candles/recent swing highs/lows. Three outcomes: pause, turn away and move through. No unrelated indicators. | Learner marks up to three useful areas and writes two if/then scenarios around the nearest area. Reveal alternate outcomes and grade evidence-based updating. |

### Module 6 — Put It All Together: Build a Complete Trading Plan

| ID | Lesson visual to produce | ChartLab / interaction to build |
|---|---|---|
| M06-L01 | Light context worksheet over a synthetic candle/volume chart with swing structure, two or three justified zones, data-source field, market state, current question and two scenarios. | Give the learner an over-marked chart. They simplify it and write a five-sentence context note with one uncertainty and two competing scenarios. |
| M06-L02 | Reusable evidence sheet: event, range/close, relative-volume method, location, main interpretation, alternative and next discriminator. | Learner records the initial view, then updates after two sequential reveals without changing the original observation notes. |
| M06-L03 | Trade-thesis canvas with context, evidence, main scenario, trigger, invalidation, alternative, no-trade condition and risk notes. Include a completed and a blank version. | On one ambiguous breakout, learner writes acceptance and failure scenarios. Reveal two endings and evaluate whether conditions activated, not whether the direction was guessed. |
| M06-L04 | Pre-trade ticket with worked fictional example: entry, structural invalidation, risk budget, contract/tick-value calculation placeholder, target, slippage and cancellation criteria. No universal risk percentage. | Learner completes the ticket using supplied instrument specifications. Change spread/slippage and ask whether the setup still qualifies. |
| M06-L05 | Capstone chart sequence with initial range, breakout, retest, next opposing area, and two alternate endings; pair with full-plan worksheet. | Staged reveal: context first, evidence next, scenarios before the retest, trade ticket before outcome, then process review. Include a losing valid trade and a no-trigger outcome that later moves favourably. |

---

## 6. Shared interactive ChartLab requirements

Every lab must contain all of the following; if the lesson is a guided visual exercise, these can be simple controls rather than a complex application.

1. **Learning target:** One sentence that says what the learner is practising.
2. **Starting state:** A readable chart and only the context the learner is supposed to have at that moment.
3. **Specific task:** Tell the learner exactly what to mark, compare, explain or decide. Avoid “analyse this chart” without more guidance.
4. **Learner response:** A text field, labels/choices, drawing/annotation field, checklist or a clearly prompted pause-and-write task.
5. **Staged reveals:** When later price bars are important, do not show them before the learner has recorded the first reading.
6. **Model answer:** Explain a sound answer and name acceptable alternatives when the chart is ambiguous.
7. **Reasoning rubric:** Score observations, context, alternative explanations, next evidence and invalidation. Do not reward a lucky prediction by itself.
8. **Counterexample:** At least one similar-looking case where the same initial cue leads to a different outcome, or where the initial evidence stays inconclusive.
9. **Feedback:** Explain what is missing and how to improve the answer; “incorrect” alone is not useful feedback.
10. **Completion cue:** A short takeaway the learner can transfer to another chart.

### Minimum scoring rubric
Score each category 0–2 (0 = absent/unsupported; 1 = partly present; 2 = clear and evidence-based):
- Observations describe visible price/volume behaviour accurately.
- Context and location are considered.
- A plausible alternative or uncertainty is acknowledged.
- Next evidence, trigger or invalidation is observable.
- The conclusion follows from the evidence without claiming certainty.

A learner can score well even if the later price moved against their preferred scenario. A correct direction guessed without reasoning is not mastery.

---

## 7. Supporting assets beyond the main charts

### Worksheets
Create both **blank learner versions** and **completed teaching versions** of:
- Context note: market state, structure, key locations, data source, uncertainty and alternatives.
- Evidence sheet: observed price event, candle range/close, relative activity and baseline, location, possible explanation and next discriminator.
- Two-scenario thesis canvas: main scenario, alternative scenario, trigger, invalidation and no-trade condition.
- Pre-trade ticket: entry, invalidation, account/instrument risk calculation, target logic, costs/slippage, cancellation and management rules.
- Post-trade review: original observation, original plan, actual price behaviour, execution, process quality and lesson learned.

Use the same terms and fields in narration, ChartLabs, Q&A and worksheets. Learners should not have to learn four names for the same concept.

### Course/module covers (optional for later site use)
If/when public course pages need thumbnails, create one course cover and six module covers from the same light visual system. Make the course title legible at small sizes. Do not put tiny chart labels into a thumbnail. These images are not substitutes for the lesson-specific teaching visuals above.

### Captions and transcripts
For each recorded lesson:
- Provide time-synchronised captions (VTT or SRT).
- Provide the final transcript in accessible text.
- Describe meaningful visual actions in the narration or transcript. Do not make the learner depend on seeing a colour-only distinction.
- Verify specialist words, price levels, numbers and chart labels against the final video.

### Data and provenance records
For every synthetic chart, retain the OHLCV data file and the script/design source used to produce it. Include a short metadata note: synthetic purpose, timeframe, chosen volume baseline, relevant levels, intended teaching point and alternate outcomes.
For every licensed chart, retain provider/source, data date/session, rights/permission and any edits. Where provider terms require a credit, place it where learners can find it.

### Q&A and answer notes
Use the second-pass learner Q&A bank as more than trivia: connect each question to the action the learner should now be able to perform. Each lesson should have clear answer notes and a short transfer task, and the course-wide questions should help learners apply consistent rules across markets and chart types.

---

## 8. Quality-control checklist

An asset cannot be marked **Approved** until all applicable checks pass:

### Teaching and accuracy
- [ ] The teaching purpose is stated in one sentence.
- [ ] The main idea is visible without requiring the presenter to explain every pixel.
- [ ] The chart is realistic enough to teach but not so cluttered that the key distinction disappears.
- [ ] There is a contrasting case or alternate outcome wherever the concept is ambiguous.
- [ ] Observation is clearly separated from interpretation.
- [ ] No claim about hidden participant motive is presented as a fact.
- [ ] Volume data type, source, period and baseline are labelled when material.
- [ ] No unrelated indicator/tool content has been added.
- [ ] The asset does not suggest a guaranteed setup or outcome.

### Production
- [ ] Editable source exists and matches the final export.
- [ ] Export renders clearly at normal playback size and on mobile.
- [ ] Typography, candles, volume bars, zones and annotations match the shared design system.
- [ ] File names and stable asset IDs follow the naming convention.
- [ ] Alt text, extended description where needed and source/data notes are supplied.
- [ ] Any external data or image has documented rights/source details.

### ChartLab and feedback
- [ ] Learner instructions say precisely what to do.
- [ ] Later bars remain hidden until the learner's first response where staged reveal matters.
- [ ] Model answer explains the reasoning and uncertainty.
- [ ] Feedback identifies a way to improve an incomplete answer.
- [ ] A counterexample or alternate ending exists.
- [ ] Scoring rewards evidence and conditional thinking, not a lucky directional call.

### Release status
Use only these labels: **Not started**, **In progress**, **Needs revision**, **Approved**. Do not call assets “complete” merely because this inventory has been written.

---

## 9. Recommended production order

1. Review and approve the shared chart design system and the M01-L01 pilot package before scaling.
2. Test the pilot with a true beginner; validate comprehension, responsive layout, keyboard use and screen-reader description, then revise the package.
3. Produce the remaining 29 asset packages module-by-module in lesson order, keeping concepts and terminology consistent.
4. Build and test ChartLabs alongside the charts, with answer feedback and counterexamples rather than saving all exercises for the end.
5. Create worksheet masters from the fields already used in Module 6, then reuse those fields in earlier practice.
6. Record and caption only after the script, visual and interaction behaviour are approved.
7. Run a final novice walkthrough and accessibility review before public release.

## 10. Explicitly out of scope

Do not add VWAP, moving-average packs, RSI/MACD tours, unrelated dashboard screenshots, paid-signal graphics, or generic stock-trading stock photos. These would weaken the course's specific promise. Include a tool or visual only when it helps learners interpret price alongside volume, use Volume Profile in context, or build/review a conditional trade plan.
