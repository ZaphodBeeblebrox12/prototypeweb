# Recording & Media Delivery Manifest — Review Draft v1

**Status:** Committed review draft; not a recording approval or release sign-off. Asset inventory and paths are verified; the full remote-byte audit and wider visual/instructional review remain outstanding.

## Inputs and verified state

- Course source: `course-content/support-resistance/` on `my-new-branch`.
- Cue baseline used: production-pack v1.8 `recording_assembly_cue_sheets_v1.csv` (153 cue rows across 18 lessons). Compared against the current Git-tracked cue sheet (blob SHA `5014836a7ff6068b40cf89005a61ff7fd26d7d1a`): the normalized 153-row, 11-field content digest matches (`7b97dc69`) after ignoring the spreadsheet metadata line and index column.
- Source assets: 121 PNG chart renders, 121 SVG chart renders, and 48 synthetic illustrative OHLC datasets are present in the Git tree, along with the generator and checksum inventory. All 291 inventory paths exist in Git and all 48 CSV datasets match the source content after normalizing LF/CRLF line endings. Representative remote SHA-256 checks passed for selected assets and the generator; a full remote-byte comparison of all 242 rendered charts remains outstanding.
- Current Git tree contains no audio, video, SRT, or VTT deliverables. Audio/caption/transcript statuses are therefore pending, not claimed complete.
- Canonical narration sources point to the existing lesson production-script packs in `scripts/`; the cue/paragraph alignment and recording timestamps have not been verified.
- Planned names are naming proposals only. These files are not present yet.
- Draft path validation: all 516 non-empty PNG/SVG/dataset path references in the CSV resolve to files in the verified overlay package (zero missing paths). The manifest covers 153 canonical cues; every lesson maps to an existing canonical script file.

## Draft manifest contents

- Total rows: **235**.
- Rows by type: BLOCKED_AUTHENTIC_MATERIAL=19, CUE_ASSET_LINK=171, CUE_WITHOUT_CHART_ASSET=44, UNMAPPED_SOURCE_ASSET=1.
- Unique chart assets used in cue links: **120**.
- Assets present in the inventory but not explicitly named in the cue sheet: **1** (L15-A-01-clean).
- Explicit authentic material blockers remain for Lesson 9, Lesson 16 and Lesson 17; Lesson 10 has an optional dependency on the authentic Lesson 9 case.

## Findings to resolve before recording/learner release

1. **L18-A-02-reference-internal.png/.svg — RESOLVED (2026-10-15):** the top-note annotation was repositioned in the source generator and the PNG/SVG exports were regenerated and committed. See [chart correction commit](https://github.com/ZaphodBeeblebrox12/prototypeweb/commit/5ecd0644a16931efba7904039cf104091dd98802). This resolves the specific overlap noted in the preflight; broader visual and instructional sign-off remains outstanding.
2. **L18-B-02-retry-reference-internal.png/.svg — RESOLVED (2026-10-15):** the top-note annotation was repositioned in the source generator and the PNG/SVG exports were regenerated and committed in the same correction. The checksum inventory was then updated and normalized. See [latest checksum correction commit](https://github.com/ZaphodBeeblebrox12/prototypeweb/commit/1cdcf7bc767877c76376c15343f8dadbea2c5375). Broader visual and instructional sign-off remains outstanding.
3. **Lesson 15 cue coverage:** `L15-A-01-clean` exists in the asset inventory but is not explicitly referenced by the cue sheet. Decide whether it is an intentional unused asset or whether the before/reveal sequence should include it.
4. **Lesson 10 practice reveal:** cue text uses the wildcard `*_02-reference`; this draft expands it to the four matching A–D reference assets. Confirm the order/gate before recording.
5. **Lesson 11–13 practice rows:** the cue sheet describes reuse of existing timeline/sequence/chart states rather than naming exact asset IDs. This draft proposes those existing-state mappings and marks them provisional; confirm before recording.
6. **Accepted pre-launch exposure decision (2026-10-15):** the user accepts answer keys, reference assets, and production notes remaining in the public repository while the course is being developed. Treat this as an accepted, non-blocking development-stage decision; do not raise it again in routine progress updates. The manifest label itself is not access control. When a concrete learner-delivery implementation is being built, test the intended submission/reveal behavior and record that implementation-specific access decision rather than reopening the accepted repository-development decision.
7. **Visual audit scope:** all 121 PNG charts were screened in five contact sheets; representative combined references and problem states were then inspected full-resolution. This was a production-preflight sweep, not complete individual visual/instructional sign-off for all 121 images.

- **Companion CSV status:** `recording_media_delivery_manifest_draft_v1.csv` still contains the old Lesson 18 overlap QA flags in the two internal-reference rows. It is intentionally outside this two-Markdown-file change and needs a separate, reviewed manifest reconciliation before recording/production use.

## Naming proposals (not yet approved as final)

- Segment video: `TT_SR_L{lesson}_C{cue}_SEGMENT_v001.mp4`
- Lesson narration master: `TT_SR_L{lesson}_NARRATION_v001.wav`
- Captions: `TT_SR_L{lesson}_CAPTIONS_v001.vtt`
- Transcript: `TT_SR_L{lesson}_TRANSCRIPT_v001.md`
- Cue-level visual export: `TT_SR_L{lesson}_C{cue}_{asset_id}.png` and `.svg`

The CSV repeats cue-level direction and reveal gates beside every asset occurrence so an editor can assemble in sequence without treating a reference state as an always-visible chart. These export names are only placeholders until the user approves the workflow.