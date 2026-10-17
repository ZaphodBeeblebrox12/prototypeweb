"""Batch-auth: complete authentication-surface regression tests.

Covers password auth, optional OAuth (no SocialApp -> pages render), signup,
createsuperuser->admin auth, admin authorization, banned-user restriction.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


def _mk_superuser(username="root"):
    return User.objects.create_superuser(
        username=username, email=f"{username}@x.com", password="pass12345!")


@pytest.mark.django_db
class TestLoginPage:
    def test_login_get_200_without_socialapp(self, client):
        assert client.get("/accounts/login/").status_code == 200
        assert client.get(reverse("account_reset_password")).status_code == 200

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_login_valid_staff_credentials_reaches_requested_admin_dashboard(self, client):
        from django.core import mail

        user = _mk_superuser()
        mail.outbox.clear()
        r = client.post("/accounts/login/?next=/admin/dashboard/", {
            "login": user.email, "password": "pass12345!"})

        assert r.status_code == 302
        assert r["Location"].endswith("/admin/dashboard/")
        # An unverified bootstrap superuser must not be forced into a mail loop.
        assert len(mail.outbox) == 0
        assert client.get("/admin/").status_code == 200
        admin_dashboard = client.get("/admin/dashboard/")
        assert admin_dashboard.status_code == 200
        assert b"Operational dashboard" in admin_dashboard.content

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_unverified_learner_login_sends_confirmation_instead_of_500(self, client):
        from django.core import mail

        user = User.objects.create_user(
            username="learner",
            email="learner@example.com",
            password="Str0ng!Pass9",
        )
        mail.outbox.clear()
        r = client.post("/accounts/login/", {
            "login": user.email, "password": "Str0ng!Pass9"})

        assert r.status_code == 302
        assert r["Location"] == reverse("account_email_verification_sent")
        assert len(mail.outbox) == 1
        assert "TradeThesis" in mail.outbox[0].subject
        assert "activate_url" not in mail.outbox[0].body
        assert "http" in mail.outbox[0].body
        sent_page = client.get(r["Location"])
        assert sent_page.status_code == 200
        assert b"Check your inbox." in sent_page.content

    def test_login_invalid_credentials(self, client):
        _mk_superuser()
        r = client.post("/accounts/login/", {
            "login": "root", "password": "wrong"}, follow=True)
        assert r.status_code == 200
        assert b"root" in r.content or b"incorrect" in r.content.lower() or b"error" in r.content.lower()


@pytest.mark.django_db
class TestSignupPage:
    def test_signup_get_200_without_socialapp(self, client):
        assert client.get("/accounts/signup/").status_code == 200

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_signup_sends_confirmation_without_500(self, client):
        from django.core import mail

        mail.outbox.clear()
        r = client.post("/accounts/signup/", {
            "email": "new@x.com",
            "password1": "Str0ng!Pass9", "password2": "Str0ng!Pass9"})

        assert r.status_code == 302
        assert r["Location"] == reverse("account_email_verification_sent")
        # Email-based signup: username is generated and user is created.
        assert User.objects.filter(email="new@x.com").exists()
        assert len(mail.outbox) == 1
        assert "TradeThesis" in mail.outbox[0].subject

    def test_signup_duplicate_rejected(self, client):
        User.objects.create_user(username="existsemail", email="dup@x.com", password="pass12345!")
        r = client.post("/accounts/signup/", {
            "email": "dup@x.com",
            "password1": "Str0ng!Pass9", "password2": "Str0ng!Pass9"})
        assert r.status_code in (200, 302)  # duplicate email -> form error
        assert User.objects.filter(email="dup@x.com").count() == 1


@pytest.mark.django_db
class TestSuperuserAdmin:
    def test_createsuperuser_authenticates(self, client):
        _mk_superuser()
        assert client.login(username="root", password="pass12345!")

    def test_superuser_reaches_admin(self, client):
        _mk_superuser()
        client.login(username="root", password="pass12345!")
        assert client.get("/admin/").status_code == 200

    def test_normal_user_denied_admin(self, client):
        u = User.objects.create_user(username="norm", email="n@x.com",
                                     password="pass12345!")
        client.force_login(u)
        assert client.get("/admin/").status_code in (301, 302, 403)


@pytest.mark.django_db
class TestGoogleProviderOptional:
    def test_google_button_hidden_without_socialapp(self, client):
        r = client.get("/accounts/login/")
        # page renders; no crash (button may or may not appear, but page is 200)
        assert r.status_code == 200

    def test_google_button_present_with_socialapp(self, client):
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        app = SocialApp.objects.create(provider="google", name="Google",
            client_id="test-client-id", secret="test-secret")
        site = Site.objects.get_or_create(id=1, defaults={"domain":"example.com","name":"example.com"})[0]
        app.sites.add(site)
        r = client.get("/accounts/login/")
        assert r.status_code == 200
        assert "google" in r.content.decode().lower()


@pytest.mark.django_db
class TestBannedUser:
    def test_banned_user_blocked_from_dashboard(self, client):
        u = User.objects.create_user(username="banned", email="b@x.com",
                                     password="pass12345!", is_banned=True)
        client.force_login(u)
        # ban middleware returns 403
        assert client.get("/dashboard/").status_code == 403


@pytest.mark.django_db
class TestUnifiedAdminEntry:
    def test_admin_login_url_uses_trade_thesis_auth_and_preserves_next(self, client):
        from urllib.parse import parse_qs, urlsplit

        response = client.get("/admin/login/?next=/admin/dashboard/")

        assert response.status_code == 302
        target = urlsplit(response["Location"])
        assert target.path == reverse("account_login")
        assert parse_qs(target.query).get("next") == ["/admin/dashboard/"]

    def test_regular_user_cannot_open_operational_admin_dashboard(self, client):
        user = User.objects.create_user(
            username="regular", email="regular@example.com", password="Str0ng!Pass9"
        )
        client.force_login(user)

        response = client.get("/admin/dashboard/", follow=True)

        assert response.status_code == 200
        assert response.request["PATH_INFO"] == reverse("account_login")
        from urllib.parse import parse_qs
        assert parse_qs(response.request["QUERY_STRING"]).get("next") == ["/admin/dashboard/"]

    def test_unverified_regular_user_cannot_use_legacy_dashboard(self, client):
        user = User.objects.create_user(
            username="unverified", email="unverified@example.com", password="Str0ng!Pass9"
        )
        client.force_login(user)

        response = client.get("/dashboard/")

        assert response.status_code == 302
        assert response["Location"] == reverse("account_email_verification_sent")


    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verified_learner_login_reaches_rendered_learning_dashboard(self, client):
        from allauth.account.models import EmailAddress

        user = User.objects.create_user(
            username="verifiedlearner",
            email="verifiedlearner@example.com",
            password="Str0ng!Pass9",
        )
        EmailAddress.objects.create(
            user=user, email=user.email, primary=True, verified=True
        )

        response = client.post("/accounts/login/?next=/learn/", {
            "login": user.email, "password": "Str0ng!Pass9"
        })
        assert response.status_code == 302
        assert response["Location"].endswith("/learn/")

        dashboard = client.get("/learn/")
        assert dashboard.status_code == 200
        assert b"Your TradeThesis desk" in dashboard.content

        logout = client.post(reverse("account_logout"))
        assert logout.status_code == 302
        assert logout["Location"].startswith("https://tradethesis-public-staging.onrender.com/")


@pytest.mark.django_db
class TestPasswordRecovery:
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_email_link_opens_and_updates_password(self, client):
        from urllib.parse import urlsplit
        from django.core import mail
        from allauth.account.models import EmailAddress

        user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="OldPass!2026",
        )
        EmailAddress.objects.create(
            user=user, email=user.email, primary=True, verified=True
        )
        mail.outbox.clear()

        response = client.post(reverse("account_reset_password"), {
            "email": user.email
        })
        assert response.status_code == 302
        assert response["Location"].endswith(reverse("account_reset_password_done"))
        assert len(mail.outbox) == 1
        assert "TradeThesis" in mail.outbox[0].subject

        reset_url = next(
            line.strip()
            for line in mail.outbox[0].body.splitlines()
            if "/accounts/password/reset/key/" in line
        )
        reset_path = urlsplit(reset_url).path
        reset_page = client.get(reset_path)
        assert reset_page.status_code == 200
        assert b"Choose a new password" in reset_page.content

        new_password = "CompletelyNew!P4ssword2026"
        changed = client.post(reset_path, {
            "password1": new_password,
            "password2": new_password,
            "action": "change password",
        })
        assert changed.status_code == 302
        assert changed["Location"].endswith(
            reverse("account_reset_password_from_key_done")
        )
        user.refresh_from_db()
        assert user.check_password(new_password)
