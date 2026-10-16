#!/usr/bin/env python3
"""Focused smoke checks for the Bollinger Bands preview and Volume & Price Analysis discovery."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
page = (ROOT / "course-source/understand-bollinger-bands/preview/first-pass/index.html").read_text(encoding="utf-8")
data = (ROOT / "site/assets/course-catalogue-data.js").read_text(encoding="utf-8")
renderer = (ROOT / "site/assets/courses-catalogue.js").read_text(encoding="utf-8")
catalogue = (ROOT / "site/courses.html").read_text(encoding="utf-8")
media_editor = (ROOT / "site/assets/instructional-image-admin.js").read_text(encoding="utf-8")

if len(re.findall(r'id:\s*"volume-price-analysis"', data)) != 1:
    raise SystemExit("Expected one Volume & Price Analysis record.")
start = data.index('id: "volume-price-analysis"')
end = data.index('id: "candlestick-patterns"', start)
entry = data[start:end]
for token in ('catalogueVisibility: "visible"', 'status: "in-development"', 'price: "Coming soon"',
              'title: "Volume & Price Analysis"', 'Point of Control and Value Area',
              'High- and low-volume nodes', 'relative volume', 'effort versus result'):
    if token.lower() not in entry.lower():
        raise SystemExit("Missing VPA catalogue detail: " + token)
if 'Course in development</button>' not in renderer:
    raise SystemExit("The development course must not offer enrolment.")
if 'course-catalogue-data.js' not in catalogue or 'courses-catalogue.js' not in catalogue:
    raise SystemExit("Catalogue data/renderer not linked from site/courses.html.")
if 'function isVolumeAnalysisLesson' not in page:
    raise SystemExit("Intentional related-course placement map is missing.")
placement = page[page.index("function isVolumeAnalysisLesson"):page.index("function renderRelatedVolumeCourseCard")]
for key in ("'4-2'", "'5-1'", "'5-2'", "'6-0'"):
    if key not in placement:
        raise SystemExit("Expected editorial cross-course placement missing: " + key)
if "const href='../../../../site/courses.html#micro-courses';" not in page:
    raise SystemExit("Lesson cross-link should resolve to catalogue for repository-root local review.")
if "https://zaphodbeeblebrox12.github.io/prototypeweb/courses.html#micro-courses" in page:
    raise SystemExit("The lesson preview must not hard-code the hosted catalogue origin.")
if "return 1+Math.max(0,refs.length-1);" not in page or "const figureAssetCount=lessonFigureAssetCount" not in page:
    raise SystemExit("Chart-example count not data-driven.")
if "const subLabel=total>1&&index>0?String.fromCharCode(64+index):'';" not in page:
    raise SystemExit("Figure suffix should follow Figure 5.1 / Figure 5.1A.")
for token in ('id="courseEditorToggle"', 'course-content-admin-editor.js', 'data-media-asset-id', 'data-enlarge-image'):
    if token not in page:
        raise SystemExit("Preview editing/figure interaction missing: " + token)
if "not uploaded or saved" not in media_editor:
    raise SystemExit("Local-only image replacement must be explicitly labelled.")
if 'Django login and shared saving are not connected in this preview' not in page:
    raise SystemExit("Preview must disclose that backend shared editing is not connected.")
for student_facing_label in ("eyebrow:'Method I ·", "eyebrow:'Method II ·", "eyebrow:'Method III ·", "eyebrow:'Method IV ·",
                             '"Method I: Trade the Volatility Breakout"', '"Method II: Follow Strength Confirmed by MFI"',
                             '"Method III: Look for Reversal Clues in Volume"', '"Method IV: Wait for a Confirmed Breakout"'):
    if student_facing_label in page:
        raise SystemExit("Internal method label leaks into student-facing material: " + student_facing_label)
print("Bollinger preview, VPA discovery, catalogue state, figure labels/counts and edit hooks passed.")
