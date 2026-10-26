"""Manifest validation, idempotent staging, review checks and atomic publishing."""

import hashlib
import json
import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, UnidentifiedImageError

from apps.audit.models import AuditLog

from .content_rendering import validate_markdown_source
from .course_card_utils import course_card_publication_issue
from .models import (
    Course,
    CourseContentRevision,
    CourseImport,
    CourseImportAsset,
    CourseMediaAsset,
    CourseModule,
    Lesson,
    LessonInstructorMaterial,
)
from .regional_content import (
    CONTENT_COUNTRY_TO_REGION,
    REGIONAL_CONTENT_CODES,
    contains_unmanaged_regional_image,
    regional_block_asset_ids,
    regional_block_values,
)

User = get_user_model()
_LESSON_HEADING = re.compile(
    r"^##\s+Lesson\s+(?P<source_id>\d+\.\d+)\s*[—–-]\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)
_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)\s]+)(?:\s+[^)]*)?\)")
_ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024
# SVG is accepted only for checked-in course source figures, never as an admin upload.
_SVG_TAGS = {
    "svg",
    "title",
    "desc",
    "g",
    "rect",
    "text",
    "tspan",
    "line",
    "path",
    "circle",
    "ellipse",
    "polyline",
    "polygon",
}
_SVG_ATTRIBUTES = {
    "xmlns",
    "width",
    "height",
    "viewBox",
    "x",
    "y",
    "x1",
    "y1",
    "x2",
    "y2",
    "cx",
    "cy",
    "r",
    "rx",
    "ry",
    "d",
    "points",
    "fill",
    "fill-opacity",
    "stroke",
    "stroke-width",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-dasharray",
    "stroke-dashoffset",
    "opacity",
    "font-family",
    "font-size",
    "font-weight",
    "text-anchor",
    "dominant-baseline",
    "transform",
    "id",
    "version",
}
_SVG_FORBIDDEN_TOKENS = (
    "<!DOCTYPE",
    "<!ENTITY",
    "<script",
    "<foreignObject",
    "<image",
    "<use",
    "href=",
    "style=",
    "url(",
    "javascript:",
    "data:",
)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _stable_asset_id(course_slug, asset_key):
    return str(
        uuid.uuid5(uuid.NAMESPACE_URL, "tradethesis-course:" + course_slug + ":" + asset_key)
    )


def _safe_source_path(package_root, source, label):
    if not isinstance(source, str) or not source.strip():
        raise ValueError(f"{label} must be a non-empty relative path.")
    path = (package_root / source).resolve()
    if path != package_root.resolve() and package_root.resolve() not in path.parents:
        raise ValueError(f"{label} escapes the course package: {source}")
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {source}")
    return path


def _split_module_markdown(source, source_path):
    matches = list(_LESSON_HEADING.finditer(source))
    if not matches:
        raise ValueError(f"No headings such as '## Lesson 1.1 — Title' found in {source_path}.")
    lessons = {}
    for index, match in enumerate(matches):
        source_id = match.group("source_id")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        body = source[match.end() : end].strip()
        if source_id in lessons:
            raise ValueError(f"Duplicate source lesson identifier {source_id} in {source_path}.")
        if not body:
            raise ValueError(f"Lesson {source_id} in {source_path} has no content.")
        lessons[source_id] = {"title": match.group("title").strip(), "content": body}
    return lessons


def _inspect_svg(path):
    """Validate checked-in course SVGs; do not enable SVG uploads from administrators."""
    data = path.read_bytes()
    if len(data) > _MAX_IMAGE_BYTES:
        return None, "source SVG exceeds 10 MB"
    try:
        source = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "source SVG must be UTF-8"
    lowered = source.lower()
    if any(token.lower() in lowered for token in _SVG_FORBIDDEN_TOKENS):
        return None, "source SVG contains active, linked or externally loaded content"
    try:
        root = ET.fromstring(source)
    except ET.ParseError:
        return None, "source SVG is not well-formed XML"
    if root.tag.rsplit("}", 1)[-1] != "svg" or not root.attrib.get("viewBox"):
        return None, "source SVG needs an svg root and viewBox"
    for element in root.iter():
        name = element.tag.rsplit("}", 1)[-1]
        if name not in _SVG_TAGS:
            return None, f"source SVG uses unsupported element: {name}"
        for attribute, value in element.attrib.items():
            key = attribute.rsplit("}", 1)[-1]
            if key not in _SVG_ATTRIBUTES or key.lower().startswith("on"):
                return None, f"source SVG uses unsupported attribute: {key}"
            if key != "xmlns" and any(
                token in value.lower()
                for token in ("url(", "javascript:", "data:", "http://", "https://")
            ):
                return None, f"source SVG contains an external or executable reference in {key}"
    children = {child.tag.rsplit("}", 1)[-1] for child in root}
    if not {"title", "desc"}.issubset(children):
        return None, "source SVG needs an accessible title and description"
    return {"format": "SVG", "sha256": _sha(data)}, None


def _inspect_image(path):
    if not path.is_file():
        return None, "source image is missing"
    if path.stat().st_size > _MAX_IMAGE_BYTES:
        return None, "source image exceeds 10 MB"
    if path.suffix.lower() == ".svg":
        return _inspect_svg(path)
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image_format = image.format
            image.load()
        if image_format not in _ALLOWED_FORMATS:
            return None, "unsupported image format; export it as JPEG, PNG or WebP"
        return {"format": image_format, "sha256": _sha(path.read_bytes())}, None
    except (UnidentifiedImageError, OSError, ValueError):
        return None, "file is not a valid supported image"


def inspect_manifest(manifest_path):
    """Read the canonical manifest and authored Markdown without changing Django."""
    manifest_path = Path(manifest_path).resolve()
    if not manifest_path.is_file():
        raise ValueError(f"Manifest not found: {manifest_path}")
    package_root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported manifest schema_version; expected 1.")
    course = manifest.get("course")
    modules_manifest = manifest.get("modules")
    if (
        not isinstance(course, dict)
        or not isinstance(modules_manifest, list)
        or not modules_manifest
    ):
        raise ValueError("Manifest requires a course object and a non-empty modules list.")

    required_course = ("title", "slug")
    for field in required_course:
        if not str(course.get(field, "")).strip():
            raise ValueError(f"Manifest course.{field} is required.")
    if slugify(course["slug"]) != course["slug"]:
        raise ValueError("course.slug must be a stable lowercase slug.")

    payload = {
        "schema_version": 1,
        "course": {
            "title": str(course["title"]).strip(),
            "slug": course["slug"],
            "summary": str(course.get("summary", "")).strip(),
            "description": str(course.get("description", "")).strip(),
            "position": int(course.get("position", 0)),
            "requires_owned_assets": course.get("requires_owned_assets") is True,
        },
        "notebook": manifest.get("notebook")
        or {
            "title": "Your Trading Notebook",
            "prompts": [
                {"label": "Observe", "text": "Describe the evidence visible in the chart."},
                {
                    "label": "Interpret",
                    "text": "State one possible reading and a reasonable alternative.",
                },
                {
                    "label": "Test",
                    "text": "Name the next evidence that would strengthen or weaken your reading.",
                },
            ],
        },
        "modules": [],
        "assets": [],
        "manifest_version": str(manifest.get("manifest_version", "1")),
    }
    warnings = []
    asset_sources = {}
    asset_records = {}
    seen_module_slugs = set()
    seen_module_positions = set()
    seen_lesson_slugs = set()
    seen_lesson_ids = set()

    for module_index, module in enumerate(modules_manifest, start=1):
        if not isinstance(module, dict):
            raise ValueError(f"Module entry {module_index} must be an object.")
        module_slug = str(module.get("slug", "")).strip()
        module_title = str(module.get("title", "")).strip()
        module_position = int(module.get("position", module_index))
        if not module_slug or slugify(module_slug) != module_slug or not module_title:
            raise ValueError(f"Module {module_index} needs a title and stable lowercase slug.")
        if module_slug in seen_module_slugs or module_position in seen_module_positions:
            raise ValueError(
                f"Duplicate module slug or position: {module_slug} / {module_position}."
            )
        seen_module_slugs.add(module_slug)
        seen_module_positions.add(module_position)

        source_path = _safe_source_path(
            package_root, module.get("source"), f"module {module_slug} source"
        )
        source_text = source_path.read_text(encoding="utf-8")
        source_lessons = _split_module_markdown(source_text, source_path)
        lessons_manifest = module.get("lessons")
        if not isinstance(lessons_manifest, list) or not lessons_manifest:
            raise ValueError(f"Module {module_slug} must declare its lesson list.")

        module_payload = {
            "slug": module_slug,
            "title": module_title,
            "summary": str(module.get("summary", "")).strip(),
            "position": module_position,
            "lessons": [],
        }
        seen_lesson_positions = set()
        for lesson_index, item in enumerate(lessons_manifest, start=1):
            source_id = str(item.get("source_id", item.get("id", ""))).strip()
            if source_id not in source_lessons:
                raise ValueError(f"Lesson source id {source_id!r} is missing from {source_path}.")
            lesson_title = str(item.get("title", source_lessons[source_id]["title"])).strip()
            if lesson_title != source_lessons[source_id]["title"]:
                raise ValueError(
                    f"Title mismatch for {source_id}: manifest says {lesson_title!r}, "
                    f"Markdown says {source_lessons[source_id]['title']!r}."
                )
            lesson_slug = str(item.get("slug", "")).strip()
            if not lesson_slug or slugify(lesson_slug) != lesson_slug:
                raise ValueError(f"Lesson {source_id} needs a stable lowercase slug.")
            lesson_position = int(item.get("position", lesson_index))
            lesson_key = (module_slug, lesson_slug)
            global_lesson_key = (module_slug, source_id)
            if lesson_key in seen_lesson_slugs or global_lesson_key in seen_lesson_ids:
                raise ValueError(f"Duplicate lesson slug or source id: {lesson_key}.")
            if lesson_position in seen_lesson_positions:
                raise ValueError(f"Duplicate lesson position in module {module_slug}.")
            seen_lesson_slugs.add(lesson_key)
            seen_lesson_ids.add(global_lesson_key)
            seen_lesson_positions.add(lesson_position)

            content = source_lessons[source_id]["content"]

            def replace_image(match, source_id=source_id, source_path=source_path):
                alt = match.group("alt").strip() or "Course figure"
                raw_path = match.group("path").strip()
                if re.match(r"^https?://", raw_path, re.IGNORECASE):
                    # Keep the authored URL as the default. Admins can upload a
                    # replacement without changing the Markdown or manifest.
                    asset_key = "remote/" + _sha(raw_path.encode("utf-8"))
                    stable_id = _stable_asset_id(course["slug"], asset_key)
                    if asset_key not in asset_records:
                        asset_records[asset_key] = {
                            "asset_key": asset_key,
                            "stable_asset_id": stable_id,
                            "alt_text": alt,
                            "source_path": "",
                            "original_url": raw_path,
                            "available_in_source": True,
                            "source_error": "",
                            "sha256": "",
                        }
                    elif not asset_records[asset_key]["alt_text"] and alt:
                        asset_records[asset_key]["alt_text"] = alt
                    return "![" + alt.replace("]", "") + "](asset://" + stable_id + ")"
                if re.match(r"^[a-z][a-z0-9+.-]*:", raw_path, re.IGNORECASE):
                    raise ValueError(
                        f"Unsupported image URL scheme in lesson {source_id}: {raw_path.split(':', 1)[0]}"
                    )
                asset_path = (source_path.parent / raw_path).resolve()
                if (
                    asset_path != package_root.resolve()
                    and package_root.resolve() not in asset_path.parents
                ):
                    raise ValueError(
                        f"Image reference escapes course package in lesson {source_id}: {raw_path}"
                    )
                asset_key = asset_path.relative_to(package_root.resolve()).as_posix()
                image_info, image_error = _inspect_image(asset_path)
                stable_id = _stable_asset_id(course["slug"], asset_key)
                if asset_key not in asset_records:
                    asset_records[asset_key] = {
                        "asset_key": asset_key,
                        "stable_asset_id": stable_id,
                        "alt_text": alt,
                        "source_path": asset_key,
                        "original_url": "",
                        "available_in_source": bool(image_info),
                        "source_error": image_error or "",
                        "sha256": image_info["sha256"] if image_info else "",
                    }
                    if image_info:
                        asset_sources[asset_key] = asset_path
                    else:
                        warnings.append(
                            f"{source_id}: {asset_key}: {image_error or 'asset unavailable'}"
                        )
                elif not asset_records[asset_key]["alt_text"] and alt:
                    asset_records[asset_key]["alt_text"] = alt
                return "![" + alt.replace("]", "") + "](asset://" + stable_id + ")"

            content = _IMAGE.sub(replace_image, content)
            validate_markdown_source(content)
            asset_ids = sorted(
                {match.group(1) for match in re.finditer(r"asset://([0-9a-fA-F-]{36})", content)}
            )
            notebook = item.get("notebook") or payload["notebook"]
            module_payload["lessons"].append(
                {
                    "source_id": source_id,
                    "slug": lesson_slug,
                    "title": lesson_title,
                    "summary": str(item.get("summary", "")).strip(),
                    "position": lesson_position,
                    "duration_minutes": max(1, int(item.get("duration_minutes", 15))),
                    "release_day": max(1, int(item.get("release_day", 1))),
                    "is_preview": bool(item.get("is_preview", False)),
                    "format": str(item.get("format", "reading")),
                    "content_markdown": content.strip(),
                    "content_json": {
                        "schema_version": 1,
                        "source_id": source_id,
                        "asset_ids": asset_ids,
                        "notebook": notebook,
                    },
                }
            )
        extra_sources = sorted(
            set(source_lessons)
            - {str(item.get("source_id", item.get("id", ""))) for item in lessons_manifest}
        )
        if extra_sources:
            raise ValueError(
                f"Module {module_slug} has Markdown lessons missing from the manifest: {', '.join(extra_sources)}."
            )
        payload["modules"].append(module_payload)

    payload["assets"] = sorted(asset_records.values(), key=lambda item: item["asset_key"])
    # Include asset hashes in the content hash. Files uploaded later to resolve placeholders do not mutate source identity.
    return payload, asset_sources, warnings


def stage_course_import(*, manifest_path, payload, asset_sources, warnings, imported_by=None):
    """Persist a review-only package. It does not touch published Course/Module/Lesson rows."""
    manifest_path = Path(manifest_path).resolve()
    content_hash = _sha(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    course_meta = payload["course"]
    with transaction.atomic():
        record = CourseImport.objects.filter(
            course_slug=course_meta["slug"], content_hash=content_hash
        ).first()
        if record is not None:
            return record, False, warnings
        CourseImport.objects.filter(
            course_slug=course_meta["slug"], status=CourseImport.Status.REVIEW
        ).update(status=CourseImport.Status.SUPERSEDED)
        record = CourseImport.objects.create(
            course_slug=course_meta["slug"],
            title=course_meta["title"],
            manifest_version=payload["manifest_version"],
            content_hash=content_hash,
            source_manifest=str(manifest_path),
            payload=payload,
            status=CourseImport.Status.REVIEW,
            imported_by=imported_by,
        )
        stage_warnings = list(warnings)
        for spec in payload["assets"]:
            asset = CourseImportAsset.objects.create(
                course_import=record,
                asset_key=spec["asset_key"],
                stable_asset_id=spec["stable_asset_id"],
                alt_text=spec["alt_text"],
                source_path=spec["source_path"],
                original_url=spec.get("original_url", ""),
                source_error=spec["source_error"],
            )
            source_file = asset_sources.get(spec["asset_key"])
            if source_file:
                image_info, image_error = _inspect_image(source_file)
                if not image_info:
                    asset.source_error = image_error or "Source image is invalid."
                    asset.save(update_fields=["source_error"])
                    stage_warnings.append(spec["asset_key"] + ": " + asset.source_error)
                    continue
                safe_ext = (
                    ".svg"
                    if image_info["format"] == "SVG"
                    else _ALLOWED_FORMATS[image_info["format"]]
                )
                allowed_suffixes = {".jpg", ".jpeg"} if safe_ext == ".jpg" else {safe_ext}
                if source_file.suffix.lower() not in allowed_suffixes:
                    asset.source_error = (
                        "Source file extension does not match its decoded image format."
                    )
                    asset.save(update_fields=["source_error"])
                    stage_warnings.append(
                        spec["asset_key"] + ": filename extension does not match the decoded image."
                    )
                    continue
                with source_file.open("rb") as stream:
                    asset.file.save("asset" + safe_ext, File(stream), save=True)
                asset.source_error = ""
                asset.save(update_fields=["source_error"])
        return record, True, stage_warnings


def validate_import_for_publish(record):
    errors = []
    payload = record.payload or {}
    course_data = payload.get("course") if isinstance(payload.get("course"), dict) else {}
    copy_issue = course_card_publication_issue(
        course_data.get("title"),
        course_data.get("summary"),
        course_data.get("description"),
    )
    if copy_issue:
        errors.append(copy_issue)
    if not payload.get("modules"):
        errors.append("The course has no modules.")
    referenced_asset_ids = set()
    regional_asset_ids = set()
    for module in payload.get("modules", []):
        if not module.get("lessons"):
            errors.append("Module " + str(module.get("title", "")) + " has no lessons.")
        for lesson in module.get("lessons", []):
            if not lesson.get("title") or not lesson.get("content_markdown", "").strip():
                errors.append(
                    "Lesson "
                    + str(lesson.get("title", lesson.get("source_id", "")))
                    + " is missing a title or lesson text."
                )
            if record.target_course_id:
                instructor_material = (
                    lesson.get("instructor_material")
                    if isinstance(lesson.get("instructor_material"), dict)
                    else {}
                )
                questions = (
                    instructor_material.get("questions")
                    if isinstance(instructor_material.get("questions"), list)
                    else []
                )
                for question_index, question in enumerate(questions, start=1):
                    if (
                        not isinstance(question, dict)
                        or not str(question.get("prompt") or "").strip()
                    ):
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " question "
                            + str(question_index)
                            + " needs a prompt."
                        )
                        continue
                    options = (
                        question.get("options") if isinstance(question.get("options"), list) else []
                    )
                    try:
                        correct_index = int(question.get("correctIndex", -1))
                    except (TypeError, ValueError):
                        correct_index = -1
                    if len(options) < 2 or correct_index < 0 or correct_index >= len(options):
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " question "
                            + str(question_index)
                            + " needs at least two choices and a correct answer selected."
                        )
            content_json = (
                lesson.get("content_json") if isinstance(lesson.get("content_json"), dict) else {}
            )
            referenced_asset_ids.update(
                str(value).lower() for value in content_json.get("asset_ids", []) if value
            )
            lesson_regional_asset_ids = regional_block_asset_ids(content_json)
            referenced_asset_ids.update(lesson_regional_asset_ids)
            regional_asset_ids.update(lesson_regional_asset_ids)
            for regional_block in regional_block_values(content_json):
                base_content = str(
                    regional_block.get("base_content", regional_block.get("baseContent", "")) or ""
                )
                if contains_unmanaged_regional_image(base_content):
                    errors.append(
                        "Lesson "
                        + str(lesson.get("title", ""))
                        + " regional content must use managed asset references for images; external image URLs cannot be region-locked."
                    )
                variants = (
                    regional_block.get("variants")
                    if isinstance(regional_block.get("variants"), list)
                    else []
                )
                seen_targets = set()
                for variant in variants:
                    if not isinstance(variant, dict):
                        continue
                    scope = str(variant.get("scope") or "country").strip().lower()
                    code = (
                        str(
                            variant.get("code")
                            or variant.get("country")
                            or variant.get("region")
                            or ""
                        )
                        .strip()
                        .upper()
                    )
                    target = (scope, code)
                    if target in seen_targets:
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " regional block repeats the "
                            + code
                            + " audience."
                        )
                    seen_targets.add(target)
                    if scope == "country" and code not in CONTENT_COUNTRY_TO_REGION:
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " uses an unsupported regional country code: "
                            + (code or "(empty)")
                            + "."
                        )
                    elif scope == "region" and code not in REGIONAL_CONTENT_CODES:
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " uses an unsupported regional audience: "
                            + (code or "(empty)")
                            + "."
                        )
                    elif scope not in {"country", "region"}:
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " has an invalid regional variant scope."
                        )
                    variant_content = str(variant.get("content") or "")
                    if contains_unmanaged_regional_image(variant_content):
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " regional content must use managed asset references for images; external image URLs cannot be region-locked."
                        )
                    if not bool(variant.get("hidden", False)) and not variant_content.strip():
                        errors.append(
                            "Lesson "
                            + str(lesson.get("title", ""))
                            + " has an empty regional variant for "
                            + code
                            + ". Add content or explicitly mark the variant hidden."
                        )
    staged = {str(asset.stable_asset_id): asset for asset in record.assets.all()}
    live = {
        str(asset.pk): asset
        for asset in CourseMediaAsset.objects.filter(pk__in=referenced_asset_ids)
    }
    for asset_id in sorted(referenced_asset_ids):
        stage_asset = staged.get(asset_id)
        live_asset = live.get(asset_id)
        staged_has_file = bool(stage_asset and stage_asset.file)
        live_has_file = bool(live_asset and live_asset.file)
        source_url = (stage_asset.original_url if stage_asset else "") or (
            live_asset.original_url if live_asset else ""
        )
        has_source_url = bool(re.match(r"^https?://", source_url, re.IGNORECASE))
        requires_owned_assets = bool(
            (payload.get("course") if isinstance(payload.get("course"), dict) else {}).get(
                "requires_owned_assets", False
            )
        )
        if asset_id in regional_asset_ids and not staged_has_file and not live_has_file:
            key = stage_asset.asset_key if stage_asset else asset_id
            errors.append(
                "Regional content image "
                + key
                + " must be uploaded to managed course storage before publishing. "
                + "External image URLs cannot be protected by regional access rules."
            )
            continue
        is_temporary_bollinger_reference = (
            record.course_slug == "understand-bollinger-bands"
            and stage_asset is not None
            and stage_asset.asset_key.startswith("remote/")
            and not staged_has_file
            and not live_has_file
        )
        if is_temporary_bollinger_reference:
            errors.append(
                "Temporary external Bollinger Bands chart reference "
                + stage_asset.asset_key
                + " must be replaced with an approved local chart before publishing."
            )
        elif (
            not staged_has_file
            and not live_has_file
            and (requires_owned_assets or not has_source_url)
        ):
            key = stage_asset.asset_key if stage_asset else asset_id
            if has_source_url:
                errors.append(
                    "Missing course-owned image "
                    + key
                    + ". This course requires persistent owned images; upload an approved "
                    "JPEG, PNG or WebP replacement before publishing."
                )
            else:
                errors.append(
                    "Missing course image "
                    + key
                    + ". Upload a valid JPEG, PNG or WebP in Course import assets before publishing."
                )
    return list(dict.fromkeys(errors))


def publish_course_import(record, *, user):
    """Atomically apply an approved import, matching by stable slugs and preserving learner rows."""
    errors = validate_import_for_publish(record)
    if errors:
        raise ValidationError(errors)
    with transaction.atomic():
        record = CourseImport.objects.select_for_update().get(pk=record.pk)
        if record.status != CourseImport.Status.REVIEW:
            raise ValidationError("Only a draft import awaiting review can be published.")
        payload = record.payload
        course_data = payload["course"]
        course = None
        if record.target_course_id:
            course = Course.objects.select_for_update().filter(pk=record.target_course_id).first()
            if course is None or course.status != Course.Status.PUBLISHED:
                raise ValidationError(
                    "The published course attached to this revision is no longer available."
                )
        if course is None:
            course = Course.objects.filter(slug=record.course_slug).first()
        if course is None:
            course = Course.objects.create(
                title=course_data["title"],
                slug=course_data["slug"],
                summary=course_data.get("summary", ""),
                description=course_data.get("description", ""),
                category=course_data.get("category", ""),
                level=course_data.get("level", ""),
                estimated_duration=course_data.get("estimated_duration", ""),
                learning_outcomes=course_data.get("learning_outcomes", []),
                catalogue_role=course_data.get(
                    "catalogue_role", Course.CatalogueRole.MINI
                ),
                position=course_data.get("position", 0),
                status=Course.Status.DRAFT,
            )
        else:
            for index, module in enumerate(course.modules.order_by("position", "pk")):
                module.position = 30000 + index
                module.save(update_fields=["position"])
        course.title = course_data["title"]
        course.slug = course_data["slug"]
        course.summary = course_data.get("summary", "")
        course.description = course_data.get("description", "")
        course.category = course_data.get("category", course.category)
        course.level = course_data.get("level", course.level)
        course.estimated_duration = course_data.get("estimated_duration", course.estimated_duration)
        course.learning_outcomes = course_data.get("learning_outcomes", course.learning_outcomes)
        course.catalogue_role = course_data.get("catalogue_role", course.catalogue_role)
        course.position = course_data.get("position", 0)
        course.save(
            update_fields=[
                "title",
                "slug",
                "summary",
                "description",
                "category",
                "level",
                "estimated_duration",
                "learning_outcomes",
                "catalogue_role",
                "position",
                "updated_at",
            ]
        )

        module_slugs = {item["slug"] for item in payload["modules"]}
        all_modules = list(course.modules.all())
        for index, module in enumerate(all_modules):
            module.position = 30000 + index
            module.is_published = False
            module.save(update_fields=["position", "is_published", "updated_at"])

        for module_index, module_data in enumerate(payload["modules"]):
            module, _created = CourseModule.objects.get_or_create(
                course=course,
                slug=module_data["slug"],
                defaults={
                    "title": module_data["title"],
                    "description": module_data.get("summary", ""),
                    "position": 20000 + module_index,
                    "is_published": False,
                },
            )
            existing_lessons = list(module.lessons.all())
            for index, lesson in enumerate(existing_lessons):
                lesson.position = 30000 + index
                lesson.is_published = False
                lesson.save(update_fields=["position", "is_published", "updated_at"])
            module.title = module_data["title"]
            module.description = module_data.get("summary", "")
            module.position = 20000 + module_index
            module.is_published = False
            module.save(
                update_fields=["title", "description", "position", "is_published", "updated_at"]
            )

            lesson_slugs = {item["slug"] for item in module_data["lessons"]}
            for lesson_index, lesson_data in enumerate(module_data["lessons"]):
                lesson, created = Lesson.objects.get_or_create(
                    module=module,
                    slug=lesson_data["slug"],
                    defaults={
                        "title": lesson_data["title"],
                        "position": 20000 + lesson_index,
                        "content_markdown": "",
                        "is_published": False,
                    },
                )
                next_markdown = lesson_data["content_markdown"]
                next_json = lesson_data.get("content_json", {})
                next_fields = {
                    "title": lesson_data["title"],
                    "summary": lesson_data.get("summary", ""),
                    "position": lesson_data["position"],
                    "duration_minutes": lesson_data["duration_minutes"],
                    "release_day": lesson_data["release_day"],
                    "is_preview": lesson_data["is_preview"],
                    "format": lesson_data.get("format", "reading"),
                    "content_markdown": next_markdown,
                    "content_json": next_json,
                    "is_published": True,
                }
                changed_fields = [
                    field for field, value in next_fields.items() if getattr(lesson, field) != value
                ]
                if not created and changed_fields:
                    CourseContentRevision.objects.create(
                        lesson=lesson,
                        editor=user,
                        revision_type=CourseContentRevision.RevisionType.IMPORT,
                        source_import=record,
                        title_before=lesson.title,
                        summary_before=lesson.summary,
                        content_markdown_before=lesson.content_markdown,
                        content_json_before=lesson.content_json,
                        fields_changed=changed_fields,
                    )
                for field, value in next_fields.items():
                    setattr(lesson, field, value)
                lesson.save()
                # Course Builder answer keys stay in the instructor-only table and never enter learner JSON.
                private_material = lesson_data.get("instructor_material")
                if isinstance(private_material, dict):
                    questions = private_material.get("questions", [])
                    if not isinstance(questions, list):
                        questions = []
                    answer_lines = []
                    for question_index, question in enumerate(questions, start=1):
                        if not isinstance(question, dict):
                            continue
                        prompt = str(question.get("prompt", "")).strip()
                        options = question.get("options", [])
                        correct_index = question.get("correctIndex", 0)
                        explanation = str(question.get("explanation", "")).strip()
                        try:
                            correct_index = int(correct_index)
                        except (TypeError, ValueError):
                            correct_index = -1
                        correct_answer = (
                            str(options[correct_index])
                            if isinstance(options, list) and 0 <= correct_index < len(options)
                            else ""
                        )
                        answer_lines.append(
                            f"Question {question_index}: {prompt}\n"
                            f"Correct answer: {correct_answer}\n"
                            f"Explanation: {explanation}"
                        )
                    LessonInstructorMaterial.objects.update_or_create(
                        lesson=lesson,
                        defaults={
                            "answer_key_markdown": "\n\n".join(answer_lines),
                            "rubric_json": {"questions": questions},
                        },
                    )
            # Rows removed from the source are kept (including their UUIDs and progress) but hidden.
            module.lessons.exclude(slug__in=lesson_slugs).update(is_published=False)
            module.position = module_data["position"]
            module.is_published = True
            module.save(update_fields=["position", "is_published", "updated_at"])
        course.modules.exclude(slug__in=module_slugs).update(is_published=False)

        for asset_data in payload.get("assets", []):
            asset_id = asset_data["stable_asset_id"]
            staged_asset = record.assets.filter(stable_asset_id=asset_id).first()
            media_asset = CourseMediaAsset.objects.filter(pk=asset_id).first()
            if media_asset is None:
                media_asset = CourseMediaAsset(
                    id=asset_id,
                    course=course,
                    asset_key=asset_data["asset_key"],
                    alt_text=asset_data.get("alt_text", ""),
                    source_path=asset_data.get("source_path", ""),
                    original_url=asset_data.get("original_url", ""),
                    updated_by=user,
                )
            else:
                media_asset.course = course
                media_asset.asset_key = asset_data["asset_key"]
                media_asset.alt_text = (
                    staged_asset.alt_text
                    if staged_asset and staged_asset.alt_text
                    else asset_data.get("alt_text", "")
                ) or media_asset.alt_text
                media_asset.source_path = asset_data.get("source_path", "")
                media_asset.original_url = (
                    asset_data.get("original_url", "") or media_asset.original_url
                )
                media_asset.updated_by = user
            if staged_asset and staged_asset.file:
                media_asset.file.name = staged_asset.file.name
            media_asset.save()

        course.status = Course.Status.PUBLISHED
        course.save(update_fields=["status", "updated_at"])
        record.target_course = course
        record.status = CourseImport.Status.PUBLISHED
        record.reviewed_by = user
        record.published_at = timezone.now()
        record.save(update_fields=["target_course", "status", "reviewed_by", "published_at"])
        CourseImport.objects.filter(
            course_slug=record.course_slug, status=CourseImport.Status.REVIEW
        ).exclude(pk=record.pk).update(status=CourseImport.Status.SUPERSEDED)
        AuditLog.log(
            action="academy_course_published",
            user=user,
            object_type="course",
            object_id=course.pk,
            metadata={
                "course_slug": course.slug,
                "course_import_id": str(record.pk),
                "content_hash": record.content_hash,
            },
        )
        return course
