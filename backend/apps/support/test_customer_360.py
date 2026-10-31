"""Tests for the permission-scoped Customer 360 view in the Admin Desk."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.support.models import AffiliateLink, SupportTicket, TicketMessage
from apps.bot_integration.models import TelegramAccount, DiscordAccount, UserChannelAssignment
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
        unlinked_member = User.objects.create_user(
            username="customer-360-no-ticket",
            email="customer-360-no-ticket@example.test",
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[unlinked_member.pk])
        )

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

        unrelated_reviewer = User.objects.create_user(
            username="customer-360-unrelated-reviewer",
            email="customer-360-unrelated-reviewer@example.test",
            is_staff=True,
        )
        self.client.force_login(unrelated_reviewer)
        forbidden = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[restricted_member.pk])
        )
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_login(restricted_reviewer)
        allowed = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[restricted_member.pk])
        )
        self.assertEqual(allowed.status_code, 200, allowed.content)

    def test_staff_requester_can_open_reviewer_visible_support_profile_without_commercial_records(self):
        staff_requester = User.objects.create_user(
            username="customer-360-staff-requester",
            email="customer-360-staff-requester@example.test",
            is_staff=True,
        )
        staff_ticket = SupportTicket.objects.create(
            user=staff_requester,
            category=SupportTicket.Category.TECHNICAL,
            message="My staff test account cannot open a staging support page.",
        )
        self.client.force_login(
            User.objects.create_user(
                username="customer-360-support-reviewer",
                email="customer-360-support-reviewer@example.test",
                is_staff=True,
            )
        )

        response = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[staff_requester.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.context["is_internal_account"])
        self.assertContains(response, "Internal staff requester")
        self.assertContains(response, staff_ticket.short_id)
        self.assertFalse(response.context["can_view_subscriptions"])
        self.assertFalse(response.context["can_view_payments"])
        self.assertFalse(response.context["can_view_invoices"])
        self.assertFalse(response.context["can_view_academy_records"])
        self.assertFalse(response.context["can_view_security_events"])
        self.assertNotContains(response, "Payments, refunds &amp; disputes")
        self.assertNotContains(response, "Subscriptions &amp; access history")
        self.assertNotContains(response, "Course access")

    def test_superuser_requester_can_open_only_the_visible_support_profile(self):
        admin_requester = User.objects.create_superuser(
            username="customer-360-admin-requester",
            email="customer-360-admin-requester@example.test",
            password="test-password-123!",
        )
        ticket = SupportTicket.objects.create(
            user=admin_requester,
            category=SupportTicket.Category.TECHNICAL,
            message="Internal administrator test request.",
        )
        reviewer = User.objects.create_user(
            username="customer-360-admin-request-reviewer",
            email="customer-360-admin-request-reviewer@example.test",
            is_staff=True,
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[admin_requester.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.context["is_internal_account"])
        self.assertContains(response, "Internal staff requester")
        self.assertContains(response, ticket.short_id)
        self.assertFalse(response.context["can_view_payments"])
        self.assertFalse(response.context["can_view_subscriptions"])
        self.assertFalse(response.context["can_view_academy_records"])
        self.assertFalse(response.context["can_view_security_events"])

    def test_support_ticket_detail_links_to_customer_360(self):
        response = self.client.get(
            reverse("staff_admin_desk_support_ticket", args=[self.ticket.pk])
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, self.url())
        self.assertContains(response, "Customer 360")


    def test_customer_360_uses_current_bot_integration_link_records(self):
        TelegramAccount.objects.create(
            user=self.member,
            chat_id=710000001,
            telegram_user_id=710000001,
            username="trade_member",
            is_active=True,
        )
        DiscordAccount.objects.create(
            user=self.member,
            discord_user_id="880000001",
            guild_id="990000001",
            username="trade_member",
            roles=["role-1"],
            is_active=True,
        )

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["telegram_community_status"], "Linked")
        self.assertEqual(response.context["discord_community_status"], "Linked")
        self.assertContains(response, "Telegram · Linked")
        self.assertContains(response, "Discord · Linked")

    def test_customer_360_flags_orphaned_telegram_access_for_cleanup(self):
        UserChannelAssignment.objects.create(
            user=self.member,
            platform="telegram",
            external_id="-100710000050",
            is_active=True,
        )

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.context["telegram_community_status"],
            "Access cleanup pending",
        )
        self.assertContains(response, "Telegram · Access cleanup pending")
        self.assertNotContains(response, "Telegram · Not linked")

    def test_customer_360_distinguishes_legacy_login_from_bot_community_link(self):
        self.member.telegram_id = 710000002
        self.member.telegram_verified = True
        self.member.discord_id = "880000002"
        self.member.discord_verified = True
        self.member.save(update_fields=[
            "telegram_id", "telegram_verified", "discord_id", "discord_verified",
        ])

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["telegram_community_status"], "Login only")
        self.assertEqual(response.context["discord_community_status"], "Legacy identity only")
        self.assertContains(response, "Telegram · Login only")
        self.assertContains(response, "Discord · Legacy identity only")
        self.assertNotContains(response, "Telegram · Linked")
