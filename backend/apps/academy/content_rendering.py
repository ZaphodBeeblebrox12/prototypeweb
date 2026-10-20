"""Safe Markdown rendering and sectioning for the shared Learning Room."""
import html
import re
import uuid

import bleach
import markdown as markdown_library
from django.urls import reverse

from .models import Course, Lesson

_ALLOWED_TAGS = {
    "a", "aside", "blockquote", "br", "code", "del", "em", "figcaption", "figure",
    "h1", "h2", "h3", "h4", "h5", "hr", "img", "li", "ol", "p", "pre",
    "s", "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
}
_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "class"],
    "aside": ["class", "aria-label"],
    "img": ["src", "alt", "title", "loading", "width", "height", "tabindex", "role", "aria-label"],
    "span": ["class", "aria-label"],
    "th": ["align"], "td": ["align"],
}
_IMAGE_REF = re.compile(r"asset://([0-9a-fA-F-]{36})")
_IMAGE_MARKDOWN = re.compile(r"!\[([^\]]*)\]\(asset://([0-9a-fA-F-]{36})(?:\s+[^)]*)?\)")
_LESSON_REF = re.compile(r"\[\[(lesson|lesson-card):([0-9a-fA-F-]{36})\]\]")
_HEADING = re.compile(r"^(#{3,6})\s+(.+?)\s*$")
_DANGEROUS_MARKDOWN = re.compile(
    r"<\s*/?\s*(?:script|style|iframe|object|embed|form|input|button|svg|math)\b"
    r"|<[^>]+\bon[a-z]+\s*=|javascript\s*:|data\s*:\s*text/html",
    re.IGNORECASE,
)


def validate_markdown_source(value):
    """Reject active markup while allowing normal Markdown and escaped examples."""
    value = (value or "").replace("\x00", "")
    if _DANGEROUS_MARKDOWN.search(value):
        from django.core.exceptions import ValidationError
        raise ValidationError("Active HTML, event handlers and executable URLs are not allowed in lesson content.")
    return value


def _resolve_asset_refs(source, asset_urls):
    def image_replacement(match):
        alt, asset_id = match.group(1), match.group(2)
        url = asset_urls.get(asset_id)
        if not url:
            return "**Image awaiting upload: " + html.escape(alt or "course figure") + "**"
        return "![" + alt.replace("]", "") + "](" + url + ")"
    source = _IMAGE_MARKDOWN.sub(image_replacement, source or "")
    return _IMAGE_REF.sub(lambda match: asset_urls.get(match.group(1), ""), source)


def _resolve_lesson_references(source, user=None, admin_preview=False):
    """Resolve stable lesson IDs at render time without copying destination content."""
    valid_ids = set()
    for _kind, raw_id in _LESSON_REF.findall(source or ""):
        try:
            valid_ids.add(str(uuid.UUID(raw_id)))
        except (TypeError, ValueError, AttributeError):
            continue
    lessons = {}
    if valid_ids:
        lessons = {
            str(lesson.pk): lesson
            for lesson in Lesson.objects.filter(
                pk__in=valid_ids,
                is_published=True,
                module__is_published=True,
                module__course__status=Course.Status.PUBLISHED,
            ).select_related("module__course", "module")
        }

    replacements = {}

    def replace_reference(match):
        kind, raw_id = match.groups()
        try:
            stable_id = str(uuid.UUID(raw_id))
        except (TypeError, ValueError, AttributeError):
            stable_id = ""
        lesson = lessons.get(stable_id)
        if lesson is None:
            markup = (
                '<aside class="tt-inline-lesson-card" aria-label="Related lesson unavailable">'
                "<p><strong>Related lesson</strong></p>"
                "<p>This lesson reference is currently unavailable.</p></aside>"
                if kind == "lesson-card"
                else '<span class="tt-lesson-reference-unavailable">Related lesson unavailable.</span>'
            )
        else:
            course = lesson.module.course
            can_open_lesson = bool(admin_preview)
            if not can_open_lesson and getattr(user, "is_authenticated", False):
                # The same gate used by lesson_detail protects contextual links.
                from .services import can_access_lesson
                can_open_lesson = can_access_lesson(user, lesson)
            destination_url = (
                reverse("academy:lesson", args=[course.slug, lesson.pk])
                if can_open_lesson
                else reverse("academy:course-detail", args=[course.slug])
            )
            safe_url = html.escape(destination_url, quote=True)
            safe_title = html.escape(lesson.title)
            safe_course = html.escape(course.title)
            if kind == "lesson-card":
                detail = html.escape(lesson.summary) if can_open_lesson and lesson.summary else ""
                access_note = "" if can_open_lesson else "<p>View the course overview to check access.</p>"
                summary = f"<p>{detail}</p>" if detail else ""
                markup = (
                    '<aside class="tt-inline-lesson-card" aria-label="Related lesson">'
                    '<p><strong>RELATED LESSON</strong></p>'
                    f'<p><a class="tt-inline-lesson-link" href="{safe_url}" rel="noopener noreferrer">'
                    f"<strong>{safe_title}</strong></a></p>"
                    f"<p>{safe_course}</p>{summary}{access_note}</aside>"
                )
            else:
                markup = (
                    f'<a class="tt-inline-lesson-link" href="{safe_url}" rel="noopener noreferrer">'
                    f"{safe_title}</a>"
                )
        token = f"TTLESSONREF{len(replacements)}TOKEN"
        replacements[token] = markup
        return token

    return _LESSON_REF.sub(replace_reference, source or ""), replacements


def render_safe_markdown(source, asset_urls=None, user=None, admin_preview=False):
    """Render sanitised Markdown, resolving stable lesson links using live Academy records."""
    source = validate_markdown_source(source or "")
    source, lesson_references = _resolve_lesson_references(
        source, user=user, admin_preview=admin_preview,
    )
    resolved = _resolve_asset_refs(source, asset_urls or {})
    rendered = markdown_library.markdown(
        resolved,
        extensions=["tables", "sane_lists", "smarty"],
        output_format="html",
    )
    # Course Builder stores a figure caption as the paragraph immediately after its image.
    # Group that pair semantically so captions remain attached and accessible in the Learning Room.
    rendered = re.sub(r"<img\b", '<img tabindex="0" role="button" aria-label="Enlarge course figure"', rendered)
    rendered = re.sub(
        r"<p>(<img\b[^>]*>)</p>\s*<p>(.*?)</p>",
        r"<figure>\1<figcaption>\2</figcaption></figure>",
        rendered,
        flags=re.DOTALL,
    )
    for token, markup in lesson_references.items():
        rendered = rendered.replace(f"<p>{token}</p>", markup)
        rendered = rendered.replace(token, markup)
    return bleach.clean(
        rendered,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols=["http", "https", "mailto"],
        strip=True,
    )


def build_lesson_sections(source, asset_urls=None, user=None, admin_preview=False):
    """Group source headings into the three reusable Learning Room tabs."""
    lines = (source or "").splitlines()
    groups = {"idea": [], "examples": [], "practice": []}
    current_group = "idea"
    current_heading = None
    current_lines = []

    def finish_section():
        nonlocal current_lines, current_heading, current_group
        if not current_lines and not current_heading:
            return
        text = "\n".join(current_lines).strip()
        if current_heading:
            text = "### " + current_heading + "\n\n" + text
        groups[current_group].append(text)
        current_lines = []
        current_heading = None

    for line in lines:
        match = _HEADING.match(line)
        if match:
            finish_section()
            current_heading = match.group(2)
            heading = current_heading.casefold()
            # Admin-added headings encode the selected Learning Room tab;
            # handle those exact prefixes before generic content heuristics.
            if heading.startswith("additional concept figure"):
                current_group = "idea"
            elif heading.startswith("additional chart examples"):
                current_group = "examples"
            elif heading.startswith("practice figure") or any(word in heading for word in (
                "practice", "task", "try a new", "test your", "model response",
                "model reasoning", "feedback", "knowledge check", "apply",
            )):
                current_group = "practice"
            elif any(word in heading for word in (
                "worked", "compare", "comparison", "chart example", "look closely",
                "case study", "case a", "case b", "figure",
            )):
                current_group = "examples"
            else:
                current_group = "idea"
            continue
        current_lines.append(line)
    finish_section()

    # Preserve any lesson that has not yet adopted section headings.
    if not any(groups.values()):
        groups["idea"] = [source or "Lesson content is being prepared."]

    rendered = {key: "\n\n".join(part for part in parts if part.strip()) for key, parts in groups.items()}
    if not rendered["idea"].strip():
        rendered["idea"] = source or "Lesson content is being prepared."
    if not rendered["examples"].strip():
        rendered["examples"] = (
            "No separately labelled chart comparison is included in this lesson yet. "
            "Read the explanation first, then look for the evidence that would distinguish its alternative outcomes."
        )
    if not rendered["practice"].strip():
        rendered["practice"] = (
            "Describe one observable fact, one possible interpretation, and the next piece of evidence "
            "that would strengthen or weaken your reading."
        )

    figure_count = len(re.findall(r"!\[[^\]]*\]\(", source or ""))
    return {
        "idea_html": render_safe_markdown(
            rendered["idea"], asset_urls, user=user, admin_preview=admin_preview,
        ),
        "examples_html": render_safe_markdown(
            rendered["examples"], asset_urls, user=user, admin_preview=admin_preview,
        ),
        "practice_html": render_safe_markdown(
            rendered["practice"], asset_urls, user=user, admin_preview=admin_preview,
        ),
        "figure_count": figure_count,
    }
