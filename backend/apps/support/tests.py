"""Tests for support-ticket account isolation."""
from django.contrib.auth import get_user_model
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
