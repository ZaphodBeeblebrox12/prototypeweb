import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import CourseBuilderTiptapDraft, CourseImport, Lesson

User = get_user_model()


def sample_document(text="Pilot content"):
    return {
        "format": "tradethesis.lesson-document",
        "version": 1,
        "document": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        },
    }


@override_settings(ACADEMY_TIPTAP_PILOT_ENABLED=True)
class TiptapPilotViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="tiptap-pilot-admin",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)

    def test_separate_editor_route_renders_without_replacing_legacy_route(self):
        response = self.client.get(reverse("staff_course_builder_tiptap"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SEPARATE PILOT")
        self.assertContains(response, "Sandbox only")
        self.assertContains(response, reverse("staff_course_builder_preview"))
        self.assertContains(response, reverse("staff_course_builder_tiptap_api"))

    def test_pilot_route_is_hidden_when_feature_flag_is_disabled(self):
        with self.settings(ACADEMY_TIPTAP_PILOT_ENABLED=False):
            response = self.client.get(reverse("staff_course_builder_tiptap"))
            api_response = self.client.get(reverse("staff_course_builder_tiptap_api"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(api_response.status_code, 404)

    def test_operational_staff_without_content_admin_role_is_forbidden(self):
        staff_user = User.objects.create_user(
            username="tiptap-pilot-operations",
            password="test-password",
            role="member",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("staff_course_builder_tiptap"))

        self.assertEqual(response.status_code, 403)


@override_settings(ACADEMY_TIPTAP_PILOT_ENABLED=True)
class TiptapPilotDraftApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="tiptap-pilot-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)
        self.url = reverse("staff_course_builder_tiptap_api")

    def post_document(self, **overrides):
        payload = {
            "title": "Sandbox lesson",
            "document": sample_document(),
        }
        payload.update(overrides)
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_get_lists_only_the_current_authors_pilot_drafts(self):
        own = CourseBuilderTiptapDraft.objects.create(
            owner=self.admin,
            title="My sandbox",
            document=sample_document(),
        )
        other = User.objects.create_user(
            username="another-pilot-author",
            password="test-password",
            role="admin",
        )
        CourseBuilderTiptapDraft.objects.create(
            owner=other,
            title="Not mine",
            document=sample_document("Private to another author"),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["drafts"]), 1)
        self.assertEqual(payload["drafts"][0]["id"], str(own.pk))

    def test_create_persists_only_a_separate_pilot_record(self):
        response = self.post_document()

        self.assertEqual(response.status_code, 201)
        draft_id = response.json()["draft"]["id"]
        draft = CourseBuilderTiptapDraft.objects.get(pk=draft_id)
        self.assertEqual(draft.owner, self.admin)
        self.assertEqual(draft.document, sample_document())
        self.assertEqual(draft.revision, 1)
        self.assertEqual(CourseImport.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_saved_draft_can_be_loaded_by_its_owner(self):
        create = self.post_document()
        draft_id = create.json()["draft"]["id"]

        response = self.client.get(self.url, {"id": draft_id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["document"], sample_document())
        self.assertEqual(response.json()["draft"]["id"], draft_id)

    def test_another_author_cannot_load_a_private_pilot_draft(self):
        create = self.post_document()
        draft_id = create.json()["draft"]["id"]
        other = User.objects.create_user(
            username="tiptap-pilot-other",
            password="test-password",
            role="admin",
        )
        self.client.force_login(other)

        response = self.client.get(self.url, {"id": draft_id})

        self.assertEqual(response.status_code, 404)

    def test_revision_check_prevents_stale_browser_overwrite(self):
        create = self.post_document()
        draft_id = create.json()["draft"]["id"]
        self.assertEqual(create.status_code, 201)

        update = self.post_document(
            id=draft_id,
            revision=1,
            title="Updated by first session",
            document=sample_document("Latest content"),
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["draft"]["revision"], 2)

        stale = self.post_document(
            id=draft_id,
            revision=1,
            title="Stale browser copy",
            document=sample_document("Old content"),
        )
        self.assertEqual(stale.status_code, 409)

        saved = CourseBuilderTiptapDraft.objects.get(pk=draft_id)
        self.assertEqual(saved.revision, 2)
        self.assertEqual(saved.title, "Updated by first session")
        self.assertEqual(saved.document, sample_document("Latest content"))

    def test_unknown_nodes_are_rejected_without_creating_a_draft(self):
        invalid = {
            "format": "tradethesis.lesson-document",
            "version": 1,
            "document": {
                "type": "doc",
                "content": [{"type": "unregisteredCourseWidget"}],
            },
        }

        response = self.post_document(document=invalid)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CourseBuilderTiptapDraft.objects.count(), 0)

    def test_trade_thesis_blocks_wait_for_their_pilot_extension(self):
        future_block = {
            "format": "tradethesis.lesson-document",
            "version": 1,
            "document": {
                "type": "doc",
                "content": [{"type": "courseFigure", "attrs": {"figureId": "figure-1"}}],
            },
        }

        response = self.post_document(document=future_block)

        self.assertEqual(response.status_code, 400)
        self.assertIn("does not support the 'courseFigure' block yet", response.json()["detail"])
        self.assertEqual(CourseBuilderTiptapDraft.objects.count(), 0)

    def test_executable_links_are_rejected_without_saving(self):
        invalid = {
            "format": "tradethesis.lesson-document",
            "version": 1,
            "document": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Unsafe",
                                "marks": [
                                    {
                                        "type": "link",
                                        "attrs": {"href": "javascript:alert(1)"},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        }

        response = self.post_document(document=invalid)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CourseBuilderTiptapDraft.objects.count(), 0)

    def test_missing_update_revision_is_rejected(self):
        create = self.post_document()
        draft_id = create.json()["draft"]["id"]

        response = self.post_document(id=draft_id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CourseBuilderTiptapDraft.objects.get(pk=draft_id).revision, 1)
