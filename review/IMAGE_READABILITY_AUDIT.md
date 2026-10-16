# TradeThesis instructional image audit — Pass 1 inventory and readability triage

**Working branch:** `feat/instructional-image-zoom-audit`  
**Base:** `my-new-branch` at `5df97459da7be69d93d5997d978d7864ec6a9726` when the feature branch was created.  
**Scope:** Repository-wide image file inventory plus the deployed Learning Room image-rendering paths. This is not a claim that every asset has received a human visual inspection.

## Inventory snapshot

The repository tree contains **465 image assets**: **319 PNGs** and **146 SVGs** (including source copies, preview mirrors, brand marks and QA screenshots). The site root currently contains 14 HTML pages, with the Support & Resistance Learning Room using dynamically selected images rather than embedding each chart in the HTML.

The full asset-by-asset inventory is in [IMAGE_ASSET_INVENTORY.csv](IMAGE_ASSET_INVENTORY.csv). It records file path, format, bytes, same-directory SVG pairing, whether the basename appears in the reviewed source files, probable asset role, and the current readability action. Raster pixel dimensions are not exposed by the repository tree metadata; they remain unverified in this pass. The source SVGs preserve vector artwork, but their text can still be too small when the entire chart is scaled down.

## Confirmed high-priority findings

1. **The Learning Room was shrinking teaching figures before a student could inspect them.** In the base CSS, `.sr-room-teaching-figure img` was capped at `max-height: 380px`, and the staged chart sat beside the response panel in a two-column workspace. The feature branch removes the 380px ceiling (desktop figure cap is now 720px/72vh; mobile has no figure-height cap) and gives the chart/response workspace a full-width, chart-first column so the image is no longer squeezed beside a text field. Source resolution and annotation size still matter, especially on narrow screens.
2. **There was no dedicated viewer on the active Learning Room page.** The chart and teaching figure images had no shared full-screen open/zoom/pan control, despite being required to answer lesson questions. The V5.2 deep lesson figures are injected dynamically, so the solution must handle later-added images instead of only binding click listeners at page load.
3. **The core chart library already provides SVG counterparts for many instructional PNGs.** A spot-check of canonical chart SVGs (including Lesson 12/14 sources) found vector SVG artwork with a 921.6 × 518.4 viewBox and chart labels commonly set around 8.5 SVG units. When scaled to roughly 350px wide, an 8.5-unit label becomes about 3.2px tall, which is not comfortable reading. Vector sourcing prevents blur, but it does not replace a larger viewing area or better annotation layout.
4. **The V5.2 schematic figures and the deployed breakout/failure figure set are PNG-only in the published directories.** A viewer will help magnify them, but it cannot recover detail that was not included in the export. The largest/denser overview-style material and any chart with crowded labels should get a larger or more focused export after visual review. No new chart or annotation should be invented.
5. **The large FIG00 overview is not currently referenced by the active V5.2 lesson renderers.** `site/module5-v5_2/assets/figures/FIG00_boundary_episode_overview.png` is present (about 1.16 MB), but `site/module5-v5_2/assets/module5-deep-content.js` and `site/module5-v5_2/assets/module5-interactions.js` do not reference it. Treat it as an overview/source asset until an explicit lesson placement is approved; do not enable it automatically as student-facing content.
6. **Some repository images are not live course images.** The inventory distinguishes brand marks, QA screenshots, production/source-preview assets and legacy mirrors so the audit does not incorrectly apply zoom controls to logos or treat every committed image as student-facing.

## Initial remediation on this feature branch

- Added `site/assets/image-inspector.js` and `site/assets/image-inspector.css`: a dependency-free, opt-in viewer for the active Learning Room chart, its dynamically rendered teaching figures, and V5.2 figures.
- Updated `site/assets/support-resistance-room.css` to give the chart a full-width reading lane and remove the old small figure-height ceiling.
- The viewer includes a viewport-sized dialog; fit, zoom-in and zoom-out controls; drag panning; wheel zoom; touch pointer pinch/pan handling; Escape and close-button dismissal; focus restoration; keyboard open/zoom/pan controls; descriptive captions; and a non-intrusive "click or tap to inspect" hint.
- The viewer is deliberately scoped to educational figures and charts. Logos and marketing imagery are excluded.
- Updated the Learning Room's chart loader to prefer the vector `.svg` source when available and fall back to its existing `.png` if needed.
- Updated the preview workflow to stage SVG companions beside the referenced chart PNGs. This does not merge or deploy the feature branch.

## Validation and remaining work

- The existing GitHub Actions browser-smoke workflow uses Playwright and is triggered for pull requests targeting `my-new-branch`; an image-inspector smoke test will be added before requesting review.
- Pixel-by-pixel visual QA across desktop/mobile has not yet been established by the source-tree inspection alone. I cannot claim that every image's text contrast, cropping or source resolution has been visually confirmed.
- Raster native dimensions need a browser or binary-asset inspection pass; GitHub file listings expose byte size but not intrinsic width/height.
- The PNG-only figures require a rendered review to decide exactly which need source re-export, larger annotation typography, or a full-chart-plus-detail layout. Their substantive candle structure, price values, answer mappings and learning gates must remain unchanged.
- The feature branch will remain unmerged and will not be deployed. Review will be requested only after the checks and audit artifacts are ready.
