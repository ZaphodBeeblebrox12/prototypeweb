from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.forms import TradeThesisSignupForm

User = get_user_model()


class AccountEmailValidationScopeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="existing-learner",
            email="existing@example.com",
            password="A-strong-test-password-123!",
        )

    def test_signup_still_rejects_an_email_already_on_the_user_model(self):
        # This deliberately omits an allauth EmailAddress row to cover legacy
        # users whose unique email exists only on the configured User model.
        form = TradeThesisSignupForm(
            data={
                "email": self.user.email,
                "password1": "Another-strong-password-456!",
                "password2": "Another-strong-password-456!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "An account with this email address already exists.",
            form.errors["email"],
        )

    def test_existing_account_email_is_valid_for_password_reset_form(self):
        from allauth.account.forms import ResetPasswordForm

        form = ResetPasswordForm(data={"email": self.user.email})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn(self.user, form.users)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    SITE_BASE_URL="https://academy.example.test",
)
class PasswordResetViewTests(TestCase):
    def setUp(self):
        mail.outbox = []
        self.user = User.objects.create_user(
            username="reset-learner",
            email="reset-learner@example.com",
            password="A-strong-test-password-123!",
        )

    def test_password_reset_get_uses_branded_trade_thesis_screen(self):
        response = self.client.get(reverse("account_reset_password"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/password_reset.html")
        self.assertContains(response, "TradeThesis / member desk")
        self.assertContains(response, "Send password reset link")

    def test_existing_user_can_request_password_reset_email(self):
        response = self.client.post(
            reverse("account_reset_password"),
            {"email": self.user.email},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("account_reset_password_done"),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your TradeThesis password", mail.outbox[0].subject)
        self.assertIn("/accounts/password/reset/key/", mail.outbox[0].body)
        self.assertIn("reset-learner@example.com", mail.outbox[0].to)

    def test_password_reset_done_screen_is_branded(self):
        response = self.client.get(reverse("account_reset_password_done"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/password_reset_done.html")
        self.assertContains(response, "Check your inbox")
