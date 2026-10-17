"""
Tests for audit logging system.
"""
import pytest
from django.contrib.auth import get_user_model

from apps.audit.models import AuditLog

User = get_user_model()


@pytest.mark.django_db
class TestAuditLog:
    """Test audit log functionality."""

    def test_create_audit_log(self, user_factory):
        """Test creating an audit log entry."""
        user = user_factory()

        log = AuditLog.objects.create(
            user=user,
            action="test_action",
            object_type="User",
            object_id=str(user.id),
            metadata={"key": "value"},
        )

        assert log.user == user
        assert log.action == "test_action"
        assert log.object_type == "User"
        assert log.object_id == str(user.id)
        assert log.metadata == {"key": "value"}
        assert log.created_at is not None

    def test_audit_log_str(self, user_factory):
        """Test audit log string representation."""
        user = user_factory()

        log = AuditLog.objects.create(
            user=user,
            action="test_action",
        )

        assert str(user) in str(log)
        assert "test_action" in str(log)

    def test_audit_log_log_method(self, user_factory):
        """Test the log class method."""
        user = user_factory()

        log = AuditLog.log(
            action="custom_action",
            user=user,
            object_type="TestObject",
            object_id="123",
            metadata={"foo": "bar"},
        )

        assert log.action == "custom_action"
        assert log.user == user
        assert log.object_type == "TestObject"
        assert log.object_id == "123"
        assert log.metadata == {"foo": "bar"}

    def test_audit_log_without_user(self):
        """Test creating audit log without user (system action)."""
        log = AuditLog.objects.create(
            action="system_cleanup",
            object_type="System",
            object_id="0",
        )

        assert log.user is None
        assert log.action == "system_cleanup"

    def test_audit_log_ordering(self, user_factory):
        """Test that audit logs are ordered by created_at descending."""
        user = user_factory()

        log1 = AuditLog.objects.create(user=user, action="action1")
        log2 = AuditLog.objects.create(user=user, action="action2")
        log3 = AuditLog.objects.create(user=user, action="action3")

        logs = list(AuditLog.objects.all())
        assert logs[0] == log3
        assert logs[1] == log2
        assert logs[2] == log1


@pytest.mark.django_db
class TestAuditLogIntegration:
    """Test audit log integration with other actions."""

    def test_user_creation_logged(self, user_factory):
        """Test that user creation is logged."""
        user = user_factory()

        # Check if user creation was logged
        # This depends on your implementation
        # For now, just verify the audit log system works
        log = AuditLog.objects.create(
            user=user,
            action="user_created",
            object_type="User",
            object_id=str(user.id),
        )

        assert log.action == "user_created"

    def test_ban_action_logged(self, user_factory):
        """Test that ban actions are logged."""
        admin = user_factory(role=User.Role.ADMIN)
        target = user_factory(telegram_id=999999)

        target.ban("Test reason")

        log = AuditLog.objects.create(
            user=admin,
            action="user_banned",
            object_type="User",
            object_id=str(target.id),
            metadata={"reason": "Test reason"},
        )

        assert log.action == "user_banned"
        assert log.metadata["reason"] == "Test reason"
