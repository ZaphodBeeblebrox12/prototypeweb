# Stage 2 Pilot Review — M01-L01 ChartLab

**Course:** Read Volume. Find Trade Setups.  
**Pilot:** Module 1, Lesson 1.1 — *What Candlesticks Don't Tell You: Reading the Volume Behind Price*  
**Branch:** `my-new-branch`  
**Review type:** Source-level inspection and targeted remediation.  
**Status:** The source-level fixes and reflowed mobile SVG variants below have been added. A Chromium smoke fixture passed 12 functional/responsive checks, but used stand-in images and mirrored interaction markup. The committed page with its actual chart SVGs has not been fully browser-validated. The pilot is **not yet approved for scale-up** because actual-page visual review, assistive-technology and novice usability checks remain outstanding.

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
- Unlocked progress buttons update the active-step indicator without locking later steps when the learner navigates backward. Restart resets unlock state and moves focus back to the first-stage heading.
- Five mobile-specific SVG variants were added. The phone layout uses a stacked comparison for Panels A and B instead of shrinking the desktop side-by-side chart to an unreadable width.

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

### Browser smoke fixture

A Chromium/Playwright fixture was exercised successfully via in-memory page content. It mirrors the ChartLab interaction handlers and uses inline stand-in chart images. Twelve checks passed:

- Initial state and disabled stages.
- Incorrect Level 1 answer gives feedback but does not unlock the next stage.
- Correct retry unlocks Level 2 and moves focus.
- Back/forward navigation updates the active-step indicator while preserving unlocked stages.
- Level 2 submission unlocks Level 3 and states that response length is not semantic grading.
- Revisited lower stages do not lock the higher unlocked stage.
- Level 3 submission reveals both alternative outcomes.
- Reflection feedback prevents empty completion.
- Restart resets forms, outcomes and unlock state.
- Rendered fixture has no horizontal overflow at 360px width.
- Reduced-motion preference is detected.
- No JavaScript page errors in the fixture at desktop or mobile sizes.

**Important limit:** this does not test the committed HTML file or its actual SVGs. An attempt to navigate the local file and loopback-hosted page was blocked by execution-environment policy, so the exact branch page still needs to be rendered and inspected in a normal browser. Do not treat fixture results as completed actual-page validation.

- The six fixed SVGs contain readable title, description and annotation text (no legacy escapes remaining in those visible nodes).
- Each SVG in `source/` matches its corresponding `exports/` file.
- The HTML references all five existing export assets using valid relative paths.
- All labelled controls, unique IDs, keyboard navigation listeners and reduced-motion handling remain present.
- The synthetic CSV and all price/volume values are unchanged.

### Responsive mobile assets\n\nThe standalone HTML now uses `<picture>` with a `(max-width: 720px)` source for each chart. Each mobile SVG is separately reflowed, has an accessible title/description, and a matching editable source/export pair. The comparison case stacks its two panels vertically. Source/export equivalence and file references are to be checked once more before scale-up.\n\n## 4. Runtime checkpoint

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
