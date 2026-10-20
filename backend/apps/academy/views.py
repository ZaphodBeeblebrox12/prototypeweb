"""Authenticated learner views for TradeThesis Academy."""
import json
import mimetypes

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch, Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .content_rendering import build_lesson_sections
from .models import (
    Course,
    CourseEntitlement,
    CourseMediaAsset,
    CourseModule,
    CourseOffer,
    Lesson,
    LessonInstructorMaterial,
    LessonProgress,
)
from .permissions import is_course_content_admin
from .services import (
    can_access_lesson,
    get_active_entitlement,
    get_resume_lesson,
    lesson_release_at,
    update_lesson_progress,
)


def _active_entitlements(user, at=None):
    at = at or timezone.now()
    return (CourseEntitlement.objects.filter(
        user=user, status=CourseEntitlement.Status.ACTIVE, starts_at__lte=at,
    ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=at)))


@login_required
def academy_home(request):
    """Member landing page: purchased courses, progress, and available offers."""
    entitlements = list(_active_entitlements(request.user).select_related("course"))
    entitlements_by_course = {ent.course_id: ent for ent in entitlements}
    courses_by_id = {course.pk: course for course in Course.objects.filter(status=Course.Status.PUBLISHED)}
    for entitlement in entitlements:
        courses_by_id.setdefault(entitlement.course_id, entitlement.course)

    course_cards = []
    for course in sorted(courses_by_id.values(), key=lambda c: (c.position, c.title.casefold())):
        entitlement = entitlements_by_course.get(course.pk)
        visible_lesson_ids = list(Lesson.objects.filter(
            module__course=course, module__is_published=True, is_published=True,
        ).values_list("pk", flat=True))
        total = len(visible_lesson_ids)
        done = LessonProgress.objects.filter(
            user=request.user, lesson_id__in=visible_lesson_ids,
            status=LessonProgress.Status.COMPLETED,
        ).count()
        course_cards.append({
            "course": course, "entitlement": entitlement,
            "total_lessons": total, "completed_lessons": done,
            "progress_percent": round(done * 100 / total) if total else 0,
            "resume_lesson": get_resume_lesson(request.user, course),
        })

    offers = CourseOffer.objects.filter(
        is_active=True, course__status=Course.Status.PUBLISHED,
        plan__is_active=True,
    ).select_related("course", "plan").order_by("position", "name")
    offers = [o for o in offers if o.is_saleable and o.course_id not in entitlements_by_course]
    return render(request, "academy/home.html", {
        "course_cards": course_cards, "offers": offers,
    })


@login_required
def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    entitlement = get_active_entitlement(request.user, course)
    if course.status != Course.Status.PUBLISHED and entitlement is None:
        from django.http import Http404
        raise Http404

    lesson_queryset = Lesson.objects.filter(is_published=True).order_by("position", "title")
    modules = CourseModule.objects.filter(course=course, is_published=True).order_by(
        "position", "title"
    ).prefetch_related(Prefetch("lessons", queryset=lesson_queryset))
    lesson_ids = [lesson.pk for module in modules for lesson in module.lessons.all()]
    progress_by_lesson = {
        p.lesson_id: p for p in LessonProgress.objects.filter(user=request.user, lesson_id__in=lesson_ids)
    }
    module_rows = []
    now = timezone.now()
    for module in modules:
        rows = []
        for lesson in module.lessons.all():
            allowed = can_access_lesson(request.user, lesson, now)
            release_at = lesson_release_at(entitlement, lesson) if entitlement else None
            rows.append({
                "lesson": lesson, "accessible": allowed,
                "progress": progress_by_lesson.get(lesson.pk),
                "release_at": release_at,
            })
        if rows:
            module_rows.append({"module": module, "lessons": rows})

    first_accessible_lesson = next(
        (
            item["lesson"]
            for row in module_rows
            for item in row["lessons"]
            if item["accessible"]
        ),
        None,
    )
    total_study_minutes = sum(
        item["lesson"].duration_minutes
        for row in module_rows
        for item in row["lessons"]
    )
    offer = CourseOffer.objects.filter(
        course=course, is_active=True, plan__is_active=True,
    ).select_related("plan", "course").first()
    if offer is not None and not offer.is_saleable:
        offer = None
    visible_lesson_ids = Lesson.objects.filter(
        module__course=course, module__is_published=True, is_published=True,
    ).values_list("pk", flat=True)
    completed = LessonProgress.objects.filter(
        user=request.user, lesson_id__in=visible_lesson_ids,
        status=LessonProgress.Status.COMPLETED,
    ).count()
    total = Lesson.objects.filter(module__course=course, module__is_published=True, is_published=True).count()
    return render(request, "academy/course_detail.html", {
        "course": course, "entitlement": entitlement, "offer": offer,
        "module_rows": module_rows, "completed_lessons": completed,
        "total_lessons": total,
        "total_modules": len(module_rows),
        "total_study_minutes": total_study_minutes,
        "total_study_hours": total_study_minutes // 60,
        "total_study_minutes_remainder": total_study_minutes % 60,
        "first_accessible_lesson": first_accessible_lesson,
        "progress_percent": round(completed * 100 / total) if total else 0,
    })


@login_required
def lesson_detail(request, course_slug, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id, module__course__slug=course_slug,
        is_published=True, module__is_published=True,
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
    asset_ids = lesson.content_json.get("asset_ids", []) if isinstance(lesson.content_json, dict) else []
    media_assets = CourseMediaAsset.objects.filter(course=course, pk__in=asset_ids)
    asset_urls = {}
    for asset in media_assets:
        if asset.file:
            asset_urls[str(asset.pk)] = reverse("academy:media-asset", args=[asset.pk])
        elif asset.original_url.startswith(("https://", "http://")):
            asset_urls[str(asset.pk)] = asset.original_url
    outline_modules = []
    modules = CourseModule.objects.filter(course=course).prefetch_related("lessons").order_by("position", "title")
    now = timezone.now()
    for module_row in modules:
        rows = []
        for outline_lesson in module_row.lessons.all():
            if not outline_lesson.is_published:
                continue
            rows.append({
                "lesson": outline_lesson,
                "accessible": can_access_lesson(request.user, outline_lesson, now),
                "current": outline_lesson.pk == lesson.pk,
                "progress": LessonProgress.objects.filter(user=request.user, lesson=outline_lesson).first(),
            })
        if rows and module_row.is_published:
            outline_modules.append({"module": module_row, "lessons": rows})
    notebook = lesson.content_json.get("notebook", {}) if isinstance(lesson.content_json, dict) else {}
    saved_responses = progress.response_json.get("notebook_responses", []) if isinstance(progress.response_json, dict) else []
    if isinstance(notebook, dict) and isinstance(notebook.get("prompts"), list):
        for prompt_index, prompt in enumerate(notebook["prompts"]):
            if isinstance(prompt, dict):
                prompt["response"] = saved_responses[prompt_index] if isinstance(saved_responses, list) and prompt_index < len(saved_responses) else ""
    video_url = lesson.content_json.get("video_url", "") if isinstance(lesson.content_json, dict) else ""
    video_url = video_url if isinstance(video_url, str) and video_url.startswith(("https://", "http://")) else ""
    video_is_file = video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))
    practice_questions = lesson.content_json.get("questions", []) if isinstance(lesson.content_json, dict) else []
    if not isinstance(practice_questions, list):
        practice_questions = []
    related_ids = lesson.content_json.get("related_course_ids", []) if isinstance(lesson.content_json, dict) else []
    related_ids = [value for value in related_ids if isinstance(value, str) and len(value) == 36 and value.count("-") == 4]
    related_courses = Course.objects.filter(
        pk__in=related_ids, status=Course.Status.PUBLISHED,
    ).exclude(pk=course.pk).order_by("position", "title")
    ordered_lessons = list(Lesson.objects.filter(
        module__course=course, module__is_published=True, is_published=True,
    ).select_related("module").order_by("module__position", "position", "title"))
    accessible_lessons = [item for item in ordered_lessons if can_access_lesson(request.user, item, now)]
    current_index = next((i for i, item in enumerate(accessible_lessons) if item.pk == lesson.pk), -1)
    previous_lesson = accessible_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = accessible_lessons[current_index + 1] if 0 <= current_index < len(accessible_lessons) - 1 else None
    total_lessons = len(ordered_lessons)
    completed_lessons = LessonProgress.objects.filter(
        user=request.user, lesson_id__in=[item.pk for item in ordered_lessons],
        status=LessonProgress.Status.COMPLETED,
    ).count()
    course_progress_percent = round(completed_lessons * 100 / total_lessons) if total_lessons else 0
    return render(request, "academy/lesson.html", {
        "course": course, "lesson": lesson, "module": lesson.module,
        "entitlement": entitlement, "progress": progress,
        "lesson_sections": build_lesson_sections(
            lesson.content_markdown,
            asset_urls,
            user=request.user,
        ),
        "notebook": notebook, "notebook_responses": saved_responses, "outline_modules": outline_modules,
        "related_courses": related_courses, "practice_questions": practice_questions,
        "video_url": video_url, "video_is_file": video_is_file,
        "previous_lesson": previous_lesson, "next_lesson": next_lesson,
        "course_progress_percent": course_progress_percent,
        "completed_lessons": completed_lessons, "total_lessons": total_lessons,
    })


@login_required
@require_POST
def lesson_quiz_submit(request, lesson_id):
    """Grade practice questions server-side; answer keys never enter the learner page."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id, is_published=True, module__is_published=True,
    )
    if not can_access_lesson(request.user, lesson):
        raise PermissionDenied("You do not have access to this lesson yet.")
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    if not isinstance(answers, dict):
        return JsonResponse({"detail": "Answers must be an object keyed by question ID."}, status=400)
    material = LessonInstructorMaterial.objects.filter(lesson=lesson).first()
    questions = material.rubric_json.get("questions", []) if material and isinstance(material.rubric_json, dict) else []
    if not questions:
        return JsonResponse({"detail": "Practice questions are not configured for this lesson."}, status=404)

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
        results.append({
            "id": question_id,
            "correct": correct,
            "explanation": str(question.get("explanation", ""))[:3000],
        })
    existing_progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    saved_response = dict(existing_progress.response_json or {}) if existing_progress and isinstance(existing_progress.response_json, dict) else {}
    saved_response.update({"quiz_answers": answers, "quiz_score": score, "quiz_total": len(results)})
    update_lesson_progress(
        user=request.user,
        lesson=lesson,
        response_json=saved_response,
    )
    return JsonResponse({"ok": True, "score": score, "total": len(results), "results": results})


@login_required
@require_POST
def lesson_notebook_submit(request, lesson_id):
    """Persist learner reflections without exposing or altering instructor materials."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id, is_published=True, module__is_published=True,
    )
    if not can_access_lesson(request.user, lesson):
        raise PermissionDenied("You do not have access to this lesson yet.")
    notebook = lesson.content_json.get("notebook", {}) if isinstance(lesson.content_json, dict) else {}
    prompts = notebook.get("prompts", []) if isinstance(notebook, dict) else []
    responses = []
    for index, _prompt in enumerate(prompts[:6]):
        responses.append(str(request.POST.get(f"prompt_{index}", "")).strip()[:4000])
    existing_progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    saved_response = dict(existing_progress.response_json or {}) if existing_progress and isinstance(existing_progress.response_json, dict) else {}
    saved_response["notebook_responses"] = responses
    update_lesson_progress(user=request.user, lesson=lesson, response_json=saved_response)
    return JsonResponse({"ok": True, "saved": True})


@login_required
def media_asset(request, asset_id):
    """Deliver teaching images only to admins or learners allowed to view a referencing lesson."""
    asset = get_object_or_404(CourseMediaAsset.objects.select_related("course"), pk=asset_id)
    if not asset.file:
        from django.http import Http404
        raise Http404
    allowed = is_course_content_admin(request.user)
    if not allowed:
        for related_lesson in Lesson.objects.filter(
            module__course=asset.course, module__is_published=True, is_published=True,
        ).select_related("module__course"):
            asset_ids = related_lesson.content_json.get("asset_ids", []) if isinstance(related_lesson.content_json, dict) else []
            if str(asset.pk) in asset_ids and can_access_lesson(request.user, related_lesson):
                allowed = True
                break
    if not allowed:
        raise PermissionDenied("You do not have access to this course image.")
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
            user=request.user, lesson=lesson,
            status=request.POST.get("status") or None,
            response_json=response_json,
            seconds_delta=seconds_delta,
        )
    except PermissionDenied as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except (ValidationError, ValueError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse({
        "ok": True, "status": progress.status,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        "time_spent_seconds": progress.time_spent_seconds,
    })
