"""Access-control and private delivery tests for protected lesson video streams."""

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
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
    PersonalizedProtectedVideo,
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
        # Most tests in this class exercise the legacy shared stream for
        # complimentary access. Paid-purchase tests opt into PURCHASE explicitly.
        self.entitlement = CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            source=CourseEntitlement.Source.COMPLIMENTARY,
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

    def _admin_preview_client(self):
        admin = User.objects.create_user(
            username="protected-video-admin",
            email="video-admin@example.com",
            password="test-password",
            role="admin",
            is_staff=True,
        )
        client = Client()
        client.force_login(admin, backend="django.contrib.auth.backends.ModelBackend")
        return client

    def test_paid_learner_lesson_view_uses_only_the_personalised_rendition(self):
        from apps.jobs.models import Job

        self.entitlement.source = CourseEntitlement.Source.PURCHASE
        self.entitlement.save(update_fields=["source"])
        self.video.source_file.name = "academy/video-source/test/source.mp4"
        self.video.save(update_fields=["source_file"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.lesson.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        rendition = PersonalizedProtectedVideo.objects.get(
            user=self.user,
            protected_video=self.video,
        )
        self.assertEqual(rendition.status, PersonalizedProtectedVideo.Status.PENDING)
        self.assertContains(response, "Your protected course video is being prepared")
        self.assertContains(response, reverse("academy:personalized-video-status", args=[rendition.pk]))
        self.assertNotContains(response, 'data-video-watermark-email')
        self.assertNotContains(response, self.manifest_url)
        self.assertTrue(Job.objects.filter(
            kind="process_personalized_video",
            payload__rendition_id=str(rendition.pk),
        ).exists())

    def test_paid_learner_receives_only_the_ready_burned_watermark_manifest(self):
        self.entitlement.source = CourseEntitlement.Source.PURCHASE
        self.entitlement.save(update_fields=["source"])
        rendition = PersonalizedProtectedVideo.objects.create(
            user=self.user,
            protected_video=self.video,
            status=PersonalizedProtectedVideo.Status.READY,
            stream_directory=f"personalized/{self.video.pk}/{self.user.pk}/0123456789abcdef0123456789abcdef",
            tracking_code="VIEWER1234",
        )

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.lesson.pk])
        )

        manifest_url = reverse("academy:personalized-video-manifest", args=[rendition.pk])
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, manifest_url)
        self.assertContains(response, 'data-protected-video-container')
        self.assertNotContains(response, self.manifest_url)
        self.assertNotContains(response, 'data-video-watermark-email')

    def test_admin_lesson_preview_renders_ready_protected_video_player(self):
        client = self._admin_preview_client()

        response = client.get(
            reverse(
                "academy:admin-lesson-preview",
                args=[self.course.slug, self.lesson.pk],
            )
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["protected_video"].pk, self.video.pk)
        self.assertEqual(
            response.context["protected_video_manifest_url"],
            self.manifest_url,
        )
        self.assertContains(response, 'data-protected-video-container')
        self.assertContains(response, 'data-protected-video')
        self.assertContains(response, self.manifest_url)
        self.assertContains(response, 'data-video-watermark-name')
        self.assertContains(response, 'data-video-watermark-email')
        self.assertContains(response, 'data-video-fullscreen')
        self.assertContains(response, 'data-video-play-toggle')
        self.assertContains(response, 'data-video-fullscreen')
        self.assertNotContains(response, "<video controls")
        self.assertContains(response, "video-admin@example.com")

    def test_admin_lesson_preview_explains_pending_and_failed_video_states(self):
        client = self._admin_preview_client()
        url = reverse(
            "academy:admin-lesson-preview",
            args=[self.course.slug, self.lesson.pk],
        )

        self.video.status = ProtectedLessonVideo.Status.PROCESSING
        self.video.processing_error = ""
        self.video.save(update_fields=("status", "processing_error"))
        processing = client.get(url)

        self.assertEqual(processing.status_code, 200, processing.content)
        self.assertContains(processing, "Protected lesson video")
        self.assertContains(processing, "Processing")
        self.assertNotContains(processing, 'data-protected-video-container')

        self.video.status = ProtectedLessonVideo.Status.FAILED
        self.video.processing_error = "FFmpeg could not read the uploaded source."
        self.video.save(update_fields=("status", "processing_error"))
        failed = client.get(url)

        self.assertEqual(failed.status_code, 200, failed.content)
        self.assertContains(failed, "Processing failed")
        self.assertContains(failed, "FFmpeg could not read the uploaded source.")
        self.assertNotContains(failed, 'data-protected-video-container')

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

    def test_paid_purchase_cannot_use_shared_unpersonalised_hls(self):
        self.entitlement.source = CourseEntitlement.Source.PURCHASE
        self.entitlement.save(update_fields=["source"])

        response = self.client.get(self.manifest_url)

        self.assertEqual(response.status_code, 404)

    def test_paid_purchase_queues_personalised_renditions_for_ready_course_videos(self):
        from apps.jobs.models import Job

        from .services import enqueue_personalized_videos_for_course

        self.entitlement.source = CourseEntitlement.Source.PURCHASE
        self.entitlement.save(update_fields=["source"])
        self.video.source_file.name = "academy/video-source/test/source.mp4"
        self.video.save(update_fields=["source_file"])

        queued = enqueue_personalized_videos_for_course(
            user=self.user,
            course=self.course,
        )

        self.assertEqual(len(queued), 1)
        rendition = PersonalizedProtectedVideo.objects.get(
            user=self.user,
            protected_video=self.video,
        )
        self.assertEqual(rendition.status, PersonalizedProtectedVideo.Status.PENDING)
        job = Job.objects.get(kind="process_personalized_video")
        self.assertEqual(job.payload["rendition_id"], str(rendition.pk))
        self.assertEqual(job.payload["user_id"], str(self.user.pk))
        self.assertEqual(job.payload["video_id"], str(self.video.pk))

        # A repeated payment callback/page visit reuses the rendition and open job.
        enqueue_personalized_videos_for_course(user=self.user, course=self.course)
        self.assertEqual(
            PersonalizedProtectedVideo.objects.filter(user=self.user, protected_video=self.video).count(),
            1,
        )
        self.assertEqual(Job.objects.filter(kind="process_personalized_video").count(), 1)

    def test_complimentary_access_does_not_queue_personalised_renditions(self):
        from apps.jobs.models import Job

        from .services import enqueue_personalized_videos_for_course

        self.video.source_file.name = "academy/video-source/test/source.mp4"
        self.video.save(update_fields=["source_file"])

        queued = enqueue_personalized_videos_for_course(
            user=self.user,
            course=self.course,
        )

        self.assertEqual(queued, [])
        self.assertFalse(PersonalizedProtectedVideo.objects.exists())
        self.assertFalse(Job.objects.filter(kind="process_personalized_video").exists())

    def test_personalized_manifest_key_and_segment_are_session_bound(self):
        self.entitlement.source = CourseEntitlement.Source.PURCHASE
        self.entitlement.save(update_fields=["source"])
        rendition = PersonalizedProtectedVideo.objects.create(
            user=self.user,
            protected_video=self.video,
            status=PersonalizedProtectedVideo.Status.READY,
            stream_directory=f"personalized/{self.video.pk}/{self.user.pk}/0123456789abcdef0123456789abcdef",
            tracking_code="ABC123TEST",
        )
        rendition_dir = Path(self.temp_dir.name) / rendition.stream_directory
        rendition_dir.mkdir(parents=True)
        (rendition_dir / "encryption.key").write_bytes(b"0123456789abcdef")
        (rendition_dir / "segment_00000.ts").write_bytes(b"personalised-segment")
        (rendition_dir / "index.m3u8").write_text(
            "#EXTM3U\n"
            '#EXT-X-KEY:METHOD=AES-128,URI="protected-key",IV=0x0123456789abcdef\n'
            "#EXTINF:6.0,\n"
            "segment_00000.ts\n"
            "#EXT-X-ENDLIST\n",
            encoding="utf-8",
        )

        manifest_url = reverse("academy:personalized-video-manifest", args=[rendition.pk])
        response = self.client.get(manifest_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])
        playlist = response.content.decode("utf-8")
        self.assertIn(
            reverse("academy:personalized-video-key", args=[rendition.pk]),
            playlist,
        )
        self.assertIn(
            reverse(
                "academy:personalized-video-segment",
                args=[rendition.pk, "segment_00000.ts"],
            ),
            playlist,
        )

        key_url = re.search(r'URI="([^"]+)"', playlist).group(1)
        segment_url = next(
            line for line in playlist.splitlines()
            if "segment_00000.ts" in line and "ticket=" in line
        )
        self.assertEqual(self.client.get(key_url).content, b"0123456789abcdef")
        segment_response = self.client.get(segment_url)
        self.assertEqual(segment_response.status_code, 200)
        self.assertEqual(
            b"".join(segment_response.streaming_content),
            b"personalised-segment",
        )

        another_session = Client()
        another_session.force_login(
            self.user, backend="django.contrib.auth.backends.ModelBackend"
        )
        self.assertEqual(another_session.get(segment_url).status_code, 404)

    def test_personalized_rendition_is_only_visible_to_its_owner(self):
        self.entitlement.source = CourseEntitlement.Source.PURCHASE
        self.entitlement.save(update_fields=["source"])
        other_user = User.objects.create_user(
            username="other-paid-video-learner",
            email="other-paid@example.com",
            password="test-password",
            role=User.Role.USER,
        )
        rendition = PersonalizedProtectedVideo.objects.create(
            user=other_user,
            protected_video=self.video,
            status=PersonalizedProtectedVideo.Status.READY,
            stream_directory="personalized/other/only",
        )

        response = self.client.get(
            reverse("academy:personalized-video-manifest", args=[rendition.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_from_the_manifest(self):
        response = Client().get(self.manifest_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_processing_command_targets_the_protected_video_uuid(self):
        from apps.academy.management.commands.process_lesson_videos import Command

        with (
            override_settings(DEBUG=True),
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
            patch.object(Command, "_process_one") as process_one,
        ):
            Command().handle(
                video=str(self.video.pk),
                lesson=None,
                all=False,
                force=True,
            )

        process_one.assert_called_once()
        self.assertEqual(process_one.call_args.args[0].pk, self.video.pk)

    def test_processing_command_rejects_an_unknown_protected_video_uuid(self):
        from django.core.management.base import CommandError

        from apps.academy.management.commands.process_lesson_videos import Command

        with (
            override_settings(DEBUG=True),
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
            self.assertRaises(CommandError),
        ):
            Command().handle(
                video="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                lesson=None,
                all=False,
                force=True,
            )

    def test_queue_handler_passes_video_uuid_not_lesson_uuid_to_command(self):
        from apps.jobs.handlers import _process_protected_lesson_video

        self.video.source_file.name = "academy/video-source/test/source.mp4"
        self.video.save(update_fields=["source_file"])

        with patch("django.core.management.call_command") as run_command:
            _process_protected_lesson_video(
                {"video_id": str(self.video.pk), "force": True},
                job=None,
            )

        run_command.assert_called_once_with(
            "process_lesson_videos",
            video=str(self.video.pk),
            force=True,
        )


    def test_queue_handler_marks_preflight_failure_as_failed(self):
        from django.core.management.base import CommandError

        from apps.jobs.handlers import _process_protected_lesson_video

        self.video.source_file.name = "academy/video-source/test/source.mp4"
        self.video.status = ProtectedLessonVideo.Status.PENDING
        self.video.stream_directory = ""
        self.video.processing_error = ""
        self.video.save(update_fields=["source_file", "status", "stream_directory", "processing_error"])

        with (
            patch("django.core.management.call_command", side_effect=CommandError("FFmpeg unavailable")),
            self.assertRaises(CommandError),
        ):
            _process_protected_lesson_video(
                {"video_id": str(self.video.pk), "force": True},
                job=None,
            )

        self.video.refresh_from_db()
        self.assertEqual(self.video.status, ProtectedLessonVideo.Status.FAILED)
        self.assertIn("FFmpeg unavailable", self.video.processing_error)

    def test_queue_handler_preserves_ready_stream_on_rebuild_preflight_failure(self):
        from django.core.management.base import CommandError

        from apps.jobs.handlers import _process_protected_lesson_video

        previous_prefix = self.video.stream_directory
        self.video.source_file.name = "academy/video-source/test/source.mp4"
        self.video.save(update_fields=["source_file"])

        with (
            patch("django.core.management.call_command", side_effect=CommandError("FFmpeg unavailable")),
            self.assertRaises(CommandError),
        ):
            _process_protected_lesson_video(
                {"video_id": str(self.video.pk), "force": True},
                job=None,
            )

        self.video.refresh_from_db()
        self.assertEqual(self.video.status, ProtectedLessonVideo.Status.READY)
        self.assertEqual(self.video.stream_directory, previous_prefix)
        self.assertIn("previous stream retained", self.video.processing_error)


class PrivateLessonVideoDriveUploadTests(TestCase):
    def test_drive_media_stream_is_decoded_before_returning_file(self):
        import gzip
        from io import BytesIO
        from unittest.mock import Mock, PropertyMock, patch

        from urllib3.response import HTTPResponse

        from .video_storage import PrivateLessonVideoStorage

        payload = b"encrypted-hls-segment-bytes-" * 200
        compressed = gzip.compress(payload)
        raw = HTTPResponse(
            body=BytesIO(compressed),
            headers={"Content-Encoding": "gzip"},
            preload_content=False,
            decode_content=False,
        )
        response = Mock()
        response.raw = raw
        storage = PrivateLessonVideoStorage()

        with (
            patch(
                "apps.academy.google_drive_storage.GoogleDriveStorageMixin._drive_asset_enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(storage, "_find_drive_file", return_value={"id": "drive-segment"}),
            patch.object(storage, "_drive_request", return_value=response) as request,
        ):
            delivered = storage._open("streams/video-id/segment_00000.ts")
            self.assertEqual(delivered.read(), payload)

        self.assertTrue(raw.decode_content)
        self.assertEqual(request.call_args.kwargs["headers"], {"Accept-Encoding": "identity"})
        self.assertTrue(request.call_args.kwargs["stream"])

    def test_drive_upload_sends_resumable_chunks_with_content_ranges(self):
        import hashlib
        from unittest.mock import Mock, PropertyMock, patch

        from django.core.files.base import ContentFile

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
                new_callable=PropertyMock,
                return_value="private-folder",
            ),
        ):
            result = storage._drive_video_upload(
                "academy/video-source/lesson/source.mp4",
                content,
                len(payload),
                hashlib.md5(payload).hexdigest(),
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
