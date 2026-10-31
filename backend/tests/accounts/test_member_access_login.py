"""End-to-end tests for sign-in from the public member-access room."""
from allauth.account.models import EmailAddress
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User


PUBLIC_ORIGIN = "https://tradethesis-public-staging.onrender.com"
GITHUB_PAGES_ORIGIN = "https://zaphodbeeblebrox12.github.io"
GITHUB_PAGES_MEMBER_ACCESS = f"{GITHUB_PAGES_ORIGIN}/prototypeweb/member-access.html"
LOGIN_PASSWORD = "A-strong-test-password-852!"


@override_settings(
    TRADETHESIS_PUBLIC_SITE_URL=PUBLIC_ORIGIN,
    TRADETHESIS_MEMBER_LOGIN_ORIGINS=[PUBLIC_ORIGIN, GITHUB_PAGES_ORIGIN],
)
class MemberAccessLoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="member_room_login",
            email="member-room-login@example.com",
        )
        self.user.set_password(LOGIN_PASSWORD)
        self.user.save()
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True,
        )

    def test_valid_login_goes_straight_to_member_dashboard(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": LOGIN_PASSWORD, "remember": "on"},
            HTTP_ORIGIN=PUBLIC_ORIGIN,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))
        self.assertTrue(self.client.session.get("_auth_user_id"))

        dashboard = self.client.get(reverse("dashboard"))
        self.assertEqual(dashboard.status_code, 200)

    def test_invalid_credentials_return_to_the_same_member_room(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": "not-the-password"},
            HTTP_ORIGIN=PUBLIC_ORIGIN,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"{PUBLIC_ORIGIN}/member-access.html?login=invalid",
        )
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_invalid_credentials_from_github_pages_return_to_the_project_member_room(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": "not-the-password"},
            HTTP_ORIGIN=GITHUB_PAGES_ORIGIN,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{GITHUB_PAGES_MEMBER_ACCESS}?login=invalid")
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_unapproved_origin_is_rejected(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": LOGIN_PASSWORD},
            HTTP_ORIGIN="https://example-attacker.invalid",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_missing_origin_is_rejected(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": LOGIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_endpoint_only_accepts_post(self):
        response = self.client.get(reverse("member_access_login"))
        self.assertEqual(response.status_code, 405)


@override_settings(
    TRADETHESIS_PUBLIC_SITE_URL=PUBLIC_ORIGIN,
    TRADETHESIS_MEMBER_LOGIN_ORIGINS=[PUBLIC_ORIGIN, GITHUB_PAGES_ORIGIN],
)
class MemberEntryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="member_entry_test",
            email="member-entry@example.com",
            password=LOGIN_PASSWORD,
        )

    def test_authenticated_member_goes_directly_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("member_entry"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_anonymous_member_returns_to_the_same_access_room(self):
        response = self.client.get(reverse("member_entry"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"{PUBLIC_ORIGIN}/member-access.html",
        )
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_anonymous_member_returns_to_github_pages_project_path_from_referer(self):
        response = self.client.get(
            reverse("member_entry"),
            HTTP_REFERER=f"{GITHUB_PAGES_ORIGIN}/prototypeweb/index.html",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], GITHUB_PAGES_MEMBER_ACCESS)
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_untrusted_member_entry_referer_falls_back_to_configured_public_site(self):
        response = self.client.get(
            reverse("member_entry"),
            HTTP_REFERER="https://attacker.invalid/prototypeweb/index.html",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{PUBLIC_ORIGIN}/member-access.html")
