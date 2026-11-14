"""Tests for the permission-aware, read-only TradeThesis Admin Desk."""
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academy.models import Course, CourseModule, Lesson
from apps.notifications.models import Notification
from apps.support.models import SupportTicket

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
            summary="A practical course summary for learners.",
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
        self.assertContains(response, "Advanced administration (rare use)")
        self.assertEqual(response.context["course_metrics"]["draft_courses"], 1)
        self.assertEqual(response.context["course_metrics"]["published_courses"], 1)
        self.assertEqual(response.context["course_metrics"]["catalogue_ready_courses"], 1)
        self.assertContains(response, "Catalogue-ready courses")
        self.assertContains(response, "Published records can still contain starter copy")
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

    def test_support_tickets_are_visible_to_staff_in_the_custom_admin_desk(self):
        operator = User.objects.create_user(
            username="support-desk-operator",
            email="support-desk-operator@example.test",
            is_staff=True,
        )
        learner = User.objects.create_user(
            username="support-ticket-learner",
            email="support-ticket-learner@example.test",
        )
        ticket = SupportTicket.objects.create(
            user=learner,
            category=SupportTicket.Category.BILLING,
            message="Payment completed but access is still missing.",
        )
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Support tickets")
        self.assertContains(response, "Payment completed but access is still missing.")
        self.assertEqual(response.context["support_tickets"]["pending"], 1)
        self.assertEqual(
            response.context["support_tickets"]["links"]["all"],
            reverse("staff_admin_desk_support_tickets"),
        )
        self.assertEqual(
            response.context["support_tickets"]["links"]["pending"],
            reverse("staff_admin_desk_support_tickets") + "?status=pending",
        )
        self.assertEqual(
            response.context["support_tickets"]["attention"][0]["can_review"],
            True,
        )

        queue_response = self.client.get(response.context["support_tickets"]["links"]["pending"])
        self.assertEqual(queue_response.status_code, 200)
        self.assertContains(queue_response, ticket.short_id)
        self.assertNotContains(
            queue_response,
            reverse("admin:support_supportticket_changelist"),
        )
        detail_response = self.client.get(
            reverse("staff_admin_desk_support_ticket", args=[ticket.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Conversation")
        self.assertContains(detail_response, "Assignment &amp; priority")

    def test_customers_overview_uses_live_reviewer_scoped_ticket_counts(self):
        owner = User.objects.create_superuser(
            username="customers-overview-owner",
            email="customers-overview-owner@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=owner, email=owner.email, verified=True, primary=True
        )
        learner = User.objects.create_user(
            username="customers-overview-learner",
            email="customers-overview-learner@example.test",
            first_name="Taylor",
            last_name="Trader",
        )
        ticket = SupportTicket.objects.create(
            user=learner,
            category=SupportTicket.Category.BILLING,
            message="Please check my payment and course access.",
        )
        SupportTicket.objects.filter(pk=ticket.pk).update(
            first_response_due_at=timezone.now() - timedelta(hours=1)
        )
        self.client.force_login(owner)

        response = self.client.get(reverse("staff_admin_desk_customers"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.context["can_view_accounts"])
        self.assertEqual(response.context["active_learners"], 1)
        self.assertEqual(response.context["support_summary"]["open"], 1)
        self.assertEqual(response.context["support_summary"]["overdue"], 1)
        self.assertEqual(response.context["support_summary"]["unassigned"], 1)
        self.assertContains(response, ticket.short_id)
        self.assertContains(
            response,
            reverse("staff_admin_desk_support_ticket", args=[ticket.pk]),
        )
        self.assertContains(response, "Customer 360")
        self.assertNotContains(response, "Ananya Rao")

    def test_generic_staff_customers_overview_does_not_expose_learner_register(self):
        operator = User.objects.create_user(
            username="customers-overview-support",
            email="customers-overview-support@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        learner = User.objects.create_user(
            username="customers-overview-member",
            email="customers-overview-member@example.test",
        )
        ticket = SupportTicket.objects.create(
            user=learner,
            category=SupportTicket.Category.TECHNICAL,
            message="I cannot connect to the community.",
        )
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk_customers"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(response.context["can_view_accounts"])
        self.assertIsNone(response.context["active_learners"])
        self.assertEqual(response.context["support_summary"]["open"], 1)
        self.assertContains(response, ticket.short_id)
        self.assertNotContains(response, reverse("staff_admin_desk_accounts"))
        self.assertNotContains(response, "Active learner accounts")

    def test_my_work_is_limited_to_current_staff_assignments_and_notifications(self):
        operator = User.objects.create_user(
            username="my-work-operator",
            email="my-work-operator@example.test",
            is_staff=True,
        )
        other_operator = User.objects.create_user(
            username="my-work-other-operator",
            email="my-work-other-operator@example.test",
            is_staff=True,
        )
        assigned_member = User.objects.create_user(
            username="my-work-assigned-member",
            email="my-work-assigned-member@example.test",
        )
        other_member = User.objects.create_user(
            username="my-work-other-member",
            email="my-work-other-member@example.test",
        )
        own_ticket = SupportTicket.objects.create(
            user=assigned_member,
            category=SupportTicket.Category.BILLING,
            message="Assigned billing request.",
            assigned_to=operator,
        )
        other_ticket = SupportTicket.objects.create(
            user=other_member,
            category=SupportTicket.Category.TECHNICAL,
            message="Another reviewer's technical request.",
            assigned_to=other_operator,
        )
        Notification.objects.create(
            user=operator,
            title="Your assignment changed",
            message="A support request is assigned to you.",
        )
        Notification.objects.create(
            user=other_operator,
            title="Private notification",
            message="This belongs to another staff member.",
        )
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk_my_work"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["support_count"], 1)
        self.assertEqual(response.context["notification_count"], 1)
        self.assertEqual(response.context["unread_notification_count"], 1)
        self.assertContains(response, own_ticket.short_id)
        self.assertNotContains(response, other_ticket.short_id)
        self.assertContains(response, "Your assignment changed")
        self.assertNotContains(response, "Private notification")

    def test_domain_overviews_render_for_superuser(self):
        owner = User.objects.create_superuser(
            username="domain-overview-owner",
            email="domain-overview-owner@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=owner, email=owner.email, verified=True, primary=True
        )
        Course.objects.create(
            title="Overview Draft Course",
            slug="overview-draft-course",
            status=Course.Status.DRAFT,
        )
        self.client.force_login(owner)

        academy = self.client.get(reverse("staff_admin_desk_academy"))
        self.assertEqual(academy.status_code, 200, academy.content)
        self.assertEqual(academy.context["course_summary"]["draft"], 1)
        self.assertTrue(academy.context["can_review_courses"])

        for route_name in (
            "staff_admin_desk_revenue",
            "staff_admin_desk_growth",
            "staff_admin_desk_platform",
        ):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200, response.content)

    def test_staff_domain_overviews_do_not_expose_unpermitted_panels(self):
        operator = User.objects.create_user(
            username="domain-overview-staff",
            email="domain-overview-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        self.client.force_login(operator)

        expectations = {
            "staff_admin_desk_academy": (
                "course_summary", "review_summary", "offer_summary",
                "entitlement_summary",
            ),
            "staff_admin_desk_revenue": (
                "payment_summary", "invoice_summary", "subscription_summary",
                "dispute_summary",
            ),
            "staff_admin_desk_growth": (
                "purchase_report", "email_report", "campaign_report",
                "promotion_report", "referral_report", "gift_summary",
            ),
            "staff_admin_desk_platform": (
                "job_summary", "provisioning_summary", "scheduler_summary",
                "audit_summary", "security_summary",
            ),
        }
        for route_name, forbidden_context_keys in expectations.items():
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200, response.content)
                for key in forbidden_context_keys:
                    self.assertNotIn(key, response.context)

    def test_staff_notifications_escape_untrusted_title_and_message(self):
        operator = User.objects.create_user(
            username="notification-render-staff",
            email="notification-render-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        Notification.objects.create(
            user=operator,
            title="<script>alert('title-xss')</script>",
            message='<img src=x onerror="alert(\'message-xss\')">',
        )
        self.client.force_login(operator)

        response = self.client.get("/notifications/")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(
            response,
            "&lt;script&gt;alert(&#x27;title-xss&#x27;)&lt;/script&gt;",
        )
        self.assertContains(
            response,
            "&lt;img src=x onerror=&quot;alert(&#x27;message-xss&#x27;)&quot;&gt;",
        )
        self.assertNotContains(response, "<script>alert('title-xss')</script>")
        self.assertNotContains(response, '<img src=x onerror="alert(\'message-xss\')">')
        self.assertContains(response, 'class="tt-admin-desk-layout"')
        self.assertContains(response, 'id="ttDeskSidebar"')

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
        self.assertEqual(expiring["status"], ["active"])
        self.assertEqual(expiring["expiring"], ["1"])
        
        recently_expired = parse_qs(urlsplit(
            response.context["subscriptions"]["links"]["recently_expired"]
        ).query)
        self.assertEqual(recently_expired["status"], ["expired"])
        self.assertEqual(recently_expired["recent"], ["1"])

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

