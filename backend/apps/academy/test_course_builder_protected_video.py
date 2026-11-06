"""Course Builder protected-video staging and publication regressions."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.academy.importing import publish_course_import
from apps.academy.models import (
    Course,
    CourseImport,
    CourseImportVideo,
    CourseModule,
    Lesson,
    ProtectedLessonVideo,
)

User = get_user_model()


class CourseBuilderProtectedVideoUploadTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        settings_context = override_settings(
            DEBUG=True,
            ACADEMY_VIDEO_STORAGE_BACKEND="filesystem",
            ACADEMY_VIDEO_STORAGE_ROOT=self.temp_dir.name,
            ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE=False,
        )
        settings_context.enable()
        self.addCleanup(settings_context.disable)

        self.admin = User.objects.create_user(
            username="course-video-author",
            password="test-password",
            role=User.Role.ADMIN,
        )
        self.client.force_login(self.admin)

    def builder_payload(self, slug="builder-protected-video-course"):
        return {
            "mode": "save",
            "course": {
                "id": "course-local-1",
                "title": "Protected Video Builder Course",
                "slug": slug,
                "summary": "A practical course about reading and managing market structure.",
                "description": "A course for disciplined technical analysis.",
                "category": "Technical analysis",
                "level": "Intermediate",
                "duration": "Self-paced",
                "accessType": "free",
                "status": "draft",
                "outcomes": ["Separate observation from interpretation."],
                "modules": [
                    {
                        "id": "module-local-1",
                        "title": "Foundations",
                        "description": "Start with observable evidence.",
                        "lessons": [
                            {
                                "id": "lesson-local-1",
                                "title": "Lesson 1.1 — First principles",
                                "summary": "Separate evidence from interpretation.",
                                "format": "video",
                                "minutes": 12,
                                "videoUrl": "",
                                "content": "## Notice\n\nDescribe what is visible before drawing a conclusion.",
                                "notebook": {
                                    "title": "Evidence notebook",
                                    "prompts": [
                                        {"label": "Observe", "text": "What evidence is visible?"}
                                    ],
                                },
                                "questions": [],
                                "images": [],
                                "image": None,
                                "relatedCourseIds": [],
                            }
                        ],
                    }
                ],
            },
        }

    def create_saved_draft(self, slug="builder-protected-video-course"):
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.builder_payload(slug)),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return CourseImport.objects.get(pk=response.json()["record_id"])

    def test_lesson_video_upload_is_private_and_reappears_when_draft_is_reloaded(self):
        draft = self.create_saved_draft()
        upload = SimpleUploadedFile(
            "support-resistance-intro.mp4",
            b"test-video-source-bytes",
            content_type="video/mp4",
        )

        response = self.client.post(
            reverse(
                "staff_course_builder_video_upload",
                args=[draft.pk, "lesson-local-1"],
            ),
            {"file": upload},
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()["video"]["kind"], "staged")
        self.assertEqual(response.json()["video"]["status"], "stored_for_draft")
        self.assertTrue(response.json()["video"]["id"])
        self.assertTrue(response.json()["updated_at"])
        staged = CourseImportVideo.objects.get(
            course_import=draft,
            lesson_id="lesson-local-1",
        )
        self.assertEqual(staged.original_filename, "support-resistance-intro.mp4")
        self.assertEqual(staged.size_bytes, len(b"test-video-source-bytes"))
        self.assertTrue(Path(self.temp_dir.name, staged.source_file.name).is_file())
        self.assertEqual(staged.source_file.url, "")

        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        reloaded = next(
            item for item in refreshed.json()["drafts"]
            if item["serverDraftId"] == str(draft.pk)
        )
        lesson = reloaded["modules"][0]["lessons"][0]
        self.assertEqual(lesson["id"], "lesson-local-1")
        self.assertEqual(lesson["protectedVideo"]["id"], str(staged.pk))
        self.assertEqual(lesson["protectedVideo"]["kind"], "staged")
        self.assertEqual(lesson["protectedVideo"]["status"], "stored_for_draft")
        self.assertEqual(
            lesson["protectedVideo"]["filename"],
            "support-resistance-intro.mp4",
        )

    def test_tiptap_video_upload_rejects_stale_draft_revision_before_storage(self):
        draft = self.create_saved_draft()
        stale_revision = draft.updated_at.isoformat()
        draft.title = "Changed from another editor"
        draft.save(update_fields=["title", "updated_at"])

        response = self.client.post(
            reverse(
                "staff_course_builder_video_upload",
                args=[draft.pk, "lesson-local-1"],
            ),
            {
                "file": SimpleUploadedFile(
                    "stale-video.mp4",
                    b"stale-video-source",
                    content_type="video/mp4",
                ),
                "expected_updated_at": stale_revision,
            },
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertTrue(response.json()["conflict"])
        self.assertEqual(CourseImportVideo.objects.filter(course_import=draft).count(), 0)
        self.assertEqual(list(Path(self.temp_dir.name).rglob("*.mp4")), [])

    def test_upload_rejects_unknown_lesson_and_unsupported_file_type(self):
        draft = self.create_saved_draft()
        unknown_lesson = self.client.post(
            reverse(
                "staff_course_builder_video_upload",
                args=[draft.pk, "lesson-does-not-exist"],
            ),
            {
                "file": SimpleUploadedFile(
                    "lesson.mp4", b"source", content_type="video/mp4"
                )
            },
        )
        self.assertEqual(unknown_lesson.status_code, 404)

        invalid_type = self.client.post(
            reverse(
                "staff_course_builder_video_upload",
                args=[draft.pk, "lesson-local-1"],
            ),
            {
                "file": SimpleUploadedFile(
                    "lesson.txt", b"not-a-video", content_type="text/plain"
                )
            },
        )
        self.assertEqual(invalid_type.status_code, 400)
        self.assertFalse(CourseImportVideo.objects.filter(course_import=draft).exists())

    def test_builder_shows_protected_video_upload_control(self):
        response = self.client.get(reverse("staff_course_builder_preview"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Protected lesson video")
        self.assertContains(response, "data-protected-video-upload")
        self.assertContains(response, "staff/course-builder/videos/")

    def test_editing_a_published_course_shows_existing_protected_stream_status(self):
        from apps.academy.course_builder_api import _builder_state_from_published_course

        course = Course.objects.create(
            title="Published video edit course",
            slug="published-video-edit-course",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Video module",
            slug="video-module",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Existing protected lesson",
            slug="existing-protected-lesson",
            format=Lesson.Format.VIDEO,
            position=1,
            is_published=True,
            content_markdown="## Notice\n\nDescribe the evidence.",
        )
        video = ProtectedLessonVideo.objects.create(
            lesson=lesson,
            status=ProtectedLessonVideo.Status.READY,
            stream_directory=f"streams/{lesson.pk}/ready",
        )
        video.source_file.save(
            "existing-lesson.mp4",
            ContentFile(b"private-video-source"),
            save=True,
        )

        state = _builder_state_from_published_course(course)
        editor_lesson = state["modules"][0]["lessons"][0]

        self.assertEqual(editor_lesson["id"], str(lesson.pk))
        self.assertEqual(editor_lesson["protectedVideo"]["id"], str(video.pk))
        self.assertEqual(editor_lesson["protectedVideo"]["kind"], "protected")
        self.assertEqual(editor_lesson["protectedVideo"]["status"], "ready")
        self.assertTrue(editor_lesson["protectedVideo"]["has_source"])
        self.assertNotIn(video.source_file.name, str(editor_lesson["protectedVideo"]))

    def test_admin_desk_cleanup_deletes_staged_private_video_file(self):
        draft = self.create_saved_draft("builder-video-cleanup-course")
        staged = CourseImportVideo(
            course_import=draft,
            lesson_id="lesson-local-1",
            original_filename="cleanup-video.mp4",
            size_bytes=12,
            uploaded_by=self.admin,
        )
        staged.source_file.save(
            "cleanup-video.mp4",
            ContentFile(b"private-video"),
            save=True,
        )
        storage_path = Path(self.temp_dir.name, staged.source_file.name)
        self.assertTrue(storage_path.is_file())

        desk_admin = User.objects.create_user(
            username="video-cleanup-admin",
            password="test-password",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.client.force_login(desk_admin)
        with (
            patch("apps.admin_desk_views._audit"),
            self.captureOnCommitCallbacks(execute=True),
        ):
            response = self.client.post(
                reverse("staff_admin_desk_course_import_delete", args=[draft.pk]),
                {"confirmation": "DELETE"},
            )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(storage_path.exists())
        self.assertFalse(CourseImportVideo.objects.filter(pk=staged.pk).exists())


class CourseBuilderProtectedVideoPublicationTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        settings_context = override_settings(
            DEBUG=True,
            ACADEMY_VIDEO_STORAGE_BACKEND="filesystem",
            ACADEMY_VIDEO_STORAGE_ROOT=self.temp_dir.name,
            ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE=False,
        )
        settings_context.enable()
        self.addCleanup(settings_context.disable)

        self.admin = User.objects.create_user(
            username="course-video-publisher",
            password="test-password",
            role=User.Role.ADMIN,
        )

    def test_publication_transfers_staged_source_and_queues_protected_processing(self):
        record = CourseImport.objects.create(
            course_slug="published-video-course",
            title="Published Video Course",
            manifest_version="course-builder-v1",
            content_hash="a" * 64,
            source_manifest="builder://published-video-course",
            status=CourseImport.Status.REVIEW,
            imported_by=self.admin,
            payload={
                "course": {
                    "title": "Published Video Course",
                    "slug": "published-video-course",
                    "summary": "A practical course for disciplined technical analysis.",
                    "description": "A course about observing price behaviour.",
                    "category": "Technical analysis",
                    "level": "Intermediate",
                    "estimated_duration": "Self-paced",
                    "access_type": Course.AccessType.FREE,
                    "learning_outcomes": ["Describe observable price behaviour."],
                    "position": 0,
                    "catalogue_role": Course.CatalogueRole.MINI,
                },
                "modules": [
                    {
                        "slug": "foundations",
                        "title": "Foundations",
                        "summary": "",
                        "position": 1,
                        "lessons": [
                            {
                                "builder_lesson_id": "lesson-local-1",
                                "slug": "first-principles",
                                "title": "First principles",
                                "summary": "Start with observation.",
                                "position": 1,
                                "duration_minutes": 12,
                                "release_day": 1,
                                "is_preview": False,
                                "format": "video",
                                "content_markdown": "## Notice\n\nDescribe what is visible.",
                                "content_json": {"schema_version": 1, "video_url": ""},
                            }
                        ],
                    }
                ],
                "assets": [],
            },
        )
        staged = CourseImportVideo(
            course_import=record,
            lesson_id="lesson-local-1",
            original_filename="first-principles.mp4",
            size_bytes=12,
            uploaded_by=self.admin,
        )
        staged.source_file.save(
            "first-principles.mp4",
            ContentFile(b"private-video", name="first-principles.mp4"),
            save=True,
        )
        staged_source_name = staged.source_file.name
        self.assertTrue(Path(self.temp_dir.name, staged_source_name).is_file())

        with (
            patch("apps.academy.importing.validate_import_for_publish", return_value=[]),
            patch("apps.academy.importing.sync_free_membership_course_access"),
            patch("apps.audit.models.AuditLog.log"),
            patch("apps.jobs.enqueue.enqueue_generic") as enqueue,
            self.captureOnCommitCallbacks(execute=True),
        ):
            course = publish_course_import(record, user=self.admin)

        lesson = course.modules.get(slug="foundations").lessons.get(slug="first-principles")
        protected_video = ProtectedLessonVideo.objects.get(lesson=lesson)
        self.assertEqual(
            ProtectedLessonVideo._meta.get_field("source_file").max_length,
            512,
        )
        self.assertEqual(protected_video.source_file.name, staged_source_name)
        self.assertEqual(protected_video.status, ProtectedLessonVideo.Status.PENDING)
        self.assertTrue(Path(self.temp_dir.name, protected_video.source_file.name).is_file())
        self.assertFalse(
            CourseImportVideo.objects.filter(
                course_import=record,
                lesson_id="lesson-local-1",
            ).exists()
        )
        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.args[0], "process_protected_lesson_video")
        self.assertEqual(enqueue.call_args.args[1]["video_id"], str(protected_video.pk))
        self.assertTrue(enqueue.call_args.args[1]["force"])
