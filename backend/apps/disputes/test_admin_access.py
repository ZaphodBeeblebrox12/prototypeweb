"""Domain-permission tests for the dispute dashboard and actions."""

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from apps.disputes.models import Dispute

User = get_user_model()


def make_staff(username, role=None):
    user = User.objects.create_user(username=username, password="pw")
    user.is_staff = True
    if role is not None:
        user.role = role
    user.save(update_fields=["is_staff", "role"])
    return user


def grant(user, *codenames):
    content_type = ContentType.objects.get_for_model(Dispute)
    permissions = list(
        Permission.objects.filter(
            content_type=content_type,
            codename__in=codenames,
        )
    )
    assert {permission.codename for permission in permissions} == set(codenames)
    user.user_permissions.add(*permissions)


class DisputeAccessTests(TestCase):
    def test_generic_staff_without_view_permission_is_denied(self):
        staff = make_staff("dispute-no-permission")
        self.client.force_login(staff)

        response = self.client.get("/admin-disputes/")

        self.assertEqual(response.status_code, 403)

    def test_staff_with_view_permission_can_open_dashboard(self):
        staff = make_staff("dispute-viewer")
        grant(staff, "view_dispute")
        self.client.force_login(staff)

        response = self.client.get("/admin-disputes/")

        self.assertEqual(response.status_code, 200)

    def test_view_permission_is_enforced_on_detail_routes(self):
        staff = make_staff("dispute-detail-viewer")
        self.client.force_login(staff)

        denied = self.client.get(f"/admin-disputes/{uuid4()}/")
        self.assertEqual(denied.status_code, 403)

        grant(staff, "view_dispute")
        allowed_to_resolve = self.client.get(f"/admin-disputes/{uuid4()}/")
        self.assertEqual(allowed_to_resolve.status_code, 404)

    def test_view_only_staff_cannot_post_dispute_actions(self):
        staff = make_staff("dispute-view-only")
        grant(staff, "view_dispute")
        self.client.force_login(staff)

        response = self.client.post(
            f"/admin-disputes/{uuid4()}/note/",
            {"note": "test note"},
        )

        self.assertEqual(response.status_code, 403)

    def test_change_without_view_is_not_enough_for_dispute_actions(self):
        staff = make_staff("dispute-change-only")
        grant(staff, "change_dispute")
        self.client.force_login(staff)

        response = self.client.post(
            f"/admin-disputes/{uuid4()}/note/",
            {"note": "test note"},
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_with_view_and_change_reaches_object_lookup(self):
        staff = make_staff("dispute-reviewer")
        grant(staff, "view_dispute", "change_dispute")
        self.client.force_login(staff)

        response = self.client.post(
            f"/admin-disputes/{uuid4()}/note/",
            {"note": "test note"},
        )

        self.assertEqual(response.status_code, 404)

    def test_application_admin_can_open_dashboard(self):
        admin = make_staff("dispute-admin", role=User.Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.get("/admin-disputes/")

        self.assertEqual(response.status_code, 200)
