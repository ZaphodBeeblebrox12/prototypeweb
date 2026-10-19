"""Persistent, permission-checked API for the in-progress Course Builder."""
import base64
import binascii
import hashlib
import json
import re
import uuid
from copy import deepcopy
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from PIL import Image, UnidentifiedImageError

from .importing import validate_import_for_publish
from .models import Course, CourseImport, CourseImportAsset, CourseMediaAsset
from .permissions import is_course_content_admin

_MAX_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_IMAGES = {"image/jpeg": ("JPEG", ".jpg"), "image/png": ("PNG", ".png"), "image/webp": ("WEBP", ".webp")}
_ASSET_REF = re.compile(r"asset://([A-Za-z0-9-]+)")


def _require_admin(request):
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied


def _asset_uuid(course_slug, asset_id):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"tradethesis-course:{course_slug}:builder/{asset_id}"))


def _clean_image_payload(course_state, course_slug):
    """Remove binary data from the JSON snapshot and return upload sources separately."""
    snapshot = deepcopy(course_state)
    images_by_key = {}
    specs_by_key = {}

    for module in snapshot.get("modules", []):
        for lesson in module.get("lessons", []):
            images = lesson.get("images")
            if not isinstance(images, list):
                legacy = lesson.get("image")
                images = [legacy] if isinstance(legacy, dict) else []
                lesson["images"] = images
            for image in images:
                if not isinstance(image, dict):
                    continue
                image_id = str(image.get("id") or uuid.uuid4())
                image["id"] = image_id
                asset_key = f"builder/{image_id}"
                stable_id = _asset_uuid(course_slug, image_id)
                source_data = str(image.get("data") or "")
                images_by_key[asset_key] = source_data
                image["assetKey"] = asset_key
                image["assetUuid"] = stable_id
                image["data"] = ""
                specs_by_key[asset_key] = {
                    "asset_key": asset_key,
                    "stable_asset_id": stable_id,
                    "alt_text": str(image.get("alt") or "")[:500],
                    "source_path": "",
                    "original_url": "",
                    "source_error": "",
                    "sha256": "",
                }
            lesson["image"] = deepcopy(images[0]) if images else None
    return snapshot, images_by_key, specs_by_key


def _build_import_payload(course_state, course_slug):
    snapshot, image_sources, asset_specs = _clean_image_payload(course_state, course_slug)
    modules = []
    seen_module_slugs = set()
    for module_index, module in enumerate(snapshot.get("modules") or [], start=1):
        module_title = str(module.get("title") or f"Module {module_index}").strip()[:200]
        module_slug = slugify(module_title)[:160] or f"module-{module_index}"
        base = module_slug
        suffix = 2
        while module_slug in seen_module_slugs:
            module_slug = f"{base[:150]}-{suffix}"
            suffix += 1
        seen_module_slugs.add(module_slug)
        lessons = []
        seen_lesson_slugs = set()
        for lesson_index, lesson in enumerate(module.get("lessons") or [], start=1):
            title = str(lesson.get("title") or f"Lesson {module_index}.{lesson_index}").strip()[:240]
            lesson_slug = slugify(title)[:160] or f"lesson-{lesson_index}"
            base_lesson_slug = lesson_slug
            suffix = 2
            while lesson_slug in seen_lesson_slugs:
                lesson_slug = f"{base_lesson_slug[:150]}-{suffix}"
                suffix += 1
            seen_lesson_slugs.add(lesson_slug)
            content = str(lesson.get("content") or "")
            image_by_id = {}
            for image in lesson.get("images") or []:
                if isinstance(image, dict) and image.get("id"):
                    image_by_id[str(image["id"])] = str(image.get("assetUuid") or _asset_uuid(course_slug, str(image["id"])))
            for old_id, new_id in image_by_id.items():
                content = content.replace(f"asset://{old_id}", f"asset://{new_id}")
            asset_ids = sorted(set(_ASSET_REF.findall(content)))
            questions = lesson.get("questions") if isinstance(lesson.get("questions"), list) else []
            related_ids = lesson.get("relatedCourseIds") if isinstance(lesson.get("relatedCourseIds"), list) else []
            content_json = {
                "schema_version": 1,
                "source_id": f"{module_index}.{lesson_index}",
                "asset_ids": asset_ids,
                "related_course_ids": [str(value) for value in related_ids if _valid_uuid(value)],
                "notebook": {},
            }
            lessons.append({
                "source_id": f"{module_index}.{lesson_index}",
                "slug": lesson_slug,
                "title": title,
                "summary": str(lesson.get("summary") or "")[:360],
                "position": lesson_index,
                "duration_minutes": max(1, min(360, int(lesson.get("minutes") or 12))),
                "release_day": 1,
                "is_preview": False,
                "format": lesson.get("format") if lesson.get("format") in {"reading", "video", "interactive", "quiz"} else "reading",
                "content_markdown": content.strip(),
                "content_json": content_json,
                "instructor_material": {"questions": questions},
            })
        modules.append({
            "slug": module_slug,
            "title": module_title,
            "summary": str(module.get("description") or "")[:5000],
            "position": module_index,
            "lessons": lessons,
        })

    payload = {
        "schema_version": 1,
        "manifest_version": "course-builder-v1",
        "course": {
            "title": str(snapshot.get("title") or "").strip()[:200],
            "slug": course_slug,
            "summary": str(snapshot.get("summary") or "").strip()[:360],
            "description": str(snapshot.get("description") or "").strip(),
            "position": 0,
        },
        "notebook": {},
        "modules": modules,
        "assets": list(asset_specs.values()),
        "builder_state": snapshot,
    }
    return payload, image_sources


def _valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def _copy_existing_asset(stable_id, target):
    """Reuse a previously uploaded draft/live asset when saving another revision."""
    previous = CourseImportAsset.objects.filter(stable_asset_id=stable_id).exclude(file="").order_by("-updated_at").first()
    if previous and previous.file and previous.file.storage.exists(previous.file.name):
        with previous.file.open("rb") as stream:
            target.file.save(PathName(previous.file.name), ContentFile(stream.read()), save=True)
        return True
    live = CourseMediaAsset.objects.filter(pk=stable_id).exclude(file="").first()
    if live and live.file and live.file.storage.exists(live.file.name):
        with live.file.open("rb") as stream:
            target.file.save(PathName(live.file.name), ContentFile(stream.read()), save=True)
        return True
    return False


def PathName(value):
    return str(value).rsplit("/", 1)[-1] or "course-figure"


def _store_images(record, image_sources):
    for asset in record.assets.all():
        source = image_sources.get(asset.asset_key, "")
        if source.startswith("data:"):
            try:
                header, encoded = source.split(",", 1)
                mime = header[5:].split(";", 1)[0].lower()
                if mime not in _ALLOWED_IMAGES:
                    raise ValueError("Choose a JPEG, PNG or WebP image.")
                raw = base64.b64decode(encoded, validate=True)
                if not raw or len(raw) > _MAX_IMAGE_BYTES:
                    raise ValueError("Each uploaded image must be smaller than 10 MB.")
                with Image.open(BytesIO(raw)) as image:
                    image.verify()
                with Image.open(BytesIO(raw)) as image:
                    expected_format, suffix = _ALLOWED_IMAGES[mime]
                    if image.format != expected_format:
                        raise ValueError("Image file content does not match its declared type.")
                asset.file.save(f"figure{suffix}", ContentFile(raw), save=True)
                asset.alt_text = asset.alt_text[:500]
                asset.source_error = ""
                asset.save(update_fields=["alt_text", "source_error", "updated_at"])
            except (ValueError, binascii.Error, UnidentifiedImageError, OSError) as exc:
                raise ValidationError(f"Could not save image {asset.asset_key}: {exc}") from exc
        elif not (asset.file and asset.file.storage.exists(asset.file.name)):
            _copy_existing_asset(asset.stable_asset_id, asset)


def _draft_response(record, request):
    state = deepcopy(record.payload.get("builder_state") or {})
    for module in state.get("modules", []):
        for lesson in module.get("lessons", []):
            images = lesson.get("images") if isinstance(lesson.get("images"), list) else []
            for image in images:
                stable_id = image.get("assetUuid")
                image["data"] = reverse("staff_course_builder_asset", args=[record.pk, stable_id]) if stable_id else ""
            lesson["image"] = deepcopy(images[0]) if images else None
    state["serverDraftId"] = str(record.pk)
    state["serverUpdatedAt"] = record.imported_at.isoformat()
    state["status"] = "draft"
    return state


@login_required
@require_http_methods(["GET", "POST"])
def course_builder_api(request):
    _require_admin(request)
    if request.method == "GET":
        drafts = []
        for record in CourseImport.objects.filter(status=CourseImport.Status.REVIEW).order_by("-imported_at"):
            if record.payload.get("builder_state"):
                drafts.append(_draft_response(record, request))
        related_courses = list(Course.objects.filter(status=Course.Status.PUBLISHED).order_by("position", "title").values("id", "title", "slug", "summary"))
        return JsonResponse({"drafts": drafts, "related_courses": related_courses})

    try:
        body = json.loads(request.body.decode("utf-8"))
        course_state = body.get("course")
        if not isinstance(course_state, dict):
            return JsonResponse({"detail": "A course draft is required."}, status=400)
        title = str(course_state.get("title") or "").strip()
        slug = slugify(str(course_state.get("slug") or title))[:160]
        if not title or not slug:
            return JsonResponse({"detail": "Add a course title before saving."}, status=400)
        if Course.objects.exclude(status=Course.Status.ARCHIVED).filter(slug=slug).exists():
            existing_course = Course.objects.get(slug=slug)
            if course_state.get("serverCourseId") != str(existing_course.pk):
                return JsonResponse({"detail": "A course with this URL slug already exists. Choose a unique slug or edit the existing course in the Academy."}, status=409)
        course_state["slug"] = slug
        payload, image_sources = _build_import_payload(course_state, slug)
        if not payload["modules"]:
            return JsonResponse({"detail": "Add at least one module before saving."}, status=400)
        for module in payload["modules"]:
            if not module["lessons"]:
                return JsonResponse({"detail": f"Add at least one lesson to {module['title']}."}, status=400)
            for lesson in module["lessons"]:
                from .content_rendering import validate_markdown_source
                validate_markdown_source(lesson["content_markdown"])
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        with transaction.atomic():
            record = CourseImport.objects.filter(
                course_slug=slug, content_hash=digest, status=CourseImport.Status.REVIEW
            ).first()
            created = record is None
            if created:
                CourseImport.objects.filter(course_slug=slug, status=CourseImport.Status.REVIEW).update(status=CourseImport.Status.SUPERSEDED)
                record = CourseImport.objects.create(
                    course_slug=slug,
                    title=title,
                    manifest_version="course-builder-v1",
                    content_hash=digest,
                    source_manifest=f"builder://{slug}",
                    payload=payload,
                    status=CourseImport.Status.REVIEW,
                    imported_by=request.user,
                )
                for spec in payload["assets"]:
                    CourseImportAsset.objects.create(
                        course_import=record,
                        asset_key=spec["asset_key"],
                        stable_asset_id=spec["stable_asset_id"],
                        alt_text=spec.get("alt_text", ""),
                        source_path="",
                        original_url="",
                        source_error="",
                    )
            _store_images(record, image_sources)
        errors = validate_import_for_publish(record)
        review_url = reverse("admin:academy_courseimport_review", args=[record.pk])
        if body.get("mode") == "submit":
            return JsonResponse({
                "ok": True, "submitted": True, "record_id": str(record.pk),
                "review_url": review_url, "publish_errors": errors,
                "message": "Draft saved. Review it before publishing to the course catalogue.",
            })
        return JsonResponse({
            "ok": True, "submitted": False, "record_id": str(record.pk),
            "updated_at": record.imported_at.isoformat(),
            "message": "Draft saved to the Academy. You can reopen it from any computer.",
        })
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
    except (ValidationError, ValueError, TypeError) as exc:
        messages = getattr(exc, "messages", None)
        return JsonResponse({"detail": messages or str(exc)}, status=400)


@login_required
@require_http_methods(["GET"])
def course_builder_asset(request, import_id, asset_id):
    _require_admin(request)
    record = get_object_or_404(CourseImport, pk=import_id)
    asset = get_object_or_404(CourseImportAsset, course_import=record, stable_asset_id=asset_id)
    if not asset.file or not asset.file.storage.exists(asset.file.name):
        raise Http404
    response = FileResponse(
        asset.file.open("rb"),
        content_type=asset.file.file.content_type if hasattr(asset.file.file, "content_type") else "application/octet-stream",
    )
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
