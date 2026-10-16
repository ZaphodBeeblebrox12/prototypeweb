# Stage 2 Pilot Review — M01-L01 ChartLab

**Course:** Read Volume. Find Trade Setups.  
**Pilot:** Module 1, Lesson 1.1 — *What Candlesticks Don't Tell You: Reading the Volume Behind Price*  
**Branch:** `my-new-branch`  
**Review type:** Source-level inspection and targeted remediation.  
**Status:** The source-level fixes below have been applied. The pilot is **not yet approved for scale-up** because browser rendering, assistive-technology and novice usability checks remain outstanding.

## 1. Source-level issues corrected

### Encoded text in Stage 3 SVGs

The initial breakout chart and its two alternate outcome charts had URL/JavaScript-style encodings such as `A%20breakout%20attempt` and `%u2014` inside visible SVG text and accessible title/description nodes. These have been decoded in both the editable `source/` assets and matching `exports/` assets:

- `assets/source/vpa-m01-l01-stage3-breakout-initial.svg`
- `assets/exports/vpa-m01-l01-stage3-breakout-initial.svg`
- `assets/source/vpa-m01-l01-stage3-outcome-continuation.svg`
- `assets/exports/vpa-m01-l01-stage3-outcome-continuation.svg`
- `assets/source/vpa-m01-l01-stage3-outcome-failure.svg`
- `assets/exports/vpa-m01-l01-stage3-outcome-failure.svg`

The change is limited to text in SVG `title`, `desc` and `text` nodes. Chart geometry and synthetic OHLCV data are unchanged.

### ChartLab navigation and accessibility improvements

- Progress buttons navigate to stages that have already been unlocked.
- When a stage is revealed, keyboard focus moves to its heading before scrolling, so the user's location is more apparent.
- Scripted scrolling and the restart action respect `prefers-reduced-motion`; a CSS fallback is included.
- Level 2 feedback now says “submitted” and explicitly states that the text-length check does not grade reasoning.

## 2. Existing strengths retained

- The page has `lang="en"`, a viewport declaration, a document title, main/header/nav landmarks, labelled inputs, non-empty image alternatives, visible focus styling, and live feedback regions.
- Learner responses are not saved to `localStorage` or `sessionStorage`.
- Stage design keeps the initial evidence visible before the learner sees two alternate chart endings.
- The self-check is not presented as automated semantic grading; learners compare their written reasoning with model criteria.

## 3. Source-level validation

The following checks were verified against the committed branch files:

- The six fixed SVGs contain readable title, description and annotation text (no legacy escapes remain in their visible text nodes).
- Each SVG in `source/` matches its corresponding `exports/` file.
- The HTML references all five expected export assets using valid relative paths.
- The document has labelled controls and unique IDs, and the new navigation, focus and reduced-motion handling is present.
- The synthetic CSV and all price/volume values are unchanged.

### Follow-up interaction defects found and corrected

A further read-through found two issues in the first navigation patch: clicking an already unlocked progress step changed the visible section without updating `aria-current`, and restarting from the completion screen hid the element that still held keyboard focus. The code now keeps the highest unlocked step separate from the active step, updates the current-step indicator when navigating backward or forward, resets unlock state on restart, and moves focus back to the first stage heading after restart.

### Browser-test limitation

I attempted a headless Chromium run using a local test fixture, but the execution environment blocked both `file://` and loopback HTTP navigation with `ERR_BLOCKED_BY_ADMINISTRATOR` before the page loaded. Therefore **no browser-rendering or browser-interaction test is claimed as passed**. The source-level checks above are not a substitute for a real browser run.

- The six fixed SVGs contain readable title, description and annotation text (no legacy escapes remaining in those visible nodes).
- Each SVG in `source/` matches its corresponding `exports/` file.
- The HTML references all five existing export assets using valid relative paths.
- All labelled controls, unique IDs, keyboard navigation listeners and reduced-motion handling remain present.
- The synthetic CSV and all price/volume values are unchanged.

## 4. Runtime checkpoint

The main narration in M01-L01 is about 842 words and its extended spoken case analysis about 217 words. At 120 words per minute, that is roughly 8.8 minutes of narration before learner pauses and practice. The lesson may reach the planned 10–15 minutes when the narrated walkthrough and 4–6 minute ChartLab are integrated as intended, but a timed rehearsal is still required. The outline is not proof of runtime.

## 5. Validation still required

- Open the committed standalone HTML in a normal browser and verify the decoded SVG titles, annotations and punctuation visually.
- Run all stages end to end: incorrect Level 1 attempt, correct retry, Level 2 submission, Level 3 submission, outcome reveal, reflection and restart.
- Use keyboard only. Verify unlocked navigation, active-step announcement, visible focus, logical focus order and no keyboard trap.
- Enable OS/browser reduce-motion and verify that stage/restart scrolling is not smooth.
- Test narrow mobile layouts and 200% zoom for content loss or horizontal scrolling.
- Test with at least one screen reader (for example, NVDA with Firefox or VoiceOver with Safari) for headings, chart alternatives, feedback announcements and newly revealed content.
- Conduct a novice usability test without coaching. Record hesitation, misunderstood labels and incorrect interpretations.
- Rehearse the complete lesson and record delivered duration.

**Scale-up gate:** Do not reproduce the pilot pattern across the remaining 29 lessons until browser and accessibility testing is complete and beginner feedback has informed any needed revisions.
