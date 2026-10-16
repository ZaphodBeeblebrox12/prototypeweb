from calendar import monthrange
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academy.models import Course, CourseEntitlement, CourseOffer
from apps.bot_integration.access import compute_target_access
from apps.bot_integration.models import (
    PlanChannelMapping,
    TelegramAccount,
    UserChannelAssignment,
)
from apps.bot_integration.services.channel_sync import (
    build_channel_display,
    get_telegram_access_state,
)
from apps.payments.models import PaymentIntent
from apps.payments.services import activate_paid_subscription, apply_refund_policy
from apps.subscriptions.models import Plan, PlanPrice

User = get_user_model()


class CourseCommunityAccessTests(TestCase):
    """Included community access has a separate clock from course access."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="construct-buyer", password="Test-password-123!"
        )
        self.plan = Plan.objects.create(
            name="CONSTRUCT one-time", tier=Plan.Tier.BASIC,
            is_active=True, is_hidden=True,
        )
        self.price = PlanPrice.objects.create(
            plan=self.plan, interval=PlanPrice.Interval.ONE_TIME,
            price_cents=1700000, currency="INR", is_active=True,
        )
        self.course = Course.objects.create(
            title="CONSTRUCT", slug="construct",
            status=Course.Status.PUBLISHED,
        )
        self.offer = CourseOffer.objects.create(
            course=self.course, name="CONSTRUCT", slug="construct",
            plan=self.plan, access_duration_days=None,
            community_access_months=12, is_active=True,
        )
        self.offer.full_clean()
        self.intent = PaymentIntent.objects.create(
            user=self.user, plan=self.plan, plan_price=self.price,
            amount=1700000, base_amount_cents=1700000, currency="INR",
            provider=PaymentIntent.Provider.RAZORPAY,
            status=PaymentIntent.Status.PENDING,
        )
        PlanChannelMapping.objects.create(
            plan=self.plan, platform="telegram",
            external_id="-100-construction-community", name="CONSTRUCT community",
        )
        PlanChannelMapping.objects.create(
            plan=self.plan, platform="discord",
            external_id="construct-member-role", name="CONSTRUCT members",
        )

    def test_verified_purchase_grants_a_separate_12_calendar_month_community_term(self):
        self.assertFalse(compute_target_access(self.user.pk).has_plan)

        activated, entitlement = activate_paid_subscription(self.intent)

        self.assertTrue(activated)
        entitlement.refresh_from_db()
        self.assertIsNone(entitlement.expires_at, "Course access remains permanent.")
        self.assertIsNotNone(entitlement.community_access_granted_at)
        granted = entitlement.community_access_granted_at
        expiry = entitlement.community_access_expires_at
        self.assertEqual((expiry.year, expiry.month), (granted.year + 1, granted.month))
        self.assertEqual(
            expiry.day,
            min(granted.day, monthrange(expiry.year, expiry.month)[1]),
        )
        self.assertEqual(
            (expiry.hour, expiry.minute, expiry.second),
            (granted.hour, granted.minute, granted.second),
        )
        target = compute_target_access(self.user.pk)
        self.assertTrue(target.has_plan)
        self.assertEqual(target.telegram_ids, {"-100-construction-community"})
        self.assertEqual(target.discord_ids, {"construct-member-role"})

        self.assertEqual(get_telegram_access_state(self.user)["state"], "not_linked")
        TelegramAccount.objects.create(user=self.user, chat_id=987654, telegram_user_id=987654)
        self.assertEqual(get_telegram_access_state(self.user)["state"], "pending")
        paid = build_channel_display(self.user)["paid"]
        community_row = next(row for row in paid if row["name"] == "CONSTRUCT community")
        self.assertTrue(community_row["entitled"])

        UserChannelAssignment.objects.create(
            user=self.user, platform="telegram", external_id="-100-construction-community"
        )
        self.assertEqual(get_telegram_access_state(self.user)["state"], "ready")

    def test_expired_community_term_no_longer_grants_channel_or_role_targets(self):
        _activated, entitlement = activate_paid_subscription(self.intent)
        CourseEntitlement.objects.filter(pk=entitlement.pk).update(
            community_access_expires_at=timezone.now() - timedelta(seconds=1)
        )

        target = compute_target_access(self.user.pk)

        self.assertFalse(target.has_plan)
        self.assertEqual(target.telegram_ids, set())
        self.assertEqual(target.discord_ids, set())
        entitlement.refresh_from_db()
        self.assertTrue(entitlement.has_access, "The separate community expiry must not shorten course access.")

    def test_full_refund_removes_bundled_community_access(self):
        _activated, entitlement = activate_paid_subscription(self.intent)
        PaymentIntent.objects.filter(pk=self.intent.pk).update(
            refunded_cents=self.intent.amount
        )
        self.intent.refresh_from_db()

        self.assertTrue(apply_refund_policy(self.intent))
        entitlement.refresh_from_db()
        self.assertEqual(entitlement.status, CourseEntitlement.Status.REVOKED)
        target = compute_target_access(self.user.pk)
        self.assertFalse(target.has_plan)
        self.assertEqual(target.telegram_ids, set())
        self.assertEqual(target.discord_ids, set())

    def test_community_access_is_shown_after_course_access_expires(self):
        _activated, entitlement = activate_paid_subscription(self.intent)
        CourseEntitlement.objects.filter(pk=entitlement.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("academy:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Community access")
        self.assertContains(response, "Available until")
        self.assertTrue(compute_target_access(self.user.pk).has_plan)

    def test_community_term_cannot_be_changed_after_payment_history_exists(self):
        self.offer.community_access_months = 6

        with self.assertRaises(ValidationError) as caught:
            self.offer.full_clean()

        self.assertIn("frozen after a payment intent exists", str(caught.exception))
