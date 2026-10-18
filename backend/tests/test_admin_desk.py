"""Tests for the permission-aware, read-only TradeThesis Admin Desk."""
from urllib.parse import parse_qs, urlsplit

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.academy.models import Course, CourseModule, Lesson

User = get_user_model()


class AdminDeskTests(TestCase):
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
        self.assertEqual(
            response.context["accounts"]["links"]["users"],
            reverse("admin:accounts_user_changelist"),
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

