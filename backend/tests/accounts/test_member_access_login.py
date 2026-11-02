"""Regression tests for the single canonical TradeThesis authentication journey."""
from allauth.account.models import EmailAddress
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User


PUBLIC_ORIGIN = "https://tradethesis-public-staging.onrender.com"
GITHUB_PAGES_ORIGIN = "https://zaphodbeeblebrox12.github.io"
LOGIN_PASSWORD = "A-strong-test-password-852!"


@override_settings(
    TRADETHESIS_MEMBER_LOGIN_ORIGINS=[PUBLIC_ORIGIN, GITHUB_PAGES_ORIGIN],
)
class LegacyMemberAccessLoginTests(TestCase):
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

    def test_legacy_post_discards_credentials_and_redirects_to_canonical_login(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": LOGIN_PASSWORD, "remember": "on"},
            HTTP_ORIGIN=PUBLIC_ORIGIN,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response["Location"],
            f"{reverse('account_login')}?next=%2Fdashboard%2F",
        )
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_legacy_post_does_not_authenticate_even_with_valid_credentials(self):
        response = self.client.post(
            reverse("member_access_login"),
            {"login": self.user.email, "password": LOGIN_PASSWORD},
            HTTP_ORIGIN=GITHUB_PAGES_ORIGIN,
        )

        self.assertEqual(response.status_code, 303)
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

    def test_legacy_endpoint_only_accepts_post(self):
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
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, primary=True, verified=True
        )

    def test_authenticated_member_goes_directly_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("member_entry"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_anonymous_member_goes_to_the_canonical_django_login(self):
        response = self.client.get(reverse("member_entry"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"{reverse('account_login')}?next=%2Fdashboard%2F",
        )
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_member_entry_does_not_send_visitors_to_a_referer_selected_host(self):
        response = self.client.get(
            reverse("member_entry"),
            HTTP_REFERER="https://attacker.invalid/prototypeweb/index.html",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"{reverse('account_login')}?next=%2Fdashboard%2F",
        )
        self.assertEqual(response["Cache-Control"], "no-store")
