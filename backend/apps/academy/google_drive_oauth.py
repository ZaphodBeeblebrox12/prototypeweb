"""Staff-only Google Drive OAuth connection flow."""

from __future__ import annotations

import secrets
from urllib.parse import urlencode, urlsplit

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from .permissions import is_course_content_admin

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"
SCOPE = "https://www.googleapis.com/auth/drive.file"
STATE_SESSION_KEY = "academy_google_drive_oauth_state"


def _require_course_admin(request):
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied


def _redirect_uri(request):
    configured = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_REDIRECT_URI", "") or "").strip()
    if not configured:
        if settings.DEBUG:
            return request.build_absolute_uri(reverse("academy_google_drive_oauth_callback"))
        raise ImproperlyConfigured("Google Drive OAuth redirect URI is not configured.")
    parsed = urlsplit(configured)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ImproperlyConfigured("Google Drive OAuth redirect URI must be an absolute HTTPS URL.")
    return configured


@login_required
@require_GET
def google_drive_oauth_start(request):
    _require_course_admin(request)
    client_id = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_ID", "") or "").strip()
    client_secret = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET", "") or "").strip()
    if not client_id or not client_secret:
        messages.error(
            request, "Google Drive OAuth client credentials are not configured on staging."
        )
        return redirect("staff_course_builder_preview")
    try:
        redirect_uri = _redirect_uri(request)
    except ImproperlyConfigured:
        messages.error(
            request, "Google Drive's HTTPS redirect URI is not configured on staging yet."
        )
        return redirect("staff_course_builder_preview")
    state = secrets.token_urlsafe(32)
    request.session[STATE_SESSION_KEY] = state
    request.session.modified = True
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }
    )
    return redirect(f"{AUTH_URL}?{query}")


@login_required
@require_GET
def google_drive_oauth_callback(request):
    _require_course_admin(request)
    expected_state = request.session.pop(STATE_SESSION_KEY, None)
    received_state = request.GET.get("state", "")
    if not expected_state or not secrets.compare_digest(str(expected_state), str(received_state)):
        messages.error(
            request, "Google Drive authorization could not be verified. Please start again."
        )
        return redirect("staff_course_builder_preview")
    if request.GET.get("error"):
        messages.error(request, "Google Drive authorization was cancelled or denied.")
        return redirect("staff_course_builder_preview")
    code = request.GET.get("code", "")
    client_id = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_ID", "") or "").strip()
    client_secret = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET", "") or "").strip()
    if not code or not client_id or not client_secret:
        messages.error(request, "Google Drive authorization was incomplete. Please start again.")
        return redirect("staff_course_builder_preview")
    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": _redirect_uri(request),
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        if response.status_code != 200:
            raise ValueError("token exchange rejected")
        token_data = response.json()
        access_token = token_data.get("access_token") if isinstance(token_data, dict) else None
        refresh_token = token_data.get("refresh_token") if isinstance(token_data, dict) else None
        if not access_token:
            raise ValueError("access token missing")
        from .models import GoogleDriveCredential

        credential, _ = GoogleDriveCredential.objects.get_or_create(pk=1)
        if not refresh_token and credential.encrypted_refresh_token:
            refresh_token = credential.get_refresh_token()
        if not refresh_token:
            raise ValueError("offline access token missing")
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        folder_fields = (
            "asset_folder_id",
            "source_folder_id",
            "support_attachment_folder_id",
        )
        folder_names = (
            "TradeThesis Course Assets",
            "TradeThesis Course Source Snapshots",
            "TradeThesis Support Attachments",
        )
        folder_ids = [getattr(credential, field) for field in folder_fields]
        for index, folder_name in enumerate(folder_names):
            if folder_ids[index]:
                continue
            # Drive's default for a newly created folder is private to the
            # connected account. Do not add public or anyone-with-link permissions.
            folder_response = requests.post(
                DRIVE_API,
                headers=headers,
                json={"name": folder_name, "mimeType": "application/vnd.google-apps.folder"},
                params={"fields": "id,name"},
                timeout=15,
            )
            if folder_response.status_code not in (200, 201):
                raise ValueError("Drive folder creation failed")
            folder_data = folder_response.json()
            folder_id = folder_data.get("id") if isinstance(folder_data, dict) else None
            if not folder_id:
                raise ValueError("Drive folder id missing")
            folder_ids[index] = folder_id
            setattr(credential, folder_fields[index], folder_id)
            credential.save(update_fields=[folder_fields[index], "updated_at"])

        credential.set_refresh_token(refresh_token)
        for field, folder_id in zip(folder_fields, folder_ids):
            setattr(credential, field, folder_id)
        credential.save(
            update_fields=["encrypted_refresh_token", *folder_fields, "updated_at"]
        )
    except Exception:
        messages.error(
            request, "Google Drive setup failed safely. Check staging configuration and try again."
        )
        return redirect("staff_course_builder_preview")
    messages.success(
        request,
        "Google Drive connected. Private asset and source folders were created in your Drive.",
    )
    return redirect("staff_course_builder_preview")
