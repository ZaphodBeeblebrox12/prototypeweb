"""Normalize editable marketing fields for the public micro-course catalogue."""

from __future__ import annotations

import re


def _text(value, limit):
    return " ".join(str(value or "").split())[:limit]


def normalize_catalogue_presentation(value):
    value = value if isinstance(value, dict) else {}
    raw_tags = value.get("tags", [])
    if isinstance(raw_tags, str):
        candidates = re.split(r"[,;\n]+", raw_tags)
    elif isinstance(raw_tags, list):
        candidates = raw_tags
    else:
        candidates = []
    tags, seen = [], set()
    for item in candidates:
        tag = _text(item, 40)
        key = tag.casefold()
        if tag and key not in seen:
            tags.append(tag)
            seen.add(key)
        if len(tags) >= 10:
            break
    return {
        "hook": _text(value.get("hook"), 200),
        "problem": _text(value.get("problem"), 500),
        "learning_focus": _text(value.get("learning_focus", value.get("learningFocus")), 500),
        "tags": tags,
        "why_this_one": _text(value.get("why_this_one", value.get("whyThisOne")), 500),
    }


def _has_copy(value):
    value = normalize_catalogue_presentation(value)
    return bool(
        value["hook"]
        or value["problem"]
        or value["learning_focus"]
        or value["tags"]
        or value["why_this_one"]
    )


def catalogue_presentation_from_builder_state(state):
    state = state if isinstance(state, dict) else {}
    raw = {
        "hook": state.get("catalogueHook", ""),
        "problem": state.get("problemStatement", ""),
        "learning_focus": state.get("learningFocus", ""),
        "tags": state.get("authoredTags", []),
        "why_this_one": state.get("whyThisOne", ""),
    }
    value = normalize_catalogue_presentation(raw)
    return value, bool(state.get("cataloguePresentationConfigured", False) or _has_copy(value))


def catalogue_presentation_from_payload(payload):
    payload = payload if isinstance(payload, dict) else {}
    course = payload.get("course") if isinstance(payload.get("course"), dict) else {}
    if isinstance(course.get("catalogue_presentation"), dict):
        value = normalize_catalogue_presentation(course["catalogue_presentation"])
        configured = course.get("catalogue_presentation_configured")
        if configured is not None:
            return value, bool(configured)
        if _has_copy(value):
            return value, True
    state = payload.get("builder_state") if isinstance(payload.get("builder_state"), dict) else {}
    return catalogue_presentation_from_builder_state(state)


def builder_fields_for_catalogue_presentation(value, configured=None):
    value = normalize_catalogue_presentation(value)
    if configured is None:
        configured = _has_copy(value)
    return {
        "catalogueHook": value["hook"],
        "problemStatement": value["problem"],
        "learningFocus": value["learning_focus"],
        "authoredTags": ", ".join(value["tags"]),
        "whyThisOne": value["why_this_one"],
        "cataloguePresentationConfigured": bool(configured),
    }


def catalogue_presentation_api_fields(value, configured):
    value = normalize_catalogue_presentation(value)
    return {
        "hook": value["hook"],
        "problem": value["problem"],
        "learningFocus": value["learning_focus"],
        "tags": value["tags"],
        "whyThisOne": value["why_this_one"],
        "cataloguePresentationConfigured": bool(configured),
    }


def default_presentation_for_course(slug):
    """Seed the approved copy on the existing Support & Resistance course only."""
    if slug != "support-resistance":
        return None
    return normalize_catalogue_presentation(
        {
            "hook": "Mark fewer zones. Give each one a reason.",
            "problem": "For traders who see a possible level around every swing and need a reason to keep or discard it.",
            "learning_focus": "Choose and defend relevant zones, read reactions and breaks, and identify invalidation.",
            "tags": [],
            "why_this_one": "Treats zones as decision areas to justify, test and invalidate—not lines to collect.",
        }
    )
