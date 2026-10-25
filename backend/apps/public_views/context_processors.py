"""Shared public-site context used by Django navigation components."""
import os


DEFAULT_PUBLIC_SITE_URL = "https://tradethesis-public-staging.onrender.com"


def sitewide_navigation(request):
    """Expose a validated, slash-trimmed public-site base URL to templates."""
    public_site_url = os.environ.get(
        "TRADETHESIS_PUBLIC_SITE_URL", DEFAULT_PUBLIC_SITE_URL
    ).strip()
    if not public_site_url.startswith("https://") or any(
        ord(char) < 32 for char in public_site_url
    ):
        public_site_url = DEFAULT_PUBLIC_SITE_URL
    return {"public_site_url": public_site_url.rstrip("/")}
