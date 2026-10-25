import base64
from unittest.mock import Mock, patch

import requests
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.test import SimpleTestCase, override_settings

from apps.core.email_backends import ResendEmailBackend


@override_settings(
    RESEND_API_KEY="re_test_key",
    RESEND_API_TIMEOUT=7,
    DEFAULT_FROM_EMAIL="TradeThesis <noreply@example.com>",
)
class ResendEmailBackendTests(SimpleTestCase):
    @patch("apps.core.email_backends.requests.post")
    def test_sends_allauth_style_text_and_html_email_over_https(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        post.return_value = response
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
        post.assert_called_once_with(
            "https://api.resend.com/emails",
            headers={
                "Authorization": "Bearer re_test_key",
                "Content-Type": "application/json",
            },
            json={
                "from": "TradeThesis <noreply@example.com>",
                "to": ["learner@example.com"],
                "subject": "Confirm your email",
                "reply_to": ["support@example.com"],
                "headers": {"X-TradeThesis": "account"},
                "text": "Open the confirmation link.",
                "html": "<p>Open the confirmation link.</p>",
            },
            timeout=7.0,
        )

    @patch("apps.core.email_backends.requests.post")
    def test_encodes_attachments(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        post.return_value = response
        message = EmailMultiAlternatives(
            subject="Receipt",
            body="Attached.",
            from_email="billing@example.com",
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

    @override_settings(RESEND_API_KEY="")
    def test_requires_api_key(self):
        with self.assertRaises(ImproperlyConfigured):
            ResendEmailBackend().send_messages(
                [
                    EmailMultiAlternatives(
                        subject="Confirm",
                        body="Confirm",
                        from_email="noreply@example.com",
                        to=["learner@example.com"],
                    )
                ]
            )

    @patch("apps.core.email_backends.requests.post")
    def test_reports_provider_failure_without_leaking_payload(self, post):
        response = Mock(status_code=401)
        response.raise_for_status.side_effect = requests.HTTPError("Unauthorized")
        post.return_value = response
        message = EmailMultiAlternatives(
            subject="Confirm",
            body="secret body not for logs",
            from_email="noreply@example.com",
            to=["learner@example.com"],
        )

        with self.assertRaisesRegex(RuntimeError, "HTTPError"):
            ResendEmailBackend().send_messages([message])

    @patch("apps.core.email_backends.requests.post")
    def test_fail_silently_returns_zero_for_provider_failure(self, post):
        response = Mock(status_code=503)
        response.raise_for_status.side_effect = requests.HTTPError("Unavailable")
        post.return_value = response
        message = EmailMultiAlternatives(
            subject="Confirm",
            body="Confirm",
            from_email="noreply@example.com",
            to=["learner@example.com"],
        )

        self.assertEqual(ResendEmailBackend(fail_silently=True).send_messages([message]), 0)

    def test_empty_message_list_is_a_noop(self):
        self.assertEqual(ResendEmailBackend().send_messages([]), 0)
