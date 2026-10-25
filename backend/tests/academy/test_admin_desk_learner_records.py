from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academy.models import (
    Course,
    CourseEntitlement,
    CourseModule,
    Lesson,
    LessonProgress,
)
from apps.payments.models import Invoice, PaymentIntent
from apps.subscriptions.models import Plan

User = get_user_model()


class AdminDeskLearnerRecordsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="desk-owner",
            email="owner@example.test",
            password="Safe-test-password-123!",
            is_staff=True,
            is_superuser=True,
        )
        self.learner = User.objects.create_user(
            username="learner-one",
            email="learner@example.test",
            password="Safe-test-password-123!",
        )
        self.course = Course.objects.create(
            title="Trading Path",
            slug="trading-path-admin-progress",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title="Foundations",
            slug="foundations-admin-progress",
            position=1,
            is_published=True,
        )
        self.completed = Lesson.objects.create(
            module=self.module,
            title="Support and resistance",
            slug="support-resistance-admin-progress",
            position=1,
            is_published=True,
        )
        self.in_progress = Lesson.objects.create(
            module=self.module,
            title="Reading price action",
            slug="price-action-admin-progress",
            position=2,
            is_published=True,
        )
        Lesson.objects.create(
            module=self.module,
            title="Unreleased lesson",
            slug="unpublished-admin-progress",
            position=3,
            is_published=False,
        )
        now = timezone.now()
        LessonProgress.objects.create(
            user=self.learner,
            lesson=self.completed,
            status=LessonProgress.Status.COMPLETED,
            started_at=now - timedelta(hours=1),
            completed_at=now - timedelta(minutes=30),
            last_seen_at=now - timedelta(minutes=30),
            time_spent_seconds=125,
        )
        LessonProgress.objects.create(
            user=self.learner,
            lesson=self.in_progress,
            status=LessonProgress.Status.IN_PROGRESS,
            started_at=now - timedelta(minutes=15),
            last_seen_at=now - timedelta(minutes=5),
            time_spent_seconds=55,
        )

        plan = Plan.objects.create(
            name="Trading Path one-time",
            tier=Plan.Tier.BASIC,
            is_hidden=True,
        )
        payment = PaymentIntent.objects.create(
            user=self.learner,
            plan=plan,
            amount=99900,
            currency="INR",
            provider=PaymentIntent.Provider.RAZORPAY,
            payment_method=PaymentIntent.PaymentMethod.UPI,
            status=PaymentIntent.Status.SUCCESS,
            provider_reference="order_admin_test_123",
            provider_payment_id="pay_admin_test_456",
        )
        CourseEntitlement.objects.create(
            user=self.learner,
            course=self.course,
            payment_intent=payment,
            source=CourseEntitlement.Source.PURCHASE,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=now - timedelta(days=1),
            expires_at=now + timedelta(days=30),
        )
        Invoice.objects.create(
            invoice_number="TT-TEST-0001",
            payment_intent=payment,
            issue_date=now.date(),
            issued_at=now,
            currency="INR",
            seller_name="TradeThesis",
            customer_name="Learner One",
            customer_email=self.learner.email,
            description="Trading Path course",
            subtotal_cents=99900,
            total_cents=99900,
            transaction_reference="txn_admin_test_789",
        )
        self.zero_progress_course = Course.objects.create(
            title="Bollinger Bands",
            slug="bollinger-bands-zero-progress",
            status=Course.Status.PUBLISHED,
        )
        zero_module = CourseModule.objects.create(
            course=self.zero_progress_course,
            title="Getting started",
            slug="getting-started-zero-progress",
            position=1,
            is_published=True,
        )
        Lesson.objects.create(
            module=zero_module,
            title="First lesson",
            slug="first-lesson-zero-progress",
            position=1,
            is_published=True,
        )
        CourseEntitlement.objects.create(
            user=self.learner,
            course=self.zero_progress_course,
            source=CourseEntitlement.Source.ADMIN,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=now - timedelta(hours=1),
        )
        self.client.force_login(self.owner)

    def test_account_detail_shows_scoped_course_progress_access_and_invoice_records(self):
        response = self.client.get(
            reverse("staff_admin_desk_account_detail", args=[self.learner.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course progress")
        self.assertContains(response, "Course access")
        self.assertContains(response, "1 / 2 lessons")
        self.assertContains(response, "50%")
        self.assertContains(response, "Bollinger Bands")
        self.assertContains(response, "0 / 1 lessons")
        self.assertContains(response, "Trading Path")
        self.assertContains(response, "pay_admin_test_456")
        self.assertContains(response, "TT-TEST-0001")
        self.assertContains(response, "txn_admin_test_789")
        self.assertNotContains(response, "Unreleased lesson")

    def test_course_and_finance_sections_are_permission_gated(self):
        staff = User.objects.create_user(
            username="account-only-staff",
            password="Safe-test-password-123!",
            is_staff=True,
            is_superuser=False,
        )
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        user_content_type = ContentType.objects.get_for_model(User)
        view_user = Permission.objects.get(
            content_type=user_content_type,
            codename="view_user",
        )
        staff.user_permissions.add(view_user)
        self.client.force_login(staff)

        response = self.client.get(
            reverse("staff_admin_desk_account_detail", args=[self.learner.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "pay_admin_test_456")
        self.assertNotContains(response, "TT-TEST-0001")
