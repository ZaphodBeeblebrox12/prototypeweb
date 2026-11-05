import json
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .lesson_document import make_lesson_document
from .models import CourseImport

User = get_user_model()


class CourseBuilderTiptapPreviewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="tiptap-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)

    def create_saved_draft(self):
        lesson_id = str(uuid.uuid4())
        markdown = "## Original lesson\n\nDescribe the visible evidence first."
        question = {
            "id": "question-1",
            "prompt": "What is visible?",
            "options": ["Evidence", "Prediction"],
            "correctIndex": 0,
            "explanation": "Keep answer material private.",
        }
        builder_lesson = {
            "id": lesson_id,
            "title": "Lesson 1.1 — Evidence",
            "summary": "A saved lesson.",
            "content": markdown,
            "document": None,
            "images": [],
            "questions": [question],
            "notebook": {
                "title": "Trading notebook",
                "prompts": [{"label": "Describe", "text": "What is visible?"}],
            },
            "reflectionPrompt": "What would change your view?",
            "reflectionModelReasoning": "Separate evidence from interpretation.",
            "reflectionChartNotes": "Compare the next test.",
            "regionalBlocks": [],
            "regionalContent": {},
            "relatedCourseIds": [],
        }
        payload_lesson = {
            "builder_lesson_id": lesson_id,
            "source_id": "1.1",
            "slug": "evidence",
            "title": "Lesson 1.1 — Evidence",
            "summary": "A saved lesson.",
            "position": 1,
            "duration_minutes": 12,
            "content_markdown": markdown,
            "content_json": {
                "schema_version": 1,
                "questions": [
                    {
                        "id": "question-1",
                        "prompt": "What is visible?",
                        "options": ["Evidence", "Prediction"],
                    }
                ],
                "notebook": builder_lesson["notebook"],
                "reflection": {
                    "prompt": builder_lesson["reflectionPrompt"],
                    "model_reasoning": builder_lesson["reflectionModelReasoning"],
                    "chart_notes": builder_lesson["reflectionChartNotes"],
                },
                "figures": {},
                "tables": {},
                "regional_blocks": {},
                "regional_lesson_content": {},
                "asset_ids": [],
            },
            "instructor_material": {"questions": [question]},
        }
        payload = {
            "schema_version": 1,
            "course": {
                "title": "Tiptap Preview Course",
                "slug": "tiptap-preview-course",
                "summary": "A safe preview draft.",
                "description": "Preview course description.",
                "learning_outcomes": ["Describe evidence."],
            },
            "modules": [
                {
                    "slug": "module-one",
                    "title": "Module 1 — Foundations",
                    "position": 1,
                    "lessons": [payload_lesson],
                }
            ],
            "assets": [],
            "builder_state": {
                "id": "local-course-draft",
                "title": "Tiptap Preview Course",
                "slug": "tiptap-preview-course",
                "summary": "A safe preview draft.",
                "description": "Preview course description.",
                "modules": [
                    {
                        "id": "module-1",
                        "title": "Module 1 — Foundations",
                        "description": "",
                        "lessons": [builder_lesson],
                    }
                ],
            },
        }
        record = CourseImport.objects.create(
            course_slug="tiptap-preview-course",
            title="Tiptap Preview Course",
            manifest_version="course-builder-v1",
            content_hash="a" * 64,
            source_manifest="builder://tiptap-preview-course",
            status=CourseImport.Status.DRAFT,
            payload=payload,
            imported_by=self.admin,
        )
        return record, lesson_id

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=False)
    def test_editor_route_and_api_are_hidden_when_feature_flag_is_off(self):
        page = self.client.get(reverse("staff_course_builder_tiptap_preview"))
        listing = self.client.get(reverse("staff_course_builder_tiptap_api"))

        self.assertEqual(page.status_code, 404)
        self.assertEqual(listing.status_code, 404)

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_admin_can_open_saved_draft_editor_and_learner_preview_controls(self):
        response = self.client.get(reverse("staff_course_builder_tiptap_preview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Staff-only draft editing")
        self.assertContains(response, "Saved course draft")
        self.assertContains(response, "Open lesson")
        self.assertContains(response, "Save draft")
        self.assertContains(response, "Open learner preview")
        self.assertContains(response, "course-builder-tiptap.js")
        self.assertContains(response, "Test Markdown import and export")
        self.assertContains(response, "Compatibility adapter")
        self.assertNotContains(response, "staff_course_builder_api")

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_saved_draft_list_and_lesson_load_exclude_instructor_answers(self):
        record, lesson_id = self.create_saved_draft()

        listing = self.client.get(reverse("staff_course_builder_tiptap_api"))
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["drafts"][0]["id"], str(record.pk))
        self.assertEqual(
            listing.json()["drafts"][0]["modules"][0]["lessons"][0]["id"],
            lesson_id,
        )

        response = self.client.get(
            reverse(
                "staff_course_builder_tiptap_lesson_api",
                args=[record.pk, lesson_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["lesson"]["content"], "## Original lesson\n\nDescribe the visible evidence first.")
        self.assertEqual(response.json()["lesson"]["questions"][0]["prompt"], "What is visible?")
        self.assertNotIn("correctIndex", response.json()["lesson"]["questions"][0])
        self.assertNotIn("explanation", response.json()["lesson"]["questions"][0])
        self.assertTrue(response.json()["expected_updated_at"])
        self.assertIn(str(record.pk), response.json()["learner_preview_url"])
        self.assertIn("?lesson=1.1", response.json()["learner_preview_url"])

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_save_updates_only_selected_lesson_document_and_markdown_mirror(self):
        record, lesson_id = self.create_saved_draft()
        expected_updated_at = record.updated_at.isoformat()
        markdown = "## A revised lesson\n\nObserve, compare, then apply."
        document = make_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "A revised lesson"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Observe, compare, then apply.",
                            }
                        ],
                    },
                    {
                        "type": "practiceQuestion",
                        "attrs": {"questionId": "question-1"},
                    },
                ],
            }
        )
        response = self.client.post(
            reverse(
                "staff_course_builder_tiptap_lesson_api",
                args=[record.pk, lesson_id],
            ),
            data=json.dumps(
                {
                    "expected_updated_at": expected_updated_at,
                    "markdown": markdown,
                    "document": document,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        record.refresh_from_db()
        state_lesson = record.payload["builder_state"]["modules"][0]["lessons"][0]
        payload_lesson = record.payload["modules"][0]["lessons"][0]
        self.assertEqual(state_lesson["content"], markdown)
        self.assertEqual(state_lesson["document"], document)
        self.assertEqual(payload_lesson["content_markdown"], markdown)
        self.assertEqual(payload_lesson["content_json"]["lesson_document"], document)
        self.assertEqual(
            payload_lesson["content_json"]["questions"][0]["prompt"],
            "What is visible?",
        )
        self.assertEqual(
            payload_lesson["instructor_material"]["questions"][0]["correctIndex"],
            0,
        )
        self.assertTrue(response.json()["learner_preview_url"])

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_unrenderable_callout_reference_is_rejected_server_side(self):
        record, lesson_id = self.create_saved_draft()
        document = make_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "callout",
                        "attrs": {
                            "calloutId": "risk-note",
                            "tone": "warning",
                            "title": "Risk",
                        },
                    }
                ],
            }
        )
        response = self.client.post(
            reverse(
                "staff_course_builder_tiptap_lesson_api",
                args=[record.pk, lesson_id],
            ),
            data=json.dumps(
                {
                    "expected_updated_at": record.updated_at.isoformat(),
                    "markdown": "## Original lesson",
                    "document": document,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("callout-renderer-not-supported", str(response.json()))

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_stale_revision_is_rejected_without_overwriting_newer_work(self):
        record, lesson_id = self.create_saved_draft()
        stale_revision = record.updated_at.isoformat()
        document = make_lesson_document(
            {"type": "doc", "content": [{"type": "paragraph"}]}
        )
        url = reverse(
            "staff_course_builder_tiptap_lesson_api",
            args=[record.pk, lesson_id],
        )
        first = self.client.post(
            url,
            data=json.dumps(
                {
                    "expected_updated_at": stale_revision,
                    "markdown": "## Saved by first tab",
                    "document": document,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            url,
            data=json.dumps(
                {
                    "expected_updated_at": stale_revision,
                    "markdown": "## Stale overwrite attempt",
                    "document": document,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(second.status_code, 409)
        self.assertTrue(second.json()["conflict"])
        record.refresh_from_db()
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        self.assertEqual(saved_lesson["content_markdown"], "## Saved by first tab")

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_draft_save_is_reflected_by_the_existing_academy_learner_preview(self):
        record, lesson_id = self.create_saved_draft()
        document = make_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is the saved Academy preview body.",
                            }
                        ],
                    }
                ],
            }
        )
        save = self.client.post(
            reverse(
                "staff_course_builder_tiptap_lesson_api",
                args=[record.pk, lesson_id],
            ),
            data=json.dumps(
                {
                    "expected_updated_at": record.updated_at.isoformat(),
                    "markdown": "This is the saved Academy preview body.",
                    "document": document,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(save.status_code, 200)

        preview = self.client.get(save.json()["learner_preview_url"])
        self.assertIn("?lesson=1.1", save.json()["learner_preview_url"])
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, "This is the saved Academy preview body.")

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_non_admin_cannot_open_editor_or_draft_api(self):
        member = User.objects.create_user(
            username="tiptap-member",
            password="test-password",
            role="member",
        )
        self.client.force_login(member)

        page = self.client.get(reverse("staff_course_builder_tiptap_preview"))
        listing = self.client.get(reverse("staff_course_builder_tiptap_api"))

        self.assertEqual(page.status_code, 403)
        self.assertEqual(listing.status_code, 403)

    def test_existing_builder_route_remains_registered(self):
        self.assertEqual(
            reverse("staff_course_builder_preview"),
            "/staff/course-builder/",
        )
