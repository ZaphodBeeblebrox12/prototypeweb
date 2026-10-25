"""
Tests for ban system.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditLog

User = get_user_model()


@pytest.mark.django_db
class TestBanAPI:
    """Test ban API endpoints."""

    def test_ban_user(self, admin_user, user_factory):
        """Test banning a user."""
        target_user = user_factory()
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.post(
            "/api/admin/ban/",
            {
                "user_id": str(target_user.id),
                "reason": "Violation of terms",
            },
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "banned"

        # Verify user was banned
        target_user.refresh_from_db()
        assert target_user.is_banned is True
        assert target_user.ban_reason == "Violation of terms"
        assert target_user.banned_at is not None

        # Verify audit log
        assert AuditLog.objects.filter(
            action="user_banned",
            object_id=str(target_user.id)
        ).exists()

    def test_ban_user_no_reason(self, admin_user, user_factory):
        """Test banning a user without reason."""
        target_user = user_factory()
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.post(
            "/api/admin/ban/",
            {
                "user_id": str(target_user.id),
            },
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK

        target_user.refresh_from_db()
        assert target_user.is_banned is True
        assert target_user.ban_reason == ""

    def test_cannot_ban_admin(self, admin_user, user_factory):
        """Test that admins cannot be banned."""
        another_admin = user_factory(
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.post(
            "/api/admin/ban/",
            {
                "user_id": str(another_admin.id),
                "reason": "Test",
            },
            format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot ban admin users" in response.json()["error"]

    def test_unban_user(self, admin_user, user_factory):
        """Test unbanning a user."""
        target_user = user_factory()
        target_user.ban("Test reason")

        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.post(
            "/api/admin/unban/",
            {
                "user_id": str(target_user.id),
            },
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "unbanned"

        # Verify user was unbanned
        target_user.refresh_from_db()
        assert target_user.is_banned is False
        assert target_user.ban_reason == ""
        assert target_user.banned_at is None

        # Verify audit log
        assert AuditLog.objects.filter(
            action="user_unbanned",
            object_id=str(target_user.id)
        ).exists()

    def test_ban_non_admin_forbidden(self, user_factory):
        """Test that non-admins cannot ban users."""
        regular_user = user_factory()
        target_user = user_factory(telegram_id=999999)

        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.post(
            "/api/admin/ban/",
            {
                "user_id": str(target_user.id),
                "reason": "Test",
            },
            format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBanEnforcement:
    """Test ban enforcement."""

    def test_banned_user_cannot_subscribe(self, banned_user):
        """Test that banned users cannot subscribe."""
        assert banned_user.can_subscribe() is False

    def test_active_user_can_subscribe(self, user_factory):
        """Test that active users can subscribe."""
        user = user_factory()
        assert user.can_subscribe() is True

    def test_inactive_user_cannot_subscribe(self, user_factory):
        """Test that inactive users cannot subscribe."""
        user = user_factory()
        user.is_active = False
        user.save()

        assert user.can_subscribe() is False

    def test_ban_method(self, user_factory):
        """Test the ban method."""
        user = user_factory()

        user.ban("Test reason")

        assert user.is_banned is True
        assert user.ban_reason == "Test reason"
        assert user.banned_at is not None

    def test_unban_method(self, user_factory):
        """Test the unban method."""
        user = user_factory()
        user.ban("Test reason")

        user.unban()

        assert user.is_banned is False
        assert user.ban_reason == ""
        assert user.banned_at is None
