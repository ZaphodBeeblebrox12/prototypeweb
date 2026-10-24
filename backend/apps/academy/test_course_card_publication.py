"""Regression coverage for publish eligibility and Option 4 course-card parity."""
import re
import uuid
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from .course_card_utils import (
    course_card_publication_issue,
    course_topic_tags,
    is_course_card_recommendable,
)
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

    def test_numbered_untitled_course_is_not_recommendable(self):
        issue = course_card_publication_issue(
            "Untitled course1",
            "A clear, practical description of what learners will study and why it matters.",
            "Explain who the course is for and what it covers.",
        )
        self.assertIn("starter course title", issue.lower())
        self.assertFalse(is_course_card_recommendable(
            "Untitled course1",
            "A clear, practical description of what learners will study and why it matters.",
            "Explain who the course is for and what it covers.",
        ))

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


    def test_related_course_topic_tags_reuse_compact_learning_outcome_labels(self):
        self.assertEqual(
            course_topic_tags([
                "Compare relative volume with price progress.",
                "Explain effort versus result.",
                "Identify failed breakouts.",
            ]),
            ["Relative volume vs price", "Effort versus result"],
        )
        self.assertEqual(
            course_topic_tags([
                "Compare relative volume with price progress.",
                "compare relative volume with price progress.",
                "",
                "Identify failed breakouts.",
            ]),
            ["Relative volume vs price", "Failed breakouts"],
        )
        self.assertEqual(course_topic_tags("not a list of outcomes"), [])

    def test_valid_course_card_reference_renders_option_three_not_a_lesson_link(self):
        from .content_rendering import render_safe_markdown

        course = Course.objects.create(
            title="Volume & Price Analysis",
            slug="volume-price-analysis-card-test",
            summary="Study how trading activity relates to the price result.",
            description="Compare volume, price progress and failed breakouts.",
            category="Technical analysis",
            learning_outcomes=[
                "Compare relative volume with price progress.",
                "Explain effort versus result.",
                "Identify failed breakouts.",
            ],
            status=Course.Status.PUBLISHED,
        )

        rendered = render_safe_markdown(
            "## Keep exploring\n\n[[course-card:" + str(course.pk) + "]]",
            admin_preview=True,
        )

        self.assertIn('class="tt-course-preview-card"', rendered)
        self.assertIn("Volume &amp; Price Analysis", rendered)
        self.assertIn("tt-course-preview-card__topics", rendered)
        self.assertIn("<span>Volume</span>", rendered)
        self.assertIn("<span>Price structure</span>", rendered)
        self.assertNotIn("Relative volume", rendered)
        self.assertNotIn("Failed breakouts", rendered)
        self.assertIn("View course outline", rendered)
        self.assertIn("/learn/course/volume-price-analysis-card-test/", rendered)
        self.assertNotIn("Course currently unavailable", rendered)

        lesson_link = render_safe_markdown("[[lesson:" + str(uuid.uuid4()) + "]]", admin_preview=True)
        self.assertNotIn("tt-course-preview-card", lesson_link)
        self.assertIn("Related lesson unavailable", lesson_link)



    def test_companion_course_uses_open_book_instead_of_title_initials(self):
        from .content_rendering import render_safe_markdown

        course = Course.objects.create(
            title="This is how a trade is actually added",
            slug="trade-added-open-book-card-test",
            summary="A practical guide to connecting the idea with the actual order.",
            category="Trading education",
            status=Course.Status.PUBLISHED,
        )
        rendered = render_safe_markdown(
            "[[course-card:" + str(course.pk) + "]]",
            admin_preview=True,
        )

        self.assertIn('class="tt-course-preview-card__mark-icon"', rendered)
        self.assertIn('viewBox="0 0 32 26"', rendered)
        self.assertIn('class="tt-course-preview-card__rings"', rendered)
        self.assertIn("Learn · in context", rendered)
        self.assertNotIn(">T/I</span>", rendered)

    def test_authored_svg_is_removed_but_companion_card_icon_is_preserved(self):
        from django.core.exceptions import ValidationError

        from .content_rendering import render_safe_markdown, validate_markdown_source

        authored_svg = '<svg class="authored-icon" viewBox="0 0 10 10"><path d="M0 0L10 10"></path></svg>'
        rendered_authored_svg = render_safe_markdown(authored_svg, admin_preview=True)
        self.assertNotIn("<svg", rendered_authored_svg.lower())
        self.assertNotIn("<path", rendered_authored_svg.lower())
        # Rendering sanitizes legacy/external content, but save/review validation
        # continues to reject the same active SVG before it can be stored.
        with self.assertRaises(ValidationError):
            validate_markdown_source(authored_svg)

        course = Course.objects.create(
            title="Companion card SVG safety test",
            slug="companion-card-svg-safety-test",
            summary="A practical guide to applying the concept.",
            category="Trading education",
            status=Course.Status.PUBLISHED,
        )
        rendered_card = render_safe_markdown(
            "[[course-card:" + str(course.pk) + "]]",
            admin_preview=True,
        )
        self.assertIn('class="tt-course-preview-card__mark-icon"', rendered_card)
        self.assertIn("<path", rendered_card.lower())

    def test_take_it_into_practice_content_is_preserved_in_practice_tab(self):
        from .content_rendering import build_lesson_sections

        source = "\n".join([
            "## Start with the decision",
            "",
            "Describe the visible evidence.",
            "",
            "### What to notice",
            "",
            "Separate observation from interpretation.",
            "",
            "### Compare the possibilities",
            "",
            "Compare two outcomes.",
            "",
            "### Take it into practice",
            "",
            "Write down what would strengthen your reading, what would weaken it, "
            "and what would make waiting the better decision.",
        ])
        sections = build_lesson_sections(source)

        self.assertNotIn("Take it into practice", sections["idea_html"])
        self.assertIn("Take it into practice", sections["practice_html"])
        self.assertIn("what would make waiting the better decision", sections["practice_html"])


class RelatedCourseSoftBotanicalParityTests(SimpleTestCase):
    def test_related_course_cards_use_soft_botanical_surfaces_and_topic_chips(self):
        root = Path(__file__).resolve().parents[2]
        styles = (root / "static" / "academy" / "learning-room.css").read_text(encoding="utf-8")
        learner = (root / "templates" / "academy" / "lesson.html").read_text(encoding="utf-8")
        staged_preview = (root / "templates" / "academy" / "course_import_website_preview.html").read_text(encoding="utf-8")

        self.assertIn("background: #edf3e8;", styles)
        self.assertIn(".tt-related-course-topics", styles)
        self.assertIn(".tt-related-course-topic", styles)
        self.assertIn('aria-label="Topics covered"', learner)
        self.assertIn('aria-label="Topics covered"', staged_preview)
        self.assertIn("{% for topic in related.topic_tags %}", learner)
        self.assertIn("{% for topic in related.topic_tags %}", staged_preview)


class OptionThreeCardParityTests(SimpleTestCase):
    def test_admin_website_preview_matches_builder_option_three_dimensions(self):
        root = Path(__file__).resolve().parents[2]
        admin_css = (root / "static" / "academy" / "course-import-preview.css").read_text(encoding="utf-8")

        self.assertIn(".tt-admin-learning-preview .tt-tab-panel .tt-course-preview-card {", admin_css)
        self.assertIn("width: min(72%, 640px);", admin_css)
        self.assertIn("max-width: 640px;", admin_css)
        self.assertIn("width: 100%; max-width: none;", admin_css)
        self.assertIn('font: 400 17px/1.12 Georgia, "Times New Roman", serif;', admin_css)
        self.assertIn("font-size: 9px;", admin_css)
        self.assertIn("-webkit-line-clamp: 2;", admin_css)

    def test_builder_and_learning_room_use_the_same_option_three_css(self):
        root = Path(__file__).resolve().parents[2]
        builder = (root / "apps" / "academy" / "course_builder_preview.html").read_text(encoding="utf-8")
        learner = (root / "static" / "academy" / "lesson-references.css").read_text(encoding="utf-8")
        comment = "/* Option 03 — compact course-cover split (shared by Builder, admin preview and learner lessons). */"
        builder_start = builder.index(comment)
        builder_end = builder.index("/* Compact layout for the catalogue selector in the lesson editor. */", builder_start)
        builder_css = builder[builder_start:builder_end].strip()
        learner_css = learner[learner.index(comment):].strip()
        def normalize(text):
            return re.sub(r"\s+", " ", text).strip()

        self.assertEqual(normalize(builder_css), normalize(learner_css))
        self.assertIn("grid-template-columns: 66px minmax(0, 1fr)", learner_css)
        self.assertIn("width: min(72%, 640px)", learner_css)
        self.assertIn("min-height: 104px", learner_css)
        self.assertIn(".tt-course-preview-card__rings::before", learner_css)
        self.assertIn(".tt-course-preview-card__rings::after", learner_css)
        self.assertIn("width: min(100%, 560px)", learner_css)
        self.assertIn("max-width: 560px", learner_css)
        self.assertIn("grid-template-columns: 60px minmax(0, 1fr)", learner_css)
        self.assertIn("grid-template-columns: 54px minmax(0, 1fr)", learner_css)
        self.assertIn("-webkit-line-clamp: 2;", learner_css)
        self.assertIn("tt-course-preview-card__topics", learner_css)
        self.assertIn("tt-course-preview-card__art", learner_css)
        self.assertIn("tt-course-preview-card__art--cover", learner_css)
        self.assertIn(".tt-course-preview-card__mark-icon", learner_css)
        self.assertIn(".tt-course-preview-card__rings", learner_css)
        self.assertIn("width: 27px", learner_css)
        self.assertNotIn("const markWords", builder)
        self.assertIn("tt-course-preview-card__mark-icon", builder)
        self.assertIn("BEHIND<br>THE MOVE", builder)
        self.assertIn("VOLUME × PRICE", builder)
        self.assertIn("View course outline", builder)
        self.assertIn(".map(topicLabel).filter(Boolean).slice(0, 2)", builder)
