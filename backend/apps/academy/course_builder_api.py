"""Persistent, permission-checked API for the in-progress Course Builder."""
import base64
import binascii
import hashlib
import json
import mimetypes
import re
import uuid
from copy import deepcopy
from urllib.parse import quote

import requests
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

def _sync_course_source_to_github(payload, course_slug):
    """Write the current authoring snapshot to this repo on the feature branch.

    PostgreSQL remains the operational draft store; this versioned JSON source
    snapshot makes the saved course easy to review and recover in GitHub.
    """
    token = getattr(settings, "ACADEMY_GITHUB_ASSET_TOKEN", "").strip()
    repository = getattr(settings, "ACADEMY_GITHUB_ASSET_REPOSITORY", "").strip()
    branch = getattr(settings, "ACADEMY_GITHUB_ASSET_BRANCH", "my-new-branch").strip()
    if not token or not repository:
        return False

    path = f"course-source/builder-drafts/{course_slug}.json"
    encoded_path = "/".join(quote(part, safe="") for part in path.split("/"))
    url = f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        current = requests.get(url, headers=headers, params={"ref": branch}, timeout=15)
        if current.status_code not in {200, 404}:
            raise ValidationError("GitHub could not check the course source file.")
        body = {
            "message": f"Save Course Builder source: {course_slug}",
            "content": base64.b64encode(
                (json.dumps(payload, ensure_ascii=False, indent=2) + "\\n").encode("utf-8")
            ).decode("ascii"),
            "branch": branch,
        }
        if current.status_code == 200:
            body["sha"] = current.json()["sha"]
        saved = requests.put(url, headers=headers, json=body, timeout=20)
        if saved.status_code not in {200, 201}:
            raise ValidationError("GitHub could not save the course source. The draft was not confirmed as synced.")
    except requests.RequestException as exc:
        raise ValidationError("GitHub could not be reached to save the course source.") from exc
    return True



def _asset_uuid(course_slug, asset_id):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"tradethesis-course:{course_slug}:builder/{asset_id}"))


def _clean_image_payload(course_state, course_slug):
    """Remove binary data from the JSON snapshot and return upload sources separately."""
    snapshot = deepcopy(course_state)
    for transient in ("serverDraftId", "serverUpdatedAt", "serverCourseId"):
        snapshot.pop(transient, None)
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
                digest = str(image.get("sha256") or "")
                if source_data.startswith("data:"):
                    try:
                        _header, encoded = source_data.split(",", 1)
                        digest = hashlib.sha256(base64.b64decode(encoded, validate=True)).hexdigest()
                    except (ValueError, binascii.Error) as exc:
                        raise ValidationError(f"Image {image.get('name') or image_id} has invalid encoded data.") from exc
                images_by_key[asset_key] = source_data
                image["assetKey"] = asset_key
                image["assetUuid"] = stable_id
                image["sha256"] = digest
                image["data"] = ""
                specs_by_key[asset_key] = {
                    "asset_key": asset_key,
                    "stable_asset_id": stable_id,
                    "alt_text": str(image.get("alt") or "")[:500],
                    "source_path": "",
                    "original_url": "",
                    "source_error": "",
                    "sha256": digest,
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
            for image in lesson.get("images") or []:
                if not isinstance(image, dict) or not image.get("caption") or not image.get("assetUuid"):
                    continue
                figure_ref = re.compile(r"(!\[[^\]]*\]\(asset://" + re.escape(str(image["assetUuid"])) + r"\))")
                caption = str(image.get("caption", "")).strip()
                content = figure_ref.sub(lambda match: match.group(1) + "\n\n" + caption, content)
            asset_ids = sorted(set(_ASSET_REF.findall(content)))
            questions = lesson.get("questions") if isinstance(lesson.get("questions"), list) else []
            learner_questions = []
            for question_index, question in enumerate(questions, start=1):
                if not isinstance(question, dict):
                    continue
                options = question.get("options") if isinstance(question.get("options"), list) else []
                learner_questions.append({
                    "id": str(question.get("id") or f"question-{module_index}-{lesson_index}-{question_index}"),
                    "prompt": str(question.get("prompt") or "").strip()[:2000],
                    "options": [str(option)[:1000] for option in options[:8]],
                })
            related_ids = lesson.get("relatedCourseIds") if isinstance(lesson.get("relatedCourseIds"), list) else []
            notebook = lesson.get("notebook") if isinstance(lesson.get("notebook"), dict) else {}
            prompts = notebook.get("prompts") if isinstance(notebook.get("prompts"), list) else []
            clean_prompts = []
            for prompt in prompts[:6]:
                if not isinstance(prompt, dict):
                    continue
                label = str(prompt.get("label") or "").strip()[:80]
                text = str(prompt.get("text") or "").strip()[:1000]
                if label and text:
                    clean_prompts.append({"label": label, "text": text})
            notebook_payload = {
                "title": str(notebook.get("title") or "Your Trading Notebook").strip()[:160],
                "prompts": clean_prompts,
            }
            video_url = str(lesson.get("videoUrl") or "").strip()[:1000]
            if video_url and not video_url.startswith(("https://", "http://")):
                raise ValidationError(f"{title}: video URL must use HTTPS or HTTP.")
            content_json = {
                "schema_version": 1,
                "source_id": f"{module_index}.{lesson_index}",
                "asset_ids": asset_ids,
                "related_course_ids": [str(value) for value in related_ids if _valid_uuid(value)],
                "questions": learner_questions,
                "notebook": notebook_payload,
                "video_url": video_url,
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
            "category": str(snapshot.get("category") or "").strip()[:80],
            "level": str(snapshot.get("level") or "").strip()[:40],
            "estimated_duration": str(snapshot.get("duration") or "").strip()[:80],
            "learning_outcomes": [str(value).strip()[:500] for value in (snapshot.get("outcomes") or []) if str(value).strip()][:20],
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
    state["serverUpdatedAt"] = record.updated_at.isoformat()
    state["status"] = "draft"
    return state


@login_required
@require_http_methods(["GET", "POST"])
def course_builder_api(request):
    _require_admin(request)
    if request.method == "GET":
        drafts = []
        for record in CourseImport.objects.filter(status=CourseImport.Status.DRAFT).order_by("-updated_at"):
            if record.payload.get("builder_state"):
                drafts.append(_draft_response(record, request))
        related_courses = list(Course.objects.filter(
            status=Course.Status.PUBLISHED,
            modules__is_published=True,
            modules__lessons__is_published=True,
        ).distinct().order_by("position", "title").values("id", "title", "slug", "summary"))
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
        mode = body.get("mode", "save")
        if mode not in {"save", "submit"}:
            return JsonResponse({"detail": "Unsupported draft action."}, status=400)

        with transaction.atomic():
            draft = CourseImport.objects.filter(
                course_slug=slug, status=CourseImport.Status.DRAFT,
            ).first()
            conflicting = CourseImport.objects.filter(
                course_slug=slug, content_hash=digest,
            )
            if draft is not None:
                conflicting = conflicting.exclude(pk=draft.pk)
            conflict = conflicting.first()
            if conflict is not None:
                # The same content may already have been reviewed or published.
                # A new editable draft needs its own immutable hash identity.
                payload["builder_revision"] = str(uuid.uuid4())
                encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                digest = hashlib.sha256(encoded).hexdigest()

            if draft is None:
                record = CourseImport.objects.create(
                    course_slug=slug,
                    title=title,
                    manifest_version="course-builder-v1",
                    content_hash=digest,
                    source_manifest=f"builder://{slug}",
                    payload=payload,
                    status=CourseImport.Status.DRAFT,
                    imported_by=request.user,
                )
            else:
                record = draft
                record.title = title
                record.manifest_version = "course-builder-v1"
                record.content_hash = digest
                record.source_manifest = f"builder://{slug}"
                record.payload = payload
                record.imported_by = request.user
                record.save(update_fields=[
                    "title", "manifest_version", "content_hash", "source_manifest",
                    "payload", "imported_by", "updated_at",
                ])

            existing_assets = {asset.asset_key: asset for asset in record.assets.all()}
            for spec in payload["assets"]:
                asset = existing_assets.pop(spec["asset_key"], None)
                if asset is None:
                    CourseImportAsset.objects.create(
                        course_import=record,
                        asset_key=spec["asset_key"],
                        stable_asset_id=spec["stable_asset_id"],
                        alt_text=spec.get("alt_text", ""),
                        source_path="",
                        original_url="",
                        source_error="",
                    )
                else:
                    asset.stable_asset_id = spec["stable_asset_id"]
                    asset.alt_text = spec.get("alt_text", "")
                    asset.source_error = ""
                    asset.save(update_fields=["stable_asset_id", "alt_text", "source_error", "updated_at"])
            for removed_asset in existing_assets.values():
                if removed_asset.file:
                    removed_asset.file.delete(save=False)
                removed_asset.delete()

            _store_images(record, image_sources)
            errors = validate_import_for_publish(record)
            if mode == "submit" and errors:
                return JsonResponse({
                    "detail": "The draft needs attention before it can be submitted.",
                    "publish_errors": errors,
                }, status=400)
            if mode == "submit":
                CourseImport.objects.filter(
                    course_slug=slug, status=CourseImport.Status.REVIEW,
                ).exclude(pk=record.pk).update(status=CourseImport.Status.SUPERSEDED)
                record.status = CourseImport.Status.REVIEW
                record.save(update_fields=["status", "updated_at"])

            github_source_synced = _sync_course_source_to_github(payload, slug)

        review_url = reverse("admin:academy_courseimport_review", args=[record.pk])
        if mode == "submit":
            return JsonResponse({
                "ok": True, "submitted": True, "record_id": str(record.pk),
                "review_url": review_url, "publish_errors": [],
                "draft": _draft_response(record, request),
                "github_source_synced": github_source_synced,
                "message": (
                    "Draft submitted and source saved to GitHub. Review it before publishing to the course catalogue."
                    if github_source_synced else
                    "Draft submitted to the Academy, but GitHub source sync is not configured. Add ACADEMY_GITHUB_ASSET_TOKEN to enable repository saves."
                ),
            })
        return JsonResponse({
            "ok": True, "submitted": False, "record_id": str(record.pk),
            "updated_at": record.updated_at.isoformat(),
            "draft": _draft_response(record, request),
            "github_source_synced": github_source_synced,
            "message": (
                "Draft saved to the Academy and source synced to the existing GitHub repository."
                if github_source_synced else
                "Draft saved to the Academy, but GitHub source sync is not configured. Add ACADEMY_GITHUB_ASSET_TOKEN to enable repository saves."
            ),
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
        content_type=mimetypes.guess_type(asset.file.name)[0] or "application/octet-stream",
    )
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
