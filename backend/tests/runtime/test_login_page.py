"""Regression coverage for the canonical, mobile-first authentication pages."""
from pathlib import Path
from types import SimpleNamespace

from allauth.socialaccount.models import SocialApp
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse


class LoginPageTests(TestCase):
    def test_login_page_renders_without_a_configured_social_provider(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back.")
        self.assertContains(response, 'name="login"')
        self.assertContains(response, 'name="password"')

    def test_mobile_login_hides_the_desktop_story_and_prioritizes_the_form(self):
        response = self.client.get(reverse("account_login"))
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("@media (max-width: 820px)", html)
        self.assertIn(".story { display: none; }", html)
        self.assertIn("min-height: 50px", html)
        self.assertIn("font-size: 16px", html)

    def test_login_keeps_the_requested_destination_on_signup_and_password_reset(self):
        response = self.client.get(
            f"{reverse('account_login')}?next=%2Flearn%2Ftrading-path%2F"
        )
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="next" value="/learn/trading-path/"', html)
        self.assertIn(
            'href="/accounts/signup/?next=%2Flearn%2Ftrading-path%2F"',
            html,
        )
        self.assertIn(
            'href="/accounts/password/reset/?next=%2Flearn%2Ftrading-path%2F"',
            html,
        )

    def test_login_uses_the_shared_trade_thesis_auth_shell(self):
        response = self.client.get(reverse("account_login"))
        self.assertContains(response, "TradeThesis Academy")
        self.assertContains(response, "sitewide-nav.css")


class SignupPageTests(TestCase):
    def test_signup_collects_first_and_last_name(self):
        response = self.client.get(reverse("account_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertContains(response, 'autocomplete="given-name"')
        self.assertContains(response, 'autocomplete="family-name"')

    def test_signup_offers_google_when_the_provider_is_configured(self):
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test-google-client-id",
            secret="test-google-secret",
        )
        site = Site.objects.get_or_create(
            id=1,
            defaults={"domain": "example.com", "name": "example.com"},
        )[0]
        app.sites.add(site)

        response = self.client.get(reverse("account_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continue with Google")


class EmailJourneyTemplateTests(TestCase):
    def test_verification_sent_uses_the_trade_thesis_auth_shell(self):
        response = self.client.get(reverse("account_email_verification_sent"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/verification_sent.html")
        self.assertContains(response, "Check your inbox.")
        self.assertContains(response, "TradeThesis Academy")

    def test_email_confirmation_form_preserves_the_next_query_on_post(self):
        request = RequestFactory().get(
            "/accounts/confirm-email/test-confirmation-key/"
            "?next=%2Flearn%2Ftrading-path%2F"
        )
        request.user = AnonymousUser()
        confirmation = SimpleNamespace(
            email_address=SimpleNamespace(email="learner@example.com")
        )

        html = render_to_string(
            "account/email_confirm.html",
            {"confirmation": confirmation, "request": request},
            request=request,
        )

        self.assertIn(
            'action="/accounts/confirm-email/test-confirmation-key/?next=%2Flearn%2Ftrading-path%2F"',
            html,
        )

    def test_public_member_access_page_does_not_collect_credentials(self):
        repository_root = Path(__file__).resolve().parents[3]
        page = (repository_root / "site" / "member-access.html").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("<form", page.lower())
        self.assertNotIn('type="password"', page.lower())
        self.assertNotIn('name="password"', page.lower())
        self.assertIn('data-academy-path="/accounts/member-entry/"', page)
