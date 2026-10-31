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
        response = self.client.post(reverse("bot_integration:telegram_unlink"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{reverse('dashboard')}#connections")
        self.account.refresh_from_db()
        self.assertFalse(self.account.is_active)
        self.assertTrue(TelegramAccount.objects.filter(user=self.user).exists())
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
