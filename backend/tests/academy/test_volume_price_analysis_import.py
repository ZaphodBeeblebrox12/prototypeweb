from apps.academy.management.commands.seed_volume_price_analysis import (
    embed_vpa_figures,
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
    assert "Knowledge check" in body
    assert "Is volume a stand-alone signal?" in body
    assert "Answer: No." not in body
    assert "Answer: No." in internal
    assert "A second lesson begins" not in body


def test_vpa_import_duration_uses_first_target_minute():
    assert estimate_duration("**Target delivered duration:** 12–16 minutes") == 12
    assert estimate_duration("No duration listed.") == 15


def test_vpa_pilot_figures_are_numbered_and_keep_later_outcomes_out(tmp_path):
    asset_root = tmp_path / "exports"
    asset_root.mkdir()
    for filename in (
        "vpa-m01-l01-stage1-spot-volume-mobile.svg",
        "vpa-m01-l01-candle-context-compare-mobile.svg",
    ):
        (asset_root / filename).write_text("<svg/>", encoding="utf-8")

    source = """**Level 1 — Notice (easy):** Identify the candidate candle.

**Level 2 — Compare (guided):** Compare the similar candles.

**Level 3 — Apply (independent):** Explain the next evidence to watch.

**Reveal rule:** Keep later outcomes hidden until the learner responds.
"""
    counters = {}
    body, media_notes = embed_vpa_figures("1.1", source, asset_root, counters)

    assert "![Figure 1.1 — Candidate candle and its local volume baseline](/static/academy/vpa/vpa-m01-l01-stage1-spot-volume-mobile.svg)" in body
    assert "![Figure 1.2 — Similar candle shapes in different contexts](/static/academy/vpa/vpa-m01-l01-candle-context-compare-mobile.svg)" in body
    assert "*Similar candle shapes in different contexts.*" in body
    assert body.index("Figure 1.1") < body.index("Level 2") < body.index("Figure 1.2") < body.index("Level 3")
    assert "stage3-outcome" not in body
    assert "learner-response-gated reveal" in media_notes
    assert counters == {1: 2}
