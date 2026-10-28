import json
from datetime import timedelta

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.payments.models import PaymentIntent
from apps.subscriptions.models import (
    FREE_MEMBERSHIP_PRODUCT_SLUG,
    Plan,
    PlanPrice,
    Product,
    Subscription,
    SubscriptionHistory,
)
from apps.subscriptions.services import ensure_free_membership_plan

from .models import (
    Course,
    CourseEntitlement,
    CourseEntitlementEvent,
    CourseModule,
    CourseOffer,
    Lesson,
    PlanCourseAccess,
)
from .services import can_access_lesson, has_active_plan_access, sync_free_membership_course_access

User = get_user_model()


class FreeAcademyAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="free-access-learner",
            email="free-access@example.test",
            password="test-password",
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True,
        )
        self.client.force_login(self.user)
        self.course = Course.objects.create(
            title="Free Foundations",
            slug="free-foundations",
            summary="A short free course.",
            status=Course.Status.PUBLISHED,
            access_type=Course.AccessType.FREE,
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title="Foundations",
            slug="foundations",
            position=0,
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="First lesson",
            slug="first-lesson",
            position=0,
            content_markdown="## First lesson\n\nFree learning starts here.",
            is_published=True,
        )

    def test_free_course_requires_explicit_enrolment_and_grants_permanent_access(self):
        self.assertFalse(can_access_lesson(self.user, self.lesson))

        response = self.client.post(reverse("academy:enrol-free-course", args=[self.course.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("academy:course-detail", args=[self.course.slug]))

        entitlement = CourseEntitlement.objects.get(user=self.user, course=self.course)
        self.assertEqual(entitlement.source, CourseEntitlement.Source.COMPLIMENTARY)
        self.assertEqual(entitlement.status, CourseEntitlement.Status.ACTIVE)
        self.assertIsNone(entitlement.expires_at)
        self.assertTrue(can_access_lesson(self.user, self.lesson))
        self.assertEqual(CourseEntitlementEvent.objects.filter(entitlement=entitlement).count(), 1)

        self.client.post(reverse("academy:enrol-free-course", args=[self.course.slug]))
        self.assertEqual(CourseEntitlement.objects.filter(user=self.user, course=self.course).count(), 1)
        self.assertEqual(CourseEntitlementEvent.objects.filter(entitlement=entitlement).count(), 1)

    def test_individual_course_offer_is_not_saleable_for_free_or_membership_courses(self):
        product = Product.objects.create(
            name="One-time Course Offers",
            slug="one-time-course-offers",
        )
        plan = Plan.objects.create(
            product=product,
            tier=Plan.Tier.PRO,
            name="Course Purchase",
            is_active=True,
            is_hidden=True,
        )
        offer = CourseOffer.objects.create(
            course=self.course,
            name="Free Foundations offer",
            slug="free-foundations-offer",
            plan=plan,
            is_active=True,
        )
        self.assertFalse(offer.is_saleable)

        self.course.access_type = Course.AccessType.MEMBERSHIP
        self.course.save(update_fields=["access_type", "updated_at"])
        self.assertFalse(offer.is_saleable)

        self.course.access_type = Course.AccessType.MIXED
        self.course.save(update_fields=["access_type", "updated_at"])
        self.assertTrue(offer.is_saleable)

    def test_free_course_endpoint_rejects_courses_not_marked_free(self):
        self.course.access_type = Course.AccessType.PAID
        self.course.save(update_fields=["access_type", "updated_at"])
        response = self.client.post(reverse("academy:enrol-free-course", args=[self.course.slug]))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CourseEntitlement.objects.filter(user=self.user, course=self.course).exists())

    def test_free_membership_maps_course_and_both_join_paths_skip_payment(self):
        paid_product = Product.objects.create(name="Existing Paid Product", slug="existing-paid-product")
        paid_plan = Plan.objects.create(product=paid_product, tier=Plan.Tier.PRO, name="Existing Paid Plan")
        paid_subscription = Subscription.objects.create(
            user=self.user,
            plan=paid_plan,
            status=Subscription.Status.ACTIVE,
            is_active=True,
            price_cents=1700000,
            price_currency="INR",
        )

        self.course.access_type = Course.AccessType.MEMBERSHIP
        self.course.save(update_fields=["access_type", "updated_at"])
        sync_free_membership_course_access(self.course)

        plan = ensure_free_membership_plan()
        self.assertEqual(plan.product.slug, FREE_MEMBERSHIP_PRODUCT_SLUG)
        self.assertEqual(plan.tier, Plan.Tier.FREE)
        self.assertFalse(plan.is_trial)
        monthly = plan.prices.get(interval=PlanPrice.Interval.MONTHLY, is_active=True)
        self.assertEqual(monthly.price_cents, 0)
        self.assertTrue(PlanCourseAccess.objects.get(plan=plan, course=self.course).is_active)

        payment_response = self.client.post(
            reverse("payment-start"),
            data=json.dumps({"plan_id": str(plan.pk), "interval": "monthly"}),
            content_type="application/json",
        )
        self.assertEqual(payment_response.status_code, 200, payment_response.content)
        self.assertTrue(payment_response.json()["is_free"])
        self.assertFalse(PaymentIntent.objects.filter(user=self.user, plan=plan).exists())

        response = self.client.post(reverse("academy:join-free-membership", args=[self.course.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(has_active_plan_access(self.user, self.course))
        self.assertTrue(can_access_lesson(self.user, self.lesson))

        free_subscription = Subscription.objects.get(user=self.user, plan=plan)
        self.assertEqual(free_subscription.status, Subscription.Status.ACTIVE)
        self.assertTrue(free_subscription.is_active)
        self.assertEqual(free_subscription.price_cents, 0)
        self.assertEqual(free_subscription.price_currency, "INR")
        self.assertIsNone(free_subscription.expires_at)
        self.assertFalse(free_subscription.is_trial)
        self.assertEqual(
            SubscriptionHistory.objects.filter(
                subscription=free_subscription,
                notes__contains="no payment was collected",
            ).count(),
            1,
        )
        paid_subscription.refresh_from_db()
        self.assertTrue(paid_subscription.is_active)
        self.assertEqual(paid_subscription.status, Subscription.Status.ACTIVE)

    def test_free_membership_landing_is_marketed_as_free(self):
        self.course.access_type = Course.AccessType.MEMBERSHIP
        self.course.save(update_fields=["access_type", "updated_at"])
        sync_free_membership_course_access(self.course)
        response = self.client.get(reverse("academy:free-membership"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TradeThesis Free")
        self.assertContains(response, "₹0")
        self.assertContains(response, "no card required")
        self.assertContains(response, self.course.title)

    def test_expired_free_membership_does_not_unlock_mapped_course(self):
        self.course.access_type = Course.AccessType.MEMBERSHIP
        self.course.save(update_fields=["access_type", "updated_at"])
        sync_free_membership_course_access(self.course)
        plan = ensure_free_membership_plan()
        Subscription.objects.create(
            user=self.user,
            plan=plan,
            status=Subscription.Status.ACTIVE,
            is_active=True,
            price_cents=0,
            price_currency="INR",
            started_at=timezone.now() - timedelta(seconds=2),
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        self.assertFalse(has_active_plan_access(self.user, self.course))
        self.assertFalse(can_access_lesson(self.user, self.lesson))

    def test_nonzero_free_plan_price_is_never_silently_joined(self):
        plan = ensure_free_membership_plan()
        price = plan.prices.get(interval=PlanPrice.Interval.MONTHLY, is_active=True)
        price.price_cents = 1
        price.save()
        self.course.access_type = Course.AccessType.MEMBERSHIP
        self.course.save(update_fields=["access_type", "updated_at"])
        PlanCourseAccess.objects.update_or_create(plan=plan, course=self.course, defaults={"is_active": True})
        response = self.client.post(reverse("academy:join-free-membership", args=[self.course.slug]))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Subscription.objects.filter(user=self.user, plan=plan).exists())
