"""Access-control and private delivery tests for protected lesson video streams."""

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlparse

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
            role="learner",
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

        self.client.force_login(self.user)
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
        segment_url = next(
            line for line in playlist.splitlines() if "segment_00000.ts?ticket=" in line
        )

        key_response = self.client.get(key_url)
        self.assertEqual(key_response.status_code, 200)
        self.assertEqual(key_response.content, b"0123456789abcdef")

        segment_response = self.client.get(segment_url)
        self.assertEqual(segment_response.status_code, 200)
        self.assertEqual(b"".join(segment_response.streaming_content), b"private-segment")
        self.assertIn("no-store", segment_response["Cache-Control"])

    def test_ticket_cannot_be_reused_from_a_different_login_session(self):
        playlist, _ticket = self._playlist_and_ticket()
        segment_url = next(
            line for line in playlist.splitlines() if "segment_00000.ts?ticket=" in line
        )

        second_session = Client()
        second_session.force_login(self.user)
        response = second_session.get(segment_url)
        self.assertEqual(response.status_code, 404)

    def test_user_without_course_entitlement_cannot_get_manifest(self):
        other_user = User.objects.create_user(
            username="unentitled-video-learner",
            email="other@example.com",
            password="test-password",
            role="learner",
        )
        client = Client()
        client.force_login(other_user)

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
