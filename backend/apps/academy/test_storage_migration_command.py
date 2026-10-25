"""Tests for safe, idempotent checksum copies."""

from io import BytesIO
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from apps.academy.management.commands.migrate_course_storage import (
    _copy_to_target,
    _ensure_target_filesystem_is_private,
    _find_google_drive_urls,
    _is_google_drive_url,
    _url_host,
)


class MemoryStorage:
    def __init__(self):
        self.items = {}

    def exists(self, name):
        return name in self.items

    def open(self, name, mode="rb"):
        if name not in self.items:
            raise FileNotFoundError(name)
        return BytesIO(self.items[name])

    def save(self, name, content):
        self.items[name] = content.read()
        return name


class StorageMigrationCopyTests(SimpleTestCase):
    def test_rejects_filesystem_storage_overlapping_public_media_root(self):
        with (
            TemporaryDirectory() as public_root,
            override_settings(MEDIA_ROOT=public_root, STATIC_ROOT=""),
        ):
            target = SimpleNamespace(location=public_root)
            with self.assertRaisesRegex(CommandError, "overlaps MEDIA_ROOT"):
                _ensure_target_filesystem_is_private(target)

    def test_accepts_private_filesystem_storage_outside_public_roots(self):
        with (
            TemporaryDirectory() as private_root,
            TemporaryDirectory() as public_root,
            override_settings(MEDIA_ROOT=public_root, STATIC_ROOT=""),
        ):
            _ensure_target_filesystem_is_private(SimpleNamespace(location=private_root))

    def test_google_drive_url_detection_blocks_known_drive_hosts(self):
        self.assertTrue(_is_google_drive_url("https://drive.google.com/file/d/123/view"))
        self.assertTrue(_is_google_drive_url("https://lh3.googleusercontent.com/abc"))
        self.assertFalse(_is_google_drive_url("https://example.com/course-image.png"))
        self.assertEqual(_url_host("not a valid URL"), "")

    def test_course_content_scan_detects_nested_drive_links(self):
        payload = {
            "lesson": {"content": "An image: https://drive.google.com/file/d/123/view"},
            "variants": [{"url": "https://example.com/image.png"}],
        }
        self.assertEqual(
            _find_google_drive_urls(payload),
            ["https://drive.google.com/file/d/123/view"],
        )

    def test_dry_run_never_writes(self):
        target = MemoryStorage()
        result = _copy_to_target(target, "course-assets/figure.png", b"image", apply=False)
        self.assertEqual(result["status"], "planned")
        self.assertEqual(target.items, {})

    def test_apply_writes_and_verifies_content(self):
        target = MemoryStorage()
        result = _copy_to_target(target, "course-assets/figure.png", b"image", apply=True)
        self.assertEqual(result["status"], "copied_verified")
        self.assertEqual(target.items["course-assets/figure.png"], b"image")

    def test_same_content_is_idempotent(self):
        target = MemoryStorage()
        target.items["course-assets/figure.png"] = b"image"
        result = _copy_to_target(target, "course-assets/figure.png", b"image", apply=True)
        self.assertEqual(result["status"], "already_present")

    def test_conflicting_content_is_never_overwritten(self):
        target = MemoryStorage()
        target.items["course-assets/figure.png"] = b"original"
        with self.assertRaisesRegex(ValueError, "Target conflict"):
            _copy_to_target(target, "course-assets/figure.png", b"replacement", apply=True)
        self.assertEqual(target.items["course-assets/figure.png"], b"original")
