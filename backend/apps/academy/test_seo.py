from django.test import TestCase, override_settings
from django.urls import reverse

from apps.academy.models import Course, CourseModule, Lesson


class AcademySeoEndpointTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Support and Resistance",
            slug="support-and-resistance",
            summary="Learn to mark meaningful price zones and assess reactions.",
            status=Course.Status.PUBLISHED,
            catalogue_role=Course.CatalogueRole.MINI,
        )
        module = CourseModule.objects.create(
            course=self.course,
            title="Mark the chart with purpose",
            slug="mark-the-chart",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="Choose meaningful levels",
            slug="choose-meaningful-levels",
            position=1,
            is_published=True,
        )

    @override_settings(TRADETHESIS_SEO_INDEXABLE=False)
    def test_staging_robots_does_not_advertise_a_sitemap(self):
        response = self.client.get(reverse("academy_robots"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Allow: /")
        self.assertNotContains(response, "Sitemap:")

    @override_settings(TRADETHESIS_SEO_INDEXABLE=False)
    def test_staging_sitemap_is_not_available(self):
        response = self.client.get(reverse("academy_sitemap"))
        self.assertEqual(response.status_code, 404)

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_production_sitemap_contains_only_published_course_overviews(self):
        hidden = Course.objects.create(
            title="Internal Draft Course",
            slug="internal-draft-course",
            summary="A complete internal course that must remain undiscoverable.",
            status=Course.Status.PUBLISHED,
            catalogue_role=Course.CatalogueRole.HIDDEN,
        )
        hidden_module = CourseModule.objects.create(
            course=hidden,
            title="Internal module",
            slug="internal-module",
            is_published=True,
        )
        Lesson.objects.create(
            module=hidden_module,
            title="Internal lesson",
            slug="internal-lesson",
            is_published=True,
        )
        draft = Course.objects.create(
            title="Unpublished Course",
            slug="unpublished-course",
            status=Course.Status.DRAFT,
        )
        response = self.client.get(reverse("academy_sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/learn/course/support-and-resistance/")
        self.assertNotContains(response, hidden.slug)
        self.assertNotContains(response, draft.slug)

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_production_robots_advertises_the_sitemap(self):
        response = self.client.get(reverse("academy_robots"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sitemap: ")
        self.assertContains(response, "/sitemap.xml")


    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_course_detail_indexing_matches_public_catalogue_eligibility(self):
        public_response = self.client.get(
            reverse("academy:course-detail", args=[self.course.slug])
        )
        self.assertEqual(public_response.status_code, 200)
        public_html = public_response.content.decode("utf-8")
        self.assertIn('name="robots" content="index, follow"', public_html)
        self.assertIn('rel="canonical"', public_html)
        self.assertIn('"@type": "Course"', public_html)

        hidden = Course.objects.create(
            title="Internal Published Course",
            slug="internal-published-course",
            summary="A complete course reserved for internal use.",
            status=Course.Status.PUBLISHED,
            catalogue_role=Course.CatalogueRole.HIDDEN,
        )
        hidden_module = CourseModule.objects.create(
            course=hidden,
            title="Internal module",
            slug="internal-module",
            is_published=True,
        )
        Lesson.objects.create(
            module=hidden_module,
            title="Internal lesson",
            slug="internal-lesson",
            is_published=True,
        )
        hidden_response = self.client.get(
            reverse("academy:course-detail", args=[hidden.slug])
        )
        hidden_html = hidden_response.content.decode("utf-8")
        self.assertIn('name="robots" content="noindex, follow"', hidden_html)
        self.assertNotIn('rel="canonical"', hidden_html)
        self.assertNotIn('"@type": "Course"', hidden_html)

        incomplete = Course.objects.create(
            title="Published Course Without Lesson Content",
            slug="published-course-without-lesson-content",
            summary="A course that has not released any lesson content yet.",
            status=Course.Status.PUBLISHED,
        )
        incomplete_response = self.client.get(
            reverse("academy:course-detail", args=[incomplete.slug])
        )
        incomplete_html = incomplete_response.content.decode("utf-8")
        self.assertIn('name="robots" content="noindex, follow"', incomplete_html)
        self.assertNotIn('rel="canonical"', incomplete_html)
        self.assertNotIn('"@type": "Course"', incomplete_html)

        placeholder = Course.objects.create(
            title="New micro-course draft",
            slug="starter-copy-course",
            summary="Add a concise course promise here.",
            status=Course.Status.PUBLISHED,
        )
        placeholder_module = CourseModule.objects.create(
            course=placeholder,
            title="Starter module",
            slug="starter-module",
            is_published=True,
        )
        Lesson.objects.create(
            module=placeholder_module,
            title="Starter lesson",
            slug="starter-lesson",
            is_published=True,
        )
        placeholder_response = self.client.get(
            reverse("academy:course-detail", args=[placeholder.slug])
        )
        placeholder_html = placeholder_response.content.decode("utf-8")
        self.assertIn('name="robots" content="noindex, follow"', placeholder_html)
        self.assertNotIn('rel="canonical"', placeholder_html)
        self.assertNotIn('"@type": "Course"', placeholder_html)

    @override_settings(TRADETHESIS_SEO_INDEXABLE=False)
    def test_staging_course_detail_remains_noindex_without_canonical_or_schema(self):
        response = self.client.get(
            reverse("academy:course-detail", args=[self.course.slug])
        )
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn('name="robots" content="noindex, follow"', html)
        self.assertNotIn('rel="canonical"', html)
        self.assertNotIn('"@type": "Course"', html)
