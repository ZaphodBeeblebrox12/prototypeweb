"""Member journey integration tests spanning dashboard, Academy access and saved progress."""
from datetime import timedelta
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academy.models import Course, CourseEntitlement, CourseModule, Lesson, LessonProgress
from apps.bot_integration.models import DiscordAccount, TelegramAccount

User = get_user_model()


class MemberDashboardJourneyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="journey-member",
            email="journey-member@example.com",
            password="Test-password-123!",
        )
        self.course = Course.objects.create(
            title="Member Journey Course",
            slug="member-journey-course",
            status=Course.Status.PUBLISHED,
            summary="A course used to test real member journeys.",
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title="Foundations",
            slug="foundations",
            position=1,
            is_published=True,
        )
        self.preview = Lesson.objects.create(
            module=self.module,
            title="Welcome Preview",
            slug="welcome-preview",
            position=1,
            is_published=True,
            is_preview=True,
            content_markdown="Preview content",
        )
        self.paid = Lesson.objects.create(
            module=self.module,
            title="First Paid Lesson",
            slug="first-paid-lesson",
            position=2,
            is_published=True,
            content_markdown="Paid content",
        )
        self.hidden = Lesson.objects.create(
            module=self.module,
            title="Unpublished Lesson",
            slug="unpublished-lesson",
            position=3,
            is_published=False,
            content_markdown="Do not count this lesson",
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, primary=True, verified=True
        )
        self.client.force_login(self.user)

    def grant_permanent_access(self):
        return CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.ACTIVE,
            starts_at=timezone.now() - timedelta(days=1),
            expires_at=None,
        )

    def test_dashboard_resumes_latest_accessible_in_progress_lesson(self):
        self.grant_permanent_access()
        now = timezone.now()
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.preview,
            status=LessonProgress.Status.IN_PROGRESS,
            started_at=now - timedelta(minutes=4),
            last_seen_at=now - timedelta(minutes=3),
        )
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.paid,
            status=LessonProgress.Status.IN_PROGRESS,
            started_at=now - timedelta(minutes=2),
            last_seen_at=now - timedelta(minutes=1),
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        card = next(
            item for item in response.context["member_course_cards"]
            if item["course"].pk == self.course.pk
        )
        self.assertEqual(card["resume_lesson"].pk, self.paid.pk)
        self.assertContains(
            response, reverse("academy:lesson", args=[self.course.slug, self.paid.pk])
        )

    def test_dashboard_resumes_preview_but_never_an_unentitled_paid_lesson(self):
        now = timezone.now()
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.preview,
            status=LessonProgress.Status.IN_PROGRESS,
            started_at=now - timedelta(minutes=3),
            last_seen_at=now - timedelta(minutes=2),
        )
        # Simulate a stale record from an earlier access period; entitlement is absent.
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.paid,
            status=LessonProgress.Status.IN_PROGRESS,
            started_at=now - timedelta(minutes=2),
            last_seen_at=now - timedelta(minutes=1),
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        card = next(
            item for item in response.context["member_course_cards"]
            if item["course"].pk == self.course.pk
        )
        self.assertEqual(card["resume_lesson"].pk, self.preview.pk)

    def test_dashboard_progress_excludes_unpublished_lessons(self):
        self.grant_permanent_access()
        now = timezone.now()
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.hidden,
            status=LessonProgress.Status.COMPLETED,
            started_at=now - timedelta(minutes=4),
            completed_at=now - timedelta(minutes=1),
            last_seen_at=now - timedelta(minutes=1),
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        card = next(
            item for item in response.context["member_course_cards"]
            if item["course"].pk == self.course.pk
        )
        self.assertEqual(card["total_lessons"], 2)
        self.assertEqual(card["completed_lessons"], 0)
        self.assertEqual(card["progress_percent"], 0)

    def test_anonymous_user_is_redirected_from_member_dashboard(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])


class MemberConnectionActionSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="connection-member",
            email="connection-member@example.com",
            password="Test-password-123!",
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, primary=True, verified=True
        )
        self.client.force_login(self.user)

    def test_get_cannot_unlink_telegram_account(self):
        account = TelegramAccount.objects.create(
            user=self.user,
            chat_id=731000001,
            telegram_user_id=731000001,
            username="member",
        )
        response = self.client.get(reverse("bot_integration:telegram_unlink"))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(TelegramAccount.objects.filter(pk=account.pk).exists())

    @patch("apps.jobs.enqueue.enqueue_reconcile")
    def test_post_unlinks_telegram_account_and_redirects(self, enqueue_reconcile):
        account = TelegramAccount.objects.create(
            user=self.user,
            chat_id=731000002,
            telegram_user_id=731000002,
            username="member",
        )
        response = self.client.post(reverse("bot_integration:telegram_unlink"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("profile"))
        self.assertFalse(TelegramAccount.objects.filter(pk=account.pk).exists())
        enqueue_reconcile.assert_called_once()

    def test_get_cannot_unlink_discord_account(self):
        account = DiscordAccount.objects.create(
            user=self.user,
            discord_user_id="journey-discord-1001",
            username="member",
        )
        response = self.client.get(reverse("bot_integration:discord_unlink"))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(DiscordAccount.objects.filter(pk=account.pk).exists())

    def test_post_unlinks_discord_account_and_redirects(self):
        account = DiscordAccount.objects.create(
            user=self.user,
            discord_user_id="journey-discord-1002",
            username="member",
        )
        response = self.client.post(reverse("bot_integration:discord_unlink"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("profile"))
        self.assertFalse(DiscordAccount.objects.filter(pk=account.pk).exists())
