"""Shared eligibility and compact-copy helpers for related course cards."""
import re

_PLACEHOLDER_TITLES = {
    "new micro-course draft",
    "untitled course",
    "untitled micro-course",
}
_PLACEHOLDER_SUMMARIES = {
    "add a concise course promise here.",
    "a clear, practical description of what learners will study and why it matters.",
    "describe the learner, what the course covers and what they can practise after completing it.",
}
_ARTICLE_WORDS = {"a", "an", "and", "for", "of", "or", "the", "to", "with"}
_LEADING_VERBS = (
    "analyse", "analyze", "apply", "assess", "build", "compare", "describe",
    "develop", "distinguish", "evaluate", "explain", "identify", "learn", "read",
    "recognise", "recognize", "understand", "use",
)


def course_card_publication_issue(title, summary, description=""):
    """Return a learner-facing reason when a course still contains starter copy."""
    title_text = " ".join(str(title or "").casefold().split())
    summary_source = str(summary or "").strip()
    if not summary_source:
        summary_source = str(description or "").strip()
    summary_text = " ".join(summary_source.casefold().split())

    if not title_text:
        return "Add a course title before publishing."
    if title_text in _PLACEHOLDER_TITLES or re.fullmatch(r"untitled course\s*\d+", title_text):
        return "Replace the starter course title before publishing."
    if not summary_text:
        return "Add a learner-facing course summary before publishing."
    if summary_text in _PLACEHOLDER_SUMMARIES:
        return "Replace the starter course summary with a learner-facing promise before publishing."
    return ""


def is_course_card_recommendable(title, summary, description=""):
    """Only recommend a published course when its visible title and copy are ready."""
    return not course_card_publication_issue(title, summary, description)


def compact_course_topic(value):
    """Turn learning outcomes into the short topic chips used by Option 4."""
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


def course_topic_tags(learning_outcomes, limit=2):
    """Return distinct, compact topic chips from a course's learning outcomes."""
    if not isinstance(learning_outcomes, list) or limit <= 0:
        return []

    topics = []
    seen = set()
    for outcome in learning_outcomes:
        topic = compact_course_topic(outcome)
        key = topic.casefold()
        if topic and key not in seen:
            topics.append(topic)
            seen.add(key)
        if len(topics) >= limit:
            break
    return topics


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
    """Return the short descriptor shown in Option 4's visual side panel."""
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
