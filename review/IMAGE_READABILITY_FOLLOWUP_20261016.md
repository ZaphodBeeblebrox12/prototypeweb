# Image Readability Follow-up — 16 October 2026

**Review branch:** `feat/image-readability-audit-20261016`  
**Base:** `my-new-branch`  
**Status:** Review-only. This branch has not been merged or deployed.

## What the audit established

The repository inventory contains 465 PNG/SVG assets across `course-content/`, `course-source/`, `site/`, `review/`, and `brand-assets/`. This includes source, duplicate, preview and QA assets; it is not a count of 465 live page images. The full path inventory and prioritized V5.2 figure review are documented in [IMAGE_READABILITY_AUDIT.md](../docs/IMAGE_READABILITY_AUDIT.md). A native-dimension CSV was produced by the existing GitHub Actions inventory workflow.

The strongest confirmed issue is *display density*. V5.2 teaching figures commonly contain two, three, four or six distinct chart panels. The source PNGs are usually around 2,000–3,000 px wide, but compressing several independent examples into one lesson-width graphic reduces their labels too far. The existing renderer already separates supported comparisons into panel views and preserves the full original below a disclosure; those original figure and panel mappings remain unchanged in this follow-up.

The staged synthetic chart set is 11 images at 2048 × 1152 px. The source dimensions are ample for the full chart, but a chart displayed beside the student response panel was too narrow on desktop; at a phone-sized fit view, annotation text still started too small.

## Changes in this follow-up

- **Full-width chart-first layout:** the staged chart now uses the full lesson reading width, with the prompt/response panel beneath it instead of competing for horizontal space beside the chart.
- **Detail-first mobile inspection:** opening an instructional image on a viewport up to 680 px starts at 200% of its fit scale. Learners can pan around the enlarged image and use **Fit** to return to the whole chart; zoom-in/zoom-out, keyboard controls, pinch/drag, Escape and close remain available.
- **Source-quality disclosure:** the viewer identifies vector artwork versus raster sources and reports source dimensions when available. For cropped SVG panel wrappers around PNG charts, it explicitly notes that the panel comes from a raster source and enlargement cannot restore detail absent from the original.
- **Visible affordance:** educational figure captions get a small “Select image to inspect details” cue, rather than relying on cursor shape alone.
- **Position preservation:** closing restores both horizontal and vertical page position and returns keyboard focus to the source figure.
- **Regression coverage:** the Playwright smoke test checks the full-width desktop layout, mobile detail-first scale, raster-source note, zoom/pan/fit, close/focus/scroll restoration and the existing lesson review gate.

## Highest-priority findings and limits

1. **Multi-panel figures:** preserve the existing individual panel views plus the full original composition. Do not force a student to inspect a six-panel figure shrunk into one small image.
2. **Mobile staged charts:** the improved initial zoom makes detail inspection more immediate, but it does not rewrite any candles, labels or stage image filenames.
3. **Single-chart annotations:** FIG14 and FIG22–FIG24 remain candidates for source-level re-export or properly authored close-up views if rendered inspection shows that the annotations are still too small. No prices, candles or annotations should be recreated from guesses.
4. **FIG00 overview:** its intrinsic dimensions and full-resolution appearance could not be verified through the repository file endpoint in the previous audit. It remains a source-review item.
5. **Other content:** interactive ChartLab drawings are intentionally excluded from static image zoom, so inspection does not interfere with drawing gestures or answer gates. Decorative brand images are also excluded.

## Validation checkpoint

The feature branch includes additional automated assertions in `site/tests/image-inspector-smoke.cjs`, and the non-deploying Learning Room verification workflow is enabled for this branch. CI results are to be recorded after the run finishes; this report does not claim the new changes have already passed the updated workflow.

The branch is deliberately not a deployment preview, and no merge, pull request, or deployment has been initiated. Review the branch changes first, then explicitly approve any merge or deployment.
