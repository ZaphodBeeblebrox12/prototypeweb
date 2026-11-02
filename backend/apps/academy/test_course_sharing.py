from django.test import TestCase
from django.urls import reverse

from .course_sharing import (
    DEFAULT_SHARE_MESSAGE,
    course_share_description,
    course_share_message,
    course_share_title,
)
from .models import Course


class CourseShareCopyTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Support & Resistance",
            slug="support-resistance-share-test",
            summary="Learn to mark meaningful price zones.",
            status=Course.Status.PUBLISHED,
            catalogue_role=Course.CatalogueRole.MINI,
        )

    def test_default_copy_inserts_course_title(self):
        self.assertEqual(course_share_title(self.course), self.course.title)
        self.assertEqual(
            course_share_message(self.course),
            DEFAULT_SHARE_MESSAGE.replace("{course_title}", self.course.title),
        )

    def test_course_specific_copy_overrides_default(self):
        self.course.share_title = "A useful chart-reading course"
        self.course.share_message = "Take a look at {course_title}."
        self.course.save(update_fields=["share_title", "share_message", "updated_at"])
        self.assertEqual(
            course_share_title(self.course), "A useful chart-reading course"
        )
        self.assertEqual(
            course_share_message(self.course), "Take a look at Support & Resistance."
        )
        self.assertEqual(
            course_share_description(self.course),
            "Take a look at Support & Resistance.",
        )

    def test_share_page_is_public_and_includes_social_metadata(self):
        response = self.client.get(
            reverse("academy:course-share", args=[self.course.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, "Support &amp; Resistance")
        self.assertContains(response, 'property="og:image"')
        self.assertContains(response, "/assets/tradethesis-icon.png")
        self.assertContains(response, 'property="og:image:alt"')
        self.assertContains(response, 'name="twitter:card" content="summary"')

    def test_hidden_courses_cannot_be_shared(self):
        self.course.catalogue_role = Course.CatalogueRole.HIDDEN
        self.course.save(update_fields=["catalogue_role", "updated_at"])
        response = self.client.get(
            reverse("academy:course-share", args=[self.course.slug])
        )
        self.assertEqual(response.status_code, 404)
