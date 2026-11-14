"""Authorization tests for user-administration APIs.

A Django is_staff flag alone must not grant powers to approve staff or
ban/unban users. Those operations belong to application admins/superusers.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


def _mk(username, **flags):
    user = User(username=username)
    for key, value in flags.items():
        setattr(user, key, value)
    user.set_password("pw")
    user.save()
    return user


class AdminBanAuthorizationTests(TestCase):
    def setUp(self):
        self.target = _mk("victim")
        self.client = APIClient()

    def _as(self, user):
        self.client.force_authenticate(user)

    def test_superuser_can_ban(self):
        self._as(_mk("root", is_superuser=True, is_staff=True))
        response = self.client.post(
            "/api/admin/ban/",
            {"user_id": str(self.target.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_banned)

    def test_role_admin_can_ban(self):
        self._as(_mk("roleadmin", role=User.Role.ADMIN))
        response = self.client.post(
            "/api/admin/ban/",
            {"user_id": str(self.target.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_banned)

    def test_plain_user_cannot_ban(self):
        self._as(_mk("plainuser"))
        response = self.client.post(
            "/api/admin/ban/",
            {"user_id": str(self.target.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_banned)

    def test_ordinary_django_staff_cannot_ban(self):
        self._as(_mk("ordinary-staff", is_staff=True))
        response = self.client.post(
            "/api/admin/ban/",
            {"user_id": str(self.target.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_banned)

    def test_ordinary_django_staff_cannot_unban(self):
        self.target.is_banned = True
        self.target.save(update_fields=["is_banned"])
        self._as(_mk("ordinary-staff-unban", is_staff=True))
        response = self.client.post(
            "/api/admin/unban/",
            {"user_id": str(self.target.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_banned)

    def test_ordinary_django_staff_cannot_list_staff_approvals(self):
        self._as(_mk("ordinary-staff-list", is_staff=True))
        response = self.client.get("/api/admin/staff-approvals/")
        self.assertEqual(response.status_code, 403)

    def test_ordinary_django_staff_cannot_approve_staff(self):
        self._as(_mk("ordinary-staff-approve", is_staff=True))
        response = self.client.post(
            "/api/admin/staff-approvals/action/",
            {"user_id": str(self.target.id), "action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.target.refresh_from_db()
        self.assertEqual(self.target.role, User.Role.USER)
        self.assertFalse(self.target.is_staff)
        self.assertFalse(self.target.is_staff_approved)

    def test_role_admin_can_list_and_approve_staff(self):
        admin = _mk("roleadmin-approve", role=User.Role.ADMIN)
        self._as(admin)
        list_response = self.client.get("/api/admin/staff-approvals/")
        self.assertEqual(list_response.status_code, 200)

        response = self.client.post(
            "/api/admin/staff-approvals/action/",
            {"user_id": str(self.target.id), "action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertEqual(self.target.role, User.Role.STAFF)
        self.assertTrue(self.target.is_staff)
        self.assertTrue(self.target.is_staff_approved)
