from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


class CourseBuilderTiptapPreviewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="tiptap-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=False)
    def test_prototype_route_is_hidden_when_feature_flag_is_off(self):
        response = self.client.get(reverse("staff_course_builder_tiptap_preview"))

        self.assertEqual(response.status_code, 404)

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_admin_can_open_isolated_prototype_without_live_save_controls(self):
        response = self.client.get(reverse("staff_course_builder_tiptap_preview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prototype only")
        self.assertContains(response, "not connected to course drafts")
        self.assertContains(response, "course-builder-tiptap.js")
        self.assertContains(response, "Download JSON")
        self.assertContains(response, "Test Markdown import and export")
        self.assertContains(response, "Replace editor from Markdown")
        self.assertContains(response, "Export editor to Markdown")
        self.assertContains(response, "currently beta")
        self.assertContains(response, "TradeThesis figure references")
        self.assertNotContains(response, "staff_course_builder_api")

    @override_settings(ACADEMY_TIPTAP_EDITOR_ENABLED=True)
    def test_non_admin_cannot_open_prototype(self):
        member = User.objects.create_user(
            username="tiptap-member",
            password="test-password",
            role="member",
        )
        self.client.force_login(member)

        response = self.client.get(reverse("staff_course_builder_tiptap_preview"))

        self.assertEqual(response.status_code, 403)

    def test_existing_builder_route_remains_registered(self):
        self.assertEqual(
            reverse("staff_course_builder_preview"),
            "/staff/course-builder/",
        )
