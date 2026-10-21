"""Small policy and copy helpers for inline course preview cards."""
import re

_PLACEHOLDER_TITLES = {
    "new micro-course draft",
    "untitled course",
    "untitled micro-course",
}
_PLACEHOLDER_SUMMARIES = {
    "add a concise course promise here.",
    "a clear, practical description of what learners will study and why it matters.",
}
_ARTICLE_WORDS = {"a", "an", "and", "for", "of", "or", "the", "to", "with"}
_LEADING_VERBS = (
    "analyse", "analyze", "apply", "assess", "build", "compare", "describe",
    "develop", "distinguish", "evaluate", "explain", "identify", "learn", "read",
    "recognise", "recognize", "understand", "use",
)


def is_course_card_recommendable(title, summary):
    """Keep empty starter records out of the picker and learner-facing copy."""
    title_text = " ".join(str(title or "").casefold().split())
    summary_text = " ".join(str(summary or "").casefold().split())
    return title_text not in _PLACEHOLDER_TITLES and summary_text not in _PLACEHOLDER_SUMMARIES


def compact_course_topic(value):
    """Turn learning outcomes into short topic chips for the Option 4 card."""
    topic = str(value or "").strip().rstrip(".")
    if not topic:
        return ""
    topic = re.sub(
        r"^(?:" + "|".join(_LEADING_VERBS) + r")\s+",
        "",
        topic,
        flags=re.IGNORECASE,
    )
    topic = re.sub(r"\band identify\b", "&", topic, flags=re.IGNORECASE)
    topic = re.sub(r"\bwith price progress\b", "vs price", topic, flags=re.IGNORECASE)
    topic = re.sub(r"\bbefore interpreting it\b", "before interpretation", topic, flags=re.IGNORECASE)
    topic = re.sub(r"^a clear,\s*", "", topic, flags=re.IGNORECASE)
    topic = re.sub(r"\b(?:a|an|the)\b", "", topic, flags=re.IGNORECASE)
    topic = re.sub(r",", "", topic)
    topic = " ".join(topic.split()).strip(" ,;:")
    if len(topic) > 32:
        clipped = topic[:29].rsplit(" ", 1)[0].rstrip(" ,;:")
        topic = (clipped or topic[:29].rstrip()) + "…"
    return topic[:1].upper() + topic[1:] if topic else ""


def course_card_mark(title):
    """Create a compact text-only art mark without inventing course imagery."""
    words = [
        word for word in re.findall(r"[A-Za-z0-9]+", str(title or ""))
        if word.casefold() not in _ARTICLE_WORDS
    ]
    if len(words) >= 2:
        return f"{words[0][0].upper()}/{words[1][0].upper()}"
    if words:
        return words[0][:2].upper()
    return "TT"


def course_card_art_copy(title, category=""):
    """Return the small two-line descriptor shown in the card's art panel."""
    source = f"{title or ''} {category or ''}".casefold()
    if "volume" in source and "price" in source:
        return "Activity", "meets outcome"
    if "support" in source and "resistance" in source:
        return "Price", "respects zones"
    if "bollinger" in source or "volatility" in source:
        return "Volatility", "in context"
    if "construction" in source:
        return "Idea", "to execution"
    return "Learn", "in context"
