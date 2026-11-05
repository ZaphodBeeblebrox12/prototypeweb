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


    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_topic_map_groups_shared_primary_topics_case_insensitively(self):
        self.course.seo_primary_topic = "  Support and Resistance Trading "
        self.course.save(update_fields=["seo_primary_topic"])
        second = Course.objects.create(
            title="Advanced Support and Resistance",
            slug="advanced-support-resistance",
            summary="Compare the strength and failure of important trading zones.",
            description="An advanced course about context and reactions around price zones.",
            status=Course.Status.DRAFT,
            seo_primary_topic="support  and resistance trading",
        )

        response = self.client.get(reverse("staff_admin_desk_seo"))
        self.assertEqual(response.status_code, 200)
        clusters = response.context["topic_clusters"]
        shared = [cluster for cluster in clusters if cluster["topic_overlap"]]
        self.assertEqual(len(shared), 1)
        self.assertEqual(shared[0]["course_count"], 2)
        self.assertContains(response, "Shared primary topic")
        self.assertContains(response, "Primary topic map")
        self.assertIn(
            second.slug,
            [row["course"].slug for row in shared[0]["courses"]],
        )

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_topic_overlap_filter_returns_only_courses_with_shared_topics(self):
        self.course.seo_primary_topic = "Support and resistance trading"
        self.course.save(update_fields=["seo_primary_topic"])
        Course.objects.create(
            title="Advanced Support and Resistance",
            slug="advanced-support-resistance",
            status=Course.Status.DRAFT,
            seo_primary_topic="support and resistance trading",
        )
        distinct = Course.objects.create(
            title="Bollinger Bands",
            slug="bollinger-bands",
            status=Course.Status.DRAFT,
            seo_primary_topic="Bollinger Bands trading strategy",
        )

        response = self.client.get(
            reverse("staff_admin_desk_seo"),
            {"filter": "topic-overlap"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(row["topic_overlap"] for row in response.context["rows"]))
        self.assertNotIn(
            distinct.slug,
            [row["course"].slug for row in response.context["rows"]],
        )
        self.assertEqual(len(response.context["rows"]), 2)


    def test_each_course_link_opens_the_matching_builder_course(self):
        other = Course.objects.create(
            title="Advanced Support and Resistance",
            slug="advanced-support-resistance",
            status=Course.Status.DRAFT,
        )

        response = self.client.get(reverse("staff_admin_desk_seo"))
        self.assertEqual(response.status_code, 200)
        urls = {
            row["course"].slug: row["builder_url"]
            for row in response.context["rows"]
        }
        expected_first = (
            f"{reverse('staff_course_builder_preview')}?open_course=support-and-resistance"
        )
        expected_second = (
            f"{reverse('staff_course_builder_preview')}?open_course=advanced-support-resistance"
        )
        self.assertEqual(urls[self.course.slug], expected_first)
        self.assertEqual(urls[other.slug], expected_second)
        self.assertContains(response, f'href="{expected_first}"')
        self.assertContains(response, f'href="{expected_second}"')

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_indexable_filter_returns_only_eligible_published_courses(self):
        draft = Course.objects.create(
            title="Bollinger Bands",
            slug="bollinger-bands",
            summary="Understand volatility and compare price behaviour around the bands.",
            status=Course.Status.DRAFT,
        )

        response = self.client.get(
            reverse("staff_admin_desk_seo"),
            {"filter": "indexable"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["course"].slug for row in response.context["rows"]],
            [self.course.slug],
        )
        self.assertNotIn(draft.slug, [row["course"].slug for row in response.context["rows"]])

    @override_settings(TRADETHESIS_SEO_INDEXABLE=True)
    def test_blocked_filter_returns_only_published_ineligible_courses(self):
        self.course.seo_indexable = False
        self.course.save(update_fields=["seo_indexable"])
        published_without_lessons = Course.objects.create(
            title="Unfinished Published Course",
            slug="unfinished-published-course",
            status=Course.Status.PUBLISHED,
        )
        draft = Course.objects.create(
            title="Draft Course",
            slug="draft-course",
            status=Course.Status.DRAFT,
        )

        response = self.client.get(
            reverse("staff_admin_desk_seo"),
            {"filter": "blocked"},
        )

        self.assertEqual(response.status_code, 200)
        result_slugs = [row["course"].slug for row in response.context["rows"]]
        self.assertIn(self.course.slug, result_slugs)
        self.assertIn(published_without_lessons.slug, result_slugs)
        self.assertNotIn(draft.slug, result_slugs)

    def test_search_matches_course_title_slug_and_primary_topic(self):
        self.course.seo_primary_topic = "Support and resistance trading"
        self.course.save(update_fields=["seo_primary_topic"])
        topic_course = Course.objects.create(
            title="Volatility study",
            slug="volatility-study",
            status=Course.Status.DRAFT,
            seo_primary_topic="Bollinger Bands trading",
        )
        slug_course = Course.objects.create(
            title="Market profile study",
            slug="market-profile-structure",
            status=Course.Status.DRAFT,
        )

        for query, expected_slug in (
            ("Support and Resistance", self.course.slug),
            ("Bollinger Bands", topic_course.slug),
            ("market-profile", slug_course.slug),
        ):
            with self.subTest(query=query):
                response = self.client.get(
                    reverse("staff_admin_desk_seo"),
                    {"q": query},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [row["course"].slug for row in response.context["rows"]],
                    [expected_slug],
                )

