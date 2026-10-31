"""Tests for the cross-customer support and engineering timeline."""

from datetime import timedelta

from django.contrib.auth.models import Permission
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.events.models import Event
from apps.jobs.models import Job, PeriodicJob, ProvisioningOperation
from apps.accounts.models import SecurityEvent
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
        PeriodicJob.objects.create(
            name="old_scheduler_error_outside_window",
            enabled=True,
            last_run_at=timezone.now() - timedelta(days=8),
            last_status=PeriodicJob.Status.ERROR,
            last_error="Old scheduler failure should not look recent.",
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
        self.assertNotContains(response, "old_scheduler_error_outside_window")
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
        EmailAddress.objects.create(
            user=learner,
            email=learner.email,
            verified=True,
            primary=True,
        )
        self.client.force_login(learner)

        response = self.client.get(reverse("staff_admin_desk_operations_timeline"))

        self.assertEqual(response.status_code, 403)


    def test_scheduler_errors_respect_the_selected_24_hour_window(self):
        PeriodicJob.objects.create(
            name="scheduler_error_older_than_24h",
            enabled=True,
            last_run_at=timezone.now() - timedelta(days=2),
            last_status=PeriodicJob.Status.ERROR,
        )

        response = self.client.get(
            reverse("staff_admin_desk_operations_timeline"),
            {"window": "24h"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.context["stats"]["scheduler_errors"], 0)
        self.assertNotContains(response, "scheduler_error_older_than_24h")

    def test_operational_feeds_are_independently_permission_scoped(self):
        member = User.objects.create_user(
            username="operations-permission-member",
            email="operations-permission-member@example.test",
        )
        Job.objects.create(
            kind="worker_permission_probe",
            status=Job.STATUS_FAILED,
            attempts=5,
            max_attempts=5,
        )
        PeriodicJob.objects.create(
            name="scheduler_permission_probe",
            enabled=True,
            last_run_at=timezone.now(),
            last_status=PeriodicJob.Status.ERROR,
        )
        ProvisioningOperation.objects.create(
            operation="grant",
            user_id=member.pk,
            channel_id="private-channel-id",
            state=ProvisioningOperation.ST_FAILED,
            attempts=3,
            last_error="PRIVATE_PROVISIONING_ERROR",
            invite_link="https://example.test/private-invite",
        )
        Event.objects.create(
            event_type=Event.Type.PAYMENT_FAILED,
            dedupe_key="operations-permission-domain-event",
            user=member,
            payload={"private": "PRIVATE_DOMAIN_PAYLOAD"},
            occurred_at=timezone.now(),
        )
        AuditLog.objects.create(
            action="ops.audit.permission_probe",
            object_type="internal",
            object_id="PRIVATE_AUDIT_OBJECT",
            metadata={"private": "PRIVATE_AUDIT_METADATA"},
        )
        SecurityEvent.objects.create(
            user=member,
            event_type=SecurityEvent.EventType.LOGIN_FAILED,
            ip_address="192.0.2.41",
            user_agent="PRIVATE_SECURITY_USER_AGENT",
            detail={"private": "PRIVATE_SECURITY_DETAIL"},
            occurred_at=timezone.now(),
        )

        permission_specs = [
            ("jobs", "view_job", "can_view_jobs"),
            ("jobs", "view_provisioningoperation", "can_view_provisioning"),
            ("jobs", "view_periodicjob", "can_view_periodic_jobs"),
            ("events", "view_event", "can_view_domain_events"),
            ("audit", "view_auditlog", "can_view_audit"),
            ("accounts", "view_securityevent", "can_view_security"),
        ]

        for index, (app_label, codename, context_flag) in enumerate(permission_specs):
            reviewer = User.objects.create_user(
                username=f"operations-permission-reviewer-{index}",
                email=f"operations-permission-reviewer-{index}@example.test",
                is_staff=True,
            )
            permission = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
            reviewer.user_permissions.add(permission)
            self.client.force_login(reviewer)

            response = self.client.get(reverse("staff_admin_desk_operations_timeline"))

            self.assertEqual(response.status_code, 200, response.content)
            self.assertTrue(response.context[context_flag])
            for _other_app, _other_codename, other_flag in permission_specs:
                if other_flag != context_flag:
                    self.assertFalse(response.context[other_flag])
            self.assertNotContains(response, "PRIVATE_PROVISIONING_ERROR")
            self.assertNotContains(response, "private-invite")
            self.assertNotContains(response, "PRIVATE_DOMAIN_PAYLOAD")
            self.assertNotContains(response, "PRIVATE_AUDIT_METADATA")
            self.assertNotContains(response, "PRIVATE_AUDIT_OBJECT")
            self.assertNotContains(response, "192.0.2.41")
            self.assertNotContains(response, "PRIVATE_SECURITY_USER_AGENT")
            self.assertNotContains(response, "PRIVATE_SECURITY_DETAIL")

    def test_worker_and_provisioning_details_stay_inside_the_admin_desk(self):
        member = User.objects.create_user(
            username="operations-detail-member",
            email="operations-detail-member@example.test",
        )
        job = Job.objects.create(
            kind="safe_worker_detail",
            status=Job.STATUS_FAILED,
            attempts=5,
            max_attempts=5,
            payload={"secret": "PRIVATE_JOB_PAYLOAD"},
        )
        operation = ProvisioningOperation.objects.create(
            operation="grant",
            user_id=member.pk,
            channel_id="PRIVATE_CHANNEL_ID",
            state=ProvisioningOperation.ST_FAILED,
            attempts=4,
            last_error="PRIVATE_PROVIDER_ERROR",
            invite_link="https://example.test/private-invite",
        )

        job_response = self.client.get(
            reverse("staff_admin_desk_operations_job", args=[job.pk])
        )
        provisioning_response = self.client.get(
            reverse("staff_admin_desk_operations_provisioning", args=[operation.pk])
        )

        self.assertEqual(job_response.status_code, 200, job_response.content)
        self.assertEqual(provisioning_response.status_code, 200, provisioning_response.content)
        self.assertContains(job_response, "safe_worker_detail")
        self.assertContains(provisioning_response, "Grant operation")
        for response in (job_response, provisioning_response):
            self.assertNotContains(response, "PRIVATE_JOB_PAYLOAD")
            self.assertNotContains(response, "PRIVATE_PROVIDER_ERROR")
            self.assertNotContains(response, "PRIVATE_CHANNEL_ID")
            self.assertNotContains(response, "private-invite")

        limited_reviewer = User.objects.create_user(
            username="operations-detail-limited-reviewer",
            email="operations-detail-limited-reviewer@example.test",
            is_staff=True,
        )
        self.client.force_login(limited_reviewer)
        denied_job = self.client.get(
            reverse("staff_admin_desk_operations_job", args=[job.pk])
        )
        denied_provisioning = self.client.get(
            reverse("staff_admin_desk_operations_provisioning", args=[operation.pk])
        )
        self.assertEqual(denied_job.status_code, 403)
        self.assertEqual(denied_provisioning.status_code, 403)
