import base64
import json
import re
import uuid
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import (
    Course,
    CourseImport,
    CourseImportAsset,
    CourseMediaAsset,
    CourseModule,
    Lesson,
    LessonInstructorMaterial,
    LessonProgress,
)

User = get_user_model()


class CourseBuilderApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="course-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)

    def draft_payload(self, slug="builder-api-course"):
        return {
            "course": {
                "id": "course-local-1",
                "title": "Builder API Course",
                "slug": slug,
                "summary": "A practical course summary.",
                "description": "Course description.",
                "category": "Chart reading",
                "level": "Intermediate",
                "duration": "Self-paced",
                "price": "",
                "accessType": "paid",
                "status": "draft",
                "outcomes": ["Describe evidence before interpreting it."],
                "modules": [
                    {
                        "id": "module-local-1",
                        "title": "Module 01 — Foundations",
                        "description": "Start with observable evidence.",
                        "lessons": [
                            {
                                "id": "lesson-local-1",
                                "title": "Lesson 1.1 — First principles",
                                "summary": "Separate evidence from interpretation.",
                                "format": "reading",
                                "minutes": 12,
                                "videoUrl": "https://media.example.test/lesson.mp4",
                                "notebook": {
                                    "title": "A useful notebook",
                                    "prompts": [
                                        {"label": "Observe", "text": "What evidence is visible?"}
                                    ],
                                },
                                "reflectionPrompt": "What evidence do you observe before interpreting it?",
                                "reflectionModelReasoning": "Separate visible evidence from interpretation and consider what would change the view.",
                                "reflectionChartNotes": "Compare the evidence with a reasonable alternative.",
                                "content": "## Notice\n\nDescribe what is visible before drawing a conclusion.",
                                "questions": [
                                    {
                                        "id": "question-local-1",
                                        "prompt": "What should you identify first?",
                                        "options": ["Visible evidence", "A prediction", "A target"],
                                        "correctIndex": 0,
                                        "explanation": "Start with what can be observed.",
                                    }
                                ],
                                "images": [],
                                "image": None,
                                "relatedCourseIds": [],
                            }
                        ],
                    }
                ],
            },
            "mode": "save",
        }

    def test_builder_learner_preview_uses_academy_template_and_keeps_notebook_authoring(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "data-builder-website-preview")
        self.assertContains(response, "data-builder-website-preview-frame")
        self.assertContains(response, "data-website-preview-status")
        self.assertContains(response, "data-website-preview-error")
        self.assertContains(response, 'data-action="refresh-website-preview"')
        self.assertContains(response, "async function refreshBuilderWebsitePreview(force = false)")
        self.assertContains(response, "website_preview_url")
        builder_source = response.content.decode("utf-8")
        preview_start = builder_source.index("function previewFields(c)")
        preview_end = builder_source.index("  renderMarkdown = function(src)", preview_start)
        learner_preview = builder_source[preview_start:preview_end]
        self.assertNotIn("builder-lesson-preview-grid", learner_preview)
        self.assertNotIn("notebookPreviewMarkup(lesson)", learner_preview)
        self.assertContains(response, "function notebookPreviewMarkup(lesson)")
        self.assertContains(response, 'class="preview-trading-notebook"')
        self.assertContains(response, "KEEP<br>IN VIEW")
        self.assertContains(response, "YOUR TRADING NOTEBOOK")
        self.assertContains(response, "notebookPreviewMarkup(lesson)")
        self.assertContains(response, "Notebook heading")
        self.assertContains(response, "notebook-editor-preview")
        self.assertContains(response, "data-notebook-preview")
        self.assertContains(response, "notebookPreviewMarkup(l)")
        self.assertContains(response, "Reflection & reasoning")
        self.assertContains(response, "Require course-owned images before publishing")
        self.assertContains(response, "Courses page placement")
        self.assertContains(response, 'id="courseAccessType"')
        self.assertContains(response, 'value="free"')
        self.assertContains(response, 'value="membership"')
        self.assertContains(response, 'value="mixed"')
        self.assertContains(response, 'data-field="catalogueRole"')
        self.assertContains(response, "Not listed on the Courses page")
        self.assertContains(response, 'data-field="catalogueHook"')
        self.assertContains(response, 'data-field="problemStatement"')
        self.assertContains(response, 'data-field="learningFocus"')
        self.assertContains(response, 'data-field="authoredTags"')
        self.assertContains(response, 'data-field="whyThisOne"')
        self.assertContains(response, "Live tile preview")
        self.assertContains(response, "Route to Chart examples")
        self.assertContains(response, "Manage inserted lesson references")
        self.assertContains(response, "lessonQualityMarkup")
        self.assertContains(response, "data-builder-website-preview-frame")
        self.assertNotContains(response, "previewFieldsBeforeQualityChecks")
        self.assertContains(response, "payload.publish_errors")
        self.assertContains(response, "What needs attention:")
        self.assertContains(response, "validation-error")
        self.assertContains(response, "Insert a companion-course card (Option 3)")
        self.assertContains(response, "data-course-card-search")
        self.assertContains(response, "eligibleCompanionCourses()")
        self.assertContains(response, "replace-course-card-and-remove-links")
        self.assertContains(response, "Keep one card here &amp; clean up")
        self.assertContains(response, "currentSlug === courseSlug")
        self.assertContains(response, "cards[cards.length - 1]")
        self.assertContains(response, "routeMarkerPattern")
        self.assertContains(response, "Kept one companion card at its final placement")
        self.assertContains(response, "removes earlier duplicates and accidental lesson links")
        self.assertContains(
            response,
            'The website preview preserves this placement.</span></div>${courseCardPickerMarkup()}</div></div><div class="helper-note">',
        )
        self.assertContains(
            response, "Those render as lesson links/cards, not as the Option 3 inline course card."
        )
        self.assertContains(response, "data-lesson-reference-picker")
        self.assertContains(response, "Uses the existing Learning Room layout")
        self.assertNotContains(response, "Reuse the Learning Room template")
        self.assertContains(response, "Regional content")
        self.assertContains(response, "previewAudienceSelect")
        self.assertContains(response, "lessonContentAudienceSelect")
        self.assertContains(response, "Start a custom version")

    def test_course_access_type_is_saved_and_reloaded_with_builder_draft(self):
        payload = self.draft_payload("builder-membership-course")
        payload["course"]["accessType"] = "membership"
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        self.assertEqual(record.payload["course"]["access_type"], "membership")
        self.assertEqual(record.payload["builder_state"]["accessType"], "membership")

        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        reloaded = next(
            draft for draft in refreshed.json()["drafts"]
            if draft["serverDraftId"] == str(record.pk)
        )
        self.assertEqual(reloaded["accessType"], "membership")

    def test_rich_text_format_dropdown_uses_accessible_custom_menu(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "function richFormatPickerMarkup()")
        self.assertContains(response, "data-rich-format-toggle")
        self.assertContains(response, "data-rich-format-menu")
        self.assertContains(response, "data-rich-format-option")
        self.assertContains(response, "Heading 2 (Main article heading)")
        self.assertContains(response, "Heading 3 (Section subheading)")
        self.assertContains(response, "Heading 4 (Minor subheading)")
        self.assertContains(response, "Heading 5 (Small heading)")
        self.assertContains(
            response, "function syncRichFormatPickerFromSelection(editor, selection)"
        )
        self.assertContains(response, "function closeRichFormatPickers(exceptPicker)")
        self.assertContains(response, "document.execCommand('formatBlock', false, value)")
        self.assertContains(response, "event.key === 'ArrowDown'")
        self.assertContains(response, "event.key === 'Escape'")
        self.assertNotContains(response, "<select data-rich-format")

    def test_rich_text_table_allows_custom_dimensions(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "function promptTableDimension(label, defaultValue, maximum)")
        self.assertContains(response, "function richTableMarkup(rows, columns)")
        self.assertContains(response, "promptTableDimension('Number of columns', 3, 12)")
        self.assertContains(response, "promptTableDimension('Number of rows', 3, 30)")
        self.assertContains(response, "richTableMarkup(rows, columns)")
        self.assertContains(response, "must be a whole number between 1 and")

    def test_regional_asset_remapping_matches_full_image_ids(self):
        from .course_builder_api import _remap_regional_asset_refs

        short_id = "image-a"
        long_id = "image-ab"
        stable_short = "11111111-1111-4111-8111-111111111111"
        stable_long = "22222222-2222-4222-8222-222222222222"
        referenced = set()

        result = _remap_regional_asset_refs(
            "![Short](asset://image-a) ![Long](asset://image-ab)",
            {short_id: stable_short, long_id: stable_long},
            referenced,
        )

        self.assertEqual(
            result,
            f"![Short](asset://{stable_short}) ![Long](asset://{stable_long})",
        )
        self.assertEqual(referenced, {stable_short, stable_long})

    def test_regional_content_is_persisted_in_publish_payload_and_builder_snapshot(self):
        payload = self.draft_payload("regional-content-course")
        lesson = payload["course"]["modules"][0]["lessons"][0]
        lesson["content"] += "\n\n[[regional-block:risk-note]]"
        lesson["regionalContent"] = {
            "country:IN": "## India version\n\nIndia-specific example.\n\n| Index | Market |\n|---|---|\n| NIFTY | India |",
            "region:APAC": "## Asia-Pacific version\n\nRegional example.",
        }
        lesson["regionalBlocks"] = [
            {
                "id": "risk-note",
                "title": "Risk disclosure",
                "baseContent": "Global educational disclosure.",
                "variants": [
                    {
                        "id": "risk-note-in",
                        "scope": "country",
                        "code": "IN",
                        "content": "India-specific disclosure in INR.",
                        "hidden": False,
                    },
                    {
                        "id": "risk-note-na",
                        "scope": "region",
                        "code": "NA",
                        "content": "North American disclosure.",
                        "hidden": False,
                    },
                    {
                        "id": "risk-note-hidden",
                        "scope": "country",
                        "code": "CA",
                        "content": "",
                        "hidden": True,
                    },
                ],
            }
        ]
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        block = saved_lesson["content_json"]["regional_blocks"]["risk-note"]
        self.assertEqual(block["base_content"], "Global educational disclosure.")
        self.assertEqual(block["variants"][0]["code"], "IN")
        self.assertEqual(block["variants"][1]["scope"], "region")
        self.assertTrue(block["variants"][2]["hidden"])
        self.assertEqual(
            saved_lesson["content_json"]["regional_lesson_content"]["country:IN"],
            lesson["regionalContent"]["country:IN"],
        )
        self.assertEqual(
            saved_lesson["content_json"]["regional_lesson_content"]["region:APAC"],
            lesson["regionalContent"]["region:APAC"],
        )
        saved_state = record.payload["builder_state"]["modules"][0]["lessons"][0]
        self.assertEqual(saved_state["regionalBlocks"][0]["title"], "Risk disclosure")
        self.assertEqual(saved_state["regionalContent"], lesson["regionalContent"])

        # Exercise the editor's reload path: a fresh API GET must hydrate the
        # same regional blocks and audience overrides that were just saved.
        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        reloaded_state = next(
            draft for draft in refreshed.json()["drafts"]
            if draft["serverDraftId"] == str(record.pk)
        )
        reloaded_lesson = reloaded_state["modules"][0]["lessons"][0]
        self.assertEqual(reloaded_lesson["regionalBlocks"], lesson["regionalBlocks"])
        self.assertEqual(reloaded_lesson["regionalContent"], lesson["regionalContent"])

    def test_whole_lesson_override_images_use_stable_managed_asset_ids(self):
        from .course_builder_api import _asset_uuid, _build_import_payload

        course_slug = "country-body-image"
        state = self.draft_payload(course_slug)["course"]
        lesson = state["modules"][0]["lessons"][0]
        stable_id = _asset_uuid(course_slug, "india-chart")
        lesson["images"] = [
            {
                "id": "india-chart",
                "name": "india-chart.png",
                "assetUuid": stable_id,
                "title": "India chart",
                "alt": "A chart for the India example",
                "caption": "A country-specific worked example.",
                "data": "",
            }
        ]
        lesson["regionalContent"] = {
            "country:IN": "## India example\n\n![India chart](asset://india-chart)"
        }
        imported, _image_sources = _build_import_payload(state, course_slug)
        saved = imported["modules"][0]["lessons"][0]
        content_json = saved["content_json"]
        self.assertIn(f"asset://{stable_id}", content_json["regional_lesson_content"]["country:IN"])
        self.assertIn(stable_id, content_json["asset_ids"])
        self.assertEqual(content_json["figures"][stable_id]["title"], "India chart")

    def test_admin_can_save_shared_draft(self):
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["ok"])
        self.assertIsNone(response.json()["github_source_synced"])
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        self.assertEqual(
            response.json()["website_preview_url"],
            reverse("academy:course-import-preview", args=[record.pk]),
        )
        self.assertEqual(record.status, CourseImport.Status.DRAFT)
        self.assertEqual(record.payload["builder_state"]["title"], "Builder API Course")
        self.assertEqual(
            record.payload["modules"][0]["lessons"][0]["content_markdown"],
            "## Notice\n\nDescribe what is visible before drawing a conclusion.",
        )
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        self.assertEqual(
            saved_lesson["content_json"]["video_url"], "https://media.example.test/lesson.mp4"
        )
        self.assertEqual(saved_lesson["content_json"]["notebook"]["title"], "A useful notebook")
        self.assertEqual(
            saved_lesson["content_json"]["reflection"]["prompt"],
            "What evidence do you observe before interpreting it?",
        )
        self.assertEqual(
            saved_lesson["content_json"]["reflection"]["model_reasoning"],
            "Separate visible evidence from interpretation and consider what would change the view.",
        )
        self.assertEqual(
            record.payload["course"]["learning_outcomes"],
            ["Describe evidence before interpreting it."],
        )
        self.assertNotIn("correctIndex", saved_lesson["content_json"])

    def test_publish_validation_rejects_hotlinked_instructional_images_for_any_course(self):
        from .importing import validate_import_for_publish

        slug = "external-instructional-image"
        asset_id = uuid.uuid4()
        payload = {
            "course": {"title": "External Image Test", "slug": slug, "requires_owned_assets": True},
            "assets": [],
            "modules": [
                {
                    "title": "Foundations",
                    "lessons": [
                        {
                            "title": "First lesson",
                            "content_markdown": f"![Chart](asset://{asset_id})",
                            "content_json": {"asset_ids": [str(asset_id)]},
                        }
                    ],
                }
            ],
        }
        record = CourseImport.objects.create(
            course_slug=slug,
            title="External Image Test",
            manifest_version="course-builder-v1",
            content_hash="e" * 64,
            source_manifest=f"builder://{slug}",
            status=CourseImport.Status.REVIEW,
            imported_by=self.admin,
            payload=payload,
        )
        CourseImportAsset.objects.create(
            course_import=record,
            asset_key="remote/external-chart",
            stable_asset_id=asset_id,
            original_url="https://charts.example.test/temporary.png",
            file="",
        )

        errors = validate_import_for_publish(record)

        self.assertTrue(any("course-owned image" in error for error in errors), errors)

    def test_storage_timeout_falls_back_to_original_url_when_no_local_copy_exists(self):
        # These asset URLs are registered behind Django's staff-only admin view.
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_staff"])
        self.client.force_login(self.admin)
        course_import = CourseImport.objects.create(
            course_slug="missing-image-fallback",
            title="Missing Image Fallback",
            manifest_version="course-builder-v1",
            content_hash="f" * 64,
            source_manifest="builder://missing-image-fallback",
            status=CourseImport.Status.DRAFT,
            imported_by=self.admin,
            payload={
                "course": {"title": "Missing Image Fallback", "slug": "missing-image-fallback"},
                "modules": [],
            },
        )
        asset_id = uuid.uuid4()
        original_url = "https://charts.example.test/third-image.png"
        CourseImportAsset.objects.create(
            course_import=course_import,
            asset_key="charts/third-image.png",
            stable_asset_id=asset_id,
            source_path="charts/missing-third-image.png",
            original_url=original_url,
            file="academy/course-imports/missing-image-fallback/third.png",
        )

        storage = CourseImportAsset._meta.get_field("file").storage
        with patch.object(storage, "exists", side_effect=OSError("Google Drive timed out")):
            response = self.client.get(
                reverse("admin:academy_courseimport_asset", args=[course_import.pk, asset_id])
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], original_url)

    def test_storage_timeout_uses_checked_in_source_path_when_available(self):
        # These asset URLs are registered behind Django's staff-only admin view.
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_staff"])
        self.client.force_login(self.admin)
        course_slug = "checked-in-image-fallback"
        source_path = "charts/third-image.png"
        course_import = CourseImport.objects.create(
            course_slug=course_slug,
            title="Checked-in Image Fallback",
            manifest_version="course-builder-v1",
            content_hash="c" * 64,
            source_manifest="builder://checked-in-image-fallback",
            status=CourseImport.Status.DRAFT,
            imported_by=self.admin,
            payload={
                "course": {"title": "Checked-in Image Fallback", "slug": course_slug},
                "modules": [],
            },
        )
        asset_id = uuid.uuid4()
        CourseImportAsset.objects.create(
            course_import=course_import,
            asset_key=source_path,
            stable_asset_id=asset_id,
            source_path=source_path,
            original_url="https://charts.example.test/fallback.png",
            file="academy/course-imports/checked-in-image-fallback/third.png",
        )

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            stored_chart = root / "course-source" / course_slug / source_path
            stored_chart.parent.mkdir(parents=True, exist_ok=True)
            stored_chart.write_bytes(b"checked-in-chart-data")

            storage = CourseImportAsset._meta.get_field("file").storage
            with (
                override_settings(BASE_DIR=str(root / "backend")),
                patch.object(storage, "exists", side_effect=OSError("Google Drive timed out")),
            ):
                response = self.client.get(
                    reverse("admin:academy_courseimport_asset", args=[course_import.pk, asset_id])
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"checked-in-chart-data")

    def test_learner_reflection_is_saved_only_after_access_check(self):
        course = Course.objects.create(
            title="Reflection Persistence",
            slug="reflection-persistence",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="First reading",
            slug="first-reading",
            position=1,
            is_published=True,
            is_preview=True,
            content_markdown="## Observe\n\nDescribe the visible evidence.",
            content_json={
                "reflection": {
                    "prompt": "What can you observe?",
                    "model_reasoning": "Separate the observation from the interpretation.",
                    "chart_notes": "Check an alternative reading.",
                },
            },
        )

        response = self.client.post(
            reverse("academy:lesson-reflection-submit", args=[lesson.pk]),
            {
                "reflection_response": "Price closed above the marked range; follow-through is not known yet."
            },
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["saved"])
        progress = LessonProgress.objects.get(user=self.admin, lesson=lesson)
        self.assertEqual(
            progress.response_json["reflection_response"],
            "Price closed above the marked range; follow-through is not known yet.",
        )

    def test_learner_cannot_save_reflection_before_lesson_access(self):
        course = Course.objects.create(
            title="Locked Reflection",
            slug="locked-reflection",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Locked reading",
            slug="locked-reading",
            position=1,
            is_published=True,
            is_preview=False,
            content_json={"reflection": {"prompt": "What do you observe?"}},
        )

        response = self.client.post(
            reverse("academy:lesson-reflection-submit", args=[lesson.pk]),
            {"reflection_response": "A response from a user without course access."},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(LessonProgress.objects.filter(user=self.admin, lesson=lesson).exists())

    @patch(
        "apps.academy.course_builder_api.course_asset_storage.status",
        return_value={
            "backend": "github",
            "label": "private GitHub repository",
            "durable": True,
            "writes_enabled": True,
        },
    )
    def test_builder_api_exposes_durable_asset_storage_status(self, storage_status):
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["asset_storage"],
            {
                "backend": "github",
                "label": "private GitHub repository",
                "durable": True,
                "writes_enabled": True,
            },
        )
        storage_status.assert_called_once_with()

    def test_local_only_existing_asset_is_migrated_when_durable_storage_is_configured(self):
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload("builder-migrate-local-image")),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        stable_id = uuid.uuid4()
        asset = CourseImportAsset.objects.create(
            course_import=record,
            asset_key="builder/legacy-local-image",
            stable_asset_id=stable_id,
            file="academy/course-imports/legacy-local-image.png",
        )
        with (
            patch(
                "apps.academy.course_builder_api.course_asset_storage.status",
                return_value={
                    "backend": "github",
                    "label": "private GitHub repository",
                    "durable": True,
                    "writes_enabled": True,
                },
            ),
            patch(
                "apps.academy.course_builder_api.course_asset_storage.remote_exists",
                return_value=False,
            ),
            patch(
                "apps.academy.course_builder_api._copy_existing_asset",
                return_value=True,
            ) as migrate_asset,
        ):
            from .course_builder_api import _store_images

            _store_images(record, {})

        migrate_asset.assert_called_once()
        migrated_id, migrated_asset = migrate_asset.call_args.args
        self.assertEqual(migrated_id, stable_id)
        self.assertEqual(migrated_asset.pk, asset.pk)

    def test_drive_image_write_failure_returns_retryable_storage_error(self):
        payload = self.draft_payload("builder-drive-image-storage-failure")
        lesson = payload["course"]["modules"][0]["lessons"][0]
        png = BytesIO()
        Image.new("RGB", (2, 2), color=(255, 255, 255)).save(png, format="PNG")
        lesson["images"] = [
            {
                "id": "drive-write-failure-figure",
                "name": "figure.png",
                "title": "Storage failure test figure",
                "alt": "A small test figure",
                "caption": "Used to verify storage failure handling.",
                "data": "data:image/png;base64," + base64.b64encode(png.getvalue()).decode("ascii"),
            }
        ]
        lesson["image"] = lesson["images"][0]

        with patch(
            "apps.academy.course_builder_api.course_asset_storage.save",
            side_effect=OSError("Google Drive invalid_grant"),
        ):
            response = self.client.post(
                reverse("staff_course_builder_api"),
                data=json.dumps(payload),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 503, response.content)
        self.assertTrue(response.json()["retryable"])
        self.assertIn("temporarily unavailable", response.json()["detail"])

    def test_catalogue_presentation_fields_persist_in_saved_builder_draft(self):
        payload = self.draft_payload("catalogue-presentation-save")
        payload["course"].update(
            {
                "catalogueRole": "flagship",
                "catalogueHook": "Mark fewer zones. Give each one a reason.",
                "problemStatement": "For traders who see a possible level around every swing.",
                "learningFocus": "Choose zones, read reactions and identify invalidation.",
                "authoredTags": "Chart reading, zones, invalidation, chart reading",
                "whyThisOne": "Treats zones as decision areas to justify, test and invalidate—not lines to collect.",
                "cataloguePresentationConfigured": True,
            }
        )
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        state = record.payload["builder_state"]
        self.assertEqual(state["catalogueRole"], "flagship")
        self.assertEqual(record.payload["course"]["catalogue_role"], "flagship")
        self.assertEqual(state["catalogueHook"], payload["course"]["catalogueHook"])
        self.assertEqual(state["problemStatement"], payload["course"]["problemStatement"])
        self.assertEqual(state["learningFocus"], payload["course"]["learningFocus"])
        self.assertEqual(state["whyThisOne"], payload["course"]["whyThisOne"])
        self.assertTrue(state["cataloguePresentationConfigured"])
        self.assertEqual(
            record.payload["course"]["catalogue_presentation"]["tags"],
            ["Chart reading", "zones", "invalidation"],
        )
        self.assertTrue(record.payload["course"]["catalogue_presentation_configured"])

    def test_existing_saved_builder_draft_can_be_resaved_when_course_slug_is_taken(self):
        slug = "builder-draft-slug-collision"
        first = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload(slug)),
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200, first.content)
        record_id = first.json()["record_id"]

        # Simulate a pre-existing Academy Course row with the same slug. Saving
        # the already-owned CourseImport draft must update that draft, not fail
        # the slug check or silently edit the existing Course.
        Course.objects.create(
            title="Existing Academy course",
            slug=slug,
            status=Course.Status.DRAFT,
        )
        payload = self.draft_payload(slug)
        payload["course"]["serverDraftId"] = record_id
        payload["course"]["summary"] = "Updated without changing the existing course."

        second = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(second.json()["record_id"], record_id)
        record = CourseImport.objects.get(pk=record_id)
        self.assertEqual(
            record.payload["builder_state"]["summary"],
            "Updated without changing the existing course.",
        )
        self.assertEqual(Course.objects.get(slug=slug).title, "Existing Academy course")

    def test_new_builder_draft_still_rejects_an_existing_course_slug(self):
        slug = "existing-academy-course-slug"
        Course.objects.create(
            title="Existing Academy course",
            slug=slug,
            status=Course.Status.DRAFT,
        )
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload(slug)),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("unique slug", response.json()["detail"])

    @override_settings(
        ACADEMY_GITHUB_ASSET_REPOSITORY="ZaphodBeeblebrox12/prototypeweb",
        ACADEMY_GITHUB_ASSET_TOKEN="test-token",
        ACADEMY_GITHUB_ASSET_BRANCH="my-new-branch",
    )
    @patch("apps.academy.course_builder_api.requests.put")
    @patch("apps.academy.course_builder_api.requests.get")
    def test_explicit_save_syncs_source_snapshot_to_existing_repo(self, github_get, github_put):
        github_get.return_value = Mock(status_code=404)
        github_put.return_value = Mock(status_code=201)
        github_put.return_value.json.return_value = {
            "content": {"sha": "blob-sha"},
            "commit": {"sha": "commit-sha"},
        }
        payload = self.draft_payload("github-source-course")
        payload["sync_source"] = True

        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["github_source_synced"])
        self.assertIn(
            "/course-source/builder-drafts/github-source-course.json",
            github_put.call_args.args[0],
        )
        saved_json = json.loads(base64.b64decode(github_put.call_args.kwargs["json"]["content"]))
        self.assertEqual(
            saved_json["modules"][0]["lessons"][0]["content_markdown"],
            "## Notice\n\nDescribe what is visible before drawing a conclusion.",
        )
        self.assertEqual(github_put.call_args.kwargs["json"]["branch"], "my-new-branch")

    def test_published_quiz_keeps_answer_key_private(self):
        from .importing import publish_course_import
        from .models import LessonInstructorMaterial

        payload = self.draft_payload("private-quiz-course")
        payload["mode"] = "submit"
        payload["sync_source"] = False
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        course = publish_course_import(record, user=self.admin)
        self.assertEqual(course.learning_outcomes, ["Describe evidence before interpreting it."])
        self.assertEqual(course.category, "Chart reading")
        lesson = Lesson.objects.get(module__course=course)
        self.assertEqual(lesson.content_json["video_url"], "https://media.example.test/lesson.mp4")
        self.assertEqual(lesson.content_json["notebook"]["prompts"][0]["label"], "Observe")

        self.assertEqual(lesson.content_json["questions"][0]["options"][0], "Visible evidence")
        self.assertNotIn("correctIndex", json.dumps(lesson.content_json))
        self.assertNotIn("explanation", json.dumps(lesson.content_json))
        instructor = LessonInstructorMaterial.objects.get(lesson=lesson)
        self.assertEqual(instructor.rubric_json["questions"][0]["correctIndex"], 0)
        self.assertIn("Start with what can be observed.", instructor.answer_key_markdown)

    def test_markdown_renderer_binding_is_declared_before_strict_mode_enhancements(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        source = response.content.decode("utf-8")
        declaration = source.index("let renderMarkdown;")
        first_assignment = source.index("  renderMarkdown = function(src)")
        self.assertIn("'use strict';", source)
        self.assertLess(declaration, first_assignment)
        self.assertIn("const baseMarkdownRenderer = renderMarkdown;", source)
        self.assertIn("const renderMarkdownWithFigures = renderMarkdown;", source)

    def test_preview_normalizes_legacy_browser_drafts_before_initial_render(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        source = response.content.decode("utf-8")
        self.assertIn("function normalizeLessonState(lesson, index)", source)
        self.assertIn("function normalizeCourseState(course)", source)
        self.assertIn("function normalizeLoadedState(value)", source)
        self.assertIn("let state=normalizeLoadedState(load());", source)
        self.assertIn("function renderEditorSafely()", source)
        self.assertIn("runRenderStep('editor', renderEditorSafely);", source)
        self.assertIn("const renderEditorWithAllEnhancements = renderEditor;", source)
        self.assertIn("renderEditorSafely = function()", source)
        self.assertIn("syncAcademy();", source)

    def test_preview_catalogue_distinguishes_loading_from_an_empty_public_catalogue(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        source = response.content.decode("utf-8")
        self.assertIn("let catalogueLoaded = false;", source)
        self.assertIn("Loading the published catalogue from the Academy…", source)
        self.assertIn("No published courses are ready for the catalogue yet.", source)

    def test_delete_draft_waits_for_initial_sync_and_checks_academy_before_local_only_removal(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        for marker in (
            "let academySyncPromise = null;",
            "academySyncPromise = syncAcademy();",
            "if (academySyncPromise && !academyReady)",
            "async function findAcademyDraftForDeletion(course, allowLegacySlugTitleFallback)",
            "String(remote.id || '') === courseId",
            "sameDraftModuleIdentity(remote, course)",
            "const remoteDraft = await findAcademyDraftForDeletion(course, staleServerDraft);",
            "The Academy did not confirm deletion of the saved draft.",
            "Local-only draft removed from this browser.",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)

    def test_delete_draft_reconciles_legacy_server_backed_browser_entries(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        source = response.content.decode("utf-8")
        self.assertIn(
            "const staleServerDraft = !course.serverDraftId && Boolean(course.serverUpdatedAt);",
            source,
        )
        self.assertIn("Deleting draft…", source)
        self.assertIn("Delete draft failed:", source)

    def test_published_course_edit_options_include_unready_courses_but_related_cards_do_not(self):
        placeholder = Course.objects.create(
            title="New micro-course draft",
            slug="new-micro-course-draft-placeholder",
            summary="Add a concise course promise here.",
            status=Course.Status.PUBLISHED,
        )
        placeholder_module = CourseModule.objects.create(
            course=placeholder,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=placeholder_module,
            title="Placeholder lesson",
            slug="placeholder-lesson",
            position=1,
            is_published=True,
            content_markdown="Placeholder content.",
        )
        course_without_published_lessons = Course.objects.create(
            title="Published course awaiting lessons",
            slug="published-course-awaiting-lessons",
            summary="A practical guide to reading market context.",
            status=Course.Status.PUBLISHED,
        )
        valid_course = Course.objects.create(
            title="Published course with real copy",
            slug="published-course-real-copy",
            summary="A practical introduction to reading market context.",
            status=Course.Status.PUBLISHED,
        )
        valid_module = CourseModule.objects.create(
            course=valid_course,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=valid_module,
            title="Read the context",
            slug="read-the-context",
            position=1,
            is_published=True,
            content_markdown="Read the context before acting.",
        )
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200, response.content)

        payload = response.json()
        edit_options = payload["published_course_options"]
        edit_option_ids = {str(item["id"]) for item in edit_options}
        self.assertIn(str(placeholder.pk), edit_option_ids)
        self.assertIn(str(course_without_published_lessons.pk), edit_option_ids)
        self.assertIn(str(valid_course.pk), edit_option_ids)

        # Editing options must not reuse the stricter learner-facing card list.
        related_ids = {str(item["id"]) for item in payload["related_courses"]}
        self.assertNotIn(str(placeholder.pk), related_ids)
        self.assertNotIn(str(course_without_published_lessons.pk), related_ids)
        self.assertIn(str(valid_course.pk), related_ids)

    def test_related_course_uses_published_course_uuid(self):
        related = Course.objects.create(
            title="Related published course",
            slug="related-published-course",
            summary="A useful related-course summary.",
            status=Course.Status.PUBLISHED,
        )
        related_module = CourseModule.objects.create(
            course=related,
            title="Related module",
            slug="related-module",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=related_module,
            title="Related lesson",
            slug="related-lesson",
            position=1,
            is_published=True,
            content_markdown="A related lesson.",
        )
        payload = self.draft_payload("course-with-related-reference")
        payload["course"]["modules"][0]["lessons"][0]["relatedCourseIds"] = [str(related.pk)]
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved = record.payload["modules"][0]["lessons"][0]["content_json"]["related_course_ids"]
        self.assertEqual(saved, [str(related.pk)])

    def test_builder_persists_stable_inline_lesson_reference_ids(self):
        destination = Course.objects.create(
            title="Volume and Price Analysis",
            slug="volume-price-analysis",
            summary="Read participation alongside price.",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=destination,
            title="Volume context",
            slug="volume-context",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Read relative volume",
            slug="read-relative-volume",
            position=1,
            is_published=True,
            is_preview=True,
            content_markdown="## Compare volume\n\nPrivate destination body is not copied.",
        )
        payload = self.draft_payload("course-with-inline-lesson-reference")
        payload["course"]["modules"][0]["lessons"][0]["content"] += f"\n\n[[lesson:{lesson.pk}]]"
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        self.assertEqual(
            saved_lesson["content_json"]["lesson_reference_ids"],
            [str(lesson.pk)],
        )
        self.assertNotIn("Private destination body", json.dumps(saved_lesson))

    def test_builder_catalogue_includes_only_published_lesson_destinations(self):
        course = Course.objects.create(
            title="Volume Profile",
            slug="volume-profile",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Value areas",
            slug="value-areas",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="Read the value area",
            slug="read-value-area",
            summary="Understand value migration and acceptance.",
            content_markdown="## Value area\n\nVolume profile helps describe acceptance.",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="Unpublished draft lesson",
            slug="draft-lesson",
            position=2,
            is_published=False,
        )
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200, response.content)
        references = response.json()["lesson_references"]
        self.assertEqual([item["title"] for item in references], ["Read the value area"])
        self.assertIn("Value area", references[0]["topics"])

    def test_notebook_reflections_are_saved_to_learner_progress(self):
        from .models import LessonProgress

        course = Course.objects.create(
            title="Notebook course",
            slug="notebook-course",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Module One",
            slug="module-one",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Lesson One",
            slug="lesson-one",
            position=1,
            is_preview=True,
            is_published=True,
            content_json={
                "notebook": {
                    "title": "Notebook",
                    "prompts": [{"label": "Observe", "text": "What is visible?"}],
                }
            },
        )
        response = self.client.post(
            reverse("academy:lesson-notebook-submit", args=[lesson.pk]),
            data={"prompt_0": "Price held the prior support zone."},
        )
        self.assertEqual(response.status_code, 200, response.content)
        progress = LessonProgress.objects.get(user=self.admin, lesson=lesson)
        self.assertEqual(
            progress.response_json["notebook_responses"],
            ["Price held the prior support zone."],
        )

    def test_bollinger_notebook_fallback_reflections_are_saved(self):
        from .models import LessonProgress

        course = Course.objects.create(
            title="Bollinger Notebook course",
            slug="understand-bollinger-bands",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Reading the bands",
            slug="reading-the-bands",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Before treating a touch as a setup",
            slug="before-treating-a-touch-as-a-setup",
            position=1,
            is_preview=True,
            is_published=True,
            content_json={},
        )

        response = self.client.post(
            reverse("academy:lesson-notebook-submit", args=[lesson.pk]),
            data={
                "prompt_0": "Price is between the middle and upper band.",
                "prompt_1": "It may be trending, but a range remains possible.",
                "prompt_2": "I will review the next close and the middle-line response.",
            },
        )

        self.assertEqual(response.status_code, 200, response.content)
        progress = LessonProgress.objects.get(user=self.admin, lesson=lesson)
        self.assertEqual(
            progress.response_json["notebook_responses"],
            [
                "Price is between the middle and upper band.",
                "It may be trending, but a range remains possible.",
                "I will review the next close and the middle-line response.",
            ],
        )

    def test_course_builder_is_not_available_to_regular_staff(self):
        staff = User.objects.create_user(
            username="ordinary-staff",
            password="test-password",
            role="staff",
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 403)

    def test_public_catalogue_includes_published_courses_only(self):
        published = Course.objects.create(
            title="Published API Course",
            slug="published-api-course",
            summary="A published course.",
            catalogue_role=Course.CatalogueRole.SUPPORTING,
            position=17,
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=published,
            title="Module One",
            slug="module-one",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="Lesson One",
            slug="lesson-one",
            position=1,
            content_markdown="A safe lesson body.",
            is_published=True,
        )
        Course.objects.create(
            title="Private Draft Course",
            slug="private-draft-course",
            status=Course.Status.DRAFT,
        )
        Course.objects.create(
            title="Intentionally Hidden Course",
            slug="intentionally-hidden-course",
            summary="Do not show this course on the public Courses page.",
            catalogue_role=Course.CatalogueRole.HIDDEN,
            status=Course.Status.PUBLISHED,
        )
        self.client.logout()
        response = self.client.get(reverse("academy_public_catalogue"))
        self.assertEqual(response.status_code, 200)
        rows = response.json()["courses"]
        titles = [item.get("title") for item in rows if item.get("title")]
        self.assertIn("Published API Course", titles)
        self.assertNotIn("Private Draft Course", titles)
        published_row = next(item for item in rows if item.get("slug") == published.slug)
        self.assertEqual(published_row["catalogueRole"], "supporting")
        self.assertEqual(published_row["catalogueOrder"], 17)
        hidden_row = next(item for item in rows if item.get("slug") == "intentionally-hidden-course")
        self.assertEqual(hidden_row["catalogueRole"], "hidden")
        self.assertEqual(hidden_row["status"], "hidden")
        self.assertNotIn("title", hidden_row)
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_published_course_editor_hydrates_saved_question_image_url(self):
        from .course_builder_api import _builder_state_from_published_course

        course = Course.objects.create(
            title="Published Image Course",
            slug="published-image-course",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Module One",
            slug="module-one",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Lesson One",
            slug="lesson-one",
            position=1,
            is_published=True,
            content_json={
                "questions": [
                    {
                        "id": "question-chart",
                        "prompt": "What does this chart show?",
                        "options": ["Rejection", "Breakout"],
                        "image_asset_id": "",
                    }
                ]
            },
        )
        asset = CourseMediaAsset.objects.create(
            course=course,
            asset_key="builder/question-chart",
            file="academy/course-media/question-chart.png",
            alt_text="Price rejecting resistance",
        )
        lesson.content_json = {
            "asset_ids": [str(asset.pk)],
            "figures": {
                str(asset.pk): {
                    "title": "Resistance test",
                    "alt": "Price rejecting resistance",
                    "caption": "Compare the closes near resistance.",
                }
            },
            "questions": [
                {
                    "id": "question-chart",
                    "prompt": "What does this chart show?",
                    "options": ["Rejection", "Breakout"],
                    "image_asset_id": str(asset.pk),
                }
            ],
        }
        lesson.save(update_fields=["content_json", "updated_at"])

        state = _builder_state_from_published_course(course)
        hydrated_lesson = state["modules"][0]["lessons"][0]
        question = hydrated_lesson["questions"][0]
        hydrated_image = next(
            image for image in hydrated_lesson["images"] if image["id"] == str(asset.pk)
        )

        self.assertEqual(question["imageId"], str(asset.pk))
        self.assertEqual(hydrated_image["data"], reverse("academy:media-asset", args=[asset.pk]))
        self.assertEqual(hydrated_image["title"], "Resistance test")
        self.assertEqual(hydrated_image["alt"], "Price rejecting resistance")

    def test_builder_question_image_is_saved_as_learner_safe_figure_reference(self):
        from .course_builder_api import _asset_uuid, _build_import_payload

        state = self.draft_payload("builder-question-image")["course"]
        lesson = state["modules"][0]["lessons"][0]
        image_id = "question-chart-01"
        lesson["images"] = [
            {
                "id": image_id,
                "name": "resistance-chart.png",
                "title": "Repeated resistance test",
                "alt": "Price testing the same resistance area three times",
                "caption": "Notice the closes around the marked zone.",
                "data": "data:image/png;base64,"
                + base64.b64encode(b"fake image bytes").decode("ascii"),
            }
        ]
        lesson["image"] = lesson["images"][0]
        lesson["questions"][0]["imageId"] = image_id

        imported, image_sources = _build_import_payload(state, "builder-question-image")
        saved_lesson = imported["modules"][0]["lessons"][0]
        stable_id = _asset_uuid("builder-question-image", image_id)
        question = saved_lesson["content_json"]["questions"][0]

        self.assertEqual(question["image_asset_id"], stable_id)
        self.assertIn(stable_id, saved_lesson["content_json"]["asset_ids"])
        self.assertEqual(
            saved_lesson["content_json"]["figures"][stable_id],
            {
                "title": "Repeated resistance test",
                "alt": "Price testing the same resistance area three times",
                "caption": "Notice the closes around the marked zone.",
            },
        )
        self.assertIn("builder/" + image_id, image_sources)
        self.assertNotIn("correctIndex", json.dumps(saved_lesson["content_json"]))
        self.assertNotIn("explanation", json.dumps(saved_lesson["content_json"]))

    def test_practice_question_image_hydration_uses_resolved_asset_url(self):
        from .views import _practice_questions_with_images

        questions = [
            {
                "id": "question-1",
                "prompt": "What does this chart show?",
                "options": ["A", "B"],
                "image_asset_id": "asset-uuid",
            }
        ]
        hydrated = _practice_questions_with_images(
            questions,
            {"asset-uuid": "/academy/media/asset-uuid/"},
            {
                "asset-uuid": {
                    "title": "Chart A",
                    "alt": "A price chart",
                    "caption": "Look at the retest.",
                }
            },
        )

        self.assertEqual(hydrated[0]["image_url"], "/academy/media/asset-uuid/")
        self.assertEqual(hydrated[0]["image_title"], "Chart A")
        self.assertEqual(hydrated[0]["image_alt"], "A price chart")
        self.assertEqual(hydrated[0]["image_caption"], "Look at the retest.")
        self.assertNotIn("image_url", questions[0])

    def test_builder_preserves_inline_figure_metadata_with_stable_asset_id(self):
        from .course_builder_api import _build_import_payload

        state = self.draft_payload("builder-figure-contract")["course"]
        lesson = state["modules"][0]["lessons"][0]
        image_id = "builder-image-01"
        caption = "Compare one setting at a time before making a judgement."
        lesson["content"] = (
            "Text before the figure.\n\n"
            f"![Band comparison](asset://{image_id})\n\n"
            "Text after the figure."
        )
        lesson["images"] = [
            {
                "id": image_id,
                "name": "band-comparison.png",
                "title": "What changing the settings changes",
                "alt": "Three cards compare shorter, baseline and longer Bollinger Band windows.",
                "caption": caption,
                "data": "data:image/png;base64,"
                + base64.b64encode(b"fake image bytes").decode("ascii"),
            }
        ]
        lesson["image"] = lesson["images"][0]

        imported, image_sources = _build_import_payload(state, "builder-figure-contract")
        saved_lesson = imported["modules"][0]["lessons"][0]
        figure_map = saved_lesson["content_json"]["figures"]
        self.assertEqual(len(figure_map), 1)
        stable_id, metadata = next(iter(figure_map.items()))
        self.assertEqual(metadata["title"], "What changing the settings changes")
        self.assertEqual(
            metadata["alt"],
            "Three cards compare shorter, baseline and longer Bollinger Band windows.",
        )
        self.assertEqual(metadata["caption"], caption)
        self.assertIn(f"asset://{stable_id}", saved_lesson["content_markdown"])
        self.assertIn(stable_id, saved_lesson["content_json"]["asset_ids"])
        self.assertNotIn(caption, saved_lesson["content_markdown"])
        self.assertIn("Text before the figure.", saved_lesson["content_markdown"])
        self.assertIn("Text after the figure.", saved_lesson["content_markdown"])
        self.assertIn("builder/builder-image-01", image_sources)

    def test_builder_persists_titled_image_groups_with_stable_asset_ids(self):
        from .course_builder_api import _build_import_payload

        state = self.draft_payload("builder-image-group")["course"]
        lesson = state["modules"][0]["lessons"][0]
        first_id = "builder-image-long"
        second_id = "builder-image-near-miss"
        group_id = "image-group-method-two"
        source = (
            "Introduce the comparison.\n\n"
            f"[[image-group:{group_id}]]\n\n"
            "Explain what differs between the cases."
        )
        lesson["content"] = source
        lesson["images"] = [
            {
                "id": first_id,
                "name": "chart-long-candidate.png",
                "title": "Long candidate",
                "alt": "Price rises alongside the upper band.",
                "caption": "Both conditions must hold.",
                "data": "data:image/png;base64,"
                + base64.b64encode(b"fake first image").decode("ascii"),
            },
            {
                "id": second_id,
                "name": "chart-near-miss.png",
                "title": "Near miss",
                "alt": "Price moves sideways while one condition fails.",
                "caption": "One condition is not met.",
                "data": "data:image/png;base64,"
                + base64.b64encode(b"fake second image").decode("ascii"),
            },
        ]
        lesson["image"] = lesson["images"][0]
        lesson["imageGroups"] = [
            {
                "id": group_id,
                "title": "Method II: price position and money flow",
                "imageIds": [first_id, second_id],
                "note": "Read both inputs together.",
            }
        ]

        imported, image_sources = _build_import_payload(state, "builder-image-group")
        saved_lesson = imported["modules"][0]["lessons"][0]
        figure_map = saved_lesson["content_json"]["figures"]
        group = figure_map[group_id]
        asset_ids = saved_lesson["content_json"]["asset_ids"]
        self.assertEqual(saved_lesson["content_markdown"], source)
        self.assertEqual(group["type"], "image-group")
        self.assertEqual(group["title"], "Method II: price position and money flow")
        self.assertEqual(group["note"], "Read both inputs together.")
        self.assertEqual(len(group["image_ids"]), 2)
        self.assertIn("builder/" + first_id, image_sources)
        self.assertIn("builder/" + second_id, image_sources)
        self.assertTrue(set(group["image_ids"]).issubset(set(asset_ids)))
        self.assertEqual(figure_map[group["image_ids"][0]]["title"], "Long candidate")
        self.assertEqual(figure_map[group["image_ids"][1]]["title"], "Near miss")
        self.assertNotIn("chart-long-candidate.png", group["title"])
        self.assertNotIn("Purpose-built teaching aid", saved_lesson["content_markdown"])

    def test_legacy_filename_title_is_cleared_when_cleaning_image_metadata(self):
        from .course_builder_api import _clean_image_payload

        state = self.draft_payload("builder-filename-title")["course"]
        lesson = state["modules"][0]["lessons"][0]
        lesson["images"] = [
            {
                "id": "legacy-image",
                "name": "BANKNIFTY_2023-08-06_16-51-56_bd975.png",
                "title": "BANKNIFTY_2023-08-06_16-51-56_bd975.png",
                "alt": "BANKNIFTY price chart",
                "caption": "",
                "data": "",
            }
        ]
        cleaned, _image_sources, _asset_specs = _clean_image_payload(
            state, "builder-filename-title"
        )
        cleaned_image = cleaned["modules"][0]["lessons"][0]["images"][0]
        self.assertEqual(cleaned_image["title"], "")
        self.assertEqual(cleaned_image["name"], "BANKNIFTY_2023-08-06_16-51-56_bd975.png")

    def test_builder_persists_grouped_header_table_metadata_losslessly(self):
        payload = self.draft_payload("builder-grouped-table")
        lesson = payload["course"]["modules"][0]["lessons"][0]
        lesson["content"] = (
            "Introductory text.\n\n" "[[table-block:market-comparison]]\n\n" "Follow-up text."
        )
        lesson["tables"] = {
            "market-comparison": {
                "title": "Market comparison",
                "rows": [
                    {
                        "section": "head",
                        "cells": [
                            {"text": "Context", "colspan": 2, "rowspan": 1, "header": True},
                            {"text": "Decision", "colspan": 2, "rowspan": 1, "header": True},
                        ],
                    },
                    {
                        "section": "head",
                        "cells": [
                            {"text": "Market", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "Evidence", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "Confirmed", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "Rejected", "colspan": 1, "rowspan": 1, "header": True},
                        ],
                    },
                    {
                        "section": "body",
                        "cells": [
                            {"text": "Range", "colspan": 1, "rowspan": 1, "header": False},
                            {
                                "text": "Repeated rejection",
                                "colspan": 1,
                                "rowspan": 1,
                                "header": False,
                            },
                            {
                                "text": "Wait for follow-through",
                                "colspan": 1,
                                "rowspan": 1,
                                "header": False,
                            },
                            {
                                "text": "Reassess the range",
                                "colspan": 1,
                                "rowspan": 1,
                                "header": False,
                            },
                        ],
                    },
                ],
            },
        }
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        saved_table = saved_lesson["content_json"]["tables"]["market-comparison"]
        self.assertEqual(saved_table["title"], "Market comparison")
        self.assertEqual(saved_table["rows"][0]["cells"][0]["colspan"], 2)
        self.assertEqual(saved_table["rows"][1]["cells"][2]["text"], "Confirmed")
        self.assertEqual(saved_lesson["content_markdown"], lesson["content"])

    def test_builder_accepts_rowspans_in_the_option_five_table_header(self):
        payload = self.draft_payload("builder-option-five-rowspan-table")
        lesson = payload["course"]["modules"][0]["lessons"][0]
        lesson["content"] = "Before the table.\n\n[[table-block:ohlc-context]]\n\nAfter the table."
        lesson["tables"] = {
            "ohlc-context": {
                "title": "From observation to execution",
                "rows": [
                    {
                        "section": "head",
                        "cells": [
                            {"text": "Price structure", "colspan": 4, "rowspan": 1, "header": True},
                            {"text": "Volume", "colspan": 1, "rowspan": 2, "header": True},
                            {"text": "Context", "colspan": 1, "rowspan": 2, "header": True},
                        ],
                    },
                    {
                        "section": "head",
                        "cells": [
                            {"text": "Open", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "High", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "Low", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "Close", "colspan": 1, "rowspan": 1, "header": True},
                        ],
                    },
                    {
                        "section": "body",
                        "cells": [
                            {"text": "Breakout", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Above range", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Activity rises", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Close holds", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Strong", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Trend", "colspan": 1, "rowspan": 1, "header": False},
                        ],
                    },
                ],
            },
        }

        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved_table = record.payload["modules"][0]["lessons"][0]["content_json"]["tables"][
            "ohlc-context"
        ]
        self.assertEqual(saved_table["rows"][0]["cells"][1]["rowspan"], 2)
        self.assertEqual(saved_table["rows"][0]["cells"][2]["text"], "Context")
        self.assertEqual(saved_table["rows"][1]["cells"][3]["text"], "Close")
        self.assertEqual(len(saved_table["rows"][2]["cells"]), 6)

    def test_builder_persists_native_comparison_figures_by_stable_token(self):
        from .course_builder_api import _build_import_payload

        state = self.draft_payload("builder-native-figure")["course"]
        lesson = state["modules"][0]["lessons"][0]
        figure_id = "figure-block-01"
        source = (
            "Text before the comparison.\n\n"
            f"[[teaching-figure:{figure_id}]]\n\n"
            "Text after the comparison."
        )
        lesson["content"] = source
        lesson["teachingFigures"] = [
            {
                "id": figure_id,
                "type": "comparison-cards",
                "title": "What changing the settings changes",
                "cards": [
                    {
                        "kicker": "SHORTER WINDOW",
                        "title": "More responsive",
                        "body": "Reacts to fewer recent bars.",
                    },
                    {
                        "kicker": "20 PERIODS · 2 DEVIATIONS",
                        "title": "Common baseline",
                        "body": "A reference, not a law.",
                    },
                    {
                        "kicker": "LONGER WINDOW",
                        "title": "More smoothed",
                        "body": "Usually reacts more slowly.",
                    },
                ],
                "note": "Compare one setting at a time.",
            }
        ]

        imported, image_sources = _build_import_payload(state, "builder-native-figure")
        saved_lesson = imported["modules"][0]["lessons"][0]
        self.assertEqual(saved_lesson["content_markdown"], source)
        self.assertEqual(image_sources, {})
        figure = saved_lesson["content_json"]["figures"][figure_id]
        self.assertEqual(figure["type"], "comparison-cards")
        self.assertEqual(figure["title"], "What changing the settings changes")
        self.assertEqual(figure["cards"][0]["kicker"], "SHORTER WINDOW")
        self.assertEqual(figure["cards"][1]["title"], "Common baseline")
        self.assertEqual(figure["cards"][2]["title"], "More smoothed")
        self.assertEqual(figure["note"], "Compare one setting at a time.")

    def test_admin_can_delete_saved_builder_draft_and_it_disappears_from_the_list(self):
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload("builder-delete-course")),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record_id = saved.json()["record_id"]
        self.assertTrue(CourseImport.objects.filter(pk=record_id).exists())

        deleted = self.client.delete(
            reverse("staff_course_builder_api"),
            data=json.dumps({"serverDraftId": record_id}),
            content_type="application/json",
        )
        self.assertEqual(deleted.status_code, 200, deleted.content)
        self.assertEqual(deleted.json()["deleted_id"], record_id)
        record = CourseImport.objects.get(pk=record_id)
        self.assertEqual(record.status, CourseImport.Status.DELETED)

        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertNotIn(
            record_id, [draft["serverDraftId"] for draft in refreshed.json()["drafts"]]
        )

    def test_course_builder_delete_does_not_remove_a_submitted_review_item(self):
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload("builder-delete-review-guard")),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record = CourseImport.objects.get(pk=saved.json()["record_id"])
        record.status = CourseImport.Status.REVIEW
        record.save(update_fields=["status"])

        deleted = self.client.delete(
            reverse("staff_course_builder_api"),
            data=json.dumps({"serverDraftId": str(record.pk)}),
            content_type="application/json",
        )
        self.assertEqual(deleted.status_code, 404)
        self.assertTrue(CourseImport.objects.filter(pk=record.pk).exists())

    def test_stale_browser_copy_cannot_recreate_a_deleted_builder_draft(self):
        payload = self.draft_payload("builder-delete-stale-copy")
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record_id = saved.json()["record_id"]

        deleted = self.client.delete(
            reverse("staff_course_builder_api"),
            data=json.dumps({"serverDraftId": record_id}),
            content_type="application/json",
        )
        self.assertEqual(deleted.status_code, 200, deleted.content)

        # Simulate a second open tab that still holds the old serverDraftId.
        payload["course"]["serverDraftId"] = record_id
        stale_save = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(stale_save.status_code, 410, stale_save.content)
        self.assertTrue(stale_save.json()["draft_deleted"])
        self.assertEqual(
            CourseImport.objects.get(pk=record_id).status,
            CourseImport.Status.DELETED,
        )
        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertNotIn(
            record_id,
            [draft["serverDraftId"] for draft in refreshed.json()["drafts"]],
        )

    def test_get_retires_legacy_builder_draft_after_course_was_deleted_in_admin(self):
        payload = self.draft_payload()
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record_id = saved.json()["record_id"]
        record = CourseImport.objects.get(pk=record_id)

        course = Course.objects.create(
            title=payload["course"]["title"],
            slug=payload["course"]["slug"],
            status=Course.Status.PUBLISHED,
        )
        LogEntry.objects.create(
            user=self.admin,
            content_type=ContentType.objects.get_for_model(Course),
            object_id=str(course.pk),
            object_repr=course.title,
            action_flag=DELETION,
            change_message="Deleted course in Django Admin",
        )
        # Simulate a legacy deletion that happened before the new CourseAdmin
        # cleanup hook was deployed.
        Course.objects.filter(pk=course.pk).delete()

        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertNotIn(
            record_id, [draft["serverDraftId"] for draft in refreshed.json()["drafts"]]
        )
        record.refresh_from_db()
        self.assertEqual(record.status, CourseImport.Status.DELETED)

    def test_published_course_can_be_loaded_into_builder_as_a_separate_review_revision(self):
        course = Course.objects.create(
            title="Published Edit Course",
            slug="published-edit-course",
            summary="Live summary",
            description="Live description",
            category="Chart reading",
            level="Intermediate",
            estimated_duration="Self-paced",
            learning_outcomes=["Keep a written process."],
            position=7,
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Foundations",
            slug="foundations",
            description="Live module description",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Lesson One",
            slug="lesson-one",
            summary="Live lesson summary",
            format="reading",
            content_markdown="## Live lesson\n\nOriginal published lesson content.\n\n[[table-block:table-live]]",
            content_json={
                "schema_version": 1,
                "source_id": "1.1",
                "asset_ids": [],
                "figures": {},
                "tables": {
                    "table-live": {
                        "title": "Grouped comparison",
                        "rows": [
                            {
                                "section": "head",
                                "cells": [
                                    {"text": "Context", "colspan": 2, "rowspan": 1, "header": True}
                                ],
                            },
                            {
                                "section": "head",
                                "cells": [
                                    {"text": "Market", "colspan": 1, "rowspan": 1, "header": True},
                                    {
                                        "text": "Response",
                                        "colspan": 1,
                                        "rowspan": 1,
                                        "header": True,
                                    },
                                ],
                            },
                            {
                                "section": "body",
                                "cells": [
                                    {"text": "Range", "colspan": 1, "rowspan": 1, "header": False},
                                    {"text": "Wait", "colspan": 1, "rowspan": 1, "header": False},
                                ],
                            },
                        ],
                    }
                },
                "related_course_ids": [],
                "questions": [
                    {
                        "id": "question-live",
                        "prompt": "Which option is correct?",
                        "options": ["First option", "Second option"],
                    }
                ],
                "notebook": {"title": "My notebook", "prompts": []},
                "video_url": "",
            },
            position=1,
            is_published=True,
        )
        LessonInstructorMaterial.objects.create(
            lesson=lesson,
            rubric_json={
                "questions": [
                    {
                        "id": "question-live",
                        "prompt": "Which option is correct?",
                        "options": ["First option", "Second option"],
                        "correctIndex": 1,
                        "explanation": "The second option matches the evidence.",
                        "imageId": "",
                    }
                ]
            },
        )
        loaded = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"action": "begin_edit_published_course", "courseId": str(course.pk)}),
            content_type="application/json",
        )
        self.assertEqual(loaded.status_code, 200, loaded.content)
        state = loaded.json()["course"]
        self.assertEqual(state["serverCourseId"], str(course.pk))
        self.assertEqual(state["modules"][0]["id"], str(module.pk))
        self.assertEqual(state["modules"][0]["lessons"][0]["id"], str(lesson.pk))
        self.assertEqual(
            state["modules"][0]["lessons"][0]["content"],
            "## Live lesson\n\nOriginal published lesson content.\n\n[[table-block:table-live]]",
        )
        self.assertEqual(
            state["modules"][0]["lessons"][0]["tables"]["table-live"]["rows"][0]["cells"][0][
                "colspan"
            ],
            2,
        )
        self.assertEqual(state["modules"][0]["lessons"][0]["questions"][0]["correctIndex"], 1)

        state["summary"] = "Revised summary"
        state["modules"][0]["lessons"][0][
            "content"
        ] = "## Live lesson\n\nReviewed replacement content."
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"course": state, "mode": "save", "sync_source": False}),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record = CourseImport.objects.get(pk=saved.json()["record_id"])
        self.assertEqual(record.target_course_id, course.pk)
        course.refresh_from_db()
        lesson.refresh_from_db()
        self.assertEqual(course.summary, "Live summary")
        self.assertIn("Original published lesson content.", lesson.content_markdown)
        self.assertEqual(record.status, CourseImport.Status.DRAFT)

        revision_state = saved.json()["draft"]
        revision_state["summary"] = "Revised summary"
        revision_state["modules"][0]["lessons"][0][
            "content"
        ] = "## Live lesson\n\nReviewed replacement content."
        submitted = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"course": revision_state, "mode": "submit", "sync_source": False}),
            content_type="application/json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        record.refresh_from_db()
        self.assertEqual(record.target_course_id, course.pk)
        self.assertEqual(record.status, CourseImport.Status.REVIEW)

        from .importing import publish_course_import

        published_again = publish_course_import(record, user=self.admin)
        self.assertEqual(published_again.pk, course.pk)
        self.assertEqual(Course.objects.filter(slug="published-edit-course").count(), 1)
        self.assertEqual(Course.objects.get(pk=course.pk).summary, "Revised summary")
        self.assertEqual(CourseModule.objects.get(pk=module.pk).pk, module.pk)
        self.assertEqual(
            Lesson.objects.get(pk=lesson.pk).content_markdown,
            "## Live lesson\n\nReviewed replacement content.",
        )
        self.assertEqual(
            CourseImport.objects.get(pk=record.pk).status, CourseImport.Status.PUBLISHED
        )

    def test_public_catalogue_hides_published_placeholder_and_uses_description_fallback(self):
        placeholder = Course.objects.create(
            title="Untitled course",
            slug="untitled-course-catalogue-regression",
            summary="Add a concise course promise here.",
            description="Describe the learner, what the course covers and what they can practise after completing it.",
            status=Course.Status.PUBLISHED,
        )
        placeholder_module = CourseModule.objects.create(
            course=placeholder,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=placeholder_module,
            title="Placeholder lesson",
            slug="placeholder-lesson",
            position=1,
            is_published=True,
            content_markdown="Placeholder content.",
        )
        valid = Course.objects.create(
            title="Volume and Price Analysis",
            slug="volume-and-price-analysis-description-fallback",
            summary="",
            description="A practical guide to comparing effort with result.",
            status=Course.Status.PUBLISHED,
        )
        valid_module = CourseModule.objects.create(
            course=valid,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=valid_module,
            title="Read the evidence",
            slug="read-the-evidence",
            position=1,
            is_published=True,
            content_markdown="Read the evidence before acting.",
        )

        self.client.logout()
        response = self.client.get(reverse("academy_public_catalogue"))

        self.assertEqual(response.status_code, 200, response.content)
        courses = response.json()["courses"]
        titles = [item["title"] for item in courses if item["status"] == "published"]
        self.assertNotIn("Untitled course", titles)
        valid_item = next(item for item in courses if item["slug"] == valid.slug)
        self.assertEqual(valid_item["description"], valid.description[:360])

    def test_coming_soon_catalogue_entry_exposes_only_announcement_metadata(self):
        CourseImport.objects.create(
            course_slug="coming-soon-options-course",
            title="Options Course",
            manifest_version="course-builder-v1",
            content_hash="a" * 64,
            source_manifest="builder://coming-soon-options-course",
            status=CourseImport.Status.DRAFT,
            payload={
                "builder_state": {
                    "title": "Options Course",
                    "slug": "coming-soon-options-course",
                    "summary": "A practical options course is nearly ready.",
                    "description": "A longer internal draft description.",
                    "category": "Options",
                    "level": "Intermediate",
                    "comingSoon": True,
                },
                "modules": [
                    {
                        "title": "Secret module title",
                        "lessons": [
                            {
                                "title": "Private lesson body",
                                "content_markdown": "PRIVATE LESSON TEXT THAT MUST NOT LEAK",
                                "instructor_material": {
                                    "questions": [{"prompt": "SECRET ANSWER KEY"}]
                                },
                            }
                        ],
                    }
                ],
            },
        )
        self.client.logout()
        response = self.client.get(reverse("academy_public_catalogue"))
        self.assertEqual(response.status_code, 200, response.content)
        teaser = next(
            item for item in response.json()["courses"] if item["status"] == "coming-soon"
        )
        self.assertEqual(teaser["title"], "Options Course")
        self.assertEqual(teaser["description"], "A practical options course is nearly ready.")
        self.assertEqual(teaser["modules"][0]["title"], "Course outline")
        body = json.dumps(teaser)
        self.assertNotIn("PRIVATE LESSON TEXT", body)
        self.assertNotIn("SECRET ANSWER KEY", body)
        self.assertNotIn("Secret module title", body)


    def test_get_offers_trading_path_as_a_one_time_shared_draft_candidate(self):
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200)
        candidate = response.json().get("trading_path_import_candidate")
        self.assertIsInstance(candidate, dict)
        self.assertEqual(candidate["course"]["title"], "Your Trading Path")
        self.assertEqual(len(candidate["course"]["modules"]), 5)
        self.assertEqual(
            sum(len(module["lessons"]) for module in candidate["course"]["modules"]),
            48,
        )

    def test_get_does_not_offer_trading_path_again_after_a_draft_exists(self):
        CourseImport.objects.create(
            course_slug="your-trading-path-import-draft",
            title="Your Trading Path",
            manifest_version="course-builder-v1",
            content_hash="a" * 64,
            source_manifest="builder://your-trading-path-import-draft",
            payload={"builder_state": {"title": "Your Trading Path"}},
            status=CourseImport.Status.DRAFT,
            imported_by=self.admin,
        )
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json().get("trading_path_import_candidate"))


    def test_support_resistance_import_includes_six_modules_eighteen_lessons_and_safe_charts(self):
        response = self.client.get(
            reverse("staff_course_builder_preview"),
            {"import": "support-resistance"},
        )
        self.assertEqual(response.status_code, 200, response.content[:1000])
        document = response.content.decode("utf-8")
        match = re.search(
            r'<script type="application/json" id="courseBuilderImportedDraft">(.*?)</script>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "The bundled draft payload should be injected for import.")
        payload = json.loads(match.group(1))
        course = payload["course"]
        self.assertEqual(course["slug"], "support-resistance-draft")
        self.assertEqual(course["status"], "draft")
        self.assertEqual(len(course["modules"]), 6)
        self.assertEqual(
            sum(len(module["lessons"]) for module in course["modules"]),
            18,
        )
        lesson_body = json.dumps(course, ensure_ascii=False)
        self.assertNotIn("ChartLab", lesson_body)
        self.assertIn("genuine instructor trade record", lesson_body)
        self.assertIn("authentic failed or invalidated thesis", lesson_body)
        self.assertIn("Stage 6 — Exit and outcome", lesson_body)
        self.assertIn("Alternative case — the decision to stand aside", lesson_body)
        self.assertIn("assessment and rubric remain a draft", lesson_body)
        hydrated_images = [
            image
            for module in course["modules"]
            for lesson in module["lessons"]
            for image in lesson.get("images", [])
        ]
        self.assertGreaterEqual(len(hydrated_images), 18)
        self.assertTrue(all(image["data"].startswith("data:image/png;base64,") for image in hydrated_images))
        self.assertTrue(all(image["id"].startswith("sr-") for image in hydrated_images))
        self.assertNotIn("imageRefs", lesson_body)
        self.assertIsNone(course["publishedSnapshot"])

class CourseBuilderPreviewWiringTests(SimpleTestCase):
    def test_empty_notebook_prompts_are_materialized_as_editable_pause_interpret_apply_fields(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        for marker in (
            "l.notebook.prompts.length===0",
            "{label:'Pause',text:'What evidence is visible?'}",
            "{label:'Interpret',text:'What could it mean in context?'}",
            "{label:'Apply',text:'What would change your view?'}",
            'data-entity="notebook-prompt"',
            "Prompt text",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)

    def test_builder_auto_imports_trading_path_from_shared_candidate(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        for marker in (
            "result.trading_path_import_candidate",
            "autoImportedTradingPath",
            "Your Trading Path is now in Your courses as an editable draft.",
            "await saveCurrentToAcademy(false, false)",
            "state.tab = 'curriculum';",
            "state.tradingPathOutlineAutoOpened = true;",
            "selectedTradingPath && !state.tradingPathOutlineAutoOpened",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)


    def test_support_resistance_import_uses_shared_draft_save_flow_without_publishing(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        for marker in (
            "supportResistanceImportRequested",
            "requestedSupportResistanceDraft",
            "clearSupportResistanceImportQuery()",
            "result.drafts",
            "!supportResistanceImportRequested && candidateCourse",
            "await saveCurrentToAcademy(false, false)",
            "Imported Support & Resistance as an editable 18-lesson draft. Nothing was published.",
            "Opened the existing Support & Resistance draft. No duplicate was created or published.",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)

    def test_legacy_regional_block_tab_is_removed_but_country_selector_remains(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")

        # The block-level editor tab is retired in favour of the whole-lesson
        # country/region selector. Legacy block persistence and rendering remain
        # available so older drafts and published lessons retain their content.
        for retired_marker in (
            "['regional','Regional content']",
            "else if(tab==='regional')panel=regionalFields(l);",
            "function regionalFields(lesson)",
            "case'add-regional-block':",
            "case'add-regional-variant':",
            "case'remove-regional-block':",
            "case'remove-regional-variant':",
            "case'insert-regional-block':",
            "case'insert-regional-image':",
            "if (el.matches('[data-regional-variant][data-field]'))",
        ):
            with self.subTest(marker=retired_marker):
                self.assertNotIn(retired_marker, source)

        self.assertNotIn(
            "['overview', 'curriculum', 'lesson', 'questions', 'media', 'reflection', 'regional', 'preview'].includes(normalized.tab)",
            source,
        )
        self.assertIn("lessonContentAudienceSelect", source)
        self.assertIn("function lessonBodyAudienceControlsMarkup(lesson)", source)
        self.assertIn("function setLessonBodyForAudience(lesson, content, audience)", source)
        self.assertIn('data-action="start-regional-lesson-content"', source)
        self.assertIn("previewAudienceSelect", source)
        self.assertIn("Use Figures for charts and the country/region audience selector above for full-lesson variations.", source)
        self.assertNotIn("Regional content for country or region differences", source)

    def test_local_autosave_is_not_suppressed_by_legacy_preview_view_state(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        start = source.index("function schedulePersist(){")
        end = source.index("function renderHeaderState()", start)
        schedule_persist = source[start:end]

        self.assertNotIn("state.view==='preview'", schedule_persist)
        self.assertIn("saveTimer=setTimeout(()=>{persist(false)", schedule_persist)

    def test_new_course_buttons_use_responsive_capture_phase_handler(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        self.assertIn(
            """const button=target?.closest(\'#newCourseButton, [data-action="new-course"]\');""",
            source,
        )
        self.assertIn(
            "event.stopImmediatePropagation();createNewCourseDraft(button);},true);", source
        )
        self.assertIn("trigger.textContent = 'Creating course…';", source)
        self.assertIn("markDirty();", source)
        self.assertIn("renderEditor();", source)
        self.assertIn("New draft created. Add details and save when ready.", source)
        self.assertIn("Could not open a new course. Please try again.", source)
        self.assertNotIn(
            "$('#newCourseButton').addEventListener('click',event=>handleAction('new-course',event.currentTarget));",
            source,
        )

    def test_course_builder_uses_site_native_dialogs_instead_of_browser_prompt_apis(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\b(?:window\.)?(?:alert|confirm|prompt)\s*\(")
        for marker in (
            'id="builderDialogBackdrop"',
            'role="dialog"',
            'aria-modal="true"',
            "async function builderConfirm(message, options = {})",
            "async function builderPrompt(message, defaultValue = '', options = {})",
            "event.key === 'Escape'",
            "builderDialogElement.querySelectorAll",
            "confirmLabel:'Delete draft'",
            "confirmLabel:'Save and leave'",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)

    def test_builder_diagnostics_capture_startup_render_and_api_phases_locally(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        for marker in (
            "window.__TRADETHESIS_COURSE_BUILDER_DIAGNOSTICS",
            "window.addEventListener('error'",
            "window.addEventListener('unhandledrejection'",
            "diagnosticStage('browser-state-normalization-started')",
            "runRenderStep('sidebar', renderSidebar)",
            "runRenderStep('editor', renderEditorSafely)",
            "runRenderStep('catalogue', renderCatalogue)",
            "diagnosticError('editor-render', error)",
            "diagnosticStage('api-fetch-started'",
            "diagnosticStage('api-response-received'",
            "diagnosticStage('api-response-parsed'",
            "diagnosticStage('academy-sync-started'",
            "diagnosticStage('academy-sync-complete'",
            "diagnosticError('academy-sync-failed', error)",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)
        self.assertIn("requestDiagnostic.payloadKeys", source)
        self.assertIn("requestDiagnostic.payloadSummary", source)
        self.assertNotIn("fetch('/staff/course-builder/diagnostics", source)

    def test_builder_preview_routes_selected_lesson_to_academy_template(self):
        source = Path(__file__).with_name("course_builder_preview.html").read_text(encoding="utf-8")
        self.assertIn("data-builder-website-preview-frame", source)
        self.assertIn(
            "previewUrl.searchParams.set('lesson', String(moduleIndex + 1) + '.' + String(lessonIndex + 1));",
            source,
        )
        self.assertIn("previewUrl.searchParams.set('preview_audience'", source)
        self.assertIn("async function refreshBuilderWebsitePreview(force = false)", source)
        self.assertNotIn('class="module-name-eyebrow"', source)

    def test_module_title_is_rendered_in_both_academy_lesson_templates(self):
        backend_root = Path(__file__).resolve().parents[2]
        lesson_template = (backend_root / "templates" / "academy" / "lesson.html").read_text(
            encoding="utf-8"
        )
        website_preview = (
            backend_root / "templates" / "academy" / "course_import_website_preview.html"
        ).read_text(encoding="utf-8")
        # Normalize whitespace so Black's wrapping does not break this template-wiring contract.
        views_source = " ".join(
            Path(__file__).with_name("views.py").read_text(encoding="utf-8").split()
        )
        self.assertIn(
            'MODULE {{ module.position|stringformat:"02d" }} · {{ module_display_title }}',
            lesson_template,
        )
        self.assertIn(
            'MODULE {{ selected_module.position|stringformat:"02d" }} · {{ selected_module_display_title }}',
            website_preview,
        )
        self.assertIn(
            '"module_display_title": _module_display_title(lesson.module.title)', views_source
        )
        self.assertIn(
            '"selected_module_display_title": _module_display_title(', views_source
        )
        self.assertIn(
            'selected_module.get("title") if selected_module else ""', views_source
        )

    def test_module_display_name_removes_an_optional_number_prefix(self):
        from .views import _module_display_title

        self.assertEqual(
            _module_display_title("Module 03 — Read the Market Before Reading the Signal"),
            "Read the Market Before Reading the Signal",
        )
        self.assertEqual(
            _module_display_title("Read the Market Before Reading the Signal"),
            "Read the Market Before Reading the Signal",
        )
