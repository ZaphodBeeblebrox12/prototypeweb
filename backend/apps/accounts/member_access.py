"""Secure cross-origin login handler for the public member-access room.

The public marketing site is currently a static Render site, while Django owns
authentication and session cookies. This endpoint lets the existing room submit
credentials directly to Django without displaying a second login page.

CSRF middleware is intentionally bypassed only for this single POST endpoint:
the browser submits a cross-origin HTML form, so it cannot carry Django's CSRF
cookie/token pair from the static origin. To compensate, the endpoint requires
an exact, configured Origin match and rejects requests without it. Do not broaden
the origin list to wildcards.
"""
from allauth.account.forms import LoginForm
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlsplit
from django.views.decorators.http import require_POST


def _allowed_member_access_origins():
    """Return the configured public origins, normalized without trailing slashes."""
    return {
        origin.strip().rstrip("/")
        for origin in getattr(settings, "TRADETHESIS_MEMBER_LOGIN_ORIGINS", [])
        if origin and origin.strip()
    }


GITHUB_PAGES_PUBLIC_ORIGIN = "https://zaphodbeeblebrox12.github.io"
GITHUB_PAGES_MEMBER_ACCESS_PATH = "/prototypeweb/member-access.html"


def _public_member_access_url(origin=None):
    """Return a fixed member-access URL for a trusted public-site origin."""
    allowed_origins = _allowed_member_access_origins()
    normalized_origin = str(origin or "").strip().rstrip("/")
    if normalized_origin in allowed_origins:
        if normalized_origin == GITHUB_PAGES_PUBLIC_ORIGIN:
            return normalized_origin + GITHUB_PAGES_MEMBER_ACCESS_PATH
        return normalized_origin + "/member-access.html"

    public_site_url = getattr(
        settings,
        "TRADETHESIS_PUBLIC_SITE_URL",
        "https://tradethesis-public-staging.onrender.com",
    ).strip().rstrip("/")
    if not public_site_url.startswith("https://"):
        public_site_url = "https://tradethesis-public-staging.onrender.com"
    return public_site_url + "/member-access.html"


def _trusted_referer_origin(request):
    """Extract a Referer origin only when it is HTTPS and exactly allowlisted."""
    referer = str(request.headers.get("Referer", "")).strip()
    if not referer:
        return ""
    try:
        parsed = urlsplit(referer)
    except ValueError:
        return ""
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        return ""
    origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    return origin if origin in _allowed_member_access_origins() else ""


@csrf_exempt
@require_POST
def member_access_login(request):
    """Authenticate from the member-access form and go directly to the dashboard."""
    origin = request.headers.get("Origin", "").strip().rstrip("/")
    if not origin or origin not in _allowed_member_access_origins():
        return HttpResponseForbidden("This sign-in request did not come from the member-access page.")

    form = LoginForm(request=request, data=request.POST)
    if form.is_valid():
        response = form.login(request, redirect_url=reverse("dashboard"))
        response["Cache-Control"] = "no-store"
        return response

    response = HttpResponseRedirect(f"{_public_member_access_url(origin)}?login=invalid")
    response["Cache-Control"] = "no-store"
    return response



def member_entry(request):
    """Send signed-in visitors to their dashboard without another login prompt.

    Anonymous visitors are returned to the public member-access room, where the
    in-room sign-in form lives. This avoids showing Django's separate login page
    just because someone clicked the dashboard link while signed out.
    """
    if request.user.is_authenticated:
        response = HttpResponseRedirect(reverse("dashboard"))
    else:
        response = HttpResponseRedirect(
            _public_member_access_url(_trusted_referer_origin(request))
        )
    response["Cache-Control"] = "no-store"
    return response
