"""Regression tests for safe Telegram unlink and paid-access revocation.

The Telegram identity must remain available until all managed channel access
has been removed and verified. No test performs a real Telegram API call.
"""
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.bot_integration.models import (
    BotAccessAudit,
    BotConfig,
    PlanChannelMapping,
    TelegramAccount,
    TelegramVerificationToken,
    UserChannelAssignment,
)
from apps.bot_integration.reconcile_jobs import run_user_reconcile
from apps.subscriptions.models import Plan, Subscription

User = get_user_model()


class FakeRevokeTransport:
    def __init__(self, *, revoke_ok=True, membership_after_revoke=False):
        self.revoke_ok = revoke_ok
        self.membership_after_revoke = membership_after_revoke
        self.revokes = []

    def revoke(self, telegram_user_id, channel_id, idempotency_key=None):
        self.revokes.append((telegram_user_id, channel_id, idempotency_key))
        return SimpleNamespace(
            ok=self.revoke_ok,
            retryable=not self.revoke_ok,
            error_code="" if self.revoke_ok else "telegram_unavailable",
            error_message="" if self.revoke_ok else "Telegram network timeout",
        )

    def is_member(self, telegram_user_id, channel_id):
        if not self.revoke_ok:
            return True
        return self.membership_after_revoke


class TelegramUnlinkReconcileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="telegram-unlink-member",
            email="telegram-unlink-member@example.com",
        )
        self.account = TelegramAccount.objects.create(
            user=self.user,
            chat_id=710000001,
            telegram_user_id=710000001,
            is_active=False,
        )

    def test_successful_unlink_revokes_managed_channel_before_deleting_identity(self):
        plan = Plan.objects.create(name="Unlink Pro", display_order=1)
        Subscription.objects.create(
            user=self.user,
            plan=plan,
            status=Subscription.Status.ACTIVE,
            is_active=True,
        )
        PlanChannelMapping.objects.create(
            plan=plan,
            platform="telegram",
            external_id="-100710000001",
            name="Paid channel",
        )
        transport = FakeRevokeTransport()

        run_user_reconcile(self.user.pk, transport=transport)

        self.assertEqual(
            [(call[0], call[1]) for call in transport.revokes],
            [(710000001, "-100710000001")],
        )
        self.assertFalse(TelegramAccount.objects.filter(user=self.user).exists())
        self.assertFalse(UserChannelAssignment.objects.filter(
            user=self.user, platform="telegram", is_active=True,
        ).exists())
        self.assertTrue(BotAccessAudit.objects.filter(
            user=self.user,
            action="unlink",
            platform="telegram",
            status="success",
            target="710000001",
        ).exists())

    def test_failed_revoke_keeps_identity_and_assignment_for_retry(self):
        assignment = UserChannelAssignment.objects.create(
            user=self.user,
            platform="telegram",
            external_id="-100710000002",
            is_active=True,
        )
        transport = FakeRevokeTransport(revoke_ok=False)

        with self.assertRaisesRegex(RuntimeError, "Telegram revoke failed"):
            run_user_reconcile(self.user.pk, transport=transport)

        self.account.refresh_from_db()
        assignment.refresh_from_db()
        self.assertFalse(self.account.is_active)
        self.assertTrue(assignment.is_active)
        self.assertTrue(TelegramAccount.objects.filter(user=self.user).exists())
        self.assertFalse(BotAccessAudit.objects.filter(
            user=self.user, action="unlink", status="success",
        ).exists())

    def test_successful_ban_without_verified_absence_does_not_complete_unlink(self):
        UserChannelAssignment.objects.create(
            user=self.user,
            platform="telegram",
            external_id="-100710000003",
            is_active=True,
        )
        transport = FakeRevokeTransport(
            revoke_ok=True,
            membership_after_revoke=True,
        )

        with self.assertRaisesRegex(RuntimeError, "Telegram revoke failed"):
            run_user_reconcile(self.user.pk, transport=transport)

        self.assertTrue(TelegramAccount.objects.filter(user=self.user).exists())
        self.assertTrue(UserChannelAssignment.objects.filter(
            user=self.user, platform="telegram", is_active=True,
        ).exists())

    def test_orphaned_active_assignment_is_not_silently_reported_as_reconciled(self):
        self.account.delete()
        UserChannelAssignment.objects.create(
            user=self.user,
            platform="telegram",
            external_id="-100710000004",
            is_active=True,
        )

        with self.assertRaisesRegex(RuntimeError, "without a linked Telegram identity"):
            run_user_reconcile(self.user.pk, transport=FakeRevokeTransport())

        self.assertTrue(UserChannelAssignment.objects.filter(
            user=self.user, platform="telegram", is_active=True,
        ).exists())


class OrphanedTelegramCleanupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="orphaned-telegram-member",
            email="orphaned-telegram-member@example.com",
        )
        BotAccessAudit.objects.create(
            user=self.user,
            action="unlink",
            platform="telegram",
            target="710000030",
            status="success",
        )

    def test_recovers_orphaned_assignment_using_prior_unlink_identity(self):
        assignment = UserChannelAssignment.objects.create(
            user=self.user,
            platform="telegram",
            external_id="-100710000030",
            is_active=True,
        )
        transport = FakeRevokeTransport()

        run_user_reconcile(self.user.pk, transport=transport)

        self.assertEqual(
            [(call[0], call[1]) for call in transport.revokes],
            [(710000030, "-100710000030")],
        )
        assignment.refresh_from_db()
        self.assertFalse(assignment.is_active)
        self.assertTrue(BotAccessAudit.objects.filter(
            user=self.user,
            action="revoke",
            platform="telegram",
            target="-100710000030",
            status="success",
        ).exists())
        self.assertFalse(TelegramAccount.objects.filter(user=self.user).exists())

    def test_recovers_open_grant_without_assignment(self):
        from apps.jobs.models import ProvisioningOperation

        op = ProvisioningOperation.objects.create(
            user_id=self.user.pk,
            channel_id="-100710000031",
            telegram_user_id=710000030,
            operation=ProvisioningOperation.OP_GRANT,
            state=ProvisioningOperation.ST_SENT,
            invite_link="https://t.me/+legacy-invite",
        )
        transport = FakeRevokeTransport()

        run_user_reconcile(self.user.pk, transport=transport)

        self.assertEqual(
            [(call[0], call[1]) for call in transport.revokes],
            [(710000030, "-100710000031")],
        )
        op.refresh_from_db()
        self.assertEqual(op.state, ProvisioningOperation.ST_FAILED)
        self.assertEqual(op.last_error, "superseded_by_revoke")

    def test_orphaned_assignment_without_numeric_unlink_audit_fails_closed(self):
        self.user.bot_audits.all().delete()
        assignment = UserChannelAssignment.objects.create(
            user=self.user,
            platform="telegram",
            external_id="-100710000032",
            is_active=True,
        )

        with self.assertRaisesRegex(RuntimeError, "without a recoverable Telegram identity"):
            run_user_reconcile(self.user.pk, transport=FakeRevokeTransport())

        assignment.refresh_from_db()
        self.assertTrue(assignment.is_active)


class TelegramUnlinkRouteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="telegram-unlink-route",
            email="telegram-unlink-route@example.com",
            password="Test-password-123!",
        )
        self.client.force_login(self.user)
        self.account = TelegramAccount.objects.create(
            user=self.user,
            chat_id=710000010,
            telegram_user_id=710000010,
            is_active=True,
        )

    @mock.patch("apps.jobs.enqueue.enqueue_reconcile")
    def test_unlink_pauses_account_and_enqueues_before_removing_identity(self, enqueue):
        stale_token = TelegramVerificationToken.create_token(self.user)
        response = self.client.post(reverse("bot_integration:telegram_unlink"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{reverse('dashboard')}#connections")
        self.account.refresh_from_db()
        self.assertFalse(self.account.is_active)
        self.assertTrue(TelegramAccount.objects.filter(user=self.user).exists())
        self.assertFalse(TelegramVerificationToken.objects.filter(pk=stale_token.pk).exists())
        enqueue.assert_called_once_with(self.user.pk, reason="telegram_unlink")
        self.assertFalse(BotAccessAudit.objects.filter(
            user=self.user, action="unlink", status="success",
        ).exists())

    @mock.patch("apps.jobs.enqueue.enqueue_reconcile")
    def test_retry_disconnect_requeues_an_already_inactive_account(self, enqueue):
        self.account.is_active = False
        self.account.save(update_fields=["is_active"])

        response = self.client.post(reverse("bot_integration:telegram_unlink"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(TelegramAccount.objects.filter(user=self.user).exists())
        enqueue.assert_called_once_with(self.user.pk, reason="telegram_unlink")

    @mock.patch("apps.jobs.enqueue.enqueue_reconcile")
    def test_connect_is_blocked_and_tokens_invalidated_for_orphaned_access(self, enqueue):
        from apps.bot_integration.models import BotAccessAudit

        self.account.delete()
        UserChannelAssignment.objects.create(
            user=self.user,
            platform="telegram",
            external_id="-100710000010",
            is_active=True,
        )
        BotAccessAudit.objects.create(
            user=self.user,
            action="unlink",
            platform="telegram",
            target="710000010",
            status="success",
        )
        BotConfig.objects.update_or_create(
            pk=1,
            defaults={
                "telegram_bot_username": "tradethesis_test_bot",
                "telegram_bot_token": "test-token-not-used-for-network-calls",
                "is_active": True,
            },
        )
        stale_token = TelegramVerificationToken.create_token(self.user)

        response = self.client.get(reverse("bot_integration:telegram_connect"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{reverse('dashboard')}#connections")
        self.assertFalse(TelegramVerificationToken.objects.filter(pk=stale_token.pk).exists())
        enqueue.assert_called_once_with(self.user.pk, reason="orphaned_telegram_cleanup")

    def test_connect_is_blocked_while_previous_disconnect_is_pending(self):
        BotConfig.objects.update_or_create(
            pk=1,
            defaults={
                "telegram_bot_username": "tradethesis_test_bot",
                "telegram_bot_token": "test-token-not-used-for-network-calls",
                "is_active": True,
            },
        )
        self.account.is_active = False
        self.account.save(update_fields=["is_active"])

        response = self.client.get(reverse("bot_integration:telegram_connect"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{reverse('dashboard')}#connections")
        self.assertFalse(TelegramVerificationToken.objects.filter(user=self.user).exists())
        follow = self.client.get(reverse("dashboard"))
        self.assertContains(follow, "previous Telegram disconnect is still being completed")
        self.assertContains(follow, "Disconnect pending")
        self.assertContains(follow, "Retry disconnect")



class CanonicalProfileConnectionStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="canonical-profile-member",
            email="canonical-profile-member@example.com",
            password="Test-password-123!",
        )
        self.client.force_login(self.user)

    def test_profile_does_not_treat_legacy_telegram_identity_as_bot_link(self):
        self.user.telegram_id = 710000020
        self.user.telegram_username = "legacy_handle"
        self.user.telegram_verified = True
        self.user.save(update_fields=[
            "telegram_id", "telegram_username", "telegram_verified",
        ])

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Not connected to this account.")
        self.assertNotContains(response, "Connected as @legacy_handle")

    def test_profile_uses_canonical_telegram_account(self):
        TelegramAccount.objects.create(
            user=self.user,
            chat_id=710000021,
            telegram_user_id=710000021,
            username="canonical_handle",
            is_active=True,
        )

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connected as @canonical_handle")
        self.assertContains(response, "Disconnect Telegram")

    def test_profile_shows_retry_for_pending_telegram_disconnect(self):
        TelegramAccount.objects.create(
            user=self.user,
            chat_id=710000022,
            telegram_user_id=710000022,
            username="pending_handle",
            is_active=False,
        )

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Disconnect pending")
        self.assertContains(response, "Retry disconnect")

    def test_profile_uses_canonical_discord_account_not_legacy_fields(self):
        self.user.discord_id = "legacy-discord-id"
        self.user.discord_username = "legacy-discord-handle"
        self.user.discord_verified = True
        self.user.save(update_fields=[
            "discord_id", "discord_username", "discord_verified",
        ])

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connect Discord")
        self.assertNotContains(response, "legacy-discord-handle")



class DelayedTelegramDeepLinkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="delayed-telegram-link",
            email="delayed-telegram-link@example.com",
        )
        self.account = TelegramAccount.objects.create(
            user=self.user,
            chat_id=710000040,
            telegram_user_id=710000040,
            is_active=False,
        )
        self.token = TelegramVerificationToken.create_token(self.user)

    @mock.patch("apps.jobs.enqueue.enqueue_reconcile")
    @mock.patch("apps.bot_integration.views.TelegramBotService")
    def test_delayed_deep_link_cannot_reactivate_pending_disconnect(self, telegram, enqueue):
        import json
        from django.test import override_settings

        body = json.dumps({
            "update_id": 987654,
            "message": {
                "message_id": 42,
                "from": {
                    "id": 710000040,
                    "is_bot": False,
                    "first_name": "Member",
                },
                "chat": {"id": 710000040, "type": "private"},
                "text": f"/start verify_{self.token.token}",
            },
        }).encode()

        with override_settings(TELEGRAM_WEBHOOK_SECRET="native-test-secret"):
            response = self.client.post(
                reverse("bot_integration:telegram_webhook"),
                data=body,
                content_type="application/json",
                HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="native-test-secret",
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.account.refresh_from_db()
        self.assertFalse(self.account.is_active)
        self.assertFalse(TelegramVerificationToken.objects.filter(pk=self.token.pk).exists())
        enqueue.assert_not_called()
        telegram.send_message.assert_called_once()
        self.assertIn("disconnect is still being completed", telegram.send_message.call_args.args[1])
