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
from django.views.decorators.http import require_POST


def _allowed_member_access_origins():
    """Return the configured public origins, normalized without trailing slashes."""
    return {
        origin.strip().rstrip("/")
        for origin in getattr(settings, "TRADETHESIS_MEMBER_LOGIN_ORIGINS", [])
        if origin and origin.strip()
    }


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

    public_site_url = getattr(
        settings,
        "TRADETHESIS_PUBLIC_SITE_URL",
        "https://tradethesis-public-staging.onrender.com",
    ).strip().rstrip("/")
    if not public_site_url.startswith("https://"):
        public_site_url = "https://tradethesis-public-staging.onrender.com"
    response = HttpResponseRedirect(f"{public_site_url}/member-access.html?login=invalid")
    response["Cache-Control"] = "no-store"
    return response
