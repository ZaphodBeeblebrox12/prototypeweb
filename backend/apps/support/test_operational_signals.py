"""Tests for privacy-preserving cross-customer support signals."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.support.models import SupportTicket
from apps.support.operational_signals import build_support_issue_clusters

User = get_user_model()


class SupportIssueSignalTests(TestCase):
    def test_similar_tickets_from_multiple_customers_produce_a_safe_signal(self):
        messages = [
            "Payment completed but I still cannot access my course lessons. Contact me at alpha@example.test.",
            "I made payment, but course access is still blocked for lessons. https://example.test/order/123",
            "Payment succeeded and course access remains blocked for my lessons.",
        ]
        tickets = []
        for index, message in enumerate(messages):
            member = User.objects.create_user(
                username=f"signal-member-{index}",
                email=f"signal-member-{index}@example.test",
            )
            tickets.append(SupportTicket.objects.create(
                user=member,
                category=SupportTicket.Category.BILLING,
                message=message,
            ))

        signals = build_support_issue_clusters(tickets)

        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal["ticket_count"], 3)
        self.assertEqual(signal["customer_count"], 3)
        self.assertEqual(signal["category_key"], SupportTicket.Category.BILLING)
        self.assertIn("payment", signal["terms"])
        self.assertIn("course", signal["terms"])
        self.assertNotIn("alpha@example.test", str(signal))
        self.assertNotIn("example.test", str(signal))
        self.assertNotIn("cannot access my course lessons", str(signal))
        self.assertEqual(len(signal["tickets"]), 3)

    def test_generic_or_single_customer_tickets_do_not_become_incident_signals(self):
        member = User.objects.create_user(
            username="signal-single-member",
            email="signal-single-member@example.test",
        )
        tickets = [
            SupportTicket.objects.create(
                user=member,
                category=SupportTicket.Category.TECHNICAL,
                message="Telegram connection keeps failing after I reconnect the bot.",
            ),
            SupportTicket.objects.create(
                user=member,
                category=SupportTicket.Category.TECHNICAL,
                message="Telegram bot connection fails whenever I reconnect.",
            ),
            SupportTicket.objects.create(
                user=member,
                category=SupportTicket.Category.TECHNICAL,
                message="The bot connection fails after reconnecting Telegram.",
            ),
        ]

        self.assertEqual(build_support_issue_clusters(tickets), [])

    def test_different_ticket_categories_are_not_clustered_together(self):
        members = [
            User.objects.create_user(
                username=f"signal-category-member-{index}",
                email=f"signal-category-member-{index}@example.test",
            )
            for index in range(3)
        ]
        tickets = [
            SupportTicket.objects.create(
                user=members[0],
                category=SupportTicket.Category.BILLING,
                message="Payment completed but course access remains blocked for lessons.",
            ),
            SupportTicket.objects.create(
                user=members[1],
                category=SupportTicket.Category.TECHNICAL,
                message="Payment completed but course access remains blocked for lessons.",
            ),
            SupportTicket.objects.create(
                user=members[2],
                category=SupportTicket.Category.ACCESS,
                message="Payment completed but course access remains blocked for lessons.",
            ),
        ]

        self.assertEqual(build_support_issue_clusters(tickets), [])

