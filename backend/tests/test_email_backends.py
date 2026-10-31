import base64
from unittest.mock import Mock, patch

import requests
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.test import TestCase, override_settings

from apps.core.email_backends import ResendEmailBackend
from apps.emailing.models import Delivery


@override_settings(
    RESEND_API_KEY="re_test_key",
    RESEND_API_TIMEOUT=7,
    DEFAULT_FROM_EMAIL="TradeThesis <noreply@tradethesis.in>",
)
class ResendEmailBackendTests(TestCase):
    def _success_response(self, email_id="re_test_message_id"):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"id": email_id}
        return response

    @patch("apps.core.email_backends.requests.post")
    def test_sends_allauth_style_text_and_html_email_over_https(self, post):
        post.return_value = self._success_response()
        message = EmailMultiAlternatives(
            subject="Confirm your email",
            body="Open the confirmation link.",
            from_email=None,
            to=["learner@example.com"],
            reply_to=["support@example.com"],
            headers={"X-TradeThesis": "account"},
        )
        message.attach_alternative("<p>Open the confirmation link.</p>", "text/html")

        sent = ResendEmailBackend().send_messages([message])

        self.assertEqual(sent, 1)
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://api.resend.com/emails")
        self.assertEqual(
            kwargs["headers"]["Authorization"],
            "Bearer re_test_key",
        )
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
        self.assertEqual(kwargs["headers"]["Idempotency-Key"], message._tradethesis_idempotency_key)
        self.assertEqual(kwargs["timeout"], 7.0)
        self.assertEqual(
            kwargs["json"],
            {
                "from": "TradeThesis <noreply@tradethesis.in>",
                "to": ["learner@example.com"],
                "subject": "Confirm your email",
                "reply_to": ["support@example.com"],
                "headers": {"X-TradeThesis": "account"},
                "text": "Open the confirmation link.",
                "html": "<p>Open the confirmation link.</p>",
            },
        )

        delivery = Delivery.objects.get(to_email="learner@example.com")
        self.assertEqual(delivery.state, Delivery.State.SENT)
        self.assertEqual(delivery.provider, "resend")
        self.assertEqual(delivery.provider_message_id, "re_test_message_id")
        self.assertIsNotNone(delivery.sent_at)

    @patch("apps.core.email_backends.requests.post")
    def test_encodes_attachments_and_tracks_provider_id(self, post):
        post.return_value = self._success_response("re_receipt_id")
        message = EmailMultiAlternatives(
            subject="Receipt",
            body="Attached.",
            from_email="billing@tradethesis.in",
            to=["learner@example.com"],
        )
        message.attach("receipt.txt", "sample receipt", "text/plain")

        self.assertEqual(ResendEmailBackend().send_messages([message]), 1)
        payload = post.call_args.kwargs["json"]
        self.assertEqual(
            payload["attachments"],
            [
                {
                    "filename": "receipt.txt",
                    "content": base64.b64encode(b"sample receipt").decode("ascii"),
                    "content_type": "text/plain",
                }
            ],
        )
        self.assertEqual(
            Delivery.objects.get(to_email="learner@example.com").provider_message_id,
            "re_receipt_id",
        )

    @patch("apps.core.email_backends.requests.post")
    def test_reuses_same_message_idempotency_key_and_does_not_double_send(self, post):
        post.return_value = self._success_response("re_once")
        message = EmailMultiAlternatives(
            subject="Confirm",
            body="Confirm",
            from_email="noreply@tradethesis.in",
            to=["learner@example.com"],
        )
        backend = ResendEmailBackend()

        self.assertEqual(backend.send_messages([message]), 1)
        first_key = message._tradethesis_idempotency_key
        self.assertEqual(backend.send_messages([message]), 1)

        self.assertEqual(post.call_count, 1)
        self.assertEqual(
            post.call_args.kwargs["headers"]["Idempotency-Key"],
            first_key,
        )
        self.assertEqual(Delivery.objects.filter(to_email="learner@example.com").count(), 1)

    @override_settings(RESEND_API_KEY="")
    def test_requires_api_key(self):
        with self.assertRaises(ImproperlyConfigured):
            ResendEmailBackend().send_messages(
                [
                    EmailMultiAlternatives(
                        subject="Confirm",
                        body="Confirm",
                        from_email="noreply@tradethesis.in",
                        to=["learner@example.com"],
                    )
                ]
            )
        self.assertEqual(Delivery.objects.count(), 0)

    @patch("apps.core.email_backends.requests.post")
    def test_provider_failure_marks_delivery_failed_without_logging_body(self, post):
        response = Mock(status_code=401)
        response.raise_for_status.side_effect = requests.HTTPError("Unauthorized")
        post.return_value = response
        message = EmailMultiAlternatives(
            subject="Confirm",
            body="secret body not for logs",
            from_email="noreply@tradethesis.in",
            to=["learner@example.com"],
        )

        with self.assertRaisesRegex(RuntimeError, "HTTPError"):
            ResendEmailBackend().send_messages([message])

        delivery = Delivery.objects.get(to_email="learner@example.com")
        self.assertEqual(delivery.state, Delivery.State.FAILED)
        self.assertEqual(delivery.error, "resend_http_401")
        self.assertNotIn("secret body", delivery.error)

    @patch("apps.core.email_backends.requests.post")
    def test_fail_silently_returns_zero_for_provider_failure(self, post):
        response = Mock(status_code=503)
        response.raise_for_status.side_effect = requests.HTTPError("Unavailable")
        post.return_value = response
        message = EmailMultiAlternatives(
            subject="Confirm",
            body="Confirm",
            from_email="noreply@tradethesis.in",
            to=["learner@example.com"],
        )

        self.assertEqual(ResendEmailBackend(fail_silently=True).send_messages([message]), 0)
        self.assertEqual(
            Delivery.objects.get(to_email="learner@example.com").state,
            Delivery.State.FAILED,
        )

    def test_empty_message_list_is_a_noop(self):
        self.assertEqual(ResendEmailBackend().send_messages([]), 0)
        self.assertEqual(Delivery.objects.count(), 0)


@override_settings(
    EMAIL_BACKEND="apps.core.email_backends.ResendEmailBackend",
    RESEND_API_KEY="re_test_key",
    DEFAULT_FROM_EMAIL="TradeThesis <noreply@tradethesis.in>",
    SITE_BASE_URL="https://academy.example.test",
    EMAIL_LOGO_URL="https://academy.example.test/logo.png",
)
class AllauthEmailRoutingTests(TestCase):
    @patch("apps.core.email_backends.requests.post")
    def test_confirmation_and_password_reset_use_resend_backend(self, post):
        from types import SimpleNamespace

        from apps.accounts.adapters import CustomAccountAdapter

        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"id": "re_allauth_id"}
        post.return_value = response

        adapter = CustomAccountAdapter()
        user = SimpleNamespace(
            username="staging-user",
            get_username=lambda: "staging-user",
        )
        adapter.send_mail(
            "account/email/email_confirmation_signup",
            "learner@example.com",
            {
                "user": user,
                "current_site": SimpleNamespace(name="TradeThesis", domain="academy.example.test"),
                "activate_url": "https://academy.example.test/accounts/confirm-email/test-key/",
                "key": "test-key",
            },
        )
        adapter.send_mail(
            "account/email/password_reset_key",
            "learner@example.com",
            {
                "user": user,
                "username": "staging-user",
                "password_reset_url": "https://academy.example.test/accounts/password/reset/key/test-key/",
                "key": "test-key",
            },
        )

        self.assertEqual(post.call_count, 2)
        self.assertEqual(
            set(Delivery.objects.values_list("provider_message_id", flat=True)),
            {"re_allauth_id"},
        )
        self.assertEqual(Delivery.objects.filter(to_email="learner@example.com").count(), 2)
