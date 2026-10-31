import hashlib
import hmac
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog

from .models import ProspectEnquiry

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    PROSPECT_ENQUIRY_RECIPIENTS=["course-team@example.test"],
)
class PublicProspectEnquiryTests(TestCase):
    def setUp(self):
        mail.outbox = []

    def valid_payload(self, **overrides):
        payload = {
            "name": "  Test   Prospect ",
            "email": "Prospect@Example.Test ",
            "phone": "",
            "starting_point": "know_patterns",
            "question": "Could you share the next programme details?",
            "contact_consent": "on",
            "marketing_opt_in": "",
            "website": "",
        }
        payload.update(overrides)
        return payload

    def test_construct_enquiry_is_saved_and_customer_and_staff_emails_are_attempted(self):
        response = self.client.post(
            reverse("prospects:enquiry", args=[ProspectEnquiry.Programme.CONSTRUCT]),
            self.valid_payload(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your enquiry has been recorded")
        record = ProspectEnquiry.objects.get()
        self.assertEqual(record.programme, ProspectEnquiry.Programme.CONSTRUCT)
        self.assertEqual(record.name, "Test Prospect")
        self.assertEqual(record.email, "prospect@example.test")
        self.assertTrue(record.contact_consent)
        self.assertFalse(record.marketing_opt_in)
        self.assertTrue(record.source_path.endswith("/enquire/construct/"))
        self.assertEqual(record.status, ProspectEnquiry.Status.NEW)
        self.assertIsNotNone(record.customer_confirmation_sent_at)
        self.assertIsNotNone(record.staff_notification_sent_at)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(record.short_reference, mail.outbox[0].body + mail.outbox[1].body)

    def test_live_classroom_is_stored_as_a_separate_programme(self):
        response = self.client.post(
            reverse("prospects:enquiry", args=[ProspectEnquiry.Programme.LIVE_CLASSROOM]),
            self.valid_payload(),
        )
        self.assertRedirects(response, reverse("prospects:received"))
        record = ProspectEnquiry.objects.get()
        self.assertEqual(record.programme, ProspectEnquiry.Programme.LIVE_CLASSROOM)

    def test_contact_permission_is_required_and_no_record_is_created_without_it(self):
        response = self.client.post(
            reverse("prospects:enquiry", args=[ProspectEnquiry.Programme.CONSTRUCT]),
            self.valid_payload(contact_consent=""),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please confirm that we may contact you")
        self.assertEqual(ProspectEnquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_submission_is_not_persisted_or_notified(self):
        response = self.client.post(
            reverse("prospects:enquiry", args=[ProspectEnquiry.Programme.CONSTRUCT]),
            self.valid_payload(website="https://spam.example"),
        )
        self.assertRedirects(response, reverse("prospects:received"))
        self.assertEqual(ProspectEnquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_rate_limit_uses_a_keyed_email_fingerprint(self):
        email = "prospect@example.test"
        fingerprint = hmac.new(
            str(settings.SECRET_KEY).encode("utf-8"),
            email.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        for index in range(5):
            ProspectEnquiry.objects.create(
                programme=ProspectEnquiry.Programme.CONSTRUCT,
                name=f"Existing Prospect {index}",
                email=email,
                contact_consent=True,
                email_fingerprint=fingerprint,
                created_at=timezone.now() - timedelta(minutes=index),
            )

        response = self.client.post(
            reverse("prospects:enquiry", args=[ProspectEnquiry.Programme.CONSTRUCT]),
            self.valid_payload(email=email),
        )
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "several requests", status_code=429)
        self.assertEqual(ProspectEnquiry.objects.count(), 5)
        self.assertNotIn(email, ProspectEnquiry.objects.first().email_fingerprint)

    @patch("apps.prospects.views.NotificationService.send_simple_email", return_value=False)
    def test_email_provider_failure_does_not_discard_enquiry_or_claim_email_was_sent(self, _send):
        response = self.client.post(
            reverse("prospects:enquiry", args=[ProspectEnquiry.Programme.CONSTRUCT]),
            self.valid_payload(),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        record = ProspectEnquiry.objects.get()
        self.assertIsNone(record.customer_confirmation_sent_at)
        self.assertIsNone(record.staff_notification_sent_at)
        self.assertContains(response, "Your enquiry has been recorded")


class ProspectAdminDeskPermissionTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="prospect-reviewer",
            email="reviewer@example.test",
            password="test-password-123!",
            is_staff=True,
        )
        self.record = ProspectEnquiry.objects.create(
            programme=ProspectEnquiry.Programme.CONSTRUCT,
            name="A prospective learner",
            email="learner@example.test",
            question="I would like details about the next cohort.",
            contact_consent=True,
        )
        self.client.force_login(self.staff)
        self.view_permission = Permission.objects.get(
            content_type__app_label="prospects",
            codename="view_prospectenquiry",
        )
        self.change_permission = Permission.objects.get(
            content_type__app_label="prospects",
            codename="change_prospectenquiry",
        )

    def test_prospect_queue_is_not_visible_without_model_permission(self):
        response = self.client.get(reverse("staff_admin_desk_prospect_enquiries"))
        self.assertEqual(response.status_code, 403)

    def test_view_permission_opens_queue_and_detail_but_cannot_update(self):
        self.staff.user_permissions.add(self.view_permission)

        queue = self.client.get(reverse("staff_admin_desk_prospect_enquiries"))
        self.assertEqual(queue.status_code, 200)
        self.assertContains(queue, "A prospective learner")

        detail = self.client.get(
            reverse("staff_admin_desk_prospect_enquiry", args=[self.record.pk])
        )
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "learner@example.test")
        self.assertNotContains(detail, 'name="staff_notes"')

        denied = self.client.post(
            reverse("staff_admin_desk_prospect_enquiry_update", args=[self.record.pk]),
            {"status": ProspectEnquiry.Status.CONTACTED, "staff_notes": "Called."},
        )
        self.assertEqual(denied.status_code, 403)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, ProspectEnquiry.Status.NEW)

    def test_change_permission_updates_status_and_private_notes_with_audit(self):
        self.staff.user_permissions.add(self.view_permission, self.change_permission)
        response = self.client.post(
            reverse("staff_admin_desk_prospect_enquiry_update", args=[self.record.pk]),
            {
                "status": ProspectEnquiry.Status.CONTACTED,
                "staff_notes": "Called; prospect asked for the programme outline.",
            },
        )
        self.assertRedirects(
            response,
            reverse("staff_admin_desk_prospect_enquiry", args=[self.record.pk]),
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, ProspectEnquiry.Status.CONTACTED)
        self.assertEqual(
            self.record.staff_notes,
            "Called; prospect asked for the programme outline.",
        )
        self.assertIsNotNone(self.record.last_contacted_at)
        audit = AuditLog.objects.get(
            action="admin.prospect_enquiry.updated",
            object_id=str(self.record.pk),
        )
        self.assertEqual(audit.metadata["status_from"], ProspectEnquiry.Status.NEW)
        self.assertEqual(audit.metadata["status_to"], ProspectEnquiry.Status.CONTACTED)
        self.assertTrue(audit.metadata["staff_notes_changed"])

    def test_invalid_status_is_rejected_without_mutating_record(self):
        self.staff.user_permissions.add(self.view_permission, self.change_permission)
        response = self.client.post(
            reverse("staff_admin_desk_prospect_enquiry_update", args=[self.record.pk]),
            {"status": "invented", "staff_notes": "Should not be saved."},
        )
        self.assertRedirects(
            response,
            reverse("staff_admin_desk_prospect_enquiry", args=[self.record.pk]),
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, ProspectEnquiry.Status.NEW)
        self.assertEqual(self.record.staff_notes, "")
        self.assertFalse(AuditLog.objects.filter(
            action="admin.prospect_enquiry.updated",
            object_id=str(self.record.pk),
        ).exists())
