from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.academy.models import Course, CourseModule, Lesson

User = get_user_model()


class AcademySeoDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="seo-admin",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)
        self.course = Course.objects.create(
            title="Support and Resistance",
            slug="support-and-resistance",
            summary="Learn to mark meaningful price zones and assess reactions.",
            description="A practical course about reading price behaviour around important zones.",
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
    def test_dashboard_explains_staging_noindex_and_course_indexability(self):
        response = self.client.get(reverse("staff_admin_desk_seo"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Site-wide indexing: disabled")
        self.assertContains(response, "Published courses")
        self.assertContains(response, "Eligible for indexing now")
        self.assertContains(response, "Site-wide indexing is disabled for this deployment.")
        self.assertContains(response, "Support and Resistance")

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_dashboard_shows_course_as_indexable_when_sitemap_rules_are_met(self):
        self.course.seo_title = "Support and Resistance Trading Course | TradeThesis"
        self.course.seo_description = "Learn to mark meaningful price zones, compare reactions and define invalidation in a structured way."
        self.course.seo_primary_topic = "Support and resistance trading"
        self.course.save(update_fields=["seo_title", "seo_description", "seo_primary_topic"])
        response = self.client.get(reverse("staff_admin_desk_seo"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eligible")
        self.assertNotContains(response, "Site-wide indexing is disabled for this deployment.")

    def test_dashboard_requires_course_content_admin(self):
        learner = User.objects.create_user(
            username="seo-learner",
            password="test-password",
            role="user",
        )
        self.client.force_login(learner)
        response = self.client.get(reverse("staff_admin_desk_seo"))
        self.assertEqual(response.status_code, 403)

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_attention_filter_returns_metadata_gaps_and_duplicate_titles(self):
        incomplete = Course.objects.create(
            title="Support and Resistance",
            slug="support-and-resistance-revisited",
            status=Course.Status.DRAFT,
        )
        response = self.client.get(
            reverse("staff_admin_desk_seo"),
            {"filter": "attention"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Duplicate search title")
        self.assertContains(response, "No search description")
        self.assertContains(response, incomplete.slug)
