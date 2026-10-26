"""Private Google Drive storage for member support screenshots.

Support files use a dedicated folder, separate from public course assets and
course-source snapshots. Google Drive files are never shared by this adapter;
all downloads pass through the authenticated support attachment view.
"""
from __future__ import annotations

import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
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
            location=str(
                getattr(
                    settings,
                    "SUPPORT_ATTACHMENTS_PRIVATE_MEDIA_ROOT",
                    Path(settings.BASE_DIR) / "private_support_attachments",
                )
            ),
            base_url=None,
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

        from apps.academy.models import GoogleDriveCredential

        # Lock the single credential row while initializing the folder. This
        # prevents concurrent first uploads from creating several Drive folders.
        with transaction.atomic():
            GoogleDriveCredential.objects.get_or_create(pk=1)
            credential = GoogleDriveCredential.objects.select_for_update().get(pk=1)
            if credential.support_attachment_folder_id:
                self._support_folder_cache = credential.support_attachment_folder_id
                return self._support_folder_cache

            # Always create a fresh folder instead of reusing a same-name folder
            # whose sharing settings may have been changed manually. Google Drive's
            # create operation adds no public or anyone-with-link permission.
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

            credential.support_attachment_folder_id = folder_id
            credential.save(update_fields=["support_attachment_folder_id", "updated_at"])
            self._support_folder_cache = folder_id
            return folder_id

    def _save(self, name, content):
        if not self._drive_auth_configured:
            if getattr(settings, "SUPPORT_ATTACHMENTS_REQUIRE_DRIVE", not settings.DEBUG):
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

    def _open(self, name, mode="rb"):
        try:
            return GoogleDriveStorageMixin._open(self, name, mode)
        except OSError:
            # During the storage cutover, retain read access to old local uploads
            # if a copy still exists. These files are only opened by the
            # authorized attachment view; they are never served from MEDIA_URL.
            legacy_root = str(getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media"))
            if Path(legacy_root).resolve() == Path(self.location).resolve():
                raise
            logger.info("Trying legacy local support attachment after storage miss.")
            legacy_storage = FileSystemStorage(location=legacy_root, base_url=None)
            return legacy_storage._open(name, mode)

    def url(self, name):
        raise ValueError(
            "Support attachments are private. Use the authenticated support download route."
        )

    def path(self, name):
        if self._drive_asset_enabled:
            raise NotImplementedError(
                "Google Drive attachments do not have a local filesystem path."
            )
        return FileSystemStorage.path(self, name)

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
        # Remove both the private dev fallback and any legacy MEDIA_ROOT copy.
        FileSystemStorage.delete(self, name)
        legacy_root = str(getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media"))
        if Path(legacy_root).resolve() != Path(self.location).resolve():
            FileSystemStorage(location=legacy_root, base_url=None).delete(name)
