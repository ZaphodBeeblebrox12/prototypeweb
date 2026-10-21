"""Tests for safe, idempotent checksum copies."""
from io import BytesIO

from django.test import SimpleTestCase

from apps.academy.management.commands.migrate_course_storage import (
    _copy_to_target,
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
    def test_google_drive_url_detection_blocks_known_drive_hosts(self):
        self.assertTrue(_is_google_drive_url("https://drive.google.com/file/d/123/view"))
        self.assertTrue(_is_google_drive_url("https://lh3.googleusercontent.com/abc"))
        self.assertFalse(_is_google_drive_url("https://example.com/course-image.png"))
        self.assertEqual(_url_host("not a valid URL"), "")

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
