# Recording & Media Delivery Manifest — Review Draft v1

**Status:** Local review draft only. Not committed. The Git repository was not changed while preparing this proposal.

## Inputs and verified state

- Course source: `course-content/support-resistance/` on `my-new-branch`.
- Cue baseline used: production-pack v1.8 `recording_assembly_cue_sheets_v1.csv` (153 cue rows across 18 lessons). Compared against the current Git-tracked cue sheet (blob SHA `5014836a7ff6068b40cf89005a61ff7fd26d7d1a`): the normalized 153-row, 11-field content digest matches (`7b97dc69`) after ignoring the spreadsheet metadata line and index column.
- Source assets: 121 chart states, each exported as PNG and SVG; 48 synthetic illustrative OHLC datasets. Remote checksum audit passed for 121 PNGs + 121 SVGs; all 48 CSVs match the source inventory after normalizing LF/CRLF line endings.
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

1. **L18-A-02-reference-internal.png/.svg:** full-resolution PNG review shows a collision between the top instructional banner and nearby marker/label text. Reposition the annotation via the source generator and recheck the PNG and SVG before production use.
2. **L18-B-02-retry-reference-internal.png/.svg:** the `earlier high` label overlaps the top banner in the full-resolution PNG. Reposition via the source generator and recheck both exports.
3. **Lesson 15 cue coverage:** `L15-A-01-clean` exists in the asset inventory but is not explicitly referenced by the cue sheet. Decide whether it is an intentional unused asset or whether the before/reveal sequence should include it.
4. **Lesson 10 practice reveal:** cue text uses the wildcard `*_02-reference`; this draft expands it to the four matching A–D reference assets. Confirm the order/gate before recording.
5. **Lesson 11–13 practice rows:** the cue sheet describes reuse of existing timeline/sequence/chart states rather than naming exact asset IDs. This draft proposes those existing-state mappings and marks them provisional; confirm before recording.
6. **Answer-key confidentiality:** `L18-A-02-reference-internal` and `L18-B-02-retry-reference-internal` are internal answer-key drawings, but they live in a public repository and are directly accessible. The manifest label is not an access-control mechanism. Keep them out of learner payloads; if they must remain confidential before submission, move them into private controlled storage before assessment pilot/launch.
7. **Visual audit scope:** all 121 PNG charts were screened in five contact sheets; representative combined references and problem states were then inspected full-resolution. This was a production-preflight sweep, not complete individual visual/instructional sign-off for all 121 images.

## Naming proposals (not yet approved as final)

- Segment video: `TT_SR_L{lesson}_C{cue}_SEGMENT_v001.mp4`
- Lesson narration master: `TT_SR_L{lesson}_NARRATION_v001.wav`
- Captions: `TT_SR_L{lesson}_CAPTIONS_v001.vtt`
- Transcript: `TT_SR_L{lesson}_TRANSCRIPT_v001.md`
- Cue-level visual export: `TT_SR_L{lesson}_C{cue}_{asset_id}.png` and `.svg`

The CSV repeats cue-level direction and reveal gates beside every asset occurrence so an editor can assemble in sequence without treating a reference state as an always-visible chart. These export names are only placeholders until the user approves the workflow.