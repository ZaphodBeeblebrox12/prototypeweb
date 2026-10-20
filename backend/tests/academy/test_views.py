import re
from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.academy.models import (
    Course,
    CourseEntitlement,
    CourseMediaAsset,
    CourseModule,
    Lesson,
    LessonProgress,
)
from apps.academy.storage import course_asset_storage

User = get_user_model()


class AcademyViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="Test-password-123!")
        self.course = Course.objects.create(
            title="Trading Path", slug="trading-path", status=Course.Status.PUBLISHED,
            summary="Learn to read the screen.",
        )
        self.module = CourseModule.objects.create(
            course=self.course, title="Foundations", slug="foundations",
            position=1, is_published=True,
        )
        self.paid_lesson = Lesson.objects.create(
            module=self.module, title="Private lesson", slug="private-lesson",
            position=1, is_published=True, content_markdown="SECRET PAID LESSON BODY",
        )
        self.preview_lesson = Lesson.objects.create(
            module=self.module, title="Preview lesson", slug="preview-lesson",
            position=2, is_published=True, is_preview=True,
            content_markdown="Public preview content.",
        )
        self.client.force_login(self.user)

    def test_course_overview_does_not_include_paid_lesson_body(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Private lesson")
        self.assertNotContains(response, "SECRET PAID LESSON BODY")

    def test_course_overview_uses_content_rich_layout_and_live_course_counts(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="tt-course-overview"')
        self.assertContains(response, 'class="tt-overview-hero"')
        self.assertContains(response, 'class="tt-overview-curriculum-grid"')
        self.assertContains(response, 'academy/course-overview.css')
        self.assertEqual(response.context["total_modules"], 1)
        self.assertEqual(response.context["total_lessons"], 2)
        self.assertEqual(response.context["total_study_minutes"], 20)
        self.assertEqual(response.context["first_accessible_lesson"], self.preview_lesson)

    def test_course_overview_keeps_checkout_unavailable_note_without_bootstrap_alert(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enrolment is not available right now")
        self.assertNotContains(response, 'class="alert alert-info"')

    def test_admin_can_preview_locked_lesson_without_creating_progress(self):
        admin = User.objects.create_user(
            username="course-content-admin",
            password="Test-password-123!",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(admin)

        overview = self.client.get(
            reverse("academy:course-detail", args=[self.course.slug])
        )
        self.assertEqual(overview.status_code, 200)
        preview_url = reverse(
            "academy:admin-lesson-preview",
            args=[self.course.slug, self.paid_lesson.pk],
        )
        self.assertContains(overview, preview_url)
        self.assertContains(overview, "Admin preview")

        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "ADMIN PREVIEW")
        self.assertContains(response, "LOCKED ACCESS BYPASSED FOR REVIEW ONLY")
        self.assertContains(response, "SECRET PAID LESSON BODY")
        self.assertContains(response, "Course outline")
        self.assertNotContains(response, "Mark complete")
        self.assertNotContains(response, "Save reflection")
        self.assertNotContains(response, "Check answers")
        self.assertFalse(
            LessonProgress.objects.filter(user=admin, lesson=self.paid_lesson).exists()
        )

    def test_locked_lesson_preview_is_for_course_content_admins_only(self):
        response = self.client.get(
            reverse("academy:admin-lesson-preview", args=[self.course.slug, self.paid_lesson.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "SECRET PAID LESSON BODY", status_code=403)

    def test_paid_lesson_is_not_retrievable_without_entitlement(self):
        response = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "SECRET PAID LESSON BODY", status_code=403)

    def test_published_preview_lesson_can_be_opened(self):
        response = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public preview content.")

    def test_published_preview_renders_multiple_images_in_selected_learning_room_tabs(self):
        placements = [
            ("Idea figure", "Additional concept figure", "idea", "https://example.com/idea.png"),
            ("Example chart", "Additional chart examples", "examples", "https://example.com/examples.png"),
            ("Practice figure", "Practice figure", "practice", "https://example.com/practice.png"),
        ]
        assets = []
        markdown_parts = ["### The question", "", "Look at the evidence in each panel."]
        for index, (alt_text, heading, _tab, url) in enumerate(placements, start=1):
            asset = CourseMediaAsset.objects.create(
                course=self.course,
                asset_key=f"test/learning-room-figure-{index}",
                alt_text=alt_text,
                original_url=url,
            )
            assets.append(asset)
            markdown_parts.extend([
                "",
                f"### {heading}",
                "",
                f"![{alt_text}](asset://{asset.pk})",
            ])
        self.preview_lesson.content_markdown = "\n".join(markdown_parts)
        self.preview_lesson.content_json = {"asset_ids": [str(asset.pk) for asset in assets]}
        self.preview_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        rendered_html = response.content.decode()
        panel_patterns = {
            tab: re.compile(
                rf'<div class="tt-tab-panel"[^>]*data-tab-panel="{tab}"[^>]*>(.*?)</div>',
                re.DOTALL,
            )
            for tab in ("idea", "examples", "practice")
        }
        panels = {}
        for tab, pattern in panel_patterns.items():
            match = pattern.search(rendered_html)
            self.assertIsNotNone(match, f"Published lesson is missing the {tab} tab panel.")
            panels[tab] = match.group(1)

        self.assertIn('<span class="tt-tab-count">3</span>', rendered_html)
        for alt_text, _heading, expected_tab, url in placements:
            self.assertIn(f'alt="{alt_text}"', panels[expected_tab])
            self.assertIn(f'src="{url}"', panels[expected_tab])
            for other_tab, panel_html in panels.items():
                if other_tab != expected_tab:
                    self.assertNotIn(url, panel_html)

    def test_uploaded_replacement_renders_through_protected_media_and_retains_source_url(self):
        source_url = "https://example.com/charts/original.png"
        image_bytes = BytesIO()
        Image.new("RGB", (12, 8), (245, 220, 170)).save(image_bytes, format="PNG")
        asset = CourseMediaAsset.objects.create(
            course=self.course,
            asset_key="test/uploaded-replacement",
            alt_text="Uploaded replacement chart",
            original_url=source_url,
        )
        asset.file.save(
            "replacement.png",
            SimpleUploadedFile("replacement.png", image_bytes.getvalue(), content_type="image/png"),
            save=True,
        )
        stored_name = asset.file.name
        self.addCleanup(lambda: course_asset_storage.delete(stored_name))

        self.preview_lesson.content_markdown = f"![Uploaded replacement chart](asset://{asset.pk})"
        self.preview_lesson.content_json = {"asset_ids": [str(asset.pk)]}
        self.preview_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        protected_url = reverse("academy:media-asset", args=[asset.pk])
        self.assertContains(response, f'src="{protected_url}"')
        self.assertNotContains(response, source_url)

        media_response = self.client.get(protected_url)
        self.assertEqual(media_response.status_code, 200)
        self.assertEqual(media_response["Content-Type"], "image/png")
        self.assertEqual(media_response["Cache-Control"], "private, no-store")
        self.assertEqual(media_response["X-Content-Type-Options"], "nosniff")

    def test_uploaded_media_for_unentitled_paid_lesson_is_forbidden(self):
        image_bytes = BytesIO()
        Image.new("RGB", (12, 8), (245, 220, 170)).save(image_bytes, format="PNG")
        asset = CourseMediaAsset.objects.create(
            course=self.course,
            asset_key="test/private-paid-image",
            alt_text="Private lesson chart",
            original_url="https://example.com/charts/private-original.png",
        )
        asset.file.save(
            "private-chart.png",
            SimpleUploadedFile("private-chart.png", image_bytes.getvalue(), content_type="image/png"),
            save=True,
        )
        stored_name = asset.file.name
        self.addCleanup(lambda: course_asset_storage.delete(stored_name))
        self.paid_lesson.content_markdown = f"![Private lesson chart](asset://{asset.pk})"
        self.paid_lesson.content_json = {"asset_ids": [str(asset.pk)]}
        self.paid_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

        response = self.client.get(reverse("academy:media-asset", args=[asset.pk]))
        self.assertEqual(response.status_code, 403)

    def test_progress_endpoint_rejects_unentitled_paid_lesson(self):
        response = self.client.post(
            reverse("academy:lesson-progress", args=[self.paid_lesson.pk]),
            {"status": "completed"},
        )
        self.assertEqual(response.status_code, 403)


    def test_opening_accessible_lesson_saves_an_in_progress_resume_point(self):
        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.preview_lesson)
        self.assertEqual(progress.status, LessonProgress.Status.IN_PROGRESS)
        self.assertIsNotNone(progress.started_at)
        self.assertIsNotNone(progress.last_seen_at)

    def test_completed_lesson_remains_completed_when_reopened(self):
        self.client.post(
            reverse("academy:lesson-progress", args=[self.preview_lesson.pk]),
            {"status": LessonProgress.Status.COMPLETED},
        )
        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.preview_lesson)
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)
        self.assertIsNotNone(progress.completed_at)

    def test_progress_status_cannot_regress_from_completed(self):
        endpoint = reverse("academy:lesson-progress", args=[self.preview_lesson.pk])
        completed = self.client.post(endpoint, {"status": LessonProgress.Status.COMPLETED})
        self.assertEqual(completed.status_code, 200)
        for status in (LessonProgress.Status.IN_PROGRESS, LessonProgress.Status.NOT_STARTED):
            response = self.client.post(endpoint, {"status": status})
            self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.preview_lesson)
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)

    def test_progress_endpoint_is_post_only(self):
        response = self.client.get(
            reverse("academy:lesson-progress", args=[self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_expired_entitlement_does_not_open_paid_lesson(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=now - timedelta(days=3),
            expires_at=now - timedelta(days=1),
        )
        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        )
        self.assertEqual(response.status_code, 403)


    def test_unpublished_lesson_and_module_cannot_be_opened_directly(self):
        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])

        self.paid_lesson.is_published = False
        self.paid_lesson.save(update_fields=["is_published", "updated_at"])
        self.assertEqual(self.client.get(lesson_url).status_code, 404)

        self.paid_lesson.is_published = True
        self.paid_lesson.save(update_fields=["is_published", "updated_at"])
        self.module.is_published = False
        self.module.save(update_fields=["is_published", "updated_at"])
        self.assertEqual(self.client.get(lesson_url).status_code, 404)

    def test_draft_course_does_not_expose_even_a_preview_lesson(self):
        self.course.status = Course.Status.DRAFT
        self.course.save(update_fields=["status", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "Public preview content.", status_code=403)

    def test_revoked_entitlement_denies_lesson_and_progress_endpoint(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.REVOKED,
            starts_at=now - timedelta(days=3),
            expires_at=None,
        )

        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        self.assertEqual(self.client.get(lesson_url).status_code, 403)

        progress_url = reverse("academy:lesson-progress", args=[self.paid_lesson.pk])
        response = self.client.post(progress_url, {"status": LessonProgress.Status.COMPLETED})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            LessonProgress.objects.filter(user=self.user, lesson=self.paid_lesson).exists()
        )

    def test_unreleased_lesson_denies_direct_access_and_progress_updates(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=now - timedelta(hours=1),
            expires_at=None,
        )
        self.paid_lesson.release_day = 2
        self.paid_lesson.save(update_fields=["release_day", "updated_at"])

        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        self.assertEqual(self.client.get(lesson_url).status_code, 403)
        progress_url = reverse("academy:lesson-progress", args=[self.paid_lesson.pk])
        response = self.client.post(progress_url, {"status": LessonProgress.Status.COMPLETED})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            LessonProgress.objects.filter(user=self.user, lesson=self.paid_lesson).exists()
        )

    def test_course_progress_excludes_unpublished_lessons_and_other_users(self):
        other_user = User.objects.create_user(
            username="other-learner", password="Test-password-123!"
        )
        hidden_lesson = Lesson.objects.create(
            module=self.module,
            title="Unpublished lesson",
            slug="unpublished-lesson",
            position=3,
            is_published=False,
            content_markdown="Must not contribute to visible progress.",
        )
        LessonProgress.objects.create(
            user=self.user, lesson=self.preview_lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        LessonProgress.objects.create(
            user=other_user, lesson=self.paid_lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        LessonProgress.objects.create(
            user=self.user, lesson=hidden_lesson,
            status=LessonProgress.Status.COMPLETED,
        )

        response = self.client.get(
            reverse("academy:course-detail", args=[self.course.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_lessons"], 2)
        self.assertEqual(response.context["completed_lessons"], 1)
        self.assertEqual(response.context["progress_percent"], 50)

    def test_learning_room_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("academy:home"))
        self.assertEqual(response.status_code, 302)
