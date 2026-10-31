"""Tests for the cross-customer support and engineering timeline."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.events.models import Event
from apps.jobs.models import Job, PeriodicJob, ProvisioningOperation
from apps.support.models import SupportTicket
from apps.subscriptions.models import Plan

User = get_user_model()


class OperationsTimelineTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="operations-timeline-admin",
            email="operations-timeline-admin@example.test",
            password="test-password-123!",
        )
        self.client.force_login(self.admin)

    def _create_support_pattern(self, *, plan=None, prefix="operations-signal"):
        messages = [
            "Payment completed but I still cannot access my course lessons. Contact alpha@example.test.",
            "I made payment, but course access is still blocked for lessons. https://example.test/order/123",
            "Payment succeeded and course access remains blocked for my lessons.",
        ]
        tickets = []
        for index, message in enumerate(messages):
            member = User.objects.create_user(
                username=f"{prefix}-{index}",
                email=f"{prefix}-{index}@example.test",
            )
            tickets.append(SupportTicket.objects.create(
                user=member,
                category=SupportTicket.Category.BILLING,
                plan=plan,
                message=message,
            ))
        return tickets

    def test_operations_timeline_combines_support_and_real_system_records(self):
        tickets = self._create_support_pattern()
        Job.objects.create(
            kind="membership_reconcile",
            status=Job.STATUS_FAILED,
            attempts=5,
            max_attempts=5,
        )
        PeriodicJob.objects.create(
            name="channel_membership_sync",
            enabled=True,
            last_run_at=timezone.now(),
            last_status=PeriodicJob.Status.ERROR,
            last_error="PRIVATE scheduler stack trace must not render",
        )
        ProvisioningOperation.objects.create(
            operation="grant",
            user_id=tickets[0].user_id,
            channel_id="internal-channel",
            state=ProvisioningOperation.ST_FAILED,
            attempts=3,
            last_error="PRIVATE provider token and invite link must not render",
        )
        Event.objects.create(
            event_type=Event.Type.PAYMENT_FAILED,
            dedupe_key="operations-timeline-payment-failed",
            user=tickets[0].user,
            payload={"provider_error": "PRIVATE provider payload must not render"},
            occurred_at=timezone.now(),
        )
        AuditLog.objects.create(
            action="payments.reconciliation.failed",
            object_type="payment",
            object_id="private-object-id",
            metadata={"secret": "PRIVATE audit metadata must not render"},
        )

        response = self.client.get(reverse("staff_admin_desk_operations_timeline"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "Operations timeline")
        self.assertContains(response, "Potential multi-customer patterns")
        self.assertContains(response, "3 customers")
        self.assertContains(response, "payment")
        self.assertContains(response, "course")
        self.assertContains(response, "membership_reconcile")
        self.assertContains(response, "channel_membership_sync")
        self.assertContains(response, "Provisioning")
        self.assertEqual(response.context["stats"]["potential_patterns"], 1)
        self.assertEqual(response.context["stats"]["failed_jobs"], 1)
        self.assertEqual(response.context["stats"]["provisioning_issues"], 1)
        self.assertEqual(response.context["stats"]["scheduler_errors"], 1)

        self.assertNotContains(response, "alpha@example.test")
        self.assertNotContains(response, "example.test/order")
        self.assertNotContains(response, "PRIVATE scheduler stack trace")
        self.assertNotContains(response, "PRIVATE provider token")
        self.assertNotContains(response, "PRIVATE provider payload")
        self.assertNotContains(response, "PRIVATE audit metadata")
        self.assertNotContains(response, "private-object-id")

    def test_support_patterns_obey_existing_plan_reviewer_scope(self):
        permitted_reviewer = User.objects.create_user(
            username="operations-plan-reviewer",
            email="operations-plan-reviewer@example.test",
            is_staff=True,
        )
        unrelated_reviewer = User.objects.create_user(
            username="operations-unrelated-reviewer",
            email="operations-unrelated-reviewer@example.test",
            is_staff=True,
        )
        restricted_plan = Plan.objects.create(
            name="Operations restricted plan",
            tier=Plan.Tier.BASIC,
            is_hidden=True,
        )
        restricted_plan.ticket_approvers.add(permitted_reviewer)
        self._create_support_pattern(
            plan=restricted_plan,
            prefix="operations-restricted",
        )

        self.client.force_login(unrelated_reviewer)
        hidden_response = self.client.get(reverse("staff_admin_desk_operations_timeline"))
        self.assertEqual(hidden_response.status_code, 200)
        self.assertEqual(hidden_response.context["stats"]["potential_patterns"], 0)
        self.assertEqual(hidden_response.context["stats"]["open_tickets"], 0)

        self.client.force_login(permitted_reviewer)
        visible_response = self.client.get(reverse("staff_admin_desk_operations_timeline"))
        self.assertEqual(visible_response.status_code, 200)
        self.assertEqual(visible_response.context["stats"]["potential_patterns"], 1)
        self.assertEqual(visible_response.context["issue_clusters"][0]["customer_count"], 3)

    def test_operations_timeline_rejects_non_staff_accounts(self):
        learner = User.objects.create_user(
            username="operations-timeline-learner",
            email="operations-timeline-learner@example.test",
        )
        self.client.force_login(learner)

        response = self.client.get(reverse("staff_admin_desk_operations_timeline"))

        self.assertEqual(response.status_code, 403)
