"""Authenticated learner views for TradeThesis Academy."""

import json
import mimetypes
import re
from contextlib import suppress
from copy import deepcopy
from urllib.parse import quote
from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch, Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from .content_rendering import (
    build_lesson_sections,
    render_safe_markdown,
    resolve_regional_blocks,
    resolve_regional_lesson_content,
)
from .course_card_utils import course_topic_tags, is_course_card_recommendable
from .course_pricing import resolved_course_offer_price
from .models import (
    Course,
    CourseEntitlement,
    CourseImport,
    CourseMediaAsset,
    CourseModule,
    CourseOffer,
    Lesson,
    LessonInstructorMaterial,
    LessonProgress,
    ProtectedLessonVideo,
)
from .permissions import is_course_content_admin
from .regional_content import (
    ASSET_REFERENCE_RE,
    IMAGE_GROUP_REFERENCE_RE,
    get_content_country,
    get_content_region_for_country,
    regional_block_asset_ids,
    regional_lesson_content_asset_ids,
)
from .services import (
    can_access_lesson,
    get_active_entitlement,
    get_resume_lesson,
    lesson_release_at,
    update_lesson_progress,
)


def _lesson_asset_ids_for_audience(lesson, country_code=None, region_code=None):
    """Return only the lesson assets referenced by content selected for this audience."""
    content_json = lesson.content_json if isinstance(lesson.content_json, dict) else {}
    declared_ids = {
        str(value).strip().lower()
        for value in content_json.get("asset_ids", [])
        if str(value or "").strip()
    }
    regional_ids = regional_block_asset_ids(content_json) | regional_lesson_content_asset_ids(
        content_json
    )
    resolved_markdown = resolve_regional_lesson_content(
        lesson.content_markdown or "",
        regional_content=content_json.get("regional_lesson_content", {}),
        country_code=country_code,
        region_code=region_code,
    )
    resolved_markdown = resolve_regional_blocks(
        resolved_markdown,
        regional_blocks=content_json.get("regional_blocks", {}),
        country_code=country_code,
        region_code=region_code,
    )
    # Preserve legacy/nonregional references, but remove assets whose only
    # reference is inside an unselected regional variant.
    allowed_ids = declared_ids - regional_ids
    allowed_ids.update(value.lower() for value in ASSET_REFERENCE_RE.findall(resolved_markdown))
    questions = (
        content_json.get("questions") if isinstance(content_json.get("questions"), list) else []
    )
    for question in questions:
        if not isinstance(question, dict):
            continue
        image_id = question.get("image_asset_id") or question.get("imageId")
        if image_id:
            allowed_ids.add(str(image_id).strip().lower())
    figures = content_json.get("figures") if isinstance(content_json.get("figures"), dict) else {}
    for group_id in IMAGE_GROUP_REFERENCE_RE.findall(resolved_markdown):
        figure = figures.get(group_id)
        if not isinstance(figure, dict) or figure.get("type") != "image-group":
            continue
        image_ids = figure.get("image_ids") if isinstance(figure.get("image_ids"), list) else []
        allowed_ids.update(
            str(value).strip().lower() for value in image_ids if str(value or "").strip()
        )
    return allowed_ids


def _module_display_title(value):
    """Return the authored module name without an optional module-number prefix."""
    title = re.sub(
        r"^module\s*\d*\s*[·—–:-]?\s*", "", str(value or "").strip(), flags=re.IGNORECASE
    )
    return title.strip() or "Learning Room"


def _regional_audience(request, admin_preview=False):
    """Resolve real content geography; only admins can simulate an audience in preview."""

    country = None
    if admin_preview and getattr(request, "user", None) and is_course_content_admin(request.user):
        audience = (
            str(request.GET.get("preview_audience") or request.GET.get("preview_country") or "")
            .strip()
            .upper()
        )
        if audience in {"", "GLOBAL"}:
            return None, None
        if audience.startswith("REGION:"):
            candidate_region = audience.split(":", 1)[1]
            if candidate_region in {"APAC", "EU", "NA", "LATAM", "MENA", "SSA"}:
                return None, candidate_region
        if len(audience) == 2 and audience.isalpha() and audience.isascii():
            country = audience
        else:
            country = get_content_country(request)
    else:
        country = get_content_country(request)
    return country, get_content_region_for_country(country) if country else None


def _practice_questions_with_images(questions, asset_urls, figure_metadata):
    """Add permission-checked asset URLs and harmless display metadata to learner questions."""
    if not isinstance(questions, list):
        return []
    asset_urls = asset_urls if isinstance(asset_urls, dict) else {}
    figure_metadata = figure_metadata if isinstance(figure_metadata, dict) else {}
    hydrated = []
    for raw_question in questions:
        if not isinstance(raw_question, dict):
            continue
        question = dict(raw_question)
        asset_id = str(question.get("image_asset_id") or "")
        metadata = figure_metadata.get(asset_id, {})
        if not isinstance(metadata, dict):
            metadata = {}
        question["image_url"] = str(asset_urls.get(asset_id) or "") if asset_id else ""
        question["image_title"] = str(metadata.get("title") or "Chart")[:240]
        question["image_alt"] = str(metadata.get("alt") or question["image_title"])[:500]
        question["image_caption"] = str(metadata.get("caption") or "")[:500]
        hydrated.append(question)
    return hydrated


def _notebook_for_course_display(course_slug, notebook):
    """Return topic-appropriate prompts; only the Bollinger course gets Bollinger-specific copy."""
    result = deepcopy(notebook) if isinstance(notebook, dict) else {}
    default_title_values = {
        "",
        "Your Trading Notebook",
        "Before you make the call",
        "Before treating a touch as a setup",
    }
    default_prompts = [
        {"label": "Describe", "text": "What evidence is visible?"},
        {"label": "Interpret", "text": "What could it mean in context?"},
        {"label": "Apply", "text": "What would change your view?"},
    ]
    legacy_generic_prompts = [
        {"label": "Observe", "text": "Describe the evidence visible in the chart."},
        {"label": "Interpret", "text": "State one possible reading and a reasonable alternative."},
        {
            "label": "Test",
            "text": "Name the next evidence that would strengthen or weaken your reading.",
        },
    ]
    legacy_bollinger_prompts = [
        {"label": "Describe", "text": "Where is price relative to the bands and middle line?"},
        {
            "label": "Interpret",
            "text": "Does the structure look like a range, a trend or a transition? What is your alternative explanation?",
        },
        {
            "label": "Test",
            "text": "What future price behaviour would strengthen or weaken your view?",
        },
    ]
    raw_prompts = result.get("prompts")
    missing_prompts = not isinstance(raw_prompts, list) or not raw_prompts
    if isinstance(raw_prompts, list):
        usable_prompts = [
            prompt
            for prompt in raw_prompts
            if isinstance(prompt, dict)
            and str(prompt.get("label") or "").strip()
            and str(prompt.get("text") or "").strip()
        ]
        missing_prompts = not usable_prompts
        result["prompts"] = usable_prompts[:6] if usable_prompts else deepcopy(default_prompts)

    matches_generic_defaults = missing_prompts
    if isinstance(raw_prompts, list):
        generic_sets = (default_prompts, legacy_generic_prompts)
        if course_slug == "understand-bollinger-bands":
            generic_sets += (legacy_bollinger_prompts,)
        for generic_set in generic_sets:
            if len(raw_prompts) == len(generic_set) and all(
                isinstance(prompt, dict)
                and str(prompt.get("label") or "").strip().rstrip(".") == default["label"]
                and str(prompt.get("text") or "").strip() == default["text"]
                for prompt, default in zip(raw_prompts, generic_set, strict=False)
            ):
                matches_generic_defaults = True
                break
    if missing_prompts:
        result["prompts"] = deepcopy(default_prompts)

    title = str(result.get("title") or "").strip()
    if title in default_title_values:
        result["title"] = "Your Trading Notebook"
    else:
        result["title"] = title

    if course_slug == "understand-bollinger-bands":
        if matches_generic_defaults:
            result["prompts"] = [
                {
                    "label": "Describe",
                    "text": "Where is price relative to the bands and middle line?",
                },
                {
                    "label": "Interpret",
                    "text": "Does the structure look like a range, a trend or a transition? What is your alternative explanation?",
                },
                {"label": "Apply", "text": "What would change your view?"},
            ]
    elif matches_generic_defaults:
        result["prompts"] = deepcopy(default_prompts)
    return result


_DEFAULT_REFLECTION = {
    "prompt": "Before opening the model reasoning, write one observable fact, one possible interpretation, and one thing that would change your view.",
    "model_reasoning": "A careful reading separates visible evidence from interpretation, considers a reasonable alternative, and names the evidence that would strengthen or weaken the interpretation.",
    "chart_notes": "",
}


def _reflection_for_display(raw_reflection):
    """Expose learner-safe reflective guidance, with defaults only for legacy lessons."""
    if not isinstance(raw_reflection, dict) or "prompt" not in raw_reflection:
        return dict(_DEFAULT_REFLECTION)
    return {
        "prompt": str(raw_reflection.get("prompt") or "").strip()[:1000],
        "model_reasoning": str(raw_reflection.get("model_reasoning") or "").strip()[:3000],
        "chart_notes": str(raw_reflection.get("chart_notes") or "").strip()[:3000],
    }


def _render_course_description(source, user=None, admin_preview=False):
    """Render a course overview description as safe, semantic Markdown HTML."""
    from django.utils.html import escape

    text = source if isinstance(source, str) else str(source or "")
    if not text.strip():
        return ""
    try:
        return render_safe_markdown(
            text,
            user=user,
            admin_preview=admin_preview,
            module_label="Course overview",
        )
    except ValidationError:
        # Keep rejected legacy markup readable as escaped text rather than passing
        # it through to the page without sanitisation.
        return "<p>" + escape(text).replace("\n", "<br>") + "</p>"


def _active_entitlements(user, at=None):
    at = at or timezone.now()
    return CourseEntitlement.objects.filter(
        user=user,
        status=CourseEntitlement.Status.ACTIVE,
        starts_at__lte=at,
    ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=at))


@login_required
def academy_home(request):
    """Member landing page: purchased courses, progress, and available offers."""
    from .services import has_active_plan_access

    entitlements = list(_active_entitlements(request.user).select_related("course"))
    entitlements_by_course = {ent.course_id: ent for ent in entitlements}
    courses_by_id = {
        course.pk: course for course in Course.objects.filter(status=Course.Status.PUBLISHED)
    }
    for entitlement in entitlements:
        courses_by_id.setdefault(entitlement.course_id, entitlement.course)

    course_cards = []
    for course in sorted(courses_by_id.values(), key=lambda c: (c.position, c.title.casefold())):
        entitlement = entitlements_by_course.get(course.pk)
        visible_lesson_ids = list(
            Lesson.objects.filter(
                module__course=course,
                module__is_published=True,
                is_published=True,
            ).values_list("pk", flat=True)
        )
        total = len(visible_lesson_ids)
        done = LessonProgress.objects.filter(
            user=request.user,
            lesson_id__in=visible_lesson_ids,
            status=LessonProgress.Status.COMPLETED,
        ).count()
        course_cards.append(
            {
                "course": course,
                "entitlement": entitlement,
                "has_access": bool(entitlement or has_active_plan_access(request.user, course)),
                "total_lessons": total,
                "completed_lessons": done,
                "progress_percent": round(done * 100 / total) if total else 0,
                "resume_lesson": get_resume_lesson(request.user, course),
            }
        )

    offers = (
        CourseOffer.objects.filter(
            is_active=True,
            course__status=Course.Status.PUBLISHED,
            course__access_type__in=[Course.AccessType.PAID, Course.AccessType.MIXED],
            plan__is_active=True,
        )
        .select_related("course", "plan")
        .order_by("position", "name")
    )
    offers = [
        offer
        for offer in offers
        if offer.is_saleable
        and offer.course_id not in entitlements_by_course
        and (
            offer.course.access_type != Course.AccessType.MIXED
            or not has_active_plan_access(request.user, offer.course)
        )
    ]
    return render(
        request,
        "academy/home.html",
        {
            "course_cards": course_cards,
            "offers": offers,
        },
    )


@login_required
def course_detail(request, course_slug):
    from .services import get_active_plan_subscription, get_free_membership_plan_for_course

    course = get_object_or_404(Course, slug=course_slug)
    entitlement = get_active_entitlement(request.user, course)
    membership_subscription = (
        get_active_plan_subscription(request.user, course)
        if course.access_type in (Course.AccessType.MEMBERSHIP, Course.AccessType.MIXED)
        else None
    )
    has_course_access = bool(entitlement or membership_subscription)
    free_membership_mapping = (
        get_free_membership_plan_for_course(course)
        if course.access_type in (Course.AccessType.MEMBERSHIP, Course.AccessType.MIXED)
        else None
    )
    free_membership_plan = free_membership_mapping.plan if free_membership_mapping else None
    can_enrol_free = (
        course.status == Course.Status.PUBLISHED
        and course.access_type == Course.AccessType.FREE
        and not has_course_access
    )
    if (
        course.status != Course.Status.PUBLISHED
        and entitlement is None
        and membership_subscription is None
    ):
        from django.http import Http404

        raise Http404

    lesson_queryset = Lesson.objects.filter(is_published=True).order_by("position", "title")
    modules = (
        CourseModule.objects.filter(course=course, is_published=True)
        .order_by("position", "title")
        .prefetch_related(Prefetch("lessons", queryset=lesson_queryset))
    )
    lesson_ids = [lesson.pk for module in modules for lesson in module.lessons.all()]
    progress_by_lesson = {
        p.lesson_id: p
        for p in LessonProgress.objects.filter(user=request.user, lesson_id__in=lesson_ids)
    }
    module_rows = []
    now = timezone.now()
    access_record = entitlement or membership_subscription
    for module in modules:
        rows = []
        for lesson in module.lessons.all():
            allowed = can_access_lesson(request.user, lesson, now)
            release_at = lesson_release_at(access_record, lesson) if access_record else None
            rows.append(
                {
                    "lesson": lesson,
                    "accessible": allowed,
                    "progress": progress_by_lesson.get(lesson.pk),
                    "release_at": release_at,
                }
            )
        if rows:
            module_rows.append({"module": module, "lessons": rows})

    first_accessible_lesson = next(
        (item["lesson"] for row in module_rows for item in row["lessons"] if item["accessible"]),
        None,
    )
    total_study_minutes = sum(
        item["lesson"].duration_minutes for row in module_rows for item in row["lessons"]
    )
    offer = (
        CourseOffer.objects.filter(
            course=course,
            is_active=True,
            course__access_type__in=[Course.AccessType.PAID, Course.AccessType.MIXED],
            plan__is_active=True,
        )
        .select_related("plan", "course")
        .first()
    )
    if offer is not None and not offer.is_saleable:
        offer = None
    offer_price_display = ""
    if offer is not None:
        resolved_price = resolved_course_offer_price(offer, request)
        if resolved_price:
            offer_price_display = resolved_price[0]
        else:
            offer = None
    visible_lesson_ids = Lesson.objects.filter(
        module__course=course,
        module__is_published=True,
        is_published=True,
    ).values_list("pk", flat=True)
    completed = LessonProgress.objects.filter(
        user=request.user,
        lesson_id__in=visible_lesson_ids,
        status=LessonProgress.Status.COMPLETED,
    ).count()
    total = Lesson.objects.filter(
        module__course=course, module__is_published=True, is_published=True
    ).count()
    return render(
        request,
        "academy/course_detail.html",
        {
            "course": course,
            "course_description_html": _render_course_description(
                course.description, user=request.user
            ),
            "entitlement": entitlement,
            "has_course_access": has_course_access,
            "can_enrol_free": can_enrol_free,
            "free_membership_plan": free_membership_plan,
            "offer": offer,
            "offer_price_display": offer_price_display,
            "module_rows": module_rows,
            "completed_lessons": completed,
            "total_lessons": total,
            "total_modules": len(module_rows),
            "total_study_minutes": total_study_minutes,
            "total_study_hours": total_study_minutes // 60,
            "total_study_minutes_remainder": total_study_minutes % 60,
            "first_accessible_lesson": first_accessible_lesson,
            "is_course_content_admin": is_course_content_admin(request.user),
            "progress_percent": round(completed * 100 / total) if total else 0,
        },
    )


def _public_free_membership_plan():
    """Return TradeThesis Free only when all active base and regional prices are zero."""
    from apps.subscriptions.models import FREE_MEMBERSHIP_PRODUCT_SLUG, Plan, PlanPrice

    candidates = (
        Plan.objects.filter(
            product__slug=FREE_MEMBERSHIP_PRODUCT_SLUG,
            product__is_active=True,
            tier=Plan.Tier.FREE,
            is_trial=False,
            is_active=True,
            is_hidden=False,
            academy_course_access__is_active=True,
            academy_course_access__course__status=Course.Status.PUBLISHED,
            academy_course_access__course__access_type__in=[
                Course.AccessType.MEMBERSHIP,
                Course.AccessType.MIXED,
            ],
            prices__interval=PlanPrice.Interval.MONTHLY,
            prices__is_active=True,
            prices__price_cents=0,
        )
        .select_related("product")
        .distinct()
        .order_by("display_order", "name")
    )
    for plan in candidates:
        if plan.prices.filter(is_active=True).exclude(price_cents=0).exists():
            continue
        if plan.geo_prices.filter(is_active=True).exclude(price_cents=0).exists():
            continue
        return plan
    return None


@login_required
@require_POST
def enrol_free_course(request, course_slug):
    """Enrol a signed-in learner in a published course explicitly marked Free."""
    from .services import enrol_in_free_course

    course = get_object_or_404(Course, slug=course_slug, status=Course.Status.PUBLISHED)
    enrol_in_free_course(user=request.user, course=course)
    return redirect("academy:course-detail", course_slug=course.slug)


@login_required
@require_POST
def join_free_membership_for_course(request, course_slug):
    """Join TradeThesis Free from a course included in that membership."""
    from apps.subscriptions.services import join_free_membership

    from .services import get_free_membership_plan_for_course

    course = get_object_or_404(Course, slug=course_slug, status=Course.Status.PUBLISHED)
    if course.access_type not in (Course.AccessType.MEMBERSHIP, Course.AccessType.MIXED):
        raise PermissionDenied("This course is not offered through TradeThesis Free.")
    mapping = get_free_membership_plan_for_course(course)
    if mapping is None:
        raise PermissionDenied("TradeThesis Free is not currently configured for this course.")
    join_free_membership(request.user, mapping.plan, request)
    return redirect("academy:course-detail", course_slug=course.slug)


def free_membership_landing(request):
    """Public, no-payment landing page for the TradeThesis Free funnel."""
    plan = _public_free_membership_plan()
    courses = (
        Course.objects.filter(
            plan_access__plan=plan,
            plan_access__is_active=True,
            status=Course.Status.PUBLISHED,
        ).order_by("position", "title")
        if plan
        else Course.objects.none()
    )
    signup_url = (
        f"{reverse('account_signup')}?next={quote(reverse('academy:free-membership'), safe='/')}"
    )
    return render(
        request,
        "academy/free_membership.html",
        {"plan": plan, "courses": courses, "signup_url": signup_url},
    )


@login_required
@require_POST
def join_free_membership_from_landing(request):
    """Join TradeThesis Free from its public landing page."""
    from apps.subscriptions.services import join_free_membership

    plan = _public_free_membership_plan()
    if plan is None:
        raise PermissionDenied("TradeThesis Free is not currently available.")
    join_free_membership(request.user, plan, request)
    return redirect("academy:home")


@never_cache
@login_required
def lesson_detail(request, course_slug, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        module__course__slug=course_slug,
        is_published=True,
        module__is_published=True,
    )
    course = lesson.module.course
    if not can_access_lesson(request.user, lesson):
        raise PermissionDenied("You do not have access to this lesson yet.")
    entitlement = get_active_entitlement(request.user, course)
    # A successful lesson visit establishes an in-progress resume point. The
    # service preserves completed status on revisits and rechecks access.
    progress = update_lesson_progress(
        user=request.user,
        lesson=lesson,
        status=LessonProgress.Status.IN_PROGRESS,
    )
    content_json = lesson.content_json if isinstance(lesson.content_json, dict) else {}
    asset_ids = content_json.get("asset_ids", [])
    regional_asset_ids = regional_block_asset_ids(content_json) | regional_lesson_content_asset_ids(
        content_json
    )
    media_assets = CourseMediaAsset.objects.filter(course=course, pk__in=asset_ids)
    asset_urls = {}
    for asset in media_assets:
        if asset.file:
            asset_urls[str(asset.pk)] = reverse("academy:media-asset", args=[asset.pk])
        elif str(asset.pk).lower() not in regional_asset_ids and asset.original_url.startswith(
            ("https://", "http://")
        ):
            # External URLs cannot enforce regional access. Regional images must
            # use managed storage before they can be submitted for review.
            asset_urls[str(asset.pk)] = asset.original_url
    outline_modules = []
    modules = (
        CourseModule.objects.filter(course=course)
        .prefetch_related("lessons")
        .order_by("position", "title")
    )
    now = timezone.now()
    for module_row in modules:
        rows = []
        for outline_lesson in module_row.lessons.all():
            if not outline_lesson.is_published:
                continue
            rows.append(
                {
                    "lesson": outline_lesson,
                    "accessible": can_access_lesson(request.user, outline_lesson, now),
                    "current": outline_lesson.pk == lesson.pk,
                    "progress": LessonProgress.objects.filter(
                        user=request.user, lesson=outline_lesson
                    ).first(),
                }
            )
        if rows and module_row.is_published:
            outline_modules.append({"module": module_row, "lessons": rows})
    notebook = _notebook_for_course_display(
        course.slug,
        lesson.content_json.get("notebook", {}) if isinstance(lesson.content_json, dict) else {},
    )
    saved_responses = (
        progress.response_json.get("notebook_responses", [])
        if isinstance(progress.response_json, dict)
        else []
    )
    reflection_response = (
        str(progress.response_json.get("reflection_response") or "")[:4000]
        if isinstance(progress.response_json, dict)
        else ""
    )
    reflection = _reflection_for_display(
        lesson.content_json.get("reflection", {}) if isinstance(lesson.content_json, dict) else {}
    )
    if isinstance(notebook, dict) and isinstance(notebook.get("prompts"), list):
        for prompt_index, prompt in enumerate(notebook["prompts"]):
            if isinstance(prompt, dict):
                prompt["response"] = (
                    saved_responses[prompt_index]
                    if isinstance(saved_responses, list) and prompt_index < len(saved_responses)
                    else ""
                )
    protected_video = ProtectedLessonVideo.objects.filter(
        lesson=lesson,
        status=ProtectedLessonVideo.Status.READY,
    ).first()
    video_url = (
        lesson.content_json.get("video_url", "") if isinstance(lesson.content_json, dict) else ""
    )
    video_url = (
        video_url
        if (
            not protected_video
            and settings.ACADEMY_ALLOW_LEGACY_VIDEO_URLS
            and isinstance(video_url, str)
            and video_url.startswith(("https://", "http://"))
        )
        else ""
    )
    video_is_file = video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))
    video_watermark_name = request.user.full_name.strip() or request.user.email
    practice_questions = (
        lesson.content_json.get("questions", []) if isinstance(lesson.content_json, dict) else []
    )
    practice_questions = _practice_questions_with_images(
        practice_questions,
        asset_urls,
        lesson.content_json.get("figures", {}) if isinstance(lesson.content_json, dict) else {},
    )
    related_ids = (
        lesson.content_json.get("related_course_ids", [])
        if isinstance(lesson.content_json, dict)
        else []
    )
    related_ids = [
        value
        for value in related_ids
        if isinstance(value, str) and len(value) == 36 and value.count("-") == 4
    ]
    related_courses = [
        related
        for related in Course.objects.filter(
            pk__in=related_ids,
            status=Course.Status.PUBLISHED,
        )
        .exclude(pk=course.pk)
        .order_by("position", "title")
        if is_course_card_recommendable(related.title, related.summary, related.description)
    ]
    for related in related_courses:
        related.topic_tags = course_topic_tags(related.learning_outcomes)
    ordered_lessons = list(
        Lesson.objects.filter(
            module__course=course,
            module__is_published=True,
            is_published=True,
        )
        .select_related("module")
        .order_by("module__position", "position", "title")
    )
    accessible_lessons = [
        item for item in ordered_lessons if can_access_lesson(request.user, item, now)
    ]
    current_index = next(
        (i for i, item in enumerate(accessible_lessons) if item.pk == lesson.pk), -1
    )
    previous_lesson = accessible_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = (
        accessible_lessons[current_index + 1]
        if 0 <= current_index < len(accessible_lessons) - 1
        else None
    )
    total_lessons = len(ordered_lessons)
    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson_id__in=[item.pk for item in ordered_lessons],
        status=LessonProgress.Status.COMPLETED,
    ).count()
    course_progress_percent = round(completed_lessons * 100 / total_lessons) if total_lessons else 0
    regional_country, regional_region = _regional_audience(request)
    return render(
        request,
        "academy/lesson.html",
        {
            "course": course,
            "lesson": lesson,
            "module": lesson.module,
            "module_display_title": _module_display_title(lesson.module.title),
            "entitlement": entitlement,
            "progress": progress,
            "lesson_sections": build_lesson_sections(
                lesson.content_markdown,
                asset_urls,
                user=request.user,
                figure_metadata=(
                    lesson.content_json.get("figures", {})
                    if isinstance(lesson.content_json, dict)
                    else {}
                ),
                table_metadata=(
                    lesson.content_json.get("tables", {})
                    if isinstance(lesson.content_json, dict)
                    else {}
                ),
                figure_prefix=f"{lesson.module.position}.{lesson.position}",
                module_label=f"Module {lesson.module.position} · {lesson.module.title}",
                course_title=course.title,
                regional_blocks=content_json.get("regional_blocks", {}),
                regional_content=content_json.get("regional_lesson_content", {}),
                country_code=regional_country,
                region_code=regional_region,
            ),
            "notebook": notebook,
            "notebook_responses": saved_responses,
            "reflection": reflection,
            "reflection_response": reflection_response,
            "outline_modules": outline_modules,
            "related_courses": related_courses,
            "practice_questions": practice_questions,
            "video_url": video_url,
            "video_is_file": video_is_file,
            "protected_video": protected_video,
            "protected_video_manifest_url": (
                reverse("academy:protected-video-manifest", args=[protected_video.pk])
                if protected_video
                else ""
            ),
            "video_watermark_name": video_watermark_name,
            "video_watermark_email": request.user.email,
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
            "course_progress_percent": course_progress_percent,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
        },
    )


@never_cache
@login_required
def admin_lesson_preview(request, course_slug, lesson_id):
    """Show a real locked lesson to course admins without altering learner state."""
    if not is_course_content_admin(request.user):
        raise PermissionDenied("Administrator course-content access is required.")

    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        module__course__slug=course_slug,
    )
    course = lesson.module.course
    entitlement = get_active_entitlement(request.user, course)
    content_json = lesson.content_json if isinstance(lesson.content_json, dict) else {}
    asset_ids = content_json.get("asset_ids", [])
    if not isinstance(asset_ids, list):
        asset_ids = []
    media_assets = CourseMediaAsset.objects.filter(course=course, pk__in=asset_ids)
    asset_urls = {}
    for asset in media_assets:
        if asset.file:
            asset_urls[str(asset.pk)] = reverse("academy:media-asset", args=[asset.pk])
        elif isinstance(asset.original_url, str) and asset.original_url.startswith(
            ("https://", "http://")
        ):
            asset_urls[str(asset.pk)] = asset.original_url

    now = timezone.now()
    modules = (
        CourseModule.objects.filter(course=course)
        .prefetch_related(
            Prefetch(
                "lessons",
                queryset=Lesson.objects.order_by("position", "title"),
            )
        )
        .order_by("position", "title")
    )
    outline_modules = []
    ordered_lessons = []
    for module_row in modules:
        rows = []
        for outline_lesson in module_row.lessons.all():
            ordered_lessons.append(outline_lesson)
            rows.append(
                {
                    "lesson": outline_lesson,
                    "accessible": can_access_lesson(request.user, outline_lesson, now),
                    "current": outline_lesson.pk == lesson.pk,
                    "progress": None,
                    "admin_preview_url": reverse(
                        "academy:admin-lesson-preview",
                        args=[course.slug, outline_lesson.pk],
                    ),
                }
            )
        if rows:
            outline_modules.append({"module": module_row, "lessons": rows})

    current_index = next(
        (index for index, item in enumerate(ordered_lessons) if item.pk == lesson.pk),
        -1,
    )
    previous_lesson = ordered_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = (
        ordered_lessons[current_index + 1]
        if 0 <= current_index < len(ordered_lessons) - 1
        else None
    )
    notebook = _notebook_for_course_display(course.slug, content_json.get("notebook", {}))
    if not isinstance(notebook, dict):
        notebook = {}
    practice_questions = _practice_questions_with_images(
        content_json.get("questions", []),
        asset_urls,
        content_json.get("figures", {}),
    )
    protected_video = ProtectedLessonVideo.objects.filter(
        lesson=lesson,
        status=ProtectedLessonVideo.Status.READY,
    ).first()
    video_url = content_json.get("video_url", "")
    if protected_video or not isinstance(video_url, str) or not video_url.startswith(
        ("https://", "http://")
    ):
        video_url = ""
    video_is_file = video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))
    video_watermark_name = request.user.full_name.strip() or request.user.email
    protected_video_manifest_url = (
        reverse("academy:protected-video-manifest", args=[protected_video.pk])
        if protected_video
        else ""
    )
    regional_country, regional_region = _regional_audience(request, admin_preview=True)

    return render(
        request,
        "academy/lesson.html",
        {
            "course": course,
            "lesson": lesson,
            "module": lesson.module,
            "module_display_title": _module_display_title(lesson.module.title),
            "entitlement": entitlement,
            "progress": None,
            "admin_preview": True,
            "lesson_sections": build_lesson_sections(
                lesson.content_markdown,
                asset_urls,
                user=request.user,
                admin_preview=True,
                figure_metadata=content_json.get("figures", {}),
                table_metadata=content_json.get("tables", {}),
                figure_prefix=f"{lesson.module.position}.{lesson.position}",
                module_label=f"Module {lesson.module.position} · {lesson.module.title}",
                course_title=course.title,
                regional_blocks=content_json.get("regional_blocks", {}),
                regional_content=content_json.get("regional_lesson_content", {}),
                country_code=regional_country,
                region_code=regional_region,
            ),
            "notebook": notebook,
            "notebook_responses": [],
            "reflection": _reflection_for_display(
                content_json.get("reflection", {}) if isinstance(content_json, dict) else {}
            ),
            "reflection_response": "",
            "outline_modules": outline_modules,
            "related_courses": Course.objects.none(),
            "practice_questions": practice_questions,
            "video_url": video_url,
            "video_is_file": video_is_file,
            "protected_video": protected_video,
            "protected_video_manifest_url": protected_video_manifest_url,
            "video_watermark_name": video_watermark_name,
            "video_watermark_email": request.user.email,
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
            "course_progress_percent": 0,
            "completed_lessons": 0,
            "total_lessons": len(ordered_lessons),
        },
    )


@xframe_options_sameorigin
@never_cache
@login_required
def course_import_website_preview(request, import_id):
    """Render an unpublished CourseImport in the real Academy shell for admins only."""
    if not is_course_content_admin(request.user):
        raise PermissionDenied("Administrator course-content access is required.")

    record = get_object_or_404(CourseImport, pk=import_id)
    payload = record.payload if isinstance(record.payload, dict) else {}
    course = payload.get("course") if isinstance(payload.get("course"), dict) else {}
    modules = payload.get("modules") if isinstance(payload.get("modules"), list) else []
    raw_assets = list(record.assets.all())
    live_assets = {
        str(asset.pk): asset
        for asset in CourseMediaAsset.objects.filter(
            pk__in=[item.stable_asset_id for item in raw_assets]
        )
    }
    asset_urls = {}
    for asset in raw_assets:
        live_asset = live_assets.get(str(asset.stable_asset_id))
        review_asset_url = reverse(
            "admin:academy_courseimport_asset",
            args=[record.pk, asset.stable_asset_id],
        )
        if asset.file or asset.source_path or (live_asset and live_asset.file):
            asset_urls[str(asset.stable_asset_id)] = review_asset_url
        elif asset.original_url.startswith(("https://", "http://")):
            asset_urls[str(asset.stable_asset_id)] = asset.original_url
        elif live_asset and live_asset.original_url.startswith(("https://", "http://")):
            asset_urls[str(asset.stable_asset_id)] = live_asset.original_url

    overview_base_url = reverse("academy:course-import-preview", args=[record.pk])
    requested_audience = str(
        request.GET.get("preview_audience") or request.GET.get("preview_country") or ""
    ).strip()
    overview_url = overview_base_url
    if requested_audience:
        overview_url += "?preview_audience=" + quote(requested_audience, safe="")
    admin_review_url = reverse("admin:academy_courseimport_review", args=[record.pk])
    preview_modules = []
    selected_lesson = None
    selected_module = None
    requested_source_id = str(request.GET.get("lesson", "")).strip()
    total_lessons = 0
    total_study_minutes = 0
    first_preview_url = overview_url

    for module_data in modules:
        if not isinstance(module_data, dict):
            continue
        lessons_data = module_data.get("lessons", [])
        if not isinstance(lessons_data, list):
            lessons_data = []
        lesson_rows = []
        for lesson_data in lessons_data:
            if not isinstance(lesson_data, dict):
                continue
            source_id = str(lesson_data.get("source_id", "")).strip()
            lesson_url = overview_url
            if source_id:
                lesson_url = overview_base_url + "?lesson=" + quote(source_id, safe="")
                if requested_audience:
                    lesson_url += "&preview_audience=" + quote(requested_audience, safe="")
            row = {
                "lesson": lesson_data,
                "preview_url": lesson_url,
                "current": bool(source_id and source_id == requested_source_id),
            }
            lesson_rows.append(row)
            total_lessons += 1
            with suppress(TypeError, ValueError):
                total_study_minutes += max(0, int(lesson_data.get("duration_minutes", 0)))
            if total_lessons == 1 and source_id:
                first_preview_url = lesson_url
            if row["current"]:
                selected_lesson = lesson_data
                selected_module = module_data
        if lesson_rows:
            preview_modules.append({"module": module_data, "lessons": lesson_rows})

    selected_sections = None
    selected_notebook = {}
    selected_reflection = dict(_DEFAULT_REFLECTION)
    selected_practice_questions = []
    selected_video_url = ""
    selected_video_is_file = False
    selected_related_courses = Course.objects.none()
    if selected_lesson is not None:
        selected_content_json = selected_lesson.get("content_json", {})
        if not isinstance(selected_content_json, dict):
            selected_content_json = {}
        regional_country, regional_region = _regional_audience(request, admin_preview=True)
        selected_sections = build_lesson_sections(
            selected_lesson.get("content_markdown", ""),
            asset_urls,
            user=request.user,
            admin_preview=True,
            regional_blocks=selected_content_json.get("regional_blocks", {}),
            regional_content=selected_content_json.get("regional_lesson_content", {}),
            country_code=regional_country,
            region_code=regional_region,
            figure_metadata=selected_content_json.get("figures", {}),
            table_metadata=selected_content_json.get("tables", {}),
            figure_prefix=str(selected_lesson.get("source_id", "")),
            module_label=f"Module {selected_module.get('position', '')} · {selected_module.get('title', '')}",
            course_title=str(course.get("title") or record.title),
        )
        content_json = selected_lesson.get("content_json", {})
        if not isinstance(content_json, dict):
            content_json = {}
        selected_notebook = _notebook_for_course_display(
            str(course.get("slug") or ""),
            content_json.get("notebook") or payload.get("notebook", {}),
        )
        if not isinstance(selected_notebook, dict):
            selected_notebook = {}
        selected_reflection = _reflection_for_display(content_json.get("reflection", {}))
        selected_practice_questions = _practice_questions_with_images(
            content_json.get("questions", []),
            asset_urls,
            content_json.get("figures", {}),
        )

        raw_related_ids = content_json.get("related_course_ids", [])
        related_ids = []
        if isinstance(raw_related_ids, list):
            for raw_id in raw_related_ids[:20]:
                if isinstance(raw_id, str):
                    with suppress(ValueError, TypeError, AttributeError):
                        related_ids.append(UUID(raw_id))
        if related_ids:
            selected_related_courses = [
                related
                for related in Course.objects.filter(
                    pk__in=related_ids,
                    status=Course.Status.PUBLISHED,
                )
                .exclude(pk=record.target_course_id)
                .order_by("position", "title")
                if is_course_card_recommendable(related.title, related.summary, related.description)
            ]
            for related in selected_related_courses:
                related.topic_tags = course_topic_tags(related.learning_outcomes)

        # Match the learner lesson view: render only ordinary HTTP(S) video
        # destinations, and use the native player only for supported file types.
        raw_video_url = content_json.get("video_url", "")
        if isinstance(raw_video_url, str):
            raw_video_url = raw_video_url.strip()
            if raw_video_url.startswith(("https://", "http://")):
                selected_video_url = raw_video_url
                selected_video_is_file = (
                    raw_video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))
                )

    return render(
        request,
        "academy/course_import_website_preview.html",
        {
            "import_record": record,
            "course": course,
            "course_description_html": _render_course_description(
                course.get("description", ""),
                user=request.user,
                admin_preview=True,
            ),
            "preview_modules": preview_modules,
            "total_modules": len(preview_modules),
            "total_lessons": total_lessons,
            "total_study_minutes": total_study_minutes,
            "total_study_hours": total_study_minutes // 60,
            "total_study_minutes_remainder": total_study_minutes % 60,
            "overview_url": overview_url,
            "first_preview_url": first_preview_url,
            "admin_review_url": admin_review_url,
            "selected_lesson": selected_lesson,
            "selected_module": selected_module,
            "selected_module_display_title": _module_display_title(
                selected_module.get("title") if selected_module else ""
            ),
            "selected_sections": selected_sections,
            "selected_notebook": selected_notebook,
            "selected_reflection": selected_reflection,
            "selected_reflection_response": "",
            "selected_practice_questions": selected_practice_questions,
            "selected_video_url": selected_video_url,
            "selected_video_is_file": selected_video_is_file,
            "selected_related_courses": selected_related_courses,
        },
    )


@login_required
@require_POST
def lesson_quiz_submit(request, lesson_id):
    """Grade practice questions server-side; answer keys never enter the learner page."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
    )
    if not can_access_lesson(request.user, lesson):
        raise PermissionDenied("You do not have access to this lesson yet.")
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    if not isinstance(answers, dict):
        return JsonResponse(
            {"detail": "Answers must be an object keyed by question ID."}, status=400
        )
    material = LessonInstructorMaterial.objects.filter(lesson=lesson).first()
    questions = (
        material.rubric_json.get("questions", [])
        if material and isinstance(material.rubric_json, dict)
        else []
    )
    if not questions:
        return JsonResponse(
            {"detail": "Practice questions are not configured for this lesson."}, status=404
        )

    results = []
    score = 0
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            continue
        question_id = str(question.get("id") or f"question-{index + 1}")
        options = question.get("options", [])
        try:
            selected = int(answers.get(question_id, -1))
            correct_index = int(question.get("correctIndex", -2))
        except (TypeError, ValueError):
            selected, correct_index = -1, -2
        correct = 0 <= selected < len(options) and selected == correct_index
        if correct:
            score += 1
        results.append(
            {
                "id": question_id,
                "correct": correct,
                # Reveal option indexes only after the learner submits an attempt.
                "selected_index": selected if 0 <= selected < len(options) else None,
                "correct_index": correct_index if 0 <= correct_index < len(options) else None,
                "explanation": str(question.get("explanation", ""))[:3000],
            }
        )
    existing_progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    saved_response = (
        dict(existing_progress.response_json or {})
        if existing_progress and isinstance(existing_progress.response_json, dict)
        else {}
    )
    saved_response.update(
        {"quiz_answers": answers, "quiz_score": score, "quiz_total": len(results)}
    )
    update_lesson_progress(
        user=request.user,
        lesson=lesson,
        response_json=saved_response,
    )
    return JsonResponse({"ok": True, "score": score, "total": len(results), "results": results})


@login_required
@require_POST
def lesson_reflection_submit(request, lesson_id):
    """Persist a learner's first reading without changing protected instructor material."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
    )
    if not can_access_lesson(request.user, lesson):
        raise PermissionDenied("You do not have access to this lesson yet.")
    content_json = lesson.content_json if isinstance(lesson.content_json, dict) else {}
    reflection = _reflection_for_display(content_json.get("reflection", {}))
    if not reflection.get("prompt"):
        return JsonResponse(
            {"detail": "A reflection exercise is not configured for this lesson."}, status=404
        )
    response_text = str(request.POST.get("reflection_response") or "").strip()[:4000]
    existing_progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    saved_response = (
        dict(existing_progress.response_json or {})
        if existing_progress and isinstance(existing_progress.response_json, dict)
        else {}
    )
    saved_response["reflection_response"] = response_text
    update_lesson_progress(user=request.user, lesson=lesson, response_json=saved_response)
    return JsonResponse({"ok": True, "saved": True})


@login_required
@require_POST
def lesson_notebook_submit(request, lesson_id):
    """Persist learner reflections without exposing or altering instructor materials."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
    )
    if not can_access_lesson(request.user, lesson):
        raise PermissionDenied("You do not have access to this lesson yet.")
    notebook = _notebook_for_course_display(
        lesson.module.course.slug,
        lesson.content_json.get("notebook", {}) if isinstance(lesson.content_json, dict) else {},
    )
    prompts = notebook.get("prompts", []) if isinstance(notebook, dict) else []
    responses = []
    for index, _prompt in enumerate(prompts[:6]):
        responses.append(str(request.POST.get(f"prompt_{index}", "")).strip()[:4000])
    existing_progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    saved_response = (
        dict(existing_progress.response_json or {})
        if existing_progress and isinstance(existing_progress.response_json, dict)
        else {}
    )
    saved_response["notebook_responses"] = responses
    update_lesson_progress(user=request.user, lesson=lesson, response_json=saved_response)
    return JsonResponse({"ok": True, "saved": True})


@login_required
def media_asset(request, asset_id):
    """Deliver images only when an accessible lesson uses them for this audience."""
    asset = get_object_or_404(CourseMediaAsset.objects.select_related("course"), pk=asset_id)
    if not asset.file:
        from django.http import Http404

        raise Http404
    allowed = is_course_content_admin(request.user)
    if not allowed:
        country_code, region_code = _regional_audience(request)
        target_asset_id = str(asset.pk).lower()
        for related_lesson in Lesson.objects.filter(
            module__course=asset.course,
            module__is_published=True,
            is_published=True,
        ).select_related("module__course"):
            if not can_access_lesson(request.user, related_lesson):
                continue
            permitted_asset_ids = _lesson_asset_ids_for_audience(
                related_lesson,
                country_code=country_code,
                region_code=region_code,
            )
            if target_asset_id in permitted_asset_ids:
                allowed = True
                break
    if not allowed:
        raise PermissionDenied(
            "You do not have access to this course image for your content audience."
        )
    response = FileResponse(
        asset.file.open("rb"),
        content_type=mimetypes.guess_type(asset.file.name)[0] or "application/octet-stream",
    )
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@require_POST
def lesson_progress(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related("module__course"), pk=lesson_id)
    raw_response = request.POST.get("response_json", "")
    response_json = None
    if raw_response:
        try:
            response_json = json.loads(raw_response)
        except (TypeError, ValueError):
            return JsonResponse({"detail": "response_json must contain valid JSON."}, status=400)
    try:
        seconds_delta = int(request.POST.get("seconds_delta", "0"))
        progress = update_lesson_progress(
            user=request.user,
            lesson=lesson,
            status=request.POST.get("status") or None,
            response_json=response_json,
            seconds_delta=seconds_delta,
        )
    except PermissionDenied as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except (ValidationError, ValueError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse(
        {
            "ok": True,
            "status": progress.status,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "time_spent_seconds": progress.time_spent_seconds,
        }
    )
