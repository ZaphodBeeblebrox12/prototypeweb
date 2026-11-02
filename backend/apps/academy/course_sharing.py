"""Course-level sharing copy and safe public metadata helpers."""

DEFAULT_SHARE_MESSAGE = (
    "I came across this TradeThesis course and thought it might be useful for anyone "
    "looking to develop a more structured approach to trading.\n\n"
    "Explore {course_title} and learn at your own pace.\n\n"
    "TradeThesis — Conviction before Execution."
)


def course_share_title(course):
    return str(getattr(course, "share_title", "") or "").strip() or str(course.title)


def course_share_message(course):
    title = str(course.title)
    authored = str(getattr(course, "share_message", "") or "").strip()
    return (authored or DEFAULT_SHARE_MESSAGE).replace("{course_title}", title).strip()


def course_share_description(course):
    """Open Graph description derived from the exact share message the author approved."""
    return " ".join(course_share_message(course).split())[:300]
