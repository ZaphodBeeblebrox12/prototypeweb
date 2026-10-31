"""Email-verification middleware must never block access-revoking actions."""
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.email_verification_middleware import EmailVerificationMiddleware

User = get_user_model()


class EmailVerificationDisconnectAllowlistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="unverified-disconnect-member",
            email="unverified-disconnect-member@example.com",
            password="Test-password-123!",
        )
        self.factory = RequestFactory()

    def _dispatch(self, path, method="post"):
        request = getattr(self.factory, method)(path)
        request.user = self.user
        middleware = EmailVerificationMiddleware(
            lambda _request: HttpResponse("downstream action reached", status=202)
        )
        return middleware(request)

    def test_telegram_unlink_is_allowed_without_verified_email(self):
        response = self._dispatch(reverse("bot_integration:telegram_unlink"))

        self.assertEqual(response.status_code, 202)
        self.assertContains(response, "downstream action reached", status_code=202)

    def test_discord_unlink_remains_allowed_without_verified_email(self):
        response = self._dispatch(reverse("bot_integration:discord_unlink"))

        self.assertEqual(response.status_code, 202)
        self.assertContains(response, "downstream action reached", status_code=202)

    def test_non_revocation_member_page_still_requires_email_verification(self):
        response = self._dispatch(reverse("profile"), method="get")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("account_email_verification_sent"))
