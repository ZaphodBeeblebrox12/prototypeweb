"""Tests for the permission-aware, read-only TradeThesis Admin Desk."""
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.academy.models import Course, CourseModule, Lesson

User = get_user_model()


class AdminDeskTests(TestCase):
    def test_shared_footer_wordmark_is_available_to_collectstatic(self):
        """The shared site footer is rendered on member pages in production."""
        wordmark = Path(settings.BASE_DIR) / "static" / "brand" / "tradethesis-wordmark.png"
        self.assertTrue(
            wordmark.is_file(),
            "Shared footer logo must exist under backend/static for collectstatic.",
        )

    def test_superuser_sees_live_course_metrics_and_management_links(self):
        admin = User.objects.create_superuser(
            username="desk-owner",
            email="desk-owner@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=admin, email=admin.email, verified=True, primary=True
        )
        Course.objects.create(
            title="Draft Course", slug="draft-course", status=Course.Status.DRAFT
        )
        published = Course.objects.create(
            title="Published Course",
            slug="published-course",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=published,
            title="Module One",
            slug="module-one",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="Visible Lesson",
            slug="visible-lesson",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=module,
            title="Unpublished Lesson",
            slug="unpublished-lesson",
            position=2,
            is_published=False,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Desk")
        self.assertContains(response, "Open Django administration")
        self.assertEqual(response.context["course_metrics"]["draft_courses"], 1)
        self.assertEqual(response.context["course_metrics"]["published_courses"], 1)
        self.assertEqual(response.context["course_metrics"]["published_lessons"], 1)
        self.assertEqual(response.context["course_metrics"]["courses_total"], 2)
        self.assertEqual(
            response.context["course_links"]["courses"],
            reverse("admin:academy_course_changelist"),
        )
        self.assertEqual(
            response.context["course_links"]["lessons"],
            reverse("admin:academy_lesson_changelist"),
        )

    def test_non_staff_user_is_forbidden(self):
        learner = User.objects.create_user(
            username="desk-learner", email="desk-learner@example.test"
        )
        EmailAddress.objects.create(
            user=learner, email=learner.email, verified=True, primary=True
        )
        self.client.force_login(learner)

        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "Admin Desk", status_code=403)

    def test_staff_without_course_content_authority_does_not_see_course_metrics(self):
        operator = User.objects.create_user(
            username="desk-operator",
            email="desk-operator@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_manage_course_content"])
        self.assertNotIn("course_metrics", response.context)
        self.assertContains(
            response,
            "Course publishing tools are visible only to administrators",
        )
        self.assertNotIn("accounts", response.context)
        self.assertNotIn("business_readiness", response.context)
        self.assertNotIn("runtime_readiness", response.context)


    def test_learner_directory_and_ban_action_are_available_in_creator_workspace(self):
        from apps.audit.models import AuditLog
        response = self.client.get(reverse("staff_admin_desk_accounts"), {"q": "desk-owner"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage learner accounts")
        learner = User.objects.create_user(username="desk-customer", email="desk-customer@example.test", password="pw")
        response = self.client.post(
            reverse("staff_admin_desk_account_action", args=[learner.pk]),
            {"action": "ban", "reason": "Requested by support"},
        )
        self.assertEqual(response.status_code, 302)
        learner.refresh_from_db()
        self.assertTrue(learner.is_banned)
        self.assertTrue(AuditLog.objects.filter(action="admin.account.ban").exists())

    def test_learner_management_never_mutates_staff_accounts(self):
        staff = User.objects.create_user(username="protected-staff", email="staff@example.test", password="pw", is_staff=True)
        response = self.client.post(
            reverse("staff_admin_desk_account_action", args=[staff.pk]),
            {"action": "deactivate", "reason": "Test reason for action"},
        )
        self.assertEqual(response.status_code, 404)
        staff.refresh_from_db()
        self.assertTrue(staff.is_active)

    def test_subscription_extension_adds_days_after_existing_expiry(self):
        from datetime import timedelta
        from apps.subscriptions.models import Plan, Subscription, SubscriptionHistory
        plan = Plan.objects.create(name="One-time Pro", tier=Plan.Tier.PRO, is_active=True)
        original_expiry = timezone.now() + timedelta(days=12)
        sub = Subscription.objects.create(
            user=self.admin, plan=plan, status=Subscription.Status.ACTIVE,
            is_active=True, started_at=timezone.now(), expires_at=original_expiry,
        )
        response = self.client.post(
            reverse("staff_admin_desk_subscription_action", args=[sub.pk]),
            {"action": "extend", "days": "30", "reason": "Goodwill access extension"},
        )
        self.assertEqual(response.status_code, 302)
        sub.refresh_from_db()
        self.assertGreater(sub.expires_at, original_expiry + timedelta(days=29))
        self.assertLess(sub.expires_at, original_expiry + timedelta(days=31))
        self.assertTrue(SubscriptionHistory.objects.filter(
            subscription=sub, event_type=SubscriptionHistory.EventType.RENEWED
        ).exists())

    def test_subscription_cancellation_and_complimentary_grant(self):
        from datetime import timedelta
        from apps.subscriptions.models import Plan, Subscription, SubscriptionHistory
        plan = Plan.objects.create(name="Cancelable Pro", tier=Plan.Tier.PRO, is_active=True)
        sub = Subscription.objects.create(
            user=self.admin, plan=plan, status=Subscription.Status.ACTIVE,
            is_active=True, started_at=timezone.now(), expires_at=timezone.now() + timedelta(days=30),
        )
        response = self.client.post(
            reverse("staff_admin_desk_subscription_action", args=[sub.pk]),
            {"action": "cancel", "reason": "Customer requested immediate cancellation"},
        )
        self.assertEqual(response.status_code, 302)
        sub.refresh_from_db()
        self.assertEqual(sub.status, Subscription.Status.CANCELED)
        self.assertFalse(sub.is_active)

        learner = User.objects.create_user(username="grant-target", email="grant@example.test", password="pw")
        hidden = Plan.objects.create(
            name="Courtesy Access", tier=Plan.Tier.PRO, is_active=True, is_hidden=True,
        )
        response = self.client.post(reverse("staff_admin_desk_subscriptions"), {
            "action": "grant", "user": str(learner.pk), "plan": str(hidden.pk),
            "duration_days": "30", "reason": "Goodwill access for learner",
        })
        self.assertEqual(response.status_code, 302)
        granted = Subscription.objects.get(user=learner, plan=hidden)
        self.assertTrue(granted.is_admin_grant)
        self.assertTrue(SubscriptionHistory.objects.filter(
            subscription=granted, event_type=SubscriptionHistory.EventType.ADMIN_GRANTED
        ).exists())

    def test_business_settings_save_and_tax_enable_confirmation(self):
        from apps.payments.models import BillingSettings
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
        from apps.payments.models import Invoice
        invoice = Invoice.objects.create(
            invoice_number="TT-TEST-0001", seller_name="TradeThesis",
            description="One-time course purchase", customer_name="Example Learner",
            customer_email="learner@example.test", subtotal_cents=99900,
            total_cents=99900, currency="INR", transaction_reference="order_test_001",
        )
        response = self.client.get(reverse("staff_admin_desk_finance"), {"tab": "invoices"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TT-TEST-0001")
        detail = self.client.get(reverse("staff_admin_desk_invoice_detail", args=[invoice.pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Print / Save as PDF")
        self.assertContains(detail, "Example Learner")

    def test_business_overview_and_operational_links_use_real_filters(self):
        admin = User.objects.create_superuser(
            username="desk-owner-2",
            email="desk-owner-2@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=admin, email=admin.email, verified=True, primary=True
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("accounts", response.context)
        self.assertIn("subscriptions", response.context)
        self.assertIn("jobs", response.context)
        self.assertIn("telegram", response.context)
        self.assertIn("policy_readiness", response.context)
        self.assertFalse(response.context["policy_readiness"]["ready"])
        self.assertIn("business_readiness", response.context)
        self.assertFalse(response.context["business_readiness"]["ready"])
        self.assertIn("runtime_readiness", response.context)
        self.assertContains(response, "Business &amp; invoice setup")
        self.assertContains(response, "Launch configuration")
        self.assertTrue(any(
            item["reason"] == "Placeholder content must be replaced and approved"
            for item in response.context["policy_readiness"]["items"]
        ))
        self.assertContains(response, "Checkout consent is blocked")
        self.assertEqual(
            response.context["accounts"]["links"]["users"],
            reverse("staff_admin_desk_accounts"),
        )

        expiring = parse_qs(urlsplit(
            response.context["subscriptions"]["links"]["expiring_soon"]
        ).query)
        self.assertEqual(expiring["is_active__exact"], ["1"])
        self.assertEqual(expiring["status__exact"], ["active"])
        self.assertTrue(expiring["expires_at__gt"][0])
        self.assertTrue(expiring["expires_at__lte"][0])

        recently_expired = parse_qs(urlsplit(
            response.context["subscriptions"]["links"]["recently_expired"]
        ).query)
        self.assertEqual(recently_expired["status__exact"], ["expired"])
        self.assertTrue(recently_expired["expires_at__gte"][0])
        self.assertTrue(recently_expired["expires_at__lte"][0])

        failed_access = parse_qs(urlsplit(
            response.context["telegram"]["links"]["failed"]
        ).query)
        self.assertEqual(failed_access["status__exact"], ["failed"])
        self.assertTrue(failed_access["created_at__gte"][0])

        failed_jobs = parse_qs(urlsplit(
            response.context["jobs"]["links"]["failed"]
        ).query)
        self.assertEqual(failed_jobs["status__exact"], ["failed"])
        self.assertTrue(failed_jobs["updated_at__gte"][0])

        stalled_jobs = parse_qs(urlsplit(
            response.context["jobs"]["links"]["stalled"]
        ).query)
        self.assertEqual(stalled_jobs["queue_state"], ["stalled"])

        # Exercise destinations, not only their query strings. These requests
        # surface invalid Django Admin lookups and missing permissions.
        destinations = [
            response.context["subscriptions"]["links"]["expiring_soon"],
            response.context["subscriptions"]["links"]["recently_expired"],
            response.context["telegram"]["links"]["failed"],
            response.context["jobs"]["links"]["pending"],
            response.context["jobs"]["links"]["failed"],
            response.context["jobs"]["links"]["stalled"],
        ]
        for destination in destinations:
            with self.subTest(destination=destination):
                self.assertEqual(self.client.get(destination).status_code, 200)

