"""Course-level sharing copy and safe public metadata helpers."""

DEFAULT_SHARE_MESSAGE = (
    "I came across this TradeThesis course and thought it might be useful for anyone "
    "looking to develop a more structured approach to trading.\n\n"
    "Explore {course_title} and learn at your own pace.\n\n"
    "TradeThesis — Conviction before Execution."
)

# Explicit course-specific invitations. These overrides intentionally take
# precedence over legacy generic copy saved on the individual Course record.
COURSE_SHARE_MESSAGE_OVERRIDES = {
    "candlestick-patterns": (
        "Most traders see a green or red candle and stop there. This course shows "
        "you the story inside it: who is in control, who is losing ground, and "
        "what that means for your next entry."
    ),
}


def course_share_title(course):
    return str(getattr(course, "share_title", "") or "").strip() or str(course.title)


def course_share_message(course):
    title = str(course.title)
    authored = str(getattr(course, "share_message", "") or "").strip()
    override = COURSE_SHARE_MESSAGE_OVERRIDES.get(str(getattr(course, "slug", "") or ""))
    # The named course override intentionally replaces its previous generic
    # invitation even if that old copy was saved directly on the Course row.
    message = override or authored or DEFAULT_SHARE_MESSAGE
    return message.replace("{course_title}", title).strip()


def course_share_description(course):
    """Open Graph description derived from the exact share message the author approved."""
    return " ".join(course_share_message(course).split())[:300]
