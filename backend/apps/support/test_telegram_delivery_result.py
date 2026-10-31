"""Support notifications must reflect actual Telegram transport outcomes."""
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from apps.support.services import _send_telegram


class SupportTelegramDeliveryResultTests(SimpleTestCase):
    @mock.patch("apps.support.services.TransactionalTelegramService.send_text")
    def test_reports_success_only_when_transactional_sender_reports_sent(self, send_text):
        send_text.return_value = SimpleNamespace(
            sent=True,
            skipped=False,
            outcome="accepted",
            error_code="",
        )

        self.assertTrue(_send_telegram(mock.Mock(), "Ticket update", 101, "notice"))

    @mock.patch("apps.support.services.TransactionalTelegramService.send_text")
    def test_skipped_unlinked_account_is_not_reported_as_delivered(self, send_text):
        send_text.return_value = SimpleNamespace(
            sent=False,
            skipped=True,
            skip_reason="no linked Telegram account",
            outcome="skipped",
            error_code="",
        )

        self.assertFalse(_send_telegram(mock.Mock(), "Ticket update", 102, "notice"))

    @mock.patch("apps.support.services.TransactionalTelegramService.send_text")
    def test_provider_failure_is_not_reported_as_delivered(self, send_text):
        send_text.return_value = SimpleNamespace(
            sent=False,
            skipped=False,
            outcome="error",
            error_code="telegram_unauthorized",
        )

        self.assertFalse(_send_telegram(mock.Mock(), "Ticket update", 103, "notice"))

    @mock.patch("apps.support.services.TransactionalTelegramService.send_text", side_effect=RuntimeError("transport down"))
    def test_transport_exception_is_not_reported_as_delivered(self, send_text):
        self.assertFalse(_send_telegram(mock.Mock(), "Ticket update", 104, "notice"))
