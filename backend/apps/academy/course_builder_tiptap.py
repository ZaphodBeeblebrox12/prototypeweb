"""Staff-only, opt-in Tiptap prototype kept separate from the live Course Builder."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.cache import add_never_cache_headers
from django.views.decorators.http import require_GET

from .permissions import is_course_content_admin


@login_required
@require_GET
def course_builder_tiptap_preview(request):
    """Render the isolated structured-editor lab without touching saved courses."""
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied

    if not getattr(settings, "ACADEMY_TIPTAP_EDITOR_ENABLED", False):
        raise Http404

    get_token(request)
    response = render(request, "academy/course_builder_tiptap.html")
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
