"""Regression coverage for public programme enquiries and Admin Desk follow-up."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import Notification
from apps.support.models import CourseEnquiry, CourseEnquiryReply

User = get_user_model()


@override_settings(
    TRADETHESIS_PUBLIC_SITE_ORIGINS=["https://public.example.test"],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class PublicCourseEnquiryTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="sales-reviewer",
            email="sales-reviewer@example.test",
            password="test-password-123!",
            is_staff=True,
        )
        self.staff.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="support",
                codename="view_courseenquiry",
            ),
            Permission.objects.get(
                content_type__app_label="support",
                codename="change_courseenquiry",
            ),
        )

    def _payload(self, **overrides):
        payload = {
            "programme": CourseEnquiry.Programme.CONSTRUCT,
            "name": "  Priya  Trader  ",
            "email": "Priya.Example@Example.Test ",
            "starting_point": CourseEnquiry.StartingPoint.RISK,
            "message": "I want to understand the weekly review process.",
            "consent": "yes",
        }
        payload.update(overrides)
        return payload

    def _post(self, payload=None, origin="https://public.example.test"):
        return self.client.post(
            reverse("public_course_enquiry_create"),
            payload if payload is not None else self._payload(),
            HTTP_ORIGIN=origin,
        )

    def test_valid_public_enquiry_is_saved_and_receipt_is_accepted(self):
        response = self._post()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "https://public.example.test/construct.html?enquiry=received#enquiry-form",
        )
        enquiry = CourseEnquiry.objects.get()
        self.assertEqual(enquiry.name, "Priya Trader")
        self.assertEqual(enquiry.email, "priya.example@example.test")
        self.assertEqual(enquiry.programme, CourseEnquiry.Programme.CONSTRUCT)
        self.assertEqual(enquiry.status, CourseEnquiry.Status.NEW)
        self.assertIsNotNone(enquiry.consent_at)
        self.assertEqual(enquiry.confirmation_email_status, "accepted")
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("not a course enrolment", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["priya.example@example.test"])
        self.assertEqual(mail.outbox[1].to, ["sales-reviewer@example.test"])
        notice = Notification.objects.get(
            user=self.staff,
            metadata__source="course_enquiry",
            metadata__enquiry_id=str(enquiry.pk),
        )
        self.assertEqual(
            notice.link,
            reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk]),
        )

    def test_live_classroom_enquiry_uses_its_own_programme_and_return_page(self):
        response = self._post({
            **self._payload(),
            "programme": CourseEnquiry.Programme.LIVE_CLASSROOM,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "https://public.example.test/live-class.html?enquiry=received#enquiry-form",
        )
        enquiry = CourseEnquiry.objects.get()
        self.assertEqual(enquiry.programme, CourseEnquiry.Programme.LIVE_CLASSROOM)

    def test_wrong_origin_is_rejected_without_saving_or_sending_email(self):
        response = self._post(origin="https://attacker.example.test")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(CourseEnquiry.objects.count(), 0)
        self.assertEqual(mail.outbox, [])

    def test_invalid_email_missing_consent_or_invalid_programme_is_not_saved(self):
        bad_email = self._post(self._payload(email="not-an-email"))
        missing_consent = self._post(self._payload(consent=""))
        bad_programme = self._post(self._payload(programme="unknown"))
        self.assertEqual(bad_email["Location"].split("enquiry=")[-1].split("#")[0], "invalid")
        self.assertIn("enquiry=invalid", missing_consent["Location"])
        self.assertIn("enquiry=invalid", bad_programme["Location"])
        self.assertEqual(CourseEnquiry.objects.count(), 0)

    def test_honeypot_is_a_quiet_no_op(self):
        response = self._post(self._payload(company_website="spam.example"))

        self.assertIn("enquiry=received", response["Location"])
        self.assertEqual(CourseEnquiry.objects.count(), 0)
        self.assertEqual(mail.outbox, [])

    def test_same_email_is_limited_to_two_recent_enquiries_per_programme(self):
        self._post()
        self._post(self._payload(message="Second question."))
        third = self._post(self._payload(message="Third question."))

        self.assertIn("enquiry=recent", third["Location"])
        self.assertEqual(CourseEnquiry.objects.count(), 2)

    def test_public_endpoint_requires_post(self):
        response = self.client.get(reverse("public_course_enquiry_create"))
        self.assertEqual(response.status_code, 405)

    def test_staff_without_enquiry_permission_cannot_open_queue(self):
        unprivileged = User.objects.create_user(
            username="unprivileged-staff",
            email="other-staff@example.test",
            password="test-password-123!",
            is_staff=True,
        )
        self.client.force_login(unprivileged)
        response = self.client.get(reverse("staff_admin_desk_course_enquiries"))
        self.assertEqual(response.status_code, 403)

    def test_authorized_staff_can_filter_and_open_queue(self):
        enquiry = CourseEnquiry.objects.create(
            programme=CourseEnquiry.Programme.CONSTRUCT,
            name="Prospect One",
            email="prospect@example.test",
            message="Interested in CONSTRUCT.",
            consent_at=timezone.now(),
        )
        self.client.force_login(self.staff)
        response = self.client.get(
            reverse("staff_admin_desk_course_enquiries"),
            {"status": CourseEnquiry.Status.NEW, "programme": CourseEnquiry.Programme.CONSTRUCT},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prospect One")
        self.assertContains(response, "prospect@example.test")
        self.assertContains(
            response,
            reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk]),
        )

    def test_reply_is_logged_and_status_changes_only_when_email_backend_accepts(self):
        enquiry = CourseEnquiry.objects.create(
            programme=CourseEnquiry.Programme.CONSTRUCT,
            name="Prospect Two",
            email="prospect.two@example.test",
            message="Please tell me about the programme.",
            consent_at=timezone.now(),
        )
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk]),
            {
                "action": "send_reply",
                "subject": "About your CONSTRUCT enquiry",
                "body": "Thank you for getting in touch. Here are the programme details.",
            },
        )

        self.assertRedirects(
            response,
            reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk]),
        )
        reply = CourseEnquiryReply.objects.get(enquiry=enquiry)
        self.assertEqual(reply.status, CourseEnquiryReply.Status.ACCEPTED)
        self.assertEqual(reply.author, self.staff)
        self.assertEqual(reply.sent_at is not None, True)
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, CourseEnquiry.Status.REPLIED)
        self.assertEqual(enquiry.responded_by, self.staff)
        self.assertEqual(mail.outbox[-1].to, ["prospect.two@example.test"])

    def test_view_only_staff_cannot_send_reply_or_change_enquiry(self):
        enquiry = CourseEnquiry.objects.create(
            programme=CourseEnquiry.Programme.LIVE_CLASSROOM,
            name="Read Only Prospect",
            email="readonly@example.test",
            consent_at=timezone.now(),
        )
        viewer = User.objects.create_user(
            username="enquiry-viewer",
            email="viewer@example.test",
            password="test-password-123!",
            is_staff=True,
        )
        viewer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="support",
                codename="view_courseenquiry",
            )
        )
        self.client.force_login(viewer)
        response = self.client.post(
            reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk]),
            {"action": "status", "status": CourseEnquiry.Status.CLOSED},
        )
        self.assertEqual(response.status_code, 403)
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, CourseEnquiry.Status.NEW)
