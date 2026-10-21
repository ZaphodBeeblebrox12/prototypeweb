import json
import tempfile
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from apps.academy.content_rendering import build_lesson_sections, validate_markdown_source
from apps.academy.forms import validate_upload_image
from apps.academy.importing import publish_course_import, validate_import_for_publish
from apps.academy.models import (
    Course,
    CourseContentRevision,
    CourseImport,
    CourseMediaAsset,
    CourseModule,
    Lesson,
    LessonProgress,
)
from apps.academy.storage import course_asset_storage
from apps.audit.models import AuditLog

User = get_user_model()


class CourseImportWorkflowTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "lessons").mkdir()
        self.source = self.root / "lessons" / "module-01.md"
        self.manifest_path = self.root / "course-manifest.json"
        self.write_source("Initial lesson explanation.")
        self.write_manifest()
        self.admin = User.objects.create_user(
            username="course-admin", password="test-password",
            role=User.Role.ADMIN, is_staff=True,
        )
        self.learner = User.objects.create_user(username="learner", password="test-password")
        self.ordinary_staff = User.objects.create_user(
            username="ordinary-staff", password="test-password",
            role=User.Role.STAFF, is_staff=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_image_validator_accepts_clear_checkbox_value(self):
        # Optional Django file fields return False when their clear checkbox is selected.
        self.assertIsNone(validate_upload_image(False))
        self.assertIsNone(validate_upload_image(None))

    def write_source(self, body):
        self.source.write_text(
            "## Lesson 1.1 — Read the evidence\n\n### The question\n\n" + body + "\n",
            encoding="utf-8",
        )

    def write_manifest(self):
        manifest = {
            "schema_version": 1,
            "manifest_version": "test-v1",
            "course": {
                "title": "Import Test Course",
                "slug": "import-test-course",
                "summary": "A course used in import tests.",
                "description": "Review before publication.",
                "position": 50,
            },
            "notebook": {
                "title": "Your Trading Notebook",
                "prompts": [{"label": "Observe", "text": "Describe the evidence."}],
            },
            "modules": [{
                "title": "Foundations",
                "slug": "foundations",
                "summary": "The first lesson.",
                "position": 1,
                "source": "lessons/module-01.md",
                "lessons": [{
                    "source_id": "1.1",
                    "title": "Read the evidence",
                    "slug": "read-the-evidence",
                    "position": 1,
                    "duration_minutes": 12,
                    "release_day": 1,
                }],
            }],
        }
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def import_draft(self):
        call_command("import_microcourse", manifest=str(self.manifest_path), verbosity=0)
        return CourseImport.objects.get(course_slug="import-test-course", status=CourseImport.Status.REVIEW)

    def test_repeated_import_is_idempotent_and_does_not_create_live_course(self):
        first = self.import_draft()
        second = self.import_draft()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(CourseImport.objects.filter(course_slug="import-test-course").count(), 1)
        self.assertFalse(Course.objects.filter(slug="import-test-course").exists())
        self.assertEqual(first.status, CourseImport.Status.REVIEW)

    def test_import_update_is_staged_until_explicit_publish_and_keeps_progress(self):
        first = self.import_draft()
        published_course = publish_course_import(first, user=self.admin)
        module = CourseModule.objects.get(course=published_course, slug="foundations")
        lesson = Lesson.objects.get(module=module, slug="read-the-evidence")
        lesson_id = lesson.pk
        progress = LessonProgress.objects.create(
            user=self.learner, lesson=lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        old_content = lesson.content_markdown

        self.write_source("Updated explanation with a contrasting example.")
        second = self.import_draft()
        lesson.refresh_from_db()
        self.assertEqual(lesson.content_markdown, old_content)
        self.assertEqual(published_course.status, Course.Status.PUBLISHED)

        publish_course_import(second, user=self.admin)
        lesson.refresh_from_db()
        progress.refresh_from_db()
        self.assertEqual(lesson.pk, lesson_id)
        self.assertIn("Updated explanation", lesson.content_markdown)
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)
        self.assertEqual(CourseContentRevision.objects.filter(lesson=lesson).count(), 1)

    def test_external_image_url_is_preserved_as_fallback_and_can_publish(self):
        original_url = "https://example.com/charts/bollinger-example.png?source=lesson"
        self.write_source(f"![Original chart]({original_url})\n\nThe source can be replaced later.")
        record = self.import_draft()

        staged_asset = record.assets.get()
        self.assertEqual(staged_asset.original_url, original_url)
        self.assertFalse(staged_asset.file)
        self.assertEqual(validate_import_for_publish(record), [])

        course = publish_course_import(record, user=self.admin)
        live_asset = CourseMediaAsset.objects.get(course=course)
        self.assertEqual(live_asset.original_url, original_url)
        self.assertFalse(live_asset.file)
        lesson = Lesson.objects.get(module__course=course)
        rendered = build_lesson_sections(
            lesson.content_markdown, {str(live_asset.pk): live_asset.original_url}
        )
        self.assertIn(original_url, rendered["idea_html"])

    def test_multiple_external_images_keep_independent_replaceable_slots(self):
        first_url = "https://example.com/charts/first.png"
        second_url = "https://example.com/charts/second.png"
        self.write_source(
            f"![First chart]({first_url})\n\n![Second chart]({second_url})"
        )
        record = self.import_draft()
        self.assertEqual(record.assets.count(), 2)
        self.assertEqual(
            set(record.assets.values_list("original_url", flat=True)),
            {first_url, second_url},
        )

        course = publish_course_import(record, user=self.admin)
        lesson = Lesson.objects.get(module__course=course)
        asset_urls = {
            str(asset.pk): asset.original_url
            for asset in CourseMediaAsset.objects.filter(course=course)
        }
        sections = build_lesson_sections(lesson.content_markdown, asset_urls)
        self.assertIn(first_url, sections["idea_html"])
        self.assertIn(second_url, sections["idea_html"])
        self.assertEqual(len(lesson.content_json["asset_ids"]), 2)

    def test_admin_can_add_multiple_url_images_to_a_lesson(self):
        course = publish_course_import(self.import_draft(), user=self.admin)
        lesson = Lesson.objects.get(module__course=course)
        self.client.force_login(self.admin)
        add_url = reverse("admin:academy_lesson_add_figure", args=[lesson.pk])
        urls = [
            ("Second chart", "https://example.com/charts/second.png", "examples"),
            ("Third chart", "https://example.com/charts/third.png", "examples"),
        ]
        for alt_text, original_url, placement in urls:
            response = self.client.post(add_url, {
                "alt_text": alt_text,
                "original_url": original_url,
                "placement": placement,
            })
            self.assertEqual(response.status_code, 302)

        lesson.refresh_from_db()
        added_assets = CourseMediaAsset.objects.filter(course=course, asset_key__startswith="admin-added/")
        self.assertEqual(added_assets.count(), 2)
        self.assertTrue(all(asset.original_url for asset in added_assets))
        self.assertEqual(len(lesson.content_json["asset_ids"]), 2)
        asset_urls = {str(asset.pk): asset.original_url for asset in added_assets}
        sections = build_lesson_sections(lesson.content_markdown, asset_urls)
        self.assertIn("https://example.com/charts/second.png", sections["examples_html"])
        self.assertIn("https://example.com/charts/third.png", sections["examples_html"])
        self.assertEqual(
            CourseContentRevision.objects.filter(lesson=lesson, revision_type=CourseContentRevision.RevisionType.ADMIN_EDIT).count(),
            2,
        )

    def test_admin_added_images_render_only_in_the_selected_learning_room_tab(self):
        course = publish_course_import(self.import_draft(), user=self.admin)
        lesson = Lesson.objects.get(module__course=course)
        self.client.force_login(self.admin)
        add_url = reverse("admin:academy_lesson_add_figure", args=[lesson.pk])
        placements = [
            ("Idea diagram", "https://example.com/figures/idea.png", "idea", "idea_html"),
            ("Chart example", "https://example.com/figures/example.png", "examples", "examples_html"),
            ("Practice figure", "https://example.com/figures/practice.png", "practice", "practice_html"),
        ]

        for alt_text, url, placement, _expected_section in placements:
            response = self.client.post(add_url, {
                "alt_text": alt_text,
                "original_url": url,
                "placement": placement,
            })
            self.assertEqual(response.status_code, 302)

        lesson.refresh_from_db()
        self.assertEqual(len(lesson.content_json["asset_ids"]), 3)
        added_assets = CourseMediaAsset.objects.filter(
            course=course, asset_key__startswith="admin-added/"
        )
        self.assertEqual(added_assets.count(), 3)
        asset_urls = {str(asset.pk): asset.original_url for asset in added_assets}
        sections = build_lesson_sections(lesson.content_markdown, asset_urls)

        for alt_text, url, _placement, expected_section in placements:
            self.assertIn(alt_text, sections[expected_section])
            self.assertIn(url, sections[expected_section])
            for other_section in ("idea_html", "examples_html", "practice_html"):
                if other_section != expected_section:
                    self.assertNotIn(url, sections[other_section])

        self.assertEqual(
            CourseContentRevision.objects.filter(
                lesson=lesson,
                revision_type=CourseContentRevision.RevisionType.ADMIN_EDIT,
            ).count(),
            3,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="academy_lesson_figure_added",
                object_type="lesson",
                object_id=str(lesson.pk),
                user=self.admin,
            ).count(),
            3,
        )

    def test_ordinary_staff_cannot_add_lesson_figures(self):
        course = publish_course_import(self.import_draft(), user=self.admin)
        lesson = Lesson.objects.get(module__course=course)
        self.client.force_login(self.ordinary_staff)
        response = self.client.post(
            reverse("admin:academy_lesson_add_figure", args=[lesson.pk]),
            {"alt_text": "Chart", "original_url": "https://example.com/chart.png", "placement": "examples"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CourseMediaAsset.objects.filter(course=course, asset_key__startswith="admin-added/").exists())

    def test_ordinary_staff_and_learner_cannot_add_or_replace_shared_images(self):
        course = publish_course_import(self.import_draft(), user=self.admin)
        lesson = Lesson.objects.get(module__course=course)
        source_url = "https://example.com/charts/admin-only.png"
        asset = CourseMediaAsset.objects.create(
            course=course,
            asset_key="remote/admin-only-chart",
            original_url=source_url,
            alt_text="Original administrator image",
        )
        add_url = reverse("admin:academy_lesson_add_figure", args=[lesson.pk])
        replace_url = reverse("admin:academy_coursemediaasset_change", args=[asset.pk])

        for user, expected_status in (
            (self.ordinary_staff, 403),
            (self.learner, 302),
        ):
            with self.subTest(user=user.username, action="add"):
                self.client.force_login(user)
                response = self.client.post(
                    add_url,
                    {
                        "alt_text": "Unauthorized addition",
                        "original_url": "https://example.com/charts/unauthorized.png",
                        "placement": "examples",
                    },
                )
                self.assertEqual(response.status_code, expected_status)
                self.assertFalse(
                    CourseMediaAsset.objects.filter(
                        course=course,
                        asset_key__startswith="admin-added/",
                    ).exists()
                )

            with self.subTest(user=user.username, action="replace"):
                response = self.client.post(
                    replace_url,
                    {"alt_text": "Unauthorized replacement"},
                )
                self.assertEqual(response.status_code, expected_status)
                asset.refresh_from_db()
                self.assertFalse(asset.file)
                self.assertEqual(asset.alt_text, "Original administrator image")
                self.assertEqual(asset.original_url, source_url)

        self.assertFalse(
            AuditLog.objects.filter(
                action="academy_course_media_replaced",
                object_type="course_media_asset",
                object_id=str(asset.pk),
            ).exists()
        )

    def test_lesson_add_figure_requires_csrf_token(self):
        course = publish_course_import(self.import_draft(), user=self.admin)
        lesson = Lesson.objects.get(module__course=course)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        response = client.post(
            reverse("admin:academy_lesson_add_figure", args=[lesson.pk]),
            {"alt_text": "Chart", "original_url": "https://example.com/chart.png", "placement": "examples"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CourseMediaAsset.objects.filter(course=course, asset_key__startswith="admin-added/").exists())

    def test_admin_can_replace_a_linked_image_with_an_upload(self):
        course = Course.objects.create(title="Image replacement course", slug="image-replacement-course")
        source_url = "https://example.com/charts/original.png"
        asset = CourseMediaAsset.objects.create(
            course=course, asset_key="remote/original-chart", original_url=source_url,
            alt_text="Original linked chart",
        )
        image_bytes = BytesIO()
        Image.new("RGB", (12, 8), (245, 220, 170)).save(image_bytes, format="PNG")
        upload = SimpleUploadedFile("my-chart.png", image_bytes.getvalue(), content_type="image/png")

        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("admin:academy_coursemediaasset_change", args=[asset.pk]),
            {"alt_text": "My replacement chart", "file": upload},
        )
        self.assertEqual(response.status_code, 302)
        asset.refresh_from_db()
        self.addCleanup(lambda: course_asset_storage.delete(asset.file.name) if asset.file else None)
        self.assertTrue(asset.file)
        self.assertEqual(asset.original_url, source_url)
        self.assertEqual(asset.alt_text, "My replacement chart")
        self.assertEqual(asset.updated_by, self.admin)
        self.assertTrue(AuditLog.objects.filter(
            action="academy_course_media_replaced",
            object_type="course_media_asset",
            object_id=str(asset.pk),
            user=self.admin,
        ).exists())


    def test_missing_image_blocks_publish_and_leaves_course_unpublished(self):
        self.write_source("![Missing chart](../assets/not-ready.png)\n\nThis is the lesson.")
        record = self.import_draft()
        errors = validate_import_for_publish(record)
        self.assertTrue(any("Missing course image" in error for error in errors))
        with self.assertRaises(ValidationError):
            publish_course_import(record, user=self.admin)
        self.assertFalse(Course.objects.filter(slug="import-test-course").exists())

    def test_ordinary_staff_cannot_open_admin_course_review(self):
        record = self.import_draft()
        self.client.force_login(self.ordinary_staff)
        response = self.client.get(
            reverse("admin:academy_courseimport_review", args=[record.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_publish_requires_csrf_token(self):
        record = self.import_draft()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        response = client.post(
            reverse("admin:academy_courseimport_publish", args=[record.pk]),
            {},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Course.objects.filter(slug="import-test-course").exists())

    def test_unsafe_active_markup_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_markdown_source("Lesson text <script>alert(1)</script>")


class CourseImportAdminPreviewTests(TestCase):
    def test_authorized_admin_can_open_course_preview(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "lessons").mkdir()
        (root / "lessons" / "module-01.md").write_text(
            "## Lesson 1.1 — Read the evidence\n\n### The question\n\nPreview text.\n\n"
            "![Temporary chart](https://example.com/temporary-chart.png)",
            encoding="utf-8",
        )
        manifest = {
            "schema_version": 1,
            "course": {"title": "Reviewable Course", "slug": "reviewable-course"},
            "modules": [{
                "title": "Start", "slug": "start", "position": 1,
                "source": "lessons/module-01.md",
                "lessons": [{"source_id": "1.1", "title": "Read the evidence", "slug": "read-the-evidence"}],
            }],
        }
        manifest_path = root / "course-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        call_command("import_microcourse", manifest=str(manifest_path), verbosity=0)
        record = CourseImport.objects.get(course_slug="reviewable-course")
        payload = record.payload
        review_lesson = payload["modules"][0]["lessons"][0]
        review_lesson["content_markdown"] += (
            "\n\n### Additional chart examples\n\n"
            "[[teaching-figure:review-comparison]]"
        )
        review_lesson["content_json"] = {
            "figures": {
                "review-comparison": {
                    "type": "comparison-cards",
                    "title": "Reviewed comparison figure",
                    "cards": [{
                        "kicker": "ALTERNATIVE",
                        "title": "Wait for confirmation",
                        "body": "A single observation is not sufficient context.",
                    }],
                },
            },
            "questions": [{
                "id": "review-question-1",
                "prompt": "Review question prompt",
                "options": ["Assess the context", "Treat the observation as a guarantee"],
            }],
            "notebook": {"title": "Review notebook", "prompts": []},
            "video_url": "https://example.com/lesson-video.mp4",
        }
        record.payload = payload
        record.save(update_fields=["payload"])
        admin_user = User.objects.create_user(
            username="preview-admin", password="test-password",
            role=User.Role.ADMIN, is_staff=True,
        )
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin:academy_courseimport_review", args=[record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preview text.")
        self.assertContains(response, 'src="https://example.com/temporary-chart.png"')
        self.assertContains(response, "Reviewed comparison figure")
        self.assertContains(response, "Review question prompt")
        self.assertContains(response, "Administrator preview only. Answer submission is disabled in this view.")
        self.assertContains(response, 'src="https://example.com/lesson-video.mp4"')
        self.assertContains(response, "Using URL for now")
        self.assertContains(response, "Open source")
        self.assertContains(response, "Approve and publish course")


class CourseSourceSvgAndReleaseGateTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "lessons").mkdir()
        (self.root / "assets").mkdir()
        self.source = self.root / "lessons" / "module-01.md"
        self.manifest_path = self.root / "course-manifest.json"

    def write_package(self, slug, image_markdown):
        newline = chr(10)
        source_lines = [
            "## Lesson 1.1 — Read the evidence", "",
            "### The question", "",
            "Read the chart in context.", "",
            image_markdown, "",
        ]
        self.source.write_text(newline.join(source_lines), encoding="utf-8")
        self.manifest_path.write_text(json.dumps({
            "schema_version": 1,
            "manifest_version": "test-v1",
            "course": {
                "title": "Source Asset Test Course",
                "slug": slug,
                "summary": "Testing reviewed source assets.",
                "description": "A staged-only test.",
                "position": 50,
            },
            "modules": [{
                "title": "Foundations",
                "slug": "foundations",
                "position": 1,
                "source": "lessons/module-01.md",
                "lessons": [{
                    "source_id": "1.1",
                    "title": "Read the evidence",
                    "slug": "read-the-evidence",
                    "position": 1,
                    "duration_minutes": 12,
                    "release_day": 1,
                }],
            }],
        }), encoding="utf-8")
        call_command("import_microcourse", manifest=str(self.manifest_path), verbosity=0)
        return CourseImport.objects.get(course_slug=slug, status=CourseImport.Status.REVIEW)

    def test_checked_in_svg_is_staged_as_svg_source_asset(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80" viewBox="0 0 120 80">'
            '<title>Example chart</title><desc>A simple chart illustration.</desc>'
            '<rect x="1" y="1" width="118" height="78" fill="#fbf7ef"/>'
            '<path d="M10 60 L40 35 L70 45 L110 15" stroke="#26392f" stroke-width="3" fill="none"/>'
            '</svg>'
        )
        (self.root / "assets" / "figure.svg").write_text(svg, encoding="utf-8")
        record = self.write_package("svg-source-test", "![Example figure](../assets/figure.svg)")
        asset = record.assets.get(asset_key="assets/figure.svg")
        self.assertTrue(asset.file.name.endswith(".svg"))
        self.assertFalse(asset.source_error)
        self.assertIn("asset://", record.payload["modules"][0]["lessons"][0]["content_markdown"])

    def test_scripted_svg_is_not_staged_as_an_image(self):
        (self.root / "assets" / "figure.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10">'
            '<title>Unsafe</title><desc>Unsafe example</desc><script>alert(1)</script></svg>',
            encoding="utf-8",
        )
        record = self.write_package("svg-unsafe-test", "![Example figure](../assets/figure.svg)")
        asset = record.assets.get(asset_key="assets/figure.svg")
        self.assertFalse(asset.file)
        self.assertIn("active, linked or externally loaded", asset.source_error)

    def test_bollinger_remote_example_blocks_publish_until_replaced(self):
        record = self.write_package(
            "understand-bollinger-bands",
            "![Temporary historical chart](https://example.com/chart.png)",
        )
        errors = validate_import_for_publish(record)
        self.assertTrue(any("Temporary external Bollinger Bands chart reference" in error for error in errors))
        asset = record.assets.get(asset_key__startswith="remote/")
        stream = BytesIO()
        Image.new("RGB", (20, 20), "white").save(stream, format="PNG")
        stream.seek(0)
        asset.file.save("replacement.png", File(stream), save=True)
        errors = validate_import_for_publish(record)
        self.assertFalse(any("Temporary external Bollinger Bands chart reference" in error for error in errors))
