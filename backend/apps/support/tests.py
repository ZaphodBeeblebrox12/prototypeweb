"""Regression tests for support-ticket lifecycle and access control."""
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from allauth.account.models import EmailAddress
from PIL import Image
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import EmailLog, Notification
from apps.subscriptions.models import Plan
from apps.support.admin import SupportTicketAdmin
from apps.support.models import AffiliateLink, SupportTicket, TicketAttachment, TicketMessage
from apps.support.services import (
    add_ticket_message, approve_ticket, reject_ticket, reopen_ticket, set_ticket_status,
)


User = get_user_model()


def valid_png_bytes():
    output = BytesIO()
    Image.new("RGB", (1, 1), (20, 120, 200)).save(output, format="PNG")
    return output.getvalue()


def uploaded_png(name="tiny.png"):
    return SimpleUploadedFile(name, valid_png_bytes(), content_type="image/png")


class SupportTicketUserScopeTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="ticket-owner",
            email="ticket-owner@example.test",
            password="test-password-123!",
        )
        self.other_user = User.objects.create_user(
            username="ticket-other",
            email="ticket-other@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=self.owner, email=self.owner.email, primary=True, verified=True
        )
        self.own_ticket = SupportTicket.objects.create(
            user=self.owner,
            category=SupportTicket.Category.BILLING,
            message="MY_PRIVATE_TICKET",
        )
        self.other_ticket = SupportTicket.objects.create(
            user=self.other_user,
            category=SupportTicket.Category.BILLING,
            message="SOMEONE_ELSES_PRIVATE_TICKET",
        )
        self.client.force_login(self.owner)

    def test_ticket_list_contains_only_the_authenticated_users_tickets(self):
        response = self.client.get(reverse("support:my_tickets"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.own_ticket.short_id))
        self.assertNotContains(response, str(self.other_ticket.short_id))
        self.assertEqual(
            list(response.context["tickets"].values_list("pk", flat=True)),
            [self.own_ticket.pk],
        )

    def test_direct_url_cannot_read_another_users_ticket(self):
        response = self.client.get(
            reverse("support:ticket_detail", kwargs={"pk": self.other_ticket.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_anonymous_ticket_detail_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("support:ticket_detail", kwargs={"pk": self.own_ticket.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_owner_can_add_a_public_reply(self):
        response = self.client.post(
            reverse("support:ticket_reply", kwargs={"pk": self.own_ticket.pk}),
            {"body": "The payment receipt is attached to my account."},
        )
        self.assertRedirects(
            response,
            reverse("support:ticket_detail", kwargs={"pk": self.own_ticket.pk}),
            fetch_redirect_response=False,
        )
        reply = self.own_ticket.messages.get()
        self.assertEqual(reply.author, self.owner)
        self.assertFalse(reply.is_internal)
        detail = self.client.get(reverse("support:ticket_detail", kwargs={"pk": self.own_ticket.pk}))
        self.assertContains(detail, "The payment receipt is attached to my account.")

    def test_member_cannot_read_internal_staff_notes(self):
        staff = User.objects.create_user(
            username="ticket-reviewer", email="ticket-reviewer@example.test",
            password="test-password-123!", is_staff=True,
        )
        add_ticket_message(self.own_ticket, staff, "Internal reviewer context.", is_internal=True)
        response = self.client.get(reverse("support:ticket_detail", kwargs={"pk": self.own_ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Internal reviewer context.")

    def test_attachment_download_is_private_and_authenticated(self):
        attachment = TicketAttachment.objects.create(
            ticket=self.own_ticket,
            file=uploaded_png(),
        )
        url = reverse("support:attachment_download", kwargs={"pk": attachment.pk})
        owner_response = self.client.get(url)
        self.assertEqual(owner_response.status_code, 200)
        self.assertEqual(owner_response["Content-Type"], "image/png")
        self.assertEqual(owner_response["X-Content-Type-Options"], "nosniff")

        self.client.force_login(self.other_user)
        self.assertEqual(self.client.get(url).status_code, 403)


class SupportTicketSubmissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ticket-submit-member",
            email="ticket-submit-member@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, primary=True, verified=True
        )
        self.client.force_login(self.user)

    def test_anonymous_user_is_redirected_before_pending_ticket_lookup(self):
        self.client.logout()
        response = self.client.get(reverse("support:request_ticket"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    @patch("apps.support.views.notify_staff_about_ticket")
    @patch("apps.support.views.send_ticket_confirmation")
    def test_billing_ticket_can_be_submitted_and_appears_in_ticket_list(
        self, send_confirmation, staff_alert
    ):
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.BILLING,
                "message": "I need help understanding a payment status.",
            },
        )
        self.assertRedirects(
            response, reverse("support:my_tickets"), fetch_redirect_response=False
        )
        ticket = SupportTicket.objects.get(user=self.user)
        self.assertEqual(ticket.category, SupportTicket.Category.BILLING)
        self.assertEqual(ticket.message, "I need help understanding a payment status.")
        send_confirmation.assert_called_once_with(ticket)
        staff_alert.assert_called_once_with(ticket)

        list_response = self.client.get(reverse("support:my_tickets"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, str(ticket.short_id))
        self.assertContains(list_response, "HELP &amp; SUPPORT")

    def test_unsupported_attachment_is_rejected_without_creating_ticket(self):
        upload = SimpleUploadedFile(
            "not-an-image.exe", b"not an image", content_type="application/octet-stream"
        )
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.BILLING,
                "message": "Please review this attachment.",
                "attachments": upload,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Only PNG, JPG, JPEG, GIF and WEBP images are allowed")
        self.assertFalse(SupportTicket.objects.filter(user=self.user).exists())

    def test_image_extension_does_not_allow_arbitrary_file_contents(self):
        upload = SimpleUploadedFile("fake.png", b"not actually a PNG", content_type="image/png")
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.BILLING,
                "message": "Please review this attachment.",
                "attachments": upload,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not a valid image matching its extension")
        self.assertFalse(SupportTicket.objects.filter(user=self.user).exists())

    @patch("apps.support.views.notify_staff_about_ticket")
    @patch("apps.support.views.send_ticket_confirmation")
    def test_same_category_open_ticket_redirects_to_existing_conversation(
        self, send_confirmation, staff_alert
    ):
        existing = SupportTicket.objects.create(
            user=self.user,
            category=SupportTicket.Category.BILLING,
            message="Existing billing issue.",
        )
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.BILLING,
                "message": "A second billing issue.",
            },
        )
        self.assertRedirects(
            response,
            reverse("support:ticket_detail", kwargs={"pk": existing.pk}),
            fetch_redirect_response=False,
        )
        self.assertEqual(SupportTicket.objects.filter(user=self.user).count(), 1)
        send_confirmation.assert_not_called()
        staff_alert.assert_not_called()

    @patch("apps.support.views.notify_staff_about_ticket")
    @patch("apps.support.views.send_ticket_confirmation")
    def test_member_can_open_a_different_category_while_another_is_open(
        self, send_confirmation, staff_alert
    ):
        SupportTicket.objects.create(
            user=self.user,
            category=SupportTicket.Category.BILLING,
            message="Existing billing issue.",
        )
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.TECHNICAL,
                "message": "I cannot open the Telegram group.",
            },
        )
        self.assertRedirects(
            response, reverse("support:my_tickets"), fetch_redirect_response=False
        )
        self.assertEqual(
            SupportTicket.objects.filter(
                user=self.user, status__in=SupportTicket.ACTIVE_STATUSES
            ).count(),
            2,
        )
        self.assertTrue(SupportTicket.objects.filter(
            user=self.user, category=SupportTicket.Category.TECHNICAL
        ).exists())
        send_confirmation.assert_called_once()
        staff_alert.assert_called_once()

    def test_access_request_requires_affiliate_link_and_screenshot(self):
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.ACCESS,
                "message": "Please review my access request.",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select the referral link you used.")
        self.assertContains(response, "Upload at least one screenshot for access requests.")
        self.assertFalse(SupportTicket.objects.filter(user=self.user).exists())

    @patch("apps.support.views.notify_staff_about_ticket")
    @patch("apps.support.views.send_ticket_confirmation")
    def test_referral_link_plan_is_auto_assigned_when_ticket_is_submitted(
        self, send_confirmation, staff_alert
    ):
        plan = Plan.objects.create(
            name="Hidden access plan", tier=Plan.Tier.BASIC, is_hidden=True
        )
        link = AffiliateLink.objects.create(
            name="Broker referral", url="https://example.test/referral",
            referral_code="TRADE123", plan=plan,
        )
        response = self.client.post(
            reverse("support:request_ticket"),
            data={
                "category": SupportTicket.Category.ACCESS,
                "affiliate_link": str(link.pk),
                "message": "Please verify my referral account.",
                "attachments": uploaded_png(),
            },
        )
        self.assertRedirects(
            response, reverse("support:my_tickets"), fetch_redirect_response=False
        )
        ticket = SupportTicket.objects.get(user=self.user)
        self.assertEqual(ticket.plan, plan)
        send_confirmation.assert_called_once_with(ticket)
        staff_alert.assert_called_once_with(ticket)


class SupportTicketWorkflowTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="workflow-member", email="workflow-member@example.test",
            password="test-password-123!",
        )
        self.allowed_reviewer = User.objects.create_user(
            username="allowed-reviewer", email="allowed@example.test",
            password="test-password-123!", is_staff=True,
        )
        self.other_reviewer = User.objects.create_user(
            username="other-reviewer", email="other@example.test",
            password="test-password-123!", is_staff=True,
        )
        self.plan = Plan.objects.create(
            name="Reviewer restricted plan", tier=Plan.Tier.BASIC, is_hidden=True
        )
        self.plan.ticket_approvers.add(self.allowed_reviewer)
        self.link = AffiliateLink.objects.create(
            name="Restricted referral", url="https://example.test/ref",
            referral_code="RESTRICTED", plan=self.plan,
        )
        self.ticket = SupportTicket.objects.create(
            user=self.member, category=SupportTicket.Category.ACCESS,
            affiliate_link=self.link, message="Verify my account.",
        )

    def test_plan_reviewer_list_applies_before_plan_is_saved_on_ticket(self):
        self.ticket.plan = None
        self.ticket.save(update_fields=["plan", "updated_at"])
        self.assertTrue(self.ticket.can_be_reviewed_by(self.allowed_reviewer))
        self.assertFalse(self.ticket.can_be_reviewed_by(self.other_reviewer))

    def test_unauthorized_staff_cannot_approve_mapped_plan(self):
        with self.assertRaises(PermissionError):
            approve_ticket(self.ticket, self.plan, self.other_reviewer)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.PENDING)

    def test_reviewer_acl_filters_the_admin_queue_not_just_ticket_detail(self):
        request = RequestFactory().get("/admin/support/supportticket/")
        ticket_admin = SupportTicketAdmin(SupportTicket, admin.site)
        request.user = self.allowed_reviewer
        self.assertIn(self.ticket.pk, list(ticket_admin.get_queryset(request).values_list("pk", flat=True)))
        request.user = self.other_reviewer
        self.assertNotIn(self.ticket.pk, list(ticket_admin.get_queryset(request).values_list("pk", flat=True)))

    def test_unauthorized_staff_cannot_reject_selected_plan(self):
        with self.assertRaises(PermissionError):
            reject_ticket(
                self.ticket, self.other_reviewer,
                "Please provide a clearer screenshot.", plan=self.plan,
            )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.PENDING)

    @patch("apps.support.services.notify_user")
    @patch("apps.support.services.enqueue_reconcile")
    @patch("apps.support.services.grant_subscription_by_admin")
    def test_approval_persists_resolution_notes_and_enqueues_access_sync(
        self, grant, enqueue, notify
    ):
        with self.captureOnCommitCallbacks(execute=True):
            approve_ticket(
                self.ticket, self.plan, self.allowed_reviewer,
                notes="Approved after checking the evidence.",
            )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.APPROVED)
        self.assertEqual(self.ticket.admin_notes, "Approved after checking the evidence.")
        grant.assert_called_once()
        enqueue.assert_called_once_with(self.member.pk, reason="support_ticket_approved")
        notify.assert_called_once()

    @patch("apps.support.services.enqueue_reconcile", side_effect=RuntimeError("queue unavailable"))
    @patch("apps.support.services.grant_subscription_by_admin")
    def test_reconciliation_enqueue_failure_rolls_back_ticket_approval(
        self, grant, enqueue
    ):
        with self.assertRaises(RuntimeError):
            approve_ticket(self.ticket, self.plan, self.allowed_reviewer)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.PENDING)
        self.assertIsNone(self.ticket.reviewed_at)
        grant.assert_called_once()
        enqueue.assert_called_once()

    def test_new_ticket_message_saves_despite_uuid_primary_key(self):
        message = TicketMessage.objects.create(
            ticket=self.ticket, author=self.member, body="Additional evidence.",
        )
        self.assertIsNotNone(message.pk)
        message.body = "Changed"
        with self.assertRaises(RuntimeError):
            message.save()

    def test_bulk_reject_action_passes_admin_and_notes_in_correct_order(self):
        self.ticket.admin_notes = "The evidence is incomplete."
        self.ticket.save(update_fields=["admin_notes", "updated_at"])
        request = RequestFactory().post("/admin/support/supportticket/")
        request.user = self.allowed_reviewer

        class MessageStorage:
            def __init__(self):
                self.entries = []
            def add(self, level, message, extra_tags=None):
                self.entries.append((level, str(message)))

        request._messages = MessageStorage()
        ticket_admin = SupportTicketAdmin(SupportTicket, admin.site)
        ticket_admin.reject_tickets(
            request, SupportTicket.objects.filter(pk=self.ticket.pk)
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.REJECTED)
        self.assertEqual(self.ticket.admin_notes, "The evidence is incomplete.")

    @patch("apps.support.services.send_mail", return_value=1)
    def test_staff_alerts_are_persisted_and_email_delivery_is_logged(self, send_email):
        from apps.support.services import notify_staff_about_ticket

        notify_staff_about_ticket(self.ticket)
        self.assertTrue(Notification.objects.filter(
            user=self.allowed_reviewer, title__contains=self.ticket.short_id
        ).exists())
        self.assertTrue(EmailLog.objects.filter(
            user=self.allowed_reviewer, template="support_ticket_staff_alert",
            status="sent",
        ).exists())
        self.assertFalse(Notification.objects.filter(
            user=self.other_reviewer, title__contains=self.ticket.short_id
        ).exists())
        self.assertFalse(EmailLog.objects.filter(
            user=self.other_reviewer, template="support_ticket_staff_alert",
        ).exists())

    def test_service_rejects_oversized_replies_server_side(self):
        with self.assertRaisesRegex(ValueError, "10,000 characters or fewer"):
            add_ticket_message(self.ticket, self.member, "x" * 10001)

    def test_priority_sets_and_recalculates_first_response_sla(self):
        self.assertIsNotNone(self.ticket.first_response_due_at)
        old_due = self.ticket.first_response_due_at
        self.ticket.priority = SupportTicket.Priority.URGENT
        self.ticket.save(update_fields=["priority", "updated_at"])
        self.ticket.refresh_from_db()
        now = timezone.now()
        self.assertLess(self.ticket.first_response_due_at, old_due)
        self.assertGreater(self.ticket.first_response_due_at, now + timedelta(hours=1, minutes=58))
        self.assertLess(self.ticket.first_response_due_at, now + timedelta(hours=2, minutes=1))

        self.ticket.first_response_due_at = now - timedelta(minutes=1)
        self.ticket.first_response_at = None
        self.ticket.save(update_fields=["first_response_due_at", "first_response_at", "updated_at"])
        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.is_sla_overdue)

    def test_start_review_assigns_reviewer_without_faking_first_response(self):
        set_ticket_status(
            self.ticket, self.allowed_reviewer, SupportTicket.Status.IN_PROGRESS
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.IN_PROGRESS)
        self.assertEqual(self.ticket.assigned_to, self.allowed_reviewer)
        self.assertIsNone(self.ticket.first_response_at)

    @patch("apps.support.services.notify_user")
    @patch("apps.support.services.notify_staff_about_ticket")
    def test_public_replies_drive_awaiting_member_and_in_progress_states(
        self, notify_staff, notify_user
    ):
        with self.captureOnCommitCallbacks(execute=True):
            add_ticket_message(
                self.ticket, self.allowed_reviewer,
                "Please confirm the referral account email.",
            )
            self.ticket.refresh_from_db()
            self.assertEqual(self.ticket.status, SupportTicket.Status.AWAITING_MEMBER)
            self.assertIsNotNone(self.ticket.first_response_at)

            add_ticket_message(
                self.ticket, self.member,
                "The email is member@example.test.",
            )
            self.ticket.refresh_from_db()
            self.assertEqual(self.ticket.status, SupportTicket.Status.IN_PROGRESS)

        notify_user.assert_called_once()
        notify_staff.assert_called_once()

    def test_closed_ticket_can_be_reopened_and_keeps_previous_review_note(self):
        with self.captureOnCommitCallbacks(execute=False):
            reject_ticket(
                self.ticket, self.allowed_reviewer,
                "Please provide a clearer referral screenshot.",
            )
            self.ticket.refresh_from_db()
            self.assertEqual(self.ticket.status, SupportTicket.Status.REJECTED)

            reopen_ticket(self.ticket, self.allowed_reviewer)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, SupportTicket.Status.IN_PROGRESS)
        self.assertEqual(self.ticket.admin_notes, "")
        self.assertIsNone(self.ticket.reviewed_at)
        self.assertTrue(TicketMessage.objects.filter(
            ticket=self.ticket,
            is_internal=True,
            body__contains="Please provide a clearer referral screenshot.",
        ).exists())
