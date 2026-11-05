"""Staff-only, opt-in Tiptap editor and draft adapter.

This route edits the existing CourseImport draft snapshot, not live Course or
Lesson rows. The legacy Course Builder, review workflow, and learner renderer
remain the source of lifecycle and preview behaviour.
"""

import hashlib
import json
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.utils.cache import add_never_cache_headers
from django.views.decorators.http import require_GET, require_http_methods

from .content_rendering import validate_markdown_source
from .lesson_document import LessonDocumentError, validate_lesson_document
from .models import CourseImport
from .permissions import is_course_content_admin


def _require_tiptap_access(request):
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied

    if not getattr(settings, "ACADEMY_TIPTAP_EDITOR_ENABLED", False):
        raise Http404


def _builder_lesson(state, lesson_id):
    for module in state.get("modules", []) if isinstance(state, dict) else []:
        if not isinstance(module, dict):
            continue
        for lesson in module.get("lessons", []) if isinstance(module.get("lessons"), list) else []:
            if isinstance(lesson, dict) and str(lesson.get("id") or "") == str(lesson_id):
                return lesson
    return None


def _payload_lesson(payload, lesson_id):
    for module in payload.get("modules", []) if isinstance(payload, dict) else []:
        if not isinstance(module, dict):
            continue
        for lesson in module.get("lessons", []) if isinstance(module.get("lessons"), list) else []:
            if not isinstance(lesson, dict):
                continue
            stable_id = lesson.get("builder_lesson_id") or lesson.get("id")
            if str(stable_id or "") == str(lesson_id):
                return lesson
    return None


def _safe_editor_lesson(lesson):
    result = deepcopy(lesson)
    questions = result.get("questions")
    if isinstance(questions, list):
        result["questions"] = [
            {
                key: question.get(key)
                for key in ("id", "prompt", "options", "imageId")
                if key in question
            }
            for question in questions
            if isinstance(question, dict)
        ]
    return result


def _draft_state(record, request):
    # Reuse the Builder's established hydration for protected-video status and
    # private draft asset URLs. That helper does not expose storage paths or keys.
    from .course_builder_api import _draft_response

    return _draft_response(record, request)


def _editor_draft_list(request):
    records = CourseImport.objects.filter(
        status__in=[CourseImport.Status.DRAFT, CourseImport.Status.REJECTED],
    ).order_by("-updated_at")[:100]
    drafts = []
    for record in records:
        payload = record.payload if isinstance(record.payload, dict) else {}
        state = payload.get("builder_state")
        if not isinstance(state, dict) or not isinstance(state.get("modules"), list):
            continue
        modules = []
        for module in state["modules"]:
            if not isinstance(module, dict):
                continue
            lessons = [
                {
                    "id": str(lesson.get("id") or ""),
                    "title": str(lesson.get("title") or "Untitled lesson"),
                }
                for lesson in module.get("lessons", [])
                if isinstance(lesson, dict) and lesson.get("id")
            ]
            modules.append(
                {
                    "id": str(module.get("id") or ""),
                    "title": str(module.get("title") or "Untitled module"),
                    "lessons": lessons,
                }
            )
        drafts.append(
            {
                "id": str(record.pk),
                "title": str(state.get("title") or record.title),
                "slug": record.course_slug,
                "status": record.status,
                "updated_at": record.updated_at.isoformat(),
                "modules": modules,
            }
        )
    response = JsonResponse({"drafts": drafts})
    add_never_cache_headers(response)
    return response


def _editor_lesson_response(request, record, lesson_id):
    state = _draft_state(record, request)
    lesson = _builder_lesson(state, lesson_id)
    if lesson is None:
        return JsonResponse({"detail": "That lesson is not part of this saved draft."}, status=404)

    document = lesson.get("document")
    document_error = ""
    if document is not None:
        try:
            document = validate_lesson_document(document)
        except LessonDocumentError as exc:
            document_error = str(exc)[:300]
            document = None

    safe_lesson = _safe_editor_lesson(lesson)
    safe_lesson["document"] = document
    safe_lesson["documentValidationError"] = document_error

    response = JsonResponse(
        {
            "draft": {
                "id": str(record.pk),
                "title": str(state.get("title") or record.title),
                "slug": record.course_slug,
                "status": record.status,
                "updated_at": record.updated_at.isoformat(),
            },
            "lesson": safe_lesson,
            "expected_updated_at": record.updated_at.isoformat(),
            "learner_preview_url": reverse("academy:course-import-preview", args=[record.pk]),
        }
    )
    add_never_cache_headers(response)
    return response


@login_required
@require_GET
def course_builder_tiptap_preview(request):
    """Render the isolated structured-editor lab for authorised course editors."""
    _require_tiptap_access(request)
    get_token(request)
    response = render(
        request,
        "academy/course_builder_tiptap.html",
        {
            "tiptap_api_url": reverse("staff_course_builder_tiptap_api"),
        },
    )
    add_never_cache_headers(response)
    response["X-Frame-Options"] = "DENY"
    response["Referrer-Policy"] = "same-origin"
    public_site_origin = str(
        getattr(settings, "TRADETHESIS_PUBLIC_SITE_URL", "") or ""
    ).rstrip("/")
    response["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        f"style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline' {public_site_origin}; "
        f"font-src 'self' data: https://cdn.jsdelivr.net {public_site_origin}; "
        f"img-src 'self' data: blob: {public_site_origin}; "
        "connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return response


@login_required
@require_http_methods(["GET", "POST"])
def course_builder_tiptap_api(request, draft_id=None, lesson_id=None):
    """Load or save one lesson in an existing, editable Course Builder draft."""
    _require_tiptap_access(request)

    if request.method == "GET" and draft_id is None:
        return _editor_draft_list(request)

    if draft_id is None or lesson_id is None:
        return JsonResponse({"detail": "Select a saved course draft and lesson."}, status=400)

    editable_statuses = [CourseImport.Status.DRAFT, CourseImport.Status.REJECTED]

    if request.method == "GET":
        record = CourseImport.objects.filter(
            pk=draft_id,
            status__in=editable_statuses,
        ).first()
        if record is None or not (record.payload or {}).get("builder_state"):
            return JsonResponse({"detail": "That saved draft is unavailable for editing."}, status=404)
        return _editor_lesson_response(request, record, lesson_id)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
    if not isinstance(body, dict):
        return JsonResponse({"detail": "The request body must be a JSON object."}, status=400)

    expected_updated_at = str(body.get("expected_updated_at") or "").strip()
    markdown = body.get("markdown")
    if not expected_updated_at:
        return JsonResponse({"detail": "Reload the lesson before saving; its revision token is missing."}, status=400)
    if not isinstance(markdown, str):
        return JsonResponse({"detail": "The Markdown compatibility mirror is required."}, status=400)

    try:
        document = validate_lesson_document(body.get("document"))
        validate_markdown_source(markdown)
    except (LessonDocumentError, ValueError, TypeError) as exc:
        messages = getattr(exc, "messages", None)
        return JsonResponse({"detail": messages or str(exc)}, status=400)

    with transaction.atomic():
        record = (
            CourseImport.objects.select_for_update()
            .filter(pk=draft_id, status__in=editable_statuses)
            .first()
        )
        if record is None:
            return JsonResponse(
                {
                    "detail": "This draft is no longer editable. Reopen it from the saved-drafts list.",
                    "draft_deleted": True,
                },
                status=410,
            )
        actual_updated_at = record.updated_at.isoformat()
        if actual_updated_at != expected_updated_at:
            return JsonResponse(
                {
                    "detail": "This course draft changed in another tab or editor. Reload it before saving to avoid overwriting newer work.",
                    "conflict": True,
                    "latest_updated_at": actual_updated_at,
                },
                status=409,
            )

        payload = deepcopy(record.payload) if isinstance(record.payload, dict) else {}
        state = payload.get("builder_state")
        if not isinstance(state, dict):
            return JsonResponse({"detail": "The saved draft has no editable Builder state."}, status=409)
        state_lesson = _builder_lesson(state, lesson_id)
        import_lesson = _payload_lesson(payload, lesson_id)
        if state_lesson is None or import_lesson is None:
            return JsonResponse({"detail": "That lesson no longer exists in this saved draft."}, status=409)

        # Update only the selected lesson's prose and canonical v1 document.
        # Course metadata, images, questions, regional variants, notebook,
        # reflection, and protected-video records remain in their existing
        # fields and pipelines.
        state_lesson["content"] = markdown
        state_lesson["document"] = document
        state_lesson.pop("documentValidationError", None)
        import_content_json = (
            deepcopy(import_lesson.get("content_json"))
            if isinstance(import_lesson.get("content_json"), dict)
            else {}
        )
        import_content_json["lesson_document"] = document
        import_lesson["content_markdown"] = markdown
        import_lesson["content_json"] = import_content_json

        payload["builder_state"] = state
        encoded = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        record.payload = payload
        record.content_hash = hashlib.sha256(encoded).hexdigest()
        if record.status == CourseImport.Status.REJECTED:
            record.status = CourseImport.Status.DRAFT
            record.payload.pop("review_feedback", None)
        record.save(update_fields=["payload", "content_hash", "status", "updated_at"])

    response = JsonResponse(
        {
            "ok": True,
            "draft_id": str(record.pk),
            "lesson_id": str(lesson_id),
            "updated_at": record.updated_at.isoformat(),
            "learner_preview_url": reverse("academy:course-import-preview", args=[record.pk]),
        }
    )
    add_never_cache_headers(response)
    return response
