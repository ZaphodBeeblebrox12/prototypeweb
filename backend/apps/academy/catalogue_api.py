"""Public, learner-safe course catalogue data for the static marketing site."""

from django.http import JsonResponse
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_GET

from apps.subscriptions.models import PlanPrice

from .catalogue_presentation import (
    catalogue_presentation_api_fields,
    catalogue_presentation_from_payload,
    normalize_catalogue_presentation,
)
from .course_card_utils import is_course_card_recommendable
from .course_pricing import resolved_course_offer_price
from .models import Course, CourseImport, CourseOffer


@require_GET
def public_course_catalogue(request):
    """Return published catalogue metadata only; never expose lesson bodies or answer keys."""
    rows = []
    presentation_by_slug = {}
    for import_record in CourseImport.objects.filter(status=CourseImport.Status.PUBLISHED).order_by(
        "course_slug", "-updated_at"
    ):
        if import_record.course_slug in presentation_by_slug:
            continue
        presentation, configured = catalogue_presentation_from_payload(import_record.payload)
        if configured:
            presentation_by_slug[import_record.course_slug] = presentation
    courses = (
        Course.objects.filter(status=Course.Status.PUBLISHED)
        .prefetch_related("modules__lessons", "offers__plan")
        .order_by("position", "title", "slug")
    )
    for course in courses:
        # Send only a minimal marker for hidden courses so the static marketing
        # page can remove a manually-curated card with the same slug.
        if course.catalogue_role == Course.CatalogueRole.HIDDEN:
            rows.append({
                "id": str(course.pk),
                "slug": course.slug,
                "catalogueRole": Course.CatalogueRole.HIDDEN,
                "status": "hidden",
            })
            continue
        if not is_course_card_recommendable(course.title, course.summary, course.description):
            continue
        modules = []
        for module in course.modules.all():
            if not module.is_published:
                continue
            lessons = [lesson for lesson in module.lessons.all() if lesson.is_published]
            if not lessons:
                continue
            modules.append(
                {
                    "title": module.title,
                    "count": f"{len(lessons)} lesson" + ("" if len(lessons) == 1 else "s"),
                    "preview": module.description[:500],
                    "points": [lesson.title for lesson in lessons[:4]],
                }
            )
        if not modules:
            continue
        offers = [
            offer for offer in course.offers.all()
            if offer.is_active and offer.plan_id and offer.plan.is_active and offer.is_saleable
        ]
        resolved_price = resolved_course_offer_price(offers[0], request) if offers else None
        has_configured_offer_price = bool(
            offers
            and (
                offers[0].plan.prices.filter(
                    interval=PlanPrice.Interval.ONE_TIME, is_active=True
                ).exists()
                or offers[0].plan.geo_prices.filter(
                    interval=PlanPrice.Interval.ONE_TIME, is_active=True
                ).exists()
            )
        ) if offers and not resolved_price else bool(resolved_price)
        if resolved_price:
            course_price, _currency = resolved_price
            price_note = (
                "One-time purchase · also included in TradeThesis Free"
                if course.access_type == Course.AccessType.MIXED
                else "One-time purchase · secure checkout"
            )
            price_configured = True
        elif course.access_type == Course.AccessType.FREE:
            course_price, price_note, price_configured = "Free", "Enrol with your account · no payment required", True
        elif course.access_type == Course.AccessType.MEMBERSHIP:
            course_price, price_note, price_configured = "Included in TradeThesis Free", "Free membership access", True
        elif course.access_type == Course.AccessType.MIXED:
            course_price, price_note, price_configured = "Included in TradeThesis Free", "Free membership or individual purchase", True
        elif course.access_type == Course.AccessType.PAID and has_configured_offer_price:
            course_price, price_note, price_configured = "", "Individual checkout is not available in your market", True
        else:
            course_price, price_note, price_configured = "", "No active purchase price is configured", False

        rows.append(
            {
                "id": str(course.pk),
                "slug": course.slug,
                "title": course.title,
                "accessType": course.access_type,
                "isFree": course.access_type == Course.AccessType.FREE,
                "includedInFreeMembership": course.access_type in (
                    Course.AccessType.MEMBERSHIP,
                    Course.AccessType.MIXED,
                ),
                "category": course.category or "TradeThesis courses",
                "level": course.level or "Self-paced",
                "description": (course.summary or course.description)[:360],
                "outcome": (
                    " ".join(course.learning_outcomes)[:500]
                    if course.learning_outcomes
                    else course.description[:360]
                ),
                "complements": "Explore this published course in the TradeThesis Academy.",
                "price": course_price,
                "priceNote": price_note,
                "priceConfigured": price_configured,
                "status": "published",
                "catalogueRole": course.catalogue_role,
                "catalogueOrder": course.position,
                "art": "structure",
                "modules": modules,
                "academyUrl": request.build_absolute_uri(
                    reverse("academy:course-detail", args=[course.slug])
                ),
                **catalogue_presentation_api_fields(
                    presentation_by_slug.get(course.slug, normalize_catalogue_presentation({})),
                    course.slug in presentation_by_slug,
                ),
            }
        )
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
    ).order_by("-updated_at", "course_slug")
    for record in teasers:
        state = (record.payload or {}).get("builder_state") or {}
        title = str(state.get("title") or record.title)[:200]
        summary = str(state.get("summary") or "")[:360]
        description = str(state.get("description") or "")[:1000]
        catalogue_role = str(state.get("catalogueRole") or Course.CatalogueRole.MINI)
        if catalogue_role not in Course.CatalogueRole.values:
            catalogue_role = Course.CatalogueRole.MINI
        if (
            not state.get("comingSoon")
            or catalogue_role == Course.CatalogueRole.HIDDEN
            or record.course_slug in published_slugs
            or record.course_slug in seen_teaser_slugs
            or not is_course_card_recommendable(title, summary, description)
        ):
            continue
        seen_teaser_slugs.add(record.course_slug)
        rows.append(
            {
                "id": "coming-soon-" + str(record.pk),
                "slug": record.course_slug,
                "title": title,
                "category": str(state.get("category") or "TradeThesis courses")[:80],
                "level": str(state.get("level") or "Self-paced")[:40],
                "description": (summary or description)[:360],
                "outcome": "Course details and enrolment will be announced closer to launch.",
                "complements": "This course is being prepared. Full details will be shared closer to launch.",
                "price": "Coming soon",
                "status": "coming-soon",
                "catalogueRole": catalogue_role,
                "catalogueOrder": max(0, int(state.get("position") or 0)),
                "art": "structure",
                "modules": [
                    {
                        "title": "Course outline",
                        "count": "Coming soon",
                        "preview": "The full course outline will be shared closer to launch.",
                        "points": ["Content is being prepared."],
                    }
                ],
                **catalogue_presentation_api_fields(
                    *catalogue_presentation_from_payload(record.payload)
                ),
            }
        )
    response = JsonResponse({"courses": rows})
    response["Access-Control-Allow-Origin"] = "*"
    response["Cache-Control"] = "public, max-age=60"
    response["X-Content-Type-Options"] = "nosniff"
    patch_vary_headers(response, ["Origin"])
    return response
