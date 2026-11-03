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
            status=Course.Status.PUBLISHED,
            catalogue_role=Course.CatalogueRole.HIDDEN,
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
