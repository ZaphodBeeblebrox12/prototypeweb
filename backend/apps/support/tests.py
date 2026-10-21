"""Tests for support-ticket account isolation and submission."""
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.support.models import SupportTicket


User = get_user_model()


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

    @patch("apps.support.views.send_ticket_confirmation")
    def test_billing_ticket_can_be_submitted_and_appears_in_ticket_list(self, send_confirmation):
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

        list_response = self.client.get(reverse("support:my_tickets"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, str(ticket.short_id))
        self.assertContains(list_response, "Help &amp; support")

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
