"""Mocked tests for the Google Drive OAuth flow."""

from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .google_drive_oauth import FORCE_REFRESH_SESSION_KEY, STATE_SESSION_KEY
from .models import GoogleDriveCredential

User = get_user_model()
REDIRECT_URI = "https://tradethesis-academy-staging.onrender.com/staff/google-drive/oauth/callback/"


@override_settings(
    ACADEMY_GOOGLE_DRIVE_CLIENT_ID="client-id-test",
    ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET="client-secret-test",
    ACADEMY_GOOGLE_DRIVE_REDIRECT_URI=REDIRECT_URI,
    SECRET_KEY="drive-oauth-test-secret-key",
)
class GoogleDriveOAuthTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="drive-oauth-admin",
            password="test-password",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(self.admin)

    def test_start_uses_exact_https_redirect_and_offline_access(self):
        response = self.client.get(reverse("academy_google_drive_oauth_start"))
        self.assertEqual(response.status_code, 302)
        query = parse_qs(urlsplit(response["Location"]).query)
        self.assertEqual(query["redirect_uri"], [REDIRECT_URI])
        self.assertEqual(query["access_type"], ["offline"])
        self.assertEqual(query["scope"], ["https://www.googleapis.com/auth/drive.file"])
        self.assertTrue(query["state"][0])
        self.assertEqual(self.client.session[STATE_SESSION_KEY], query["state"][0])
        self.assertFalse(self.client.session[FORCE_REFRESH_SESSION_KEY])

    def test_start_can_request_a_forced_refresh(self):
        response = self.client.get(reverse("academy_google_drive_oauth_start"), {"force_refresh": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session[FORCE_REFRESH_SESSION_KEY])

    def test_bad_state_does_not_contact_google(self):
        session = self.client.session
        session[STATE_SESSION_KEY] = "expected"
        session.save()
        with patch("apps.academy.google_drive_oauth.requests.post") as post:
            response = self.client.get(
                reverse("academy_google_drive_oauth_callback"),
                {"state": "wrong", "code": "authorization-code"},
            )
        self.assertEqual(response.status_code, 302)
        post.assert_not_called()
        self.assertFalse(GoogleDriveCredential.objects.exists())

    def test_forced_reconnect_without_new_refresh_token_does_not_reuse_old_token(self):
        credential = GoogleDriveCredential.objects.create(pk=1)
        credential.set_refresh_token("OLD_INVALID_REFRESH_TOKEN")
        credential.save(update_fields=["encrypted_refresh_token", "updated_at"])

        session = self.client.session
        session[STATE_SESSION_KEY] = "expected"
        session[FORCE_REFRESH_SESSION_KEY] = True
        session.save()
        token = Mock(status_code=200)
        token.json.return_value = {"access_token": "ACCESS_TEST"}

        with patch("apps.academy.google_drive_oauth.requests.post", return_value=token) as post:
            response = self.client.get(
                reverse("academy_google_drive_oauth_callback"),
                {"state": "expected", "code": "authorization-code"},
            )

        self.assertEqual(response.status_code, 302)
        post.assert_called_once()
        credential.refresh_from_db()
        self.assertEqual(credential.get_refresh_token(), "OLD_INVALID_REFRESH_TOKEN")
        messages = [str(message) for message in django_messages.get_messages(response.wsgi_request)]
        self.assertTrue(any("did not issue a new refresh token" in message for message in messages))

    def test_callback_encrypts_token_and_creates_private_folders(self):
        session = self.client.session
        session[STATE_SESSION_KEY] = "expected"
        session.save()
        token = Mock(status_code=200)
        token.json.return_value = {"access_token": "ACCESS_TEST", "refresh_token": "REFRESH_TEST"}
        assets = Mock(status_code=200)
        assets.json.return_value = {"id": "asset-folder"}
        sources = Mock(status_code=200)
        sources.json.return_value = {"id": "source-folder"}
        support = Mock(status_code=200)
        support.json.return_value = {"id": "support-folder"}
        with patch(
            "apps.academy.google_drive_oauth.requests.post",
            side_effect=[token, assets, sources, support],
        ):
            response = self.client.get(
                reverse("academy_google_drive_oauth_callback"),
                {"state": "expected", "code": "authorization-code"},
            )
        self.assertEqual(response.status_code, 302)
        credential = GoogleDriveCredential.objects.get(pk=1)
        self.assertEqual(credential.get_refresh_token(), "REFRESH_TEST")
        self.assertNotIn("REFRESH_TEST", credential.encrypted_refresh_token)
        self.assertEqual(credential.asset_folder_id, "asset-folder")
        self.assertEqual(credential.source_folder_id, "source-folder")
        self.assertEqual(credential.support_attachment_folder_id, "support-folder")
        self.assertNotIn("ACCESS_TEST", response.content.decode())
        self.assertNotIn("REFRESH_TEST", response.content.decode())

    @override_settings(DEBUG=False, ACADEMY_GOOGLE_DRIVE_REDIRECT_URI="")
    def test_production_settings_never_guess_redirect_uri(self):
        response = self.client.get(reverse("academy_google_drive_oauth_start"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("accounts.google.com", response.get("Location", ""))
