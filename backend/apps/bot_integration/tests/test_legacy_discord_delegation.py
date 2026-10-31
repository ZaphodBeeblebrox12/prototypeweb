"""Legacy Discord entry points must delegate to managed integration."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LegacyDiscordRouteDelegationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="legacy-discord-routes",
            email="legacy-discord-routes@example.com",
            password="Test-password-123!",
        )
        self.client.force_login(self.user)

    @mock.patch("apps.bot_integration.views.discord_oauth_start")
    def test_old_auth_connect_route_delegates_to_canonical_start(self, canonical_start):
        canonical_start.return_value = mock.Mock(status_code=302)

        self.client.get(reverse("discord_connect"))

        canonical_start.assert_called_once()

    @mock.patch("apps.bot_integration.views.discord_oauth_callback")
    def test_old_auth_callback_route_delegates_to_canonical_callback(self, canonical_callback):
        canonical_callback.return_value = mock.Mock(status_code=302)

        self.client.get(
            reverse("discord_callback"),
            {"code": "authorization-code", "state": "session-state"},
        )

        canonical_callback.assert_called_once()

    @mock.patch("apps.bot_integration.views.unlink_discord")
    def test_old_auth_disconnect_route_delegates_to_managed_role_removal(self, canonical_unlink):
        canonical_unlink.return_value = mock.Mock(status_code=302)

        self.client.post(reverse("discord_disconnect"))

        canonical_unlink.assert_called_once()

    def test_legacy_api_returns_canonical_same_origin_connect_route(self):
        response = self.client.post(reverse("api_discord_connect"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn(
            reverse("bot_integration:discord_connect"),
            response.json()["authorization_url"],
        )

    @mock.patch("apps.bot_integration.views.discord_oauth_callback")
    def test_historical_api_callback_uri_delegates_to_managed_callback(self, canonical_callback):
        canonical_callback.return_value = mock.Mock(status_code=302)

        response = self.client.get(
            reverse("api_discord_callback_legacy"),
            {"code": "authorization-code", "state": "session-state"},
        )

        self.assertEqual(response.status_code, 302)
        canonical_callback.assert_called_once()
