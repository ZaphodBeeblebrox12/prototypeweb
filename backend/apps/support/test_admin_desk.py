"""Regression tests for the custom TradeThesis Admin Desk support workspace."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.notifications.models import Notification
from apps.subscriptions.models import Plan
from apps.support.models import AffiliateLink, SupportTicket, TicketMessage

User = get_user_model()


class AdminDeskSupportTicketTests(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user(
            username="desk-support-reviewer",
            email="desk-support-reviewer@example.test",
            password="test-password-123!",
            is_staff=True,
        )
        self.other_reviewer = User.objects.create_user(
            username="desk-support-other",
            email="desk-support-other@example.test",
            password="test-password-123!",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="desk-support-member",
            email="desk-support-member@example.test",
            password="test-password-123!",
        )
        self.ticket = SupportTicket.objects.create(
            user=self.member,
            category=SupportTicket.Category.BILLING,
            message="Payment completed but my course access is still missing.",
        )
        self.client.force_login(self.reviewer)

    def test_dashboard_support_links_and_recent_ticket_open_inside_admin_desk(self):
        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.context["support_tickets"]["links"]["all"],
            reverse("staff_admin_desk_support_tickets"),
        )
        self.assertEqual(
            response.context["support_tickets"]["links"]["pending"],
            reverse("staff_admin_desk_support_tickets") + "?status=pending",
        )
        self.assertEqual(
            response.context["support_tickets"]["recent"][0]["can_review"],
            True,
        )
        self.assertContains(
            response,
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk]),
        )
        self.assertNotContains(response, "/admin/support/supportticket/")

    def test_queue_filters_to_ticket_status_and_support_reviewer_scope(self):
        restricted_plan = Plan.objects.create(
            name="Reviewer-only queue plan",
            tier=Plan.Tier.BASIC,
            is_hidden=True,
        )
        restricted_plan.ticket_approvers.add(self.other_reviewer)
        link = AffiliateLink.objects.create(
            name="Restricted broker",
            url="https://example.test/restricted",
            referral_code="DESK-ONLY",
            plan=restricted_plan,
        )
        restricted_ticket = SupportTicket.objects.create(
            user=User.objects.create_user(
                username="restricted-ticket-member",
                email="restricted-ticket@example.test",
            ),
            category=SupportTicket.Category.ACCESS,
            affiliate_link=link,
            plan=restricted_plan,
            message="Restricted access request.",
        )

        response = self.client.get(
            reverse("staff_admin_desk_support_tickets"),
            {"status": SupportTicket.Status.PENDING},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, self.ticket.short_id)
        self.assertNotContains(response, restricted_ticket.short_id)
        self.assertEqual(response.context["stats"]["pending"], 1)
        self.assertEqual(response.context["status_filter"], SupportTicket.Status.PENDING)

        self.client.force_login(self.other_reviewer)
        allowed_response = self.client.get(reverse("staff_admin_desk_support_tickets"))
        self.assertEqual(allowed_response.status_code, 200, allowed_response.content)
        self.assertContains(allowed_response, restricted_ticket.short_id)

    def test_ticket_detail_shows_conversation_private_notes_and_member_evidence_links(self):
        TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.member,
            body="Here is a follow-up with my receipt reference.",
        )
        TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.reviewer,
            body="Staff-only reconciliation check.",
            is_internal=True,
        )

        response = self.client.get(
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Support workspace")
        self.assertContains(response, "Here is a follow-up with my receipt reference.")
        self.assertContains(response, "Staff-only reconciliation check.")
        self.assertContains(response, "Internal note")
        self.assertContains(response, "Send reply")
        self.assertContains(response, "Save internal note")
        self.assertNotContains(response, "/admin/support/supportticket/")

    def test_unauthorized_reviewer_cannot_open_ticket_with_restricted_plan(self):
        plan = Plan.objects.create(
            name="Private queue plan",
            tier=Plan.Tier.BASIC,
            is_hidden=True,
        )
        plan.ticket_approvers.add(self.other_reviewer)
        link = AffiliateLink.objects.create(
            name="Private broker",
            url="https://example.test/private",
            referral_code="PRIVATE",
            plan=plan,
        )
        restricted = SupportTicket.objects.create(
            user=self.member,
            category=SupportTicket.Category.ACCESS,
            affiliate_link=link,
            plan=plan,
            message="Private access request.",
        )

        response = self.client.get(
            reverse("staff_admin_desk_support_ticket", args=[restricted.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_public_reply_and_internal_note_use_existing_ticket_message_service(self):
        url = reverse("staff_admin_desk_support_ticket_action", args=[self.ticket.pk])

        public = self.client.post(
            url,
            {"action": "public_reply", "body": "I have checked your payment reference."},
        )
        self.assertRedirects(
            public,
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk]),
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.AWAITING_MEMBER)
        public_message = self.ticket.messages.get()
        self.assertEqual(public_message.body, "I have checked your payment reference.")
        self.assertFalse(public_message.is_internal)

        internal = self.client.post(
            url,
            {"action": "internal_note", "body": "Compare gateway settlement log."},
        )
        self.assertRedirects(
            internal,
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk]),
        )
        private_message = self.ticket.messages.get(body="Compare gateway settlement log.")
        self.assertTrue(private_message.is_internal)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.AWAITING_MEMBER)

    def test_assignment_and_priority_can_be_updated_without_django_admin(self):
        response = self.client.post(
            reverse("staff_admin_desk_support_ticket_action", args=[self.ticket.pk]),
            {
                "action": "update_details",
                "assigned_to": str(self.reviewer.pk),
                "priority": SupportTicket.Priority.HIGH,
            },
        )

        self.assertRedirects(
            response,
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk]),
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.reviewer)
        self.assertEqual(self.ticket.priority, SupportTicket.Priority.HIGH)
        self.assertIsNotNone(self.ticket.first_response_due_at)

    @patch("apps.support.services.notify_user")
    def test_reviewer_can_start_work_and_return_ticket_to_member(self, notify):
        url = reverse("staff_admin_desk_support_ticket_action", args=[self.ticket.pk])
        started = self.client.post(url, {"action": "start_review"})
        self.assertRedirects(
            started, reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.IN_PROGRESS)
        self.assertEqual(self.ticket.assigned_to, self.reviewer)

        awaiting = self.client.post(url, {"action": "awaiting_member"})
        self.assertRedirects(
            awaiting, reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.AWAITING_MEMBER)

    @patch("apps.support.admin_desk_views.approve_ticket", create=True)
    def test_access_ticket_approval_is_posted_through_dashboard(self, approve):
        plan = Plan.objects.create(
            name="Dashboard hidden access",
            tier=Plan.Tier.BASIC,
            is_hidden=True,
        )
        link = AffiliateLink.objects.create(
            name="Dashboard access link",
            url="https://example.test/dashboard",
            referral_code="DESK-ACCESS",
            plan=plan,
        )
        ticket = SupportTicket.objects.create(
            user=self.member,
            category=SupportTicket.Category.ACCESS,
            affiliate_link=link,
            plan=plan,
            message="Please verify my referral access.",
        )

        response = self.client.post(
            reverse("staff_admin_desk_support_ticket_action", args=[ticket.pk]),
            {
                "action": "approve",
                "plan": str(plan.pk),
                "admin_notes": "Evidence checked and approved.",
            },
        )

        self.assertRedirects(
            response, reverse("staff_admin_desk_support_ticket", args=[ticket.pk])
        )
        approve.assert_called_once()
        args, kwargs = approve.call_args
        self.assertEqual(args[0].pk, ticket.pk)
        self.assertEqual(args[1].pk, plan.pk)
        self.assertEqual(args[2], self.reviewer)
        self.assertEqual(kwargs["notes"], "Evidence checked and approved.")

    @patch("apps.support.services.notify_user")
    def test_reject_and_reopen_actions_stay_inside_dashboard(self, notify):
        detail = reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
        action = reverse("staff_admin_desk_support_ticket_action", args=[self.ticket.pk])
        rejected = self.client.post(
            action,
            {"action": "reject", "admin_notes": "Please provide a clearer payment receipt."},
        )
        self.assertRedirects(rejected, detail)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.REJECTED)
        self.assertEqual(self.ticket.admin_notes, "Please provide a clearer payment receipt.")

        reopened = self.client.post(action, {"action": "reopen"})
        self.assertRedirects(reopened, detail)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.IN_PROGRESS)
        self.assertEqual(self.ticket.admin_notes, "")

    @patch("apps.support.services._send_email", return_value=True)
    def test_staff_notifications_link_back_to_admin_desk_ticket(self, _send_email):
        from apps.support.services import notify_staff_about_ticket

        notify_staff_about_ticket(self.ticket)
        notification = Notification.objects.get(
            user=self.reviewer,
            metadata__source="support_ticket",
        )
        self.assertTrue(
            notification.link.endswith(
                reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
            )
        )
        self.assertNotIn("/admin/support/supportticket/", notification.link)
