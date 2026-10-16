from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError

from apps.academy.management.commands.seed_support_resistance import (
    embed_snr_figures,
    estimate_duration,
    extract_snr_student_body,
    lesson_segments,
)
from apps.academy.management.commands.seed_trading_path import (
    embed_existing_figures,
    split_lesson_source,
)
from apps.academy.models import Course


def test_lesson_segments_separate_bundled_canonical_scripts():
    source = """# LESSON 02 — First
## Body
First lesson.

# LESSON 03 — Second
## Body
Second lesson.
"""
    segments = lesson_segments(source)

    assert "First lesson." in segments[2]
    assert "Second lesson." in segments[3]
    assert "Second lesson." not in segments[2]


def test_foundational_lesson_import_uses_only_marked_student_script():
    source = """## Lesson 01 Production Script — Example
## 1. Instructional decision
Do not import this production note.
## 3. Student-facing lesson script and reveal timing
# Student lesson
Describe what you see.
### Knowledge check
Q1. What did price do?
Correct: It moved up.
## 4. Chart asset specifications
CHART NEEDED: internal/path.png
"""
    body, answers = extract_snr_student_body(1, source)

    assert "Describe what you see." in body
    assert "Q1. What did price do?" in body
    assert "Correct: It moved up." not in body
    assert "It moved up." in answers
    assert "Do not import this production note." not in body
    assert "CHART NEEDED" not in body


def test_later_lesson_import_keeps_teaching_but_separates_model_answers():
    source = """# Lesson 13 — Retests
## Lesson purpose
Internal outline only.
## Learning outcomes
Identify the zone and describe evidence.
## Student-facing opening
Observe first, then interpret.
## Chart sequence and reveal instructions
Do not show future candles before submission.
## Core teaching script
A retest is not a guaranteed event.
## Guided practice
Choose a defensible interpretation.
**Acceptable response example:**
> Price returns to the zone and may hold or fail.
## Knowledge check
Q1. Does every breakout retest?
Correct: No.
## Instructor notes
Keep the answer private.
"""
    body, answers = extract_snr_student_body(13, source)

    assert "Identify the zone and describe evidence." in body
    assert "Observe first, then interpret." in body
    assert "A retest is not a guaranteed event." in body
    assert "Choose a defensible interpretation." in body
    assert "Do not show future candles" not in body
    assert "Price returns to the zone" not in body
    assert "Price returns to the zone" in answers
    assert "Q1. Does every breakout retest?" in body
    assert "Correct: No." not in body
    assert "Correct: No." in answers
    assert "Keep the answer private." not in body


def test_duration_uses_the_lower_bound_and_falls_back_safely():
    assert estimate_duration("**Estimated duration:** 25–30 minutes") == 25
    assert estimate_duration("No declared time.") == 15


def test_trading_path_embeds_only_available_charts_as_numbered_figures(tmp_path):
    generated = tmp_path / "generated"
    static = tmp_path / "static"
    generated.mkdir()
    static.mkdir()
    available = ("L1-03-candle-anatomy.png", "L1-03-volume-spike.png")
    for filename in available:
        (generated / filename).write_bytes(b"test-image")
        (static / filename).write_bytes(b"test-image")

    tick = chr(96)
    source = "\n".join([
        "# Day 3 — Reading Charts",
        "",
        "Read the candle.",
        "",
        "✅ Diagram already made: " + tick + "charts/generated/L1-03-candle-anatomy.png" + tick,
        "",
        "Look at volume.",
        "",
        "📊 CHART NEEDED: " + tick + "charts/L1-03-volume-spike.png" + tick,
        "MUST SHOW:",
        "  - a volume spike",
        "",
        "📊 CHART NEEDED: " + tick + "charts/generated/L1-03-not-available.png" + tick,
        "MUST SHOW:",
        "  - an unavailable image",
    ])
    counters = {}
    embedded, embedded_notes = embed_existing_figures(
        source, generated, static, 1, counters
    )
    body, _answers, remaining_notes = split_lesson_source(embedded)

    assert "![Figure 1.1 — Candle anatomy](/static/academy/course-images/L1-03-candle-anatomy.png)" in body
    assert "*Figure 1.2 — Volume spike.*" in body
    assert "Diagram already made:" not in body
    assert "CHART NEEDED:" not in body
    assert "Figure 1.1" in embedded_notes
    assert "MUST SHOW:" in embedded_notes
    assert "L1-03-not-available.png" in remaining_notes
    assert counters == {1: 2}


def test_support_resistance_importer_embeds_only_curated_first_view_figures(tmp_path):
    static_root = tmp_path / "support-resistance"
    static_root.mkdir()
    for filename in (
        "L01-A-01-clean.svg",
        "L02-A-01-clean.svg",
        "L08-A-01-many-crossings.svg",
        "L08-A-02-fewer-interpretable.svg",
        "L15-A-01-clean.svg",
    ):
        (static_root / filename).write_text("<svg/>", encoding="utf-8")

    opening = "## 3. Student-facing lesson script and reveal timing\n\nObserve before interpreting."
    lesson_1, notes_1 = embed_snr_figures(1, 1, opening, static_root)
    assert "![Figure 1.1 — Price revisits a similar lower area in this illustrative sequence; no support boundary is drawn.](/static/academy/support-resistance/L01-A-01-clean.svg)" in lesson_1
    assert "*Repeated lower reactions around a broad area (illustrative chart).*" in lesson_1
    assert "does not implement a response-gated" in notes_1

    lesson_2_body = "## 3. Lesson script and reveal timing\n\nRead structure before drawing."
    lesson_2, notes_2 = embed_snr_figures(2, 1, lesson_2_body, static_root)
    assert "/static/academy/support-resistance/L02-A-01-clean.svg" in lesson_2
    assert "Figure 1.2" in lesson_2
    assert "Figure 1.2 uses curated static asset" in notes_2

    lesson_8, notes_8 = embed_snr_figures(8, 3, opening, static_root)
    assert "/static/academy/support-resistance/L08-A-01-many-crossings.svg" in lesson_8
    assert "/static/academy/support-resistance/L08-A-02-fewer-interpretable.svg" in lesson_8
    assert "Figure 3.3" in lesson_8 and "Figure 3.4" in lesson_8
    assert "INTERNAL" not in lesson_8
    assert notes_8.count("Figure 3.") == 2

    lesson_15 = "## Student-facing opening\n\nThink in conditional scenarios."
    lesson_15, notes_15 = embed_snr_figures(15, 6, lesson_15, static_root)
    assert "Figure 6.1" in lesson_15
    assert "L15-A-01-clean.svg" in notes_15

    for lesson_number, module_position in ((9, 4), (16, 6), (17, 6), (18, 6)):
        body = "## Student-facing opening\n\nCase material remains pending."
        unchanged, notes = embed_snr_figures(lesson_number, module_position, body, static_root)
        assert unchanged == body
        assert notes == ""


@mock.patch("apps.academy.management.commands.seed_academy_catalogue.call_command")
def test_catalogue_preflight_validates_all_courses_without_writing(mock_call_command):
    output = StringIO()

    call_command("seed_academy_catalogue", stdout=output)

    assert [call.args[0] for call in mock_call_command.call_args_list] == [
        "seed_trading_path",
        "seed_support_resistance",
        "seed_volume_price_analysis",
    ]
    assert all("apply" not in call.kwargs for call in mock_call_command.call_args_list)
    assert "Validated 3 canonical course sources: 16 modules and 78 lessons." in output.getvalue()
    assert Course.objects.count() == 0


@mock.patch("apps.academy.management.commands.seed_academy_catalogue.call_command")
def test_catalogue_apply_refuses_existing_course_before_any_import(mock_call_command):
    Course.objects.create(title="Existing S&R", slug="support-resistance")
    output = StringIO()

    try:
        call_command("seed_academy_catalogue", apply=True, stdout=output)
    except CommandError as exc:
        assert "Catalogue import is create-only" in str(exc)
        assert "support-resistance" in str(exc)
    else:
        raise AssertionError("Expected an existing catalogue slug to block import.")

    mock_call_command.assert_not_called()

