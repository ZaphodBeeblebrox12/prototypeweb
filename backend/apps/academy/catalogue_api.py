"""Public, learner-safe course catalogue data for the static marketing site."""
from django.http import JsonResponse
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_GET

from .course_card_utils import is_course_card_recommendable
from .catalogue_presentation import (
    catalogue_presentation_api_fields,
    catalogue_presentation_from_payload,
    normalize_catalogue_presentation,
)
from .models import Course, CourseImport


@require_GET
def public_course_catalogue(request):
    """Return published catalogue metadata only; never expose lesson bodies or answer keys."""
    rows = []
    presentation_by_slug = {}
    for import_record in CourseImport.objects.filter(status=CourseImport.Status.PUBLISHED).order_by("course_slug", "-updated_at"):
        if import_record.course_slug in presentation_by_slug:
            continue
        presentation, configured = catalogue_presentation_from_payload(import_record.payload)
        if configured:
            presentation_by_slug[import_record.course_slug] = presentation
    courses = Course.objects.filter(status=Course.Status.PUBLISHED).prefetch_related("modules__lessons")
    for course in courses:
        if not is_course_card_recommendable(course.title, course.summary, course.description):
            continue
        modules = []
        for module in course.modules.all():
            if not module.is_published:
                continue
            lessons = [lesson for lesson in module.lessons.all() if lesson.is_published]
            if not lessons:
                continue
            modules.append({
                "title": module.title,
                "count": f"{len(lessons)} lesson" + ("" if len(lessons) == 1 else "s"),
                "preview": module.description[:500],
                "points": [lesson.title for lesson in lessons[:4]],
            })
        if not modules:
            continue
        rows.append({
            "id": str(course.pk),
            "slug": course.slug,
            "title": course.title,
            "category": course.category or "TradeThesis courses",
            "level": course.level or "Self-paced",
            "description": (course.summary or course.description)[:360],
            "outcome": " ".join(course.learning_outcomes)[:500] if course.learning_outcomes else course.description[:360],
            "complements": "Explore this published course in the TradeThesis Academy.",
            "price": "",
            "status": "published",
            "art": "structure",
            "modules": modules,
            "academyUrl": request.build_absolute_uri(reverse("academy:course-detail", args=[course.slug])),
            **catalogue_presentation_api_fields(presentation_by_slug.get(course.slug, normalize_catalogue_presentation({})), course.slug in presentation_by_slug),
        })
    # Teasers are metadata-only and never expose unpublished lesson content.
    published_slugs = {
        slug
        for slug, title, summary, description in Course.objects.filter(
            status=Course.Status.PUBLISHED,
        ).values_list("slug", "title", "summary", "description")
        if is_course_card_recommendable(title, summary, description)
    }
    seen_teaser_slugs = set()
    teasers = CourseImport.objects.filter(
        status__in=[CourseImport.Status.DRAFT, CourseImport.Status.REVIEW],
        target_course__isnull=True,
    ).order_by("-updated_at")
    for record in teasers:
        state = (record.payload or {}).get("builder_state") or {}
        title = str(state.get("title") or record.title)[:200]
        summary = str(state.get("summary") or "")[:360]
        description = str(state.get("description") or "")[:1000]
        if (
            not state.get("comingSoon")
            or record.course_slug in published_slugs
            or record.course_slug in seen_teaser_slugs
            or not is_course_card_recommendable(title, summary, description)
        ):
            continue
        seen_teaser_slugs.add(record.course_slug)
        rows.append({
            "id": "coming-soon-" + str(record.pk), "slug": record.course_slug,
            "title": title,
            "category": str(state.get("category") or "TradeThesis courses")[:80],
            "level": str(state.get("level") or "Self-paced")[:40],
            "description": (summary or description)[:360],
            "outcome": "Course details and enrolment will be announced closer to launch.",
            "complements": "This course is being prepared. Full details will be shared closer to launch.",
            "price": "Coming soon", "status": "coming-soon", "art": "structure",
            "modules": [{
                "title": "Course outline", "count": "Coming soon",
                "preview": "The full course outline will be shared closer to launch.",
                "points": ["Content is being prepared."],
            }],
            **catalogue_presentation_api_fields(*catalogue_presentation_from_payload(record.payload)),
        })
    response = JsonResponse({"courses": rows})
    response["Access-Control-Allow-Origin"] = "*"
    response["Cache-Control"] = "public, max-age=60"
    response["X-Content-Type-Options"] = "nosniff"
    patch_vary_headers(response, ["Origin"])
    return response
