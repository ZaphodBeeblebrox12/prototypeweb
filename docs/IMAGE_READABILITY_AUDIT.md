# TradeThesis image readability audit

**Audit base:** `my-new-branch` at `5df97459da7be69d93d5997d978d7864ec6a9726` (16 October 2026)  
**Implementation branch:** `feat/instructional-image-readability-20261016`  
**Scope:** repository image assets, deployed static-site pages, Learning Room image renderers, V5.2 Lessons 12–14, staged chart activities, and existing CI validation.  
**Important scope distinction:** repository inventory counts include teaching sources, production files, duplicates, snapshots and other non-public assets; they are not all displayed by the website.

## Findings at a glance

The tree contains **465 image/vector assets** (319 png, 146 svg). The current V5.2 module has 26 schematic figures and 11 staged synthetic chart PNGs. The 26 source figures are generally high-resolution; the main problem is *display density*, not an obviously inadequate PNG export. Several figures combine two, three, four or six independent panels into one wide image. The lesson text column is about 920 px wide, so 3-panel and 4-panel figures can reduce small annotations to roughly a third or a quarter of their source size. The reader then adds a 500 px maximum image height, while other generic figure styles have 340 px and 380 px height caps.

The first corrective step is therefore not “make every file larger”: it is (1) split dense comparative figures into readable panel views, (2) remove arbitrary height ceilings on instructional figures, and (3) add an accessible viewer for detail inspection. The original composition must remain available so the learner can see the whole comparison.

## Prioritised findings

| Priority | Asset / pattern | What is wrong | Corrective action |
|---|---|---|---|
| P0 | V5.2 multi-panel figures: FIG01–FIG13, FIG15–FIG21, FIG25 | Several independent comparisons are squeezed into one image within a narrow reading column. A zoom-only solution still makes the student repeatedly zoom and pan before understanding the lesson. | Render each source panel separately at full reading-column width; keep the original complete figure in a disclosure control. |
| P0 | Instructional figure height constraints | `.sr-v52-figure img` used `max-height:500px`; older teaching figures used 380 px; generic generated figures used 340 px; staged chart figures had a 450 px cap at narrower breakpoints. | Remove those fixed ceilings for educational illustrations and retain native aspect ratio. |
| P1 | FIG00 opening overview; FIG14, FIG22–FIG24 single-chart annotated examples | Text callouts remain small when the full chart is fitted to the lesson width. FIG00's binary was too large for the repository file endpoint to return for pixel inspection during this pass. | Use the viewer for detail. Mark FIG00 for a source/export review; consider a purpose-built panel layout or larger annotation export if its full-size text remains hard to read. Do not fabricate or change chart evidence. |
| P1 | Eleven staged charts for Lessons 12–14 | The stage image is appropriately one chart per step, but small labels still need to be inspectable on mobile. | Make stage charts zoomable without altering stage ordering, responses, model-answer mapping or reveal gates. |
| P1 | Earlier Support & Resistance teaching figures / generic reading figures | Figure sizing was inconsistent and several instructional image types had different zoom behaviour or no zoom affordance. | Reuse one inspector for recognized educational figures; exclude brand marks and decorative artwork. |
| P2 | Interactive ChartLab SVG | This is a live student drawing surface, not a static illustration. Generic zooming on its SVG could interfere with drag/draw interactions. | Keep the interactive chart outside static image inspection; preserve its existing controls and activity state. |

## V5.2 figure-by-figure visual audit

Native dimensions below were read from the PNG header for 25 assets. The FIG00 asset could not be returned by the file-content endpoint in this pass, so its native pixel dimensions and detailed pixels remain **unverified**. All dimensions refer to the original source image, not its browser display size.

| Figure | Native dimensions | Visible content / layout | Finding and corrective action |
|---|---:|---|---|
| FIG00 boundary episode overview | Not verified | Four conceptual boundary episodes | Keep whole-image zoom; needs a source-quality review and possible four-part presentation. |
| FIG01 breakout evidence ladder | 2661 × 1209 | Three panels: excursion, close, follow-through | Split into three full-width panel views. |
| FIG02 filter tradeoffs | 2661 × 1209 | Three confirmation-rule comparisons | Split into three full-width panel views. |
| FIG03 context changes the question | 2501 × 1226 | Local versus wider context | Split into two panel views. |
| FIG04 break, return, response | 2923 × 1106 | Four steps in one row | Split into four panel views. |
| FIG05 three retest outcomes | 2695 × 1243 | Hold, re-entry, inconclusive | Split into three panel views. |
| FIG06 retest is not owed | 2547 × 1604 | Four panels in a 2 × 2 grid | Split into four panel views. |
| FIG07 failure is not reverse signal | 2695 × 1226 | Three possible post-failure paths | Split into three panel views. |
| FIG08 volume context, not gate | 2847 × 1964 | Four price/volume combinations | Split into four panel views; its two chart rows are particularly dense when scaled into the lesson column. |
| FIG09 decision record timeline | 2923 × 1192 | Four steps in one row | Split into four panel views. |
| FIG10 failed signal family | 3008 × 1792 | Six failure patterns in a 3 × 2 grid | Split into six panel views. This is a highest-priority density problem. |
| FIG11 first pullback, later failure | 2551 × 1243 | Two comparative charts | Split into two panel views. |
| FIG12 after-failure alternatives | 2711 × 1209 | Three possible range outcomes | Split into three panel views. |
| FIG13 gap and spike failures | 2567 × 1278 | Two complications | Split into two panel views. |
| FIG14 failed failure reclaim | 2377 × 1209 | One annotated chart | Keep overview; zoom for callouts. |
| FIG15 failure label checklist | 2574 × 1295 | Four-step decision chain plus summary statement | Split into five readable units (four steps and the summary). |
| FIG16 retest depth and closes | 2695 × 1226 | Three retest responses | Split into three panel views. |
| FIG17 range vs trendline failure | 2551 × 1261 | Two structural examples | Split into two panel views. |
| FIG18 neckline formation failures | 2567 × 1261 | Two formation examples | Split into two panel views. |
| FIG19 simple break, return, response | 2103 × 1053 | Three simplified steps | Split into three panel views. |
| FIG20 simple retest outcomes | 1971 × 1011 | Hold-like, failure-like, inconclusive | Split into three panel views. |
| FIG21 structural stop after failure | 2363 × 1229 | Two hypothetical directional examples with structural stop labels | Split into two panel views. Preserve all stop labels and the “not trade signals” disclaimer. |
| FIG22 range-edge upthrust | 2484 × 1341 | One annotated chart | Keep overview; zoom for numbered sequence/callouts. |
| FIG23 spring / downside reclaim | 2484 × 1341 | One annotated chart | Keep overview; zoom for the excursion, re-entry and response labels. |
| FIG24 prior-swing failure test | 2484 × 1341 | One annotated chart | Keep overview; zoom for the pivot and follow-through labels. |
| FIG25 continuation pause outcomes | 2721 × 1341 | Two contrasting charts | Split into two panel views. |

## Staged synthetic charts: Lessons 12–14

These remain individual learning states, rather than panel-comparison figures. They are intended to be zoomable without changing the image-to-answer mapping. The image filenames are deliberately left unchanged because the existing interaction code uses the selected stage image to locate its matching model response.

| Lesson | Stage images |
|---|---|
| 12 — Breakout or temporary penetration? | `L12-A-01-first-crossing.png`, `L12-A-02-return-inside.png`, `L12-B-02-follow-through.png` |
| 13 — Retests and role reversal | `L13-A-01-break-beyond.png`, `L13-B-01-return-to-area.png`, `L13-C1-hold.png`, `L13-C2-fail.png` |
| 14 — Failed breakouts | `L14-A-01-area-before-break.png`, `L14-B-01-first-move-beyond.png`, `L14-C-01-return-through.png`, `L14-D-01-pullback-holds.png` |

## Components and pages inspected

- `site/support-resistance-room.html`: main Learning Room shell; loads the base CSS, Learning Room CSS and both lesson scripts.
- `site/assets/support-resistance-room.js`: shared lessons, staged charts, and dynamically generated `.sr-room-teaching-figure` images.
- `site/assets/support-resistance-room-v5_2-integration.js`: long-form V5.2 reading blocks; `renderBlock()` maps figure blocks to images and captions.
- `site/assets/support-resistance-room.css`: staged chart and earlier lesson figure layout.
- `site/assets/support-resistance-room-v5_2-integration.css`: V5.2 figure styles.
- `site/assets/site.css`: generic `.generated-figure` styling and global responsive image defaults.
- `site/module5-v5_2/index.html`: legacy route redirects Lesson 12–14 to the Learning Room.
- `site/module5-v5_2/assets/figures/`: 26 original schematic PNGs.
- `site/module5-v5_2/charts/`: 11 stage-specific synthetic chart PNGs.
- `site/chartlab/clear-w.html`: interactive SVG drawing surface, intentionally excluded from static image zoom.
- `site/community.html`, `site/index.html`, `site/courses.html`, `site/live-class.html`, `site/construct.html`, `site/member-area.html`, `site/member-access.html`, and `site/trading-path.html`: checked for real `img` references and inline SVG. Brand logos and decorative chart illustrations are not to be made zoom controls.

## Source quality versus display quality

The inspected V5.2 PNGs are usually 2,000–3,000 pixels wide. That is generally enough source resolution for a reading-column display **when the chart panel is separated**. The major visual failure is shrinking several complete panels into one 920 px column. The fix keeps the original PNG untouched and presents crop-window SVGs that expose the existing pixels at a useful size; it does not redraw candles, prices, boundaries or annotations.

Single-chart assets FIG14 and FIG22–FIG24 may still have tiny annotations when the full view is shown, even though the viewer can zoom. Those must be checked visually in-browser; if the labels are still hard to read, the correct follow-up is a source-level re-export or a clearly labelled close-up, not merely more CSS width. FIG00 also remains a source-review item because a binary preview could not be inspected in this pass.

## Repository image inventory

The full appendix below lists all **465** image/vector asset paths found in the repository tree at the audit base. This is an asset inventory, not a claim that every file is used on the live site. Paths include source material, reference images, generated figures, duplicate assets, logos, embedded/site artwork, screenshots and vector illustrations.

### Counts by top-level area

- `course-content/`: 346
- `site/`: 55
- `course-source/`: 44
- `review/`: 17
- `brand-assets/`: 3

### All repository image/vector asset paths

- `brand-assets/tradethesis-horizontal.png` — 28,446 bytes
- `brand-assets/tradethesis-icon.png` — 23,834 bytes
- `brand-assets/tradethesis-wordmark.png` — 23,828 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-01-clean.png` — 36,098 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-01-clean.svg` — 13,901 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-02-support-reference.png` — 43,404 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-02-support-reference.svg` — 15,228 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-03-resistance-reference.png` — 42,696 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-03-resistance-reference.svg` — 15,232 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-04-combined-reference.png` — 45,282 bytes
- `course-content/support-resistance/chart_assets/charts/CL01-04-combined-reference.svg` — 16,524 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-01-clean.png` — 35,713 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-01-clean.svg` — 15,202 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-02-support-reference.png` — 42,128 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-02-support-reference.svg` — 16,500 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-03-resistance-reference.png` — 42,132 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-03-resistance-reference.svg` — 16,466 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-04-combined-reference.png` — 44,681 bytes
- `course-content/support-resistance/chart_assets/charts/CL02-04-combined-reference.svg` — 17,775 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-01-clean.png` — 36,728 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-01-clean.svg` — 14,836 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-02-support-reference.png` — 41,001 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-02-support-reference.svg` — 16,072 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-03-neckline-reference.png` — 42,292 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-03-neckline-reference.svg` — 16,087 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-04-combined-reference.png` — 46,996 bytes
- `course-content/support-resistance/chart_assets/charts/CL03-04-combined-reference.svg` — 17,414 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-01-clean.png` — 36,992 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-01-clean.svg` — 14,386 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-02-band.png` — 37,454 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-02-band.svg` — 14,996 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-03-labelled.png` — 41,826 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-03-labelled.svg` — 15,613 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-04-support-label.png` — 40,865 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-04-support-label.svg` — 15,605 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-05-breakdown.png` — 40,952 bytes
- `course-content/support-resistance/chart_assets/charts/L01-A-05-breakdown.svg` — 17,022 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-01-clean.png` — 40,160 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-01-clean.svg` — 15,747 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-02-band.png` — 40,690 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-02-band.svg` — 16,365 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-03-labelled.png` — 45,748 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-03-labelled.svg` — 17,007 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-04-resistance-label.png` — 44,887 bytes
- `course-content/support-resistance/chart_assets/charts/L01-B-04-resistance-label.svg` — 17,007 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-A-01-clean.png` — 36,477 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-A-01-clean.svg` — 12,971 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-A-02-reference.png` — 42,137 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-A-02-reference.svg` — 14,305 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-B-01-clean.png` — 37,256 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-B-01-clean.svg` — 13,474 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-B-02-reference.png` — 45,262 bytes
- `course-content/support-resistance/chart_assets/charts/L01-PRACTICE-B-02-reference.svg` — 14,775 bytes
- `course-content/support-resistance/chart_assets/charts/L02-A-01-clean.png` — 37,106 bytes
- `course-content/support-resistance/chart_assets/charts/L02-A-01-clean.svg` — 14,341 bytes
- `course-content/support-resistance/chart_assets/charts/L02-A-02-turns.png` — 43,681 bytes
- `course-content/support-resistance/chart_assets/charts/L02-A-02-turns.svg` — 20,148 bytes
- `course-content/support-resistance/chart_assets/charts/L02-A-03-structure-reference.png` — 59,364 bytes
- `course-content/support-resistance/chart_assets/charts/L02-A-03-structure-reference.svg` — 21,927 bytes
- `course-content/support-resistance/chart_assets/charts/L02-B-01-clean.png` — 38,246 bytes
- `course-content/support-resistance/chart_assets/charts/L02-B-01-clean.svg` — 14,802 bytes
- `course-content/support-resistance/chart_assets/charts/L02-B-02-structure-reference.png` — 55,979 bytes
- `course-content/support-resistance/chart_assets/charts/L02-B-02-structure-reference.svg` — 20,605 bytes
- `course-content/support-resistance/chart_assets/charts/L02-C-01-clean.png` — 38,241 bytes
- `course-content/support-resistance/chart_assets/charts/L02-C-01-clean.svg` — 17,078 bytes
- `course-content/support-resistance/chart_assets/charts/L02-C-02-major-turns.png` — 46,791 bytes
- `course-content/support-resistance/chart_assets/charts/L02-C-02-major-turns.svg` — 22,775 bytes
- `course-content/support-resistance/chart_assets/charts/L02-C-03-range-reference.png` — 42,510 bytes
- `course-content/support-resistance/chart_assets/charts/L02-C-03-range-reference.svg` — 18,357 bytes
- `course-content/support-resistance/chart_assets/charts/L02-D-01-early-state.png` — 39,897 bytes
- `course-content/support-resistance/chart_assets/charts/L02-D-01-early-state.svg` — 14,415 bytes
- `course-content/support-resistance/chart_assets/charts/L02-D-02-later-state.png` — 53,213 bytes
- `course-content/support-resistance/chart_assets/charts/L02-D-02-later-state.svg` — 21,605 bytes
- `course-content/support-resistance/chart_assets/charts/L02-E-01-practice.png` — 38,014 bytes
- `course-content/support-resistance/chart_assets/charts/L02-E-01-practice.svg` — 17,081 bytes
- `course-content/support-resistance/chart_assets/charts/L02-E-02-reference.png` — 67,992 bytes
- `course-content/support-resistance/chart_assets/charts/L02-E-02-reference.svg` — 24,054 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-01-clean.png` — 39,356 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-01-clean.svg` — 19,272 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-02-candidate-turns.png` — 55,287 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-02-candidate-turns.svg` — 29,439 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-03-reference-points.png` — 52,853 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-03-reference-points.svg` — 23,319 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-04-simplified.png` — 63,816 bytes
- `course-content/support-resistance/chart_assets/charts/L03-A-04-simplified.svg` — 24,020 bytes
- `course-content/support-resistance/chart_assets/charts/L03-B-01-candidate-turns.png` — 55,183 bytes
- `course-content/support-resistance/chart_assets/charts/L03-B-01-candidate-turns.svg` — 28,182 bytes
- `course-content/support-resistance/chart_assets/charts/L03-B-01-practice.png` — 40,341 bytes
- `course-content/support-resistance/chart_assets/charts/L03-B-01-practice.svg` — 18,879 bytes
- `course-content/support-resistance/chart_assets/charts/L03-B-02-reference.png` — 67,997 bytes
- `course-content/support-resistance/chart_assets/charts/L03-B-02-reference.svg` — 25,871 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-01-clean.png` — 38,024 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-01-clean.svg` — 17,103 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-02-broad-bracket.png` — 43,718 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-02-broad-bracket.svg` — 18,352 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-03-too-narrow.png` — 45,346 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-03-too-narrow.svg` — 18,434 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-04-defensible-zone.png` — 45,186 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-04-defensible-zone.svg` — 18,408 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-05-too-broad.png` — 47,255 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-05-too-broad.svg` — 18,872 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-06-compare.png` — 53,793 bytes
- `course-content/support-resistance/chart_assets/charts/L04-A-06-compare.svg` — 20,172 bytes
- `course-content/support-resistance/chart_assets/charts/L04-B-01-clean.png` — 39,954 bytes
- `course-content/support-resistance/chart_assets/charts/L04-B-01-clean.svg` — 17,089 bytes
- `course-content/support-resistance/chart_assets/charts/L04-B-02-zone.png` — 46,280 bytes
- `course-content/support-resistance/chart_assets/charts/L04-B-02-zone.svg` — 18,344 bytes
- `course-content/support-resistance/chart_assets/charts/L04-B-03-resistance.png` — 44,603 bytes
- `course-content/support-resistance/chart_assets/charts/L04-B-03-resistance.svg` — 18,349 bytes
- `course-content/support-resistance/chart_assets/charts/L04-C-01-practice.png` — 38,294 bytes
- `course-content/support-resistance/chart_assets/charts/L04-C-01-practice.svg` — 15,732 bytes
- `course-content/support-resistance/chart_assets/charts/L04-C-02-reference.png` — 55,465 bytes
- `course-content/support-resistance/chart_assets/charts/L04-C-02-reference.svg` — 17,748 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-01-overmarked.png` — 44,408 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-01-overmarked.svg` — 22,471 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-02-candidate-ids.png` — 50,224 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-02-candidate-ids.svg` — 26,859 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-03-reduced-reference.png` — 65,607 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-03-reduced-reference.svg` — 22,239 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-04-minor-removed.png` — 49,151 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-04-minor-removed.svg` — 25,530 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-05-nearby-combined.png` — 46,793 bytes
- `course-content/support-resistance/chart_assets/charts/L05-A-05-nearby-combined.svg` — 23,017 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-01-clean.png` — 38,929 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-01-clean.svg` — 15,757 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-02-reaction-points.png` — 48,467 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-02-reaction-points.svg` — 18,861 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-03-wick-body-guides.png` — 49,730 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-03-wick-body-guides.svg` — 18,349 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-04-too-narrow.png` — 46,352 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-04-too-narrow.svg` — 17,076 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-05-defensible.png` — 45,554 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-05-defensible.svg` — 17,060 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-06-too-broad.png` — 46,374 bytes
- `course-content/support-resistance/chart_assets/charts/L06-A-06-too-broad.svg` — 17,512 bytes
- `course-content/support-resistance/chart_assets/charts/L06-B-01-clean.png` — 36,728 bytes
- `course-content/support-resistance/chart_assets/charts/L06-B-01-clean.svg` — 15,247 bytes
- `course-content/support-resistance/chart_assets/charts/L06-B-02-defensible.png` — 44,071 bytes
- `course-content/support-resistance/chart_assets/charts/L06-B-02-defensible.svg` — 16,520 bytes
- `course-content/support-resistance/chart_assets/charts/L06-C-01-practice.png` — 38,828 bytes
- `course-content/support-resistance/chart_assets/charts/L06-C-01-practice.svg` — 15,316 bytes
- `course-content/support-resistance/chart_assets/charts/L06-C-02-reference.png` — 56,524 bytes
- `course-content/support-resistance/chart_assets/charts/L06-C-02-reference.svg` — 17,334 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-01-overmarked.png` — 43,515 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-01-overmarked.svg` — 21,607 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-02-merge-redundant.png` — 47,518 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-02-merge-redundant.svg` — 21,613 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-03-contextual-omissions.png` — 63,865 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-03-contextual-omissions.svg` — 21,363 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-04-clean-final.png` — 51,094 bytes
- `course-content/support-resistance/chart_assets/charts/L07-A-04-clean-final.svg` — 20,628 bytes
- `course-content/support-resistance/chart_assets/charts/L07-B-01-practice.png` — 41,985 bytes
- `course-content/support-resistance/chart_assets/charts/L07-B-01-practice.svg` — 19,584 bytes
- `course-content/support-resistance/chart_assets/charts/L07-B-02-reference.png` — 57,637 bytes
- `course-content/support-resistance/chart_assets/charts/L07-B-02-reference.svg` — 18,632 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-01-many-crossings.png` — 43,679 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-01-many-crossings.svg` — 18,425 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-02-fewer-interpretable.png` — 40,633 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-02-fewer-interpretable.svg` — 15,723 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-03-comparison-A.png` — 55,932 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-03-comparison-A.svg` — 19,113 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-04-comparison-B.png` — 51,327 bytes
- `course-content/support-resistance/chart_assets/charts/L08-A-04-comparison-B.svg` — 16,397 bytes
- `course-content/support-resistance/chart_assets/charts/L09-A-01-directional-approach.png` — 42,832 bytes
- `course-content/support-resistance/chart_assets/charts/L09-A-01-directional-approach.svg` — 14,307 bytes
- `course-content/support-resistance/chart_assets/charts/L09-B-01-overlapping-approach.png` — 42,129 bytes
- `course-content/support-resistance/chart_assets/charts/L09-B-01-overlapping-approach.svg` — 14,739 bytes
- `course-content/support-resistance/chart_assets/charts/L09-PRACTICE-01-clean.png` — 42,899 bytes
- `course-content/support-resistance/chart_assets/charts/L09-PRACTICE-01-clean.svg` — 13,469 bytes
- `course-content/support-resistance/chart_assets/charts/L09-PRACTICE-02-reference.png` — 57,550 bytes
- `course-content/support-resistance/chart_assets/charts/L09-PRACTICE-02-reference.svg` — 14,202 bytes
- `course-content/support-resistance/chart_assets/charts/L10-A-01-first-interaction.png` — 37,572 bytes
- `course-content/support-resistance/chart_assets/charts/L10-A-01-first-interaction.svg` — 10,550 bytes
- `course-content/support-resistance/chart_assets/charts/L10-A-02-close-away.png` — 38,110 bytes
- `course-content/support-resistance/chart_assets/charts/L10-A-02-close-away.svg` — 11,447 bytes
- `course-content/support-resistance/chart_assets/charts/L10-A-03-follow-through.png` — 40,281 bytes
- `course-content/support-resistance/chart_assets/charts/L10-A-03-follow-through.svg` — 13,895 bytes
- `course-content/support-resistance/chart_assets/charts/L10-B-01-crossing.png` — 38,981 bytes
- `course-content/support-resistance/chart_assets/charts/L10-B-01-crossing.svg` — 12,034 bytes
- `course-content/support-resistance/chart_assets/charts/L10-B-02-follow-through.png` — 49,719 bytes
- `course-content/support-resistance/chart_assets/charts/L10-B-02-follow-through.svg` — 13,650 bytes
- `course-content/support-resistance/chart_assets/charts/L10-C-01-mixed.png` — 38,891 bytes
- `course-content/support-resistance/chart_assets/charts/L10-C-01-mixed.svg` — 13,391 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-A-01-clean.png` — 38,026 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-A-01-clean.svg` — 11,661 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-A-02-reference.png` — 50,015 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-A-02-reference.svg` — 12,336 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-B-01-clean.png` — 36,352 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-B-01-clean.svg` — 10,702 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-B-02-reference.png` — 49,430 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-B-02-reference.svg` — 11,403 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-C-01-clean.png` — 37,084 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-C-01-clean.svg` — 11,168 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-C-02-reference.png` — 49,112 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-C-02-reference.svg` — 11,874 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-D-01-clean.png` — 37,280 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-D-01-clean.svg` — 11,200 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-D-02-reference.png` — 49,391 bytes
- `course-content/support-resistance/chart_assets/charts/L10-PRACTICE-D-02-reference.svg` — 11,874 bytes
- `course-content/support-resistance/chart_assets/charts/L11-01-first-reaction.png` — 41,105 bytes
- `course-content/support-resistance/chart_assets/charts/L11-01-first-reaction.svg` — 12,524 bytes
- `course-content/support-resistance/chart_assets/charts/L11-02-second-visit.png` — 42,867 bytes
- `course-content/support-resistance/chart_assets/charts/L11-02-second-visit.svg` — 15,252 bytes
- `course-content/support-resistance/chart_assets/charts/L11-03-deeper-test.png` — 44,897 bytes
- `course-content/support-resistance/chart_assets/charts/L11-03-deeper-test.svg` — 18,434 bytes
- `course-content/support-resistance/chart_assets/charts/L11-04-move-through.png` — 43,254 bytes
- `course-content/support-resistance/chart_assets/charts/L11-04-move-through.svg` — 18,779 bytes
- `course-content/support-resistance/chart_assets/charts/L12-A-01-first-crossing.png` — 36,714 bytes
- `course-content/support-resistance/chart_assets/charts/L12-A-01-first-crossing.svg` — 10,220 bytes
- `course-content/support-resistance/chart_assets/charts/L12-A-02-return-inside.png` — 37,919 bytes
- `course-content/support-resistance/chart_assets/charts/L12-A-02-return-inside.svg` — 11,858 bytes
- `course-content/support-resistance/chart_assets/charts/L12-B-01-first-crossing.png` — 38,807 bytes
- `course-content/support-resistance/chart_assets/charts/L12-B-01-first-crossing.svg` — 12,024 bytes
- `course-content/support-resistance/chart_assets/charts/L12-B-02-follow-through.png` — 39,607 bytes
- `course-content/support-resistance/chart_assets/charts/L12-B-02-follow-through.svg` — 13,418 bytes
- `course-content/support-resistance/chart_assets/charts/L12-C-01-mixed.png` — 38,337 bytes
- `course-content/support-resistance/chart_assets/charts/L12-C-01-mixed.svg` — 12,930 bytes
- `course-content/support-resistance/chart_assets/charts/L13-A-01-break-beyond.png` — 39,712 bytes
- `course-content/support-resistance/chart_assets/charts/L13-A-01-break-beyond.svg` — 12,474 bytes
- `course-content/support-resistance/chart_assets/charts/L13-B-01-return-to-area.png` — 40,404 bytes
- `course-content/support-resistance/chart_assets/charts/L13-B-01-return-to-area.svg` — 13,826 bytes
- `course-content/support-resistance/chart_assets/charts/L13-C1-hold.png` — 53,415 bytes
- `course-content/support-resistance/chart_assets/charts/L13-C1-hold.svg` — 14,597 bytes
- `course-content/support-resistance/chart_assets/charts/L13-C2-fail.png` — 53,670 bytes
- `course-content/support-resistance/chart_assets/charts/L13-C2-fail.svg` — 15,971 bytes
- `course-content/support-resistance/chart_assets/charts/L13-PRACTICE-01-clean.png` — 10,943 bytes
- `course-content/support-resistance/chart_assets/charts/L13-PRACTICE-01-clean.svg` — 7,010 bytes
- `course-content/support-resistance/chart_assets/charts/L13-PRACTICE-02-reference.png` — 13,965 bytes
- `course-content/support-resistance/chart_assets/charts/L13-PRACTICE-02-reference.svg` — 8,878 bytes
- `course-content/support-resistance/chart_assets/charts/L14-A-01-area-before-break.png` — 38,342 bytes
- `course-content/support-resistance/chart_assets/charts/L14-A-01-area-before-break.svg` — 12,286 bytes
- `course-content/support-resistance/chart_assets/charts/L14-B-01-first-move-beyond.png` — 40,253 bytes
- `course-content/support-resistance/chart_assets/charts/L14-B-01-first-move-beyond.svg` — 14,260 bytes
- `course-content/support-resistance/chart_assets/charts/L14-C-01-return-through.png` — 52,397 bytes
- `course-content/support-resistance/chart_assets/charts/L14-C-01-return-through.svg` — 16,804 bytes
- `course-content/support-resistance/chart_assets/charts/L14-D-01-pullback-holds.png` — 38,005 bytes
- `course-content/support-resistance/chart_assets/charts/L14-D-01-pullback-holds.svg` — 14,278 bytes
- `course-content/support-resistance/chart_assets/charts/L15-A-01-clean.png` — 36,147 bytes
- `course-content/support-resistance/chart_assets/charts/L15-A-01-clean.svg` — 12,526 bytes
- `course-content/support-resistance/chart_assets/charts/L15-A-02-zones.png` — 44,443 bytes
- `course-content/support-resistance/chart_assets/charts/L15-A-02-zones.svg` — 15,600 bytes
- `course-content/support-resistance/chart_assets/charts/L15-A-03-scenario-prompt.png` — 56,260 bytes
- `course-content/support-resistance/chart_assets/charts/L15-A-03-scenario-prompt.svg` — 16,308 bytes
- `course-content/support-resistance/chart_assets/charts/L15-B-01-practice.png` — 36,735 bytes
- `course-content/support-resistance/chart_assets/charts/L15-B-01-practice.svg` — 12,579 bytes
- `course-content/support-resistance/chart_assets/charts/L15-B-02-reference.png` — 59,363 bytes
- `course-content/support-resistance/chart_assets/charts/L15-B-02-reference.svg` — 15,931 bytes
- `course-content/support-resistance/chart_assets/charts/L18-A-01-unseen.png` — 41,375 bytes
- `course-content/support-resistance/chart_assets/charts/L18-A-01-unseen.svg` — 21,619 bytes
- `course-content/support-resistance/chart_assets/charts/L18-A-02-reference-internal.png` — 74,567 bytes
- `course-content/support-resistance/chart_assets/charts/L18-A-02-reference-internal.svg` — 28,100 bytes
- `course-content/support-resistance/chart_assets/charts/L18-B-01-retry-unseen.png` — 37,895 bytes
- `course-content/support-resistance/chart_assets/charts/L18-B-01-retry-unseen.svg` — 17,527 bytes
- `course-content/support-resistance/chart_assets/charts/L18-B-02-retry-reference-internal.png` — 67,414 bytes
- `course-content/support-resistance/chart_assets/charts/L18-B-02-retry-reference-internal.svg` — 23,765 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG01_breakout_evidence_ladder.png` — 86,635 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG02_filter_tradeoffs.png` — 115,483 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG03_context_changes_the_question.png` — 100,452 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG04_break_return_response.png` — 81,995 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG05_three_retest_outcomes.png` — 94,093 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG06_failure_sequence.png` — 87,459 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG07_failure_is_not_reverse_signal.png` — 113,367 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG08_volume_context_not_gate.png` — 110,565 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG09_decision_record_timeline.png` — 113,868 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/assets/figures/FIG10_failed_signal_family.png` — 117,393 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L12-01-before-break.png` — 63,659 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L12-02-outside-zone.png` — 72,534 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L12-03-later-failure.png` — 81,081 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L13-01-before-break.png` — 67,043 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L13-02-return-toward-area.png` — 70,162 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L13-03-later-evidence.png` — 86,575 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L14-01-before-break.png` — 65,971 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L14-02-initial-return.png` — 73,153 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/charts/L14-03-failed-follow-through.png` — 80,351 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v2/FIGURE_OVERVIEW.png` — 352,978 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG00_boundary_episode_overview.png` — 1,163,182 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG01_breakout_evidence_ladder.png` — 125,592 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG02_filter_tradeoffs.png` — 155,292 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG03_context_changes_the_question.png` — 134,205 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG04_break_return_response.png` — 122,820 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG05_three_retest_outcomes.png` — 126,895 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG06_retest_is_not_owed.png` — 158,275 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG07_failure_is_not_reverse_signal.png` — 137,190 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG08_volume_context_not_gate.png` — 176,101 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG09_decision_record_timeline.png` — 119,666 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG10_failed_signal_family.png` — 213,274 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG11_first_pullback_later_failure.png` — 116,592 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG12_after_failure_alternatives.png` — 135,879 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG13_gap_and_spike_failures.png` — 131,916 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG14_failed_failure_reclaim.png` — 110,965 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG15_failure_label_checklist.png` — 168,144 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG16_retest_depth_and_closes.png` — 136,917 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG17_range_vs_trendline_failure.png` — 125,174 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG18_neckline_formation_failures.png` — 121,250 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG19_simple_break_return_response.png` — 81,995 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG20_simple_retest_outcomes.png` — 94,093 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG21_failed_breakout_structural_stop.png` — 129,876 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG22_range_edge_upthrust.png` — 151,888 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG23_spring_downside_reclaim.png` — 141,437 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG24_prior_swing_failure_test.png` — 139,048 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/assets/figures/FIG25_continuation_pause_outcomes.png` — 159,238 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L12-01-before-break.png` — 63,659 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L12-02-outside-zone.png` — 72,534 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L12-03-later-failure.png` — 81,081 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L13-01-before-break.png` — 67,043 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L13-02-return-toward-area.png` — 70,162 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L13-03-later-evidence.png` — 86,575 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L14-01-before-break.png` — 65,971 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L14-02-initial-return.png` — 73,153 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/charts/L14-03-failed-follow-through.png` — 80,351 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/FIGURE_OVERVIEW.png` — 1,017,137 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5_2/tools/source_figures/FIG00_generated_overview_source.png` — 1,243,086 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG00_boundary_episode_overview.png` — 1,163,182 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG01_breakout_evidence_ladder.png` — 125,592 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG02_filter_tradeoffs.png` — 155,292 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG03_context_changes_the_question.png` — 134,205 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG04_break_return_response.png` — 122,820 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG05_three_retest_outcomes.png` — 126,895 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG06_retest_is_not_owed.png` — 158,275 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG07_failure_is_not_reverse_signal.png` — 137,190 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG08_volume_context_not_gate.png` — 176,101 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG09_decision_record_timeline.png` — 119,666 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG10_failed_signal_family.png` — 213,274 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG11_first_pullback_later_failure.png` — 116,592 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG12_after_failure_alternatives.png` — 135,879 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG13_gap_and_spike_failures.png` — 131,916 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG14_failed_failure_reclaim.png` — 110,965 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG15_failure_label_checklist.png` — 168,144 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG16_retest_depth_and_closes.png` — 136,917 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG17_range_vs_trendline_failure.png` — 125,174 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG18_neckline_formation_failures.png` — 121,250 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG19_simple_break_return_response.png` — 81,995 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG20_simple_retest_outcomes.png` — 94,093 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG21_failed_breakout_structural_stop.png` — 129,876 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG22_range_edge_upthrust.png` — 151,888 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG23_spring_downside_reclaim.png` — 141,437 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG24_prior_swing_failure_test.png` — 139,048 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/assets/figures/FIG25_continuation_pause_outcomes.png` — 159,238 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L12-01-before-break.png` — 63,659 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L12-02-outside-zone.png` — 72,534 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L12-03-later-failure.png` — 81,081 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L13-01-before-break.png` — 67,043 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L13-02-return-toward-area.png` — 70,162 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L13-03-later-evidence.png` — 86,575 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L14-01-before-break.png` — 65,971 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L14-02-initial-return.png` — 73,153 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/charts/L14-03-failed-follow-through.png` — 80,351 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/FIGURE_OVERVIEW.png` — 1,017,137 bytes
- `course-content/support-resistance/production/previews/module5-breakouts-failures-v5/tools/source_figures/FIG00_generated_overview_source.png` — 1,243,086 bytes
- `course-source/starter-drip-course/charts/generated/L1-01-auction.png` — 49,040 bytes
- `course-source/starter-drip-course/charts/generated/L1-02-order-types.png` — 65,122 bytes
- `course-source/starter-drip-course/charts/generated/L1-03-candle-anatomy.png` — 36,575 bytes
- `course-source/starter-drip-course/charts/generated/L1-03-timeframes.png` — 178,881 bytes
- `course-source/starter-drip-course/charts/generated/L1-03-volume-spike.png` — 39,214 bytes
- `course-source/starter-drip-course/charts/generated/L1-04-point-move.png` — 78,196 bytes
- `course-source/starter-drip-course/charts/generated/L1-05-equity-curves.png` — 111,820 bytes
- `course-source/starter-drip-course/charts/generated/L1-06-spread.png` — 57,365 bytes
- `course-source/starter-drip-course/charts/generated/L1-07-three-analyses.png` — 80,492 bytes
- `course-source/starter-drip-course/charts/generated/L1-08-styles.png` — 100,081 bytes
- `course-source/starter-drip-course/charts/generated/L2-09-sr-zones.png` — 108,981 bytes
- `course-source/starter-drip-course/charts/generated/L2-10-trendline-channel.png` — 87,460 bytes
- `course-source/starter-drip-course/charts/generated/L2-11-candle-patterns.png` — 407,158 bytes
- `course-source/starter-drip-course/charts/generated/L2-12-chart-patterns.png` — 80,480 bytes
- `course-source/starter-drip-course/charts/generated/L2-13-moving-averages.png` — 113,314 bytes
- `course-source/starter-drip-course/charts/generated/L2-14-rsi-divergence.png` — 79,259 bytes
- `course-source/starter-drip-course/charts/generated/L2-15-fibonacci.png` — 80,680 bytes
- `course-source/starter-drip-course/charts/generated/L2-16-topdown.png` — 150,865 bytes
- `course-source/starter-drip-course/charts/generated/L2-22-breakout-vs-pullback.png` — 122,755 bytes
- `course-source/starter-drip-course/charts/generated/L3-17-trade-anatomy.png` — 88,404 bytes
- `course-source/starter-drip-course/charts/generated/L3-18-stop-placement.png` — 100,842 bytes
- `course-source/starter-drip-course/charts/generated/L3-21-risk-reward.png` — 76,468 bytes
- `course-source/starter-drip-course/charts/generated/L4-26-overtrading.png` — 117,790 bytes
- `course-source/starter-drip-course/charts/generated/L4-28-backtest.png` — 93,269 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-candle-context-compare-mobile.svg` — 11,726 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-candle-context-compare.svg` — 17,529 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage1-spot-volume-mobile.svg` — 4,519 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage1-spot-volume.svg` — 5,305 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage3-breakout-initial-mobile.svg` — 6,024 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage3-breakout-initial.svg` — 7,240 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage3-outcome-continuation-mobile.svg` — 7,042 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage3-outcome-continuation.svg` — 8,058 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage3-outcome-failure-mobile.svg` — 7,039 bytes
- `course-source/volume-price-analysis/assets/exports/vpa-m01-l01-stage3-outcome-failure.svg` — 8,058 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-candle-context-compare-mobile.svg` — 11,726 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-candle-context-compare.svg` — 17,529 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage1-spot-volume-mobile.svg` — 4,519 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage1-spot-volume.svg` — 5,305 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage3-breakout-initial-mobile.svg` — 6,024 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage3-breakout-initial.svg` — 7,240 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage3-outcome-continuation-mobile.svg` — 7,042 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage3-outcome-continuation.svg` — 8,058 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage3-outcome-failure-mobile.svg` — 7,039 bytes
- `course-source/volume-price-analysis/assets/source/vpa-m01-l01-stage3-outcome-failure.svg` — 8,058 bytes
- `review/screenshots/construct-community-desktop-pass-2.png` — 211,555 bytes
- `review/screenshots/construct-community-mobile-pass-2.png` — 85,910 bytes
- `review/screenshots/construct-hero-desktop-pass-2.png` — 372,474 bytes
- `review/screenshots/construct-paper-practice-desktop-pass-2.png` — 230,396 bytes
- `review/screenshots/construct-paper-practice-mobile-pass-2.png` — 86,195 bytes
- `review/screenshots/course-comparison-desktop-pass-2.png` — 280,409 bytes
- `review/screenshots/course-comparison-mobile-pass-2.png` — 83,878 bytes
- `review/screenshots/course-construct-offer-desktop-pass-2.png` — 259,684 bytes
- `review/screenshots/course-construct-offer-mobile-pass-2.png` — 88,517 bytes
- `review/screenshots/desktop-full-viewport.png` — 320,589 bytes
- `review/screenshots/desktop-overview.png` — 137,951 bytes
- `review/screenshots/desktop-short-viewport.png` — 137,951 bytes
- `review/screenshots/homepage-learning-desktop-pass-2.png` — 257,581 bytes
- `review/screenshots/homepage-learning-mobile-pass-2.png` — 85,859 bytes
- `review/screenshots/homepage-options-desktop-pass-2.png` — 221,684 bytes
- `review/screenshots/homepage-options-mobile-pass-2.png` — 87,439 bytes
- `review/screenshots/mobile-drawer.png` — 98,536 bytes
- `site/assets/breakout-failure-figures/FIG01_breakout_evidence_ladder.png` — 125,592 bytes
- `site/assets/breakout-failure-figures/FIG02_filter_tradeoffs.png` — 155,292 bytes
- `site/assets/breakout-failure-figures/FIG03_context_changes_the_question.png` — 134,205 bytes
- `site/assets/breakout-failure-figures/FIG04_break_return_response.png` — 122,820 bytes
- `site/assets/breakout-failure-figures/FIG05_three_retest_outcomes.png` — 126,895 bytes
- `site/assets/breakout-failure-figures/FIG06_retest_is_not_owed.png` — 158,275 bytes
- `site/assets/breakout-failure-figures/FIG07_failure_is_not_reverse_signal.png` — 137,190 bytes
- `site/assets/breakout-failure-figures/FIG08_volume_context_not_gate.png` — 176,101 bytes
- `site/assets/breakout-failure-figures/FIG09_decision_record_timeline.png` — 119,666 bytes
- `site/assets/breakout-failure-figures/FIG10_failed_signal_family.png` — 213,274 bytes
- `site/assets/breakout-failure-figures/FIG14_failed_failure_reclaim.png` — 110,965 bytes
- `site/assets/breakout-failure-figures/FIG17_range_vs_trendline_failure.png` — 125,174 bytes
- `site/assets/breakout-failure-figures/FIG18_neckline_formation_failures.png` — 121,250 bytes
- `site/assets/breakout-failure-figures/FIG19_simple_break_return_response.png` — 81,995 bytes
- `site/assets/breakout-failure-figures/FIG20_simple_retest_outcomes.png` — 94,093 bytes
- `site/assets/tradethesis-horizontal.png` — 28,446 bytes
- `site/assets/tradethesis-icon.png` — 23,834 bytes
- `site/assets/tradethesis-wordmark.png` — 23,828 bytes
- `site/module5-v5_2/assets/figures/FIG00_boundary_episode_overview.png` — 1,163,182 bytes
- `site/module5-v5_2/assets/figures/FIG01_breakout_evidence_ladder.png` — 125,592 bytes
- `site/module5-v5_2/assets/figures/FIG02_filter_tradeoffs.png` — 155,292 bytes
- `site/module5-v5_2/assets/figures/FIG03_context_changes_the_question.png` — 134,205 bytes
- `site/module5-v5_2/assets/figures/FIG04_break_return_response.png` — 122,820 bytes
- `site/module5-v5_2/assets/figures/FIG05_three_retest_outcomes.png` — 126,895 bytes
- `site/module5-v5_2/assets/figures/FIG06_retest_is_not_owed.png` — 158,275 bytes
- `site/module5-v5_2/assets/figures/FIG07_failure_is_not_reverse_signal.png` — 137,190 bytes
- `site/module5-v5_2/assets/figures/FIG08_volume_context_not_gate.png` — 176,101 bytes
- `site/module5-v5_2/assets/figures/FIG09_decision_record_timeline.png` — 119,666 bytes
- `site/module5-v5_2/assets/figures/FIG10_failed_signal_family.png` — 213,274 bytes
- `site/module5-v5_2/assets/figures/FIG11_first_pullback_later_failure.png` — 116,592 bytes
- `site/module5-v5_2/assets/figures/FIG12_after_failure_alternatives.png` — 135,879 bytes
- `site/module5-v5_2/assets/figures/FIG13_gap_and_spike_failures.png` — 131,916 bytes
- `site/module5-v5_2/assets/figures/FIG14_failed_failure_reclaim.png` — 110,965 bytes
- `site/module5-v5_2/assets/figures/FIG15_failure_label_checklist.png` — 168,144 bytes
- `site/module5-v5_2/assets/figures/FIG16_retest_depth_and_closes.png` — 136,917 bytes
- `site/module5-v5_2/assets/figures/FIG17_range_vs_trendline_failure.png` — 125,174 bytes
- `site/module5-v5_2/assets/figures/FIG18_neckline_formation_failures.png` — 121,250 bytes
- `site/module5-v5_2/assets/figures/FIG19_simple_break_return_response.png` — 81,995 bytes
- `site/module5-v5_2/assets/figures/FIG20_simple_retest_outcomes.png` — 94,093 bytes
- `site/module5-v5_2/assets/figures/FIG21_failed_breakout_structural_stop.png` — 129,876 bytes
- `site/module5-v5_2/assets/figures/FIG22_range_edge_upthrust.png` — 151,888 bytes
- `site/module5-v5_2/assets/figures/FIG23_spring_downside_reclaim.png` — 141,437 bytes
- `site/module5-v5_2/assets/figures/FIG24_prior_swing_failure_test.png` — 139,048 bytes
- `site/module5-v5_2/assets/figures/FIG25_continuation_pause_outcomes.png` — 159,238 bytes
- `site/module5-v5_2/charts/L12-A-01-first-crossing.png` — 36,714 bytes
- `site/module5-v5_2/charts/L12-A-02-return-inside.png` — 37,919 bytes
- `site/module5-v5_2/charts/L12-B-02-follow-through.png` — 39,607 bytes
- `site/module5-v5_2/charts/L13-A-01-break-beyond.png` — 39,712 bytes
- `site/module5-v5_2/charts/L13-B-01-return-to-area.png` — 40,404 bytes
- `site/module5-v5_2/charts/L13-C1-hold.png` — 53,415 bytes
- `site/module5-v5_2/charts/L13-C2-fail.png` — 53,670 bytes
- `site/module5-v5_2/charts/L14-A-01-area-before-break.png` — 38,342 bytes
- `site/module5-v5_2/charts/L14-B-01-first-move-beyond.png` — 40,253 bytes
- `site/module5-v5_2/charts/L14-C-01-return-through.png` — 52,397 bytes
- `site/module5-v5_2/charts/L14-D-01-pullback-holds.png` — 38,005 bytes

## Validation notes

- Repository, branch, page shell, script references, CSS sizing rules, figure files, figure inventory, and existing Learning Room CI workflow were inspected.
- The static figure source assets and their visible panel structures were reviewed using representative PNGs (including the multi-panel figures called out above).
- A reusable inspector and focused Playwright test are included in the proposed feature branch change set.
- Browser validation should be considered complete only if the new GitHub Actions browser workflow passes. If the workflow cannot run, or cannot visually inspect a source, it must be reported rather than described as verified.
- No chart, annotation, lesson text, stage filename, model answer, answer gate, legacy route, or activity scoring rule is intentionally modified by this readability work.
