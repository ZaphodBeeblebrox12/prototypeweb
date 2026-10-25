"""Core service views for TradeThesis Academy."""
from django.db import DatabaseError, connections
from django.http import JsonResponse

from apps.public_views.urls import public_front_door


# Keep reverse("index") compatible, but do not render a legacy marketing page.
index = public_front_door


def health_check(request):
    """Return service readiness without leaking internal error details."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)

    return JsonResponse({"status": "ok"})
