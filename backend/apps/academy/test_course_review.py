"""Regression tests for read-only course-import review and learner lesson tabs."""
from types import SimpleNamespace
import uuid

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
