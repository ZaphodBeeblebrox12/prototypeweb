"""Tests for the TradeThesis Admin Desk course approval workflow."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Course, CourseImport

User = get_user_model()


class AdminDeskCourseReviewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="desk-course-approver",
            password="test-password",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(self.admin)

    def make_import(self, *, status=CourseImport.Status.REVIEW, slug="desk-course-review"):
        return CourseImport.objects.create(
            course_slug=slug,
            title="Admin Desk Review Course",
            manifest_version="course-builder-v1",
            content_hash=(slug[:1] or "a") * 64,
            source_manifest=f"builder://{slug}",
            status=status,
            imported_by=self.admin,
            payload={
                "course": {
                    "title": "Admin Desk Review Course",
                    "slug": slug,
                    "summary": "A complete course summary for review.",
                },
                "builder_state": {
                    "title": "Admin Desk Review Course",
                    "summary": "A complete course summary for review.",
                    "modules": [],
                },
                "assets": [],
                "modules": [],
            },
        )

    def test_admin_dashboard_links_approval_count_and_queue_to_admin_desk(self):
        record = self.make_import()
        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["course_metrics"]["imports_awaiting_review"], 1)
        self.assertEqual(
            response.context["course_links"]["imports"],
            reverse("staff_admin_desk_course_reviews"),
        )
        self.assertEqual(
            response.context["course_review_items"][0]["url"],
            reverse("staff_admin_desk_course_review", args=[record.pk]),
        )
        self.assertContains(response, "Pending course approvals")
        self.assertContains(response, "Admin Desk Review Course")
        self.assertNotEqual(
            response.context["course_links"]["imports"],
            reverse("admin:academy_courseimport_changelist"),
        )

    def test_approval_queue_shows_only_submissions_awaiting_review(self):
        pending = self.make_import(slug="desk-pending-course")
        self.make_import(status=CourseImport.Status.DRAFT, slug="desk-draft-course")
        self.make_import(status=CourseImport.Status.REJECTED, slug="desk-returned-course")

        response = self.client.get(reverse("staff_admin_desk_course_reviews"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["pending_count"], 1)
        self.assertContains(response, pending.title)
        self.assertContains(
            response,
            reverse("staff_admin_desk_course_review", args=[pending.pk]),
        )
        self.assertNotContains(response, "desk-draft-course")
        self.assertNotContains(response, "desk-returned-course")

    def test_review_page_renders_full_preview_and_admin_desk_actions(self):
        record = self.make_import()
        with patch(
            "apps.academy.review_context.validate_import_for_publish",
            return_value=[],
        ):
            response = self.client.get(
                reverse("staff_admin_desk_course_review", args=[record.pk])
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Review submission")
        self.assertContains(response, "Approve and publish course")
        self.assertContains(response, "Return to author with feedback")
        self.assertContains(
            response,
            reverse("staff_admin_desk_course_approve", args=[record.pk]),
        )
        self.assertContains(
            response,
            reverse("staff_admin_desk_course_reject", args=[record.pk]),
        )
        self.assertNotContains(
            response,
            reverse("admin:academy_courseimport_review", args=[record.pk]),
        )
        self.assertNotContains(response, "Back to imports")

    def test_approve_action_uses_canonical_publisher_and_returns_to_queue(self):
        record = self.make_import()
        published_course = Course.objects.create(
            title="Admin Desk Review Course",
            slug=record.course_slug,
            summary="A complete course summary for review.",
            status=Course.Status.PUBLISHED,
        )
        with patch(
            "apps.academy.importing.publish_course_import",
            return_value=published_course,
        ) as publish:
            response = self.client.post(
                reverse("staff_admin_desk_course_approve", args=[record.pk])
            )

        self.assertRedirects(response, reverse("staff_admin_desk_course_reviews"))
        publish.assert_called_once_with(record, user=self.admin)

    def test_reject_action_requires_feedback_and_returns_submission_to_builder(self):
        record = self.make_import()

        missing_feedback = self.client.post(
            reverse("staff_admin_desk_course_reject", args=[record.pk]),
            {"feedback": "   "},
        )
        self.assertRedirects(
            missing_feedback,
            reverse("staff_admin_desk_course_review", args=[record.pk]),
        )
        record.refresh_from_db()
        self.assertEqual(record.status, CourseImport.Status.REVIEW)

        returned = self.client.post(
            reverse("staff_admin_desk_course_reject", args=[record.pk]),
            {"feedback": "Add a clearer learning outcome and replace the missing chart."},
        )
        self.assertRedirects(returned, reverse("staff_admin_desk_course_reviews"))
        record.refresh_from_db()
        self.assertEqual(record.status, CourseImport.Status.REJECTED)
        self.assertEqual(record.reviewed_by, self.admin)
        self.assertEqual(
            record.payload["review_feedback"],
            "Add a clearer learning outcome and replace the missing chart.",
        )

        builder = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(builder.status_code, 200, builder.content)
        returned_draft = next(
            draft for draft in builder.json()["drafts"]
            if draft["serverDraftId"] == str(record.pk)
        )
        self.assertEqual(
            returned_draft["reviewFeedback"],
            "Add a clearer learning outcome and replace the missing chart.",
        )

    def test_course_approval_pages_are_restricted_to_course_content_admins(self):
        self.client.force_login(
            User.objects.create_user(
                username="desk-regular-staff",
                password="test-password",
                role="learner",
                is_staff=True,
            )
        )
        response = self.client.get(reverse("staff_admin_desk_course_reviews"))
        self.assertEqual(response.status_code, 403)
