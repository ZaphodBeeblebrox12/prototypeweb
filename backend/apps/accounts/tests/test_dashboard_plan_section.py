"""Plan & Billing section on the user dashboard (redesign v2).

Contract tests between DashboardView and templates/accounts/dashboard.html:
immutable billing snapshot, state badges (active/trial/expiring/expired/
complimentary), upgrade-only candidate grid, ended-subscription messaging,
trial gating, interval-correct pricing, and CTA wiring into the EXISTING
payments/support flows (no duplicated business logic in the UI).
"""
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.academy.models import (
    Course, CourseEntitlement, CourseModule, Lesson, LessonProgress,
)
from apps.bot_integration.models import BotConfig
from apps.subscriptions.models import (
    GeoPlanPrice, Plan, PlanFeature, PlanPrice, Product, Subscription,
)

User = get_user_model()


def make_user(username="dashuser"):
    return User.objects.create_user(username=username, email=f"{username}@t.co")


def make_plan(name, tier, order, **kwargs):
    return Plan.objects.create(name=name, tier=tier, display_order=order, **kwargs)


def make_price(plan, cents, interval="monthly", currency="USD"):
    return PlanPrice.objects.create(
        plan=plan, interval=interval, price_cents=cents, currency=currency)


def make_active_sub(user, plan, **kwargs):
    defaults = dict(
        status=Subscription.Status.ACTIVE, is_active=True,
        started_at=timezone.now() - datetime.timedelta(days=30),
        expires_at=timezone.now() + datetime.timedelta(days=30),
        price_cents=233, price_currency="USD",
    )
    defaults.update(kwargs)
    return Subscription.objects.create(user=user, plan=plan, **defaults)


class PlanSectionRenderTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)
        self.basic = make_plan("Basic", "basic", 10)
        self.pro = make_plan("Pro", "pro", 20)
        make_price(self.basic, 233)
        make_price(self.pro, 12312)
        PlanFeature.objects.create(plan=self.pro, text="Priority support", position=1)

    def _get(self):
        # name="dashboard" lives in apps/accounts/profile_urls.py
        # (root include, no namespace -> bare name)
        return self.client.get(reverse("dashboard"))

    # ---------- free user ----------
    def test_free_user_sees_all_purchasable_plans(self):
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Free plan")
        self.assertContains(r, "Available plans")
        self.assertContains(r, "Basic")
        self.assertContains(r, "Pro")
        # purchasable CTA wires into the existing payment-start flow
        self.assertContains(
            r, f"{reverse('payment-start')}?plan_id={self.pro.id}")

    def test_free_user_with_ended_subscription_sees_ended_notice(self):
        make_active_sub(self.user, self.basic,
                        status=Subscription.Status.EXPIRED, is_active=False,
                        expires_at=timezone.now() - datetime.timedelta(days=2))
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "ended on")
        self.assertContains(r, "regain access")

    def test_trial_offer_renders_for_free_user_with_geo_price(self):
        trial = Plan.objects.create(
            name="Trial", tier="basic", display_order=5, is_trial=True,
            trial_duration_days=7)
        GeoPlanPrice.objects.create(
            plan=trial, country="IN", price_cents=0, currency="INR")
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Start free trial")
        self.assertContains(r, "7 days free")

    def test_trial_offer_absent_without_geo_price(self):
        Plan.objects.create(
            name="Trial", tier="basic", display_order=5, is_trial=True,
            trial_duration_days=7)
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Start free trial")

    def test_unpriced_plan_renders_request_access(self):
        vip = make_plan("VIP", "vip", 30)  # no prices -> invite only
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Invite only")
        self.assertContains(r, "Request access")
        self.assertContains(r, reverse("support:request_ticket"))

    def test_quarterly_only_plan_labels_interval_correctly(self):
        q_only = make_plan("Quarterly Ent", "enterprise", 25)
        make_price(q_only, 12000, interval="quarterly")
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "/ quarter")
        self.assertContains(
            r, f"plan_id={q_only.id}&interval=quarterly")

    # ---------- subscribed user (upgrade-only) ----------
    def test_current_plan_card_uses_immutable_snapshot(self):
        make_active_sub(self.user, self.basic, price_cents=233,
                        price_currency="EUR")
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "€2.33")  # snapshot currency, not the plan's USD
        self.assertContains(r, reverse("manage-subscription"))
        self.assertContains(r, reverse("upgrade-page"))

    def test_subscribed_user_sees_only_upgrade_candidates(self):
        make_active_sub(self.user, self.basic)
        starter = make_plan("Starter", "free", 5)  # LOWER tier than basic
        make_price(starter, 100)
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Starter")   # no downgrade / double-pay bait
        self.assertNotContains(r, f"plan_id={starter.id}")  # no purchase link
        self.assertContains(r, "Upgrade")

    def test_trial_panel_hidden_for_subscribed_user(self):
        make_active_sub(self.user, self.basic)
        trial = Plan.objects.create(
            name="Trial", tier="pro", display_order=15, is_trial=True,
            trial_duration_days=7)
        GeoPlanPrice.objects.create(
            plan=trial, country="IN", price_cents=0, currency="INR")
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Start free trial")

    def test_highest_tier_shows_friendly_empty_state(self):
        make_active_sub(self.user, self.pro)  # nothing above pro
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "nothing above it")

    # ---------- state badges ----------
    def test_expiring_subscription_shows_urgency(self):
        make_active_sub(self.user, self.basic,
                        expires_at=timezone.now() + datetime.timedelta(days=3))
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Expiring soon")
        self.assertContains(r, "3 days left")

    def test_trial_badge_for_trial_subscription(self):
        make_active_sub(self.user, self.basic, is_trial=True)
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Trial ends")

    def test_expired_subscription_shows_expired_badge_not_active(self):
        make_active_sub(self.user, self.basic,
                        expires_at=timezone.now() - datetime.timedelta(days=1))
        r = self._get()
        self.assertEqual(r.status_code, 200)
        # the subscription badge must not claim Active (the user-account
        # status card also says "Active" — match the badge markup instead)
        self.assertNotContains(
            r, 'bg-success"><i class="bi bi-check-circle-fill"></i> Active')
        self.assertContains(r, "Expired")


class MultiProductDashboardTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)
        self.thesis = Product.objects.create(name="Trade Thesis", slug="thesis")
        self.terminal = Product.objects.create(name="Trade Terminal", slug="terminal")
        self.thesis_plan = make_plan("Thesis Pro", "pro", 10, product=self.thesis)
        self.terminal_plan = make_plan("Terminal Pro", "pro", 10, product=self.terminal)
        make_price(self.thesis_plan, 4900)
        make_price(self.terminal_plan, 9900)

    def _get(self):
        return self.client.get(reverse("dashboard"))

    def test_both_subscriptions_render_as_separate_cards(self):
        make_active_sub(self.user, self.thesis_plan)
        make_active_sub(self.user, self.terminal_plan)
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Trade Thesis")
        self.assertContains(r, "Trade Terminal")
        self.assertContains(r, "Thesis Pro")
        self.assertContains(r, "Terminal Pro")
        # subscribed products are not re-offered in Explore
        self.assertNotContains(r, f"plan_id={self.thesis_plan.id}")
        self.assertNotContains(r, f"plan_id={self.terminal_plan.id}")

    def test_unsubscribed_product_appears_in_explore(self):
        make_active_sub(self.user, self.thesis_plan)
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Trade Terminal")   # explore group header
        self.assertContains(r, "Terminal Pro")
        self.assertContains(r, "Get started")

    def test_trial_gated_per_product(self):
        make_active_sub(self.user, self.thesis_plan)
        trial = Plan.objects.create(
            name="Terminal Trial", tier="pro", display_order=5,
            product=self.terminal, is_trial=True, trial_duration_days=7)
        GeoPlanPrice.objects.create(
            plan=trial, country="IN", price_cents=0, currency="INR")
        r = self._get()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Start free trial")  # terminal has no sub
        self.assertContains(r, "Trade Terminal")    # labeled with product

class MemberCourseDashboardDataTests(TestCase):
    """The live member desk must use the current user's published learning data."""

    def setUp(self):
        self.user = make_user("course_learner")
        self.client.force_login(self.user)
        self.course = Course.objects.create(
            title="Dashboard Course",
            slug="dashboard-course",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title="Module One",
            slug="module-one",
            position=1,
            is_published=True,
        )
        self.completed_lesson = Lesson.objects.create(
            module=self.module,
            title="Completed Preview",
            slug="completed-preview",
            position=1,
            is_preview=True,
            is_published=True,
        )
        self.resume_lesson = Lesson.objects.create(
            module=self.module,
            title="Resume Preview",
            slug="resume-preview",
            position=2,
            is_preview=True,
            is_published=True,
        )
        self.unpublished_lesson = Lesson.objects.create(
            module=self.module,
            title="Unpublished lesson",
            slug="unpublished-lesson",
            position=3,
            is_preview=True,
            is_published=False,
        )

    def test_missing_telegram_bot_config_is_explained_in_connections(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["telegram_bot_configured"])
        self.assertContains(response, "The TradeThesis Telegram bot is not configured yet.")
        self.assertContains(response, 'aria-disabled="true">Telegram setup required</span>')
        self.assertNotContains(
            response,
            f'href="{reverse("bot_integration:telegram_connect")}"',
        )

    def test_configured_telegram_bot_keeps_connect_links_available(self):
        BotConfig.objects.update_or_create(
            pk=1,
            defaults={
                "telegram_bot_username": "tradethesis_test_bot",
                "telegram_bot_token": "test-main-bot-token",
                "is_active": True,
            },
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["telegram_bot_configured"])
        self.assertContains(
            response,
            f'href="{reverse("bot_integration:telegram_connect")}"',
        )

    def test_course_without_access_or_saved_progress_uses_empty_state(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["member_course_cards"], [])
        self.assertContains(response, "Nothing to resume just yet")
        self.assertContains(response, "Explore the course catalogue")

    def test_active_entitlement_shows_course_without_prior_progress(self):
        CourseEntitlement.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEntitlement.Status.ACTIVE,
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        cards = response.context["member_course_cards"]
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["course"].pk, self.course.pk)
        self.assertIsNotNone(cards[0]["entitlement"])
        self.assertContains(response, "Access active")
        self.assertNotContains(response, "Nothing to resume just yet")

    def test_dashboard_progress_and_resume_are_user_scoped_and_published_only(self):
        other_user = make_user("other_course_learner")
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.completed_lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.resume_lesson,
            status=LessonProgress.Status.IN_PROGRESS,
        )
        # These records must not affect the current learner's dashboard totals.
        LessonProgress.objects.create(
            user=other_user,
            lesson=self.resume_lesson,
            status=LessonProgress.Status.COMPLETED,
        )
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.unpublished_lesson,
            status=LessonProgress.Status.COMPLETED,
        )

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        card = next(
            item for item in response.context["member_course_cards"]
            if item["course"].pk == self.course.pk
        )
        self.assertEqual(card["total_lessons"], 2)
        self.assertEqual(card["completed_lessons"], 1)
        self.assertEqual(card["progress_percent"], 50)
        self.assertEqual(card["resume_lesson"].pk, self.resume_lesson.pk)
        self.assertContains(
            response,
            reverse("academy:lesson", args=[self.course.slug, self.resume_lesson.pk]),
        )
        self.assertEqual(response.context["member_lessons_completed"], 1)

