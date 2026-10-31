"""Legacy Discord identity cleanup when the managed account row is absent."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.bot_integration.models import (
    BotAccessAudit,
    DiscordAccount,
    PlanChannelMapping,
    UserChannelAssignment,
)
from apps.subscriptions.models import Plan

User = get_user_model()


class LegacyDiscordUnlinkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="legacy-discord-unlink",
            email="legacy-discord-unlink@example.com",
            password="Test-password-123!",
        )
        self.user.discord_id = "discord-legacy-5001"
        self.user.discord_username = "legacy_member"
        self.user.discord_avatar = "avatar-hash"
        self.user.discord_verified = True
        self.user.save(update_fields=[
            "discord_id", "discord_username", "discord_avatar", "discord_verified",
        ])
        self.client.force_login(self.user)

    @mock.patch("apps.bot_integration.views.DiscordBotService.get_member_roles")
    @mock.patch("apps.bot_integration.views.DiscordBotService.remove_role", return_value=True)
    def test_legacy_disconnect_removes_only_managed_roles_then_clears_identity(
        self, remove_role, get_member_roles,
    ):
        plan = Plan.objects.create(name="Legacy Discord plan", display_order=1)
        PlanChannelMapping.objects.create(
            plan=plan, platform="discord", external_id="managed-plan-role",
        )
        UserChannelAssignment.objects.create(
            user=self.user, platform="discord",
            external_id="managed-assignment-role", is_active=True,
        )
        get_member_roles.side_effect = [
            ["managed-plan-role", "managed-assignment-role", "unmanaged-role"],
            ["unmanaged-role"],
        ]

        response = self.client.post(reverse("bot_integration:discord_unlink"))

        self.assertEqual(response.status_code, 302)
        remove_role.assert_has_calls([
            mock.call("discord-legacy-5001", "managed-assignment-role"),
            mock.call("discord-legacy-5001", "managed-plan-role"),
        ])
        self.assertEqual(remove_role.call_count, 2)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.discord_id)
        self.assertEqual(self.user.discord_username, "")
        self.assertEqual(self.user.discord_avatar, "")
        self.assertFalse(self.user.discord_verified)
        self.assertFalse(DiscordAccount.objects.filter(user=self.user).exists())
        assignment = UserChannelAssignment.objects.get(
            user=self.user, platform="discord", external_id="managed-assignment-role",
        )
        self.assertFalse(assignment.is_active)
        self.assertTrue(BotAccessAudit.objects.filter(
            user=self.user, action="unlink", platform="discord",
            target="discord-legacy-5001", status="success",
        ).exists())

    @mock.patch("apps.bot_integration.views.DiscordBotService.get_member_roles", return_value=None)
    @mock.patch("apps.bot_integration.views.DiscordBotService.remove_role")
    def test_unreadable_live_roles_keep_legacy_identity_for_retry(self, remove_role, _get_member_roles):
        response = self.client.post(reverse("bot_integration:discord_unlink"))

        self.assertEqual(response.status_code, 302)
        remove_role.assert_not_called()
        self.user.refresh_from_db()
        self.assertEqual(self.user.discord_id, "discord-legacy-5001")
        self.assertTrue(self.user.discord_verified)

    @mock.patch("apps.bot_integration.views.DiscordBotService.get_member_roles")
    @mock.patch("apps.bot_integration.views.DiscordBotService.remove_role", return_value=False)
    def test_failed_role_removal_keeps_legacy_identity_for_retry(self, remove_role, get_member_roles):
        UserChannelAssignment.objects.create(
            user=self.user, platform="discord",
            external_id="managed-role", is_active=True,
        )
        get_member_roles.side_effect = [["managed-role"], ["managed-role"]]

        response = self.client.post(reverse("bot_integration:discord_unlink"))

        self.assertEqual(response.status_code, 302)
        remove_role.assert_called_once_with("discord-legacy-5001", "managed-role")
        self.user.refresh_from_db()
        self.assertEqual(self.user.discord_id, "discord-legacy-5001")
        self.assertTrue(self.user.discord_verified)
        self.assertTrue(BotAccessAudit.objects.filter(
            user=self.user, action="revoke", platform="discord",
            target="managed-role", status="failed",
        ).exists())
