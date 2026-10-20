"""Authenticated learner views for TradeThesis Academy."""
import json
import mimetypes
from contextlib import suppress
from urllib.parse import quote
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch, Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .content_rendering import build_lesson_sections, render_safe_markdown
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
)
from .permissions import is_course_content_admin
from .services import (
    can_access_lesson,
    get_active_entitlement,
    get_resume_lesson,
    lesson_release_at,
    update_lesson_progress,
)


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
        "course": course,
        "course_description_html": _render_course_description(course.description, user=request.user),
        "entitlement": entitlement, "offer": offer,
        "module_rows": module_rows, "completed_lessons": completed,
        "total_lessons": total,
        "total_modules": len(module_rows),
        "total_study_minutes": total_study_minutes,
        "total_study_hours": total_study_minutes // 60,
        "total_study_minutes_remainder": total_study_minutes % 60,
        "first_accessible_lesson": first_accessible_lesson,
        "is_course_content_admin": is_course_content_admin(request.user),
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
    practice_questions = _practice_questions_with_images(
        practice_questions,
        asset_urls,
        lesson.content_json.get("figures", {}) if isinstance(lesson.content_json, dict) else {},
    )
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
            figure_metadata=(
                lesson.content_json.get("figures", {})
                if isinstance(lesson.content_json, dict) else {}
            ),
            figure_prefix=f"{lesson.module.position}.{lesson.position}",
            module_label=f"Module {lesson.module.position} · {lesson.module.title}",
        ),
        "notebook": notebook, "notebook_responses": saved_responses, "outline_modules": outline_modules,
        "related_courses": related_courses, "practice_questions": practice_questions,
        "video_url": video_url, "video_is_file": video_is_file,
        "previous_lesson": previous_lesson, "next_lesson": next_lesson,
        "course_progress_percent": course_progress_percent,
        "completed_lessons": completed_lessons, "total_lessons": total_lessons,
    })


@login_required
def admin_lesson_preview(request, course_slug, lesson_id):
    """Show a real locked lesson to course admins without altering learner state."""
    if not is_course_content_admin(request.user):
        raise PermissionDenied("Administrator course-content access is required.")

    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        module__course__slug=course_slug,
        module__course__status=Course.Status.PUBLISHED,
        module__is_published=True,
        is_published=True,
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
        elif isinstance(asset.original_url, str) and asset.original_url.startswith(("https://", "http://")):
            asset_urls[str(asset.pk)] = asset.original_url

    now = timezone.now()
    modules = CourseModule.objects.filter(
        course=course,
        is_published=True,
    ).prefetch_related(
        Prefetch(
            "lessons",
            queryset=Lesson.objects.filter(is_published=True).order_by("position", "title"),
        )
    ).order_by("position", "title")
    outline_modules = []
    ordered_lessons = []
    for module_row in modules:
        rows = []
        for outline_lesson in module_row.lessons.all():
            ordered_lessons.append(outline_lesson)
            rows.append({
                "lesson": outline_lesson,
                "accessible": can_access_lesson(request.user, outline_lesson, now),
                "current": outline_lesson.pk == lesson.pk,
                "progress": None,
                "admin_preview_url": reverse(
                    "academy:admin-lesson-preview",
                    args=[course.slug, outline_lesson.pk],
                ),
            })
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
    notebook = content_json.get("notebook", {})
    if not isinstance(notebook, dict):
        notebook = {}
    practice_questions = _practice_questions_with_images(
        content_json.get("questions", []),
        asset_urls,
        content_json.get("figures", {}),
    )
    video_url = content_json.get("video_url", "")
    if not isinstance(video_url, str) or not video_url.startswith(("https://", "http://")):
        video_url = ""
    video_is_file = video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))

    return render(request, "academy/lesson.html", {
        "course": course,
        "lesson": lesson,
        "module": lesson.module,
        "entitlement": entitlement,
        "progress": None,
        "admin_preview": True,
        "lesson_sections": build_lesson_sections(
            lesson.content_markdown,
            asset_urls,
            user=request.user,
            admin_preview=True,
            figure_metadata=content_json.get("figures", {}),
            figure_prefix=f"{lesson.module.position}.{lesson.position}",
            module_label=f"Module {lesson.module.position} · {lesson.module.title}",
        ),
        "notebook": notebook,
        "notebook_responses": [],
        "outline_modules": outline_modules,
        "related_courses": Course.objects.none(),
        "practice_questions": practice_questions,
        "video_url": video_url,
        "video_is_file": video_is_file,
        "previous_lesson": previous_lesson,
        "next_lesson": next_lesson,
        "course_progress_percent": 0,
        "completed_lessons": 0,
        "total_lessons": len(ordered_lessons),
    })


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

    overview_url = reverse("academy:course-import-preview", args=[record.pk])
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
                lesson_url = overview_url + "?lesson=" + quote(source_id, safe="")
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
    selected_practice_questions = []
    selected_video_url = ""
    selected_video_is_file = False
    selected_related_courses = Course.objects.none()
    if selected_lesson is not None:
        selected_content_json = selected_lesson.get("content_json", {})
        if not isinstance(selected_content_json, dict):
            selected_content_json = {}
        selected_sections = build_lesson_sections(
            selected_lesson.get("content_markdown", ""),
            asset_urls,
            user=request.user,
            admin_preview=True,
            figure_metadata=selected_content_json.get("figures", {}),
            figure_prefix=str(selected_lesson.get("source_id", "")),
            module_label=f"Module {selected_module.get('position', '')} · {selected_module.get('title', '')}",
        )
        content_json = selected_lesson.get("content_json", {})
        if not isinstance(content_json, dict):
            content_json = {}
        selected_notebook = content_json.get("notebook") or payload.get("notebook", {})
        if not isinstance(selected_notebook, dict):
            selected_notebook = {}
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
            selected_related_courses = Course.objects.filter(
                pk__in=related_ids,
                status=Course.Status.PUBLISHED,
            ).exclude(pk=record.target_course_id).order_by("position", "title")

        # Match the learner lesson view: render only ordinary HTTP(S) video
        # destinations, and use the native player only for supported file types.
        raw_video_url = content_json.get("video_url", "")
        if isinstance(raw_video_url, str):
            raw_video_url = raw_video_url.strip()
            if raw_video_url.startswith(("https://", "http://")):
                selected_video_url = raw_video_url
                selected_video_is_file = raw_video_url.lower().split("?", 1)[0].endswith(
                    (".mp4", ".webm", ".ogg")
                )

    return render(request, "academy/course_import_website_preview.html", {
        "import_record": record,
        "course": course,
        "course_description_html": _render_course_description(
            course.get("description", ""), user=request.user, admin_preview=True,
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
        "selected_sections": selected_sections,
        "selected_notebook": selected_notebook,
        "selected_practice_questions": selected_practice_questions,
        "selected_video_url": selected_video_url,
        "selected_video_is_file": selected_video_is_file,
        "selected_related_courses": selected_related_courses,
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
            # Reveal option indexes only after the learner submits an attempt.
            "selected_index": selected if 0 <= selected < len(options) else None,
            "correct_index": correct_index if 0 <= correct_index < len(options) else None,
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
