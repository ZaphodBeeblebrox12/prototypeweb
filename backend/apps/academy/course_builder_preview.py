"""Admin-only staging view for the in-progress Course Builder prototype."""
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.utils.cache import add_never_cache_headers
from django.views.decorators.http import require_GET

from .permissions import is_course_content_admin


_PREVIEW_FILE = Path(__file__).with_name("course_builder_preview.html")


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
