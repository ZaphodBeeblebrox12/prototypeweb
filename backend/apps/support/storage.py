"""Private Google Drive storage for member support screenshots.

Support files use a dedicated folder, separate from public course assets and
course-source snapshots. Google Drive files are never shared by this adapter;
all downloads pass through the authenticated support attachment view.
"""
from __future__ import annotations

import json
import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

from apps.academy.google_drive_storage import (
    DRIVE_API,
    GoogleDriveStorageMixin,
)

logger = logging.getLogger(__name__)
_SUPPORT_FOLDER_NAME = "TradeThesis Support Attachments"
_GOOGLE_FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


@deconstructible
class SupportAttachmentStorage(GoogleDriveStorageMixin, FileSystemStorage):
    """Write ticket uploads to a private Drive folder; local fallback is dev-only."""

    def __init__(self):
        super().__init__(
            location=str(getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media")),
            base_url=getattr(settings, "MEDIA_URL", "/media/"),
        )
        self._support_folder_cache = ""

    @property
    def _asset_folder_id(self):
        configured = str(
            getattr(settings, "ACADEMY_GOOGLE_DRIVE_SUPPORT_FOLDER_ID", "") or ""
        ).strip()
        if configured:
            return configured
        if self._support_folder_cache:
            return self._support_folder_cache
        record = self._credential_record()
        return str(getattr(record, "support_attachment_folder_id", "") or "").strip()

    @property
    def _drive_asset_enabled(self):
        return bool(self._drive_auth_configured and self._asset_folder_id)

    def _ensure_support_folder(self):
        """Return the dedicated folder ID, creating and persisting it when needed."""
        existing = self._asset_folder_id
        if existing:
            return existing
        if not self._drive_auth_configured:
            return ""

        # This is a fixed name created by this app. The folder is intentionally
        # created without public permissions or link-sharing settings.
        response = self._drive_request(
            "GET",
            f"{DRIVE_API}/files",
            params={
                "q": (
                    "name='TradeThesis Support Attachments' and "
                    "mimeType='application/vnd.google-apps.folder' and trashed = false"
                ),
                "pageSize": 10,
                "orderBy": "createdTime",
                "fields": "files(id,name,mimeType)",
            },
        )
        try:
            found = response.json().get("files")
        except (ValueError, AttributeError, TypeError) as exc:
            raise OSError("Google Drive returned an unreadable support-folder listing.") from exc
        if not isinstance(found, list):
            raise OSError("Google Drive returned an unreadable support-folder listing.")

        folder_id = str(found[0].get("id") or "").strip() if found else ""
        if not folder_id:
            response = self._drive_request(
                "POST",
                f"{DRIVE_API}/files",
                expected=(200, 201),
                params={"fields": "id,name,mimeType"},
                json={"name": _SUPPORT_FOLDER_NAME, "mimeType": _GOOGLE_FOLDER_MIME_TYPE},
            )
            try:
                result = response.json()
            except (ValueError, AttributeError, TypeError) as exc:
                raise OSError("Google Drive returned an unreadable support-folder response.") from exc
            folder_id = str(result.get("id") or "").strip() if isinstance(result, dict) else ""
            if not folder_id:
                raise OSError("Google Drive did not confirm the support folder.")

        self._support_folder_cache = folder_id
        try:
            from apps.academy.models import GoogleDriveCredential

            credential, _ = GoogleDriveCredential.objects.get_or_create(pk=1)
            if credential.support_attachment_folder_id != folder_id:
                credential.support_attachment_folder_id = folder_id
                credential.save(update_fields=["support_attachment_folder_id", "updated_at"])
        except Exception:
            # A configured environment folder ID is still sufficient. Without a
            # durable DB record, this process uses its cache and logs the issue.
            logger.exception("Could not persist the Google Drive support folder ID.")
        return folder_id

    def _save(self, name, content):
        if not self._drive_auth_configured:
            if getattr(settings, "ACADEMY_REQUIRE_DURABLE_ASSETS", not settings.DEBUG):
                raise OSError(
                    "Google Drive support attachment storage is not configured. "
                    "Reconnect Google Drive or configure the support folder before uploading."
                )
            return FileSystemStorage._save(self, name, content)

        folder_id = self._ensure_support_folder()
        if not folder_id:
            raise OSError("Google Drive support attachment storage is not configured.")

        raw = b"".join(content.chunks())
        suffix = Path(name).suffix.lower()
        content_type = mimetypes.guess_type(name)[0] or {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(suffix, "application/octet-stream")
        self._write_drive_bytes(
            name=Path(name).name,
            logical_key=name,
            folder_id=folder_id,
            raw=raw,
            content_type=content_type,
        )
        return name

    def delete(self, name):
        """Remove remote bytes as well as any legacy local copy."""
        if self._drive_asset_enabled:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found:
                self._drive_request(
                    "DELETE",
                    f"{DRIVE_API}/files/{found['id']}",
                    expected=(204,),
                )
        # Also remove a legacy local copy if one existed before Drive was enabled.
        return FileSystemStorage.delete(self, name)
