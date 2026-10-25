"""Security and rendering tests for in-context lesson references."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .content_rendering import render_safe_markdown
from .models import Course, CourseImport, CourseModule, Lesson

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
            course=self.course,
            title="Volume context",
            slug="volume-context",
            position=1,
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Read relative volume",
            slug="read-relative-volume",
            summary="Compare activity with progress in price.",
            content_markdown="PRIVATE_DESTINATION_BODY",
            position=1,
            is_preview=True,
            is_published=True,
        )

    def test_inline_link_resolves_to_the_accessible_lesson(self):
        rendered = render_safe_markdown(
            f"See [[lesson:{self.lesson.pk}]] for the worked example.",
            user=self.user,
        )
        expected_url = reverse(
            "academy:lesson",
            args=[self.course.slug, self.lesson.pk],
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
            "academy:lesson",
            args=[self.course.slug, self.lesson.pk],
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


class CourseCardReferenceRenderingTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Volume and Price Analysis",
            slug="volume-price-analysis-card-test",
            summary="Read activity alongside price progress.",
            category="Volume analysis",
            level="Intermediate",
            estimated_duration="3 hours",
            learning_outcomes=[
                "Compare activity with price progress.",
                "Identify when volume does not confirm the move.",
            ],
            status=Course.Status.PUBLISHED,
        )

    def test_inline_course_card_uses_live_catalogue_fields_and_keeps_position(self):
        rendered = render_safe_markdown(
            "Before the card.\n\n[[course-card:" + str(self.course.pk) + "]]\n\nAfter the card."
        )
        expected_url = reverse("academy:course-detail", args=[self.course.slug])
        card_index = rendered.index('class="tt-course-preview-card"')
        self.assertLess(rendered.index("Before the card."), card_index)
        self.assertLess(card_index, rendered.index("After the card."))
        self.assertIn(self.course.title, rendered)
        self.assertIn(self.course.summary, rendered)
        self.assertIn("Companion course", rendered)
        self.assertIn("<span>Volume</span>", rendered)
        self.assertIn("<span>Price structure</span>", rendered)
        self.assertIn("BEHIND<br>THE MOVE", rendered)
        self.assertIn("VOLUME × PRICE", rendered)
        self.assertIn("tt-course-preview-card__topics", rendered)
        self.assertIn("View course outline", rendered)
        self.assertIn(f'href="{expected_url}"', rendered)

    def test_published_placeholder_course_is_not_rendered_as_a_recommendation(self):
        self.course.title = "New micro-course draft"
        self.course.summary = "Add a concise course promise here."
        self.course.save(update_fields=["title", "summary"])
        rendered = render_safe_markdown("[[course-card:" + str(self.course.pk) + "]]")
        self.assertIn("Course currently unavailable", rendered)
        self.assertNotIn("New micro-course draft", rendered)
        self.assertNotIn("Add a concise course promise here.", rendered)

    def test_course_card_does_not_expose_a_draft_course(self):
        self.course.status = Course.Status.DRAFT
        self.course.save(update_fields=["status"])
        rendered = render_safe_markdown("[[course-card:" + str(self.course.pk) + "]]")
        self.assertIn("Course currently unavailable", rendered)
        self.assertNotIn(self.course.title, rendered)
        self.assertNotIn(self.course.summary, rendered)

    def test_explicitly_announced_coming_soon_card_uses_builder_catalogue_fields(self):
        teaser = CourseImport.objects.create(
            course_slug="order-flow-volume-coming-soon",
            title="Order Flow and Volume",
            content_hash="a" * 64,
            source_manifest="{}",
            payload={
                "builder_state": {
                    "comingSoon": True,
                    "title": "Order Flow and Volume",
                    "summary": "Understand activity in context.",
                    "category": "Volume analysis",
                    "level": "Intermediate",
                    "duration": "2 hours",
                    "outcomes": ["Compare volume with price progress."],
                }
            },
            status=CourseImport.Status.DRAFT,
        )
        rendered = render_safe_markdown("[[course-card:coming-soon:" + str(teaser.pk) + "]]")
        self.assertIn(
            'class="tt-course-preview-card tt-course-preview-card--coming-soon"', rendered
        )
        self.assertIn("Order Flow and Volume", rendered)
        self.assertIn("Understand activity in context.", rendered)
        self.assertIn("Volume vs price", rendered)
        self.assertIn("Coming soon", rendered)
        self.assertNotIn("course-detail", rendered)

    def test_private_builder_draft_is_not_exposed_as_a_course_card(self):
        teaser = CourseImport.objects.create(
            course_slug="private-draft-card-test",
            title="Private draft course title",
            content_hash="b" * 64,
            source_manifest="{}",
            payload={
                "builder_state": {
                    "comingSoon": False,
                    "title": "Private draft course title",
                    "summary": "Private draft summary.",
                }
            },
            status=CourseImport.Status.DRAFT,
        )
        rendered = render_safe_markdown("[[course-card:coming-soon:" + str(teaser.pk) + "]]")
        self.assertIn("Course currently unavailable", rendered)
        self.assertNotIn("Private draft course title", rendered)
        self.assertNotIn("Private draft summary.", rendered)

    def test_coming_soon_reference_automatically_uses_live_course_after_publication(self):
        teaser = CourseImport.objects.create(
            course_slug=self.course.slug,
            title="Old teaser title",
            content_hash="c" * 64,
            source_manifest="{}",
            payload={"builder_state": {"comingSoon": True, "title": "Old teaser title"}},
            status=CourseImport.Status.PUBLISHED,
            target_course=self.course,
        )
        rendered = render_safe_markdown("[[course-card:coming-soon:" + str(teaser.pk) + "]]")
        expected_url = reverse("academy:course-detail", args=[self.course.slug])
        self.assertIn(self.course.title, rendered)
        self.assertIn(f'href="{expected_url}"', rendered)
        self.assertNotIn("Old teaser title", rendered)

    def test_course_card_escapes_catalogue_copy(self):
        self.course.title = '<script>alert("x")</script>'
        self.course.summary = '<img src=x onerror="alert(1)">'
        self.course.save(update_fields=["title", "summary"])
        rendered = render_safe_markdown("[[course-card:" + str(self.course.pk) + "]]")
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<img src=x onerror=", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img src=x onerror=", rendered)
