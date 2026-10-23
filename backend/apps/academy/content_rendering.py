"""Safe Markdown rendering and sectioning for the shared Learning Room."""
import html
import re
import uuid

import bleach
import markdown as markdown_library
from django.urls import reverse

from .course_card_utils import (
    compact_course_topic,
    course_card_art_copy,
    course_card_mark,
    is_course_card_recommendable,
)
from .models import Course, CourseImport, Lesson
from .regional_content import resolve_regional_lesson_content, strip_unmanaged_regional_images

_ALLOWED_TAGS = {
    "a", "aside", "blockquote", "br", "caption", "code", "del", "div", "em", "figcaption", "figure",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "img", "li", "ol", "p", "pre",
    "s", "small", "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
}
_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "class"],
    "aside": ["class", "aria-label"],
    "div": ["class", "role", "aria-label", "tabindex"],
    "figure": ["class", "data-figure-id"],
    "figcaption": ["class"],
    "table": ["class"],
    "caption": ["class"],
    "img": ["src", "alt", "title", "loading", "width", "height", "tabindex", "role", "aria-label"],
    "span": ["class", "aria-label", "title"],
    "strong": ["class"],
    "th": ["align", "colspan", "rowspan", "scope"], "td": ["align", "colspan", "rowspan"],
}
_IMAGE_REF = re.compile(r"asset://([0-9a-fA-F-]{36})")
_IMAGE_MARKDOWN = re.compile(r"!\[([^\]]*)\]\(asset://([0-9a-fA-F-]{36})(?:\s+[^)]*)?\)")
_TEACHING_FIGURE_TOKEN = re.compile(r"\[\[teaching-figure:([A-Za-z0-9_-]{1,120})\]\]")
_IMAGE_GROUP_TOKEN = re.compile(r"\[\[image-group:([A-Za-z0-9_-]{1,120})\]\]")
_LESSON_REF = re.compile(r"\[\[(lesson|lesson-card):([0-9a-fA-F-]{36})\]\]")
_COURSE_CARD_REF = re.compile(r"\[\[course-card:(?:(coming-soon):)?([0-9a-fA-F-]{36})\]\]")
_TABLE_BLOCK_TOKEN = re.compile(r"\[\[table-block:([A-Za-z0-9_-]{1,120})\]\]")
_TAB_ROUTE_TOKEN = re.compile(r"^\s*\[\[lesson-tab:(idea|examples|practice)\]\]\s*$", re.IGNORECASE)


def _deduplicate_course_card_refs(source):
    """Keep the final placement of each companion course card within a lesson."""
    source = source or ""
    matches = list(_COURSE_CARD_REF.finditer(source))
    seen = set()
    remove_spans = []
    for match in reversed(matches):
        key = ((match.group(1) or "").casefold(), match.group(2).casefold())
        if key in seen:
            remove_spans.append((match.start(), match.end()))
        else:
            seen.add(key)
    for start, end in remove_spans:
        source = source[:start] + source[end:]
    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", source)

_REGIONAL_BLOCK_TOKEN = re.compile(r"\[\[regional-block:([A-Za-z0-9_-]{1,120})\]\]")
_REGIONAL_CODES = frozenset({"APAC", "EU", "NA", "LATAM", "MENA", "SSA"})
_HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
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


def _resolve_course_cards(source):
    """Resolve stable course-card references into the approved compact inline course preview."""
    from html import escape

    references = []
    for kind, raw_id in _COURSE_CARD_REF.findall(source or ""):
        try:
            references.append((kind, str(uuid.UUID(raw_id))))
        except (TypeError, ValueError, AttributeError):
            continue
    if not references:
        return source or "", {}

    all_ids = {stable_id for _kind, stable_id in references}
    teaser_ids = {stable_id for kind, stable_id in references if kind == "coming-soon"}
    courses_by_id = {
        str(course.pk): course
        for course in Course.objects.filter(pk__in=all_ids, status=Course.Status.PUBLISHED)
        if is_course_card_recommendable(course.title, course.summary, course.description)
    }
    teasers_by_id = {
        str(teaser.pk): teaser
        for teaser in CourseImport.objects.filter(pk__in=teaser_ids).select_related("target_course")
    } if teaser_ids else {}
    teaser_slugs = {teaser.course_slug for teaser in teasers_by_id.values()}
    published_by_slug = {
        course.slug: course
        for course in Course.objects.filter(slug__in=teaser_slugs, status=Course.Status.PUBLISHED)
        if is_course_card_recommendable(course.title, course.summary, course.description)
    } if teaser_slugs else {}

    def render_topics(raw):
        if not isinstance(raw, list):
            return ""
        topics = []
        for value in raw:
            if not isinstance(value, str):
                continue
            label = compact_course_topic(value)
            if label and label not in topics:
                topics.append(label)
            if len(topics) == 2:
                break
        if not topics:
            return ""
        chips = "".join(f"<span>{escape(topic)}</span>" for topic in topics)
        return '<div class="tt-course-preview-card__topics" aria-label="Topics covered">' + chips + "</div>"

    def render_art(title, category=""):
        mark = escape(course_card_mark(title))
        first, second = course_card_art_copy(title, category)
        source_text = f"{title} {category}".casefold()
        is_volume_price = "volume" in source_text and "price" in source_text
        art_class = "tt-course-preview-card__art tt-course-preview-card__art--cover"
        if is_volume_price:
            mark_markup = '<span class="tt-course-preview-card__mark tt-course-preview-card__mark--feature">BEHIND<br>THE MOVE</span>'
            art_label = "VOLUME × PRICE"
        else:
            mark_markup = f'<span class="tt-course-preview-card__mark">{mark}</span>'
            art_label = f"{first} · {second}"
        return (
            f'<div class="{art_class}">'
            f'{mark_markup}'
            f'<small>{escape(art_label)}</small>'
            '</div>'
        )

    def render_card(title, summary, topics, destination="", category="", coming_soon=False):
        safe_title = escape(str(title or "Course"))
        safe_summary = escape(str(summary or "Move beyond this example and study the broader toolkit."))
        if coming_soon:
            kicker = "Coming soon"
            cta = (
                '<span class="tt-course-preview-card__cta" aria-label="Course not yet available">'
                'In preparation</span>'
            )
            modifier = " tt-course-preview-card--coming-soon"
        else:
            kicker = "Companion course"
            safe_destination = escape(destination, quote=True)
            cta = (
                f'<a class="tt-course-preview-card__cta" href="{safe_destination}" '
                'rel="noopener noreferrer">View course outline <span>↗</span></a>'
            )
            modifier = ""
        card_text = f"{title} {category}".casefold()
        display_topics = ["Volume", "Price structure"] if "volume" in card_text and "price" in card_text else topics
        return (
            f'<aside class="tt-course-preview-card{modifier}" aria-label="Explore a related TradeThesis course">'
            '<div class="tt-course-preview-card__copy">'
            f'<span class="tt-course-preview-card__kicker">{kicker}</span>'
            f'<h3>{safe_title}</h3><p>{safe_summary}</p>'
            f'{render_topics(display_topics)}{cta}'
            '</div>'
            f'{render_art(title, category)}'
            '</aside>'
        )

    def render_published_course(course):
        return render_card(
            course.title,
            (course.summary or course.description)[:360],
            course.learning_outcomes,
            destination=reverse("academy:course-detail", args=[course.slug]),
            category=course.category,
        )

    def render_coming_soon(teaser, builder_state):
        title = str(builder_state.get("title") or teaser.title or "Course")
        summary = str(
            builder_state.get("summary") or builder_state.get("description")
            or "Move beyond this example and study the broader toolkit."
        )[:360]
        category = str(builder_state.get("category") or "TradeThesis courses")[:80]
        return render_card(title, summary, builder_state.get("outcomes"), category=category, coming_soon=True)

    def unavailable_card():
        return (
            '<aside class="tt-course-preview-card tt-course-preview-card--unavailable" '
            'aria-label="Course currently unavailable">'
            '<div class="tt-course-preview-card__copy">'
            '<span class="tt-course-preview-card__kicker">Keep learning</span>'
            '<h3>Course currently unavailable</h3>'
            '<p>This course is not in the published catalogue right now.</p>'
            '</div></aside>'
        )

    replacements = {}

    def replace_reference(match):
        kind, stable_id = match.groups()
        course = courses_by_id.get(stable_id) if not kind else None
        coming_soon_data = None
        if kind == "coming-soon":
            teaser = teasers_by_id.get(stable_id)
            if teaser is not None:
                target = teaser.target_course
                if target is not None and target.status == Course.Status.PUBLISHED:
                    if is_course_card_recommendable(target.title, target.summary, target.description):
                        course = target
                else:
                    course = published_by_slug.get(teaser.course_slug)
                if course is None and (
                    teaser.status in (CourseImport.Status.DRAFT, CourseImport.Status.REVIEW)
                    and teaser.target_course_id is None
                    and isinstance(teaser.payload, dict)
                ):
                    builder_state = teaser.payload.get("builder_state")
                    if isinstance(builder_state, dict) and builder_state.get("comingSoon"):
                        teaser_title = str(builder_state.get("title") or teaser.title or "Course")
                        teaser_summary = str(builder_state.get("summary") or builder_state.get("description") or "")
                        if is_course_card_recommendable(teaser_title, teaser_summary, str(builder_state.get("description") or "")):
                            coming_soon_data = (teaser, builder_state)

        if course is not None:
            markup = render_published_course(course)
        elif coming_soon_data is not None:
            markup = render_coming_soon(*coming_soon_data)
        else:
            markup = unavailable_card()

        token = f"TTCOURSECARDREF{len(replacements)}TOKEN"
        replacements[token] = markup
        return token

    return _COURSE_CARD_REF.sub(replace_reference, source or ""), replacements



def resolve_regional_blocks(source, regional_blocks=None, country_code=None, region_code=None):
    """Resolve builder-managed regional content server-side before sectioning.

    An exact country override wins over a region override. An explicitly hidden
    matching block produces no markup; otherwise global/base text is the fallback.
    """
    source = str(source or "")
    if not source:
        return source
    if isinstance(regional_blocks, list):
        blocks = {
            str(item.get("id") or ""): item
            for item in regional_blocks
            if isinstance(item, dict) and item.get("id")
        }
    elif isinstance(regional_blocks, dict):
        blocks = {str(key): value for key, value in regional_blocks.items() if isinstance(value, dict)}
    else:
        blocks = {}
    country = str(country_code or "").strip().upper()
    region = str(region_code or "").strip().upper()
    if region not in _REGIONAL_CODES:
        region = ""

    def replace(match):
        block = blocks.get(match.group(1))
        if not isinstance(block, dict):
            # A stale marker must not leak authoring syntax to learners.
            return ""
        variants = block.get("variants") if isinstance(block.get("variants"), list) else []
        selected = None
        if country:
            selected = next((
                item for item in variants
                if isinstance(item, dict)
                and str(item.get("scope") or "").strip().lower() == "country"
                and str(item.get("code") or item.get("country") or "").strip().upper() == country
            ), None)
        if selected is None and region:
            selected = next((
                item for item in variants
                if isinstance(item, dict)
                and str(item.get("scope") or "").strip().lower() == "region"
                and str(item.get("code") or item.get("region") or "").strip().upper() == region
            ), None)
        if selected is not None:
            if bool(selected.get("hidden", False)):
                return ""
            return strip_unmanaged_regional_images(selected.get("content") or "")
        return strip_unmanaged_regional_images(
            block.get("base_content", block.get("baseContent", "")) or ""
        )

    return _REGIONAL_BLOCK_TOKEN.sub(replace, source)


def render_safe_markdown(
    source,
    asset_urls=None,
    user=None,
    admin_preview=False,
    figure_metadata=None,
    figure_prefix=None,
    module_label="",
    course_title="",
    table_metadata=None,
):
    """Render sanitised Markdown, structured tables, figures and groups."""
    from html import escape

    source = validate_markdown_source(source or "")
    source, lesson_references = _resolve_lesson_references(
        source, user=user, admin_preview=admin_preview,
    )
    source, course_cards = _resolve_course_cards(source)
    table_metadata = table_metadata if isinstance(table_metadata, dict) else {}
    table_frames = {}

    def replace_table_block(match):
        table_id = match.group(1)
        metadata = table_metadata.get(table_id)
        rows = metadata.get("rows") if isinstance(metadata, dict) else None
        if not isinstance(rows, list) or not rows:
            markup = '<aside class="tt-structured-table-unavailable" role="status"><strong>Table unavailable in this preview</strong></aside>'
        else:
            head_rows, body_rows = [], []
            title = escape(str(metadata.get("title") or "Lesson table").strip() or "Lesson table")
            for row in rows[:60]:
                if not isinstance(row, dict):
                    continue
                section = "head" if row.get("section") == "head" else "body"
                cells = row.get("cells") if isinstance(row.get("cells"), list) else []
                cell_markup = []
                for cell in cells[:12]:
                    if not isinstance(cell, dict):
                        continue
                    tag = "th" if section == "head" or bool(cell.get("header")) else "td"
                    try:
                        colspan = max(1, min(12, int(cell.get("colspan", 1))))
                        rowspan = max(1, min(12, int(cell.get("rowspan", 1))))
                    except (TypeError, ValueError):
                        colspan, rowspan = 1, 1
                    spans = (f' colspan="{colspan}"' if colspan > 1 else "") + (f' rowspan="{rowspan}"' if rowspan > 1 else "")
                    scope = ' scope="colgroup"' if tag == "th" and colspan > 1 else (' scope="col"' if tag == "th" else "")
                    cell_markup.append(f"<{tag}{spans}{scope}>{escape(str(cell.get('text') or ''))}</{tag}>")
                if not cell_markup:
                    continue
                row_markup = "<tr>" + "".join(cell_markup) + "</tr>"
                (head_rows if section == "head" else body_rows).append(row_markup)
            thead = "<thead>" + "".join(head_rows) + "</thead>" if head_rows else ""
            tbody = "<tbody>" + "".join(body_rows) + "</tbody>" if body_rows else ""
            if not head_rows:
                markup = '<aside class="tt-structured-table-unavailable" role="status"><strong>Table has no header row</strong></aside>'
            else:
                markup = (
                    '<div class="lesson-table-wrap tt-structured-table-wrap" role="region" tabindex="0" '
                    'aria-label="Scrollable table: ' + title + '">'
                    '<table class="tt-structured-table"><caption class="tt-structured-table-caption">'
                    + title + '</caption>' + thead + tbody + "</table></div>"
                )
        token = f"TTSTRUCTUREDTABLE{len(table_frames)}END"
        table_frames[token] = markup
        return token

    source = _TABLE_BLOCK_TOKEN.sub(replace_table_block, source or "")
    asset_urls = asset_urls or {}
    figure_metadata = figure_metadata if isinstance(figure_metadata, dict) else {}
    figure_frames = {}
    raw_module_label = str(module_label or "LEARNING ROOM").strip()
    module_match = re.match(r"^module\s*(\d+)\s*[·—–:-]\s*(.*)$", raw_module_label, re.IGNORECASE)
    if module_match:
        module_number, module_name = module_match.groups()
        module_name = re.sub(
            r"^module\s*\d*\s*[·—–:-]?\s*", "", module_name, flags=re.IGNORECASE,
        ).strip()
        module_title = f"MODULE {int(module_number)} · {module_name}" if module_name else f"MODULE {int(module_number)}"
    elif raw_module_label.upper().startswith("MODULE"):
        module_title = raw_module_label
    else:
        module_title = f"MODULE · {raw_module_label}"
    safe_module_title = escape(module_title, quote=True)
    safe_course_title = escape(str(course_title or "Course").strip() or "Course", quote=True)

    def figure_header(title):
        safe_title = escape(str(title or "Chart").strip())
        return (
            '<span class="tt-purpose-figure-head">'
            '<span class="tt-purpose-figure-header-top">'
            f'<span class="tt-purpose-figure-module">{safe_module_title}</span>'
            '</span>'
            f'<strong class="tt-purpose-figure-title">{safe_title}</strong>'
            '</span>'
        )

    def image_group_header(title):
        safe_title = escape(str(title or "Image group").strip())
        return (
            '<span class="tt-purpose-figure-head tt-image-group-head">'
            '<span class="tt-purpose-figure-header-top">'
            f'<span class="tt-purpose-figure-module">{safe_module_title}</span>'
            f'<span class="tt-image-group-context" title="{safe_course_title}">{safe_course_title}</span>'
            '</span>'
            f'<strong class="tt-purpose-figure-title">{safe_title}</strong>'
            '</span>'
        )

    def display_image_title(metadata):
        raw_title = str(metadata.get("title") or "").strip()
        # Older drafts sometimes stored a filename as the title. Never display that
        # implementation detail as the authored heading in the learner-facing figure.
        if raw_title and re.search(r"\.(?:jpe?g|png|webp|gif|svg)$", raw_title, re.IGNORECASE):
            return "Chart"
        return raw_title or "Chart"

    def replace_structured_figure(match):
        alt_from_markdown, asset_id = match.groups()
        metadata = figure_metadata.get(asset_id)
        if not isinstance(metadata, dict):
            return match.group(0)

        alt = str(metadata.get("alt") or alt_from_markdown or "Course image").strip()
        title = display_image_title(metadata)
        caption = str(metadata.get("caption") or "").strip()

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
            f'{figure_header(title)}'
            f'<span class="tt-purpose-figure-body">{body}</span>{caption_markup}</figure>'
        )
        token = f"TTSTRUCTUREDFIGURE{len(figure_frames)}END"
        figure_frames[token] = markup
        return token

    def replace_image_group(match):
        group_id = match.group(1)
        metadata = figure_metadata.get(group_id)
        if not isinstance(metadata, dict) or metadata.get("type") != "image-group":
            return match.group(0)

        title = display_image_title(metadata)
        safe_group_id = escape(group_id, quote=True)
        raw_ids = metadata.get("image_ids", [])
        if not isinstance(raw_ids, list):
            raw_ids = []
        items = []
        for raw_id in raw_ids[:12]:
            asset_id = str(raw_id)
            image_metadata = figure_metadata.get(asset_id, {})
            if not isinstance(image_metadata, dict):
                image_metadata = {}
            alt = str(image_metadata.get("alt") or "Course image").strip()
            image_title = display_image_title(image_metadata)
            caption = str(image_metadata.get("caption") or "").strip()
            image_url = asset_urls.get(asset_id, "")
            if image_url:
                image = (
                    f'<span class="tt-purpose-figure-image">'
                    f'<img src="{escape(str(image_url), quote=True)}" alt="{escape(alt, quote=True)}" '
                    'loading="lazy" decoding="async" tabindex="0" role="button" '
                    'aria-label="Enlarge course figure"></span>'
                )
            else:
                image = (
                    '<span class="tt-purpose-figure-missing" role="status">'
                    '<strong>Image unavailable</strong></span>'
                )
            caption_markup = (
                f'<span class="tt-image-group-caption">{escape(caption)}</span>' if caption else ""
            )
            items.append(
                '<span class="tt-image-group-item">'
                f'{image}'
                '<span class="tt-image-group-item-heading">'
                '<span class="tt-image-group-case-id" aria-hidden="true"></span>'
                f'<strong class="tt-image-group-item-title">{escape(image_title)}</strong>'
                '</span>'
                f'{caption_markup}</span>'
            )

        if len(items) < 2:
            return '<span class="tt-purpose-figure-missing">This image group needs at least two uploaded images.</span>'
        note = str(metadata.get("note") or "").strip()
        note_markup = f'<span class="tt-purpose-figure-note">{escape(note)}</span>' if note else ""
        markup = (
            f'<figure class="tt-purpose-figure tt-image-group-figure" data-figure-id="{safe_group_id}">'
            f'{image_group_header(title)}'
            '<span class="tt-purpose-figure-body">'
            f'<span class="tt-image-group-grid">{"".join(items)}</span>'
            f'{note_markup}</span></figure>'
        )
        token = f"TTSTRUCTUREDFIGURE{len(figure_frames)}END"
        figure_frames[token] = markup
        return token

    source = _IMAGE_GROUP_TOKEN.sub(replace_image_group, source)

    # Replace only Markdown image references that have saved figure metadata. The placeholder
    # preserves the exact text/image/text position and prevents Markdown from stripping the frame.
    source = _IMAGE_MARKDOWN.sub(replace_structured_figure, source)

    def replace_teaching_figure(match):
        figure_id = match.group(1)
        metadata = figure_metadata.get(figure_id)
        if not isinstance(metadata, dict) or metadata.get("type") != "comparison-cards":
            return match.group(0)

        title = display_image_title(metadata)
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
            f'{figure_header(title)}'
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

    # Python-Markdown expresses table alignment as inline CSS. The sanitizer
    # intentionally strips style attributes, so convert only its known safe
    # left/center/right table-cell alignment into the already-allowed align
    # attribute before sanitising the final HTML.
    rendered = re.sub(
        r'(<(?:th|td)\b[^>]*?)\sstyle="text-align:\s*(left|center|right)\s*;?"',
        r'\1 align="\2"',
        rendered,
        flags=re.IGNORECASE,
    )

    # Match the approved course template: information tables sit in a framed,
    # horizontally scrollable wrapper so the header and cells remain readable
    # on narrow screens. Avoid nesting the wrapper when the author already used it.
    def wrap_information_table(match):
        prefix = rendered[:match.start()]
        last_open = prefix.rfind("<div")
        last_close = prefix.rfind("</div>")
        if last_open > last_close:
            opening_tag_end = prefix.find(">", last_open)
            opening_tag = prefix[last_open:opening_tag_end + 1]
            if re.search(r'class=["\'][^"\']*\blesson-table-wrap\b[^"\']*["\']', opening_tag, re.IGNORECASE):
                return match.group(0)
        return (
            '<div class="lesson-table-wrap" role="region" '
            'aria-label="Scrollable information table" tabindex="0">'
            + match.group(0) + '</div>'
        )

    rendered = re.sub(
        r"<table\b[^>]*>.*?</table>",
        wrap_information_table,
        rendered,
        flags=re.IGNORECASE | re.DOTALL,
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
    for token, markup in course_cards.items():
        rendered = rendered.replace(f"<p>{token}</p>", markup)
        rendered = rendered.replace(token, markup)
    for token, markup in table_frames.items():
        rendered = rendered.replace(f"<p>{token}</p>", markup)
        rendered = rendered.replace(token, markup)
    return bleach.clean(
        rendered,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols=["http", "https", "mailto"],
        strip=True,
    )



def _count_lesson_figures(source, figure_metadata=None):
    """Count displayed visual assets, including Builder structured figures.

    Image-group members count as individual assets. Repeated tokens count each
    displayed instance rather than only counting unique figure definitions.
    """
    source = source or ""
    figure_metadata = figure_metadata if isinstance(figure_metadata, dict) else {}
    count = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", source))

    for group_id in _IMAGE_GROUP_TOKEN.findall(source):
        metadata = figure_metadata.get(group_id)
        if not isinstance(metadata, dict) or metadata.get("type") != "image-group":
            continue
        image_ids = metadata.get("image_ids", [])
        if isinstance(image_ids, list):
            count += len({str(asset_id) for asset_id in image_ids if asset_id})

    for figure_id in _TEACHING_FIGURE_TOKEN.findall(source):
        metadata = figure_metadata.get(figure_id)
        if isinstance(metadata, dict) and metadata.get("type") == "comparison-cards":
            count += 1
    return count


def build_lesson_sections(
    source,
    asset_urls=None,
    user=None,
    admin_preview=False,
    figure_metadata=None,
    figure_prefix=None,
    module_label="",
    course_title="",
    regional_blocks=None,
    regional_content=None,
    country_code=None,
    region_code=None,
    table_metadata=None,
):
    """Group source headings into the three reusable Learning Room tabs."""
    source = resolve_regional_lesson_content(
        source or "", regional_content=regional_content,
        country_code=country_code, region_code=region_code,
    )
    source = resolve_regional_blocks(
        source, regional_blocks=regional_blocks,
        country_code=country_code, region_code=region_code,
    )
    source = _deduplicate_course_card_refs(source)
    lines = source.splitlines()
    groups = {"idea": [], "examples": [], "practice": []}
    current_group = "idea"
    current_heading = None
    current_lines = []
    pending_route = None

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
        route_marker = _TAB_ROUTE_TOKEN.match(line)
        if route_marker:
            # A route token is an instruction for the next heading, not a command
            # to move any text that follows it. Keep it pending until that heading
            # arrives so a misplaced token cannot strand a heading on one tab and
            # silently move its paragraph and companion cards to another.
            pending_route = route_marker.group(1).casefold()
            continue

        match = _HEADING.match(line)
        if match:
            finish_section()
            explicit_route = pending_route is not None
            if explicit_route:
                current_group = pending_route
                pending_route = None
            current_heading = line.strip()
            heading = match.group(2).casefold()
            if explicit_route:
                # The explicit route wins over heading-name heuristics for this heading.
                pass
            # Admin-added headings encode the selected Learning Room tab;
            # handle those exact prefixes before generic content heuristics.
            elif heading.startswith("compare the possibilities") or heading.startswith("additional concept figure"):
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

        if line.strip() and pending_route is not None:
            # The token was inserted inside a section instead of before a heading.
            # Ignore that stale instruction while preserving the section's own text.
            pending_route = None
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

    figure_count = _count_lesson_figures(source, figure_metadata)
    return {
        "idea_html": render_safe_markdown(
            rendered["idea"], asset_urls, user=user, admin_preview=admin_preview,
            figure_metadata=figure_metadata, figure_prefix=figure_prefix,
            module_label=module_label, course_title=course_title,
            table_metadata=table_metadata,
        ),
        "examples_html": render_safe_markdown(
            rendered["examples"], asset_urls, user=user, admin_preview=admin_preview,
            figure_metadata=figure_metadata, figure_prefix=figure_prefix,
            module_label=module_label, course_title=course_title,
        ),
        "practice_html": render_safe_markdown(
            rendered["practice"], asset_urls, user=user, admin_preview=admin_preview,
            figure_metadata=figure_metadata, figure_prefix=figure_prefix,
            module_label=module_label, course_title=course_title,
        ),
        "figure_count": figure_count,
    }
