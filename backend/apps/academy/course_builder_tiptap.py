"""Staff-only, opt-in Tiptap editor and draft adapter.

This route edits the existing CourseImport draft snapshot, not live Course or
Lesson rows. The legacy Course Builder, review workflow, and learner renderer
remain the source of lifecycle and preview behaviour.
"""

import hashlib
import json
import uuid
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import Http404, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.utils.cache import add_never_cache_headers
from django.views.decorators.http import require_GET, require_http_methods
from PIL import Image, UnidentifiedImageError

from .content_rendering import validate_markdown_source
from .course_card_utils import is_course_card_recommendable
from .lesson_document import LessonDocumentError, validate_lesson_document
from .models import Course, CourseImport, CourseImportAsset, CourseImportVideo, Lesson, ProtectedLessonVideo
from .permissions import is_course_content_admin


_TIPTAP_MAX_IMAGE_BYTES = 10 * 1024 * 1024
_TIPTAP_IMAGE_FORMATS = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
}


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


def _document_reference_errors(document, lesson_state, lesson_payload, lesson_id, record=None):
    """Reject document references that the existing Academy renderer cannot resolve."""
    content_json = (
        lesson_payload.get("content_json")
        if isinstance(lesson_payload.get("content_json"), dict)
        else {}
    )
    figures = content_json.get("figures") if isinstance(content_json.get("figures"), dict) else {}
    tables = content_json.get("tables") if isinstance(content_json.get("tables"), dict) else {}
    regional_blocks = (
        content_json.get("regional_blocks")
        if isinstance(content_json.get("regional_blocks"), dict)
        else {}
    )
    regional_content = (
        content_json.get("regional_lesson_content")
        if isinstance(content_json.get("regional_lesson_content"), dict)
        else {}
    )
    public_questions = (
        content_json.get("questions")
        if isinstance(content_json.get("questions"), list)
        else []
    )
    question_ids = {
        str(item.get("id"))
        for item in public_questions
        if isinstance(item, dict) and item.get("id")
    }
    state_questions = (
        lesson_state.get("questions") if isinstance(lesson_state.get("questions"), list) else []
    )
    question_ids.update(
        str(item.get("id"))
        for item in state_questions
        if isinstance(item, dict) and item.get("id")
    )
    image_ids = {
        str(value)
        for value in content_json.get("asset_ids", [])
        if value
    }
    state_images = (
        lesson_state.get("images") if isinstance(lesson_state.get("images"), list) else []
    )
    image_ids.update(
        str(item.get("assetUuid") or item.get("id"))
        for item in state_images
        if isinstance(item, dict) and (item.get("assetUuid") or item.get("id"))
    )
    image_group_ids = {
        str(item.get("id"))
        for item in (lesson_state.get("imageGroups") or [])
        if isinstance(item, dict) and item.get("id")
    }
    comparison_ids = {
        str(item.get("id"))
        for item in (lesson_state.get("teachingFigures") or [])
        if isinstance(item, dict) and item.get("id")
    }
    raw_video = (
        lesson_state.get("protectedVideo")
        if isinstance(lesson_state.get("protectedVideo"), dict)
        else {}
    )
    video_id = str(raw_video.get("id") or "")
    has_notebook = isinstance(lesson_state.get("notebook"), dict) and bool(
        lesson_state.get("notebook")
    )
    has_reflection = any(
        str(lesson_state.get(key) or "").strip()
        for key in (
            "reflectionPrompt",
            "reflectionModelReasoning",
            "reflectionChartNotes",
        )
    )
    errors = []

    def visit(node, path):
        if not isinstance(node, dict):
            return
        node_type = node.get("type")
        attrs = node.get("attrs") if isinstance(node.get("attrs"), dict) else {}
        reference = ""
        reason = ""
        if node_type == "image":
            source = str(attrs.get("assetId") or attrs.get("src") or "")
            if source.startswith("asset://"):
                reference = source[len("asset://"):]
                if reference not in image_ids and reference not in figures:
                    reason = "image asset is not part of this saved lesson"
        elif node_type in {"courseFigure", "comparisonFigure"}:
            reference = str(attrs.get("figureId") or "")
            figure = figures.get(reference)
            figure_type = figure.get("type") if isinstance(figure, dict) else ""
            if node_type == "comparisonFigure":
                if reference not in comparison_ids and figure_type != "comparison-cards":
                    reason = "comparison figure is not part of this saved lesson"
            elif reference not in image_ids and figure_type != "image":
                reason = "image figure is not part of this saved lesson"
        elif node_type == "imageGroup":
            reference = str(attrs.get("groupId") or "")
            figure = figures.get(reference)
            if not (
                reference in image_group_ids
                or (isinstance(figure, dict) and figure.get("type") == "image-group")
            ):
                reason = "image-group reference is not part of this saved lesson"
        elif node_type == "tableReference":
            reference = str(attrs.get("tableId") or "")
            if reference not in tables:
                reason = "table reference is not part of this saved lesson"
        elif node_type == "regionalBlock":
            reference = str(attrs.get("blockId") or "")
            if reference not in regional_blocks:
                reason = "regional block is not part of this saved lesson"
        elif node_type == "regionalLessonVariant":
            reference = str(attrs.get("variantKey") or "")
            if reference not in regional_content:
                reason = "whole-lesson regional variant is not part of this saved lesson"
        elif node_type == "courseCard":
            reference = str(attrs.get("courseId") or "")
            if attrs.get("comingSoon"):
                try:
                    teaser_id = uuid.UUID(reference)
                except (TypeError, ValueError, AttributeError):
                    teaser_id = None
                teaser = (
                    CourseImport.objects.filter(
                        pk=teaser_id,
                        status__in=[CourseImport.Status.DRAFT, CourseImport.Status.REVIEW],
                    ).first()
                    if teaser_id
                    else None
                )
                teaser_state = (
                    teaser.payload.get("builder_state")
                    if teaser and isinstance(teaser.payload, dict)
                    else None
                )
                if not isinstance(teaser_state, dict) or not teaser_state.get("comingSoon"):
                    reason = "coming-soon course-card reference is not an active teaser"
            else:
                try:
                    course_id = uuid.UUID(reference)
                except (TypeError, ValueError, AttributeError):
                    course_id = None
                course = (
                    Course.objects.filter(
                        pk=course_id,
                        status=Course.Status.PUBLISHED,
                    ).first()
                    if course_id
                    else None
                )
                if course is None or not is_course_card_recommendable(
                    course.title,
                    course.summary,
                    course.description,
                ):
                    reason = "course-card reference is not a recommendable published course"
        elif node_type == "lessonReference":
            reference = str(attrs.get("lessonId") or "")
            try:
                lesson_reference_id = uuid.UUID(reference)
            except (TypeError, ValueError, AttributeError):
                lesson_reference_id = None
            available_lesson = (
                Lesson.objects.filter(
                    pk=lesson_reference_id,
                    is_published=True,
                    module__is_published=True,
                    module__course__status=Course.Status.PUBLISHED,
                ).exists()
                if lesson_reference_id
                else False
            )
            if not available_lesson:
                reason = "lesson reference is not a published Academy lesson"
        elif node_type == "practiceQuestion":
            reference = str(attrs.get("questionId") or "")
            if reference not in question_ids:
                reason = "practice question is not part of this saved lesson"
        elif node_type == "videoBlock":
            reference = str(attrs.get("videoId") or "")
            staged_video_exists = bool(
                record
                and record.videos.filter(
                    pk=reference,
                    lesson_id=str(lesson_id),
                ).exclude(source_file="").exists()
            )
            live_video_exists = bool(
                record
                and record.target_course_id
                and ProtectedLessonVideo.objects.filter(
                    pk=reference,
                    lesson_id=str(lesson_id),
                    lesson__module__course_id=record.target_course_id,
                ).exists()
            )
            if not (staged_video_exists or live_video_exists or (reference and reference == video_id)):
                reason = "protected-video reference is not part of this saved lesson"
        elif node_type == "notebookBlock":
            reference = str(attrs.get("notebookId") or "")
            if not has_notebook or reference != "notebook-" + str(lesson_id):
                reason = "notebook reference is not part of this saved lesson"
        elif node_type == "reflectionBlock":
            reference = str(attrs.get("reflectionId") or "")
            if not has_reflection or reference != "reflection-" + str(lesson_id):
                reason = "reflection reference is not part of this saved lesson"
        elif node_type == "callout":
            reference = str(attrs.get("calloutId") or "")
            reason = (
                "callout-renderer-not-supported: "
                "callout blocks do not yet have learner-renderer parity"
            )
        if reason:
            errors.append(f"{node_type or 'unknown'} {reference!r}: {reason}.")
        for index, child in enumerate(node.get("content", []) if isinstance(node.get("content"), list) else []):
            visit(child, f"{path}.content[{index}]")

    root = document.get("document") if isinstance(document, dict) else None
    if isinstance(root, dict):
        visit(root, "document")
    return errors


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


def _learner_preview_url(record, lesson_payload):
    preview_url = reverse("academy:course-import-preview", args=[record.pk])
    source_id = str(lesson_payload.get("source_id") or "").strip()
    if source_id:
        preview_url += "?" + urlencode({"lesson": source_id})
    return preview_url


def _editor_lesson_response(request, record, lesson_id):
    state = _draft_state(record, request)
    lesson = _builder_lesson(state, lesson_id)
    if lesson is None:
        return JsonResponse({"detail": "That lesson is not part of this saved draft."}, status=404)
    payload = record.payload if isinstance(record.payload, dict) else {}
    lesson_payload = _payload_lesson(payload, lesson_id)
    if lesson_payload is None:
        return JsonResponse({"detail": "That lesson is missing from the saved import snapshot."}, status=409)

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
            "learner_preview_url": _learner_preview_url(record, lesson_payload),
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
    video_url_supplied = "video_url" in body
    external_video_url = str(body.get("video_url") or "").strip()
    if len(external_video_url) > 1000:
        return JsonResponse(
            {"detail": "External video links must be 1,000 characters or fewer."},
            status=400,
        )
    if video_url_supplied and external_video_url:
        parsed_video_url = urlsplit(external_video_url)
        if (
            parsed_video_url.scheme.lower() not in {"https", "http"}
            or not parsed_video_url.netloc
            or parsed_video_url.username
            or parsed_video_url.password
        ):
            return JsonResponse(
                {"detail": "External video links must be valid HTTP or HTTPS URLs."},
                status=400,
            )
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
        staged_protected_video = record.videos.filter(
            lesson_id=str(lesson_id),
        ).exclude(source_file="").exists()
        live_protected_video = bool(
            record.target_course_id
            and ProtectedLessonVideo.objects.filter(
                lesson_id=str(lesson_id),
                lesson__module__course_id=record.target_course_id,
            ).exists()
        )
        if video_url_supplied and external_video_url and (
            staged_protected_video or live_protected_video
        ):
            return JsonResponse(
                {
                    "detail": (
                        "This lesson already has a protected video. Keep that protected stream "
                        "as the lesson video, or remove it through the existing Course Builder "
                        "before switching to an external video link."
                    )
                },
                status=409,
            )

        reference_errors = _document_reference_errors(
            document,
            state_lesson,
            import_lesson,
            lesson_id,
            record=record,
        )
        if reference_errors:
            return JsonResponse(
                {
                    "detail": "The lesson document contains references that cannot be rendered safely.",
                    "compatibility_errors": reference_errors[:20],
                },
                status=400,
            )

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
        if video_url_supplied:
            state_lesson["videoUrl"] = external_video_url
            import_content_json["video_url"] = external_video_url
        import_lesson["content_markdown"] = markdown
        import_lesson["content_json"] = import_content_json

        if record.status == CourseImport.Status.REJECTED:
            payload.pop("review_feedback", None)
        payload["builder_state"] = state
        encoded = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        new_content_hash = hashlib.sha256(encoded).hexdigest()
        duplicate_snapshot = CourseImport.objects.filter(
            course_slug=record.course_slug,
            content_hash=new_content_hash,
        ).exclude(pk=record.pk).exists()
        if duplicate_snapshot:
            return JsonResponse(
                {
                    "detail": "An identical saved snapshot already exists for this course. Reload the draft list before saving again.",
                    "conflict": True,
                },
                status=409,
            )
        record.payload = payload
        record.content_hash = new_content_hash
        if record.status == CourseImport.Status.REJECTED:
            record.status = CourseImport.Status.DRAFT
        record.save(update_fields=["payload", "content_hash", "status", "updated_at"])

    response = JsonResponse(
        {
            "ok": True,
            "draft_id": str(record.pk),
            "lesson_id": str(lesson_id),
            "updated_at": record.updated_at.isoformat(),
            "learner_preview_url": _learner_preview_url(record, import_lesson),
        }
    )
    add_never_cache_headers(response)
    return response



def _tiptap_media_image(image, *, data_url=""):
    stable_id = str(
        image.get("assetUuid") or image.get("assetId") or image.get("id") or ""
    ).strip()
    if not stable_id:
        return None
    return {
        "id": stable_id,
        "assetUuid": stable_id,
        "name": str(image.get("name") or "Course image")[:240],
        "title": str(image.get("title") or "")[:240],
        "alt": str(image.get("alt") or image.get("alt_text") or "")[:500],
        "caption": str(image.get("caption") or "")[:500],
        "data": str(data_url or image.get("data") or ""),
    }


def _tiptap_media_image_url(record, stable_id):
    return reverse("staff_course_builder_asset", args=[record.pk, stable_id])


def _tiptap_add_image_to_lesson(state, payload, lesson_id, image):
    state_lesson = _builder_lesson(state, lesson_id)
    import_lesson = _payload_lesson(payload, lesson_id)
    if state_lesson is None or import_lesson is None:
        return False

    stable_id = str(image["assetUuid"])
    images = state_lesson.get("images")
    if not isinstance(images, list):
        images = []
    if not any(
        isinstance(item, dict)
        and str(item.get("assetUuid") or item.get("id") or "") == stable_id
        for item in images
    ):
        images.append(deepcopy(image))
    state_lesson["images"] = images
    if not state_lesson.get("image"):
        state_lesson["image"] = deepcopy(image)

    content_json = (
        deepcopy(import_lesson.get("content_json"))
        if isinstance(import_lesson.get("content_json"), dict)
        else {}
    )
    asset_ids = content_json.get("asset_ids")
    if not isinstance(asset_ids, list):
        asset_ids = []
    if stable_id not in {str(value) for value in asset_ids}:
        asset_ids.append(stable_id)
    content_json["asset_ids"] = asset_ids

    figures = content_json.get("figures")
    if not isinstance(figures, dict):
        figures = {}
    existing_figure = figures.get(stable_id)
    if not isinstance(existing_figure, dict):
        figures[stable_id] = {
            "type": "image",
            "title": image.get("title", ""),
            "alt": image.get("alt", ""),
            "caption": image.get("caption", ""),
        }
    else:
        existing_figure.setdefault("type", "image")
        existing_figure.setdefault("title", image.get("title", ""))
        existing_figure.setdefault("alt", image.get("alt", ""))
        existing_figure.setdefault("caption", image.get("caption", ""))
    content_json["figures"] = figures
    import_lesson["content_json"] = content_json

    assets = payload.get("assets")
    if not isinstance(assets, list):
        assets = []
    if not any(
        isinstance(item, dict)
        and str(item.get("stable_asset_id") or "") == stable_id
        for item in assets
    ):
        payload_asset = image.get("_asset_spec")
        if isinstance(payload_asset, dict):
            assets.append(deepcopy(payload_asset))
    payload["assets"] = assets
    return True


@login_required
@require_http_methods(["GET", "POST"])
def course_builder_tiptap_media_api(request, draft_id):
    """List, upload and attach image assets using the existing Academy asset store."""
    _require_tiptap_access(request)
    editable_statuses = [CourseImport.Status.DRAFT, CourseImport.Status.REJECTED]
    record = CourseImport.objects.filter(
        pk=draft_id,
        status__in=editable_statuses,
    ).first()
    if record is None or not (record.payload or {}).get("builder_state"):
        return JsonResponse({"detail": "That saved draft is unavailable for media editing."}, status=404)

    if request.method == "GET":
        state = _draft_state(record, request)
        images_by_id = {}
        for module in state.get("modules", []):
            if not isinstance(module, dict):
                continue
            for lesson in module.get("lessons", []):
                if not isinstance(lesson, dict):
                    continue
                for raw_image in lesson.get("images", []):
                    if not isinstance(raw_image, dict):
                        continue
                    image = _tiptap_media_image(raw_image)
                    if image and image["data"]:
                        images_by_id[image["assetUuid"]] = image
        for asset in record.assets.all():
            stable_id = str(asset.stable_asset_id)
            if stable_id not in images_by_id and asset.file:
                images_by_id[stable_id] = {
                    "id": stable_id,
                    "assetUuid": stable_id,
                    "name": Path(asset.file.name).name[:240] or "Course image",
                    "title": "",
                    "alt": str(asset.alt_text or "")[:500],
                    "caption": "",
                    "data": _tiptap_media_image_url(record, stable_id),
                }
        response = JsonResponse(
            {
                "images": sorted(
                    images_by_id.values(),
                    key=lambda item: (item["title"] or item["name"]).casefold(),
                ),
                "updated_at": record.updated_at.isoformat(),
            }
        )
        add_never_cache_headers(response)
        return response

    expected_updated_at = str(request.POST.get("expected_updated_at") or "").strip()
    lesson_id = str(request.POST.get("lesson_id") or "").strip()
    requested_asset_id = ""
    if request.content_type == "application/json":
        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
        if not isinstance(body, dict):
            return JsonResponse({"detail": "The request body must be a JSON object."}, status=400)
        expected_updated_at = str(body.get("expected_updated_at") or "").strip()
        lesson_id = str(body.get("lesson_id") or "").strip()
        requested_asset_id = str(body.get("asset_id") or "").strip()

    if not expected_updated_at:
        return JsonResponse(
            {"detail": "Reload the lesson before changing its media; its revision token is missing."},
            status=400,
        )
    if not lesson_id:
        return JsonResponse({"detail": "Select a lesson before adding an image."}, status=400)

    uploaded = request.FILES.get("file")
    raw_bytes = b""
    extension = ""
    if uploaded is not None:
        if uploaded.size <= 0 or uploaded.size > _TIPTAP_MAX_IMAGE_BYTES:
            return JsonResponse(
                {"detail": "Each image must be larger than 0 bytes and no larger than 10 MB."},
                status=400,
            )
        raw_bytes = uploaded.read()
        if len(raw_bytes) != uploaded.size:
            return JsonResponse({"detail": "The image upload could not be read completely."}, status=400)
        try:
            with Image.open(BytesIO(raw_bytes)) as source_image:
                detected_format = str(source_image.format or "").upper()
                source_image.verify()
            if detected_format not in _TIPTAP_IMAGE_FORMATS:
                raise ValueError("Choose a JPEG, PNG or WebP image.")
            extension, _mime_type = _TIPTAP_IMAGE_FORMATS[detected_format]
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            return JsonResponse({"detail": f"The uploaded image is invalid: {exc}"}, status=400)

    staged_file_name = ""
    staged_storage = None
    try:
        with transaction.atomic():
            record = (
                CourseImport.objects.select_for_update()
                .filter(pk=draft_id, status__in=editable_statuses)
                .first()
            )
            if record is None:
                return JsonResponse({"detail": "That saved draft is no longer editable."}, status=410)
            actual_updated_at = record.updated_at.isoformat()
            if actual_updated_at != expected_updated_at:
                return JsonResponse(
                    {
                        "detail": "This course draft changed in another tab. Reload it before changing media.",
                        "conflict": True,
                        "latest_updated_at": actual_updated_at,
                    },
                    status=409,
                )

            payload = deepcopy(record.payload) if isinstance(record.payload, dict) else {}
            state = payload.get("builder_state")
            if not isinstance(state, dict):
                return JsonResponse({"detail": "The saved draft has no editable Builder state."}, status=409)
            if _builder_lesson(state, lesson_id) is None or _payload_lesson(payload, lesson_id) is None:
                return JsonResponse({"detail": "That lesson no longer exists in this saved draft."}, status=409)

            if uploaded is not None:
                image_id = str(uuid.uuid4())
                stable_id = str(
                    uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        f"tradethesis-course:{record.course_slug}:builder/{image_id}",
                    )
                )
                filename = Path(str(uploaded.name or "course-image").replace("\\", "/")).name
                filename = filename[:200] or "course-image"
                image_name = Path(filename).stem[:160] or "course-image"
                staged_asset = CourseImportAsset(
                    course_import=record,
                    asset_key=f"builder/{image_id}",
                    stable_asset_id=stable_id,
                    alt_text="",
                    source_path="",
                    original_url="",
                    source_error="",
                )
                staged_asset.file.save(
                    image_name + extension,
                    ContentFile(raw_bytes, name=image_name + extension),
                    save=False,
                )
                staged_storage = staged_asset.file.storage
                staged_file_name = staged_asset.file.name
                staged_asset.save()
                image = {
                    "id": image_id,
                    "assetUuid": stable_id,
                    "assetKey": staged_asset.asset_key,
                    "name": filename,
                    "title": "",
                    "alt": "",
                    "caption": "",
                    "data": _tiptap_media_image_url(record, stable_id),
                    "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                    "_asset_spec": {
                        "asset_key": staged_asset.asset_key,
                        "stable_asset_id": stable_id,
                        "alt_text": "",
                        "source_path": "",
                        "original_url": "",
                        "source_error": "",
                        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                    },
                }
            else:
                if not requested_asset_id:
                    return JsonResponse({"detail": "Choose an image from this draft's media library."}, status=400)
                try:
                    parsed_asset_id = str(uuid.UUID(requested_asset_id))
                except (ValueError, TypeError, AttributeError):
                    return JsonResponse({"detail": "The selected image reference is invalid."}, status=400)

                existing_image = None
                for module in state.get("modules", []):
                    if not isinstance(module, dict):
                        continue
                    for lesson in module.get("lessons", []):
                        if not isinstance(lesson, dict):
                            continue
                        for raw_image in lesson.get("images", []):
                            if not isinstance(raw_image, dict):
                                continue
                            stable = str(raw_image.get("assetUuid") or raw_image.get("id") or "")
                            if stable == parsed_asset_id:
                                existing_image = deepcopy(raw_image)
                                break
                        if existing_image:
                            break
                    if existing_image:
                        break
                asset_record = record.assets.filter(stable_asset_id=parsed_asset_id).first()
                if existing_image is None and asset_record is None:
                    return JsonResponse({"detail": "That image is not part of this saved draft."}, status=404)
                if existing_image is not None:
                    image = _tiptap_media_image(
                        existing_image,
                        data_url=existing_image.get("data") or _tiptap_media_image_url(record, parsed_asset_id),
                    )
                else:
                    image = {
                        "id": parsed_asset_id,
                        "assetUuid": parsed_asset_id,
                        "name": Path(asset_record.file.name).name[:240] if asset_record.file else "Course image",
                        "title": "",
                        "alt": str(asset_record.alt_text or "")[:500],
                        "caption": "",
                        "data": _tiptap_media_image_url(record, parsed_asset_id),
                        "_asset_spec": {
                            "asset_key": asset_record.asset_key,
                            "stable_asset_id": parsed_asset_id,
                            "alt_text": str(asset_record.alt_text or "")[:500],
                            "source_path": str(asset_record.source_path or ""),
                            "original_url": str(asset_record.original_url or ""),
                            "source_error": str(asset_record.source_error or ""),
                            "sha256": "",
                        },
                    }

            image_for_state = deepcopy(image)
            if isinstance(image.get("_asset_spec"), dict):
                image_for_state["_asset_spec"] = image["_asset_spec"]
            if not _tiptap_add_image_to_lesson(state, payload, lesson_id, image_for_state):
                return JsonResponse({"detail": "The selected lesson could not accept this image."}, status=409)
            for module in state.get("modules", []):
                if not isinstance(module, dict):
                    continue
                for lesson in module.get("lessons", []):
                    if not isinstance(lesson, dict):
                        continue
                    for item in lesson.get("images", []):
                        if isinstance(item, dict) and str(item.get("assetUuid") or "") == str(image["assetUuid"]):
                            item.pop("_asset_spec", None)
                    if isinstance(lesson.get("image"), dict):
                        lesson["image"].pop("_asset_spec", None)

            encoded = json.dumps(
                payload,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            new_content_hash = hashlib.sha256(encoded).hexdigest()
            duplicate_snapshot = CourseImport.objects.filter(
                course_slug=record.course_slug,
                content_hash=new_content_hash,
            ).exclude(pk=record.pk).exists()
            if duplicate_snapshot:
                return JsonResponse(
                    {"detail": "An identical saved snapshot already exists for this course. Reload before changing media.", "conflict": True},
                    status=409,
                )
            record.payload = payload
            record.content_hash = new_content_hash
            if record.status == CourseImport.Status.REJECTED:
                record.status = CourseImport.Status.DRAFT
            record.save(update_fields=["payload", "content_hash", "status", "updated_at"])
            image.pop("_asset_spec", None)
            response_payload = {
                "ok": True,
                "image": image,
                "updated_at": record.updated_at.isoformat(),
            }
    except (OSError, ValueError) as exc:
        if staged_file_name and staged_storage:
            try:
                staged_storage.delete(staged_file_name)
            except Exception:
                pass
        return JsonResponse(
            {"detail": "The image could not be saved to Academy asset storage: " + str(exc)},
            status=503,
        )
    except Exception:
        if staged_file_name and staged_storage:
            try:
                staged_storage.delete(staged_file_name)
            except Exception:
                pass
        raise

    response = JsonResponse(response_payload, status=201 if uploaded is not None else 200)
    add_never_cache_headers(response)
    return response
