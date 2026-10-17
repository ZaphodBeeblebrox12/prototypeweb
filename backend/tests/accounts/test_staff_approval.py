"""
Tests for staff approval workflow.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditLog

User = get_user_model()


@pytest.mark.django_db
class TestStaffApprovalAPI:
    """Test staff approval API endpoints."""

    def test_list_pending_approvals(self, admin_user, staff_user):
        """Test listing pending staff approvals."""
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.get("/api/admin/staff-approvals/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(staff_user.id)
        assert data[0]["telegram_username"] == staff_user.telegram_username

    def test_list_pending_approvals_non_admin(self, user_factory):
        """Test that non-admins cannot list approvals."""
        regular_user = user_factory()
        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.get("/api/admin/staff-approvals/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_approve_staff_user(self, admin_user, staff_user):
        """Test approving a staff user."""
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.post(
            "/api/admin/staff-approvals/action/",
            {
                "user_id": str(staff_user.id),
                "action": "approve",
            },
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "approved"

        # Verify user was updated
        staff_user.refresh_from_db()
        assert staff_user.is_staff_approved is True
        assert staff_user.is_staff is True

        # Verify audit log
        assert AuditLog.objects.filter(
            action="staff_approved",
            object_id=str(staff_user.id)
        ).exists()

    def test_reject_staff_user(self, admin_user, staff_user):
        """Test rejecting a staff user."""
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.post(
            "/api/admin/staff-approvals/action/",
            {
                "user_id": str(staff_user.id),
                "action": "reject",
            },
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "rejected"

        # Verify user was demoted
        staff_user.refresh_from_db()
        assert staff_user.role == User.Role.USER

        # Verify audit log
        assert AuditLog.objects.filter(
            action="staff_rejected",
            object_id=str(staff_user.id)
        ).exists()

    def test_approve_nonexistent_user(self, admin_user):
        """Test approving a non-existent user."""
        client = APIClient()
        client.force_authenticate(user=admin_user)

        import uuid
        response = client.post(
            "/api/admin/staff-approvals/action/",
            {
                "user_id": str(uuid.uuid4()),
                "action": "approve",
            },
            format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestStaffRoleBehavior:
    """Test staff role behavior."""

    def test_new_staff_requires_approval(self, user_factory):
        """Test that new staff users require approval."""
        user = user_factory(role=User.Role.STAFF)

        assert user.role == User.Role.STAFF
        assert user.is_staff_approved is False
        assert user.is_staff is False

    def test_approved_staff_has_permissions(self, staff_user):
        """Test that approved staff has staff permissions."""
        staff_user.approve_staff()

        assert staff_user.is_staff_approved is True
        assert staff_user.is_staff is True
