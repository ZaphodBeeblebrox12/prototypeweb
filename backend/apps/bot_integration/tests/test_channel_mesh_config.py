"""Tests for plan-level Channel Mesh configuration and access targets."""

from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.bot_integration.access import compute_target_access
from apps.bot_integration.models import (
    ChannelMesh, ChannelMeshDestination, PlanChannelMapping,
    PlanMeshMapping, TelegramAccount, UserChannelAssignment,
    UserMeshAssignment,
)
from apps.bot_integration.reconcile_jobs import run_user_reconcile
from apps.bot_integration.services.channel_mesh import assign_user_to_mesh_spawn
from apps.subscriptions.models import Plan, Subscription


class FakeMeshTransport:
    def __init__(self):
        self.grants = []
        self.revokes = []
        self.membership = {}

    def create_invite_link(self, telegram_user_id, channel_id, idempotency_key=None):
        self.grants.append((telegram_user_id, channel_id, idempotency_key))
        self.membership.setdefault(channel_id, True)
        return "https://t.me/+test-mesh"

    def send_invite_dm(self, telegram_user_id, channel_id, invite_link):
        return True

    def is_member(self, telegram_user_id, channel_id):
        return self.membership.get(channel_id, True)

    def revoke(self, telegram_user_id, channel_id, idempotency_key=None):
        self.revokes.append((telegram_user_id, channel_id, idempotency_key))
        self.membership[channel_id] = False
        return mock.Mock(ok=True, retryable=False)


class ChannelMeshAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mesh-member", password="x")
        self.plan = Plan.objects.create(
            name="Mesh course", tier="basic", display_order=1
        )
        self.mesh = ChannelMesh.objects.create(
            key="forex-mesh",
            name="Forex Mesh",
            source_chat_id="-100100",
            is_active=True,
        )
        self.spawn_one = ChannelMeshDestination.objects.create(
            mesh=self.mesh, external_id="-100201", name="Forex Spawn 1",
            chat_type=ChannelMeshDestination.CHAT_TYPE_CHANNEL, is_active=True,
        )
        self.spawn_two = ChannelMeshDestination.objects.create(
            mesh=self.mesh, external_id="-100202", name="Forex Spawn 2",
            chat_type=ChannelMeshDestination.CHAT_TYPE_CHANNEL, is_active=True,
        )
        self.direct = PlanChannelMapping.objects.create(
            plan=self.plan, platform="telegram",
            external_id="-100301", name="Direct course channel",
        )
        self.mesh_mapping = PlanMeshMapping.objects.create(
            plan=self.plan, mesh=self.mesh, is_active=True
        )
        self.subscription = Subscription.objects.create(
            user=self.user, plan=self.plan,
            status=Subscription.Status.ACTIVE, is_active=True,
        )
        self.telegram = TelegramAccount.objects.create(
            user=self.user, chat_id=555111, telegram_user_id=555111, is_active=True
        )

    def test_plan_can_combine_direct_and_mesh_without_granting_source_or_every_spawn(self):
        assign_user_to_mesh_spawn(self.user, self.mesh, self.spawn_one)

        target = compute_target_access(self.user.pk)

        self.assertEqual(target.telegram_ids, {"-100301", "-100201"})
        self.assertEqual(target.mesh_ids, {self.mesh.pk})
        self.assertNotIn(self.mesh.source_chat_id, target.telegram_ids)
        self.assertNotIn(self.spawn_two.external_id, target.telegram_ids)

    def test_mesh_plan_without_allocation_does_not_grant_all_spawns(self):
        target = compute_target_access(self.user.pk)

        self.assertEqual(target.telegram_ids, {"-100301"})
        self.assertNotIn(self.mesh.source_chat_id, target.telegram_ids)
        self.assertNotIn(self.spawn_one.external_id, target.telegram_ids)
        self.assertNotIn(self.spawn_two.external_id, target.telegram_ids)

    def test_assignment_service_requires_an_active_mesh_plan_entitlement(self):
        other_user = User.objects.create_user(username="no-mesh-entitlement", password="x")

        with self.assertRaises(ValidationError):
            assign_user_to_mesh_spawn(other_user, self.mesh, self.spawn_one)

    def test_assignment_service_rejects_spawn_from_another_mesh(self):
        other_mesh = ChannelMesh.objects.create(
            key="crypto-mesh", name="Crypto Mesh",
            source_chat_id="-100110", is_active=True,
        )
        other_spawn = ChannelMeshDestination.objects.create(
            mesh=other_mesh, external_id="-100210", name="Crypto Spawn",
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            assign_user_to_mesh_spawn(self.user, self.mesh, other_spawn)

    def test_reassignment_waits_until_previous_spawn_grant_is_revoked(self):
        assignment = assign_user_to_mesh_spawn(self.user, self.mesh, self.spawn_one)
        UserChannelAssignment.objects.create(
            user=self.user, platform="telegram",
            external_id=self.spawn_one.external_id, is_active=True,
        )

        with self.assertRaisesRegex(ValidationError, "Finish its revocation"):
            assign_user_to_mesh_spawn(self.user, self.mesh, self.spawn_two)

        assignment.refresh_from_db()
        self.assertEqual(assignment.destination_id, self.spawn_one.pk)

        UserChannelAssignment.objects.filter(
            user=self.user, platform="telegram",
            external_id=self.spawn_one.external_id,
        ).update(is_active=False)

        assignment = assign_user_to_mesh_spawn(self.user, self.mesh, self.spawn_two)
        self.assertEqual(assignment.destination_id, self.spawn_two.pk)

    def test_direct_and_mesh_access_use_existing_durable_provisioning_and_expiry(self):
        transport = FakeMeshTransport()
        assign_user_to_mesh_spawn(self.user, self.mesh, self.spawn_one)

        run_user_reconcile(self.user.pk, transport=transport)

        self.assertEqual(
            {channel_id for _, channel_id, _ in transport.grants},
            {"-100301", "-100201"},
        )
        self.assertTrue(UserChannelAssignment.objects.filter(
            user=self.user, platform="telegram",
            external_id="-100301", is_active=True,
        ).exists())
        self.assertTrue(UserChannelAssignment.objects.filter(
            user=self.user, platform="telegram",
            external_id="-100201", is_active=True,
        ).exists())

        self.subscription.status = Subscription.Status.EXPIRED
        self.subscription.is_active = False
        self.subscription.save()
        run_user_reconcile(self.user.pk, transport=transport)

        self.assertEqual(
            {channel_id for _, channel_id, _ in transport.revokes},
            {"-100301", "-100201"},
        )
        self.assertFalse(UserMeshAssignment.objects.get(
            user=self.user, mesh=self.mesh
        ).is_active)


class ChannelMeshConfigurationValidationTests(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name="Direct plan", tier="basic", display_order=1
        )
        self.mesh = ChannelMesh.objects.create(
            key="options-mesh", name="Options Mesh",
            source_chat_id="-100410", is_active=True,
        )
        self.spawn = ChannelMeshDestination.objects.create(
            mesh=self.mesh, external_id="-100411", name="Spawn",
            is_active=True,
        )

    def test_mesh_source_cannot_be_a_direct_membership_target(self):
        mapping = PlanChannelMapping(
            plan=self.plan, platform="telegram",
            external_id=self.mesh.source_chat_id,
        )
        with self.assertRaises(ValidationError):
            mapping.full_clean()

    def test_spawn_cannot_also_be_a_direct_membership_target(self):
        mapping = PlanChannelMapping(
            plan=self.plan, platform="telegram",
            external_id=self.spawn.external_id,
        )
        with self.assertRaises(ValidationError):
            mapping.full_clean()

    def test_existing_direct_channel_and_nonoverlapping_mesh_can_coexist(self):
        PlanChannelMapping.objects.create(
            plan=self.plan, platform="telegram", external_id="-100499"
        )
        mapping = PlanMeshMapping(
            plan=self.plan, mesh=self.mesh, is_active=True
        )
        mapping.full_clean()
        mapping.save()
        self.assertTrue(
            PlanMeshMapping.objects.filter(plan=self.plan, mesh=self.mesh).exists()
        )
