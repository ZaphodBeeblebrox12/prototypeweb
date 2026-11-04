"""Staff-only, side-by-side Tiptap editor pilot.

Pilot documents are stored independently from CourseImport and Lesson records.
The pilot has no publish, review, pricing, entitlement, or learner-facing actions.
"""

import json
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.cache import add_never_cache_headers
from django.views.decorators.http import require_GET, require_http_methods

from .lesson_document import LessonDocumentError, validate_lesson_document
from .models import CourseBuilderTiptapDraft
from .permissions import is_course_content_admin

MAX_PILOT_REQUEST_BYTES = 1_500_000
MAX_PILOT_DRAFTS_PER_AUTHOR = 100

PILOT_NODE_TYPES = frozenset(
    {
        "doc",
        "paragraph",
        "heading",
        "text",
        "hardBreak",
        "horizontalRule",
        "blockquote",
        "bulletList",
        "orderedList",
        "listItem",
        "codeBlock",
        "table",
        "tableRow",
        "tableHeader",
        "tableCell",
    }
)
PILOT_MARK_TYPES = frozenset(
    {"bold", "italic", "strike", "underline", "code", "link"}
)


def _validate_pilot_schema(document):
    """Reject valid future lesson blocks until the pilot has their editor extensions."""
    def visit(node):
        node_type = node["type"]
        if node_type not in PILOT_NODE_TYPES:
            raise LessonDocumentError(
                f"The Tiptap pilot does not support the {node_type!r} block yet."
            )
        for mark in node.get("marks", []):
            if mark["type"] not in PILOT_MARK_TYPES:
                raise LessonDocumentError(
                    f"The Tiptap pilot does not support the {mark['type']!r} format yet."
                )
        for child in node.get("content", []):
            visit(child)

    visit(document)


def _require_tiptap_pilot_access(request):
    if not getattr(settings, "ACADEMY_TIPTAP_PILOT_ENABLED", False):
        raise Http404
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied


def _draft_summary(draft):
    return {
        "id": str(draft.pk),
        "title": draft.title,
        "revision": draft.revision,
        "updated_at": draft.updated_at.isoformat(),
    }


@login_required
@require_GET
def tiptap_pilot_editor(request):
    """Render the isolated editor shell; the existing Course Builder is untouched."""
    _require_tiptap_pilot_access(request)
    response = render(request, "academy/tiptap_pilot.html")
    add_never_cache_headers(response)
    response["X-Frame-Options"] = "DENY"
    response["Referrer-Policy"] = "same-origin"
    response["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )
    return response


@login_required
@require_http_methods(["GET", "POST"])
def tiptap_pilot_api(request):
    """List, load, create and revision-check sandbox drafts for the new editor only."""
    _require_tiptap_pilot_access(request)

    if request.method == "GET":
        raw_id = request.GET.get("id")
        if raw_id:
            try:
                draft_id = uuid.UUID(raw_id)
            except (ValueError, TypeError, AttributeError):
                return JsonResponse({"detail": "The pilot draft ID is invalid."}, status=400)
            draft = get_object_or_404(
                CourseBuilderTiptapDraft,
                pk=draft_id,
                owner=request.user,
            )
            return JsonResponse({"draft": _draft_summary(draft), "document": draft.document})

        drafts = (
            CourseBuilderTiptapDraft.objects.filter(owner=request.user)
            .order_by("-updated_at")[:MAX_PILOT_DRAFTS_PER_AUTHOR]
        )
        return JsonResponse({"drafts": [_draft_summary(draft) for draft in drafts]})

    if len(request.body) > MAX_PILOT_REQUEST_BYTES:
        return JsonResponse(
            {"detail": "This pilot document is too large to save."},
            status=413,
        )
    if request.content_type != "application/json":
        return JsonResponse({"detail": "The request must use application/json."}, status=415)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
    if not isinstance(body, dict):
        return JsonResponse({"detail": "The request body must be an object."}, status=400)

    title = body.get("title")
    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:
        return JsonResponse(
            {"detail": "A draft title of 1–200 characters is required."},
            status=400,
        )

    try:
        document = validate_lesson_document(body.get("document"))
        _validate_pilot_schema(document["document"])
    except LessonDocumentError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    raw_id = body.get("id")
    if raw_id is None:
        draft_count = CourseBuilderTiptapDraft.objects.filter(owner=request.user).count()
        if draft_count >= MAX_PILOT_DRAFTS_PER_AUTHOR:
            return JsonResponse(
                {"detail": "The pilot draft limit has been reached for this account."},
                status=400,
            )
        draft = CourseBuilderTiptapDraft.objects.create(
            owner=request.user,
            title=title.strip(),
            document=document,
            revision=1,
        )
        return JsonResponse(
            {"draft": _draft_summary(draft), "document": draft.document},
            status=201,
        )

    try:
        draft_id = uuid.UUID(str(raw_id))
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({"detail": "The pilot draft ID is invalid."}, status=400)

    expected_revision = body.get("revision")
    if type(expected_revision) is not int or expected_revision < 1:
        return JsonResponse(
            {"detail": "A valid draft revision is required when updating a saved draft."},
            status=400,
        )

    with transaction.atomic():
        draft = get_object_or_404(
            CourseBuilderTiptapDraft.objects.select_for_update(),
            pk=draft_id,
            owner=request.user,
        )
        if draft.revision != expected_revision:
            return JsonResponse(
                {
                    "detail": (
                        "This pilot draft changed in another session. "
                        "Reload it before saving your changes."
                    ),
                    "current_revision": draft.revision,
                },
                status=409,
            )
        draft.title = title.strip()
        draft.document = document
        draft.revision += 1
        draft.save(update_fields=["title", "document", "revision", "updated_at"])

    return JsonResponse({"draft": _draft_summary(draft), "document": draft.document})

