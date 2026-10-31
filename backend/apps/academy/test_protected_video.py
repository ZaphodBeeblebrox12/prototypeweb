"""Access-control and private delivery tests for protected lesson video streams."""

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlparse

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import (
    Course,
    CourseEntitlement,
    CourseModule,
    Lesson,
    ProtectedLessonVideo,
)

User = get_user_model()


class ProtectedLessonVideoDeliveryTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        context = override_settings(ACADEMY_VIDEO_STORAGE_ROOT=self.temp_dir.name)
        context.enable()
        self.addCleanup(context.disable)

        self.user = User.objects.create_user(
            username="protected-video-learner",
            email="learner@example.com",
            password="test-password",
            role=User.Role.USER,
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True,
        )
        self.course = Course.objects.create(
            title="Protected Video Course",
            slug="protected-video-course",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title="Video module",
            slug="video-module",
            position=1,
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Protected lesson",
            slug="protected-lesson",
            format=Lesson.Format.VIDEO,
            position=1,
            is_preview=False,
            is_published=True,
        )
        self.entitlement = CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            source=CourseEntitlement.Source.PURCHASE,
        )
        self.video = ProtectedLessonVideo.objects.create(
            lesson=self.lesson,
            status=ProtectedLessonVideo.Status.READY,
            stream_directory=f"streams/{self.lesson.pk}",
        )

        self.stream_dir = Path(self.temp_dir.name) / self.video.stream_directory
        self.stream_dir.mkdir(parents=True)
        (self.stream_dir / "encryption.key").write_bytes(b"0123456789abcdef")
        (self.stream_dir / "segment_00000.ts").write_bytes(b"private-segment")
        (self.stream_dir / "index.m3u8").write_text(
            "#EXTM3U\n"
            '#EXT-X-KEY:METHOD=AES-128,URI="protected-key",IV=0x0123456789abcdef\n'
            "#EXTINF:6.0,\n"
            "segment_00000.ts\n"
            "#EXT-X-ENDLIST\n",
            encoding="utf-8",
        )

        self.client.force_login(
            self.user, backend="django.contrib.auth.backends.ModelBackend"
        )
        self.manifest_url = reverse(
            "academy:protected-video-manifest", args=[self.video.pk]
        )

    def _playlist_and_ticket(self):
        response = self.client.get(self.manifest_url)
        self.assertEqual(response.status_code, 200)
        playlist = response.content.decode("utf-8")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn("protected-key", playlist)
        key_match = re.search(r'URI="([^"]+)"', playlist)
        self.assertIsNotNone(key_match)
        ticket = parse_qs(urlparse(key_match.group(1)).query).get("ticket", [])
        self.assertTrue(ticket)
        return playlist, ticket[0]

    def _segment_url(self, playlist):
        return next(
            line
            for line in playlist.splitlines()
            if "segment_00000.ts" in line and "ticket=" in line
        )

    def test_manifest_rewrites_key_and_segment_to_session_bound_routes(self):
        playlist, _ = self._playlist_and_ticket()
        self.assertIn(
            reverse("academy:protected-video-key", args=[self.video.pk]),
            playlist,
        )
        self.assertIn(
            reverse(
                "academy:protected-video-segment",
                args=[self.video.pk, "segment_00000.ts"],
            ),
            playlist,
        )
        self.assertNotIn("private-segment", playlist)

    def test_key_and_segment_are_delivered_only_to_the_entitled_session(self):
        playlist, _ticket = self._playlist_and_ticket()
        key_url = re.search(r'URI="([^"]+)"', playlist).group(1)
        segment_url = self._segment_url(playlist)

        key_response = self.client.get(key_url)
        self.assertEqual(key_response.status_code, 200)
        self.assertEqual(key_response.content, b"0123456789abcdef")

        segment_response = self.client.get(segment_url)
        self.assertEqual(segment_response.status_code, 200)
        self.assertEqual(
            b"".join(segment_response.streaming_content), b"private-segment"
        )
        self.assertIn("no-store", segment_response["Cache-Control"])

    def test_ticket_cannot_be_reused_from_a_different_login_session(self):
        playlist, _ticket = self._playlist_and_ticket()
        segment_url = self._segment_url(playlist)

        second_session = Client()
        second_session.force_login(
            self.user, backend="django.contrib.auth.backends.ModelBackend"
        )
        response = second_session.get(segment_url)
        self.assertEqual(response.status_code, 404)

    def test_user_without_course_entitlement_cannot_get_manifest(self):
        other_user = User.objects.create_user(
            username="unentitled-video-learner",
            email="other@example.com",
            password="test-password",
            role=User.Role.USER,
        )
        EmailAddress.objects.create(
            user=other_user,
            email=other_user.email,
            primary=True,
            verified=True,
        )
        client = Client()
        client.force_login(
            other_user, backend="django.contrib.auth.backends.ModelBackend"
        )

        response = client.get(self.manifest_url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_ticket_cannot_get_the_encryption_key(self):
        response = self.client.get(
            reverse("academy:protected-video-key", args=[self.video.pk]),
            {"ticket": "not-a-valid-ticket"},
        )
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_from_the_manifest(self):
        response = Client().get(self.manifest_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])


class PrivateLessonVideoDriveUploadTests(TestCase):
    def test_drive_upload_sends_resumable_chunks_with_content_ranges(self):
        from unittest.mock import Mock, patch
        from django.core.files.base import ContentFile
        from django.test.utils import override_settings
        from .video_storage import PrivateLessonVideoStorage

        payload = b"x" * (8 * 1024 * 1024 + 17)
        content = ContentFile(payload)
        listing = Mock()
        listing.json.return_value = {"files": []}
        start = Mock()
        start.headers = {"Location": "https://upload.example/session"}
        first_chunk = Mock()
        first_chunk.status_code = 308
        first_chunk.headers = {"Range": "bytes=0-8388607"}
        final_chunk = Mock()
        final_chunk.status_code = 200
        final_chunk.json.return_value = {"id": "drive-object-id"}

        storage = PrivateLessonVideoStorage()
        with (
            patch.object(storage, "_drive_request", side_effect=[
                listing, start, first_chunk, final_chunk
            ]) as request,
            patch(
                "apps.academy.google_drive_storage.GoogleDriveStorageMixin._asset_folder_id",
                new_callable=__import__("unittest.mock", fromlist=["PropertyMock"]).PropertyMock,
                return_value="private-folder",
            ),
        ):
            result = storage._drive_video_upload(
                "academy/video-source/lesson/source.mp4",
                content,
                len(payload),
                __import__("hashlib").md5(payload).hexdigest(),
                "video/mp4",
            )

        self.assertEqual(result["id"], "drive-object-id")
        put_calls = [
            call for call in request.call_args_list if call.args[0] == "PUT"
        ]
        self.assertEqual(len(put_calls), 2)
        self.assertEqual(
            put_calls[0].kwargs["headers"]["Content-Range"],
            f"bytes 0-{8 * 1024 * 1024 - 1}/{len(payload)}",
        )
        self.assertEqual(
            put_calls[1].kwargs["headers"]["Content-Range"],
            f"bytes {8 * 1024 * 1024}-{len(payload) - 1}/{len(payload)}",
        )
        self.assertEqual(len(put_calls[0].kwargs["data"]), 8 * 1024 * 1024)
        self.assertEqual(len(put_calls[1].kwargs["data"]), 17)
        self.assertEqual(put_calls[0].kwargs["timeout"], (20, 300))
