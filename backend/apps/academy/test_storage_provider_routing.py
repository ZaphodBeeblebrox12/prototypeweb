"""Regression tests for provider-neutral course asset routing."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings

from apps.academy.storage import GoogleDrivePrivateCourseAssetStorage


class CourseAssetProviderRoutingTests(SimpleTestCase):
    def _settings(self, target_root, legacy_root, *, durable=True):
        return override_settings(
            ACADEMY_ASSET_STORAGE_BACKEND="django",
            ACADEMY_ASSET_STORAGE_ALIAS="academy_assets_test",
            ACADEMY_ASSET_STORAGE_DURABLE=durable,
            ACADEMY_ASSET_STORAGE_LABEL="test durable provider",
            ACADEMY_REQUIRE_DURABLE_ASSETS=True,
            DEBUG=False,
            ACADEMY_PRIVATE_MEDIA_ROOT=legacy_root,
            STORAGES={
                "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
                "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
                "academy_assets_test": {
                    "BACKEND": "django.core.files.storage.FileSystemStorage",
                    "OPTIONS": {"location": target_root},
                },
            },
        )

    def test_configured_provider_writes_reads_and_keeps_logical_name(self):
        with TemporaryDirectory() as target_root, TemporaryDirectory() as legacy_root, self._settings(target_root, legacy_root):
            storage = GoogleDrivePrivateCourseAssetStorage()
            name = "academy/course-assets/figure.png"
            self.assertEqual(
                storage.save(name, ContentFile(b"figure bytes", name="figure.png")), name
            )
            self.assertEqual(storage.status()["backend"], "django_storage")
            self.assertTrue(storage.status()["durable"])
            self.assertTrue(storage.remote_exists(name))
            with storage.open(name, "rb") as stream:
                self.assertEqual(stream.read(), b"figure bytes")

    def test_legacy_private_local_file_remains_readable_before_copy(self):
        with TemporaryDirectory() as target_root, TemporaryDirectory() as legacy_root:
            name = "academy/course-assets/legacy.png"
            path = Path(legacy_root, name)
            path.parent.mkdir(parents=True)
            path.write_bytes(b"old image")
            with self._settings(target_root, legacy_root):
                storage = GoogleDrivePrivateCourseAssetStorage()
                with storage.open(name, "rb") as stream:
                    self.assertEqual(stream.read(), b"old image")
                self.assertTrue(storage.exists(name))
                self.assertFalse(storage.remote_exists(name))

    def test_source_snapshots_use_content_addressed_paths_and_are_verified(self):
        with TemporaryDirectory() as target_root, TemporaryDirectory() as legacy_root, self._settings(target_root, legacy_root):
            storage = GoogleDrivePrivateCourseAssetStorage()
            payload = {"course": "example", "modules": [{"title": "A module"}]}
            self.assertTrue(storage.save_source_snapshot(payload, "example-course"))
            snapshots = list(Path(target_root, "course-source", "builder-drafts", "example-course").glob("*.json"))
            self.assertEqual(len(snapshots), 1)
            raw = snapshots[0].read_bytes()
            self.assertEqual(json.loads(raw.decode("utf-8")), payload)
            self.assertEqual(snapshots[0].stem, hashlib.sha256(raw).hexdigest())

    def test_generic_provider_must_be_explicitly_marked_durable(self):
        with TemporaryDirectory() as target_root, TemporaryDirectory() as legacy_root, self._settings(target_root, legacy_root, durable=False):
            storage = GoogleDrivePrivateCourseAssetStorage()
            self.assertFalse(storage.status()["durable"])
            self.assertFalse(storage.status()["writes_enabled"])
            with self.assertRaisesRegex(OSError, "not enabled for writes"):
                storage.save("academy/course-assets/blocked.png", ContentFile(b"no write"))
