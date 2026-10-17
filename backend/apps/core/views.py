"""
Core views for community platform.
"""
from django.db import DatabaseError, connections
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    """Home page view."""
    return render(request, "index.html")


def health_check(request):
    """Return service readiness without leaking internal error details."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)

    return JsonResponse({"status": "ok"})
