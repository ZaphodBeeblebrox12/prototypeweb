# Binary Asset Transfer Status

**Status:** Source manifests committed; rendered charts and underlying data still need a binary-capable/local Git upload.

The verified production ZIP `tradethesis_sr_course_production_pack_v1_8.zip` includes:
- 121 PNG chart renders.
- 121 SVG chart renders.
- 48 CSV OHLC/source datasets.
- `chart_assets/source/build_chart_assets.py` (chart build source).
- asset and dataset manifests, source scripts, course documentation and production trackers.

The current GitHub integration exposes Git blob creation for text but no operation to upload arbitrary local binary files or attach a release asset. The repository therefore contains the text-based source and manifests, but not all chart binaries, datasets or the generator script as individual files yet. This is a known transfer gap, not a missing-artifact claim.

## Completion procedure

1. Clone `https://github.com/ZaphodBeeblebrox12/prototypeweb.git` locally and check out `my-new-branch`.
2. Extract the chart assets from the v1.8 production ZIP (keep `charts/`, `data/`, `source/` and their original names) into `course-content/support-resistance/chart_assets/`.
3. Verify that the extracted manifest paths resolve, that the expected counts are 121 PNG, 121 SVG and 48 CSV, and that the Python source exists.
4. Run the chart builder in a controlled environment only if its dependencies and output behaviour are understood; compare generated files to the archive before overwriting anything.
5. Commit the assets with a message such as `Add reproducible support-resistance chart assets and OHLC data`.
6. Verify the commit tree and record SHA-256 checksums for the archive and the asset set.
7. Keep the production ZIP as backup until the repo copy is verified.

Do not put the complete ZIP inside the repo as a substitute for extracted assets. Do not mark this status complete until the counts and paths are verified.
