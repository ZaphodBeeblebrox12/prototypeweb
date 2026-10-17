"""Small global context values shared by Django templates."""


def public_site(request):
    """Expose the public marketing-site URL for auth and account templates."""
    from django.conf import settings

    return {
        "PUBLIC_SITE_URL": (
            getattr(
                settings,
                "PUBLIC_SITE_URL",
                "https://tradethesis-public-staging.onrender.com",
            )
            or "https://tradethesis-public-staging.onrender.com"
        ).rstrip("/")
    }
