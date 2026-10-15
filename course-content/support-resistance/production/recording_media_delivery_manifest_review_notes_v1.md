# Recording & Media Delivery Manifest — Review Draft v1

**Status:** Committed review draft; not a recording approval or release sign-off. Asset inventory/path coverage and the full remote-byte SHA-256 audit are verified. Wider visual/instructional approval, cue-to-narration alignment, and media assembly remain outstanding.

## Inputs and verified state

- Course source: `course-content/support-resistance/` on `my-new-branch`.
- Cue baseline used: production-pack v1.8, 153 cue rows across 18 lessons. Before this reviewed reconciliation, the normalized 153-row, 11-field content digest in the Git-tracked cue sheet matched the v1.8 baseline (`7b97dc69`) after ignoring the spreadsheet metadata line and index column. The current cue sheet now intentionally differs in the reviewed Lesson 10–13 and Lesson 15 cue instructions recorded below.
- Source assets: 121 PNG chart renders, 121 SVG chart renders, and 48 synthetic illustrative OHLC datasets are present in the Git tree, along with the generator and checksum inventory. All 291 inventory paths exist in Git and all 48 CSV datasets match the source content after normalizing LF/CRLF line endings. The full remote-byte SHA-256 comparison of all 242 rendered charts was completed on 2026-10-15: all 121 PNG and 121 SVG files matched their recorded `SHA256SUMS.txt` entries with no byte mismatches. This integrity result is not full visual/instructional approval.
- Current Git tree contains no audio, video, SRT, or VTT deliverables. Audio/caption/transcript statuses are therefore pending, not claimed complete.
- Canonical narration sources point to the existing lesson production-script packs in `scripts/`; the cue/paragraph alignment and recording timestamps have not been verified.
- Planned names are naming proposals only. These files are not present yet.
- Draft path validation before this reconciliation: all 516 non-empty PNG/SVG/dataset path references resolved to files in the verified overlay package. After the approved Lesson 13 change replaces four reused chart-link rows with one no-asset hold row, the manifest retains 504 non-empty source PNG/SVG/dataset path references; the remaining cue-linked source paths are carried forward unchanged and the held Lesson 13 row has no chart paths. The manifest still covers the 153 canonical cue rows, with Lesson 13 cue 5 explicitly held rather than treated as an asset-backed practice.

## Draft manifest contents

- Total rows after reviewed reconciliation: **232**.
- Rows by type: BLOCKED_AUTHENTIC_MATERIAL=19, CUE_ASSET_LINK=167, CUE_WITHOUT_CHART_ASSET=45, UNMAPPED_SOURCE_ASSET=1.
- Unique chart assets used in cue links: **120**.
- One inventory asset is not explicitly named in a recording cue: **L15-A-01-clean**, now explicitly designated intentionally unused in the current recording plan because Lesson 15 opens on the already-marked L15-A-02-zones state. It remains in the source inventory.
- Explicit authentic material blockers remain for Lesson 9, Lesson 16 and Lesson 17; Lesson 10 has an optional dependency on the authentic Lesson 9 case.

## Findings to resolve before recording/learner release

1. **L18-A-02-reference-internal.png/.svg — RESOLVED (2026-10-15):** the top-note annotation was repositioned in the source generator and the PNG/SVG exports were regenerated and committed. See [chart correction commit](https://github.com/ZaphodBeeblebrox12/prototypeweb/commit/5ecd0644a16931efba7904039cf104091dd98802). This resolves the specific overlap noted in the preflight; broader visual and instructional sign-off remains outstanding.
2. **L18-B-02-retry-reference-internal.png/.svg — RESOLVED (2026-10-15):** the top-note annotation was repositioned in the source generator and the PNG/SVG exports were regenerated and committed in the same correction. The checksum inventory was then updated and normalized. See [latest checksum correction commit](https://github.com/ZaphodBeeblebrox12/prototypeweb/commit/1cdcf7bc767877c76376c15343f8dadbea2c5375). Broader visual and instructional sign-off remains outstanding.
3. **Lesson 15 cue coverage — RESOLVED:** `L15-A-01-clean` is intentionally unused in the current recording plan. Cue 1 starts with `L15-A-02-zones`, which matches the script's opening with zones already marked. The clean state remains in the asset inventory but is not exported or inserted into the recording sequence.
4. **Lesson 10 practice reveal — RESOLVED:** the cue sheet and manifest now explicitly interleave each practice clean state with its own reference: A clean → A reference, then B, C and D in the same order. Each reference remains gated until its own response is submitted; the four reference states must not be preloaded.
5. **Lessons 11–12 familiar-state reuse — RESOLVED AS RETRIEVAL:** the follow-up cue reuses the named timeline/crossing states to practise updating reasoning. The cue and manifest now label this as retrieval/reflection on familiar examples, not unseen or independent practice.
6. **Lesson 13 guided practice — HELD:** the four existing L13 state links are removed from the separate practice cue because those states already appear in the teaching sequence. Cue 5 remains explicitly held until a genuinely fresh chart is committed or the user explicitly approves re-scoping it as familiar-example retrieval.
7. **Accepted pre-launch exposure decision (2026-10-15): the user accepts answer keys, reference assets, and production notes remaining in the public repository while the course is being developed. Treat this as an accepted, non-blocking development-stage decision; do not raise it again in routine progress updates. The manifest label itself is not access control. When a concrete learner-delivery implementation is being built, test the intended submission/reveal behavior and record that implementation-specific access decision rather than reopening the accepted repository-development decision.
8. **Visual audit scope:** all 121 PNG charts were screened in five contact sheets; representative combined references and problem states were then inspected full-resolution. This was a production-preflight sweep, not complete individual visual/instructional sign-off for all 121 images.

- **Companion CSV reconciliation — RESOLVED FOR THIS PASS:** the two Lesson 18 rows now record the specific annotation-overlap correction as resolved in the committed generator and PNG/SVG exports. The rows explicitly retain the outstanding full visual/instructional sign-off and reveal-gate/runtime testing; this is not recording or release approval.

## Naming proposals (not yet approved as final)

- Segment video: `TT_SR_L{lesson}_C{cue}_SEGMENT_v001.mp4`
- Lesson narration master: `TT_SR_L{lesson}_NARRATION_v001.wav`
- Captions: `TT_SR_L{lesson}_CAPTIONS_v001.vtt`
- Transcript: `TT_SR_L{lesson}_TRANSCRIPT_v001.md`
- Cue-level visual export: `TT_SR_L{lesson}_C{cue}_{asset_id}.png` and `.svg`

The CSV repeats cue-level direction and reveal gates beside every asset occurrence so an editor can assemble in sequence without treating a reference state as an always-visible chart. These export names are only placeholders until the user approves the workflow.