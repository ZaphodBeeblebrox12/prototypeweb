import json
import re
from datetime import timedelta
from io import BytesIO
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.academy.models import (
    Course,
    CourseEntitlement,
    CourseImport,
    CourseMediaAsset,
    CourseModule,
    Lesson,
    LessonInstructorMaterial,
    LessonProgress,
)
from apps.academy.storage import course_asset_storage

User = get_user_model()


class AcademyViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="Test-password-123!")
        self.course = Course.objects.create(
            title="Trading Path", slug="trading-path", status=Course.Status.PUBLISHED,
            summary="Learn to read the screen.",
        )
        self.module = CourseModule.objects.create(
            course=self.course, title="Foundations", slug="foundations",
            position=1, is_published=True,
        )
        self.paid_lesson = Lesson.objects.create(
            module=self.module, title="Private lesson", slug="private-lesson",
            position=1, is_published=True, content_markdown="SECRET PAID LESSON BODY",
        )
        self.preview_lesson = Lesson.objects.create(
            module=self.module, title="Preview lesson", slug="preview-lesson",
            position=2, is_published=True, is_preview=True,
            content_markdown="Public preview content.",
        )
        self.client.force_login(self.user)

    def test_course_overview_does_not_include_paid_lesson_body(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Private lesson")
        self.assertNotContains(response, "SECRET PAID LESSON BODY")

    def test_course_overview_renders_markdown_description_as_heading_and_list(self):
        self.course.description = (
            "### What learners will practise\n\n"
            "- Describe the evidence before interpreting it.\n"
            "- Compare alternatives and identify invalidation.\n"
            "- Build a clear, conditional decision process."
        )
        self.course.save(update_fields=["description", "updated_at"])

        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h3>What learners will practise</h3>")
        self.assertContains(response, "<ul>")
        self.assertContains(response, "<li>Describe the evidence before interpreting it.</li>")
        self.assertNotContains(response, "### What learners will practise")
        self.assertNotContains(response, "- Describe the evidence before interpreting it.")

    def test_course_overview_uses_content_rich_layout_and_live_course_counts(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="tt-course-overview"')
        self.assertContains(response, 'class="tt-overview-hero"')
        self.assertContains(response, 'class="tt-overview-curriculum-grid"')
        self.assertContains(response, 'academy/course-overview.css')
        self.assertEqual(response.context["total_modules"], 1)
        self.assertEqual(response.context["total_lessons"], 2)
        self.assertEqual(response.context["total_study_minutes"], 20)
        self.assertEqual(response.context["first_accessible_lesson"], self.preview_lesson)

    def test_course_overview_keeps_checkout_unavailable_note_without_bootstrap_alert(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enrolment is not available right now")
        self.assertNotContains(response, 'class="alert alert-info"')

    def test_admin_can_preview_locked_lesson_without_creating_progress(self):
        admin = User.objects.create_user(
            username="course-content-admin",
            password="Test-password-123!",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(admin)

        overview = self.client.get(
            reverse("academy:course-detail", args=[self.course.slug])
        )
        self.assertEqual(overview.status_code, 200)
        preview_url = reverse(
            "academy:admin-lesson-preview",
            args=[self.course.slug, self.paid_lesson.pk],
        )
        self.assertContains(overview, preview_url)
        self.assertContains(overview, "Admin preview")

        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "ADMIN PREVIEW")
        self.assertContains(response, "LOCKED ACCESS BYPASSED FOR REVIEW ONLY")
        self.assertContains(response, "SECRET PAID LESSON BODY")
        self.assertContains(response, "Course outline")
        self.assertNotContains(response, "Mark complete")
        self.assertNotContains(response, "Save reflection")
        self.assertNotContains(response, "Check answers")
        self.assertFalse(
            LessonProgress.objects.filter(user=admin, lesson=self.paid_lesson).exists()
        )

    def test_regional_audience_preview_uses_saved_blocks_in_learning_room(self):
        admin = User.objects.create_user(
            username="regional-preview-admin",
            password="Test-password-123!",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(admin)
        record = CourseImport.objects.create(
            course_slug="regional-preview-course",
            title="Regional preview course",
            manifest_version="1.0",
            content_hash="b" * 64,
            source_manifest="{}",
            payload={
                "course": {
                    "title": "Regional preview course",
                    "slug": "regional-preview-course",
                    "summary": "A saved draft for audience preview tests.",
                    "description": "Preview each authored version in the Learning Room.",
                },
                "modules": [{
                    "title": "Foundations",
                    "slug": "foundations",
                    "position": 1,
                    "lessons": [{
                        "source_id": "1.1",
                        "title": "Audience-specific disclosure",
                        "slug": "audience-specific-disclosure",
                        "position": 1,
                        "duration_minutes": 5,
                        "content_markdown": (
                            "### The question\n\nObserve first.\n\n"
                            "[[regional-block:risk-note]]"
                        ),
                        "content_json": {
                            "regional_blocks": {
                                "risk-note": {
                                    "id": "risk-note",
                                    "title": "Country disclosure",
                                    "base_content": "Global disclosure.",
                                    "variants": [
                                        {
                                            "scope": "country", "code": "IN",
                                            "content": "India-specific disclosure.",
                                            "hidden": False,
                                        },
                                        {
                                            "scope": "region", "code": "APAC",
                                            "content": "APAC-specific disclosure.",
                                            "hidden": False,
                                        },
                                        {
                                            "scope": "country", "code": "US",
                                            "content": "US-only hidden disclosure.",
                                            "hidden": True,
                                        },
                                    ],
                                },
                            },
                        },
                    }, {
                        "source_id": "1.2",
                        "title": "Navigation target lesson",
                        "slug": "navigation-target-lesson",
                        "position": 2,
                        "duration_minutes": 5,
                        "content_markdown": "### Keep the selected audience\n\nThe preview should preserve its audience here too.",
                        "content_json": {},
                    }],
                }],
            },
        )
        preview_url = reverse("academy:course-import-preview", args=[record.pk])
        cases = [
            (
                {"lesson": "1.1", "preview_audience": "IN"},
                "India-specific disclosure.",
                ("APAC-specific disclosure.", "Global disclosure.", "US-only hidden disclosure."),
            ),
            (
                {"lesson": "1.1", "preview_audience": "REGION:APAC"},
                "APAC-specific disclosure.",
                ("India-specific disclosure.", "Global disclosure.", "US-only hidden disclosure."),
            ),
            (
                {"lesson": "1.1"},
                "Global disclosure.",
                ("India-specific disclosure.", "APAC-specific disclosure.", "US-only hidden disclosure."),
            ),
            (
                {"lesson": "1.1", "preview_audience": "US"},
                None,
                (
                    "India-specific disclosure.",
                    "APAC-specific disclosure.",
                    "Global disclosure.",
                    "US-only hidden disclosure.",
                ),
            ),
        ]
        for params, expected, absent in cases:
            with self.subTest(audience=params.get("preview_audience", "GLOBAL")):
                response = self.client.get(preview_url, params)
                self.assertEqual(response.status_code, 200, response.content)
                if expected:
                    self.assertContains(response, expected)
                for phrase in absent:
                    self.assertNotContains(response, phrase)

                next_lesson_url = response.context["preview_modules"][0]["lessons"][1]["preview_url"]
                next_query = parse_qs(urlparse(next_lesson_url).query)
                self.assertEqual(next_query.get("lesson"), ["1.2"])
                if params.get("preview_audience"):
                    self.assertEqual(next_query.get("preview_audience"), [params["preview_audience"]])
                else:
                    self.assertNotIn("preview_audience", next_query)

    def test_staged_course_preview_displays_structured_questions_read_only(self):
        admin = User.objects.create_user(
            username="preview-content-admin",
            password="Test-password-123!",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(admin)
        record = CourseImport.objects.create(
            course_slug="preview-course",
            title="Preview course",
            manifest_version="1.0",
            content_hash="a" * 64,
            source_manifest="{}",
            payload={
                "course": {
                    "title": "Preview course",
                    "slug": "preview-course",
                    "summary": "A course used to test the website preview.",
                    "description": (
                        "### What learners will practise\n\n"
                        "- Describe the evidence before interpreting it.\n"
                        "- Compare alternatives and identify invalidation.\n"
                        "- Build a clear, conditional decision process."
                    ),
                    "learning_outcomes": ["Use a conditional checklist before considering a trade."],
                },
                "modules": [{
                    "title": "Foundations",
                    "slug": "foundations",
                    "position": 1,
                    "summary": "Start with the evidence.",
                    "lessons": [{
                        "source_id": "1.1",
                        "title": "Read the evidence",
                        "slug": "read-the-evidence",
                        "position": 1,
                        "duration_minutes": 12,
                        "summary": "A structured preview lesson.",
                        "content_markdown": (
                            "### The question\n\n"
                            "Start by describing what is visible."
                        ),
                        "content_json": {
                            "questions": [{
                                "id": "q1",
                                "prompt": "How should the observation be used?",
                                "options": [
                                    "As evidence to assess in context",
                                    "As an automatic signal",
                                ],
                            }],
                            "notebook": {
                                "title": "Your Trading Notebook",
                                "prompts": [{
                                    "label": "Observe",
                                    "text": "Record the evidence you can see.",
                                }],
                            },
                        },
                    }],
                }],
            },
        )

        response = self.client.get(
            reverse("academy:course-import-preview", args=[record.pk]),
            {"lesson": "1.1"},
        )

        overview_response = self.client.get(reverse("academy:course-import-preview", args=[record.pk]))
        self.assertEqual(overview_response.status_code, 200, overview_response.content)
        self.assertContains(overview_response, "<h3>What learners will practise</h3>")
        self.assertContains(overview_response, "<ul>")
        self.assertContains(overview_response, "<li>Describe the evidence before interpreting it.</li>")
        self.assertNotContains(overview_response, "### What learners will practise")
        self.assertNotContains(overview_response, "- Describe the evidence before interpreting it.")
        self.assertContains(overview_response, "Use a conditional checklist before considering a trade.")
        self.assertContains(overview_response, 'class="tt-overview-outcome-grid"')

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "How should the observation be used?")
        self.assertContains(response, "As evidence to assess in context")
        self.assertContains(
            response,
            "Administrator preview only. Answer submission is disabled in this view.",
        )
        self.assertContains(response, '<fieldset class="tt-question tt-admin-question" disabled>')
        self.assertContains(response, "Record the evidence you can see.")
        self.assertNotContains(response, "Check answers")
        self.assertNotContains(response, "Save reflection")

    def test_locked_lesson_preview_is_for_course_content_admins_only(self):
        response = self.client.get(
            reverse("academy:admin-lesson-preview", args=[self.course.slug, self.paid_lesson.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "SECRET PAID LESSON BODY", status_code=403)

    def test_paid_lesson_is_not_retrievable_without_entitlement(self):
        response = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "SECRET PAID LESSON BODY", status_code=403)

    def test_published_preview_lesson_can_be_opened(self):
        response = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public preview content.")

    def test_related_courses_panel_adapts_to_one_two_or_three_courses(self):
        courses = [
            Course.objects.create(
                title=f"Related course {index}",
                slug=f"related-course-count-{index}",
                summary=f"Practise skill {index} in context.",
                position=10 + index,
                status=Course.Status.PUBLISHED,
            )
            for index in range(1, 4)
        ]
        self.preview_lesson.content_json = {}
        for count in (1, 2, 3):
            with self.subTest(course_count=count):
                self.preview_lesson.content_json = {
                    "related_course_ids": [str(course.pk) for course in courses[:count]],
                }
                self.preview_lesson.save(update_fields=["content_json", "updated_at"])
                response = self.client.get(
                    reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertContains(response, f'data-course-count="{count}"')
                self.assertEqual(
                    response.content.decode().count('class="tt-related-course-link tt-related-course-card"'),
                    count,
                )
                self.assertContains(response, "Explore course")
                self.assertContains(response, "Course references do not grant access or include a purchase.")

    def test_related_courses_use_bright_course_cards_in_branded_panel(self):
        related_courses = [
            Course.objects.create(
                title="Support and Resistance",
                slug="related-support-resistance",
                summary="Identify price zones and assess reactions.",
                position=3,
                status=Course.Status.PUBLISHED,
            ),
            Course.objects.create(
                title="Volume and Price Analysis",
                slug="related-volume-price",
                summary="Read activity alongside price progress.",
                position=4,
                status=Course.Status.PUBLISHED,
            ),
            Course.objects.create(
                title="Build and Manage a Trade",
                slug="related-trade-management",
                summary="Construct a plan and manage risk through exit.",
                position=5,
                status=Course.Status.PUBLISHED,
            ),
        ]
        self.preview_lesson.content_json = {
            "related_course_ids": [str(course.pk) for course in related_courses],
        }
        self.preview_lesson.save(update_fields=["content_json", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'class="tt-related-courses tt-related-courses--cards"')
        self.assertContains(response, 'class="tt-related-courses-kicker">Continue learning</p>')
        self.assertContains(response, 'id="tt-related-courses-heading">Build on this lesson</h2>')
        self.assertEqual(response.content.decode().count('class="tt-related-course-link tt-related-course-card"'), 3)
        self.assertEqual(response.content.decode().count('class="tt-related-course-card-cta"'), 3)
        self.assertContains(response, 'data-course-count="3"')
        for index, course in enumerate(related_courses, start=1):
            self.assertContains(response, f'href="{reverse("academy:course-detail", args=[course.slug])}"')
            self.assertContains(response, f"{index:02d}")
            self.assertContains(response, course.title)
            self.assertContains(response, course.summary)
        self.assertContains(response, "Course references do not grant access or include a purchase.")

    def test_quiz_submit_returns_indices_for_red_green_feedback_after_submission(self):
        self.preview_lesson.content_json = {
            "questions": [{
                "id": "question-1",
                "prompt": "What does the chart show?",
                "options": ["Breakout", "Rejection"],
            }],
        }
        self.preview_lesson.save(update_fields=["content_json", "updated_at"])
        LessonInstructorMaterial.objects.create(
            lesson=self.preview_lesson,
            rubric_json={"questions": [{
                "id": "question-1",
                "options": ["Breakout", "Rejection"],
                "correctIndex": 1,
                "explanation": "The repeated rejection is the key evidence.",
            }]},
        )

        page = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'data-question-option="question-1"')
        self.assertNotContains(page, '"correct_index": 1')
        self.assertNotContains(page, '"selected_index": 0')
        self.assertNotContains(page, "The repeated rejection is the key evidence.")

        response = self.client.post(
            reverse("academy:lesson-quiz-submit", args=[self.preview_lesson.pk]),
            data=json.dumps({"answers": {"question-1": 0}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        result = response.json()["results"][0]
        self.assertFalse(result["correct"])
        self.assertEqual(result["selected_index"], 0)
        self.assertEqual(result["correct_index"], 1)
        self.assertIn("The repeated rejection is the key evidence.", result["explanation"])

    def test_published_preview_renders_multiple_images_in_selected_learning_room_tabs(self):
        placements = [
            ("Idea figure", "Additional concept figure", "idea", "https://example.com/idea.png"),
            ("Example chart", "Additional chart examples", "examples", "https://example.com/examples.png"),
            ("Practice figure", "Practice figure", "practice", "https://example.com/practice.png"),
        ]
        assets = []
        markdown_parts = ["### The question", "", "Look at the evidence in each panel."]
        for index, (alt_text, heading, _tab, url) in enumerate(placements, start=1):
            asset = CourseMediaAsset.objects.create(
                course=self.course,
                asset_key=f"test/learning-room-figure-{index}",
                alt_text=alt_text,
                original_url=url,
            )
            assets.append(asset)
            markdown_parts.extend([
                "",
                f"### {heading}",
                "",
                f"![{alt_text}](asset://{asset.pk})",
            ])
        self.preview_lesson.content_markdown = "\n".join(markdown_parts)
        self.preview_lesson.content_json = {"asset_ids": [str(asset.pk) for asset in assets]}
        self.preview_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        rendered_html = response.content.decode()
        panel_patterns = {
            tab: re.compile(
                rf'<div class="tt-tab-panel"[^>]*data-tab-panel="{tab}"[^>]*>(.*?)</div>',
                re.DOTALL,
            )
            for tab in ("idea", "examples", "practice")
        }
        panels = {}
        for tab, pattern in panel_patterns.items():
            match = pattern.search(rendered_html)
            self.assertIsNotNone(match, f"Published lesson is missing the {tab} tab panel.")
            panels[tab] = match.group(1)

        self.assertIn('<span class="tt-tab-count">3</span>', rendered_html)
        for alt_text, _heading, expected_tab, url in placements:
            self.assertIn(f'alt="{alt_text}"', panels[expected_tab])
            self.assertIn(f'src="{url}"', panels[expected_tab])
            for other_tab, panel_html in panels.items():
                if other_tab != expected_tab:
                    self.assertNotIn(url, panel_html)

    def test_uploaded_replacement_renders_through_protected_media_and_retains_source_url(self):
        source_url = "https://example.com/charts/original.png"
        image_bytes = BytesIO()
        Image.new("RGB", (12, 8), (245, 220, 170)).save(image_bytes, format="PNG")
        asset = CourseMediaAsset.objects.create(
            course=self.course,
            asset_key="test/uploaded-replacement",
            alt_text="Uploaded replacement chart",
            original_url=source_url,
        )
        asset.file.save(
            "replacement.png",
            SimpleUploadedFile("replacement.png", image_bytes.getvalue(), content_type="image/png"),
            save=True,
        )
        stored_name = asset.file.name
        self.addCleanup(lambda: course_asset_storage.delete(stored_name))

        self.preview_lesson.content_markdown = f"![Uploaded replacement chart](asset://{asset.pk})"
        self.preview_lesson.content_json = {"asset_ids": [str(asset.pk)]}
        self.preview_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        protected_url = reverse("academy:media-asset", args=[asset.pk])
        self.assertContains(response, f'src="{protected_url}"')
        self.assertNotContains(response, source_url)

        media_response = self.client.get(protected_url)
        self.assertEqual(media_response.status_code, 200)
        self.assertEqual(media_response["Content-Type"], "image/png")
        self.assertEqual(media_response["Cache-Control"], "private, no-store")
        self.assertEqual(media_response["X-Content-Type-Options"], "nosniff")

    def test_regional_media_urls_only_allow_assets_selected_for_the_actual_country(self):
        def make_asset(asset_key, filename, label):
            image_bytes = BytesIO()
            Image.new("RGB", (12, 8), (245, 220, 170)).save(image_bytes, format="PNG")
            asset = CourseMediaAsset.objects.create(
                course=self.course, asset_key=asset_key, alt_text=label,
            )
            asset.file.save(
                filename,
                SimpleUploadedFile(filename, image_bytes.getvalue(), content_type="image/png"),
                save=True,
            )
            stored_name = asset.file.name
            self.addCleanup(lambda storage=course_asset_storage, name=stored_name: storage.delete(name))
            return asset

        base_asset = make_asset("test/regional-base", "regional-base.png", "Global image")
        india_asset = make_asset("test/regional-india", "regional-india.png", "India image")
        us_asset = make_asset("test/regional-us", "regional-us.png", "US image")
        hidden_asset = make_asset("test/regional-hidden", "regional-hidden.png", "Hidden image")
        self.preview_lesson.content_markdown = "## Regional notice\n\n[[regional-block:notice]]"
        self.preview_lesson.content_json = {
            "asset_ids": [str(base_asset.pk), str(india_asset.pk), str(us_asset.pk), str(hidden_asset.pk)],
            "regional_blocks": {
                "notice": {
                    "base_content": f"![Global image](asset://{base_asset.pk})",
                    "variants": [
                        {"scope": "country", "code": "IN", "content": f"![India image](asset://{india_asset.pk})", "hidden": False},
                        {"scope": "country", "code": "US", "content": f"![US image](asset://{us_asset.pk})", "hidden": False},
                        {"scope": "country", "code": "CA", "content": f"![Hidden image](asset://{hidden_asset.pk})", "hidden": True},
                    ],
                },
            },
        }
        self.preview_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])
        base_url = reverse("academy:media-asset", args=[base_asset.pk])
        india_url = reverse("academy:media-asset", args=[india_asset.pk])
        us_url = reverse("academy:media-asset", args=[us_asset.pk])
        hidden_url = reverse("academy:media-asset", args=[hidden_asset.pk])

        # An unmapped audience uses base content; it cannot retrieve either override.
        self.assertEqual(self.client.get(base_url, HTTP_CF_IPCOUNTRY="ZZ").status_code, 200)
        self.assertEqual(self.client.get(india_url, HTTP_CF_IPCOUNTRY="ZZ").status_code, 403)
        self.assertEqual(self.client.get(us_url, HTTP_CF_IPCOUNTRY="ZZ").status_code, 403)

        # Actual requester geography selects India; hidden overrides never expose images.
        self.assertEqual(self.client.get(india_url, HTTP_CF_IPCOUNTRY="IN").status_code, 200)
        self.assertEqual(self.client.get(us_url, HTTP_CF_IPCOUNTRY="IN").status_code, 403)
        self.assertEqual(self.client.get(hidden_url, HTTP_CF_IPCOUNTRY="CA").status_code, 403)

        # Pricing's debug-only test_country override must never change regional media permissions.
        with self.settings(DEBUG=True):
            self.assertEqual(
                self.client.get(india_url, {"test_country": "US"}, HTTP_CF_IPCOUNTRY="IN").status_code,
                200,
            )
            self.assertEqual(
                self.client.get(us_url, {"test_country": "US"}, HTTP_CF_IPCOUNTRY="IN").status_code,
                403,
            )

    def test_uploaded_media_for_unentitled_paid_lesson_is_forbidden(self):
        image_bytes = BytesIO()
        Image.new("RGB", (12, 8), (245, 220, 170)).save(image_bytes, format="PNG")
        asset = CourseMediaAsset.objects.create(
            course=self.course,
            asset_key="test/private-paid-image",
            alt_text="Private lesson chart",
            original_url="https://example.com/charts/private-original.png",
        )
        asset.file.save(
            "private-chart.png",
            SimpleUploadedFile("private-chart.png", image_bytes.getvalue(), content_type="image/png"),
            save=True,
        )
        stored_name = asset.file.name
        self.addCleanup(lambda: course_asset_storage.delete(stored_name))
        self.paid_lesson.content_markdown = f"![Private lesson chart](asset://{asset.pk})"
        self.paid_lesson.content_json = {"asset_ids": [str(asset.pk)]}
        self.paid_lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

        response = self.client.get(reverse("academy:media-asset", args=[asset.pk]))
        self.assertEqual(response.status_code, 403)

    def test_progress_endpoint_rejects_unentitled_paid_lesson(self):
        response = self.client.post(
            reverse("academy:lesson-progress", args=[self.paid_lesson.pk]),
            {"status": "completed"},
        )
        self.assertEqual(response.status_code, 403)


    def test_opening_accessible_lesson_saves_an_in_progress_resume_point(self):
        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.preview_lesson)
        self.assertEqual(progress.status, LessonProgress.Status.IN_PROGRESS)
        self.assertIsNotNone(progress.started_at)
        self.assertIsNotNone(progress.last_seen_at)

    def test_completed_lesson_remains_completed_when_reopened(self):
        self.client.post(
            reverse("academy:lesson-progress", args=[self.preview_lesson.pk]),
            {"status": LessonProgress.Status.COMPLETED},
        )
        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.preview_lesson)
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)
        self.assertIsNotNone(progress.completed_at)

    def test_progress_status_cannot_regress_from_completed(self):
        endpoint = reverse("academy:lesson-progress", args=[self.preview_lesson.pk])
        completed = self.client.post(endpoint, {"status": LessonProgress.Status.COMPLETED})
        self.assertEqual(completed.status_code, 200)
        for status in (LessonProgress.Status.IN_PROGRESS, LessonProgress.Status.NOT_STARTED):
            response = self.client.post(endpoint, {"status": status})
            self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.preview_lesson)
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)

    def test_progress_endpoint_is_post_only(self):
        response = self.client.get(
            reverse("academy:lesson-progress", args=[self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_expired_entitlement_does_not_open_paid_lesson(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=now - timedelta(days=3),
            expires_at=now - timedelta(days=1),
        )
        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        )
        self.assertEqual(response.status_code, 403)


    def test_unpublished_lesson_and_module_cannot_be_opened_directly(self):
        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])

        self.paid_lesson.is_published = False
        self.paid_lesson.save(update_fields=["is_published", "updated_at"])
        self.assertEqual(self.client.get(lesson_url).status_code, 404)

        self.paid_lesson.is_published = True
        self.paid_lesson.save(update_fields=["is_published", "updated_at"])
        self.module.is_published = False
        self.module.save(update_fields=["is_published", "updated_at"])
        self.assertEqual(self.client.get(lesson_url).status_code, 404)

    def test_draft_course_does_not_expose_even_a_preview_lesson(self):
        self.course.status = Course.Status.DRAFT
        self.course.save(update_fields=["status", "updated_at"])

        response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "Public preview content.", status_code=403)

    def test_revoked_entitlement_denies_lesson_and_progress_endpoint(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.REVOKED,
            starts_at=now - timedelta(days=3),
            expires_at=None,
        )

        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        self.assertEqual(self.client.get(lesson_url).status_code, 403)

        progress_url = reverse("academy:lesson-progress", args=[self.paid_lesson.pk])
        response = self.client.post(progress_url, {"status": LessonProgress.Status.COMPLETED})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            LessonProgress.objects.filter(user=self.user, lesson=self.paid_lesson).exists()
        )

    def test_unreleased_lesson_denies_direct_access_and_progress_updates(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=now - timedelta(hours=1),
            expires_at=None,
        )
        self.paid_lesson.release_day = 2
        self.paid_lesson.save(update_fields=["release_day", "updated_at"])

        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        self.assertEqual(self.client.get(lesson_url).status_code, 403)
        progress_url = reverse("academy:lesson-progress", args=[self.paid_lesson.pk])
        response = self.client.post(progress_url, {"status": LessonProgress.Status.COMPLETED})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            LessonProgress.objects.filter(user=self.user, lesson=self.paid_lesson).exists()
        )

    def test_course_progress_excludes_unpublished_lessons_and_other_users(self):
        other_user = User.objects.create_user(
            username="other-learner", password="Test-password-123!"
        )
        hidden_lesson = Lesson.objects.create(
            module=self.module,
            title="Unpublished lesson",
            slug="unpublished-lesson",
            position=3,
            is_published=False,
            content_markdown="Must not contribute to visible progress.",
        )
        LessonProgress.objects.create(
            user=self.user, lesson=self.preview_lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        LessonProgress.objects.create(
            user=other_user, lesson=self.paid_lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        LessonProgress.objects.create(
            user=self.user, lesson=hidden_lesson,
            status=LessonProgress.Status.COMPLETED,
        )

        response = self.client.get(
            reverse("academy:course-detail", args=[self.course.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_lessons"], 2)
        self.assertEqual(response.context["completed_lessons"], 1)
        self.assertEqual(response.context["progress_percent"], 50)

    def test_learning_room_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("academy:home"))
        self.assertEqual(response.status_code, 302)
