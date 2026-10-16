from apps.academy.management.commands.seed_volume_price_analysis import (
    estimate_duration,
    extract_vpa_student_body,
    lesson_segments,
)


def test_volume_price_analysis_parser_keeps_narration_and_separates_checks():
    source = """# Module 1 — Read the Market Behind the Candles
## Lesson 1.1 — Reading the Volume Behind Price
### Learning objective
Describe price outcome and activity separately.
### Outline and timing
- Observe
- Compare
### Full narration script
Start by describing the candle you can see.
### Learner progression — Notice → Compare → Apply
**Notice:** Record what changed.
### Knowledge check
Q1. Is volume a stand-alone signal?
Answer: No.
## Lesson 1.2 — Spotting Unusual Volume
### Learning objective
Compare activity with a baseline.
### Full narration script
A second lesson begins.
"""
    segments = lesson_segments(source)
    assert len(segments) == 2
    body, internal = extract_vpa_student_body(segments[0][3])

    assert "Describe price outcome" in body
    assert "Start by describing the candle" in body
    assert "Record what changed." in body
    assert "Knowledge check" not in body
    assert "Answer: No." in internal
    assert "A second lesson begins" not in body


def test_vpa_import_duration_uses_first_target_minute():
    assert estimate_duration("**Target delivered duration:** 12–16 minutes") == 12
    assert estimate_duration("No duration listed.") == 15
