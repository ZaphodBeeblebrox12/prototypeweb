from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.academy.models import (
    Course,
    CourseEntitlement,
    CourseEntitlementEvent,
    CourseModule,
    CourseOffer,
    Lesson,
    PersonalizedProtectedVideo,
    ProtectedLessonVideo,
)
from apps.jobs.models import Job
from apps.payments.models import PaymentIntent
from apps.subscriptions.models import Plan, PlanPrice

User = get_user_model()
STAGING_HOST = "tradethesis-academy-staging.onrender.com"


@override_settings(
    ACADEMY_STAGING_PAYMENT_SIMULATOR_ENABLED=True,
    ACADEMY_STAGING_PAYMENT_SIMULATOR_HOST=STAGING_HOST,
    SITE_BASE_URL=f"https://{STAGING_HOST}",
)
class StagingPaymentSimulatorTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="simulator-admin",
            email="simulator-admin@example.com",
            password="test-password",
            role="admin",
            is_staff=True,
        )
        self.learner = User.objects.create_user(
            username="simulator-learner",
            email="simulator-learner@example.com",
            password="test-password",
            role=User.Role.USER,
        )
        self.plan = Plan.objects.create(
            name="Simulator course plan",
            tier=Plan.Tier.BASIC,
            is_active=True,
            is_hidden=True,
        )
        self.price = PlanPrice.objects.create(
            plan=self.plan,
            interval=PlanPrice.Interval.ONE_TIME,
            price_cents=99900,
            currency="INR",
            is_active=True,
        )
        self.course = Course.objects.create(
            title="Simulator protected course",
            slug="simulator-protected-course",
            status=Course.Status.PUBLISHED,
            access_type=Course.AccessType.PAID,
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title="Test module",
            slug="test-module",
            position=1,
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Test lesson",
            slug="test-lesson",
            position=1,
            is_published=True,
        )
        self.offer = CourseOffer.objects.create(
            course=self.course,
            name="Simulator protected course",
            slug="simulator-protected-course",
            plan=self.plan,
            is_active=True,
        )
        self.video = ProtectedLessonVideo.objects.create(
            lesson=self.lesson,
            source_file="academy/video-source/simulator/test-source.mp4",
            status=ProtectedLessonVideo.Status.READY,
            stream_directory="streams/simulator/test",
        )
        self.client.force_login(
            self.admin,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        self.url = reverse("academy:staging-payment-simulator")

    def test_get_page_is_available_only_on_exact_staging_host(self):
        response = self.client.get(self.url, HTTP_HOST=STAGING_HOST)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STAGING ONLY")
        self.assertContains(response, "NO MONEY COLLECTED")

        wrong_host = self.client.get(self.url, HTTP_HOST="tradethesis-public-staging.onrender.com")
        self.assertEqual(wrong_host.status_code, 404)

    def test_disabled_setting_hides_simulator_even_on_staging_host(self):
        with override_settings(ACADEMY_STAGING_PAYMENT_SIMULATOR_ENABLED=False):
            response = self.client.get(self.url, HTTP_HOST=STAGING_HOST)
        self.assertEqual(response.status_code, 404)

    def test_non_admin_cannot_access_simulator(self):
        learner_client = Client()
        learner_client.force_login(
            self.learner,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        response = learner_client.get(self.url, HTTP_HOST=STAGING_HOST)
        self.assertEqual(response.status_code, 404)

    def test_simulated_purchase_uses_real_activation_and_queues_personal_video(self):
        response = self.client.post(
            self.url,
            {
                "course_offer": str(self.offer.pk),
                "learner": str(self.learner.pk),
                "acknowledge": "on",
            },
            HTTP_HOST=STAGING_HOST,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Course access was granted successfully")
        self.assertContains(response, "SIMULATOR — NO MONEY COLLECTED")

        intent = PaymentIntent.objects.get(user=self.learner)
        self.assertEqual(intent.provider, PaymentIntent.Provider.SIMULATOR)
        self.assertEqual(intent.status, PaymentIntent.Status.SUCCESS)
        self.assertEqual(intent.amount, self.price.price_cents)
        self.assertEqual(intent.currency, self.price.currency)
        self.assertFalse(intent.provider_reference)

        entitlement = CourseEntitlement.objects.get(
            user=self.learner,
            course=self.course,
        )
        self.assertEqual(entitlement.source, CourseEntitlement.Source.PURCHASE)
        self.assertEqual(entitlement.payment_intent_id, intent.pk)
        self.assertEqual(entitlement.granted_by_id, self.admin.pk)

        event = CourseEntitlementEvent.objects.get(entitlement=entitlement)
        self.assertEqual(event.actor_id, self.admin.pk)
        self.assertTrue(event.details["simulated"])
        self.assertIn("no money was collected", event.details["simulation_note"])

        rendition = PersonalizedProtectedVideo.objects.get(
            user=self.learner,
            protected_video=self.video,
        )
        self.assertEqual(rendition.status, PersonalizedProtectedVideo.Status.PENDING)
        job = Job.objects.get(kind="process_personalized_video")
        self.assertEqual(job.payload["rendition_id"], str(rendition.pk))
        self.assertEqual(job.payload["user_id"], str(self.learner.pk))
        self.assertEqual(job.payload["video_id"], str(self.video.pk))

        # The simulator must not create a provider transaction or a real receipt.
        self.assertEqual(PaymentIntent.objects.filter(user=self.learner).count(), 1)
        self.assertEqual(intent.provider_payment_id, "")
        self.assertEqual(intent.provider_reference, "")

    def test_learner_with_existing_active_access_cannot_receive_duplicate_simulation(self):
        CourseEntitlement.objects.create(
            user=self.learner,
            course=self.course,
            source=CourseEntitlement.Source.COMPLIMENTARY,
        )
        response = self.client.post(
            self.url,
            {
                "course_offer": str(self.offer.pk),
                "learner": str(self.learner.pk),
                "acknowledge": "on",
            },
            HTTP_HOST=STAGING_HOST,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already has active access")
        self.assertFalse(PaymentIntent.objects.filter(user=self.learner).exists())
        self.assertFalse(CourseEntitlement.objects.filter(
            user=self.learner,
            course=self.course,
            source=CourseEntitlement.Source.PURCHASE,
        ).exists())
