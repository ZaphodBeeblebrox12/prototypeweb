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
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from PIL import Image, UnidentifiedImageError

from .course_builder_lifecycle import mark_builder_draft_deleted
from .course_card_utils import is_course_card_recommendable
from .importing import validate_import_for_publish
from .models import (
    Course,
    CourseImport,
    CourseImportAsset,
    CourseMediaAsset,
    GoogleDriveCredential,
    Lesson,
    LessonInstructorMaterial,
)
from .permissions import is_course_content_admin
from .storage import course_asset_storage

logger = logging.getLogger(__name__)

_MAX_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_IMAGES = {"image/jpeg": ("JPEG", ".jpg"), "image/png": ("PNG", ".png"), "image/webp": ("WEBP", ".webp")}
_ASSET_REF = re.compile(r"asset://([A-Za-z0-9-]+)")
_REGIONAL_BLOCK_TOKEN = re.compile(r"\[\[regional-block:([A-Za-z0-9_-]{1,120})\]\]")
_ALLOWED_CONTENT_REGIONS = {"APAC", "EU", "NA", "LATAM", "MENA", "SSA"}
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
    server_draft_id = str(course_state.get("serverDraftId") or "").strip()
    server_course_id = str(course_state.get("serverCourseId") or "").strip()
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
                requested_stable_id = str(image.get("assetUuid") or "")
                may_reuse_stable_id = False
                if _valid_uuid(requested_stable_id):
                    if server_course_id and _valid_uuid(server_course_id):
                        may_reuse_stable_id = CourseMediaAsset.objects.filter(
                            pk=requested_stable_id, course_id=server_course_id,
                        ).exists()
                    if not may_reuse_stable_id and server_draft_id and _valid_uuid(server_draft_id):
                        may_reuse_stable_id = CourseImportAsset.objects.filter(
                            course_import_id=server_draft_id, stable_asset_id=requested_stable_id,
                        ).exists()
                stable_id = requested_stable_id if may_reuse_stable_id else _asset_uuid(course_slug, image_id)
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

            # Images assigned to practice questions are instructional assets too, even though
            # their placement is outside the lesson Markdown body.
            questions = lesson.get("questions") if isinstance(lesson.get("questions"), list) else []
            question_image_ids = set()
            for question in questions:
                if not isinstance(question, dict):
                    continue
                builder_image_id = str(question.get("imageId") or "").strip()
                stable_image_id = image_by_id.get(builder_image_id)
                if stable_image_id:
                    question_image_ids.add(stable_image_id)

            # Regional content blocks occupy an explicit marker in the lesson body.
            # Store country/region alternatives in learner-safe JSON, and allow their
            # assets through the same publication and protected-media authorization path.
            def remap_regional_assets(value, image_mapping, referenced_asset_ids):
                value = str(value or "")[:40000]
                for old_id, stable_id in image_mapping.items():
                    value = value.replace(f"asset://{old_id}", f"asset://{stable_id}")
                referenced_asset_ids.update(_ASSET_REF.findall(value))
                return value

            regional_blocks_payload = {}
            regional_block_asset_ids = set()
            raw_regional_blocks = lesson.get("regionalBlocks") if isinstance(lesson.get("regionalBlocks"), list) else []
            active_regional_markers = set(_REGIONAL_BLOCK_TOKEN.findall(content))
            for block in raw_regional_blocks[:100]:
                if not isinstance(block, dict):
                    continue
                block_id = str(block.get("id") or "").strip()
                if not block_id or not re.fullmatch(r"[A-Za-z0-9_-]{1,120}", block_id):
                    raise ValidationError(f"{title}: a regional content block has an invalid ID.")
                if block_id in regional_blocks_payload:
                    raise ValidationError(f"{title}: duplicate regional content block ID {block_id}.")
                if block_id not in active_regional_markers:
                    # Keep unused authoring blocks in builder_state, not learner JSON.
                    continue

                base_content = remap_regional_assets(
                    block.get("baseContent", ""), image_by_id, regional_block_asset_ids
                )
                variants = []
                seen_variant_targets = set()
                raw_variants = block.get("variants") if isinstance(block.get("variants"), list) else []
                if len(raw_variants) > 30:
                    raise ValidationError(f"{title}: a regional block may contain at most 30 variants.")
                for variant_index, variant in enumerate(raw_variants, start=1):
                    if not isinstance(variant, dict):
                        continue
                    scope = str(variant.get("scope") or "country").strip().lower()
                    code = str(variant.get("code") or ("IN" if scope == "country" else "APAC")).strip().upper()
                    if scope == "country":
                        if len(code) != 2 or not code.isalpha() or not code.isascii():
                            raise ValidationError(f"{title}: country variants must use a two-letter country code.")
                    elif scope == "region":
                        if code not in _ALLOWED_CONTENT_REGIONS:
                            raise ValidationError(f"{title}: unsupported regional audience {code}.")
                    else:
                        raise ValidationError(f"{title}: regional variant scope must be country or region.")
                    target_key = (scope, code)
                    if target_key in seen_variant_targets:
                        raise ValidationError(f"{title}: regional block {block_id} repeats the {code} audience.")
                    seen_variant_targets.add(target_key)
                    variant_id = str(variant.get("id") or f"{block_id}-variant-{variant_index}")[:150]
                    variants.append({
                        "id": variant_id,
                        "scope": scope,
                        "code": code,
                        "content": remap_regional_assets(variant.get("content", ""), image_by_id, regional_block_asset_ids),
                        "hidden": bool(variant.get("hidden", False)),
                    })
                regional_blocks_payload[block_id] = {
                    "id": block_id,
                    "title": str(block.get("title") or "Regional content").strip()[:240],
                    "base_content": base_content,
                    "variants": variants,
                }

            # Keep figure placement inside authored Markdown; questions may reference the same
            # assets independently. Titles, alt text and captions travel in figure metadata.
            asset_ids = sorted(
                set(_ASSET_REF.findall(content))
                | regional_block_asset_ids
                | {asset_id for group_ids in image_group_asset_ids.values() for asset_id in group_ids}
                | question_image_ids
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
            learner_questions = []
            for question_index, question in enumerate(questions, start=1):
                if not isinstance(question, dict):
                    continue
                options = question.get("options") if isinstance(question.get("options"), list) else []
                public_question = {
                    "id": str(question.get("id") or f"question-{module_index}-{lesson_index}-{question_index}"),
                    "prompt": str(question.get("prompt") or "").strip()[:2000],
                    "options": [str(option)[:1000] for option in options[:8]],
                }
                builder_image_id = str(question.get("imageId") or "").strip()
                stable_image_id = image_by_id.get(builder_image_id)
                if stable_image_id:
                    public_question["image_asset_id"] = stable_image_id
                learner_questions.append(public_question)
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
            reflection = {
                "prompt": str(
                    lesson.get("reflectionPrompt")
                    if "reflectionPrompt" in lesson
                    else "Before opening the model reasoning, write one observable fact, one possible interpretation, and one thing that would change your view."
                ).strip()[:1000],
                "model_reasoning": str(
                    lesson.get("reflectionModelReasoning")
                    if "reflectionModelReasoning" in lesson
                    else "A careful reading separates visible evidence from interpretation, considers a reasonable alternative, and names the evidence that would strengthen or weaken the interpretation."
                ).strip()[:3000],
                "chart_notes": str(lesson.get("reflectionChartNotes") or "").strip()[:3000],
            }
            content_json = {
                "schema_version": 1,
                "reflection": reflection,
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
                "regional_blocks": regional_blocks_payload,
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
            "position": max(0, min(32767, int(snapshot.get("position") or 0))),
            "requires_owned_assets": bool(snapshot.get("requiresOwnedAssets", False)),
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
            if storage_status.get("durable") and not storage.remote_exists(asset.file.name):
                # The usual exists() intentionally includes local fallback for
                # compatibility. Check remote providers separately so a local file
                # is migrated instead of being mistaken for a durable upload.
                if not _copy_existing_asset(asset.stable_asset_id, asset):
                    raise ValidationError(
                        f"Image {asset.asset_key} is only present in temporary storage. "
                        "Re-upload it before relying on this lesson."
                    )
            elif not storage.exists(asset.file.name):
                _copy_existing_asset(asset.stable_asset_id, asset)
        else:
            _copy_existing_asset(asset.stable_asset_id, asset)


def _retire_legacy_drafts_for_deleted_courses(records):
    """Retire old builder drafts left behind by pre-fix Django Admin deletions.

    Course deletion is recorded in Django's admin log. Legacy Builder drafts
    were not linked to the Course row, so older deletions left their imports
    active. Only reconcile an absent Course whose title-derived slug and exact
    deleted title match a logged deletion that occurred after the draft began.
    """
    builder_records = [
        record for record in records
        if record.payload.get("builder_state")
        and slugify(record.title) == record.course_slug
    ]
    if not builder_records:
        return set()

    slugs = {record.course_slug for record in builder_records}
    active_slugs = set(
        Course.objects.filter(slug__in=slugs).values_list("slug", flat=True)
    )
    candidate_titles = {
        record.title for record in builder_records
        if record.course_slug not in active_slugs
    }
    if not candidate_titles:
        return set()

    course_content_type = ContentType.objects.get_for_model(Course)
    deletion_rows = LogEntry.objects.filter(
        content_type=course_content_type,
        action_flag=DELETION,
        object_repr__in=candidate_titles,
    ).values_list("object_repr", "action_time")

    latest_deletion_by_title = {}
    for title, action_time in deletion_rows:
        if title not in latest_deletion_by_title or action_time > latest_deletion_by_title[title]:
            latest_deletion_by_title[title] = action_time

    retired_ids = set()
    for record in builder_records:
        deleted_at = latest_deletion_by_title.get(record.title)
        if (
            record.course_slug not in active_slugs
            and deleted_at is not None
            and deleted_at >= record.imported_at
        ):
            with transaction.atomic():
                locked = CourseImport.objects.select_for_update().filter(
                    pk=record.pk, status=CourseImport.Status.DRAFT,
                ).first()
                if locked and locked.payload.get("builder_state"):
                    mark_builder_draft_deleted(locked)
                    retired_ids.add(str(locked.pk))
    return retired_ids


def _builder_state_from_published_course(course):
    """Hydrate published learner content and private authoring material for a revision."""
    all_assets = {str(asset.pk): asset for asset in course.media_assets.all()}
    modules = []
    for module in course.modules.filter(is_published=True).order_by("position", "title"):
        lessons = []
        for lesson in module.lessons.filter(is_published=True).order_by("position", "title"):
            content_json = lesson.content_json if isinstance(lesson.content_json, dict) else {}
            figures = content_json.get("figures") if isinstance(content_json.get("figures"), dict) else {}
            asset_ids = {str(value) for value in content_json.get("asset_ids", []) if value}
            asset_ids.update(_ASSET_REF.findall(lesson.content_markdown or ""))
            image_groups, teaching_figures = [], []
            for figure_id, figure in figures.items():
                if not isinstance(figure, dict):
                    continue
                if figure.get("type") == "image-group":
                    group_ids = [str(value) for value in figure.get("image_ids", []) if value]
                    asset_ids.update(group_ids)
                    image_groups.append({
                        "id": str(figure_id), "title": str(figure.get("title") or ""),
                        "imageIds": group_ids, "note": str(figure.get("note") or ""),
                    })
                elif figure.get("type") == "comparison-cards":
                    teaching_figures.append({
                        "id": str(figure_id), "title": str(figure.get("title") or "Comparison"),
                        "cards": deepcopy(figure.get("cards") or []), "note": str(figure.get("note") or ""),
                    })
                elif str(figure_id) in all_assets:
                    asset_ids.add(str(figure_id))
            images = []
            for asset_id in sorted(asset_ids):
                asset = all_assets.get(asset_id)
                if asset is None:
                    continue
                metadata = figures.get(asset_id, {}) if isinstance(figures.get(asset_id), dict) else {}
                stored_name = asset.file.name if asset.file else asset.source_path
                images.append({
                    "id": asset_id, "assetUuid": asset_id, "assetKey": asset.asset_key,
                    "name": stored_name.rsplit("/", 1)[-1] if stored_name else asset.asset_key.rsplit("/", 1)[-1],
                    "title": str(metadata.get("title") or ""),
                    "alt": str(metadata.get("alt") or asset.alt_text or ""),
                    "caption": str(metadata.get("caption") or ""),
                    "data": reverse("academy:media-asset", args=[asset.pk]) if asset.file else "",
                })
            public_questions = [
                item for item in content_json.get("questions", []) if isinstance(item, dict)
            ] if isinstance(content_json.get("questions"), list) else []
            try:
                instructor_material = lesson.instructor_material
            except LessonInstructorMaterial.DoesNotExist:
                instructor_material = None
            rubric = instructor_material.rubric_json if instructor_material and isinstance(instructor_material.rubric_json, dict) else {}
            saved_questions = rubric.get("questions")
            if isinstance(saved_questions, list):
                questions = deepcopy(saved_questions)
            else:
                questions = [{
                    "id": str(item.get("id") or f"question-{lesson.pk}-{index}"),
                    "prompt": str(item.get("prompt") or ""), "options": list(item.get("options") or []),
                    "correctIndex": -1, "explanation": "",
                    "imageId": str(item.get("image_asset_id") or ""),
                } for index, item in enumerate(public_questions, start=1)]
            normalized_questions = []
            for index, item in enumerate(questions, start=1):
                if not isinstance(item, dict):
                    continue
                row = deepcopy(item)
                row["id"] = str(row.get("id") or f"question-{lesson.pk}-{index}")
                row["prompt"] = str(row.get("prompt") or "")
                row["options"] = [str(value) for value in row.get("options", [])] if isinstance(row.get("options"), list) else []
                try:
                    row["correctIndex"] = int(row.get("correctIndex", -1))
                except (TypeError, ValueError):
                    row["correctIndex"] = -1
                row["explanation"] = str(row.get("explanation") or "")
                public_match = next((
                    candidate for candidate in public_questions
                    if candidate.get("id") and str(candidate.get("id")) == row["id"]
                ), public_questions[index - 1] if index <= len(public_questions) else {})
                row["imageId"] = str(public_match.get("image_asset_id") or row.get("imageId") or "") if isinstance(public_match, dict) else str(row.get("imageId") or "")
                normalized_questions.append(row)
            notebook = content_json.get("notebook") if isinstance(content_json.get("notebook"), dict) else {}
            lessons.append({
                "id": str(lesson.pk), "title": lesson.title, "summary": lesson.summary,
                "minutes": lesson.duration_minutes, "format": lesson.format,
                "videoUrl": str(content_json.get("video_url") or ""),
                "reflectionPrompt": str((content_json.get("reflection") or {}).get("prompt") or "Before opening the model reasoning, write one observable fact, one possible interpretation, and one thing that would change your view."),
                "reflectionModelReasoning": str((content_json.get("reflection") or {}).get("model_reasoning") or "A careful reading separates visible evidence from interpretation, considers a reasonable alternative, and names the evidence that would strengthen or weaken the interpretation."),
                "reflectionChartNotes": str((content_json.get("reflection") or {}).get("chart_notes") or ""),
                "notebook": deepcopy(notebook) or {
                    "title": "Your Trading Notebook",
                    "prompts": [
                        {"label": "Observe", "text": "Describe the evidence visible in the chart."},
                        {"label": "Interpret", "text": "State one possible reading and a reasonable alternative."},
                        {"label": "Test", "text": "Name the next evidence that would strengthen or weaken your reading."},
                    ],
                },
                "content": lesson.content_markdown or "", "questions": normalized_questions,
                "images": images, "image": deepcopy(images[0]) if images else None,
                "imageGroups": image_groups, "teachingFigures": teaching_figures,
                "regionalBlocks": [
                    {
                        "id": str(block_id),
                        "title": str(block.get("title") or "Regional content"),
                        "baseContent": str(block.get("base_content") or ""),
                        "variants": [
                            {
                                "id": str(variant.get("id") or f"{block_id}-variant-{index}"),
                                "scope": str(variant.get("scope") or "country"),
                                "code": str(variant.get("code") or "IN"),
                                "content": str(variant.get("content") or ""),
                                "hidden": bool(variant.get("hidden", False)),
                            }
                            for index, variant in enumerate(block.get("variants", []), start=1)
                            if isinstance(variant, dict)
                        ] if isinstance(block.get("variants"), list) else [],
                    }
                    for block_id, block in (content_json.get("regional_blocks") or {}).items()
                    if isinstance(block, dict)
                ],
                "relatedCourseIds": [str(value) for value in content_json.get("related_course_ids", [])],
            })
        if lessons:
            modules.append({"id": str(module.pk), "title": module.title, "description": module.description, "lessons": lessons})
    latest_published_import = CourseImport.objects.filter(
        course_slug=course.slug, status=CourseImport.Status.PUBLISHED,
    ).order_by("-updated_at").first()
    published_import_payload = latest_published_import.payload if latest_published_import and isinstance(latest_published_import.payload, dict) else {}
    published_import_course = published_import_payload.get("course") if isinstance(published_import_payload.get("course"), dict) else {}
    requires_owned_assets = bool(published_import_course.get("requires_owned_assets", False))
    return {
        "id": "published-" + str(course.pk), "serverCourseId": str(course.pk),
        "title": course.title, "slug": course.slug, "summary": course.summary,
        "description": course.description, "category": course.category or "Technical analysis",
        "level": course.level or "Intermediate", "duration": course.estimated_duration or "Self-paced",
        "price": "", "priceNote": "Pricing and checkout are configured separately.",
        "status": "draft-update", "comingSoon": False, "requiresOwnedAssets": requires_owned_assets, "position": course.position,
        "createdAt": course.created_at.isoformat(), "updatedAt": course.updated_at.isoformat(),
        "publishedAt": course.updated_at.isoformat(), "publishedSnapshot": None,
        "outcomes": list(course.learning_outcomes or []), "modules": modules,
    }


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
    state["status"] = "draft-update" if record.target_course_id else "draft"
    if record.target_course_id:
        state["serverCourseId"] = str(record.target_course_id)
    return state


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def course_builder_api(request):
    _require_admin(request)
    if request.method == "DELETE":
        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"detail": "The request body must be valid JSON."}, status=400)
        raw_id = body.get("serverDraftId") or body.get("id")
        if not raw_id:
            return JsonResponse({"detail": "A saved draft ID is required."}, status=400)
        try:
            draft_id = uuid.UUID(str(raw_id))
        except (ValueError, TypeError, AttributeError):
            return JsonResponse({"detail": "The saved draft ID is invalid."}, status=400)

        # Only builder drafts may be deleted here. Submitted/reviewed items and
        # actual published Course rows are intentionally outside this endpoint.
        with transaction.atomic():
            record = get_object_or_404(
                CourseImport.objects.select_for_update(),
                pk=draft_id,
                status=CourseImport.Status.DRAFT,
            )
            if not record.payload.get("builder_state"):
                return JsonResponse({"detail": "Only Course Builder drafts can be deleted here."}, status=404)
            mark_builder_draft_deleted(record)
        return JsonResponse({"ok": True, "deleted_id": str(draft_id)})

    if request.method == "GET":
        drafts = []
        builder_records = list(
            CourseImport.objects.filter(status=CourseImport.Status.DRAFT).order_by("-updated_at")
        )
        retired_ids = _retire_legacy_drafts_for_deleted_courses(builder_records)
        for record in builder_records:
            if (
                record.payload.get("builder_state")
                and str(record.pk) not in retired_ids
                and record.status == CourseImport.Status.DRAFT
            ):
                drafts.append(_draft_response(record, request))
        related_courses = []
        catalogue_candidates = Course.objects.filter(
            status=Course.Status.PUBLISHED,
            modules__is_published=True,
            modules__lessons__is_published=True,
        ).distinct().order_by("position", "title").values(
            "id", "title", "slug", "summary", "description", "category", "level",
            "estimated_duration", "learning_outcomes",
        )
        for course in catalogue_candidates:
            if not is_course_card_recommendable(
                course["title"], course["summary"], course["description"],
            ):
                continue
            course["summary"] = (course["summary"] or course["description"])[:360]
            course.pop("description", None)
            related_courses.append(course)
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
        coming_soon_courses = []
        published_slugs = {
            slug
            for slug, title, summary in Course.objects.filter(
                status=Course.Status.PUBLISHED,
            ).values_list("slug", "title", "summary")
            if is_course_card_recommendable(title, summary)
        }
        seen_teaser_slugs = set()
        teaser_records = CourseImport.objects.filter(
            status__in=[CourseImport.Status.DRAFT, CourseImport.Status.REVIEW],
            target_course__isnull=True,
        ).order_by("-updated_at")
        for teaser in teaser_records:
            builder_state = (teaser.payload or {}).get("builder_state") or {}
            if not builder_state.get("comingSoon") or teaser.course_slug in published_slugs or teaser.course_slug in seen_teaser_slugs:
                continue
            teaser_title = str(builder_state.get("title") or teaser.title)[:200]
            teaser_summary = str(builder_state.get("summary") or builder_state.get("description") or "")[:360]
            if not is_course_card_recommendable(teaser_title, teaser_summary, str(builder_state.get("description") or "")):
                continue
            seen_teaser_slugs.add(teaser.course_slug)
            coming_soon_courses.append({
                "id": "coming-soon-" + str(teaser.pk), "slug": teaser.course_slug,
                "title": teaser_title,
                "category": str(builder_state.get("category") or "TradeThesis courses")[:80],
                "level": str(builder_state.get("level") or "Self-paced")[:40],
                "description": teaser_summary,
                "summary": str(builder_state.get("summary") or "")[:360],
                "estimated_duration": str(builder_state.get("duration") or "")[:80],
                "learning_outcomes": [str(value).strip()[:240] for value in builder_state.get("outcomes", []) if str(value).strip()][:6] if isinstance(builder_state.get("outcomes"), list) else [],
                "outcome": "Course details and enrolment will be announced closer to launch.",
                "complements": "This course is being prepared. Full details will be shared closer to launch.",
                "price": "Coming soon", "status": "coming-soon", "art": "structure",
                "modules": [{
                    "title": "Course outline", "count": "Coming soon",
                    "preview": "The full course outline will be shared closer to launch.",
                    "points": ["Content is being prepared."],
                }],
            })
        return JsonResponse({
            "drafts": drafts, "related_courses": related_courses,
            "lesson_references": lesson_references, "coming_soon_courses": coming_soon_courses,
            "asset_storage": asset_storage_status,
        })

    try:
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            return JsonResponse({"detail": "The request body must be a JSON object."}, status=400)
        if body.get("action") == "begin_edit_published_course":
            raw_course_id = str(body.get("courseId") or "").strip()
            if not _valid_uuid(raw_course_id):
                return JsonResponse({"detail": "A valid published course ID is required."}, status=400)
            published_course = Course.objects.filter(pk=uuid.UUID(raw_course_id), status=Course.Status.PUBLISHED).first()
            if published_course is None:
                return JsonResponse({"detail": "That course is no longer published. Refresh the Course Builder and try again."}, status=404)
            existing_edit = CourseImport.objects.filter(target_course=published_course, status=CourseImport.Status.DRAFT).order_by("-updated_at").first()
            if existing_edit and existing_edit.payload.get("builder_state"):
                return JsonResponse({"ok": True, "draft": _draft_response(existing_edit, request), "reused": True})
            return JsonResponse({"ok": True, "course": _builder_state_from_published_course(published_course), "reused": False})
        course_state = body.get("course")
        if not isinstance(course_state, dict):
            return JsonResponse({"detail": "A course draft is required."}, status=400)
        title = str(course_state.get("title") or "").strip()
        slug = slugify(str(course_state.get("slug") or title))[:160]
        if not title or not slug:
            return JsonResponse({"detail": "Add a course title before saving."}, status=400)
        server_draft_id = str(course_state.get("serverDraftId") or "").strip()
        server_draft_uuid = None
        if server_draft_id:
            if not _valid_uuid(server_draft_id):
                return JsonResponse({"detail": "The saved draft ID is invalid."}, status=400)
            server_draft_uuid = uuid.UUID(server_draft_id)
            if not CourseImport.objects.filter(
                pk=server_draft_uuid, status=CourseImport.Status.DRAFT,
            ).exists():
                return JsonResponse({
                    "detail": "This saved draft was deleted or is no longer editable. Refresh the Course Builder before saving again.",
                    "draft_deleted": True,
                }, status=410)
        server_course_id = str(course_state.get("serverCourseId") or "").strip()
        server_course = None
        if server_course_id:
            if not _valid_uuid(server_course_id):
                return JsonResponse({"detail": "The published course ID is invalid."}, status=400)
            server_course = Course.objects.filter(pk=uuid.UUID(server_course_id), status=Course.Status.PUBLISHED).first()
            if server_course is None:
                return JsonResponse({"detail": "The published course could not be found or is no longer published. Refresh the Builder before saving."}, status=409)
        existing_course = Course.objects.exclude(status=Course.Status.ARCHIVED).filter(slug=slug).first()
        if server_course and existing_course and existing_course.pk != server_course.pk:
            return JsonResponse({"detail": "That URL slug already belongs to another course. Choose a unique slug before saving."}, status=409)
        if existing_course and server_course is None:
            owns_existing_draft = (
                _valid_uuid(server_draft_id)
                and CourseImport.objects.filter(
                    pk=server_draft_id, course_slug=slug,
                    status=CourseImport.Status.DRAFT, target_course__isnull=True,
                ).exists()
            )
            if not owns_existing_draft:
                return JsonResponse({"detail": "A course with this URL slug already exists. Choose a unique slug or use Edit published course."}, status=409)
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
                for regional_block in (lesson.get("content_json") or {}).get("regional_blocks", {}).values():
                    if not isinstance(regional_block, dict):
                        continue
                    validate_markdown_source(regional_block.get("base_content", ""))
                    for regional_variant in regional_block.get("variants", []):
                        if isinstance(regional_variant, dict):
                            validate_markdown_source(regional_variant.get("content", ""))
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        mode = body.get("mode", "save")
        sync_source_requested = bool(body.get("sync_source", mode == "submit"))
        if mode not in {"save", "submit"}:
            return JsonResponse({"detail": "Unsupported draft action."}, status=400)

        with transaction.atomic():
            # Lock the exact draft the browser believes it is editing. A deleted
            # or submitted draft must never be silently recreated by a stale tab.
            if server_draft_uuid:
                draft = CourseImport.objects.select_for_update().filter(
                    pk=server_draft_uuid, status=CourseImport.Status.DRAFT,
                ).first()
                if draft is None:
                    return JsonResponse({
                        "detail": "This saved draft was deleted or is no longer editable. Refresh the Course Builder before saving again.",
                        "draft_deleted": True,
                    }, status=410)
                if server_course and draft.target_course_id != server_course.pk:
                    return JsonResponse({"detail": "This draft is not linked to the selected published course. Reload it from Edit published course."}, status=409)
                if draft.target_course_id and not server_course:
                    return JsonResponse({"detail": "Reload this published-course revision from Edit published course before saving."}, status=409)
                conflicting_slug_draft = CourseImport.objects.select_for_update().filter(
                    course_slug=slug, status=CourseImport.Status.DRAFT,
                ).exclude(pk=draft.pk).exists()
                if conflicting_slug_draft and draft.course_slug != slug:
                    return JsonResponse({
                        "detail": "Another saved draft already uses this course URL slug. Choose a unique slug.",
                    }, status=409)
            elif server_course:
                draft = CourseImport.objects.select_for_update().filter(
                    course_slug=slug, status=CourseImport.Status.DRAFT, target_course=server_course,
                ).first()
            else:
                draft = CourseImport.objects.select_for_update().filter(
                    course_slug=slug, status=CourseImport.Status.DRAFT, target_course__isnull=True,
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
                    target_course=server_course,
                    imported_by=request.user,
                )
            else:
                record = draft
                if server_course:
                    record.target_course = server_course
                record.course_slug = slug
                record.title = title
                record.manifest_version = "course-builder-v1"
                record.content_hash = digest
                record.source_manifest = f"builder://{slug}"
                record.payload = payload
                record.imported_by = request.user
                record.save(update_fields=[
                    "course_slug", "title", "manifest_version", "content_hash", "source_manifest",
                    "target_course", "payload", "imported_by", "updated_at",
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
    staged = record.assets.filter(stable_asset_id=asset_id).first()
    file_field = staged.file if staged and staged.file and staged.file.storage.exists(staged.file.name) else None
    if file_field is None and record.target_course_id:
        live_asset = CourseMediaAsset.objects.filter(pk=asset_id, course_id=record.target_course_id).first()
        if live_asset and live_asset.file and live_asset.file.storage.exists(live_asset.file.name):
            file_field = live_asset.file
        elif live_asset and re.match(r"^https?://", live_asset.original_url or "", re.IGNORECASE):
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(live_asset.original_url)
    if file_field is None:
        raise Http404
    response = FileResponse(
        file_field.open("rb"),
        content_type=mimetypes.guess_type(file_field.name)[0] or "application/octet-stream",
    )
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
