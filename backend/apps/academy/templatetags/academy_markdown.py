import bleach
import markdown as markdown_library

from bleach.sanitizer import ALLOWED_PROTOCOLS
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_ALLOWED_TAGS = {
    "a", "abbr", "blockquote", "br", "caption", "code", "dd", "del", "details",
    "dl", "dt", "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img",
    "li", "ol", "p", "pre", "s", "small", "strong", "summary", "sup", "sub",
    "table", "tbody", "td", "th", "thead", "tr", "ul",
}
_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
}


def render_markdown(value):
    """Render lesson Markdown while stripping unsafe raw HTML and attributes."""
    html = markdown_library.markdown(
        value or "",
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )
    cleaned = bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols=set(ALLOWED_PROTOCOLS),
        strip=True,
        strip_comments=True,
    )
    return mark_safe(cleaned)


@register.filter(name="academy_markdown")
def academy_markdown(value):
    return render_markdown(value)
