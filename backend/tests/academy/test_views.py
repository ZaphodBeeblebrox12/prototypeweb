from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academy.models import (
    Course,
    CourseEntitlement,
    CourseModule,
    CourseOffer,
    Lesson,
    LessonProgress,
)
from apps.subscriptions.models import Plan, PlanPrice

User = get_user_model()


class AcademyViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="Test-password-123!")
        self.course = Course.objects.create(
            title="Trading Path", slug="trading-path", status=Course.Status.PUBLISHED,
            summary="Learn to read the screen.",
        )
        self.module = CourseModule.objects.create(
            course=self.course, title="Foundations", slug="foundations",
            position=1, is_published=True,
        )
        self.paid_lesson = Lesson.objects.create(
            module=self.module, title="Private lesson", slug="private-lesson",
            position=1, is_published=True, content_markdown="SECRET PAID LESSON BODY",
        )
        self.preview_lesson = Lesson.objects.create(
            module=self.module, title="Preview lesson", slug="preview-lesson",
            position=2, is_published=True, is_preview=True,
            content_markdown="Public preview content.",
        )
        self.client.force_login(self.user)

    def test_course_overview_does_not_include_paid_lesson_body(self):
        response = self.client.get(reverse("academy:course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Private lesson")
        self.assertNotContains(response, "SECRET PAID LESSON BODY")

    def test_paid_lesson_is_not_retrievable_without_entitlement(self):
        response = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "SECRET PAID LESSON BODY", status_code=403)

    def test_published_preview_lesson_can_be_opened(self):
        response = self.client.get(reverse("academy:lesson", args=[self.course.slug, self.preview_lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public preview content.")

    def test_progress_endpoint_rejects_unentitled_paid_lesson(self):
        response = self.client.post(
            reverse("academy:lesson-progress", args=[self.paid_lesson.pk]),
            {"status": "completed"},
        )
        self.assertEqual(response.status_code, 403)

    def test_dashboard_uses_real_learning_progress_and_activity(self):
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.preview_lesson,
            status=LessonProgress.Status.COMPLETED,
            time_spent_seconds=245,
        )
        response = self.client.get(reverse("academy:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["completed_lesson_count"], 1)
        self.assertEqual(response.context["learning_minutes"], 4)
        self.assertEqual(response.context["active_course_count"], 0)
        self.assertEqual(len(response.context["recent_activity"]), 1)
        self.assertContains(response, "Recent activity")
        self.assertContains(response, "Preview lesson")

    def test_dashboard_does_not_expose_unpublished_draft_courses(self):
        Course.objects.create(
            title="Unpublished VPA draft",
            slug="unpublished-vpa-draft",
            status=Course.Status.DRAFT,
        )
        response = self.client.get(reverse("academy:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Unpublished VPA draft")

    def test_entitled_learner_can_complete_lesson_and_see_dashboard_update(self):
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            source=CourseEntitlement.Source.ADMIN,
        )
        lesson_url = reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        response = self.client.get(lesson_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SECRET PAID LESSON BODY")

        progress_response = self.client.post(
            reverse("academy:lesson-progress", args=[self.paid_lesson.pk]),
            {"status": "completed", "seconds_delta": "310"},
        )
        self.assertEqual(progress_response.status_code, 200)
        self.assertEqual(progress_response.json()["status"], LessonProgress.Status.COMPLETED)
        saved = LessonProgress.objects.get(user=self.user, lesson=self.paid_lesson)
        self.assertEqual(saved.time_spent_seconds, 310)
        self.assertIsNotNone(saved.completed_at)

        dashboard = self.client.get(reverse("academy:home"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.context["active_course_count"], 1)
        self.assertEqual(dashboard.context["completed_lesson_count"], 1)
        self.assertEqual(dashboard.context["learning_minutes"], 5)
        card = next(row for row in dashboard.context["course_cards"] if row["course"] == self.course)
        self.assertEqual(card["progress_percent"], 50)

    def test_expired_entitlement_cannot_open_or_complete_paid_lesson(self):
        now = timezone.now()
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            source=CourseEntitlement.Source.ADMIN,
            starts_at=now - timedelta(days=3),
            expires_at=now - timedelta(days=1),
        )
        lesson_response = self.client.get(
            reverse("academy:lesson", args=[self.course.slug, self.paid_lesson.pk])
        )
        self.assertEqual(lesson_response.status_code, 403)
        progress_response = self.client.post(
            reverse("academy:lesson-progress", args=[self.paid_lesson.pk]),
            {"status": "completed"},
        )
        self.assertEqual(progress_response.status_code, 403)
        self.assertFalse(LessonProgress.objects.filter(user=self.user, lesson=self.paid_lesson).exists())

    def test_unpurchased_course_appears_in_library_not_my_learning(self):
        catalog_course = Course.objects.create(
            title="Separate catalogue course",
            slug="separate-catalogue-course",
            status=Course.Status.PUBLISHED,
            summary="A saleable course not yet enrolled in.",
        )
        plan = Plan.objects.create(
            name="Separate course offer",
            tier=Plan.Tier.BASIC,
            is_active=True,
            is_hidden=True,
        )
        PlanPrice.objects.create(
            plan=plan,
            interval=PlanPrice.Interval.ONE_TIME,
            price_cents=50000,
            currency="INR",
            is_active=True,
        )
        CourseOffer.objects.create(
            course=catalog_course,
            name="Separate catalogue course",
            slug="separate-catalogue-course-offer",
            plan=plan,
            is_active=True,
        )

        response = self.client.get(reverse("academy:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["course_cards"], [])
        self.assertEqual(
            [offer.course.slug for offer in response.context["offers"]],
            [catalog_course.slug],
        )
        self.assertContains(response, "Course library")

    def test_learning_room_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("academy:home"))
        self.assertEqual(response.status_code, 302)
