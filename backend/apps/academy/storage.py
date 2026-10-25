"""Course image storage backed by the existing TradeThesis GitHub repository.

The repository and branch are configured in Django settings; the write token
comes from the hosting environment. Without a token, local private filesystem
storage remains available for development.

GitHub's authenticated Contents API is used only server-side. Image delivery
continues through Django's authenticated/entitlement-checked views; no GitHub
download URL is exposed to learners.
"""

import base64
import hashlib
import json
import logging
from pathlib import Path
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, storages
from django.core.files.storage.handler import InvalidStorageError
from django.core.files.utils import validate_file_name
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str

from .google_drive_storage import DRIVE_API, GoogleDriveStorageMixin

logger = logging.getLogger(__name__)


@deconstructible
class PrivateCourseAssetStorage(FileSystemStorage):
    """Use private GitHub storage when configured, otherwise local disk.

    Reads fall back to the old local directory when a GitHub object is absent,
    allowing existing locally stored assets to remain readable during migration.
    """

    def __init__(self):
        location = getattr(
            settings,
            "ACADEMY_PRIVATE_MEDIA_ROOT",
            Path(settings.BASE_DIR) / "private_course_media",
        )
        super().__init__(location=str(location), base_url=settings.MEDIA_URL)
        self.repository = getattr(settings, "ACADEMY_GITHUB_ASSET_REPOSITORY", "").strip()
        self.token = getattr(settings, "ACADEMY_GITHUB_ASSET_TOKEN", "").strip()
        self.branch = getattr(settings, "ACADEMY_GITHUB_ASSET_BRANCH", "my-new-branch").strip()
        self.path_prefix = getattr(
            settings, "ACADEMY_GITHUB_ASSET_PATH_PREFIX", "course-assets"
        ).strip("/")
        self.timeout = int(getattr(settings, "ACADEMY_GITHUB_ASSET_TIMEOUT", 15))
        self.github_enabled = bool(self.repository and self.token)
        self.api_root = "https://api.github.com"

    def _github_path(self, name):
        clean_name = force_str(name).replace("\\", "/").lstrip("/")
        if not clean_name or any(part in {".", ".."} for part in clean_name.split("/")):
            raise SuspiciousFileOperation("Invalid course asset path.")
        validate_file_name(clean_name, allow_relative_path=True)
        return "/".join(part for part in (self.path_prefix, clean_name) if part)

    def _headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _url(self, path):
        encoded = "/".join(quote(part, safe="") for part in path.split("/"))
        return f"{self.api_root}/repos/{self.repository}/contents/{encoded}"

    def _request(self, method, url, **kwargs):
        try:
            response = requests.request(
                method, url, headers=self._headers(), timeout=self.timeout, **kwargs
            )
        except requests.RequestException as exc:
            raise OSError("Private course image storage is temporarily unavailable.") from exc
        if response.status_code >= 400:
            if response.status_code == 404:
                return None
            logger.warning(
                "GitHub course asset request failed with status %s",
                response.status_code,
            )
            raise OSError(f"Private course image storage returned HTTP {response.status_code}.")
        return response

    def _metadata(self, name):
        path = self._github_path(name)
        return self._request("GET", self._url(path), params={"ref": self.branch})

    def remote_exists(self, name):
        """Return whether an asset exists in GitHub, excluding any local fallback."""
        return bool(self.github_enabled and self._metadata(name) is not None)

    def _open(self, name, mode="rb"):
        if not self.github_enabled:
            return super()._open(name, mode)
        response = self._metadata(name)
        if response is None:
            return super()._open(name, mode)
        metadata = response.json()
        encoded = metadata.get("content", "").strip()
        if not encoded and metadata.get("sha"):
            blob = self._request(
                "GET",
                f"{self.api_root}/repos/{self.repository}/git/blobs/{metadata['sha']}",
            )
            if blob is None:
                raise OSError("The private course image could not be read.")
            encoded = blob.json().get("content", "").strip()
        if not encoded:
            raise OSError("GitHub returned no content for the course image.")
        return ContentFile(base64.b64decode(encoded), name=name)

    def _save(self, name, content):
        if not self.github_enabled:
            if getattr(settings, "ACADEMY_REQUIRE_DURABLE_ASSETS", not settings.DEBUG):
                raise OSError(
                    "Durable course image storage is not configured. Connect Google Drive "
                    "or set ACADEMY_GITHUB_ASSET_TOKEN before uploading lesson images."
                )
            return super()._save(name, content)
        path = self._github_path(name)
        raw = b"".join(content.chunks())
        payload = {
            "message": f"Store course asset {Path(name).name}",
            "content": base64.b64encode(raw).decode("ascii"),
            "branch": self.branch,
        }
        response = self._request("PUT", self._url(path), json=payload)
        if response is None:
            raise OSError("GitHub could not store the course image.")
        return name

    def exists(self, name):
        if not self.github_enabled:
            return super().exists(name)
        if self._metadata(name) is not None:
            return True
        return super().exists(name)

    def delete(self, name):
        if not self.github_enabled:
            return super().delete(name)
        metadata_response = self._metadata(name)
        if metadata_response is not None:
            metadata = metadata_response.json()
            response = self._request(
                "DELETE",
                self._url(self._github_path(name)),
                json={
                    "message": f"Remove course asset {Path(name).name}",
                    "sha": metadata["sha"],
                    "branch": self.branch,
                },
            )
            if response is None:
                raise OSError("GitHub could not remove the course image.")
            return
        # Compatibility with assets saved to local disk before GitHub was enabled.
        super().delete(name)


@deconstructible
class GoogleDrivePrivateCourseAssetStorage(GoogleDriveStorageMixin, PrivateCourseAssetStorage):
    """Route course assets to a selected provider while retaining migration fallbacks."""

    SUPPORTED_PROVIDERS = {"google_drive", "github", "django"}

    def __init__(self):
        super().__init__()
        self.provider_mode = (
            str(
                getattr(settings, "ACADEMY_ASSET_STORAGE_BACKEND", "google_drive") or "google_drive"
            )
            .strip()
            .lower()
        )
        if self.provider_mode not in self.SUPPORTED_PROVIDERS:
            raise ImproperlyConfigured(
                "ACADEMY_ASSET_STORAGE_BACKEND must be google_drive, github, or django."
            )
        self.storage_alias = str(
            getattr(settings, "ACADEMY_ASSET_STORAGE_ALIAS", "academy_assets") or "academy_assets"
        ).strip()
        self.external_storage = None
        try:
            self.external_storage = storages[self.storage_alias]
        except (InvalidStorageError, KeyError, AttributeError) as exc:
            if self.provider_mode == "django":
                raise ImproperlyConfigured(
                    "The configured course asset storage alias is missing from Django STORAGES."
                ) from exc
        if self.external_storage is self:
            raise ImproperlyConfigured("The course asset storage alias cannot refer to itself.")

    def _effective_backend(self):
        if self.provider_mode == "django":
            return "django_storage"
        if self.provider_mode == "github":
            return "github" if self.github_enabled else "local_filesystem"
        if self._drive_asset_enabled:
            return "google_drive"
        if self.github_enabled:
            return "github"
        return "local_filesystem"

    def get_available_name(self, name, max_length=None):
        if self.provider_mode == "django":
            validate_file_name(name, allow_relative_path=True)
            if max_length is not None and len(name) > max_length:
                raise SuspiciousFileOperation("The requested course asset path is too long.")
            return name
        return super().get_available_name(name, max_length=max_length)

    def _open_drive(self, name, mode="rb"):
        if not self._drive_asset_enabled:
            return None
        found = self._find_drive_file(name, self._asset_folder_id)
        if not found:
            return None
        response = self._drive_request(
            "GET",
            f"{DRIVE_API}/files/{found['id']}",
            params={"alt": "media"},
            expected=(200,),
        )
        return ContentFile(response.content, name=name)

    def _open_github(self, name):
        if not self.github_enabled:
            return None
        response = self._metadata(name)
        if response is None:
            return None
        try:
            metadata = response.json()
            encoded = str(metadata.get("content", "") or "").strip()
            if not encoded and metadata.get("sha"):
                blob = self._request(
                    "GET", f"{self.api_root}/repos/{self.repository}/git/blobs/{metadata['sha']}"
                )
                if blob is None:
                    raise OSError("The private course image could not be read.")
                encoded = str(blob.json().get("content", "") or "").strip()
            if not encoded:
                raise OSError("GitHub returned no content for the course image.")
            return ContentFile(base64.b64decode(encoded), name=name)
        except (ValueError, AttributeError, TypeError) as exc:
            raise OSError("The private course image could not be decoded.") from exc

    def _open_external(self, name, mode="rb"):
        if self.external_storage is not None and self.external_storage.exists(name):
            return self.external_storage.open(name, mode)
        return None

    def _try_open_backend(self, backend, readers, name, mode):
        try:
            reader = readers[backend]
            if backend == "github":
                return reader(name)
            return reader(name, mode)
        except Exception as exc:
            # Provider read failures should not defeat read-through recovery. Never log
            # full URLs, response bodies, signed links, or exception messages.
            logger.warning(
                "Course asset read failed on provider %s (%s); trying retained copies.",
                backend,
                type(exc).__name__,
            )
            return None

    def _open(self, name, mode="rb"):
        primary = self._effective_backend()
        readers = {
            "google_drive": self._open_drive,
            "github": self._open_github,
            "django_storage": self._open_external,
        }
        if primary in readers:
            result = self._try_open_backend(primary, readers, name, mode)
            if result is not None:
                return result
        # Retained providers remain readable for migration, rollback, and outages.
        for backend in ("django_storage", "google_drive", "github"):
            if backend == primary:
                continue
            result = self._try_open_backend(backend, readers, name, mode)
            if result is not None:
                return result
        return FileSystemStorage._open(self, name, mode)

    def _save(self, name, content):
        primary = self._effective_backend()
        if primary == "django_storage":
            if not self.status()["writes_enabled"] or self.external_storage is None:
                raise OSError("The configured durable course storage is not enabled for writes.")
            return self.external_storage.save(name, content)
        if primary == "github":
            return PrivateCourseAssetStorage._save(self, name, content)
        if primary == "google_drive":
            return GoogleDriveStorageMixin._save(self, name, content)
        return PrivateCourseAssetStorage._save(self, name, content)

    def _primary_remote_exists(self, name):
        primary = self._effective_backend()
        if primary == "google_drive":
            return bool(self._find_drive_file(name, self._asset_folder_id))
        if primary == "github":
            return bool(self.github_enabled and self._metadata(name) is not None)
        if primary == "django_storage":
            return bool(self.external_storage and self.external_storage.exists(name))
        return False

    def remote_exists(self, name):
        """Check the active destination only, not any retained compatibility copy."""
        if not self.status()["durable"]:
            return False
        return self._primary_remote_exists(name)

    def exists(self, name):
        primary = self._effective_backend()
        if self._primary_remote_exists(name):
            return True
        if (
            primary != "django_storage"
            and self.external_storage is not None
            and self.external_storage.exists(name)
        ):
            return True
        if (
            primary != "google_drive"
            and self._drive_asset_enabled
            and self._find_drive_file(name, self._asset_folder_id)
        ):
            return True
        if primary != "github" and self.github_enabled and self._metadata(name) is not None:
            return True
        return FileSystemStorage.exists(self, name)

    def size(self, name):
        primary = self._effective_backend()
        if primary == "google_drive":
            found = self._find_drive_file(name, self._asset_folder_id)
            if found and found.get("size") is not None:
                return int(found["size"])
        elif primary == "github" and self.github_enabled:
            response = self._metadata(name)
            if response is not None:
                try:
                    return int(response.json()["size"])
                except (ValueError, AttributeError, TypeError, KeyError):
                    pass
        elif (
            primary == "django_storage"
            and self.external_storage
            and self.external_storage.exists(name)
        ):
            return self.external_storage.size(name)
        if (
            primary != "django_storage"
            and self.external_storage is not None
            and self.external_storage.exists(name)
        ):
            return self.external_storage.size(name)
        if primary != "google_drive" and self._drive_asset_enabled:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found and found.get("size") is not None:
                return int(found["size"])
        if primary != "github" and self.github_enabled:
            response = self._metadata(name)
            if response is not None:
                try:
                    return int(response.json()["size"])
                except (ValueError, AttributeError, TypeError, KeyError):
                    pass
        return FileSystemStorage.size(self, name)

    def delete(self, name):
        """Delete only from the selected provider; keep older copies for rollback."""
        primary = self._effective_backend()
        if primary == "google_drive":
            found = self._find_drive_file(name, self._asset_folder_id)
            if found:
                self._drive_request("DELETE", f"{DRIVE_API}/files/{found['id']}", expected=(204,))
            return
        if primary == "github":
            if self.github_enabled:
                response = self._metadata(name)
                if response is not None:
                    metadata = response.json()
                    self._request(
                        "DELETE",
                        self._url(self._github_path(name)),
                        json={
                            "message": f"Remove course asset {Path(name).name}",
                            "sha": metadata["sha"],
                            "branch": self.branch,
                        },
                    )
            return
        if primary == "django_storage":
            if self.external_storage is not None and self.external_storage.exists(name):
                self.external_storage.delete(name)
            return
        FileSystemStorage.delete(self, name)

    def status(self):
        try:
            primary = self._effective_backend()
        except Exception:
            primary = "local_filesystem"
        required = bool(getattr(settings, "ACADEMY_REQUIRE_DURABLE_ASSETS", not settings.DEBUG))
        if primary == "google_drive":
            backend, label, durable = "google_drive", "Google Drive", True
        elif primary == "github":
            backend, label, durable = "github", "private GitHub repository", True
        elif primary == "django_storage":
            backend = "django_storage"
            label = str(getattr(settings, "ACADEMY_ASSET_STORAGE_LABEL", "") or "").strip()
            label = label or f"configured storage ({self.storage_alias})"
            durable = bool(getattr(settings, "ACADEMY_ASSET_STORAGE_DURABLE", False))
        else:
            backend, label, durable = "local_filesystem", "local filesystem", False
        return {
            "backend": backend,
            "label": label,
            "durable": durable,
            "writes_enabled": durable or not required,
        }

    def save_source_snapshot(self, payload, course_slug):
        """Save content-addressed course source snapshots using the selected provider."""
        if self.provider_mode == "django":
            if not self.status()["writes_enabled"] or self.external_storage is None:
                raise ImproperlyConfigured(
                    "The configured durable storage destination is not enabled for writes."
                )
            raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
                "utf-8"
            )
            digest = hashlib.sha256(raw).hexdigest()
            logical_name = f"course-source/builder-drafts/{course_slug}/{digest}.json"
            if self.external_storage.exists(logical_name):
                with self.external_storage.open(logical_name, "rb") as stream:
                    if hashlib.sha256(stream.read()).hexdigest() != digest:
                        raise OSError(
                            "The stored course source snapshot does not match its content hash."
                        )
                return True
            saved = self.external_storage.save(logical_name, ContentFile(raw))
            if saved != logical_name:
                raise OSError("The configured storage changed the logical course source filename.")
            with self.external_storage.open(logical_name, "rb") as stream:
                if hashlib.sha256(stream.read()).hexdigest() != digest:
                    raise OSError("The stored course source snapshot failed checksum verification.")
            return True
        if self.provider_mode == "github":
            raise ImproperlyConfigured(
                "GitHub course source snapshots use the dedicated GitHub source sync routine."
            )
        if not self._drive_auth_configured or not self._source_folder_id:
            raise ImproperlyConfigured("Google Drive course source snapshots are not configured.")
        raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        digest = hashlib.sha256(raw).hexdigest()
        self._write_drive_bytes(
            name=f"{course_slug}-{digest[:12]}.json",
            logical_key=f"course-source/builder-drafts/{course_slug}/{digest}.json",
            folder_id=self._source_folder_id,
            raw=raw,
            content_type="application/json",
        )
        return True


course_asset_storage = GoogleDrivePrivateCourseAssetStorage()
