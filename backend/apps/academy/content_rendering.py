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
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "img", "li", "ol", "p", "pre",
    "s", "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
}
_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "class"],
    "aside": ["class", "aria-label"],
    "figure": ["class", "data-figure-id"],
    "figcaption": ["class"],
    "img": ["src", "alt", "title", "loading", "width", "height", "tabindex", "role", "aria-label"],
    "span": ["class", "aria-label"],
    "th": ["align"], "td": ["align"],
}
_IMAGE_REF = re.compile(r"asset://([0-9a-fA-F-]{36})")
_IMAGE_MARKDOWN = re.compile(r"!\[([^\]]*)\]\(asset://([0-9a-fA-F-]{36})(?:\s+[^)]*)?\)")
_TEACHING_FIGURE_TOKEN = re.compile(r"\[\[teaching-figure:([A-Za-z0-9_-]{1,120})\]\]")
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


def render_safe_markdown(
    source,
    asset_urls=None,
    user=None,
    admin_preview=False,
    figure_metadata=None,
    figure_prefix=None,
):
    """Render sanitised Markdown and structured inline figures using stable asset IDs."""
    from html import escape

    source = validate_markdown_source(source or "")
    source, lesson_references = _resolve_lesson_references(
        source, user=user, admin_preview=admin_preview,
    )
    asset_urls = asset_urls or {}
    figure_metadata = figure_metadata if isinstance(figure_metadata, dict) else {}
    figure_frames = {}

    def replace_structured_figure(match):
        alt_from_markdown, asset_id = match.groups()
        metadata = figure_metadata.get(asset_id)
        if not isinstance(metadata, dict):
            return match.group(0)

        alt = str(metadata.get("alt") or alt_from_markdown or metadata.get("title") or "Course figure").strip()
        title = str(metadata.get("title") or metadata.get("caption") or alt or "Course figure").strip()
        caption = str(metadata.get("caption") or "").strip()
        if figure_prefix and not title.casefold().startswith("figure "):
            title = f"Figure {figure_prefix} · {title}"

        safe_title = escape(title)
        safe_alt = escape(alt, quote=True)
        safe_asset_id = escape(asset_id, quote=True)
        safe_caption = escape(caption)
        image_url = asset_urls.get(asset_id, "")
        if image_url:
            safe_url = escape(str(image_url), quote=True)
            body = (
                f'<span class="tt-purpose-figure-image"><img src="{safe_url}" alt="{safe_alt}" '
                'loading="lazy" decoding="async" tabindex="0" role="button" '
                'aria-label="Enlarge course figure"></span>'
            )
        else:
            body = (
                '<span class="tt-purpose-figure-missing" role="status">'
                '<strong>Figure awaiting upload</strong>'
                '<span>The image for this figure is not available in this preview.</span>'
                '</span>'
            )
        caption_markup = f'<figcaption><p>{safe_caption}</p></figcaption>' if safe_caption else ""
        markup = (
            f'<figure class="tt-purpose-figure" data-figure-id="{safe_asset_id}">'
            f'<span class="tt-purpose-figure-head"><strong>{safe_title}</strong>'
            '<span>Purpose-built teaching aid</span></span>'
            f'<span class="tt-purpose-figure-body">{body}</span>{caption_markup}</figure>'
        )
        token = f"TTSTRUCTUREDFIGURE{len(figure_frames)}END"
        figure_frames[token] = markup
        return token

    # Replace only Markdown image references that have saved figure metadata. The placeholder
    # preserves the exact text/image/text position and prevents Markdown from stripping the frame.
    source = _IMAGE_MARKDOWN.sub(replace_structured_figure, source)

    def replace_teaching_figure(match):
        figure_id = match.group(1)
        metadata = figure_metadata.get(figure_id)
        if not isinstance(metadata, dict) or metadata.get("type") != "comparison-cards":
            return match.group(0)

        title = str(metadata.get("title") or "Comparison").strip()
        if figure_prefix and not title.casefold().startswith("figure "):
            title = f"Figure {figure_prefix} · {title}"
        safe_title = escape(title)
        safe_id = escape(figure_id, quote=True)
        cards = metadata.get("cards", [])
        if not isinstance(cards, list):
            cards = []
        card_markup = []
        for card in cards[:4]:
            if not isinstance(card, dict):
                continue
            kicker = escape(str(card.get("kicker") or "").strip())
            card_title = escape(str(card.get("title") or "").strip())
            body = escape(str(card.get("body") or "").strip())
            if not (kicker or card_title or body):
                continue
            card_markup.append(
                '<span class="tt-comparison-card">'
                f'<span class="tt-comparison-kicker">{kicker}</span>'
                f'<strong>{card_title}</strong>'
                f'<span class="tt-comparison-copy">{body}</span>'
                '</span>'
            )
        note = escape(str(metadata.get("note") or "").strip())
        note_markup = f'<span class="tt-purpose-figure-note">{note}</span>' if note else ""
        markup = (
            f'<figure class="tt-purpose-figure tt-comparison-figure" data-figure-id="{safe_id}">'
            f'<span class="tt-purpose-figure-head"><strong>{safe_title}</strong>'
            '<span>Purpose-built teaching aid</span></span>'
            '<span class="tt-purpose-figure-body">'
            f'<span class="tt-comparison-cards">{"".join(card_markup)}</span>'
            f'{note_markup}</span></figure>'
        )
        token = f"TTSTRUCTUREDFIGURE{len(figure_frames)}END"
        figure_frames[token] = markup
        return token

    source = _TEACHING_FIGURE_TOKEN.sub(replace_teaching_figure, source)
    resolved = _resolve_asset_refs(source, asset_urls)
    rendered = markdown_library.markdown(
        resolved,
        extensions=["tables", "sane_lists", "smarty"],
        output_format="html",
    )
    # Existing authored image-plus-caption pairs continue to work for old course content.
    rendered = re.sub(r"<img\b", '<img tabindex="0" role="button" aria-label="Enlarge course figure"', rendered)
    rendered = re.sub(
        r"<p>(<img\b[^>]*>)</p>\s*<p>(.*?)</p>",
        r'<figure class="tt-course-figure">\1<figcaption>\2</figcaption></figure>',
        rendered,
        flags=re.DOTALL,
    )
    for token, markup in figure_frames.items():
        rendered = rendered.replace(f"<p>{token}</p>", markup).replace(token, markup)
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



def build_lesson_sections(
    source,
    asset_urls=None,
    user=None,
    admin_preview=False,
    figure_metadata=None,
    figure_prefix=None,
):
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
            # Keep the full authored heading marker instead of flattening H4-H6 to H3.
            text = current_heading + ("\n\n" + text if text else "")
        groups[current_group].append(text)
        current_lines = []
        current_heading = None

    for line in lines:
        match = _HEADING.match(line)
        if match:
            finish_section()
            current_heading = line.strip()
            heading = match.group(2).casefold()
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
            figure_metadata=figure_metadata, figure_prefix=figure_prefix,
        ),
        "examples_html": render_safe_markdown(
            rendered["examples"], asset_urls, user=user, admin_preview=admin_preview,
            figure_metadata=figure_metadata, figure_prefix=figure_prefix,
        ),
        "practice_html": render_safe_markdown(
            rendered["practice"], asset_urls, user=user, admin_preview=admin_preview,
            figure_metadata=figure_metadata, figure_prefix=figure_prefix,
        ),
        "figure_count": figure_count,
    }
