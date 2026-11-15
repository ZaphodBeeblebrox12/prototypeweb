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

    def test_restricted_support_ticket_blocks_detail_action_and_customer_profile(self):
        from apps.subscriptions.models import Plan

        operator = User.objects.create_user(
            username="restricted-scope-operator",
            email="restricted-scope-operator@example.test",
            is_staff=True,
        )
        other_reviewer = User.objects.create_user(
            username="restricted-scope-approver",
            email="restricted-scope-approver@example.test",
            is_staff=True,
        )
        member = User.objects.create_user(
            username="restricted-scope-member",
            email="restricted-scope-member@example.test",
        )
        restricted_plan = Plan.objects.create(
            name="Restricted reviewer plan",
            tier=Plan.Tier.PRO,
        )
        restricted_plan.ticket_approvers.add(other_reviewer)
        ticket = SupportTicket.objects.create(
            user=member,
            plan=restricted_plan,
            category=SupportTicket.Category.BILLING,
            message="A private support request for another reviewer.",
        )
        self.client.force_login(operator)

        detail_response = self.client.get(
            reverse("staff_admin_desk_support_ticket", args=[ticket.pk])
        )
        self.assertEqual(detail_response.status_code, 404)

        messages_before = ticket.messages.count()
        action_response = self.client.post(
            reverse("staff_admin_desk_support_ticket_action", args=[ticket.pk]),
            {
                "action": "public_reply",
                "body": "This reply must not be saved by an unauthorised reviewer.",
            },
        )
        self.assertEqual(action_response.status_code, 404)
        self.assertEqual(ticket.messages.count(), messages_before)

        customer_response = self.client.get(
            reverse("staff_admin_desk_customer_360", args=[member.pk])
        )
        self.assertEqual(customer_response.status_code, 403)
        self.assertNotContains(
            customer_response,
            "A private support request for another reviewer.",
            status_code=403,
        )

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

    def test_growth_referral_summary_requires_reward_and_settings_permissions(self):
        from django.contrib.auth.models import Permission

        operator = User.objects.create_user(
            username="growth-referral-report-staff",
            email="growth-referral-report-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        reward_permission = Permission.objects.get(
            content_type__app_label="growth",
            codename="view_referralreward",
        )
        settings_permission = Permission.objects.get(
            content_type__app_label="growth",
            codename="view_referralsettings",
        )
        operator.user_permissions.add(reward_permission)
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk_growth"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotIn("referral_report", response.context)
        self.assertFalse(response.context["can_view_referrals"])

        operator.user_permissions.add(settings_permission)
        response = self.client.get(reverse("staff_admin_desk_growth"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("referral_report", response.context)
        self.assertTrue(response.context["can_view_referrals"])

    def test_growth_email_report_uses_marked_sent_not_delivered_language(self):
        owner = User.objects.create_superuser(
            username="growth-email-report-owner",
            email="growth-email-report-owner@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=owner, email=owner.email, verified=True, primary=True
        )
        self.client.force_login(owner)

        response = self.client.get(reverse("staff_admin_desk_growth"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Marked sent")
        self.assertContains(
            response,
            "A Sent state is not presented as provider-confirmed Delivered",
        )

    def test_global_search_respects_domain_permissions_and_ticket_reviewer_scope(self):
        from django.contrib.auth.models import Permission
        from apps.payments.models import PaymentIntent
        from apps.subscriptions.models import Plan

        operator = User.objects.create_user(
            username="global-search-operator",
            email="global-search-operator@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        for app_label, codename in (
            ("accounts", "view_user"),
            ("academy", "view_course"),
            ("payments", "view_paymentintent"),
        ):
            permission = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
            operator.user_permissions.add(permission)

        member = User.objects.create_user(
            username="needle-member",
            email="needle-member@example.test",
            first_name="Needle",
            last_name="Member",
        )
        hidden_member = User.objects.create_user(
            username="hidden-scope-member",
            email="hidden-scope-member@example.test",
        )
        other_reviewer = User.objects.create_user(
            username="global-search-other-reviewer",
            email="global-search-other-reviewer@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=other_reviewer,
            email=other_reviewer.email,
            verified=True,
            primary=True,
        )

        visible_plan = Plan.objects.create(
            name="Visible support plan",
            tier=Plan.Tier.BASIC,
        )
        visible_plan.ticket_approvers.add(operator)
        hidden_plan = Plan.objects.create(
            name="Restricted support plan",
            tier=Plan.Tier.PRO,
        )
        hidden_plan.ticket_approvers.add(other_reviewer)

        visible_ticket = SupportTicket.objects.create(
            user=member,
            plan=visible_plan,
            category=SupportTicket.Category.TECHNICAL,
            message="Needle visible support request",
        )
        hidden_ticket = SupportTicket.objects.create(
            user=hidden_member,
            plan=hidden_plan,
            category=SupportTicket.Category.TECHNICAL,
            message="Needle restricted support request",
        )
        course = Course.objects.create(
            title="Needle Course",
            slug="needle-course",
            status=Course.Status.DRAFT,
        )
        payment_plan = Plan.objects.create(
            name="Needle Payment Plan",
            tier=Plan.Tier.ENTERPRISE,
        )
        PaymentIntent.objects.create(
            user=member,
            plan=payment_plan,
            provider=PaymentIntent.Provider.RAZORPAY,
            amount=129900,
            currency="INR",
            status=PaymentIntent.Status.SUCCESS,
        )
        self.client.force_login(operator)

        response = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": "needle"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        groups = {
            group["name"]: group["results"]
            for group in response.context["search_groups"]
        }
        self.assertEqual(set(groups), {"Customers", "Academy", "Revenue"})
        self.assertContains(response, member.username)
        self.assertContains(response, visible_ticket.short_id)
        self.assertNotContains(response, hidden_ticket.short_id)
        self.assertNotContains(response, hidden_member.username)
        self.assertContains(response, course.title)
        self.assertContains(response, payment_plan.name)
        self.assertContains(response, "INR 1,299.00")
        self.assertNotContains(response, "Needle restricted support request")

    def test_global_search_includes_disputes_only_with_revenue_permission(self):
        from django.contrib.auth.models import Permission
        from apps.disputes.models import Dispute
        from apps.payments.models import PaymentIntent
        from apps.subscriptions.models import Plan

        member = User.objects.create_user(
            username="needle-dispute-member",
            email="needle-dispute-member@example.test",
        )
        plan = Plan.objects.create(
            name="Dispute search plan",
            tier=Plan.Tier.BASIC,
        )
        payment = PaymentIntent.objects.create(
            user=member,
            plan=plan,
            provider=PaymentIntent.Provider.STRIPE,
            amount=459900,
            currency="INR",
            status=PaymentIntent.Status.SUCCESS,
        )
        provider_dispute_id = "dp_private_search_9381"
        dispute = Dispute.objects.create(
            payment_intent=payment,
            provider=PaymentIntent.Provider.STRIPE,
            provider_dispute_id=provider_dispute_id,
            reason_category=Dispute.ReasonCategory.NOT_RECEIVED,
            amount_cents=459900,
            currency="INR",
            status=Dispute.Status.OPENED,
        )
        other_member = User.objects.create_user(
            username="unrelated-dispute-member",
            email="unrelated-dispute-member@example.test",
        )
        other_payment = PaymentIntent.objects.create(
            user=other_member,
            plan=plan,
            provider=PaymentIntent.Provider.RAZORPAY,
            amount=129900,
            currency="INR",
            status=PaymentIntent.Status.SUCCESS,
        )
        Dispute.objects.create(
            payment_intent=other_payment,
            provider=PaymentIntent.Provider.RAZORPAY,
            provider_dispute_id="dp_unrelated_case_6421",
            reason_category=Dispute.ReasonCategory.DUPLICATE,
            amount_cents=129900,
            currency="INR",
            status=Dispute.Status.OPENED,
        )

        limited_operator = User.objects.create_user(
            username="dispute-search-limited",
            email="dispute-search-limited@example.test",
            is_staff=True,
        )
        self.client.force_login(limited_operator)
        denied_response = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": member.username},
        )
        self.assertEqual(denied_response.status_code, 200)
        self.assertEqual(denied_response.context["search_groups"], [])
        self.assertNotContains(denied_response, member.email)
        self.assertNotContains(denied_response, provider_dispute_id)

        reviewer = User.objects.create_user(
            username="dispute-search-reviewer",
            email="dispute-search-reviewer@example.test",
            is_staff=True,
        )
        permission = Permission.objects.get(
            content_type__app_label="disputes",
            codename="view_dispute",
        )
        reviewer.user_permissions.add(permission)
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": member.username},
        )
        self.assertEqual(response.status_code, 200, response.content)
        groups = {
            group["name"]: group["results"]
            for group in response.context["search_groups"]
        }
        self.assertEqual(set(groups), {"Revenue"})
        self.assertEqual(len(groups["Revenue"]), 1)
        result = groups["Revenue"][0]
        self.assertEqual(result["kind"], "Dispute")
        self.assertIn(member.username, result["title"])
        self.assertIn("Service not received", result["detail"])
        self.assertIn("INR 4,599.00", result["detail"])
        self.assertEqual(
            result["url"],
            reverse("disputes:dashboard") + "?q=" + member.username,
        )
        self.assertContains(response, "Dispute")
        self.assertNotContains(response, provider_dispute_id)

        dispute_workspace = self.client.get(result["url"])
        self.assertEqual(dispute_workspace.status_code, 200, dispute_workspace.content)
        matching_rows = list(
            dispute_workspace.context["rows"].values_list("pk", flat=True)
        )
        self.assertEqual(matching_rows, [dispute.pk])
        self.assertContains(dispute_workspace, provider_dispute_id[:16])
        self.assertNotContains(dispute_workspace, "dp_unrelated_case_6421")

        application_admin = User.objects.create_user(
            username="dispute-search-application-admin",
            email="dispute-search-application-admin@example.test",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.client.force_login(application_admin)
        admin_search = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": member.username},
        )
        self.assertEqual(admin_search.status_code, 200, admin_search.content)
        admin_groups = {
            group["name"]: group["results"]
            for group in admin_search.context["search_groups"]
        }
        self.assertEqual(set(admin_groups), {"Revenue"})
        self.assertEqual(admin_groups["Revenue"][0]["url"], result["url"])
        admin_dispute_workspace = self.client.get(result["url"])
        self.assertEqual(
            admin_dispute_workspace.status_code, 200, admin_dispute_workspace.content
        )

    def test_finance_refund_ledger_is_read_only_and_permission_scoped(self):
        from django.contrib.auth.models import Permission
        from apps.payments.models import PaymentIntent, Refund
        from apps.subscriptions.models import Plan

        member = User.objects.create_user(
            username="refund-ledger-member",
            email="refund-ledger-member@example.test",
        )
        plan = Plan.objects.create(
            name="Refund ledger plan",
            tier=Plan.Tier.BASIC,
        )
        payment = PaymentIntent.objects.create(
            user=member,
            plan=plan,
            provider=PaymentIntent.Provider.STRIPE,
            amount=459900,
            currency="INR",
            status=PaymentIntent.Status.SUCCESS,
        )
        provider_refund_id = "rf_private_refund_reference_9381"
        private_metadata = "refund-metadata-must-not-render"
        refund = Refund.objects.create(
            payment_intent=payment,
            provider=PaymentIntent.Provider.STRIPE,
            provider_refund_id=provider_refund_id,
            amount_cents=129900,
            currency="INR",
            source=Refund.Source.WEBHOOK,
            commercial_context=Refund.CommercialContext.STANDARD,
            refunded_at=timezone.now(),
            metadata={"private_payload": private_metadata},
        )

        unprivileged = User.objects.create_user(
            username="refund-ledger-unprivileged",
            email="refund-ledger-unprivileged@example.test",
            is_staff=True,
        )
        self.client.force_login(unprivileged)
        denied = self.client.get(
            reverse("staff_admin_desk_finance"),
            {"tab": "refunds", "q": member.username},
        )
        self.assertEqual(denied.status_code, 403)

        refund_operator = User.objects.create_user(
            username="refund-ledger-operator",
            email="refund-ledger-operator@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=refund_operator,
            email=refund_operator.email,
            verified=True,
            primary=True,
        )
        refund_permission = Permission.objects.get(
            content_type__app_label="payments",
            codename="view_refund",
        )
        refund_operator.user_permissions.add(refund_permission)
        self.client.force_login(refund_operator)

        response = self.client.get(reverse("staff_admin_desk_finance"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["tab"], "refunds")
        self.assertTrue(response.context["can_view_refunds"])
        self.assertTrue(response.context["desk_nav"]["finance"])
        platform_access = self.client.get(reverse("staff_admin_desk_platform"))
        self.assertEqual(platform_access.status_code, 200)
        revenue_access = next(
            section for section in platform_access.context["my_access"]["sections"]
            if section["name"] == "Revenue"
        )
        refund_access = {
            item["label"]: item for item in revenue_access["items"]
        }
        self.assertTrue(refund_access["Refund ledger"]["granted"])
        self.assertFalse(response.context["can_view_payments"])
        self.assertFalse(response.context["can_view_invoices"])
        self.assertEqual(
            list(response.context["refund_page"].object_list.values_list("pk", flat=True)),
            [refund.pk],
        )
        self.assertContains(response, member.username)
        self.assertContains(response, "Refund ledger plan")
        self.assertContains(response, "Stripe")
        self.assertContains(response, "INR 1,299.00")
        self.assertContains(response, "Webhook")
        self.assertContains(response, "Standard paid plan")
        self.assertNotContains(response, provider_refund_id)
        self.assertNotContains(response, private_metadata)
        self.assertNotContains(response, "Initiate refund")
        self.assertEqual(Refund.objects.count(), 1)

        search = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": member.username},
        )
        self.assertEqual(search.status_code, 200, search.content)
        self.assertEqual(len(search.context["search_groups"]), 1)
        results = search.context["search_groups"][0]["results"]
        self.assertEqual(search.context["search_groups"][0]["name"], "Revenue")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["kind"], "Refund record")
        self.assertIn(member.username, results[0]["title"])
        self.assertIn("Standard paid plan", results[0]["detail"])
        self.assertIn("INR 1,299.00", results[0]["detail"])
        self.assertEqual(
            results[0]["url"],
            reverse("staff_admin_desk_finance")
            + f"?q={member.username}&tab=refunds",
        )
        self.assertNotIn(provider_refund_id, str(results))
        self.assertNotIn(private_metadata, str(results))

        payment_operator = User.objects.create_user(
            username="payment-only-operator",
            email="payment-only-operator@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=payment_operator,
            email=payment_operator.email,
            verified=True,
            primary=True,
        )
        payment_permission = Permission.objects.get(
            content_type__app_label="payments",
            codename="view_paymentintent",
        )
        payment_operator.user_permissions.add(payment_permission)
        self.client.force_login(payment_operator)

        payment_only_response = self.client.get(
            reverse("staff_admin_desk_finance"),
            {"tab": "refunds"},
        )
        self.assertEqual(payment_only_response.status_code, 200)
        self.assertEqual(payment_only_response.context["tab"], "payments")
        self.assertFalse(payment_only_response.context["can_view_refunds"])
        payment_platform_access = self.client.get(reverse("staff_admin_desk_platform"))
        self.assertEqual(payment_platform_access.status_code, 200)
        payment_revenue_access = next(
            section for section in payment_platform_access.context["my_access"]["sections"]
            if section["name"] == "Revenue"
        )
        payment_refund_access = {
            item["label"]: item for item in payment_revenue_access["items"]
        }
        self.assertFalse(payment_refund_access["Refund ledger"]["granted"])
        self.assertNotContains(payment_only_response, "tab=refunds")

        payment_only_search = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": member.username},
        )
        self.assertEqual(payment_only_search.status_code, 200)
        payment_results = [
            result
            for group in payment_only_search.context["search_groups"]
            for result in group["results"]
        ]
        self.assertNotIn("Refund record", [result["kind"] for result in payment_results])
        self.assertNotIn(provider_refund_id, str(payment_results))
        self.assertNotIn(private_metadata, str(payment_results))

    def test_platform_webhook_summary_omits_provider_ids_payloads_and_errors(self):
        from django.contrib.auth.models import Permission
        from apps.payments.models import WebhookEvent

        operator = User.objects.create_user(
            username="platform-webhook-staff",
            email="platform-webhook-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        permission = Permission.objects.get(
            content_type__app_label="payments",
            codename="view_webhookevent",
        )
        operator.user_permissions.add(permission)
        provider_event_id = "evt_private_provider_reference_9834"
        payload_secret = "payload-secret-do-not-render"
        error_detail = "provider-internal-error-do-not-render"
        WebhookEvent.objects.create(
            provider="stripe",
            provider_event_id=provider_event_id,
            event_type="payment_intent.succeeded",
            payload={"secret": payload_secret},
            status=WebhookEvent.Status.FAILED,
            error=error_detail,
        )
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk_platform"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["webhook_summary"]["total_7d"], 1)
        self.assertEqual(response.context["webhook_summary"]["failed"], 1)
        self.assertContains(response, "Provider webhook evidence")
        self.assertContains(response, "payment_intent.succeeded")
        self.assertContains(response, "Failed")
        self.assertNotContains(response, provider_event_id)
        self.assertNotContains(response, payload_secret)
        self.assertNotContains(response, error_detail)
        access_sections = {
            section["name"]: section["items"]
            for section in response.context["my_access"]["sections"]
        }
        platform_access = {
            item["label"]: item["granted"]
            for item in access_sections["Platform"]
        }
        self.assertTrue(platform_access["Provider webhook events"])
        self.assertFalse(platform_access["Background jobs"])

    def test_platform_access_summary_shows_only_current_staff_permissions(self):
        from django.contrib.auth.models import Group, Permission

        operator = User.objects.create_user(
            username="platform-access-staff",
            email="platform-access-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        permission = Permission.objects.get(
            content_type__app_label="jobs",
            codename="view_job",
        )
        operator.user_permissions.add(permission)
        group = Group.objects.create(name="Platform Operations")
        operator.groups.add(group)
        self.client.force_login(operator)

        response = self.client.get(reverse("staff_admin_desk_platform"))

        self.assertEqual(response.status_code, 200, response.content)
        access = response.context["my_access"]
        self.assertEqual(access["identity"]["application_role"], "User")
        self.assertTrue(access["identity"]["is_staff"])
        self.assertFalse(access["identity"]["is_superuser"])
        self.assertEqual(access["groups"], ["Platform Operations"])
        sections = {section["name"]: section["items"] for section in access["sections"]}
        platform_items = {item["label"]: item for item in sections["Platform"]}
        customer_items = {item["label"]: item for item in sections["Customers"]}
        self.assertTrue(platform_items["Background jobs"]["granted"])
        self.assertFalse(platform_items["Provisioning operations"]["granted"])
        self.assertFalse(customer_items["Learner accounts"]["granted"])
        self.assertTrue(customer_items["Support tickets"]["granted"])
        self.assertContains(response, "Your access")
        self.assertContains(response, "plan scope")
        self.assertNotContains(response, "Edit permissions")

    def test_application_admin_access_summary_matches_growth_and_dispute_routes(self):
        application_admin = User.objects.create_user(
            username="application-admin-access-summary",
            email="application-admin-access-summary@example.test",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.client.force_login(application_admin)

        platform_response = self.client.get(reverse("staff_admin_desk_platform"))
        self.assertEqual(platform_response.status_code, 200, platform_response.content)
        sections = {
            section["name"]: {
                item["label"]: item
                for item in section["items"]
            }
            for section in platform_response.context["my_access"]["sections"]
        }
        revenue_access = sections["Revenue"]
        self.assertTrue(revenue_access["Disputes"]["granted"])
        self.assertTrue(revenue_access["Change disputes"]["granted"])
        self.assertFalse(revenue_access["Refund ledger"]["granted"])

        growth_access = sections["Growth"]
        self.assertTrue(growth_access["Growth overview & reporting"]["granted"])
        self.assertTrue(growth_access["Referral rewards"]["granted"])
        self.assertTrue(growth_access["Create and send gifts"]["granted"])
        self.assertFalse(growth_access["Campaign register"]["granted"])
        self.assertFalse(growth_access["Gift invite register"]["granted"])

        growth_response = self.client.get(reverse("staff_admin_desk_growth"))
        self.assertEqual(growth_response.status_code, 200, growth_response.content)
        self.assertTrue(growth_response.context["can_view_campaigns"])
        self.assertTrue(growth_response.context["can_view_email"])
        self.assertTrue(growth_response.context["can_view_promotions"])
        self.assertTrue(growth_response.context["can_view_purchases"])
        self.assertFalse(growth_response.context.get("campaign_url"))
        self.assertFalse(growth_response.context.get("email_url"))
        self.assertFalse(growth_response.context.get("promotion_url"))
        self.assertFalse(growth_response.context.get("events_url"))
        self.assertFalse(growth_response.context["gift_summary"]["url"])
        self.assertContains(
            growth_response,
            "Register access requires its model permission",
        )
        self.assertNotContains(growth_response, "/admin/campaigns/campaign/")
        self.assertNotContains(growth_response, "/admin/growth/giftinvite/")

        dispute_response = self.client.get(reverse("disputes:dashboard"))
        self.assertEqual(dispute_response.status_code, 200, dispute_response.content)

    def test_global_search_returns_safe_webhook_results_only_with_view_permission(self):
        from django.contrib.auth.models import Permission
        from apps.payments.models import WebhookEvent

        operator = User.objects.create_user(
            username="global-search-webhook-staff",
            email="global-search-webhook-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        permission = Permission.objects.get(
            content_type__app_label="payments",
            codename="view_webhookevent",
        )
        operator.user_permissions.add(permission)
        provider_event_id = "evt_search_private_6812"
        payload_secret = "webhook-search-secret"
        internal_error = "webhook-search-internal-error"
        WebhookEvent.objects.create(
            provider="stripe",
            provider_event_id=provider_event_id,
            event_type="charge.dispute.created",
            payload={"api_secret": payload_secret},
            status=WebhookEvent.Status.FAILED,
            error=internal_error,
        )
        self.client.force_login(operator)

        response = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": "dispute"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        groups = response.context["search_groups"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["name"], "Platform")
        self.assertEqual(len(groups[0]["results"]), 1)
        self.assertContains(response, "charge.dispute.created")
        self.assertContains(response, "Failed")
        self.assertNotContains(response, provider_event_id)
        self.assertNotContains(response, payload_secret)
        self.assertNotContains(response, internal_error)
        self.assertEqual(
            groups[0]["results"][0]["url"],
            f"{reverse('admin:payments_webhookevent_changelist')}?q=dispute",
        )

    def test_global_search_preserves_unknown_provisioning_state_without_exposing_id(self):
        from uuid import uuid4
        from django.contrib.auth.models import Permission
        from apps.jobs.models import ProvisioningOperation

        operator = User.objects.create_user(
            username="global-search-platform-staff",
            email="global-search-platform-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        permission = Permission.objects.get(
            content_type__app_label="jobs",
            codename="view_provisioningoperation",
        )
        operator.user_permissions.add(permission)
        operation = ProvisioningOperation.objects.create(
            operation=ProvisioningOperation.OP_GRANT,
            user_id=uuid4(),
            channel_id="staging-channel",
            state=ProvisioningOperation.ST_UNKNOWN,
        )
        self.client.force_login(operator)

        by_identifier = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": str(operation.operation_id)},
        )
        self.assertEqual(by_identifier.status_code, 200, by_identifier.content)
        self.assertEqual(by_identifier.context["search_groups"], [])
        # The search input retains the query for usability; the UUID must not
        # appear as a result, URL, or provisioning-detail identifier.
        self.assertEqual(by_identifier.context["total_results"], 0)

        by_operation = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": "grant"},
        )
        self.assertEqual(by_operation.status_code, 200, by_operation.content)
        self.assertContains(by_operation, "Needs verification")
        self.assertNotContains(by_operation, str(operation.operation_id))

    def test_global_search_does_not_expose_unpermitted_account_or_course_records(self):
        operator = User.objects.create_user(
            username="global-search-limited-staff",
            email="global-search-limited-staff@example.test",
            is_staff=True,
        )
        EmailAddress.objects.create(
            user=operator, email=operator.email, verified=True, primary=True
        )
        User.objects.create_user(
            username="private-search-target",
            email="private-search-target@example.test",
        )
        Course.objects.create(
            title="Private Search Course",
            slug="private-search-course",
            status=Course.Status.DRAFT,
        )
        self.client.force_login(operator)

        response = self.client.get(
            reverse("staff_admin_desk_search"),
            {"q": "private-search"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["search_groups"], [])
        self.assertEqual(response.context["total_results"], 0)
        self.assertNotContains(response, "private-search-target")
        self.assertNotContains(response, "Private Search Course")

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

        growth = self.client.get(reverse("staff_admin_desk_growth"))
        self.assertContains(growth, "Simulation only")
        self.assertContains(growth, "not sent to provider")
        self.assertContains(growth, "Marked sent")

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

    def test_specialist_overviews_only_build_explicitly_granted_panels(self):
        from django.contrib.auth.models import Permission

        def staff_with_permission(username, app_label, codename):
            operator = User.objects.create_user(
                username=username,
                email=f"{username}@example.test",
                is_staff=True,
            )
            EmailAddress.objects.create(
                user=operator, email=operator.email, verified=True, primary=True
            )
            permission = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
            operator.user_permissions.add(permission)
            return operator

        scenarios = (
            (
                "academy-specialist",
                "academy",
                "view_course",
                "staff_admin_desk_academy",
                {"course_summary"},
                {"review_summary", "offer_summary", "entitlement_summary"},
            ),
            (
                "revenue-specialist",
                "payments",
                "view_paymentintent",
                "staff_admin_desk_revenue",
                {"payment_summary"},
                {
                    "invoice_summary",
                    "subscription_summary",
                    "dispute_summary",
                    "business_url",
                },
            ),
            (
                "growth-specialist",
                "events",
                "view_event",
                "staff_admin_desk_growth",
                {"purchase_report"},
                {
                    "email_report",
                    "campaign_report",
                    "promotion_report",
                    "referral_report",
                    "gift_summary",
                },
            ),
            (
                "platform-specialist",
                "jobs",
                "view_job",
                "staff_admin_desk_platform",
                {"job_summary"},
                {
                    "provisioning_summary",
                    "scheduler_summary",
                    "audit_summary",
                    "security_summary",
                },
            ),
        )

        for (
            username,
            app_label,
            codename,
            route_name,
            allowed_keys,
            denied_keys,
        ) in scenarios:
            with self.subTest(username=username):
                operator = staff_with_permission(username, app_label, codename)
                self.client.force_login(operator)
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200, response.content)
                for key in allowed_keys:
                    self.assertIn(key, response.context)
                for key in denied_keys:
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

