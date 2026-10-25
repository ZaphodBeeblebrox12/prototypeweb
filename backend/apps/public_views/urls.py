"""Academy front-door routes; public marketing is served by the static-site service."""
import os

from django.http import HttpResponseRedirect
from django.urls import path

from .youtube_live import youtube_live_status


PUBLIC_SITE_URL_DEFAULT = "https://tradethesis-public-staging.onrender.com/"


def public_front_door(request):
    """Redirect Academy's root to the separate TradeThesis public website."""
    public_site_url = os.environ.get(
        "TRADETHESIS_PUBLIC_SITE_URL", PUBLIC_SITE_URL_DEFAULT
    ).strip()
    if not public_site_url.startswith("https://"):
        public_site_url = PUBLIC_SITE_URL_DEFAULT
    if any(ord(char) < 32 for char in public_site_url):
        public_site_url = PUBLIC_SITE_URL_DEFAULT
    return HttpResponseRedirect(public_site_url)


urlpatterns = [
    path("api/youtube/live-status/", youtube_live_status, name="youtube_live_status"),
    path("", public_front_door, name="landing"),
]
