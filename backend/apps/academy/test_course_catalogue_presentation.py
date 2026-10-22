"""Regression coverage for authored public catalogue presentation metadata."""
import hashlib
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Course, CourseImport, CourseModule, Lesson


class PublicCataloguePresentationTests(TestCase):
    def test_published_course_returns_editorial_copy_and_tags_without_lesson_bodies(self):
        course = Course.objects.create(
            title="Support & Resistance", slug="support-resistance",
            summary="Legacy short summary.", description="Existing catalogue description.",
            category="Chart reading", level="Foundational skill", status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course, title="Mark the chart with purpose", slug="mark-the-chart-with-purpose",
            description="Practise useful zones.", position=1, is_published=True,
        )
        Lesson.objects.create(
            module=module, title="Swing highs and lows", slug="swing-highs-and-lows",
            summary="Spot meaningful swings.", content_markdown="PRIVATE LESSON BODY MUST NOT BE RETURNED",
            position=1, is_published=True,
        )
        presentation = {
            "hook": "Mark fewer zones. Give each one a reason.",
            "problem": "For traders who see a possible level around every swing and need a reason to keep or discard it.",
            "learning_focus": "Choose and defend relevant zones, read reactions and breaks, and identify invalidation.",
            "tags": ["Chart reading", "Zones"],
            "why_this_one": "Treats zones as decision areas to justify, test and invalidate—not lines to collect.",
        }
        CourseImport.objects.create(
            course_slug=course.slug, title=course.title, manifest_version="course-builder-v1",
            content_hash=hashlib.sha256(b"catalogue presentation test").hexdigest(),
            source_manifest="{}", payload={"course": {"slug": course.slug, "catalogue_presentation": presentation, "catalogue_presentation_configured": True}},
            status=CourseImport.Status.PUBLISHED, target_course=course, published_at=timezone.now(),
        )
        response = self.client.get(reverse("academy_public_catalogue"))
        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.json()["courses"] if item["slug"] == "support-resistance")
        self.assertEqual(row["hook"], presentation["hook"])
        self.assertEqual(row["problem"], presentation["problem"])
        self.assertEqual(row["learningFocus"], presentation["learning_focus"])
        self.assertEqual(row["tags"], presentation["tags"])
        self.assertEqual(row["whyThisOne"], presentation["why_this_one"])
        self.assertTrue(row["cataloguePresentationConfigured"])
        self.assertNotIn("PRIVATE LESSON BODY MUST NOT BE RETURNED", response.content.decode("utf-8"))

    def test_unconfigured_legacy_course_does_not_claim_authored_metadata(self):
        course = Course.objects.create(
            title="Legacy catalogue course", slug="legacy-catalogue-course",
            summary="A useful learner-facing course summary.", status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course, title="Course basics", slug="course-basics", position=1, is_published=True,
        )
        Lesson.objects.create(module=module, title="First reading", slug="first-reading", position=1, is_published=True, content_markdown="Read the chart carefully.")
        response = self.client.get(reverse("academy_public_catalogue"))
        row = next(item for item in response.json()["courses"] if item["slug"] == course.slug)
        self.assertFalse(row["cataloguePresentationConfigured"])
        self.assertEqual(row["tags"], [])
        self.assertEqual(row["hook"], "")
