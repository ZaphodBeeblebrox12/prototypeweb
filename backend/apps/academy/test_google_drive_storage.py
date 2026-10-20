"""Mocked regression tests for the Drive adapter."""
from unittest.mock import Mock, patch

from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings

from apps.academy.storage import GoogleDrivePrivateCourseAssetStorage


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

    def test_drive_save_uses_stable_key_and_folder(self):
        with patch.object(self.storage, "_write_drive_bytes", return_value={"id": "drive-file"}) as write:
            name = self.storage.save(
                "academy/example/figure.png",
                ContentFile(b"image bytes", name="figure.png"),
            )
        self.assertEqual(name, "academy/example/figure.png")
        kwargs = write.call_args.kwargs
        self.assertEqual(kwargs["logical_key"], name)
        self.assertEqual(kwargs["folder_id"], "asset-folder-test")
        self.assertEqual(kwargs["raw"], b"image bytes")

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(SuspiciousFileOperation):
            self.storage.get_available_name("../escape.png")

    def test_source_snapshot_requires_configured_folder(self):
        storage = GoogleDrivePrivateCourseAssetStorage()
        with override_settings(ACADEMY_GOOGLE_DRIVE_SOURCE_FOLDER_ID=""):
            with self.assertRaises(ImproperlyConfigured):
                storage.save_source_snapshot({"modules": []}, "missing-folder")

    def test_drive_errors_do_not_disclose_credentials(self):
        session = Mock()
        session.request.return_value = Mock(status_code=403)
        with patch.object(self.storage, "_drive_session", return_value=session):
            with self.assertRaisesRegex(OSError, "HTTP 403") as raised:
                self.storage._drive_request("GET", "https://www.googleapis.com/drive/v3/files")
        self.assertNotIn("secret-test", str(raised.exception))
        self.assertNotIn("refresh-test", str(raised.exception))
