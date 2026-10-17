"""Regression: /accounts/login/ must not 500 when an optional social provider
has no SocialApp configured (allauth get_providers is empty -> block skipped).

Root cause: login.html hard-rendered {% provider_login_url 'google' %}, which
raises SocialApp.DoesNotExist when unconfigured, crashing the whole page.
Fix: wrap the block in {% get_providers %} ... {% if 'google' in ... %}.
"""
import pytest
from django.test import TestCase


class LoginPageSocialProviderTest(TestCase):
    def test_login_page_200_without_socialapp(self):
        """No SocialApp configured -> page must still render (no 500)."""
        r = self.client.get("/accounts/login/")
        assert r.status_code == 200
        html = r.content.decode()
        assert (
            'href="https://tradethesis-public-staging.onrender.com/" '
            'class="brand-logo"' in html
        )
        assert 'href="/" class="brand-logo"' not in html
        assert "{% endfor %}" not in html

    def test_login_page_200_with_google_socialapp(self):
        """A configured SocialApp -> page renders and Google button present."""
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        app = SocialApp.objects.create(
            provider="google", name="Google",
            client_id="test-google-client-id", secret="test-google-secret")
        site = Site.objects.get_or_create(
            id=1, defaults={"domain": "example.com", "name": "example.com"})[0]
        app.sites.add(site)
        r = self.client.get("/accounts/login/")
        assert r.status_code == 200
        assert "google" in r.content.decode().lower()


    def test_login_and_signup_share_one_branded_access_screen(self):
        login = self.client.get("/accounts/login/?next=/learn/")
        signup = self.client.get("/accounts/signup/?next=/learn/")

        assert login.status_code == 200
        assert signup.status_code == 200
        login_html = login.content.decode()
        signup_html = signup.content.decode()
        assert 'data-auth-mode="login"' in login_html
        assert 'data-auth-mode="signup"' in signup_html
        assert "Your place to learn, connect and" in login_html
        assert "Your place to learn, connect and" in signup_html
        assert 'name="login"' in login_html
        assert 'name="password1"' in signup_html
        assert 'name="password2"' in signup_html

    def test_django_root_redirects_to_public_tradethesis_site(self):
        from django.conf import settings

        response = self.client.get("/")
        assert response.status_code == 302
        assert response["Location"] == f"{settings.PUBLIC_SITE_URL}/"

        health = self.client.get("/health/")
        assert health.status_code == 200
        assert health.content.decode() == "ok"
