# Binary Asset Transfer Status

**Status: committed to `my-new-branch`. Inventory and path coverage are verified; all 48 CSV datasets match the source content after normalizing Git's LF line endings. Full remote-byte SHA-256 verification of all 242 rendered files was completed on 2026-10-15; all matched their recorded checksum entries. Full visual/instructional approval remains outstanding.**

## Verified Git record

- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Asset upload commit: `8e4e3c411567aeebd26146daf6be7fe0a65a8e74` — [view commit](https://github.com/ZaphodBeeblebrox12/prototypeweb/commit/8e4e3c411567aeebd26146daf6be7fe0a65a8e74)
- Commit message: `this is course-content/support-resistance/chart_assets`
- Asset directory: `course-content/support-resistance/chart_assets/`

The upload commit added 292 files to Git. The current branch tree contains the expected inventory:

- 121 PNG chart renders.
- 121 SVG chart renders.
- 48 OHLC/source CSV datasets under `data/`.
- 2 existing CSV manifests.
- `source/build_chart_assets.py`.
- `SHA256SUMS.txt`.

## Integrity and scope of verification

The local overlay archive `tradethesis_sr_chart_assets_repo_overlay_v1.zip` is 4,528,218 bytes, SHA-256 `17b81228ec7aa976c859d75d6c3a7050e80b7088eae169eda4f017d4cb40ca8b`. Its 291 checksum entries (121 PNG + 121 SVG + 48 data CSVs + the generator) were checked against the archive contents; all matched. All 291 unique paths in that inventory exist in the Git tree, with no missing or duplicate inventory paths.

All 48 committed CSV Git blobs were compared against the local source using Git's expected CRLF-to-LF line-ending normalization; all 48 matched. The original checksum inventory records SHA-256 hashes of the extracted source files, where the CSVs use CRLF. Git stores normalized LF text blobs, so comparing the recorded CSV hashes directly to LF-formatted Git blob bytes will produce a different hash even when the data content matches. The checksum inventory is intentionally left unchanged because its hashes correctly describe the source overlay files.

The full remote-byte SHA-256 comparison of all 242 rendered chart files (121 PNG and 121 SVG) was completed on 2026-10-15. Every remote file matched its corresponding entry in `SHA256SUMS.txt`; no byte mismatches were found. This supersedes the earlier representative-only verification note.

The CSV values are synthetic illustrative values, not historical market data. File presence and checksum verification do not constitute visual, instructional, or learner-facing approval.

## Remaining work

1. Review the rendered charts visually against their intended teaching cues and approve or log issues; checksum success is not visual or instructional approval.
2. Continue to treat authentic instructor materials for Lessons 9, 16, and 17 as outstanding dependencies. Synthetic chart assets do not replace those records.

## Regeneration policy

Use the committed CSV source data and `source/build_chart_assets.py` as reproducible inputs. Before regenerating, inspect the script's dependencies and output paths; run it in an isolated environment and compare generated files to committed exports. Do not overwrite committed chart renders just because regeneration runs successfully. Update manifests and checksums only when a reviewed asset change is intentional.

## Boundaries

- Internal reference states and answer keys must not be placed in learner-facing delivery.
- Asset file presence does not mean the visuals are approved; visual review remains outstanding.
- No website, course-room, or other repository files are included in this proposed documentation-only change.
