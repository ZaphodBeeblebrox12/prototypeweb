"""Course image storage backed by the existing TradeThesis GitHub repository.

The repository and branch are configured in Django settings; the write token
comes from the hosting environment. Without a token, local private filesystem
storage remains available for development.

GitHub's authenticated Contents API is used only server-side. Image delivery
continues through Django's authenticated/entitlement-checked views; no GitHub
download URL is exposed to learners.
"""
import base64
import logging
from pathlib import Path
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.utils import validate_file_name
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str

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
        self.path_prefix = getattr(settings, "ACADEMY_GITHUB_ASSET_PATH_PREFIX", "course-assets").strip("/")
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
                        logger.warning("GitHub course asset request failed with status %s", response.status_code)
            raise OSError(
                f"Private course image storage returned HTTP {response.status_code}."
            )
        return response

    def _metadata(self, name):
        path = self._github_path(name)
        return self._request("GET", self._url(path), params={"ref": self.branch})

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


course_asset_storage = PrivateCourseAssetStorage()
