"""Public, learner-safe course catalogue data for the static marketing site."""
from django.http import JsonResponse
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_GET

from .models import Course


@require_GET
def public_course_catalogue(request):
    """Return published catalogue metadata only; never expose lesson bodies or answer keys."""
    rows = []
    courses = Course.objects.filter(status=Course.Status.PUBLISHED).prefetch_related("modules__lessons")
    for course in courses:
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
            "description": course.summary or course.description[:360],
            "outcome": " ".join(course.learning_outcomes)[:500] if course.learning_outcomes else course.description[:360],
            "complements": "Explore this published course in the TradeThesis Academy.",
            "price": "",
            "status": "published",
            "art": "structure",
            "modules": modules,
            "academyUrl": request.build_absolute_uri(reverse("academy:course-detail", args=[course.slug])),
        })
    response = JsonResponse({"courses": rows})
    response["Access-Control-Allow-Origin"] = "*"
    response["Cache-Control"] = "public, max-age=60"
    response["X-Content-Type-Options"] = "nosniff"
    patch_vary_headers(response, ["Origin"])
    return response
