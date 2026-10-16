# Course Development Workflow Summary
## Read Volume. Find Trade Setups. — Volume Price Analysis

**Purpose:** Preserve the method used to research, structure, write, deepen, edit, assess and prepare the course so the same standard can be followed in future courses or when this catalogue is revised.

**Current location:** `course-source/volume-price-analysis/` on `my-new-branch` in `ZaphodBeeblebrox12/prototypeweb`.

**Current status:** Six-module, 30-lesson manuscript and supporting documents exist. The first pilot asset package for Module 1, Lesson 1.1 has been created. The remaining lesson assets, full lesson rehearsals, beginner testing, accessibility testing, and public website integration are not complete.

---

## 1. Start with the learner and the course promise

Before writing scripts, define who the course is for and what the student should be able to do.

- **Learner:** Someone who has only recently started studying market charts. They may recognise candles but are not expected to know specialist trading vocabulary.
- **Course promise:** Learn to read recorded volume alongside price, recognise potential trading situations, evaluate breakouts and failures, and build a structured trade plan.
- **Boundary:** Keep the course about volume, price behaviour, price structure and Volume Profile where relevant. Do not turn it into a general indicator course.
- **Teaching principle:** Teach the learner how to reason from evidence rather than memorise a pattern name or be told what direction to trade.

The public-facing module and lesson titles were refined to sound useful and desirable to a prospective student without resorting to hype or promises of guaranteed results.

## 2. How we established the six modules and 30 lessons

The catalogue was shaped around a learning journey rather than a list of book chapters. We consulted respected works and approaches in volume/price analysis, including Anna Coulling, Tom Williams, Richard Wyckoff, David Weis, James Dalton and colleagues, and Buff Dormeier. Their methods overlap in places, but are not interchangeable.

The course then organised the most relevant ideas into six progressive modules, each containing five lessons:

1. **Read the Market Behind the Candles** — understand what volume adds to candle reading and learn to compare activity with price results.
2. **Spot Buying and Selling Pressure** — study effort versus result, progress, stalled moves and price/volume disagreement.
3. **Find Trade Setups at the Levels That Matter** — apply the reading to trends, pullbacks, support/resistance and range edges.
4. **Spot False Breakouts Before You Chase Them** — evaluate breakouts, failed moves, climactic activity, springs/upthrusts and evidence of a possible reversal.
5. **Find the Price Levels Worth Watching** — learn Volume Profile, Point of Control, Value Area, nodes and changes in where activity is concentrated.
6. **Put It All Together: Build a Complete Trading Plan** — combine context, evidence, alternative scenarios, triggers, invalidation, risk, execution and review.

**Why this order:** It moves from reading a single candle and its volume, to reading a sequence, to using that skill at important locations, to evaluating failures, and finally to creating a full plan. Module 6 is a practical capstone, not just a recap.

### How we used the authors' work

The goal was not to copy books or include every topic because an author discusses it. The author-research pass asks: *What distinctive, high-value contribution does this work make, is it represented in our material, and does it directly support our course promise?*

Concepts that strengthen volume-price reading should be taught in the relevant module. Anything that would pull the course into an unrelated or much broader method should be an explicit scope decision, not silently added. Wording, chart examples and exercises must be original; the sources inform the teaching approach rather than supply text to reproduce.

---

## 3. The passes we used—and what each pass is for

The passes have distinct jobs. They are not six rounds of rewriting the same paragraphs.

### Pass 1 — Course architecture and full teaching draft

**Question:** Have we found the right modules, lessons and central ideas—and drafted enough material to teach each lesson?

For each lesson, create:
- A clear learning objective.
- A timed lesson outline.
- A full teaching script, not just a list of talking points.
- A worked chart example and, where useful, a contrasting outcome.
- A lesson-end knowledge check.
- Inline comments for required illustrations, charts and ChartLabs.
- Instructor notes for accuracy, scope or teaching limitations.

The first pass is a substantial draft, not a claim that every script is production-ready. A topic appearing in the outline does not mean the learner has yet practised it enough.

### Pass 2 — Author-specific value, coverage gaps and learner Q&A

**Question:** Have we captured the important ideas from respected approaches, and does each lesson give the learner real, usable value?

Review the material against the source works. Distinguish:
- A concept that is only mentioned.
- A concept that is explained.
- A concept that is demonstrated with a worked chart.
- A concept that the learner practises and can apply independently.

The second-pass Q&A was changed from a simple recall quiz into a learning resource. Each of the 30 lessons has two applied questions, model reasoning, and a short chart-practice task. Answers explain evidence, plausible alternatives and what to look for next. The course-wide questions reinforce the same approach across topics.

The central quality question is:

> **If a learner answers this correctly, what can they now do on a chart that they could not do before?**

If a question only tests a definition, improve it with a realistic situation, a decision, or a follow-up action. If a source concept is not relevant to the course promise, keep it out rather than expanding scope without reason.

### Pass 3 — Beginner-first editorial language and voice

**Question:** Can a person who is new to the market understand and follow the teaching without losing the analytical depth?

The editorial pass applies a consistent voice: calm, patient, direct, practical and honest.

- Explain the everyday meaning before using the technical label.
- Define specialist terms on first use.
- Use short, active sentences.
- Teach one unfamiliar idea at a time.
- Explain with a chart and a concrete example rather than abstract description alone.
- Separate what the chart shows from what it might mean.
- Include a plausible alternative when the evidence is uncertain.
- Avoid unsupported claims about hidden participant motives.
- Explain what could change the reading.
- Read the script aloud; if it sounds like a research paper, rewrite it.

The point is not to make the course shallow. It is to make difficult ideas understandable on the first or second reading.

### Pass 4 — Visual and exercise production

**Question:** What must the learner see, compare, mark or try so the explanation becomes a skill?

Every lesson receives explicit asset requirements. A ChartLab must do more than provide something to click. It should tell the learner what to do, let them make a decision before the answer is revealed when useful, and explain why the answer is sound.

Each lesson's asset specification should include:
- The chart or illustration and its teaching purpose.
- A synthetic or properly licensed dataset.
- An editable master and final export.
- Alt text and an extended description when needed.
- A learner task and response format.
- Staged reveals or contrasting outcomes.
- Model answer, acceptable alternatives and feedback.
- A simple reasoning rubric.
- Provenance, file name and completion status.

### Pass 5 — Runtime and depth verification

**Question:** Does the complete delivered lesson actually teach enough, within its intended length?

The production rule is strict:

- **Hard minimum: 10 minutes.**
- **Normal range: 10–20 minutes; preferred planning target: 12–16 minutes.**
- **Over 20 minutes:** permitted when the material genuinely requires more time, such as a complex sequence or a full capstone case. Record why.

Time a real rehearsal. Count actual instruction, narrated chart work, guided practice, feedback and recap. Do not count an unbuilt ChartLab, a silent placeholder, loading time or repeated definitions as teaching. If a lesson is under 10 minutes, add a worked example, a contrasting case or meaningful learner practice. Do not pad it.

A draft outline with minute labels is not proof of runtime. The final runtime is verified only after the lesson is assembled and rehearsed.

### Pass 6 — Technical, learner and release review

**Question:** Is the lesson accurate, understandable, usable and ready for the intended platform?

Before public release:
- Check technical definitions and data-source limitations.
- Confirm charts match their datasets and scripts.
- Test links, images, mobile layouts, keyboard use and accessibility.
- Test ChartLabs and model feedback.
- Run each lesson with a full rehearsal and confirm its minimum duration.
- Have a true beginner try the material and note confusion without being coached through the answer.
- Revise confusing explanations and retest.
- Add final captions/transcripts and check data/image rights.

Only then consider public website integration. Source material saved in a repository is not the same as a completed, published course.

---

## 4. Required depth inside an individual lesson

Each lesson should teach a student to do something, not simply recognise a phrase.

A strong lesson generally contains the following elements:

1. **The problem:** What chart-reading question are we trying to answer, and why is it useful?
2. **The concept:** Explain the idea in ordinary language, then introduce its technical name if needed.
3. **A worked example:** Walk through the visible evidence step by step—price context, candle result, volume comparison, location and what happens next.
4. **A contrast or counterexample:** Show a similar-looking event that leads to a different reading, or remains uncertain.
5. **A decision method:** Give the learner a short process they can repeat on a new chart.
6. **Learner practice:** Ask them to mark, compare, describe or write a conditional scenario before revealing the answer.
7. **Feedback:** Explain why a response is sound, what is missing, and which alternative remains possible.
8. **Limits and recap:** State what the concept cannot prove and give one habit the learner can take to another chart.

Not every lesson needs equal time in every section. More complex topics can take longer. Each section must earn its place by improving understanding or practice.

## 5. The standard workflow for building each lesson

Use this sequence for every lesson and future catalogue:

1. Define the beginner's question and the measurable learning objective.
2. Identify the relevant source concepts and distinguish what is essential from what would broaden scope.
3. Write a timed outline and explain the idea in plain language.
4. Build the complete worked chart example.
5. Add a realistic counterexample or alternate outcome.
6. Write the learner task and model answer together; the answer should demonstrate the learning objective.
7. Specify all required visuals, data, ChartLab states, accessibility text and production files.
8. Estimate lesson timing, then confirm the actual runtime in rehearsal.
9. Test the lesson with a beginner, revise and retest.
10. Mark the lesson approved only when content, visuals, activity, answer feedback and duration have all passed review.

The script, visual, Q&A and ChartLab must tell the same story. Do not define a term one way in the script and use it differently in the exercise.

---

## 6. First pilot asset package: what is already built

The first sample package is **Module 1, Lesson 1.1 — What Candlesticks Don't Tell You: Reading the Volume Behind Price**.

The pilot contains:
- An editable SVG chart master and an export.
- Synthetic OHLCV data for the two comparison panels.
- Alt text, extended description and source note.
- A standalone HTML ChartLab with learner response fields, self-check and model-answer reveal.
- An instructor guide with an answer key, acceptable alternatives, feedback guidance and a scoring rubric.
- A package README describing purpose, files and limitations.

The exercise compares similar green candles in different contexts. One appears after a controlled pullback; the other appears after an extended advance near a prior-high area with a different volume relationship. The student must describe the evidence and say what they would watch next, rather than guess a guaranteed direction.

**Pilot status:** Files have been created and structurally checked, but the full novice pilot, rendered-browser test and formal accessibility review still need to occur. The ChartLab checks response completion; it does not automatically grade the quality of the analysis.

The pilot is the template to validate before producing the other 29 asset packages—not proof that all 30 lessons are fully produced.

---

## 7. The current working documents

- [Potential lesson catalog](POTENTIAL_LESSON_CATALOG.md) — the six modules, 30 lessons and course promise.
- [Asset production brief](ASSET_PRODUCTION_BRIEF.md) — the lesson-by-lesson visual and ChartLab inventory, file requirements and quality gate.
- [Lesson manuscripts and README](lessons/README.md) — scripts and lesson-production status.
- [Editorial language guide](lessons/EDITORIAL_LANGUAGE_GUIDE.md) — beginner voice and consistent terminology.
- [Learner Q&A bank](lessons/Q_AND_A_BANK.md) — applied questions, model reasoning and practice tasks.
- [Chart walkthroughs](lessons/CHART_WALKTHROUGHS.md) — presenter notes for the visual work.
- [Pilot asset package](assets/README.md) — actual files created for Module 1, Lesson 1.1.

---

## 8. Current status and next steps

### Completed as working source
- Six-module, 30-lesson course architecture.
- First-pass teaching manuscripts and subsequent audits/refinement.
- Lesson-level outlines, narration, knowledge checks and inline asset/ChartLab comments.
- Author-coverage and scope review.
- Beginner-oriented editorial language guide.
- Applied Q&A bank with model answers and chart practice.
- Asset production brief for all 30 lessons.
- One pilot asset package for Module 1, Lesson 1.1.

### Still required before calling the course production-ready
- Pilot the sample with a true beginner; fix misunderstandings found.
- Test the HTML in a real browser and complete an accessibility review.
- Build and test the remaining 29 lesson asset packages and ChartLabs.
- Complete worksheets, feedback and model answers in production form.
- Rehearse and time all 30 lessons, with none below 10 minutes.
- Complete technical review, transcript/caption work, rights checks and a novice walkthrough.
- Integrate the course into public pages only after the teaching content and assets are reviewed and approved.

**Operating principle:** Build depth through clarity, examples, contrasting cases and learner practice—not repetition, unnecessary indicators or longer scripts that do not teach anything new.
