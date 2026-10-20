"""Security and rendering tests for in-context lesson references."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .content_rendering import render_safe_markdown
from .models import Course, CourseModule, Lesson

User = get_user_model()


class LessonReferenceRenderingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="lesson-reference-learner",
            password="test-password",
            role="learner",
        )
        self.course = Course.objects.create(
            title="Volume and Price Analysis",
            slug="volume-price-analysis",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(
            course=self.course, title="Volume context", slug="volume-context",
            position=1, is_published=True,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Read relative volume",
            slug="read-relative-volume",
            summary="Compare activity with progress in price.",
            content_markdown="PRIVATE_DESTINATION_BODY",
            position=1, is_preview=True, is_published=True,
        )

    def test_inline_link_resolves_to_the_accessible_lesson(self):
        rendered = render_safe_markdown(
            f"See [[lesson:{self.lesson.pk}]] for the worked example.",
            user=self.user,
        )
        expected_url = reverse(
            "academy:lesson", args=[self.course.slug, self.lesson.pk],
        )
        self.assertIn(f'href="{expected_url}"', rendered)
        self.assertIn("Read relative volume", rendered)
        self.assertNotIn("PRIVATE_DESTINATION_BODY", rendered)

    def test_related_lesson_card_renders_live_catalogue_metadata(self):
        rendered = render_safe_markdown(
            f"[[lesson-card:{self.lesson.pk}]]",
            user=self.user,
        )
        expected_url = reverse(
            "academy:lesson", args=[self.course.slug, self.lesson.pk],
        )
        self.assertIn('class="tt-inline-lesson-card"', rendered)
        self.assertIn(f'href="{expected_url}"', rendered)
        self.assertIn("Compare activity with progress in price.", rendered)

    def test_restricted_lesson_links_to_course_access_page_not_lesson_body(self):
        self.lesson.is_preview = False
        self.lesson.save(update_fields=["is_preview"])
        rendered = render_safe_markdown(
            f"See [[lesson:{self.lesson.pk}]] for more detail.",
            user=self.user,
        )
        course_url = reverse("academy:course-detail", args=[self.course.slug])
        self.assertIn(f'href="{course_url}"', rendered)
        self.assertNotIn(
            reverse("academy:lesson", args=[self.course.slug, self.lesson.pk]),
            rendered,
        )
        self.assertNotIn("PRIVATE_DESTINATION_BODY", rendered)

    def test_unpublished_destination_becomes_a_safe_placeholder(self):
        self.lesson.is_published = False
        self.lesson.save(update_fields=["is_published"])
        rendered = render_safe_markdown(
            f"See [[lesson:{self.lesson.pk}]] for more detail.",
            user=self.user,
        )
        self.assertIn("Related lesson unavailable.", rendered)
        self.assertNotIn("Read relative volume", rendered)
        self.assertNotIn("PRIVATE_DESTINATION_BODY", rendered)
