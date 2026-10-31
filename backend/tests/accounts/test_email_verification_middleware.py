from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from allauth.account.models import EmailAddress

from apps.accounts.email_verification_middleware import EmailVerificationMiddleware

User = get_user_model()


class EmailVerificationMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = EmailVerificationMiddleware(
            lambda request: HttpResponse("allowed")
        )

    def _user(self, username="learner", email="learner@example.com", **fields):
        return User.objects.create_user(
            username=username,
            email=email,
            password="test-password-123",
            **fields,
        )

    def _request(self, path, user):
        request = self.factory.get(path)
        request.user = user
        return self.middleware(request)

    def _assert_redirected_to_verification(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("account_email_verification_sent"),
        )

    def test_unverified_user_cannot_open_dashboard_directly(self):
        user = self._user()
        response = self._request(reverse("dashboard"), user)
        self._assert_redirected_to_verification(response)

    def test_unverified_user_cannot_bypass_gate_through_authenticated_api(self):
        user = self._user()
        response = self._request(reverse("api_user_me"), user)
        self._assert_redirected_to_verification(response)

    def test_verification_sent_page_remains_accessible(self):
        user = self._user()
        response = self._request(reverse("account_email_verification_sent"), user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"allowed")

    def test_current_email_verification_allows_protected_page(self):
        user = self._user(email="Learner@example.com")
        EmailAddress.objects.create(
            user=user,
            email="learner@example.com",
            primary=True,
            verified=True,
        )

        response = self._request(reverse("dashboard"), user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"allowed")

    def test_verified_historic_email_does_not_verify_new_current_email(self):
        user = self._user(email="new-address@example.com")
        EmailAddress.objects.create(
            user=user,
            email="old-address@example.com",
            primary=True,
            verified=True,
        )

        response = self._request(reverse("dashboard"), user)

        self._assert_redirected_to_verification(response)

    def test_telegram_user_without_email_remains_exempt(self):
        user = self._user(email=None, telegram_id=123456789)
        response = self._request(reverse("dashboard"), user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"allowed")

    def test_staff_remains_exempt(self):
        user = self._user(is_staff=True)
        response = self._request(reverse("dashboard"), user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"allowed")
