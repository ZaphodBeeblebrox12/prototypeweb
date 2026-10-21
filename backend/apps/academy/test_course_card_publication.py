"""Regression coverage for publish eligibility and Option 4 course-card parity."""
import re
import uuid
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from .course_card_utils import course_card_publication_issue, is_course_card_recommendable
from .importing import publish_course_import, validate_import_for_publish
from .models import Course, CourseImport

User = get_user_model()


class CoursePublicationReadinessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="course-publication-readiness-admin",
            password="test-password",
            role="admin",
            is_staff=True,
        )

    def make_record(self, *, title, summary, description="", slug="publication-readiness-course"):
        return CourseImport.objects.create(
            course_slug=slug,
            title=title,
            manifest_version="course-builder-v1",
            content_hash=uuid.uuid4().hex * 2,
            source_manifest="builder://" + slug,
            status=CourseImport.Status.REVIEW,
            imported_by=self.admin,
            payload={
                "course": {
                    "title": title,
                    "slug": slug,
                    "summary": summary,
                    "description": description,
                },
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
                        "release_day": 1,
                        "content_markdown": "## Evidence\n\nDescribe the visible evidence before interpreting it.",
                        "content_json": {"asset_ids": []},
                    }],
                }],
            },
        )

    def test_starter_course_title_cannot_pass_publication_validation(self):
        record = self.make_record(
            title="Untitled course",
            summary="Add a concise course promise here.",
            description="Describe the learner and what the course covers.",
            slug="untitled-course-publication-blocked",
        )

        errors = validate_import_for_publish(record)

        self.assertTrue(any("starter course title" in error.lower() for error in errors))
        with self.assertRaises(ValidationError):
            publish_course_import(record, user=self.admin)
        self.assertFalse(Course.objects.filter(slug=record.course_slug).exists())

    def test_starter_course_summary_cannot_pass_publication_validation(self):
        record = self.make_record(
            title="Volume and Price Analysis",
            summary="Add a concise course promise here.",
            description="A thoughtful description cannot replace the visible starter summary.",
            slug="placeholder-summary-publication-blocked",
        )

        errors = validate_import_for_publish(record)

        self.assertTrue(any("starter course summary" in error.lower() for error in errors))
        with self.assertRaises(ValidationError):
            publish_course_import(record, user=self.admin)
        self.assertFalse(Course.objects.filter(slug=record.course_slug).exists())

    def test_description_can_supply_real_catalogue_copy_when_summary_is_blank(self):
        issue = course_card_publication_issue(
            "Volume and Price Analysis",
            "",
            "A practical guide to reading activity alongside the price result.",
        )
        self.assertEqual(issue, "")
        self.assertTrue(is_course_card_recommendable(
            "Volume and Price Analysis",
            "",
            "A practical guide to reading activity alongside the price result.",
        ))

    def test_missing_summary_and_description_are_not_catalogue_ready(self):
        self.assertIn(
            "summary",
            course_card_publication_issue("Volume and Price Analysis", "").lower(),
        )


class OptionFourCardParityTests(SimpleTestCase):
    def test_builder_and_learning_room_use_the_same_option_four_css(self):
        root = Path(__file__).resolve().parents[2]
        builder = (root / "apps" / "academy" / "course_builder_preview.html").read_text(encoding="utf-8")
        learner = (root / "static" / "academy" / "lesson-references.css").read_text(encoding="utf-8")
        comment = "/* Option 04 — the mini course preview (shared by Builder, admin preview and learner lessons). */"
        builder_start = builder.index(comment)
        builder_end = builder.index("/* Compact layout for the catalogue selector in the lesson editor. */", builder_start)
        builder_css = builder[builder_start:builder_end].strip()
        learner_css = learner[learner.index(comment):].strip()
        def normalize(text):
            return re.sub(r"\s+", " ", text).strip()

        self.assertEqual(normalize(builder_css), normalize(learner_css))
        self.assertIn("grid-template-columns:minmax(0,1fr) 132px", learner_css)
        self.assertIn("grid-template-columns:1fr", learner_css)
        self.assertIn("tt-course-preview-card__topics", learner_css)
        self.assertIn("tt-course-preview-card__art", learner_css)
        self.assertIn("View course outline", builder)
