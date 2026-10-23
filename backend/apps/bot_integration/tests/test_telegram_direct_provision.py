"""Regression tests for direct Django-to-Telegram provisioning (no bridge/network)."""

from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, override_settings

from apps.bot_integration.reconcile_jobs import ProvisionTransport
from apps.bot_integration.services.telegram import TelegramBotService
from apps.bot_integration.services.telegram_transport import (
    OUTCOME_ACCEPTED,
    OUTCOME_INDETERMINATE,
    TelegramMessageResult,
)


class DirectProvisionTransportTests(SimpleTestCase):
    @mock.patch.object(TelegramBotService, "create_one_time_invite_link")
    @mock.patch.object(TelegramBotService, "unban_user")
    def test_grant_unbans_before_creating_one_time_invite(self, unban, create):
        unban.return_value = (True, "")
        create.return_value = "https://t.me/+one-use-link"

        link = ProvisionTransport().create_invite_link(12345, "-100123")

        self.assertEqual(link, "https://t.me/+one-use-link")
        unban.assert_called_once_with("-100123", 12345)
        create.assert_called_once_with("-100123")

    @mock.patch.object(TelegramBotService, "create_one_time_invite_link")
    @mock.patch.object(TelegramBotService, "unban_user")
    def test_unban_failure_prevents_invite_creation(self, unban, create):
        unban.return_value = (False, "Telegram network timeout")

        link = ProvisionTransport().create_invite_link(12345, "-100123")

        self.assertIsNone(link)
        create.assert_not_called()

    @mock.patch.object(TelegramBotService, "send_message_result")
    def test_accepted_dm_is_confirmed(self, send):
        send.return_value = TelegramMessageResult(
            outcome=OUTCOME_ACCEPTED, message_id=99
        )

        delivered = ProvisionTransport().send_invite_dm(
            12345, "-100123", "https://t.me/+one-use-link"
        )

        self.assertIs(delivered, True)
        self.assertIn("https://t.me/+one-use-link", send.call_args.args[1])

    @mock.patch.object(TelegramBotService, "send_message_result")
    def test_indeterminate_dm_is_not_reported_as_success(self, send):
        send.return_value = TelegramMessageResult(
            outcome=OUTCOME_INDETERMINATE,
            error_code="timeout",
            error_message="timeout",
        )

        delivered = ProvisionTransport().send_invite_dm(
            12345, "-100123", "https://t.me/+one-use-link"
        )

        self.assertIsNone(delivered)

    @mock.patch.object(TelegramBotService, "is_member", return_value=None)
    def test_membership_transport_error_remains_unknown(self, is_member):
        result = ProvisionTransport().is_member(12345, "-100123")
        self.assertIsNone(result)
        is_member.assert_called_once_with("-100123", 12345)

    @mock.patch.object(TelegramBotService, "ban_user", return_value=(True, ""))
    def test_revoke_uses_direct_ban_api(self, ban):
        result = ProvisionTransport().revoke(12345, "-100123")
        self.assertTrue(result.ok)
        ban.assert_called_once_with("-100123", 12345)


class TelegramWebhookConfigurationTests(SimpleTestCase):
    @override_settings(TELEGRAM_WEBHOOK_SECRET="test_webhook_secret-123")
    @mock.patch.object(TelegramBotService, "_api_request", return_value={"ok": True})
    @mock.patch.object(
        TelegramBotService, "_get_config",
        return_value=SimpleNamespace(telegram_webhook_url="https://academy.example/bot/telegram/webhook/"),
    )
    def test_set_webhook_sends_native_secret_token(self, get_config, api_request):
        self.assertTrue(TelegramBotService.set_webhook())
        api_request.assert_called_once_with("setWebhook", {
            "url": "https://academy.example/bot/telegram/webhook/",
            "secret_token": "test_webhook_secret-123",
            "allowed_updates": ["message"],
        })

    @override_settings(TELEGRAM_WEBHOOK_SECRET="invalid secret with spaces")
    @mock.patch.object(TelegramBotService, "_api_request")
    @mock.patch.object(
        TelegramBotService, "_get_config",
        return_value=SimpleNamespace(telegram_webhook_url="https://academy.example/bot/telegram/webhook/"),
    )
    def test_set_webhook_refuses_invalid_secret_format(self, get_config, api_request):
        self.assertFalse(TelegramBotService.set_webhook())
        api_request.assert_not_called()


class TelegramMembershipResultTests(SimpleTestCase):
    @mock.patch.object(
        TelegramBotService, "_api_request",
        return_value={"ok": True, "result": {"status": "member"}},
    )
    def test_member_status_is_true(self, api_request):
        self.assertIs(TelegramBotService.is_member("-100123", 12345), True)

    @mock.patch.object(
        TelegramBotService, "_api_request",
        return_value={"ok": True, "result": {"status": "left"}},
    )
    def test_left_status_is_false(self, api_request):
        self.assertIs(TelegramBotService.is_member("-100123", 12345), False)

    @mock.patch.object(
        TelegramBotService, "_api_request",
        return_value={"ok": False, "description": "network unavailable"},
    )
    def test_api_error_is_unknown(self, api_request):
        self.assertIsNone(TelegramBotService.is_member("-100123", 12345))
