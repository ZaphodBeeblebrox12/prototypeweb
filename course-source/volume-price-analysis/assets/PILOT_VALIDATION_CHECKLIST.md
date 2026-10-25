# M01-L01 Pilot Validation Checklist
## Read Volume. Find Trade Setups.

**Branch:** `my-new-branch`  
**Status:** IN PROGRESS — NOT APPROVED FOR SCALING  
**Purpose:** Keep source-level checks, browser checks, accessibility checks, novice testing and actual lesson timing separate. Passing a source check is not evidence that the learner-facing experience has passed.

## Current source-level checks

These checks were completed against the current branch source on 16 October 2026.

| Check | Result | Evidence / limit |
|---|---|---|
| Unique HTML IDs | Pass | Static source scan found no duplicate IDs. |
| JavaScript element references | Pass | Static scan found no `getElementById(...)` reference without a matching ID. This does not execute the code in a browser. |
| Referenced desktop/mobile SVG paths | Pass | All 10 paths referenced by the standalone HTML are present in `assets/exports/`. |
| SVG structural markers | Pass | Each of the 10 referenced assets contains an SVG root, a `viewBox`, title/description markers and a closing SVG tag. This was not a full XML render test. |
| Synthetic data fixture | Pass | The CSV has 72 data records plus its header. |
| Level 1 factual checks | Pass, source-level only | The learner must select the correct candle direction, relative-volume relationship and preceding price sequence; unanswered or incorrect selections block progression. |
| Level 1 written observation | Pass, source-level only | A written observation is required after the factual checks. Text length is a completion gate, not semantic grading. |
| Restart reset logic | Pass, source-level only | The handler clears text fields, factual selections, self-check boxes and feedback, hides the outcome reveal, closes model reasoning and returns to Level 1. |
| Delayed outcome reveal | Pass, source-level only | The continuation/failure panels remain hidden until the learner submits the initial Level 3 response. Actual browser behaviour remains untested. |

## Browser test protocol

Run this against the **committed, exact HTML and real SVG files**, not a substitute fixture. Test at least one current desktop browser and one mobile-sized viewport. Record browser/version, viewport, date, tester and observed result.

### 1. Initial load and chart rendering

- [ ] Open `lab-specs/vpa-m01-l01-candle-context-lab.html` from the asset package or from the intended test host.
- [ ] Confirm no broken images, missing fonts or SVG load failures.
- [ ] Confirm the Level 1 panel is the only lesson stage shown initially; the progress indicator marks Level 1 current.
- [ ] Confirm the Level 2 and Level 3 panels are not visually exposed initially.
- [ ] Check the desktop comparison has equal candidate candle dimensions and the intended common scale increment.
- [ ] Inspect browser console for JavaScript errors and failed requests.

### 2. Level 1: observation and validation

- [ ] Try continuing with all three radio groups unanswered; the page must keep the learner at Level 1 and focus the missing group.
- [ ] Answer a group incorrectly; the page must keep the learner at Level 1 and give a retry message.
- [ ] Correct all three visible-fact checks but leave the written observation too short; the page must not advance.
- [ ] Enter a meaningful observation of at least the minimum length with all correct factual selections; Level 2 must open.
- [ ] Verify no feedback claims to have graded the meaning of the free-text response.

### 3. Level 2: comparison

- [ ] Confirm the mobile comparison stacks vertically instead of squeezing two panels side by side.
- [ ] Confirm the equal-size candle comparison, activity baselines and chart labels remain legible at normal viewing size.
- [ ] Attempt to continue with each text response blank/too short; progression must be blocked and focus must move to the missing response.
- [ ] Enter both responses and continue; Level 3 must open.
- [ ] Return to Level 1 and confirm previously entered answers remain until restart.

### 4. Level 3: staged reveal and model reasoning

- [ ] Before initial submission, verify neither continuation nor failure chart is visible.
- [ ] Attempt to reveal outcomes with missing/too-short text; progression must be blocked.
- [ ] Submit the initial observation and two possible outcomes; both alternative charts must then be shown.
- [ ] Confirm the two paths share the same initial breakout event and only diverge in subsequent price behaviour.
- [ ] Complete the outcome review and open model reasoning; confirm focus moves to the intended content and no earlier answer is silently overwritten.
- [ ] Use Back navigation after the reveal and verify the experience remains understandable and the earlier response is not lost.
- [ ] Use Restart; all written answers, factual selections, self-checks and feedback should clear, the outcome panels should hide, model reasoning should close, and focus should return to Level 1.

### 5. Responsive, zoom and accessibility review

- [ ] Test at 1440 px, 1024 px, 720 px and a 320–390 px mobile viewport.
- [ ] At narrow widths, confirm mobile SVGs load and labels are readable without horizontal scrolling.
- [ ] Test browser zoom at 200% and a narrow reflow test; inputs and actions must remain reachable.
- [ ] Complete the whole lab using only the keyboard. Confirm a visible focus indicator, logical order, radio-group operation, and sensible focus after stage changes, errors, reveal and restart.
- [ ] Check with a screen reader that headings, fieldset legends, radio labels, textarea labels, progress state, error feedback and hidden/revealed panels are announced appropriately.
- [ ] Check text and interface contrast; do not rely on colour alone for meaning.
- [ ] Confirm reduced-motion preference suppresses smooth scrolling/animation.
- [ ] Confirm the page explains that responses remain local and are not saved or sent to a server.

### 6. Beginner usability and full lesson timing

- [ ] Ask a true beginner to complete the lab without verbal coaching. Record where they hesitate, misread a label, misunderstand the task or try to predict instead of observe.
- [ ] Ask the learner to explain, in their own words, why the same-looking candle has different context and what later evidence distinguishes the two breakout paths.
- [ ] Revise any confusing wording or charts, then repeat the usability test.
- [ ] Time the complete **lesson**, not only this standalone lab: narration, chart walkthrough, all three activities, feedback, Q&A and recap.
- [ ] Record measured active elapsed time. Exclude loading failures and technical delays, but include the time a learner genuinely needs to read, observe, answer and review feedback.
- [ ] Verify the measured experience is **greater than 10:00 minutes**. Aim for 12–16 minutes; do not stretch a lesson with empty pauses or repeated narration.

## Acceptance criteria

Do not mark M01-L01 approved until all of the following are true:

1. All real chart assets render at desktop and mobile sizes without console/resource errors.
2. The positive, negative, retry, Back and Restart paths work in the browser.
3. Keyboard, focus, zoom/reflow, contrast and screen-reader checks have been reviewed.
4. A beginner can complete the activity and understand the difference between observation and interpretation without instructor intervention.
5. The entire lesson has been timed and exceeds 10 minutes of genuine learner experience, normally landing in the 12–16 minute target.
6. The result, defects found, fixes and retest outcome are recorded below.

## Known limitations — do not overstate

- The standalone pilot is **not integrated with the site's member account or progress system**.
- Responses are local to the page and are **not saved or sent to a server**.
- Free-text answers are **not semantically graded**. Minimum length checks do not prove understanding.
- The source scan does not prove real browser rendering, accessibility or novice usability.
- Successful completion of this one pilot does not verify any of the other 29 lessons. Each lesson requires its own assets, testing and actual timed run-through.

## Test record

| Date | Tester / browser / viewport | Checks run | Result / defects | Retest |
|---|---|---|---|---|
| 16 Oct 2026 | Source-level static check | IDs, JS element references, ten asset paths, SVG structural markers, Level 1 validation wiring and reset wiring | Source checks passed; no exact-page browser or novice test was performed | Pending |

**Release decision: NOT APPROVED for scaling or publication.**