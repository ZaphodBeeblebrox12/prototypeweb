"""Admin-only staging view for the in-progress Course Builder prototype."""

import base64
import json
import re
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.utils.cache import add_never_cache_headers
from django.views.decorators.http import require_GET

from .permissions import is_course_content_admin

_PREVIEW_FILE = Path(__file__).with_name("course_builder_preview.html")
_TRADING_PATH_IMPORT_FILE = Path(__file__).with_name("course_builder_trading_path_import.json")
_SUPPORT_RESISTANCE_IMPORT_FILE = Path(__file__).with_name(
    "course_builder_support_resistance_import.json"
)
_SUPPORT_RESISTANCE_CHART_DIR = (
    Path(__file__).resolve().parents[3]
    / "course-content"
    / "support-resistance"
    / "chart_assets"
    / "charts"
)
_SAFE_CHART_ASSET_ID = re.compile(r"[A-Za-z0-9-]{1,100}\\Z")


def _support_resistance_import_payload():
    """Load the draft package and hydrate only its approved illustrative PNG references."""
    try:
        payload = json.loads(_SUPPORT_RESISTANCE_IMPORT_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("The Support & Resistance import source is unavailable.") from exc

    course = payload.get("course") if isinstance(payload, dict) else None
    if not isinstance(course, dict) or not isinstance(course.get("modules"), list):
        raise ValueError("The Support & Resistance import source has an invalid structure.")

    for module in course["modules"]:
        if not isinstance(module, dict) or not isinstance(module.get("lessons"), list):
            raise ValueError("A Support & Resistance module is invalid.")
        for lesson in module["lessons"]:
            if not isinstance(lesson, dict):
                raise ValueError("A Support & Resistance lesson is invalid.")
            image_refs = lesson.pop("imageRefs", [])
            if not isinstance(image_refs, list):
                raise ValueError("A Support & Resistance image reference list is invalid.")
            images = []
            for image_ref in image_refs:
                if not isinstance(image_ref, dict):
                    raise ValueError("A Support & Resistance image reference is invalid.")
                asset_id = str(image_ref.get("assetId") or "")
                if not _SAFE_CHART_ASSET_ID.fullmatch(asset_id):
                    raise ValueError("A Support & Resistance chart asset identifier is invalid.")
                asset_path = _SUPPORT_RESISTANCE_CHART_DIR / f"{asset_id}.png"
                try:
                    raw_image = asset_path.read_bytes()
                except OSError as exc:
                    raise ValueError(
                        f"Required Support & Resistance chart asset is missing: {asset_id}.png"
                    ) from exc
                images.append(
                    {
                        "id": f"sr-{asset_id}",
                        "name": f"{asset_id}.png",
                        "title": str(image_ref.get("title") or "Chart example")[:240],
                        "alt": str(image_ref.get("alt") or "Illustrative price chart")[:500],
                        "caption": str(image_ref.get("caption") or "")[:500],
                        "data": "data:image/png;base64,"
                        + base64.b64encode(raw_image).decode("ascii"),
                    }
                )
            lesson["images"] = images
            lesson["image"] = images[0] if images else None
    return payload


@login_required
@require_GET
def course_builder_preview(request):
    """Serve the in-progress builder to authorised course-content administrators.

    Drafts are persisted as reviewable Academy imports. Publication still goes
    through the existing import-review workflow; pricing and checkout are separate.
    """
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied

    try:
        document = _PREVIEW_FILE.read_text(encoding="utf-8")
    except OSError:
        return HttpResponse(
            "Course Builder preview is unavailable. Please contact the site administrator.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    import_key = request.GET.get("import")
    import_payload = None
    if import_key == "trading-path":
        try:
            import_payload = json.loads(_TRADING_PATH_IMPORT_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return HttpResponse(
                "The Trading Path import source is unavailable. Please contact the site administrator.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )
    elif import_key == "support-resistance":
        try:
            import_payload = _support_resistance_import_payload()
        except ValueError as exc:
            return HttpResponse(
                str(exc) + " Please contact the site administrator.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )

    if import_payload is not None:
        marker = "<!-- COURSE_BUILDER_IMPORTED_DRAFT_DATA -->"
        if marker not in document:
            return HttpResponse(
                "The Course Builder import hook is unavailable. Please contact the site administrator.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )
        import_json = json.dumps(import_payload, ensure_ascii=False, separators=(",", ":"))
        # Prevent authored course text from closing the JSON script element.
        import_json = import_json.replace("&", "\\u0026")
        import_json = import_json.replace("<", "\\u003c")
        import_json = import_json.replace(">", "\\u003e")
        import_tag = (
            '<script type="application/json" id="courseBuilderImportedDraft">'
            + import_json
            + "</script>"
        )
        document = document.replace(marker, import_tag, 1)

    get_token(request)  # Ensure the authenticated builder receives a CSRF cookie for JSON saves.
    response = HttpResponse(document, content_type="text/html; charset=utf-8")
    add_never_cache_headers(response)
    response["X-Frame-Options"] = "DENY"
    response["Content-Security-Policy"] = (
        "default-src 'self' data: blob:; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "media-src 'self' https: http: blob:; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return response
