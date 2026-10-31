"""Tests for the permission-scoped Customer 360 view in the Admin Desk."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.support.models import AffiliateLink, SupportTicket, TicketMessage
from apps.subscriptions.models import Plan

User = get_user_model()


class Customer360Tests(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_superuser(
            username="customer-360-admin",
            email="customer-360-admin@example.test",
            password="test-password-123!",
        )
        self.member = User.objects.create_user(
            username="customer-360-member",
            email="customer-360-member@example.test",
            first_name="Taylor",
            last_name="Trader",
        )
        self.ticket = SupportTicket.objects.create(
            user=self.member,
            category=SupportTicket.Category.BILLING,
            message="I completed payment but my course access is missing.",
        )
        self.client.force_login(self.reviewer)

    def url(self):
        return reverse("staff_admin_desk_customer_360", args=[self.member.pk])

    def test_customer_360_combines_account_support_and_permissioned_sections(self):
        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Customer 360")
        self.assertContains(response, "Taylor Trader")
        self.assertContains(response, "customer-360-member")
        self.assertContains(response, "customer-360-member@example.test")
        self.assertContains(response, "Support history")
        self.assertContains(response, self.ticket.short_id)
        self.assertContains(response, "Subscriptions &amp; access history")
        self.assertContains(response, "Payments, refunds &amp; disputes")
        self.assertContains(response, "Course access")
        self.assertContains(response, "Learning progress")
        self.assertEqual(response.context["stats"]["open_tickets"], 1)
        self.assertTrue(response.context["can_view_subscriptions"])
        self.assertTrue(response.context["can_view_payments"])
        self.assertTrue(response.context["can_view_academy_records"])

    def test_customer_360_shows_public_conversation_but_never_internal_ticket_notes(self):
        TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.member,
            body="I can share the invoice number if needed.",
            is_internal=False,
        )
        TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.reviewer,
            body="Internal gateway reconciliation note - do not disclose.",
            is_internal=True,
        )

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "I can share the invoice number if needed.")
        self.assertNotContains(response, "Internal gateway reconciliation note")
        self.assertNotContains(response, "provider_payment_id")
        self.assertNotContains(response, "ip_address")
        self.assertNotContains(response, "user_agent")

    def test_support_reviewer_without_finance_or_learning_permissions_sees_only_allowed_sections(self):
        reviewer = User.objects.create_user(
            username="customer-360-support-only",
            email="customer-360-support-only@example.test",
            is_staff=True,
        )
        self.client.force_login(reviewer)

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Taylor Trader")
        self.assertContains(response, "Support history")
        self.assertNotContains(response, "Subscriptions &amp; access history")
        self.assertNotContains(response, "Payments, refunds &amp; disputes")
        self.assertNotContains(response, "Course access")
        self.assertFalse(response.context["can_view_subscriptions"])
        self.assertFalse(response.context["can_view_payments"])
        self.assertFalse(response.context["can_view_academy_records"])

    def test_customer_360_refuses_profiles_without_a_visible_ticket_or_global_account_permission(self):
        reviewer = User.objects.create_user(
            username="customer-360-limited",
            email="customer-360-limited@example.test",
            is_staff=True,
        )
        self.client.force_login(reviewer)

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 403)

    def test_customer_360_obeys_existing_plan_based_ticket_reviewer_scope(self):
        restricted_reviewer = User.objects.create_user(
            username="customer-360-authorised",
            email="customer-360-authorised@example.test",
            is_staff=True,
        )
        restricted_plan = Plan.objects.create(
            name="Customer 360 restricted plan",
            tier=Plan.Tier.BASIC,
            is_hidden=True,
        )
        restricted_plan.ticket_approvers.add(restricted_reviewer)
        affiliate = AffiliateLink.objects.create(
            name="Restricted customer route",
            url="https://example.test/customer-360",
            referral_code="C360-RESTRICTED",
            plan=restricted_plan,
        )
        restricted_member = User.objects.create_user(
            username="customer-360-restricted-member",
            email="customer-360-restricted-member@example.test",
        )
        SupportTicket.objects.create(
            user=restricted_member,
            category=SupportTicket.Category.ACCESS,
            affiliate_link=affiliate,
            plan=restricted_plan,
            message="Restricted plan access request.",
        )

        self.client.force_login(self.reviewer)
        forbidden = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[restricted_member.pk])
        )
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_login(restricted_reviewer)
        allowed = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[restricted_member.pk])
        )
        self.assertEqual(allowed.status_code, 200, allowed.content)

    def test_support_ticket_detail_links_to_customer_360(self):
        response = self.client.get(
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, self.url())
        self.assertContains(response, "Customer 360")
