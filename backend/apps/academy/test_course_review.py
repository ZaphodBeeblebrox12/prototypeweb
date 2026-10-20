"""Regression tests for read-only course-import review and learner lesson tabs."""
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from .models import CourseImport

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
