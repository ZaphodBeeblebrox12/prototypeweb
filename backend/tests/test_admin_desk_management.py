"""Regression tests for creator-facing Admin Desk management workflows."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.payments.models import BillingSettings, Invoice
from apps.subscriptions.models import Plan, Subscription, SubscriptionHistory

User = get_user_model()


class AdminDeskManagementTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="desk-management-owner",
            email="desk-management-owner@example.test",
            password="test-password-123!",
        )
        self.learner = User.objects.create_user(
            username="desk-management-learner",
            email="desk-management-learner@example.test",
            password="test-password-123!",
        )
        self.client.force_login(self.owner)

    def test_learner_directory_and_ban_action_are_available_in_creator_workspace(self):
        response = self.client.get(
            reverse("staff_admin_desk_accounts"),
            {"q": "desk-management-learner"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage learner accounts")
        self.assertContains(response, "desk-management-learner")

        response = self.client.post(
            reverse("staff_admin_desk_account_action", args=[self.learner.pk]),
            {"action": "ban", "reason": "Requested by customer support"},
        )
        self.assertEqual(response.status_code, 302)
        self.learner.refresh_from_db()
        self.assertTrue(self.learner.is_banned)
        self.assertTrue(AuditLog.objects.filter(action="admin.account.ban").exists())

    def test_learner_management_never_mutates_staff_accounts(self):
        staff = User.objects.create_user(
            username="protected-staff", email="staff@example.test",
            password="test-password-123!", is_staff=True,
        )
        response = self.client.post(
            reverse("staff_admin_desk_account_action", args=[staff.pk]),
            {"action": "deactivate", "reason": "Test reason for action"},
        )
        self.assertEqual(response.status_code, 404)
        staff.refresh_from_db()
        self.assertTrue(staff.is_active)

    def test_subscription_extension_adds_days_after_existing_expiry(self):
        plan = Plan.objects.create(
            name="Management Basic", tier=Plan.Tier.BASIC, is_active=True,
        )
        original_expiry = timezone.now() + timedelta(days=12)
        subscription = Subscription.objects.create(
            user=self.learner, plan=plan, status=Subscription.Status.ACTIVE,
            is_active=True, started_at=timezone.now(), expires_at=original_expiry,
        )
        response = self.client.post(
            reverse("staff_admin_desk_subscription_action", args=[subscription.pk]),
            {"action": "extend", "days": "30", "reason": "Goodwill access extension"},
        )
        self.assertEqual(response.status_code, 302)
        subscription.refresh_from_db()
        self.assertGreater(subscription.expires_at, original_expiry + timedelta(days=29))
        self.assertLess(subscription.expires_at, original_expiry + timedelta(days=31))
        self.assertTrue(SubscriptionHistory.objects.filter(
            subscription=subscription, event_type=SubscriptionHistory.EventType.RENEWED,
        ).exists())
        self.assertTrue(AuditLog.objects.filter(action="admin.subscription.extend").exists())

    def test_subscription_extension_never_limits_permanent_access(self):
        plan = Plan.objects.create(
            name="Permanent Access", tier=Plan.Tier.BASIC, is_active=True,
        )
        subscription = Subscription.objects.create(
            user=self.learner, plan=plan, status=Subscription.Status.ACTIVE,
            is_active=True, started_at=timezone.now(), expires_at=None,
        )
        response = self.client.post(
            reverse("staff_admin_desk_subscription_action", args=[subscription.pk]),
            {"action": "extend", "days": "30", "reason": "Goodwill access extension"},
        )
        self.assertEqual(response.status_code, 302)
        subscription.refresh_from_db()
        self.assertIsNone(subscription.expires_at)
        self.assertFalse(SubscriptionHistory.objects.filter(
            subscription=subscription, event_type=SubscriptionHistory.EventType.RENEWED,
        ).exists())

    def test_subscription_cancel_and_complimentary_grant_use_audited_services(self):
        plan = Plan.objects.create(
            name="Management Basic", tier=Plan.Tier.BASIC, is_active=True,
        )
        subscription = Subscription.objects.create(
            user=self.learner, plan=plan, status=Subscription.Status.ACTIVE,
            is_active=True, started_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        response = self.client.post(
            reverse("staff_admin_desk_subscription_action", args=[subscription.pk]),
            {"action": "cancel", "reason": "Customer requested immediate cancellation"},
        )
        self.assertEqual(response.status_code, 302)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.Status.CANCELED)
        self.assertFalse(subscription.is_active)

        other = User.objects.create_user(
            username="desk-grant-target", email="desk-grant-target@example.test",
            password="test-password-123!",
        )
        hidden = Plan.objects.create(
            name="Courtesy Pro", tier=Plan.Tier.PRO, is_active=True, is_hidden=True,
        )
        response = self.client.post(reverse("staff_admin_desk_subscriptions"), {
            "action": "grant", "user": str(other.pk), "plan": str(hidden.pk),
            "duration_days": "30", "reason": "Goodwill access for learner",
        })
        self.assertEqual(response.status_code, 302)
        granted = Subscription.objects.get(user=other, plan=hidden)
        self.assertTrue(granted.is_admin_grant)
        self.assertTrue(SubscriptionHistory.objects.filter(
            subscription=granted, event_type=SubscriptionHistory.EventType.ADMIN_GRANTED,
        ).exists())
        self.assertTrue(AuditLog.objects.filter(action="admin.subscription.granted").exists())

    def test_business_settings_save_and_tax_enable_requires_confirmation(self):
        response = self.client.post(reverse("staff_admin_desk_business"), {
            "seller_name": "TradeThesis", "legal_name": "TradeThesis Learning",
            "address": "Gurugram, Haryana, India", "country": "in",
            "support_email": "help@tradethesis.example", "tax_registration_number": "",
            "invoice_prefix": "TT", "tax_enabled": "", "tax_label": "GST",
            "tax_rate_percentage": "0.00", "tax_inclusive": "", "confirm_tax_enable": "",
        })
        self.assertEqual(response.status_code, 302)
        settings = BillingSettings.objects.get(pk=1)
        self.assertEqual(settings.legal_name, "TradeThesis Learning")
        self.assertEqual(settings.country, "IN")
        self.assertFalse(settings.tax_enabled)

        response = self.client.post(reverse("staff_admin_desk_business"), {
            "seller_name": "TradeThesis", "legal_name": "TradeThesis Learning",
            "address": "Gurugram, Haryana, India", "country": "IN",
            "support_email": "help@tradethesis.example", "tax_registration_number": "",
            "invoice_prefix": "TT", "tax_enabled": "on", "tax_label": "GST",
            "tax_rate_percentage": "18.00", "tax_inclusive": "", "confirm_tax_enable": "",
        })
        self.assertEqual(response.status_code, 200)
        settings.refresh_from_db()
        self.assertFalse(settings.tax_enabled)

    def test_invoice_register_and_printable_invoice_view(self):
        invoice = Invoice.objects.create(
            invoice_number="TT-TEST-0001", seller_name="TradeThesis",
            description="One-time course purchase", customer_name="Example Learner",
            customer_email="learner@example.test", subtotal_cents=99900,
            total_cents=99900, currency="INR", transaction_reference="order_test_001",
        )
        response = self.client.get(
            reverse("staff_admin_desk_finance"), {"tab": "invoices"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TT-TEST-0001")
        detail = self.client.get(
            reverse("staff_admin_desk_invoice_detail", args=[invoice.pk]),
        )
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Print / Save as PDF")
        self.assertContains(detail, "Example Learner")
