"""Mocked regression tests for the Drive adapter."""

import hashlib
from unittest.mock import Mock, patch

from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings

from apps.academy.storage import GoogleDrivePrivateCourseAssetStorage, PrivateCourseAssetStorage


@override_settings(
    ACADEMY_PRIVATE_MEDIA_ROOT="/tmp/course-assets-drive-test",
    ACADEMY_GITHUB_ASSET_REPOSITORY="",
    ACADEMY_GITHUB_ASSET_TOKEN="",
    ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="refresh-test",
    ACADEMY_GOOGLE_DRIVE_CLIENT_ID="client-test",
    ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET="secret-test",
    ACADEMY_GOOGLE_DRIVE_ASSET_FOLDER_ID="asset-folder-test",
    ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID="source-folder-test",
    ACADEMY_GOOGLE_DRIVE_TIMEOUT=3,
)
class GoogleDriveCourseStorageTests(SimpleTestCase):
    def setUp(self):
        self.storage = GoogleDrivePrivateCourseAssetStorage()

    @override_settings(
        ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="",
        ACADEMY_GOOGLE_DRIVE_ASSET_FOLDER_ID="",
        ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID="",
    )
    def test_oauth_client_without_authorization_keeps_drive_disabled(self):
        self.assertFalse(self.storage._drive_asset_enabled)

    def test_matching_existing_drive_content_is_not_uploaded_twice(self):
        raw = b"same image bytes after a timed-out request"
        existing = {
            "id": "previous-upload",
            "name": "figure.png",
            "md5Checksum": hashlib.md5(raw).hexdigest(),
            "properties": {"tradeThesisPathHash": "key"},
        }
        with (
            patch.object(self.storage, "_find_drive_file", return_value=existing) as find,
            patch.object(self.storage, "_drive_request") as drive_request,
        ):
            result = self.storage._write_drive_bytes(
                name="figure.png",
                logical_key="course-assets/example/figure.png",
                folder_id="asset-folder-test",
                raw=raw,
                content_type="image/png",
            )

        find.assert_called_once_with("course-assets/example/figure.png", "asset-folder-test")
        self.assertEqual(result, existing)
        drive_request.assert_not_called()

    def test_status_reports_configured_drive_as_durable(self):
        self.assertEqual(
            self.storage.status(),
            {
                "backend": "google_drive",
                "label": "Google Drive",
                "durable": True,
                "writes_enabled": True,
            },
        )

    @override_settings(
        ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="refresh-test",
        ACADEMY_GOOGLE_DRIVE_CLIENT_ID="",
        ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET="",
        ACADEMY_GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON="",
        ACADEMY_GITHUB_ASSET_REPOSITORY="",
        ACADEMY_GITHUB_ASSET_TOKEN="",
        ACADEMY_REQUIRE_DURABLE_ASSETS=True,
        DEBUG=False,
    )
    def test_incomplete_drive_oauth_does_not_fall_back_to_ephemeral_writes(self):
        storage = GoogleDrivePrivateCourseAssetStorage()
        self.assertFalse(storage._drive_asset_enabled)
        self.assertFalse(storage.status()["durable"])
        self.assertFalse(storage.status()["writes_enabled"])

    def test_remote_exists_checks_remote_providers_without_local_fallback(self):
        with (
            patch.object(self.storage, "_find_drive_file", return_value=None),
            patch.object(PrivateCourseAssetStorage, "remote_exists", return_value=False),
        ):
            self.assertFalse(self.storage.remote_exists("legacy-local-image.png"))

    def test_drive_save_uses_stable_key_and_folder(self):
        with patch.object(
            self.storage, "_write_drive_bytes", return_value={"id": "drive-file"}
        ) as write:
            name = self.storage.save(
                "academy/example/figure.png",
                ContentFile(b"image bytes", name="figure.png"),
            )
        self.assertEqual(name, "academy/example/figure.png")
        kwargs = write.call_args.kwargs
        self.assertEqual(kwargs["logical_key"], name)
        self.assertEqual(kwargs["folder_id"], "asset-folder-test")
        self.assertEqual(kwargs["raw"], b"image bytes")

    def test_stored_oauth_token_overrides_stale_environment_token(self):
        record = Mock(encrypted_refresh_token="encrypted-token")
        record.get_refresh_token.return_value = "database-refresh-token"
        with (
            override_settings(ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="stale-environment-token"),
            patch.object(self.storage, "_credential_record", return_value=record),
        ):
            self.assertEqual(self.storage._refresh_token, "database-refresh-token")

    def test_environment_oauth_token_is_fallback_without_stored_token(self):
        with (
            override_settings(ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="environment-refresh-token"),
            patch.object(self.storage, "_credential_record", return_value=None),
        ):
            self.assertEqual(self.storage._refresh_token, "environment-refresh-token")

    def test_service_account_credentials_take_precedence_over_oauth(self):
        session = Mock()
        service_credentials = Mock()
        with (
            override_settings(
                ACADEMY_GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON='{"type":"service_account"}',
                ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="stale-environment-token",
            ),
            patch(
                "google.oauth2.service_account.Credentials.from_service_account_info",
                return_value=service_credentials,
            ) as service_account_factory,
            patch("google.oauth2.credentials.Credentials") as oauth_factory,
            patch("google.auth.transport.requests.AuthorizedSession", return_value=session),
        ):
            storage = GoogleDrivePrivateCourseAssetStorage()
            self.assertIs(storage._drive_session(), session)

        service_account_factory.assert_called_once()
        oauth_factory.assert_not_called()
        self.assertEqual(storage._drive_session_auth_source, "service_account")

    def test_cached_session_is_rebuilt_when_oauth_token_rotates(self):
        first_record = Mock(encrypted_refresh_token="encrypted-one")
        first_record.get_refresh_token.return_value = "database-refresh-one"
        second_record = Mock(encrypted_refresh_token="encrypted-two")
        second_record.get_refresh_token.return_value = "database-refresh-two"
        first_session, second_session = Mock(), Mock()
        with (
            override_settings(
                ACADEMY_GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON="",
                ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN="",
            ),
            patch.object(
                self.storage,
                "_credential_record",
                side_effect=[first_record, second_record],
            ),
            patch("google.oauth2.credentials.Credentials") as oauth_factory,
            patch(
                "google.auth.transport.requests.AuthorizedSession",
                side_effect=[first_session, second_session],
            ),
        ):
            self.assertIs(self.storage._drive_session(), first_session)
            self.assertIs(self.storage._drive_session(), second_session)

        self.assertEqual(oauth_factory.call_count, 2)
        self.assertEqual(
            [call.kwargs["refresh_token"] for call in oauth_factory.call_args_list],
            ["database-refresh-one", "database-refresh-two"],
        )

    def test_refresh_errors_log_only_allowlisted_provider_code(self):
        session = Mock()
        session.request.side_effect = Exception(
            "invalid_grant: Token has been expired or revoked.",
            {"error": "invalid_grant", "error_description": "do not log this detail", "refresh_token": "refresh-test"},
        )
        self.storage._drive_session_auth_source = "oauth_environment"
        with (
            patch.object(self.storage, "_drive_session", return_value=session),
            self.assertLogs("apps.academy.google_drive_storage", level="WARNING") as captured,
            self.assertRaisesRegex(OSError, "temporarily unavailable"),
        ):
            self.storage._drive_request("GET", "https://www.googleapis.com/drive/v3/files")

        log_output = "\n".join(captured.output)
        self.assertIn("provider_error=invalid_grant", log_output)
        self.assertIn("source=oauth_environment", log_output)
        self.assertNotIn("do not log this detail", log_output)
        self.assertNotIn("refresh-test", log_output)

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(SuspiciousFileOperation):
            self.storage.get_available_name("../escape.png")

    def test_source_snapshot_requires_configured_folder(self):
        storage = GoogleDrivePrivateCourseAssetStorage()
        with (
            override_settings(ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID=""),
            self.assertRaises(ImproperlyConfigured),
        ):
            storage.save_source_snapshot({"modules": []}, "missing-folder")

    def test_drive_errors_do_not_disclose_credentials(self):
        session = Mock()
        session.request.return_value = Mock(status_code=403)
        with (
            patch.object(self.storage, "_drive_session", return_value=session),
            self.assertRaisesRegex(OSError, "HTTP 403") as raised,
        ):
            self.storage._drive_request("GET", "https://www.googleapis.com/drive/v3/files")
        self.assertNotIn("secret-test", str(raised.exception))
        self.assertNotIn("refresh-test", str(raised.exception))
