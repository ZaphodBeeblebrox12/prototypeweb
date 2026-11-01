"""Django Admin must collect and persist names for newly created members."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AdminUserCreationNamesTests(TestCase):
    def setUp(self):
        admin_user = User.objects.create_superuser(
            username="names-admin",
            email="names-admin@example.com",
            password="7!Qv#9mL2$pR8xZ4@tW",
        )
        self.client.force_login(admin_user)
        self.add_url = reverse("admin:accounts_user_add")

    def test_add_user_form_includes_email_and_both_name_fields(self):
        response = self.client.get(self.add_url)

        self.assertEqual(response.status_code, 200)
        for field in ("email", "first_name", "last_name", "password1", "password2"):
            self.assertContains(response, f'name="{field}"')

    def test_admin_creation_persists_first_and_last_name(self):
        response = self.client.post(
            self.add_url,
            {
                "username": "nisha-kapoor",
                "email": "nisha.kapoor@example.com",
                "first_name": "Nisha",
                "last_name": "Kapoor",
                "nickname": "Nisha",
                "password1": "4#nV8!xB2$qL6@rT9p",
                "password2": "4#nV8!xB2$qL6@rT9p",
            },
        )

        self.assertEqual(response.status_code, 302, response.content.decode()[:2000])
        user = User.objects.get(username="nisha-kapoor")
        self.assertEqual(user.email, "nisha.kapoor@example.com")
        self.assertEqual(user.first_name, "Nisha")
        self.assertEqual(user.last_name, "Kapoor")
        self.assertEqual(user.full_name, "Nisha Kapoor")

    def test_admin_creation_rejects_missing_first_or_last_name(self):
        response = self.client.post(
            self.add_url,
            {
                "username": "incomplete-member",
                "email": "incomplete@example.com",
                "first_name": "",
                "last_name": "Member",
                "password1": "4#nV8!xB2$qL6@rT9p",
                "password2": "4#nV8!xB2$qL6@rT9p",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="incomplete-member").exists())
        self.assertContains(response, "This field is required.")
