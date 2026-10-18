"""Regression coverage for the member desk Telegram connection flow.

These tests cover only the Django route and token/deep-link wiring. No Telegram
network request is made.
"""
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.bot_integration.models import BotConfig, TelegramVerificationToken

User = get_user_model()


class TelegramConnectionFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="telegram-member",
            email="telegram-member@example.com",
            password="Test-password-123!",
        )
        self.client.force_login(self.user)

    def configure_bot(self, username):
        config, _ = BotConfig.objects.update_or_create(
            pk=1,
            defaults={
                "telegram_bot_username": username,
                "telegram_bot_token": "test-token-not-used-for-network-calls",
                "is_active": True,
            },
        )
        return config

    def test_member_desk_connect_button_uses_deep_link_route(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        connect_path = reverse("bot_integration:telegram_connect")
        self.assertContains(response, f'href="{connect_path}"')

    def test_missing_bot_username_returns_to_member_desk_not_legacy_profile(self):
        self.configure_bot("")
        with override_settings(TELEGRAM_BOT_USERNAME=""):
            response = self.client.get(reverse("bot_integration:telegram_connect"))

        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)
        follow = self.client.get(response["Location"])
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, "Telegram connection is not configured yet")
        self.assertContains(follow, "member-flash-error")
        self.assertNotEqual(response["Location"], reverse("profile"))

    def test_environment_bot_username_is_used_when_database_username_is_blank(self):
        self.configure_bot("")
        with override_settings(TELEGRAM_BOT_USERNAME="@tradethesis_env_bot"):
            response = self.client.get(reverse("bot_integration:telegram_connect"))

        self.assertEqual(response.status_code, 302)
        parsed = urlsplit(response["Location"])
        self.assertEqual(parsed.netloc, "t.me")
        self.assertEqual(parsed.path, "/tradethesis_env_bot")
        self.assertTrue(
            parse_qs(parsed.query).get("start", [""])[0].startswith("verify_")
        )

    def test_connect_generates_verification_token_and_redirects_to_telegram(self):
        self.configure_bot("tradethesis_test_bot")
        old_token = TelegramVerificationToken.create_token(self.user)

        response = self.client.get(reverse("bot_integration:telegram_connect"))

        self.assertEqual(response.status_code, 302)
        location = response["Location"]
        parsed = urlsplit(location)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "t.me")
        self.assertEqual(parsed.path, "/tradethesis_test_bot")
        self.assertTrue(parse_qs(parsed.query).get("start", [""])[0].startswith("verify_"))

        start_value = parse_qs(parsed.query)["start"][0]
        token_value = start_value.removeprefix("verify_")
        token = TelegramVerificationToken.objects.get(user=self.user, token=token_value)
        self.assertTrue(token.is_valid())
        self.assertFalse(TelegramVerificationToken.objects.filter(pk=old_token.pk).exists())

    def test_connect_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("bot_integration:telegram_connect"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response["Location"])
