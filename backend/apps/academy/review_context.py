"""Shared preparation of course-import review data for Admin Desk and Django Admin."""

from django.urls import reverse

from .content_rendering import build_lesson_sections
from .importing import validate_import_for_publish
from .models import CourseImport, CourseMediaAsset
from .views import _reflection_for_display


def build_course_import_review_data(record, request, *, allow_asset_edits=True):
    """Build a learner-safe curriculum preview and publication validation for a staged import."""
    asset_urls = {}
    staged_assets = list(record.assets.all())
    for asset in staged_assets:
        live_asset = CourseMediaAsset.objects.filter(pk=asset.stable_asset_id).first()
        if asset.file or (live_asset and live_asset.file):
            asset_urls[str(asset.stable_asset_id)] = reverse(
                "admin:academy_courseimport_asset", args=[record.pk, asset.stable_asset_id]
            )
        elif asset.original_url.startswith(("https://", "http://")):
            asset_urls[str(asset.stable_asset_id)] = asset.original_url
        elif live_asset and live_asset.original_url.startswith(("https://", "http://")):
            asset_urls[str(asset.stable_asset_id)] = live_asset.original_url

    review_modules = []
    for module in record.payload.get("modules", []):
        review_lessons = []
        for lesson_data in module.get("lessons", []):
            content_json = lesson_data.get("content_json", {})
            if not isinstance(content_json, dict):
                content_json = {}
            figure_metadata = content_json.get("figures", {})
            if not isinstance(figure_metadata, dict):
                figure_metadata = {}
            notebook = content_json.get("notebook") or record.payload.get("notebook", {})
            reflection = _reflection_for_display(content_json.get("reflection", {}))
            sections = build_lesson_sections(
                lesson_data.get("content_markdown", ""),
                asset_urls,
                user=request.user,
                admin_preview=True,
                figure_metadata=figure_metadata,
                figure_prefix=f"{module.get('position', 0)}.{lesson_data.get('position', 0)}",
                module_label=f"Module {module.get('position', '')} · {module.get('title', '')}",
                course_title=str(
                    (record.payload.get("course") or {}).get("title") or record.title
                ),
            )
            questions = []
            raw_questions = content_json.get("questions", [])
            if isinstance(raw_questions, list):
                for raw_question in raw_questions[:50]:
                    if not isinstance(raw_question, dict):
                        continue
                    question = dict(raw_question)
                    asset_id = str(question.get("image_asset_id") or "")
                    image_metadata = figure_metadata.get(asset_id, {})
                    if not isinstance(image_metadata, dict):
                        image_metadata = {}
                    question["image_url"] = asset_urls.get(asset_id, "") if asset_id else ""
                    question["image_title"] = str(image_metadata.get("title") or "Chart")[:240]
                    question["image_alt"] = str(
                        image_metadata.get("alt") or question["image_title"]
                    )[:500]
                    question["image_caption"] = str(image_metadata.get("caption") or "")[:500]
                    questions.append(question)

            raw_video_url = content_json.get("video_url", "")
            video_url = raw_video_url.strip() if isinstance(raw_video_url, str) else ""
            if not video_url.startswith(("https://", "http://")):
                video_url = ""
            video_is_file = (
                video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))
            )
            review_lessons.append(
                {
                    "lesson": lesson_data,
                    "sections": sections,
                    "notebook": notebook,
                    "reflection": reflection,
                    "reflection_response": "",
                    "questions": questions,
                    "video_url": video_url,
                    "video_is_file": video_is_file,
                    "tab_id_prefix": f"review-{module.get('position', 0)}-{lesson_data.get('position', 0)}",
                }
            )
        review_modules.append({"module": module, "lessons": review_lessons})

    errors = (
        validate_import_for_publish(record)
        if record.status == CourseImport.Status.REVIEW
        else []
    )
    asset_rows = []
    for asset in staged_assets:
        live_asset = CourseMediaAsset.objects.filter(pk=asset.stable_asset_id).first()
        original_url = asset.original_url or (live_asset.original_url if live_asset else "")
        has_file = bool(asset.file) or bool(live_asset and live_asset.file)
        asset_rows.append(
            {
                "asset": asset,
                "has_file": has_file,
                "preview_url": asset_urls.get(str(asset.stable_asset_id), ""),
                "original_url": original_url,
                "has_external_source": original_url.startswith(("https://", "http://")),
                "status_label": (
                    "Uploaded replacement"
                    if has_file
                    else ("Using URL for now" if original_url.startswith(("https://", "http://")) else "Needs upload")
                ),
                "edit_url": (
                    reverse("admin:academy_courseimportasset_change", args=[asset.pk])
                    if allow_asset_edits
                    else ""
                ),
            }
        )
    return {
        "review_modules": review_modules,
        "publish_errors": errors,
        "asset_rows": asset_rows,
    }
