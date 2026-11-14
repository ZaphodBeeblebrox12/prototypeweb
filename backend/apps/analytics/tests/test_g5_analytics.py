"""G5: signup attribution, last-touch purchase credit, analytics reports."""
import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from apps.analytics.models import SignupAttribution
from apps.analytics.services.attribution import (
    attribute_purchase, capture_signup_attribution)
from apps.analytics.services import report
from apps.campaigns.models import Audience, Campaign, CampaignMetrics, CampaignRecipient
from apps.emailing.models import Delivery, Template, TemplateVersion
from apps.events.models import record_event
from apps.promotions.models import Coupon, CouponRedemption
from rest_framework.test import APIClient

User = get_user_model()


class SignupAttributionTests(TestCase):
    def test_capture_first_touch(self):
        u = User.objects.create_user(username="a1", password="pw")
        obj, created = capture_signup_attribution(
            u, utm={"utm_source": "google", "utm_campaign": "launch"})
        self.assertTrue(created)
        self.assertEqual(obj.utm_source, "google")
        self.assertEqual(obj.utm_campaign, "launch")

    def test_first_touch_wins_on_repeat(self):
        u = User.objects.create_user(username="a2", password="pw")
        capture_signup_attribution(u, utm={"utm_source": "first"})
        obj, created = capture_signup_attribution(u, utm={"utm_source": "second"})
        self.assertFalse(created)
        self.assertEqual(obj.utm_source, "first")  # first touch preserved


class LastTouchTests(TestCase):
    def _template(self):
        import uuid
        t = Template.objects.create(name=f"T-{uuid.uuid4().hex[:6]}", kind="marketing")
        return TemplateVersion.objects.create(template=t, version_number=1, editor_mode="html",
                                              subject="s", html="<p>x</p>")

    def _delivery(self, user, days_ago, campaign=None):
        v = self._template()
        d = Delivery.objects.create(
            idempotency_key=f"lt-{user.username}-{days_ago}-{v.id}", template_version=v, user=user,
            to_email=f"{user.username}@x.com", kind="marketing", subject="s",
            state=Delivery.State.SENT, provider="stub",
            sent_at=timezone.now() - datetime.timedelta(days=days_ago))
        if campaign:
            CampaignRecipient.objects.create(
                campaign=campaign, user=user, email=d.to_email, status="sent", delivery=d)
        return d

    def test_last_touch_before_purchase_gets_credit(self):
        u = User.objects.create_user(username="lt1", password="pw")
        aud = Audience.objects.create(name="A", rules={})
        tv = self._template()
        camp = Campaign.objects.create(name="Launch", template_version=tv, audience=aud)
        self._delivery(u, days_ago=3)                        # older, no campaign link
        d2 = self._delivery(u, days_ago=1, campaign=camp)    # last touch
        purchase_at = timezone.now()
        credit = attribute_purchase(u, purchase_at)
        self.assertIsNotNone(credit)
        self.assertEqual(credit["campaign_name"], "Launch")

    def test_no_delivery_no_credit(self):
        u = User.objects.create_user(username="lt2", password="pw")
        self.assertIsNone(attribute_purchase(u, timezone.now()))

    def test_delivery_after_purchase_not_credited(self):
        u = User.objects.create_user(username="lt3", password="pw")
        self._delivery(u, days_ago=-1)  # sent AFTER purchase
        self.assertIsNone(attribute_purchase(u, timezone.now() - datetime.timedelta(days=2)))


class ReportTests(TestCase):
    def test_signup_analytics_aggregates_purchases(self):
        u = User.objects.create_user(username="r1", password="pw")
        for i in range(3):
            record_event("purchase.completed", dedupe_key=f"rep{i}",
                         user_id=u.id, payload={"amount": 500})
        result = report.signup_analytics(days=7)
        self.assertEqual(result["total_purchases"], 3)
        self.assertEqual(result["purchases_per_day"][0]["revenue_cents"], 1500)

    def test_email_performance_counts_states(self):
        u = User.objects.create_user(username="r2", password="pw")
        t = Template.objects.create(name="T", kind="marketing")
        v = TemplateVersion.objects.create(template=t, version_number=1, editor_mode="html",
                                           subject="s", html="<p>x</p>")
        Delivery.objects.create(idempotency_key="e1", template_version=v, user=u,
                                to_email="r2@x.com", kind="marketing", subject="s",
                                state=Delivery.State.SENT, provider="stub")
        Delivery.objects.create(idempotency_key="e2", template_version=v, user=u,
                                to_email="r2@x.com", kind="marketing", subject="s",
                                state=Delivery.State.BOUNCED, provider="stub")
        result = report.email_performance(days=7)
        self.assertEqual(result["sent"], 1)
        self.assertEqual(result["bounced"], 1)

    def test_campaign_performance_from_metrics(self):
        u = User.objects.create_user(username="r3", password="pw")
        aud = Audience.objects.create(name="A", rules={})
        t = Template.objects.create(name="T", kind="marketing")
        tv = TemplateVersion.objects.create(template=t, version_number=1, editor_mode="html",
                                            subject="s", html="<p>x</p>")
        camp = Campaign.objects.create(name="C", template_version=tv, audience=aud)
        CampaignMetrics.objects.create(campaign=camp, total=5, sent=4, failed=1)
        result = report.campaign_performance()
        self.assertEqual(result[0]["campaign"], "C")
        self.assertEqual(result[0]["sent"], 4)


class PromotionReportTests(TestCase):
    def test_promotion_performance_sums_discount_cents(self):
        coupon = Coupon.objects.create(
            code="PROMO10",
            name="Promotion test",
            discount_type=Coupon.DiscountType.PERCENT,
            percent_off=10,
        )
        first_user = User.objects.create_user(username="promo-first")
        second_user = User.objects.create_user(username="promo-second")
        CouponRedemption.objects.create(
            coupon=coupon,
            user=first_user,
            discount_cents=250,
        )
        CouponRedemption.objects.create(
            coupon=coupon,
            user=second_user,
            discount_cents=175,
        )

        result = report.promotion_performance()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["code"], "PROMO10")
        self.assertEqual(result[0]["redemptions"], 2)
        self.assertEqual(result[0]["total_discount_cents"], 425)

    def test_promotion_performance_handles_no_redemptions(self):
        self.assertEqual(report.promotion_performance(), [])


class AnalyticsOverviewPermissionTests(TestCase):
    required_permissions = (
        ("events", "view_event"),
        ("emailing", "view_delivery"),
        ("campaigns", "view_campaign"),
        ("promotions", "view_couponredemption"),
        ("growth", "view_referralreward"),
    )

    def _grant_growth_analytics(self, user):
        permissions = []
        for app_label, codename in self.required_permissions:
            content_type = ContentType.objects.get(
                app_label=app_label,
                model=codename.removeprefix("view_"),
            )
            permissions.append(
                Permission.objects.get(
                    content_type=content_type,
                    codename=codename,
                )
            )
        user.user_permissions.add(*permissions)

    def _get(self, user):
        client = APIClient()
        client.force_authenticate(user)
        return client.get("/api/analytics/overview/")

    def test_generic_staff_without_growth_grants_is_denied(self):
        staff = User.objects.create_user(username="analytics-unprivileged")
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])

        response = self._get(staff)

        self.assertEqual(response.status_code, 403)

    def test_growth_staff_with_all_report_grants_is_allowed(self):
        staff = User.objects.create_user(username="analytics-growth-staff")
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        self._grant_growth_analytics(staff)

        response = self._get(staff)

        self.assertEqual(response.status_code, 200)
        self.assertIn("promotions", response.data)

    def test_application_admin_is_allowed(self):
        admin = User.objects.create_user(
            username="analytics-admin",
            role=User.Role.ADMIN,
        )

        response = self._get(admin)

        self.assertEqual(response.status_code, 200)
