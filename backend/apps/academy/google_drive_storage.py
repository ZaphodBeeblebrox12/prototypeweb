"""Google Drive-backed private storage with existing GitHub/local fallback."""
from __future__ import annotations

import hashlib
import json
import logging
import mimetypes
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.utils import validate_file_name

logger = logging.getLogger(__name__)
DRIVE_API = "https://www.googleapis.com/drive/v3"
UPLOAD_API = "https://www.googleapis.com/upload/drive/v3/files"
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"


class GoogleDriveStorageMixin:
    """Write to Drive when fully authorized; preserve legacy reads during setup."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drive_session_cache = None

    def _credential_record(self):
        try:
            from .models import GoogleDriveCredential
            return GoogleDriveCredential.objects.filter(pk=1).first()
        except Exception:
            return None

    @property
    def _service_account_json(self):
        return str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", "") or "").strip()

    @property
    def _refresh_token(self):
        configured = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN", "") or "").strip()
        if configured:
            return configured
        record = self._credential_record()
        return record.get_refresh_token() if record and record.encrypted_refresh_token else ""

    @property
    def _asset_folder_id(self):
        configured = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_ASSET_FOLDER_ID", "") or "").strip()
        if configured:
            return configured
        record = self._credential_record()
        return record.asset_folder_id if record else ""

    @property
    def _source_folder_id(self):
        configured = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID", "") or "").strip()
        if configured:
            return configured
        record = self._credential_record()
        return record.source_folder_id if record else ""

    @property
    def _drive_auth_configured(self):
        refresh_token = self._refresh_token
        client_id = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_ID", "") or "").strip()
        client_secret = str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET", "") or "").strip()
        # A partially entered client configuration must not disable legacy storage.
        if not refresh_token and not self._service_account_json:
            return False
        if refresh_token and not (client_id and client_secret):
            raise ImproperlyConfigured("Google Drive refresh token is missing its OAuth client credentials.")
        return bool(self._service_account_json or (refresh_token and client_id and client_secret))

    @property
    def _drive_asset_enabled(self):
        configured = self._drive_auth_configured
        return bool(configured and self._asset_folder_id)

    def _drive_session(self):
        if self._drive_session_cache is not None:
            return self._drive_session_cache
        try:
            from google.auth.transport.requests import AuthorizedSession
            if self._refresh_token:
                from google.oauth2.credentials import Credentials
                credentials = Credentials(
                    token=None,
                    refresh_token=self._refresh_token,
                    token_uri=str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_TOKEN_URI", "https://oauth2.googleapis.com/token")),
                    client_id=str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_ID", "") or "").strip(),
                    client_secret=str(getattr(settings, "ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET", "") or "").strip(),
                    scopes=[DRIVE_SCOPE],
                )
            elif self._service_account_json:
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_info(
                    json.loads(self._service_account_json), scopes=[DRIVE_SCOPE]
                )
            else:
                raise ImproperlyConfigured("Google Drive credentials are not configured.")
            self._drive_session_cache = AuthorizedSession(credentials)
        except ImportError as exc:
            raise ImproperlyConfigured("Google Drive dependencies are not installed.") from exc
        except ImproperlyConfigured:
            raise
        except Exception as exc:
            raise ImproperlyConfigured("Google Drive credential configuration is invalid.") from exc
        return self._drive_session_cache

    def _drive_request(self, method, url, *, expected=(200,), **kwargs):
        try:
            response = self._drive_session().request(
                method, url,
                timeout=int(getattr(settings, "ACADEMY_GOOGLE_DRIVE_TIMEOUT", 20)),
                **kwargs,
            )
        except Exception as exc:
            logger.warning("Google Drive request could not be completed (%s).", exc.__class__.__name__)
            raise OSError("Google Drive course storage is temporarily unavailable.") from exc
        if response.status_code not in expected:
            logger.warning("Google Drive request failed (method=%s status=%s).", method, response.status_code)
            raise OSError(f"Google Drive course storage returned HTTP {response.status_code}.")
        return response

    @staticmethod
    def _logical_hash(logical_key):
        return hashlib.sha256(str(logical_key).encode("utf-8")).hexdigest()

    def _find_drive_file(self, logical_key, folder_id):
        key = self._logical_hash(logical_key)
        query = (
            f"'{folder_id}' in parents and "
            f"properties has {{ key='tradeThesisPathHash' and value='{key}' }} and trashed = false"
        )
        response = self._drive_request(
            "GET", f"{DRIVE_API}/files",
            params={"q": query, "pageSize": 2, "orderBy": "modifiedTime desc",
                    "fields": "files(id,name,size,mimeType,md5Checksum,properties)"},
        )
        try:
            found = response.json().get("files")
        except (ValueError, AttributeError, TypeError) as exc:
            raise OSError("Google Drive returned an unreadable file listing.") from exc
        if not isinstance(found, list):
            raise OSError("Google Drive returned an unreadable file listing.")
        if len(found) > 1:
            logger.warning("Duplicate Drive asset keys found; newest item selected.")
        return found[0] if found else None

    def _write_drive_bytes(self, *, name, logical_key, folder_id, raw, content_type):
        existing = self._find_drive_file(logical_key, folder_id)
        metadata = {
            "name": name,
            "mimeType": content_type or "application/octet-stream",
            "properties": {"tradeThesisPathHash": self._logical_hash(logical_key)},
        }
        if existing:
            method, url = "PATCH", f"{UPLOAD_API}/{existing['id']}"
        else:
            method, url = "POST", UPLOAD_API
            metadata["parents"] = [folder_id]
        boundary = "tradethesis_" + uuid.uuid4().hex
        body = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode()
            + json.dumps(metadata, separators=(",", ":")).encode()
            + f"\r\n--{boundary}\r\nContent-Type: {content_type or 'application/octet-stream'}\r\n\r\n".encode()
            + raw + f"\r\n--{boundary}--\r\n".encode()
        )
        response = self._drive_request(
            method, url, expected=(200, 201),
            params={"uploadType": "multipart", "fields": "id,name,size,md5Checksum,properties"},
            headers={"Content-Type": f"multipart/related; boundary={boundary}"}, data=body,
        )
        try:
            result = response.json()
        except (ValueError, AttributeError, TypeError) as exc:
            raise OSError("Google Drive returned an unreadable upload confirmation.") from exc
        if not isinstance(result, dict) or not result.get("id"):
            raise OSError("Google Drive did not confirm the uploaded file.")
        return result

    def get_available_name(self, name, max_length=None):
        if self._drive_asset_enabled and (max_length is None or len(name) <= max_length):
            validate_file_name(name, allow_relative_path=True)
            return name
        return super().get_available_name(name, max_length=max_length)

    def _open(self, name, mode="rb"):
        if self._drive_asset_enabled:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found:
                response = self._drive_request(
                    "GET", f"{DRIVE_API}/files/{found['id']}",
                    params={"alt": "media"}, expected=(200,),
                )
                return ContentFile(response.content, name=name)
        return super()._open(name, mode)

    def _save(self, name, content):
        if not self._drive_asset_enabled:
            return super()._save(name, content)
        raw = b"".join(content.chunks())
        self._write_drive_bytes(
            name=Path(name).name,
            logical_key=name,
            folder_id=self._asset_folder_id,
            raw=raw,
            content_type=mimetypes.guess_type(name)[0] or "application/octet-stream",
        )
        return name

    def exists(self, name):
        if self._drive_asset_enabled and self._find_drive_file(name, self._asset_folder_id):
            return True
        return super().exists(name)

    def size(self, name):
        if self._drive_asset_enabled:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found and found.get("size") is not None:
                return int(found["size"])
        return super().size(name)

    def delete(self, name):
        if self._drive_asset_enabled:
            found = self._find_drive_file(name, self._asset_folder_id)
            if found:
                self._drive_request("DELETE", f"{DRIVE_API}/files/{found['id']}", expected=(204,))
                return super().delete(name)
        return super().delete(name)

    def save_source_snapshot(self, payload, course_slug):
        if not self._drive_auth_configured or not self._source_folder_id:
            raise ImproperlyConfigured("Google Drive source snapshots are not configured.")
        raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        self._write_drive_bytes(
            name=f"{course_slug}-{digest[:12]}.json",
            logical_key=f"course-source/builder-drafts/{course_slug}/{digest}.json",
            folder_id=self._source_folder_id,
            raw=raw,
            content_type="application/json",
        )
        return True
