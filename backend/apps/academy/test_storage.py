"""Focused tests for private GitHub course asset storage."""
import base64
from unittest.mock import Mock, patch

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase, override_settings

from apps.academy.storage import PrivateCourseAssetStorage


@override_settings(
    ACADEMY_PRIVATE_MEDIA_ROOT="/tmp/course-assets-test",
    ACADEMY_GITHUB_ASSET_REPOSITORY="owner/private-assets",
    ACADEMY_GITHUB_ASSET_TOKEN="test-token",
    ACADEMY_GITHUB_ASSET_BRANCH="main",
    ACADEMY_GITHUB_ASSET_PATH_PREFIX="course-assets",
)
class PrivateCourseAssetStorageTests(SimpleTestCase):
    def setUp(self):
        self.storage = PrivateCourseAssetStorage()
        self.storage.github_enabled = True
        self.storage.repository = "owner/private-assets"
        self.storage.token = "test-token"
        self.storage.branch = "main"
        self.storage.path_prefix = "course-assets"

    def test_github_path_preserves_nested_upload_path(self):
        self.assertEqual(
            self.storage._github_path("academy/course-imports/abc/figure.png"),
            "course-assets/academy/course-imports/abc/figure.png",
        )

    def test_save_writes_base64_content_to_configured_branch(self):
        response = Mock()
        with patch.object(self.storage, "_request", return_value=response) as request:
            result = self.storage._save(
                "academy/course-assets/figure.png",
                ContentFile(b"image bytes", name="figure.png"),
            )

        self.assertEqual(result, "academy/course-assets/figure.png")
        args, kwargs = request.call_args
        self.assertEqual(args[0], "PUT")
        self.assertTrue(args[1].endswith("/course-assets/academy/course-assets/figure.png"))
        self.assertEqual(kwargs["json"]["branch"], "main")
        self.assertEqual(
            base64.b64decode(kwargs["json"]["content"]),
            b"image bytes",
        )

    def test_open_reads_authenticated_github_content(self):
        encoded = base64.b64encode(b"private image").decode("ascii")
        response = Mock()
        response.json.return_value = {"content": encoded, "encoding": "base64"}
        with patch.object(self.storage, "_metadata", return_value=response):
            image = self.storage._open("academy/course-assets/figure.png")
        self.assertEqual(image.read(), b"private image")

    def test_open_falls_back_to_local_storage_when_github_asset_is_absent(self):
        with patch.object(self.storage, "_metadata", return_value=None), patch.object(
            FileSystemStorage, "_open", autospec=True, side_effect=FileNotFoundError
        ) as local_open:
            with self.assertRaises(FileNotFoundError):
                self.storage._open("missing.png")
            local_open.assert_called_once_with(self.storage, "missing.png", "rb")


    def test_missing_remote_provider_refuses_hosted_image_writes(self):
        with override_settings(
            ACADEMY_GITHUB_ASSET_REPOSITORY="owner/private-assets",
            ACADEMY_GITHUB_ASSET_TOKEN="",
            ACADEMY_REQUIRE_DURABLE_ASSETS=True,
            DEBUG=False,
        ):
            storage = PrivateCourseAssetStorage()
            with self.assertRaisesRegex(OSError, "Durable course image storage is not configured"):
                storage._save("academy/course-assets/figure.png", ContentFile(b"image bytes"))

    def test_request_timeout_uses_safe_error_without_credentials(self):
        with (
            patch(
                "apps.academy.storage.requests.request",
                side_effect=requests.Timeout("test-token must never appear in a public error"),
            ),
            self.assertRaisesRegex(OSError, "temporarily unavailable") as raised,
        ):
            self.storage._request("GET", "https://api.github.com/example")

        self.assertNotIn("test-token", str(raised.exception))

    def test_request_rejects_authorization_errors_without_logging_credentials(self):
        for status_code in (401, 403):
            with self.subTest(status_code=status_code):
                with (
                    self.assertLogs("apps.academy.storage", level="WARNING") as logs,
                    patch(
                        "apps.academy.storage.requests.request",
                        return_value=Mock(status_code=status_code),
                    ),
                    self.assertRaisesRegex(OSError, f"HTTP {status_code}"),
                ):
                    self.storage._request("GET", "https://api.github.com/example")

                self.assertNotIn("test-token", "\n".join(logs.output))
