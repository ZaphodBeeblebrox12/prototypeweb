"""Search discovery endpoints for public Academy course overviews."""
from xml.etree import ElementTree

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_GET

from .course_card_utils import is_course_card_recommendable
from .models import Course

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ElementTree.register_namespace("", SITEMAP_NS)


def _indexing_enabled():
    return bool(getattr(settings, "TRADETHESIS_SEO_INDEXABLE", False))


def is_public_course_seo_candidate(course):
    """Return whether a published course belongs in public search discovery."""
    return (
        course.status == Course.Status.PUBLISHED
        and course.catalogue_role != Course.CatalogueRole.HIDDEN
        and is_course_card_recommendable(course.title, course.summary, course.description)
    )


@require_GET
def academy_robots_txt(request):
    """Allow crawlers to read noindex tags; advertise sitemap only after opt-in."""
    lines = ["User-agent: *", "Allow: /"]
    if _indexing_enabled():
        lines.extend(["", f"Sitemap: {request.build_absolute_uri(reverse('academy_sitemap'))}"])
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


@require_GET
def academy_sitemap_xml(request):
    """List visible published course overviews, never lessons or private areas."""
    if not _indexing_enabled():
        return HttpResponse("Search indexing is disabled for this deployment.", status=404)

    root = ElementTree.Element(f"{{{SITEMAP_NS}}}urlset")
    courses = (
        Course.objects.filter(
            status=Course.Status.PUBLISHED,
            modules__is_published=True,
            modules__lessons__is_published=True,
        )
        .exclude(catalogue_role=Course.CatalogueRole.HIDDEN)
        .distinct()
        .order_by("position", "title", "slug")
    )
    for course in courses:
        if not is_public_course_seo_candidate(course):
            continue
        node = ElementTree.SubElement(root, f"{{{SITEMAP_NS}}}url")
        loc = request.build_absolute_uri(reverse("academy:course-detail", args=[course.slug]))
        ElementTree.SubElement(node, f"{{{SITEMAP_NS}}}loc").text = loc
        if course.updated_at:
            ElementTree.SubElement(node, f"{{{SITEMAP_NS}}}lastmod").text = course.updated_at.date().isoformat()

    payload = ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)
    return HttpResponse(payload, content_type="application/xml; charset=utf-8")
