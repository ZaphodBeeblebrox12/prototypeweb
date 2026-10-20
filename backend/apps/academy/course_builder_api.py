"""Persistent, permission-checked API for the in-progress Course Builder."""
import base64
import binascii
import hashlib
import json
import logging
import mimetypes
import re
import uuid
from copy import deepcopy
from io import BytesIO
from urllib.parse import quote

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from PIL import Image, UnidentifiedImageError

from .importing import validate_import_for_publish
from .models import (
    Course,
    CourseImport,
    CourseImportAsset,
    CourseMediaAsset,
    GoogleDriveCredential,
    Lesson,
)
from .permissions import is_course_content_admin
from .storage import course_asset_storage

logger = logging.getLogger(__name__)

_MAX_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_IMAGES = {"image/jpeg": ("JPEG", ".jpg"), "image/png": ("PNG", ".png"), "image/webp": ("WEBP", ".webp")}
_ASSET_REF = re.compile(r"asset://([A-Za-z0-9-]+)")
_LESSON_REF_TOKEN = re.compile(r"\[\[(?:lesson|lesson-card):([0-9a-fA-F-]{36})\]\]")


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
        raise ValidationError(
            "GitHub source sync is not configured; set ACADEMY_GITHUB_ASSET_TOKEN "
            "and verify ACADEMY_GITHUB_ASSET_REPOSITORY."
        )

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
                (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            ).decode("ascii"),
            "branch": branch,
        }
        if current.status_code == 200:
            try:
                current_payload = current.json()
            except (ValueError, AttributeError) as exc:
                raise ValidationError("GitHub returned an unreadable course source response.") from exc
            current_sha = current_payload.get("sha") if isinstance(current_payload, dict) else None
            if not current_sha:
                raise ValidationError("GitHub returned an incomplete course source response.")
            body["sha"] = current_sha
        saved = requests.put(url, headers=headers, json=body, timeout=20)
        if saved.status_code not in {200, 201}:
            raise ValidationError("GitHub could not save the course source. The draft was not confirmed as synced.")
        try:
            saved_payload = saved.json()
        except (ValueError, AttributeError) as exc:
            raise ValidationError("GitHub returned an unreadable save confirmation.") from exc
        if (
            not isinstance(saved_payload, dict)
            or not isinstance(saved_payload.get("content"), dict)
            or not saved_payload["content"].get("sha")
            or not isinstance(saved_payload.get("commit"), dict)
            or not saved_payload["commit"].get("sha")
        ):
            raise ValidationError("GitHub did not confirm the saved course source.")
    except requests.RequestException as exc:
        raise ValidationError("GitHub could not be reached to save the course source.") from exc
    return True


class CourseSourceSyncError(Exception):
    """Safe, retryable failure from the external course-source backup."""


def _sync_course_source_to_storage(payload, course_slug):
    """Prefer Google Drive for durable source snapshots; keep GitHub as migration fallback."""
    service_account_ready = bool(
        getattr(settings, "ACADEMY_GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", "")
        and getattr(settings, "ACADEMY_GOOGLE_DRIVE_ASSET_FOLDER_ID", "")
        and getattr(settings, "ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID", "")
    )
    oauth_ready = bool(
        getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_ID", "")
        and getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET", "")
        and ((getattr(settings, "ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN", "")
              and getattr(settings, "ACADEMY_GOOGLE_DRIVE_ASSET_FOLDER_ID", "")
              and getattr(settings, "ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID", ""))
             or GoogleDriveCredential.objects.filter(
                 pk=1, encrypted_refresh_token__gt="", asset_folder_id__gt="", source_folder_id__gt=""
             ).exists())
    )
    if service_account_ready or oauth_ready:
        try:
            course_asset_storage.save_source_snapshot(payload, course_slug)
            return "google_drive"
        except (ImproperlyConfigured, OSError, ValueError, TypeError) as exc:
            raise CourseSourceSyncError(
                "Google Drive could not confirm the course source snapshot. "
                "The latest draft remains saved in the Academy as a draft; please retry."
            ) from exc
    try:
        _sync_course_source_to_github(payload, course_slug)
        return "github"
    except ValidationError as exc:
        messages = getattr(exc, "messages", None)
        message = " ".join(str(value) for value in messages) if messages else "GitHub source sync failed."
        raise CourseSourceSyncError(
            f"{message} The latest draft remains saved in the Academy as a draft; please retry."
        ) from exc


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
                image["alt"] = str(image.get("alt") or "").strip()[:500]
                image["caption"] = str(image.get("caption") or "").strip()[:500]
                display_title = str(image.get("title") or "").strip()
                if display_title and display_title == str(image.get("name") or "").strip():
                    display_title = ""
                # The visible heading is author-entered metadata only; alt text and
                # captions remain separate and a filename is never promoted to a title.
                image["title"] = display_title[:240]
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
            # Grouped images are referenced by a semantic token instead of individual
            # Markdown image tokens. Resolve group membership to stable asset UUIDs, and
            # count those assets as lesson references for delivery/access checks.
            image_group_asset_ids = {}
            for image_group in lesson.get("imageGroups") or []:
                if not isinstance(image_group, dict):
                    continue
                group_id = str(image_group.get("id") or "").strip()
                if not group_id or not re.search(
                    r"\[\[image-group:" + re.escape(group_id) + r"\]\]", content,
                ):
                    continue
                stable_ids = []
                raw_ids = image_group.get("imageIds") if isinstance(image_group.get("imageIds"), list) else []
                for raw_id in raw_ids:
                    stable_id = image_by_id.get(str(raw_id))
                    if stable_id and stable_id not in stable_ids:
                        stable_ids.append(stable_id)
                if len(stable_ids) >= 2:
                    image_group_asset_ids[group_id] = stable_ids

            # Keep figure placement inside the authored Markdown. Titles, alt text and captions
            # travel separately with stable asset UUIDs; do not append captions to the prose.
            asset_ids = sorted(
                set(_ASSET_REF.findall(content))
                | {asset_id for group_ids in image_group_asset_ids.values() for asset_id in group_ids}
            )
            referenced_assets = set(asset_ids)
            figures = {
                str(image.get("assetUuid")): {
                    "title": str(image.get("title") or "").strip()[:240],
                    "alt": str(image.get("alt") or "").strip()[:500],
                    "caption": str(image.get("caption") or "").strip()[:500],
                }
                for image in lesson.get("images") or []
                if isinstance(image, dict)
                and image.get("assetUuid")
                and str(image.get("assetUuid")) in referenced_assets
            }
            # Multi-image groups render as one named figure with a module label
            # and a responsive image grid. Individual image titles/captions remain editable.
            for group_id, stable_ids in image_group_asset_ids.items():
                image_group = next(
                    item for item in (lesson.get("imageGroups") or [])
                    if isinstance(item, dict) and str(item.get("id") or "").strip() == group_id
                )
                figures[group_id] = {
                    "type": "image-group",
                    "title": str(image_group.get("title") or "").strip()[:240],
                    "image_ids": stable_ids,
                    "note": str(image_group.get("note") or "").strip()[:1500],
                }

            # Purpose-built comparison-card figures are authored content blocks, not image files.
            # Keep their data beside the stable token so the same renderer can show them in every view.
            for figure in lesson.get("teachingFigures") or []:
                if not isinstance(figure, dict):
                    continue
                figure_id = str(figure.get("id") or "").strip()
                if not figure_id or not re.search(
                    r"\[\[teaching-figure:" + re.escape(figure_id) + r"\]\]",
                    content,
                ):
                    continue
                cards = []
                raw_cards = figure.get("cards") if isinstance(figure.get("cards"), list) else []
                for card in raw_cards[:4]:
                    if not isinstance(card, dict):
                        continue
                    cards.append({
                        "kicker": str(card.get("kicker") or "").strip()[:100],
                        "title": str(card.get("title") or "").strip()[:240],
                        "body": str(card.get("body") or "").strip()[:1000],
                    })
                figures[figure_id] = {
                    "type": "comparison-cards",
                    "title": str(figure.get("title") or "Comparison").strip()[:240],
                    "cards": cards,
                    "note": str(figure.get("note") or "").strip()[:1500],
                }
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
                "figures": figures,
                "lesson_reference_ids": sorted({
                    str(uuid.UUID(value))
                    for value in _LESSON_REF_TOKEN.findall(content)
                    if _valid_uuid(value)
                }),
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
            target.file.save(path_name(previous.file.name), ContentFile(stream.read()), save=True)
        return True
    live = CourseMediaAsset.objects.filter(pk=stable_id).exclude(file="").first()
    if live and live.file and live.file.storage.exists(live.file.name):
        with live.file.open("rb") as stream:
            target.file.save(path_name(live.file.name), ContentFile(stream.read()), save=True)
        return True
    return False


def path_name(value):
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
            except (ImproperlyConfigured, ValueError, binascii.Error, UnidentifiedImageError, OSError) as exc:
                raise ValidationError(f"Could not save image {asset.asset_key}: {exc}") from exc
        elif asset.file:
            storage = asset.file.storage
            storage_status = storage.status()
            if storage_status.get("durable"):
                # The usual exists() intentionally includes local fallback for
                # compatibility. Check remote providers separately so a local file
                # is migrated instead of being mistaken for a durable upload.
                if not storage.remote_exists(asset.file.name):
                    if not _copy_existing_asset(asset.stable_asset_id, asset):
                        raise ValidationError(
                            f"Image {asset.asset_key} is only present in temporary storage. "
                            "Re-upload it before relying on this lesson."
                        )
            elif not storage.exists(asset.file.name):
                _copy_existing_asset(asset.stable_asset_id, asset)
        else:
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
        # Return catalogue metadata only (never lesson bodies or instructor
        # answer keys). This lets the Builder search references after drafts
        # are reopened on another device without persisting copied lesson text.
        lesson_references = []
        published_lessons = Lesson.objects.filter(
            module__course__status=Course.Status.PUBLISHED,
            module__is_published=True,
            is_published=True,
        ).select_related("module__course", "module").order_by(
            "module__course__position", "module__position", "position", "title",
        )
        for lesson in published_lessons:
            topics = re.findall(
                r"^#{1,6}\s+(.+?)\s*$",
                lesson.content_markdown or "",
                re.MULTILINE,
            )[:8]
            lesson_references.append({
                "id": str(lesson.pk),
                "title": lesson.title,
                "summary": lesson.summary,
                "module_title": lesson.module.title,
                "course_id": str(lesson.module.course_id),
                "course_title": lesson.module.course.title,
                "course_slug": lesson.module.course.slug,
                "topics": topics,
            })
        asset_storage_status = course_asset_storage.status()
        logger.info(
            "Course Builder asset storage configured: backend=%s durable=%s writes_enabled=%s",
            asset_storage_status["backend"],
            asset_storage_status["durable"],
            asset_storage_status["writes_enabled"],
        )
        return JsonResponse({
            "drafts": drafts,
            "related_courses": related_courses,
            "lesson_references": lesson_references,
            "asset_storage": asset_storage_status,
        })

    try:
        body = json.loads(request.body.decode("utf-8"))
        course_state = body.get("course")
        if not isinstance(course_state, dict):
            return JsonResponse({"detail": "A course draft is required."}, status=400)
        title = str(course_state.get("title") or "").strip()
        slug = slugify(str(course_state.get("slug") or title))[:160]
        if not title or not slug:
            return JsonResponse({"detail": "Add a course title before saving."}, status=400)
        existing_course = Course.objects.exclude(status=Course.Status.ARCHIVED).filter(slug=slug).first()
        if existing_course and course_state.get("serverCourseId") != str(existing_course.pk):
            # Re-saving an already-created Course Builder draft must remain possible
            # even if a Course row with this slug now exists. A matching draft ID is
            # proof that this request is updating its own draft, not creating a second
            # import against an existing Academy course.
            server_draft_id = str(course_state.get("serverDraftId") or "")
            owns_existing_draft = (
                _valid_uuid(server_draft_id)
                and CourseImport.objects.filter(
                    pk=server_draft_id,
                    course_slug=slug,
                    status=CourseImport.Status.DRAFT,
                ).exists()
            )
            if not owns_existing_draft:
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
        sync_source_requested = bool(body.get("sync_source", mode == "submit"))
        if mode not in {"save", "submit"}:
            return JsonResponse({"detail": "Unsupported draft action."}, status=400)

        with transaction.atomic():
            # Lock an existing draft so overlapping submissions serialize.
            draft = CourseImport.objects.select_for_update().filter(
                course_slug=slug, status=CourseImport.Status.DRAFT,
            ).first()
            if mode == "submit" and draft is None:
                # The browser may retry after the server accepted a submission
                # but the redirect to the review page failed. Reuse an identical
                # review record rather than creating a duplicate import.
                existing_review = CourseImport.objects.filter(
                    course_slug=slug,
                    content_hash=digest,
                    status=CourseImport.Status.REVIEW,
                ).order_by("-imported_at").first()
                if existing_review is not None:
                    review_url = reverse(
                        "admin:academy_courseimport_review",
                        args=[existing_review.pk],
                    )
                    return JsonResponse({
                        "ok": True,
                        "submitted": True,
                        "record_id": str(existing_review.pk),
                        "review_url": review_url,
                        "publish_errors": [],
                        "github_source_synced": None,
                        "source_snapshot_backend": None,
                        "source_snapshot_synced": False,
                        "message": "This course version is already awaiting review. No duplicate submission was created.",
                    })
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
            if not sync_source_requested:
                for removed_asset in existing_assets.values():
                    if removed_asset.file:
                        storage = removed_asset.file.storage
                        name = removed_asset.file.name
                        transaction.on_commit(
                            lambda storage=storage, name=name: storage.delete(name),
                            robust=True,
                        )
                    removed_asset.delete()

            _store_images(record, image_sources)
            errors = validate_import_for_publish(record)
            if mode == "submit" and errors:
                return JsonResponse({
                    "detail": "The draft needs attention before it can be submitted.",
                    "publish_errors": errors,
                }, status=400)
            # Keep review transitions and stale-asset deletion until after a
            # requested remote source snapshot has been confirmed.

        source_snapshot_backend = (
            _sync_course_source_to_storage(payload, slug)
            if sync_source_requested else None
        )
        github_source_synced = (
            source_snapshot_backend == "github"
            if source_snapshot_backend is not None else None
        )

        # Re-lock the record and make sure the content did not change while
        # the remote request was in flight. Do not mark a stale version for review.
        with transaction.atomic():
            current_record = CourseImport.objects.select_for_update().get(pk=record.pk)
            if current_record.content_hash != digest:
                return JsonResponse({
                    "detail": "The draft changed while its source snapshot was being saved. The latest draft remains saved; retry the save or submission.",
                    "retryable": True,
                    "draft_preserved": True,
                }, status=409)
            desired_asset_keys = {
                str(item.get("asset_key"))
                for item in (current_record.payload.get("assets") or [])
                if isinstance(item, dict) and item.get("asset_key")
            }
            for stale_asset in current_record.assets.exclude(asset_key__in=desired_asset_keys):
                if stale_asset.file:
                    storage = stale_asset.file.storage
                    name = stale_asset.file.name
                    transaction.on_commit(
                        lambda storage=storage, name=name: storage.delete(name),
                        robust=True,
                    )
                stale_asset.delete()
            if mode == "submit":
                CourseImport.objects.filter(
                    course_slug=slug, status=CourseImport.Status.REVIEW,
                ).exclude(pk=current_record.pk).update(status=CourseImport.Status.SUPERSEDED)
                current_record.status = CourseImport.Status.REVIEW
                current_record.save(update_fields=["status", "updated_at"])
            record = current_record

        review_url = reverse("admin:academy_courseimport_review", args=[record.pk])
        if mode == "submit":
            return JsonResponse({
                "ok": True, "submitted": True, "record_id": str(record.pk),
                "review_url": review_url, "publish_errors": [],
                "draft": _draft_response(record, request),
                "github_source_synced": github_source_synced,
                "source_snapshot_backend": source_snapshot_backend,
                "source_snapshot_synced": source_snapshot_backend is not None,
                "message": (
                    "Draft submitted and source snapshot saved to Google Drive. Review it before publishing to the course catalogue."
                    if source_snapshot_backend == "google_drive" else
                    "Draft submitted and source snapshot synced to GitHub. Review it before publishing to the course catalogue."
                    if source_snapshot_backend == "github" else
                    "Draft submitted to the Academy. No external source snapshot was requested."
                ),
            })
        return JsonResponse({
            "ok": True, "submitted": False, "record_id": str(record.pk),
            "updated_at": record.updated_at.isoformat(),
            "website_preview_url": reverse("academy:course-import-preview", args=[record.pk]),
            "draft": _draft_response(record, request),
            "github_source_synced": github_source_synced,
            "source_snapshot_backend": source_snapshot_backend,
            "source_snapshot_synced": source_snapshot_backend is not None,
            "message": (
                "Draft saved to the Academy and source snapshot saved to Google Drive."
                if source_snapshot_backend == "google_drive" else
                "Draft saved to the Academy and source snapshot synced to GitHub."
                if source_snapshot_backend == "github" else
                "Draft autosaved to the Academy. Use Save draft to create a source snapshot."
            ),
        })
    except CourseSourceSyncError as exc:
        return JsonResponse({
            "detail": str(exc),
            "retryable": True,
            "draft_preserved": True,
            "record_id": str(record.pk),
        }, status=503)
    except (ImproperlyConfigured, OSError):
        return JsonResponse({
            "detail": "Course storage is temporarily unavailable or not configured for durable image writes. Any previously saved draft remains unchanged; please connect Google Drive or configure GitHub storage, then retry.",
            "retryable": True,
            "draft_preserved": bool(draft is not None),
        }, status=503)
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
