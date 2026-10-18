"""Channel membership snapshot + display builder tests (display-only layer)."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.bot_integration.models import (
    ChannelMembershipSnapshot,
    ChannelMesh,
    ChannelMeshDestination,
    CommunityChannel,
    PlanChannelMapping,
    PlanMeshMapping,
    TelegramAccount,
    UserChannelAssignment,
    UserMeshAssignment,
)
from apps.bot_integration.services import channel_sync
from apps.subscriptions.models import Plan, Subscription

User = get_user_model()


class ChannelSyncTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="member1", password="x")
        self.account = TelegramAccount.objects.create(
            user=self.user, chat_id=555111, telegram_user_id=555111)
        self.ch = CommunityChannel.objects.create(
            platform="telegram", external_id="@free_signals",
            name="Free Signals", invite_url="https://t.me/free_signals")

    def _resp(self, status):
        return {"ok": True, "result": {"status": status}}

    def test_member_status_recorded(self):
        with mock.patch.object(channel_sync.TelegramBotService, "_api_request",
                               return_value=self._resp("member")):
            channel_sync.sync_channel_memberships_for_user(self.user.id)
        snap = ChannelMembershipSnapshot.objects.get(user=self.user, channel=self.ch)
        self.assertTrue(snap.is_member)
        self.assertIsNotNone(snap.checked_at)

    def test_kicked_and_left_not_members(self):
        for status in ("kicked", "left"):
            with mock.patch.object(channel_sync.TelegramBotService, "_api_request",
                                   return_value=self._resp(status)):
                channel_sync.sync_channel_memberships_for_user(self.user.id)
            snap = ChannelMembershipSnapshot.objects.get(user=self.user, channel=self.ch)
            self.assertFalse(snap.is_member, status)

    def test_admin_and_creator_count_as_member(self):
        for status in ("administrator", "creator"):
            with mock.patch.object(channel_sync.TelegramBotService, "_api_request",
                                   return_value=self._resp(status)):
                channel_sync.sync_channel_memberships_for_user(self.user.id)
            snap = ChannelMembershipSnapshot.objects.get(user=self.user, channel=self.ch)
            self.assertTrue(snap.is_member, status)

    def test_repeated_sync_updates_single_snapshot(self):
        with mock.patch.object(channel_sync.TelegramBotService, "_api_request",
                               return_value=self._resp("member")):
            channel_sync.sync_channel_memberships_for_user(self.user.id)
            channel_sync.sync_channel_memberships_for_user(self.user.id)
        self.assertEqual(ChannelMembershipSnapshot.objects.count(), 1)

    def test_no_account_is_noop(self):
        TelegramAccount.objects.all().delete()
        channel_sync.sync_channel_memberships_for_user(self.user.id)  # no raise
        self.assertEqual(ChannelMembershipSnapshot.objects.count(), 0)

    def test_api_errors_swallowed_keep_snapshot(self):
        with mock.patch.object(channel_sync.TelegramBotService, "_api_request",
                               side_effect=RuntimeError("net down")):
            channel_sync.sync_channel_memberships_for_user(self.user.id)  # no raise


class ChannelDisplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="member2", password="x")
        self.free = CommunityChannel.objects.create(
            platform="telegram", external_id="@free", name="Free Chat",
            invite_url="https://t.me/free")
        self.plan = Plan.objects.create(name="Pro", tier="pro",
                                        is_active=True, display_order=1)
        PlanChannelMapping.objects.create(
            plan=self.plan, platform="telegram",
            external_id="-1001", name="Premium Chat")
        ChannelMembershipSnapshot.objects.create(
            user=self.user, channel=self.free,
            is_member=True, checked_at="2026-09-22T00:00:00Z")

    def test_display_merges_free_and_paid(self):
        data = channel_sync.build_channel_display(self.user)
        self.assertEqual(len(data["free"]), 1)
        self.assertTrue(data["free"][0]["is_member"])
        self.assertEqual(data["free"][0]["invite_url"], "https://t.me/free")
        self.assertEqual(len(data["paid"]), 1)
        self.assertFalse(data["paid"][0]["entitled"])

    def test_entitled_when_active_subscription(self):
        Subscription.objects.create(
            user=self.user, plan=self.plan, status=Subscription.Status.ACTIVE,
            is_active=True, price_cents=1000, price_currency="USD")
        UserChannelAssignment.objects.create(
            user=self.user, platform="telegram", external_id="-1001")
        data = channel_sync.build_channel_display(self.user)
        self.assertTrue(data["paid"][0]["entitled"])
        self.assertTrue(data["paid"][0]["assigned"])



class ChannelMeshDisplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="meshdisplay", password="x")
        self.plan = Plan.objects.create(
            name="Mesh plan", tier="pro", is_active=True, display_order=1
        )
        Subscription.objects.create(
            user=self.user, plan=self.plan,
            status=Subscription.Status.ACTIVE, is_active=True,
            price_cents=1000, price_currency="USD",
        )
        self.mesh = ChannelMesh.objects.create(
            key="display-mesh", name="Forex Mesh",
            source_chat_id="-100901", is_active=True,
        )
        self.spawn = ChannelMeshDestination.objects.create(
            mesh=self.mesh, external_id="-100902",
            name="Forex Members A", is_active=True,
        )
        PlanMeshMapping.objects.create(
            plan=self.plan, mesh=self.mesh, is_active=True
        )

    def test_mesh_plan_display_shows_spawn_assignment_not_source(self):
        UserMeshAssignment.objects.create(
            user=self.user, mesh=self.mesh, destination=self.spawn,
            is_active=True,
        )

        data = channel_sync.build_channel_display(self.user)

        self.assertEqual(len(data["meshes"]), 1)
        self.assertEqual(data["meshes"][0]["name"], "Forex Mesh")
        self.assertEqual(data["meshes"][0]["plan_name"], "Mesh plan")
        self.assertTrue(data["meshes"][0]["assigned"])
        self.assertEqual(data["meshes"][0]["spawn_name"], "Forex Members A")
        self.assertNotIn(self.mesh.source_chat_id, str(data["meshes"]))

    def test_mesh_plan_display_shows_assignment_pending(self):
        data = channel_sync.build_channel_display(self.user)

        self.assertEqual(len(data["meshes"]), 1)
        self.assertFalse(data["meshes"][0]["assigned"])
        self.assertEqual(data["meshes"][0]["status"], "Spawn assignment pending")
