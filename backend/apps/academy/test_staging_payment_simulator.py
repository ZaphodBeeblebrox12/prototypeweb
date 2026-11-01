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
                "course": str(self.course.pk),
                "learner": str(self.learner.pk),
                "acknowledge": "on",
            },
            HTTP_HOST=STAGING_HOST,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Course access was granted successfully")
        self.assertContains(response, "SIMULATOR — NO MONEY COLLECTED")

        intent = PaymentIntent.objects.get(user=self.learner)
        self.assertEqual(intent.provider, PaymentIntent.Provider.RAZORPAY)
        self.assertTrue(intent.is_simulated)
        self.assertEqual(intent.get_provider_display(), "Simulator — no money collected")
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

        self.assertContains(response, "Personalised video preparation status")
        self.assertContains(response, "Waiting to prepare")
        self.assertContains(response, "Background job:")
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

    def test_published_course_without_public_offer_is_available_for_internal_simulation(self):
        from apps.subscriptions.models import Product

        course = Course.objects.create(
            title="No-offer simulation course",
            slug="no-offer-simulation-course",
            summary="A published test course without a public checkout offer.",
            status=Course.Status.PUBLISHED,
            access_type=Course.AccessType.FREE,
        )
        module = CourseModule.objects.create(
            course=course,
            title="Protected video module",
            slug="protected-video-module",
            position=1,
            is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Protected test video",
            slug="protected-test-video",
            position=1,
            is_published=True,
        )
        video = ProtectedLessonVideo.objects.create(
            lesson=lesson,
            source_file="academy/video-source/no-offer/source.mp4",
            status=ProtectedLessonVideo.Status.READY,
            stream_directory="streams/no-offer/source",
        )

        page = self.client.get(self.url, HTTP_HOST=STAGING_HOST)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "No-offer simulation course")

        response = self.client.post(
            self.url,
            {
                "course": str(course.pk),
                "learner": str(self.learner.pk),
                "acknowledge": "on",
            },
            HTTP_HOST=STAGING_HOST,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Course access was granted successfully")
        self.assertContains(response, "Internal only")

        intent = PaymentIntent.objects.get(user=self.learner)
        self.assertEqual(intent.status, PaymentIntent.Status.SUCCESS)
        self.assertTrue(intent.is_simulated)
        self.assertEqual(intent.currency, "INR")
        self.assertEqual(intent.amount, 100)

        entitlement = CourseEntitlement.objects.get(
            user=self.learner,
            course=course,
        )
        self.assertEqual(entitlement.source, CourseEntitlement.Source.PURCHASE)
        self.assertEqual(entitlement.payment_intent_id, intent.pk)

        offer = CourseOffer.objects.get(course=course, slug=f"staging-sim-{course.pk.hex}")
        self.assertFalse(offer.is_active)
        self.assertFalse(offer.is_saleable)
        self.assertFalse(offer.plan.is_active)
        self.assertTrue(offer.plan.is_hidden)
        self.assertIsInstance(offer.plan.product, Product)
        self.assertFalse(offer.plan.product.is_active)
        self.assertEqual(
            offer.plan.prices.get(interval=PlanPrice.Interval.ONE_TIME).price_cents,
            100,
        )

        rendition = PersonalizedProtectedVideo.objects.get(
            user=self.learner,
            protected_video=video,
        )
        self.assertEqual(rendition.status, PersonalizedProtectedVideo.Status.PENDING)
        job = Job.objects.get(
            kind="process_personalized_video",
            payload__rendition_id=str(rendition.pk),
        )
        self.assertEqual(job.payload["user_id"], str(self.learner.pk))

    def test_failed_simulated_video_can_be_requeued_without_new_payment_or_entitlement(self):
        purchase_response = self.client.post(
            self.url,
            {
                "course": str(self.course.pk),
                "learner": str(self.learner.pk),
                "acknowledge": "on",
            },
            HTTP_HOST=STAGING_HOST,
        )
        self.assertEqual(purchase_response.status_code, 200)

        rendition = PersonalizedProtectedVideo.objects.get(
            user=self.learner,
            protected_video=self.video,
        )
        rendition.status = PersonalizedProtectedVideo.Status.FAILED
        rendition.processing_error = "Simulated FFmpeg failure for test."
        rendition.save(update_fields=["status", "processing_error", "updated_at"])

        original_job = Job.objects.get(
            kind="process_personalized_video",
            payload__rendition_id=str(rendition.pk),
        )
        original_job.status = Job.STATUS_FAILED
        original_job.attempts = original_job.max_attempts
        original_job.idempotency_key = None
        original_job.save(update_fields=["status", "attempts", "idempotency_key"])

        retry_url = reverse(
            "academy:staging-retry-video",
            args=[rendition.pk],
        )
        retry_response = self.client.post(retry_url, HTTP_HOST=STAGING_HOST)

        self.assertEqual(retry_response.status_code, 302)
        self.assertEqual(retry_response["Location"], self.url)

        status_page = self.client.get(self.url, HTTP_HOST=STAGING_HOST)
        self.assertEqual(status_page.status_code, 200)
        self.assertContains(status_page, "Personalised video preparation status")
        self.assertContains(status_page, "Waiting to prepare")
        self.assertContains(status_page, "Background job:")
        self.assertNotContains(status_page, "Personalised videos that need a retry")

        rendition.refresh_from_db()
        self.assertEqual(rendition.status, PersonalizedProtectedVideo.Status.PENDING)
        self.assertEqual(
            PaymentIntent.objects.filter(user=self.learner, is_simulated=True).count(),
            1,
        )
        self.assertEqual(
            CourseEntitlement.objects.filter(user=self.learner, course=self.course).count(),
            1,
        )

        retry_job = Job.objects.get(
            kind="process_personalized_video",
            payload__rendition_id=str(rendition.pk),
            status=Job.STATUS_PENDING,
        )
        self.assertNotEqual(retry_job.pk, original_job.pk)
        self.assertEqual(retry_job.payload["user_id"], str(self.learner.pk))
        self.assertEqual(retry_job.payload["video_id"], str(self.video.pk))

    def test_retry_endpoint_is_hidden_from_non_admins(self):
        learner_client = Client()
        learner_client.force_login(
            self.learner,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        response = learner_client.post(
            reverse("academy:staging-retry-video", args=["28692e3b-ddc4-4a6a-9ada-99dbd8bf10a1"]),
            HTTP_HOST=STAGING_HOST,
        )
        self.assertEqual(response.status_code, 404)

    def test_learner_with_existing_active_access_cannot_receive_duplicate_simulation(self):
        CourseEntitlement.objects.create(
            user=self.learner,
            course=self.course,
            source=CourseEntitlement.Source.COMPLIMENTARY,
        )
        response = self.client.post(
            self.url,
            {
                "course": str(self.course.pk),
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
