"""Regression tests for read-only course-import review and learner lesson tabs."""
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from .models import Course, CourseImport

User = get_user_model()


class CourseReviewTemplateTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="course-review-author",
            password="test-password",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(self.admin)

    def test_review_preview_renders_notebook_prompts_read_only(self):
        slug = "review-template-regression-course"
        record = CourseImport.objects.create(
            course_slug=slug,
            title="Review Template Regression Course",
            manifest_version="course-builder-v1",
            content_hash="a" * 64,
            source_manifest=f"builder://{slug}",
            status=CourseImport.Status.REVIEW,
            imported_by=self.admin,
            payload={
                "course": {"title": "Review Template Regression Course", "slug": slug},
                "assets": [],
                "modules": [{
                    "slug": "foundations",
                    "title": "Foundations",
                    "summary": "",
                    "position": 1,
                    "lessons": [{
                        "source_id": "1.1",
                        "slug": "first-principles",
                        "title": "First principles",
                        "summary": "",
                        "position": 1,
                        "duration_minutes": 12,
                        "content_markdown": "## Notice\n\nDescribe what is visible before interpreting it.",
                        "content_json": {
                            "asset_ids": [],
                            "notebook": {
                                "title": "Evidence notebook",
                                "prompts": [{
                                    "label": "Observe",
                                    "text": "What evidence can you see?",
                                }],
                            },
                        },
                    }],
                }],
            },
        )

        response = self.client.get(
            reverse("admin:academy_courseimport_review", args=[record.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Evidence notebook")
        self.assertContains(response, "What evidence can you see?")
        self.assertNotContains(response, "data-notebook-response")
        self.assertNotContains(response, "lesson-notebook-submit")
        self.assertNotContains(response, "data-practice-quiz")

    def test_staging_authored_bollinger_source_creates_review_only_preview(self):
        slug = "understand-bollinger-bands"
        record = CourseImport.objects.create(
            course_slug=slug,
            title="Understand Bollinger Bands",
            manifest_version="1.0",
            content_hash="b" * 64,
            source_manifest=f"course-source/{slug}/course-manifest.json",
            status=CourseImport.Status.REVIEW,
            imported_by=self.admin,
            payload={
                "course": {"title": "Understand Bollinger Bands", "slug": slug},
                "assets": [],
                "modules": [],
            },
        )
        payload = {
            "course": {"title": "Understand Bollinger Bands", "slug": slug},
            "assets": [],
            "modules": [],
        }
        with (
            patch("apps.academy.admin.inspect_manifest", return_value=(payload, {}, [])) as inspect,
            patch("apps.academy.admin.stage_course_import", return_value=(record, True, [])) as stage,
        ):
            response = self.client.post(
                reverse("admin:academy_courseimport_stage_bollinger")
            )

        self.assertRedirects(
            response,
            reverse("admin:academy_courseimport_review", args=[record.pk]),
            fetch_redirect_response=False,
        )
        inspect.assert_called_once()
        stage.assert_called_once()
        self.assertEqual(stage.call_args.kwargs["imported_by"], self.admin)
        self.assertEqual(record.status, CourseImport.Status.REVIEW)

    def test_staging_authored_bollinger_source_requires_post(self):
        with patch("apps.academy.admin.inspect_manifest") as inspect:
            response = self.client.get(
                reverse("admin:academy_courseimport_stage_bollinger")
            )
        self.assertEqual(response.status_code, 405)
        inspect.assert_not_called()

    def test_course_import_changelist_offers_secure_canonical_staging_action(self):
        response = self.client.get(reverse("admin:academy_courseimport_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stage Understand Bollinger Bands for review")
        self.assertContains(response, "csrfmiddlewaretoken")

    def _website_preview_record(self, video_url=None, course_slug="website-preview-course", related_course_ids=None):
        return CourseImport.objects.create(
            course_slug=course_slug,
            title="Website Preview Course",
            manifest_version="1.0",
            content_hash="d" * 64,
            source_manifest="builder://website-preview-course",
            status=CourseImport.Status.REVIEW,
            imported_by=self.admin,
            payload={
                "course": {
                    "title": "Website Preview Course",
                    "slug": "website-preview-course",
                    "summary": "A short promise for the course.",
                    "description": "A course description for the learner-facing page.",
                },
                "notebook": {
                    "title": "Evidence notebook",
                    "prompts": [{"label": "Observe", "text": "What evidence is visible?"}],
                },
                "assets": [],
                "modules": [{
                    "slug": "foundations",
                    "title": "Foundations",
                    "summary": "Start by observing the chart.",
                    "position": 1,
                    "lessons": [
                        {
                            "source_id": "1.1",
                            "slug": "first-principles",
                            "title": "First principles",
                            "summary": "Begin with visible evidence.",
                            "position": 1,
                            "duration_minutes": 12,
                            "content_markdown": (
                                "## The idea\n\nAuthored lesson text for the website preview.\n\n"
                                "## Chart examples\n\nCompare the two cases.\n\n"
                                "## Test your reading\n\nWhat evidence would change your view?"
                            ),
                            "content_json": {
                                "asset_ids": [],
                                "video_url": video_url,
                                "related_course_ids": related_course_ids or [],
                                "notebook": {
                                    "title": "Evidence notebook",
                                    "prompts": [{
                                        "label": "Observe",
                                        "text": "What evidence is visible?",
                                    }],
                                },
                            },
                        },
                        {
                            "source_id": "1.2",
                            "slug": "second-principles",
                            "title": "Second principles",
                            "summary": "",
                            "position": 2,
                            "duration_minutes": 13,
                            "content_markdown": "## The idea\n\nSecond lesson body.",
                            "content_json": {"asset_ids": []},
                        },
                    ],
                }],
            },
        )

    def test_website_preview_uses_shared_shell_and_shows_full_curriculum(self):
        record = self._website_preview_record()
        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Website Preview Course")
        self.assertContains(response, "A short promise for the course.")
        self.assertContains(response, 'class="tt-course-overview')
        self.assertContains(response, "ADMIN PREVIEW")
        self.assertContains(response, "First principles")
        self.assertContains(response, "Second principles")
        self.assertContains(response, "Content review")
        self.assertNotContains(response, "data-notebook-response")
        self.assertNotContains(response, "data-practice-quiz")
        self.assertIsNone(response.context["selected_lesson"])

    def test_website_preview_renders_lesson_tabs_read_only(self):
        record = self._website_preview_record()
        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk]),
            {"lesson": "1.1"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "tt-admin-learning-preview")
        self.assertContains(response, "The idea")
        self.assertContains(response, "Chart examples")
        self.assertContains(response, "Test your reading")
        self.assertContains(response, "Authored lesson text for the website preview.")
        self.assertContains(response, "Evidence notebook")
        self.assertContains(response, "What evidence is visible?")
        self.assertNotContains(response, "data-notebook-response")
        self.assertNotContains(response, "data-practice-quiz")
        self.assertNotContains(response, "Mark complete")
        self.assertEqual(response.context["selected_lesson"]["source_id"], "1.1")

    def test_website_preview_renders_mp4_video_inline_before_lesson_tabs(self):
        video_url = "https://media.example.test/lesson.mp4?token=preview"
        record = self._website_preview_record(video_url=video_url)
        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk]),
            {"lesson": "1.1"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'class="tt-video-lesson"')
        self.assertContains(response, '<video controls preload="metadata"')
        self.assertContains(response, f'src="{video_url}"')
        self.assertTrue(response.context["selected_video_is_file"])
        self.assertLess(
            response.content.index(b'class="tt-video-lesson"'),
            response.content.index(b'id="lesson-tab-idea"'),
        )

    def test_website_preview_links_external_video_and_ignores_unsafe_url(self):
        external_url = "https://video.example.test/lesson/123"
        record = self._website_preview_record(video_url=external_url)
        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk]),
            {"lesson": "1.1"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, f'href="{external_url}"')
        self.assertContains(response, "Open lesson video")
        self.assertFalse(response.context["selected_video_is_file"])

        unsafe_record = self._website_preview_record(
            video_url="javascript:alert(1)",
            course_slug="website-preview-unsafe-video",
        )
        unsafe_response = self.client.get(
            reverse("academy:course-import-preview", args=[unsafe_record.pk]),
            {"lesson": "1.1"},
        )

        self.assertEqual(unsafe_response.status_code, 200, unsafe_response.content)
        self.assertNotContains(unsafe_response, 'class="tt-video-lesson"')
        self.assertEqual(unsafe_response.context["selected_video_url"], "")

    def test_website_preview_renders_published_related_courses_only(self):
        published = Course.objects.create(
            title="Volume and Price Analysis",
            slug="volume-and-price-analysis",
            summary="Study effort, result and volume context.",
            status=Course.Status.PUBLISHED,
        )
        unpublished = Course.objects.create(
            title="Unpublished Draft Course",
            slug="unpublished-draft-course",
            summary="This must not appear in a learner-facing reference.",
            status=Course.Status.DRAFT,
        )
        record = self._website_preview_record(
            related_course_ids=[str(published.pk), str(unpublished.pk), "not-a-uuid"],
        )
        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk]),
            {"lesson": "1.1"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Continue learning")
        self.assertContains(response, "Volume and Price Analysis")
        self.assertContains(response, "Study effort, result and volume context.")
        self.assertContains(response, reverse("academy:course-detail", args=[published.slug]))
        self.assertNotContains(response, "Unpublished Draft Course")
        self.assertNotContains(response, "This must not appear in a learner-facing reference.")
        self.assertEqual(list(response.context["selected_related_courses"]), [published])

    def test_website_preview_places_lesson_header_in_main_column(self):
        record = self._website_preview_record()
        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk]),
            {"lesson": "1.1"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        content = response.content
        grid_index = content.index(b'class="tt-room-grid"')
        outline_index = content.index(b'class="tt-outline"')
        main_index = content.index(b'<main class="tt-lesson-main">')
        header_index = content.index(b'<header class="tt-course-header tt-course-header--depth">')
        article_index = content.index(b'<article class="tt-lesson-article">')
        self.assertLess(grid_index, outline_index)
        self.assertLess(outline_index, main_index)
        self.assertLess(main_index, header_index)
        self.assertLess(header_index, article_index)

    def test_website_preview_is_for_course_content_admins_only(self):
        record = self._website_preview_record()
        learner = User.objects.create_user(
            username="website-preview-learner",
            password="test-password",
            role="learner",
        )
        self.client.force_login(learner)

        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_content_review_links_to_website_preview(self):
        record = self._website_preview_record()
        response = self.client.get(
            reverse("admin:academy_courseimport_review", args=[record.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("academy:course-import-preview", args=[record.pk]),
        )
        self.assertContains(response, "View website preview")

    def test_shared_tabs_keep_notebook_form_for_a_real_lesson(self):
        lesson_id = uuid.uuid4()
        rendered = render_to_string(
            "academy/partials/lesson_tabs.html",
            {
                "lesson": SimpleNamespace(id=lesson_id),
                "lesson_sections": {
                    "idea_html": "<p>Idea</p>",
                    "examples_html": "<p>Examples</p>",
                    "practice_html": "<p>Practice</p>",
                    "figure_count": 0,
                },
                "notebook": {
                    "title": "Learner notebook",
                    "prompts": [{"label": "Observe", "text": "What is visible?"}],
                },
                "practice_questions": [],
            },
        )

        self.assertIn("data-notebook-response", rendered)
        self.assertIn(
            reverse("academy:lesson-notebook-submit", args=[lesson_id]),
            rendered,
        )
