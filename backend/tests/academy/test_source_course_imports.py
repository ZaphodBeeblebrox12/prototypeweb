from apps.academy.management.commands.seed_support_resistance import (
    estimate_duration,
    extract_snr_student_body,
    lesson_segments,
)


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
    assert "Correct: No." not in body
    assert "Correct: No." in answers
    assert "Keep the answer private." not in body


def test_duration_uses_the_lower_bound_and_falls_back_safely():
    assert estimate_duration("**Estimated duration:** 25–30 minutes") == 25
    assert estimate_duration("No declared time.") == 15
