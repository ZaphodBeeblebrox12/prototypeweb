# Binary Asset Transfer Status

**Status: prepared and verified locally; Git transfer is still pending. Do not mark complete until the user's local Git push is verified from the branch tree.**

## Verified inputs and inventory

The following archives were found in the ChatGPT Library and materialized into the current working session:

- `tradethesis_sr_course_production_pack_v1_8.zip` — 6,986,161 bytes; SHA-256 `347074b5ae607a6d442763e4b2d606a5f83216158007bf15d3a9f3594633ac42`.
- `tradethesis_sr_chart_assets_v1.zip` — 5,420,019 bytes; SHA-256 `772844620389972a61ab77c955a9caed3bb8673afb701c57e7bcf58187d31eb6`.

The chart-assets archive was extracted and inspected. It contains exactly 121 PNG renders, 121 SVG renders, 48 OHLC/source CSV datasets, and one `source/build_chart_assets.py` generator. The 121 asset-manifest IDs each resolve to both `charts/<asset_id>.png` and `charts/<asset_id>.svg`; all 48 dataset-manifest paths resolve to files under `data/`. These are synthetic illustrative values, not historical market data. This was a file/path/count audit, not visual or instructional approval.

A repository-overlay ZIP was prepared with the exact destination layout under `course-content/support-resistance/chart_assets/`. It contains only `charts/`, `data/`, `source/` and a SHA-256 inventory; it deliberately excludes the existing manifests and documentation so the extraction does not overwrite current Git-tracked text files.

- Overlay ZIP: `tradethesis_sr_chart_assets_repo_overlay_v1.zip`
- Size: 4,528,218 bytes
- SHA-256: `17b81228ec7aa976c859d75d6c3a7050e80b7088eae169eda4f017d4cb40ca8b`
- Inventory: 291 file checksums (121 PNG + 121 SVG + 48 CSV + 1 generator)
- ZIP entries: 292 including `chart_assets/SHA256SUMS.txt`

The GitHub integration can update text files, but cannot transfer these local binary files into Git. Therefore, this is a prepared transfer package, **not a completed repository transfer**.

## Exact local transfer procedure (PowerShell)

Download the prepared overlay ZIP to the root of a local clone of this repository. Do not add either full production ZIP to Git.

```powershell
git clone https://github.com/ZaphodBeeblebrox12/prototypeweb.git
Set-Location prototypeweb
git switch my-new-branch
git pull --ff-only

# Put tradethesis_sr_chart_assets_repo_overlay_v1.zip in this directory.
(Get-FileHash .\tradethesis_sr_chart_assets_repo_overlay_v1.zip -Algorithm SHA256).Hash.ToLower()
# Expected: 17b81228ec7aa976c859d75d6c3a7050e80b7088eae169eda4f017d4cb40ca8b

Expand-Archive -LiteralPath .\tradethesis_sr_chart_assets_repo_overlay_v1.zip -DestinationPath . -Force

# Verify every file listed in the bundle inventory.
Get-Content .\course-content\support-resistance\chart_assets\SHA256SUMS.txt | ForEach-Object {
    $parts = $_ -split '  ', 2
    $expected = $parts[0]
    $path = $parts[1]
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing: $path" }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $expected) { throw "Checksum mismatch: $path" }
}
if ((Get-ChildItem .\course-content\support-resistance\chart_assets\charts -Filter *.png -File).Count -ne 121) { throw 'Expected 121 PNG files' }
if ((Get-ChildItem .\course-content\support-resistance\chart_assets\charts -Filter *.svg -File).Count -ne 121) { throw 'Expected 121 SVG files' }
if ((Get-ChildItem .\course-content\support-resistance\chart_assets\data -Filter *.csv -File).Count -ne 48) { throw 'Expected 48 OHLC/source CSV files' }
if (-not (Test-Path .\course-content\support-resistance\chart_assets\source\build_chart_assets.py)) { throw 'Generator missing' }

git status --short
git add course-content/support-resistance/chart_assets/charts course-content/support-resistance/chart_assets/data course-content/support-resistance/chart_assets/source course-content/support-resistance/chart_assets/SHA256SUMS.txt
git commit -m "Add reproducible support-resistance chart assets and OHLC data"
git push origin my-new-branch
```

After pushing, verify on GitHub that the commit is the branch head and the tree contains all 242 renders, 48 data files, generator, and checksum inventory. Record the resulting commit SHA and rerun the counts against the remote tree before changing this status to complete. Keep both original ZIP archives as backups until that verification passes.

## Regeneration policy

Use the committed CSV source data and `source/build_chart_assets.py` as the reproducible inputs. Before regenerating, inspect the script's dependencies and output paths; run it in an isolated environment and compare output hashes with the committed exports. Do not overwrite committed chart renders merely because regeneration runs successfully. Update manifests and checksums only when a reviewed asset change is intentional.

## Boundaries

- No image is a substitute for a missing real instructor case. Lessons 9, 16 and 17 still require authentic user-provided records.
- Internal reference states and answer keys must not be placed in learner-facing delivery.
- Asset file presence does not mean the visuals are approved; visual review remains a second-pass item.
