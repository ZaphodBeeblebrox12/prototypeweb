"""Signed allocator-to-Django API tests for Channel Mesh assignments."""

import json
import time
import uuid

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.bot_integration.models import (
    ChannelMesh, ChannelMeshDestination, PlanMeshMapping, TelegramAccount,
    UserMeshAssignment,
)
from apps.bot_integration.provision_auth import sign_payload
from apps.subscriptions.models import Plan, Subscription


@override_settings(PROVISION_SHARED_SECRET="mesh-test-secret")
class ChannelMeshAssignmentEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mesh-api-member", password="x")
        self.plan = Plan.objects.create(
            name="Mesh API plan", tier="basic", display_order=1
        )
        self.mesh = ChannelMesh.objects.create(
            key="mesh-api", name="API Mesh",
            source_chat_id="-100700", is_active=True,
        )
        self.spawn = ChannelMeshDestination.objects.create(
            mesh=self.mesh, external_id="-100701", name="API Spawn",
            is_active=True,
        )
        PlanMeshMapping.objects.create(plan=self.plan, mesh=self.mesh, is_active=True)
        Subscription.objects.create(
            user=self.user, plan=self.plan,
            status=Subscription.Status.ACTIVE, is_active=True,
        )
        self.telegram = TelegramAccount.objects.create(
            user=self.user, telegram_user_id=7654321,
            chat_id=7654321, is_active=True,
        )

    def signed_post(self, payload, secret="mesh-test-secret", url_name="mesh_assign"):
        body = json.dumps(payload, separators=(",", ":")).encode()
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        signature = sign_payload(secret, timestamp, nonce, body)
        return self.client.post(
            reverse(f"bot_integration:{url_name}"),
            data=body,
            content_type="application/json",
            HTTP_X_BOT_INSTANCE="existing-trading-bot",
            HTTP_X_BOT_TIMESTAMP=timestamp,
            HTTP_X_BOT_NONCE=nonce,
            HTTP_X_BOT_SIGNATURE=signature,
        )

    def test_signed_inventory_returns_only_active_meshes_and_spawns(self):
        ChannelMeshDestination.objects.create(
            mesh=self.mesh, external_id="-100702", name="Inactive Spawn",
            is_active=False,
        )
        inactive_mesh = ChannelMesh.objects.create(
            key="inactive-mesh", name="Inactive Mesh",
            source_chat_id="-100720", is_active=False,
        )
        ChannelMeshDestination.objects.create(
            mesh=inactive_mesh, external_id="-100721", name="Inactive Mesh Spawn",
            is_active=True,
        )

        response = self.signed_post({}, url_name="mesh_inventory")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(
            [item["mesh_key"] for item in response.json()["meshes"]],
            ["mesh-api"],
        )
        spawns = response.json()["meshes"][0]["spawns"]
        self.assertEqual([item["spawn_chat_id"] for item in spawns], ["-100701"])
        self.assertNotIn(self.mesh.source_chat_id, {
            item["spawn_chat_id"] for item in spawns
        })

    def test_signed_allocator_choice_is_saved_and_returns_assignment(self):
        response = self.signed_post({
            "telegram_user_id": 7654321,
            "mesh_key": "mesh-api",
            "spawn_chat_id": "-100701",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["assignment"]["spawn_chat_id"], "-100701")
        assignment = UserMeshAssignment.objects.get(user=self.user, mesh=self.mesh)
        self.assertEqual(assignment.destination_id, self.spawn.pk)
        self.assertTrue(assignment.is_active)

    def test_unsigned_request_is_rejected(self):
        response = self.client.post(
            reverse("bot_integration:mesh_assign"),
            data=json.dumps({
                "telegram_user_id": 7654321,
                "mesh_key": "mesh-api",
                "spawn_chat_id": "-100701",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(UserMeshAssignment.objects.exists())

    def test_allocator_cannot_assign_spawn_from_another_mesh(self):
        other_mesh = ChannelMesh.objects.create(
            key="other-mesh", name="Other Mesh",
            source_chat_id="-100710", is_active=True,
        )
        other_spawn = ChannelMeshDestination.objects.create(
            mesh=other_mesh, external_id="-100711", name="Other Spawn",
            is_active=True,
        )

        response = self.signed_post({
            "telegram_user_id": 7654321,
            "mesh_key": "mesh-api",
            "spawn_chat_id": other_spawn.external_id,
        })

        self.assertEqual(response.status_code, 404)
        self.assertFalse(UserMeshAssignment.objects.exists())

    def test_signed_request_requires_a_valid_entitlement(self):
        Subscription.objects.filter(user=self.user).update(
            status=Subscription.Status.EXPIRED, is_active=False
        )

        response = self.signed_post({
            "telegram_user_id": 7654321,
            "mesh_key": "mesh-api",
            "spawn_chat_id": "-100701",
        })

        self.assertEqual(response.status_code, 409)
        self.assertFalse(UserMeshAssignment.objects.exists())

    def test_bad_signature_is_rejected(self):
        response = self.signed_post({
            "telegram_user_id": 7654321,
            "mesh_key": "mesh-api",
            "spawn_chat_id": "-100701",
        }, secret="wrong-secret")

        self.assertEqual(response.status_code, 401)
        self.assertFalse(UserMeshAssignment.objects.exists())
