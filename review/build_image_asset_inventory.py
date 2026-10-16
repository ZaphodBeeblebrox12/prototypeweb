#!/usr/bin/env python3
"""Generate a repository-tracked image inventory with intrinsic image dimensions.

Designed to run in a GitHub Actions checkout so PNG headers and SVG root metadata
can be inspected without downloading binary assets through the GitHub connector.
"""
from __future__ import annotations

import argparse
import csv
import re
import struct
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = {".png", ".svg"}
TEXT_EXTENSIONS = {
    ".html", ".htm", ".js", ".mjs", ".css", ".md", ".json", ".yml",
    ".yaml", ".txt", ".csv"
}
SVG_TAG_RE = re.compile(r"<svg\b([^>]*)>", re.IGNORECASE | re.DOTALL)
SVG_ATTR_RE = re.compile(r"""(?<![\w-])([A-Za-z_:][\w:.-]*)\s*=\s*["']([^"']*)["']""")
MENTION_RE = re.compile(r"(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+\.(?:png|svg))(?![A-Za-z0-9_.-])", re.IGNORECASE)


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / name.decode("utf-8") for name in output.split(b"\0") if name]


def tidy_number(value: float) -> str:
    rounded = round(value)
    return str(rounded) if abs(value - rounded) < 0.01 else f"{value:.2f}".rstrip("0").rstrip(".")


def read_png_size(path: Path) -> tuple[str, str]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return "", "PNG header could not be parsed"
    width, height = struct.unpack(">II", header[16:24])
    if not width or not height:
        return "", "PNG dimensions are zero"
    return f"{width} × {height} px", "PNG IHDR dimensions"


def css_px(value: str) -> float | None:
    match = re.fullmatch(r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(px|pt|pc|in|cm|mm|q)?\s*", value, re.I)
    if not match:
        return None
    number = float(match.group(1))
    unit = (match.group(2) or "px").lower()
    factor = {
        "px": 1.0, "pt": 96 / 72, "pc": 16.0, "in": 96.0,
        "cm": 96 / 2.54, "mm": 96 / 25.4, "q": 96 / 101.6
    }[unit]
    return number * factor


def read_svg_size(path: Path) -> tuple[str, str]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            head = stream.read(32768)
    except OSError as exc:
        return "", f"SVG could not be read: {exc}"
    root = SVG_TAG_RE.search(head)
    if not root:
        return "", "SVG root element not found"
    attrs = {key.lower(): value for key, value in SVG_ATTR_RE.findall(root.group(1))}
    width_raw, height_raw = attrs.get("width", ""), attrs.get("height", "")
    viewbox_raw = attrs.get("viewbox", "")
    dims: list[str] = []
    width_px, height_px = css_px(width_raw), css_px(height_raw)
    if width_px is not None and height_px is not None:
        dims.append(f"viewport ≈ {tidy_number(width_px)} × {tidy_number(height_px)} CSS px")
    elif width_raw or height_raw:
        dims.append(f"viewport {width_raw or 'auto'} × {height_raw or 'auto'}")
    viewbox = re.split(r"[\s,]+", viewbox_raw.strip()) if viewbox_raw else []
    if len(viewbox) == 4:
        try:
            dims.append("viewBox " + " × ".join(tidy_number(float(v)) for v in viewbox[2:]))
        except ValueError:
            dims.append("viewBox " + viewbox_raw)
    return "; ".join(dims), "SVG root metadata"


def group_and_action(path: str) -> tuple[str, str]:
    if path.startswith(("brand-assets/", "site/assets/tradethesis-")):
        return "Brand identity", "Decorative branding; intentionally excluded from image viewer"
    if path.startswith("review/screenshots/"):
        return "QA/reference screenshot", "Not an instructional web image"
    if path.startswith("course-content/support-resistance/chart_assets/charts/"):
        return "Support & Resistance chart source", "Teaching chart; inspect at normal/mobile size; prefer paired SVG when readable"
    if path.startswith("site/assets/support-resistance-charts/"):
        return "Learning Room chart (generated at deployment/test time)", "Stage chart; prefer paired SVG with PNG fallback"
    if path.startswith("site/assets/breakout-failure-figures/"):
        return "Learning Room teaching figure", "PNG-only published figure; assess for larger labels or focused detail view"
    if path.startswith("site/module5-v5_2/assets/figures/"):
        if path.endswith("FIG00_boundary_episode_overview.png"):
            return "V5.2 overview/reference figure", "Not referenced by active lesson renderers; do not expose automatically"
        return "V5.2 Lessons 12–14 teaching figure", "PNG-only published schematic; inspect label size and likely detail-view needs"
    if path.startswith("site/module5-v5_2/charts/"):
        return "V5.2 staged-chart mirror", "Verify direct usage; page routes into the shared Learning Room"
    if "production/previews/" in path:
        return "Production/preview source asset", "Source/preview asset; not assumed live without a matching reference"
    if path.startswith("course-source/starter-drip-course/charts/"):
        return "Self-paced course chart illustration", "Verify its displayed dimensions in the ebook/course delivery"
    if path.startswith("course-source/volume-price-analysis/assets/"):
        return "Volume/price-analysis instructional vector", "Vector source/export; typography still needs rendered/mobile review"
    if path.startswith("prototypes/"):
        return "Prototype instructional visual", "Prototype; not assumed to be live"
    return "Other repository image asset", "Confirm use and inspect if learner-facing"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="review/IMAGE_ASSET_INVENTORY.generated.csv")
    args = parser.parse_args()
    files = tracked_files()
    images = sorted(
        (p for p in files if p.suffix.lower() in IMAGE_EXTENSIONS and p.is_file()),
        key=lambda p: p.relative_to(ROOT).as_posix().lower()
    )
    basenames = defaultdict(list)
    for path in images:
        basenames[path.name.lower()].append(path)
    references: dict[str, set[str]] = defaultdict(set)

    excluded_text = {
        "review/image_asset_inventory.csv",
        "review/image_asset_inventory.generated.csv",
        "review/build_image_asset_inventory.py",
        "course-content/support-resistance/chart_assets/sha256sums.txt",
        "course-content/support-resistance/chart_assets/asset_manifest.csv",
        "course-content/support-resistance/chart_assets/asset_audit.md",
    }
    for source in files:
        rel = source.relative_to(ROOT).as_posix()
        if source.suffix.lower() not in TEXT_EXTENSIONS or rel.lower() in excluded_text:
            continue
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in MENTION_RE.finditer(text):
            filename = match.group(1).lower()
            if filename not in basenames:
                continue
            # Store the reference against every same-named variant, as code can
            # choose a PNG then map to the adjacent SVG at run time.
            for target in basenames[filename]:
                references[target.relative_to(ROOT).as_posix()].add(rel)

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "path", "format", "file_size_bytes", "native_dimensions",
        "dimension_source", "paired_png_svg_variant",
        "reference_file_count", "referenced_by", "asset_group",
        "first_pass_readability_action"
    ]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for path in images:
            rel = path.relative_to(ROOT).as_posix()
            if path.suffix.lower() == ".png":
                dimensions, dimension_source = read_png_size(path)
                pair = path.with_suffix(".svg")
                paired = "yes" if pair.is_file() else "no"
            else:
                dimensions, dimension_source = read_svg_size(path)
                pair = path.with_suffix(".png")
                paired = "yes" if pair.is_file() else "no"
            group, action = group_and_action(rel)
            refs = sorted(references.get(rel, set()))
            writer.writerow({
                "path": rel,
                "format": path.suffix[1:].upper(),
                "file_size_bytes": path.stat().st_size,
                "native_dimensions": dimensions,
                "dimension_source": dimension_source,
                "paired_png_svg_variant": paired,
                "reference_file_count": len(refs),
                "referenced_by": "; ".join(refs),
                "asset_group": group,
                "first_pass_readability_action": action,
            })
    print(f"Generated {len(images)} image records with native dimensions: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
