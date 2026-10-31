"""Contract tests keeping public Trading Path offers aligned with Academy data."""

from pathlib import Path

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Course, CourseModule, Lesson


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class PublicTradingPathCommerceContractTests(TestCase):
    def test_free_trading_path_is_published_to_the_public_catalogue_as_free(self):
        course = Course.objects.create(
            title="The TradeThesis Trading Path",
            slug="trading-path",
            summary=(
                "A structured course connecting market mechanics, chart reading, "
                "trade planning, risk management and review."
            ),
            description=(
                "Learn to observe price, build a thesis, define invalidation, "
                "manage exposure and review trading decisions."
            ),
            status=Course.Status.PUBLISHED,
            access_type=Course.AccessType.FREE,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="How markets work",
            slug="how-markets-work",
            position=1,
            content_markdown="Private lesson body.",
            is_published=True,
        )

        response = self.client.get(reverse("academy_public_catalogue"))
        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.json()["courses"] if item["slug"] == "trading-path")

        self.assertEqual(row["accessType"], Course.AccessType.FREE)
        self.assertTrue(row["isFree"])
        self.assertEqual(row["price"], "Free")
        self.assertIn("no payment required", row["priceNote"].lower())
        self.assertTrue(row["academyUrl"].endswith("/learn/course/trading-path/"))
        self.assertNotIn("Private lesson body.", response.content.decode("utf-8"))
        self.assertEqual(response["Cache-Control"], "private, no-store")


class PublicTradingPathStaticContractTests(SimpleTestCase):
    def test_homepage_and_course_page_use_academy_backed_commerce_fields(self):
        homepage = (REPOSITORY_ROOT / "site" / "index.html").read_text(encoding="utf-8")
        course_page = (REPOSITORY_ROOT / "site" / "trading-path.html").read_text(encoding="utf-8")
        commerce_script = (
            REPOSITORY_ROOT / "site" / "assets" / "course-commerce.js"
        ).read_text(encoding="utf-8")

        self.assertNotIn("₹999", homepage)
        self.assertIn('data-course-commerce="trading-path"', homepage)
        self.assertIn("data-course-price", homepage)
        self.assertIn("data-course-access-message", homepage)
        self.assertIn("assets/course-commerce.js", homepage)

        self.assertNotIn(">Free</strong>", course_page)
        self.assertNotIn("Enrol for free to access", course_page)
        self.assertIn('data-course-commerce="trading-path"', course_page)
        self.assertIn("data-course-enrol-cta", course_page)
        self.assertIn("assets/course-commerce.js", course_page)

        self.assertIn("/api/academy/catalogue/", commerce_script)
        self.assertIn("credentials: \"omit\"", commerce_script)
        self.assertIn("Temporarily unavailable", commerce_script)
        self.assertIn("course.price", commerce_script)
