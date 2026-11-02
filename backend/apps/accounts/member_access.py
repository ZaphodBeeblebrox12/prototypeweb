"""Compatibility entry points for the public TradeThesis member area.

Authentication is owned by Django/allauth. The public site no longer collects
or submits passwords; it sends visitors to the canonical Academy login page.
The old POST route remains briefly for cached public pages, but it discards the
submitted credentials and redirects with 303 so the browser opens the canonical
login form using GET.
"""
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def _allowed_member_access_origins():
    """Return explicitly configured public origins for the legacy POST bridge."""
    return {
        origin.strip().rstrip("/")
        for origin in getattr(settings, "TRADETHESIS_MEMBER_LOGIN_ORIGINS", [])
        if origin and origin.strip()
    }


def _canonical_login_url():
    """Preserve the default member-area destination on the canonical login page."""
    query = urlencode({"next": reverse("dashboard")})
    return f"{reverse('account_login')}?{query}"


@csrf_exempt
@require_POST
def member_access_login(request):
    """Redirect legacy cross-origin form submissions without authenticating them."""
    origin = request.headers.get("Origin", "").strip().rstrip("/")
    if not origin or origin not in _allowed_member_access_origins():
        return HttpResponseForbidden(
            "This legacy sign-in form is no longer available. Open the TradeThesis member area."
        )

    # Deliberately do not inspect request.POST: the old page may still be cached,
    # but all credential verification must happen on the canonical same-origin form.
    response = HttpResponse(status=303)
    response["Location"] = _canonical_login_url()
    response["Cache-Control"] = "no-store"
    return response


def member_entry(request):
    """Send members to the dashboard or the canonical login page."""
    if request.user.is_authenticated:
        response = HttpResponseRedirect(reverse("dashboard"))
    else:
        response = HttpResponseRedirect(_canonical_login_url())
    response["Cache-Control"] = "no-store"
    return response
