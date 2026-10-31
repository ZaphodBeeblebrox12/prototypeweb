"""Private lesson-video storage with Google Drive now and local-disk migration later.

Drive objects are private: this storage never returns a public URL. Django
proxies manifests, AES keys, and segments after checking learner entitlement.
"""
import hashlib
import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

from .google_drive_storage import DRIVE_API, UPLOAD_API, GoogleDriveStorageMixin

logger = logging.getLogger(__name__)


@deconstructible
class PrivateLessonVideoStorage(GoogleDriveStorageMixin, FileSystemStorage):
    """Store source and HLS objects in the existing private Drive asset folder."""

    def __init__(self):
        location = getattr(settings, "ACADEMY_VIDEO_STORAGE_ROOT", "")
        super().__init__(location=str(location) if location else None, base_url=None)

    @property
    def _use_drive(self):
        return (
            getattr(settings, "ACADEMY_VIDEO_STORAGE_BACKEND", "google_drive") == "google_drive"
            and self._drive_asset_enabled
        )

    @property
    def is_durable(self):
        backend = getattr(settings, "ACADEMY_VIDEO_STORAGE_BACKEND", "google_drive")
        if backend == "google_drive":
            return self._drive_asset_enabled
        return bool(getattr(settings, "ACADEMY_VIDEO_STORAGE_DURABLE", False))

    def _local_backend(self):
        return FileSystemStorage(
            location=str(getattr(settings, "ACADEMY_VIDEO_STORAGE_ROOT", "") or ""),
            base_url=None,
        )

    def url(self, name):
        return ""

    def path(self, name):
        if self._use_drive:
            raise NotImplementedError("Google Drive lesson videos do not have a local filesystem path.")
        return self._local_backend().path(name)

    def _drive_video_upload(self, name, raw, content_type):
        """Use Drive's resumable-upload protocol; source videos can exceed 5 MB."""
        logical_key = str(name).replace("\\", "/").lstrip("/")
        if not logical_key or any(part in {".", ".."} for part in logical_key.split("/")):
            raise ValueError("Invalid protected video storage key.")
        folder_id = self._asset_folder_id
        key_hash = self._logical_hash(logical_key)
        query = (
            f"'{folder_id}' in parents and "
            f"properties has {{ key='tradeThesisPathHash' and value='{key_hash}' }} and trashed = false"
        )
        listing = self._drive_request(
            "GET", f"{DRIVE_API}/files",
            params={"q": query, "pageSize": 2, "fields": "files(id,name,size,md5Checksum)"},
        ).json().get("files", [])
        if len(listing) > 1:
            logger.warning("Duplicate Drive protected-video keys found; newest item selected.")
        existing = listing[0] if listing else None
        digest = hashlib.md5(raw).hexdigest()
        if existing and str(existing.get("md5Checksum") or "").lower() == digest:
            return existing

        metadata = {
            "name": Path(logical_key).name,
            "mimeType": content_type or mimetypes.guess_type(logical_key)[0] or "application/octet-stream",
            "properties": {"tradeThesisPathHash": key_hash, "tradeThesisProtectedVideo": "true"},
        }
        if existing:
            method, url = "PATCH", f"{UPLOAD_API}/{existing['id']}"
        else:
            method, url = "POST", UPLOAD_API
            metadata["parents"] = [folder_id]
        start = self._drive_request(
            method, url, expected=(200, 201),
            params={"uploadType": "resumable", "fields": "id,name,size,md5Checksum"},
            headers={
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": metadata["mimeType"],
                "X-Upload-Content-Length": str(len(raw)),
            },
            json=metadata,
        )
        upload_url = start.headers.get("Location")
        if not upload_url:
            raise OSError("Google Drive did not create a resumable upload session.")
        uploaded = self._drive_request(
            "PUT", upload_url, expected=(200, 201),
            headers={"Content-Type": metadata["mimeType"], "Content-Length": str(len(raw))},
            data=raw,
        )
        result = uploaded.json()
        if not isinstance(result, dict) or not result.get("id"):
            raise OSError("Google Drive did not confirm the protected-video upload.")
        return result

    def _save(self, name, content):
        if self._use_drive:
            raw = b"".join(content.chunks())
            self._drive_video_upload(
                name, raw, getattr(content, "content_type", None)
                or mimetypes.guess_type(name)[0] or "application/octet-stream",
            )
            return name
        if not settings.DEBUG and getattr(settings, "ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE", True):
            raise OSError(
                "Protected video storage is not configured. Connect Google Drive or configure "
                "a durable local video volume before uploading videos."
            )
        return self._local_backend()._save(name, content)

    def _open(self, name, mode="rb"):
        if self._use_drive:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found:
                response = self._drive_request(
                    "GET", f"{DRIVE_API}/files/{found['id']}",
                    params={"alt": "media"}, expected=(200,),
                )
                return ContentFile(response.content, name=name)
        return self._local_backend()._open(name, mode)

    def exists(self, name):
        if self._use_drive and self._find_drive_file(name, self._asset_folder_id):
            return True
        return self._local_backend().exists(name)

    def size(self, name):
        if self._use_drive:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found and found.get("size") is not None:
                return int(found["size"])
        return self._local_backend().size(name)

    def delete(self, name):
        if self._use_drive:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found:
                self._drive_request("DELETE", f"{DRIVE_API}/files/{found['id']}", expected=(204,))
                return
        return self._local_backend().delete(name)


lesson_video_storage = PrivateLessonVideoStorage()
