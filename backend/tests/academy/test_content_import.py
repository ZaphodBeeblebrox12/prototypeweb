from apps.academy.management.commands.seed_trading_path import (
    duration_minutes,
    lesson_summary,
    split_lesson_source,
)


def test_source_split_removes_frontmatter_answers_and_chart_instructions():
    source = """---
lesson: 1
title: Example
---

# Day 1 — Example

## What you'll learn
- Read the auction
- Compare buyer and seller pressure

Lesson body that the learner should see.

📊 CHART NEEDED: `charts/example.png`
INSTRUMENT / TIMEFRAME: Nifty · 5-minute
MUST SHOW:
- A labelled candle
- A marked zone

Answers: 1 — the price is the last agreement.

"""
    body, answers, notes = split_lesson_source(source)

    assert "Lesson body that the learner should see." in body
    assert "---" not in body
    assert "# Day 1 — Example" not in body
    assert "Answers:" not in body
    assert "CHART NEEDED" not in body
    assert "the price is the last agreement" in answers
    assert "charts/example.png" in notes
    assert "INSTRUMENT / TIMEFRAME" in notes


def test_source_split_moves_collapsed_answer_keys_to_instructor_material():
    source = """# Day 8 — Quiz

Question one?

<details><summary>Answer key (don't peek)</summary>1b · 2a</details>

Graduation message for the learner.
"""
    body, answers, notes = split_lesson_source(source)

    assert "Question one?" in body
    assert "Graduation message for the learner." in body
    assert "<details>" not in body
    assert "1b · 2a" in answers
    assert not notes


def test_lesson_metadata_helpers_are_compact_and_predictable():
    assert duration_minutes("~13 min") == 13
    assert duration_minutes("unmeasured") == 10
    summary = lesson_summary("## What you'll learn\n- First concept\n- Second concept\n- Third concept\n- Fourth concept", "")
    assert summary == "First concept Second concept Third concept"
