# Module 5 — Editorial Pass Record and Template Backlog

**Current edition:** v5.2 — Chart-Led Editorial Pass  
**Status:** The chart-led editorial pass is reflected in the lesson content and interactive preview. The wider lesson-template redesign remains deliberately deferred. No GitHub or canonical website changes were made.

## What this pass changed

### 1. Actual chart evidence now appears with its question

- Lessons 12, 13 and 14 each show the first stage of their actual historical NIFTY 50 chart inside the reading, at the point where that example is introduced.
- Each chart is followed by a specific question the learner can answer from the visible candles alone.
- A button takes the learner to the staged evidence exercise to record the response. Later chart stages are not inserted into the reading, so the first look does not reveal the ending.
- The staged chart panel now has stage-specific captions with the instrument, daily timeframe, visible date range, chosen zone and observation to inspect.
- Text introduces only the first visible state before sending the learner to the staged reveal. Specific claims about later price action are explained with their stage-specific chart and model answer, not assumed from prose.
- The example zones remain instructional annotations, not official index levels. The historical charts and CSV excerpts remain internal-development assets until data rights are cleared or they are replaced with user-owned/authorised data.

### 2. Volume is an existing catalogue course

- Lesson 12 now presents **Volume** as a separate course in the TradeThesis catalogue, not as a future release.
- The related-course card is a reusable content block so comparable course signposts can be added without rewriting the layout each time.
- The current standalone preview references the course by title and catalogue status; it does not invent a production URL.
- The NIFTY 50 teaching example is explicitly described as a price-only index chart. It cannot support claims about volume because no volume bars are shown.

### 3. Specialist terms are explained when needed

Lesson 12 defines spot FX, CFDs and tick volume at the point of use and explains why volume measures from different instruments or data feeds are not interchangeable. The lesson directs learners to check what the platform actually measures rather than assume every volume display is traded size.

### 4. Model responses preserve the student's thinking

The staged prompts ask learners to state what is visible, what it may mean and what remains uncertain. Model answers and self-checks remain available after the staged exercise; a final-direction guess is not the grading standard.

## Template pass — deliberately deferred

**Do not redesign the overall lesson template during the current editorial pass.** The recurring blocks still feel less developed than the template used in TradeThesis Trading Path. Audit that difference separately, after reviewing the chart-led copy.

Examples to review in that later pass:

- “Your field note: keep the first read”
- “Here is what I would put in my own journal”
- Observation / Interpretation / Alternative / Revision-condition fields
- Weak-note versus stronger-note examples
- Takeaways, staged prompts, model answers and self-checks
- The new reusable `caseChart` and `relatedCourse` content blocks

Compare Module 5 side by side with Trading Path for teaching depth, section hierarchy, visual rhythm, transitions, worked examples, and the balance between explanation, practice and reflection. Decide which components should be standardized across courses and which should be used only when they help a specific learning objective. Do not merely copy the labels into every lesson.

The purpose of the template pass is to make future courses faster to produce **without losing teaching depth**. It should preserve substantive explanation and visual evidence rather than shorten everything to fit a template.

## Remaining checks before integration/release

1. Verify all historical-chart descriptions and captions against the images and underlying OHLC excerpts.
2. Perform browser-level desktop, tablet and mobile review, including keyboard access, focus visibility, text wrapping, image scaling and reveal flow.
3. During the separate template pass, compare with TradeThesis Trading Path and decide how the reusable course-reference card should behave when integrated with real catalogue URLs.
4. Only after review, decide whether to integrate into the website Learning Room and whether the historical examples have been replaced or cleared for distribution.

## Boundaries

- No GitHub commits, canonical script replacements or Learning Room changes are authorised by this package.
- Do not publish the current NIFTY 50 chart assets or CSV excerpts until the source rights are confirmed or the examples are replaced with user-owned/authorised data.
- Keep the three existing ChartLabs in place: Clear W (Lesson 5), Uneven Lows (Lesson 8), Wider Neckline (Lesson 14).
