from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from allauth.account.models import EmailAddress

from apps.accounts.adapters import CustomAccountAdapter
from apps.accounts.models import User


class StagingConfirmationEmailTests(TestCase):
    @override_settings(ACADEMY_STAGING_UNVERIFIED_LOGIN_ENABLED=True)
    def test_confirmation_mail_is_not_sent_on_explicit_staging_opt_in(self):
        adapter = CustomAccountAdapter()

        # The staging branch must return before touching the email confirmation
        # object or invoking Django's configured external email backend.
        adapter.send_confirmation_mail(
            request=None,
            emailconfirmation=None,
            signup=True,
        )

    @override_settings(
        ACADEMY_STAGING_UNVERIFIED_LOGIN_ENABLED=True,
        ACCOUNT_EMAIL_VERIFICATION="none",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_signup_page_collects_first_and_last_name(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertContains(response, "First name")
        self.assertContains(response, "Last name")

    def test_staging_signup_creates_unverified_account_with_name_without_sending_email(self):
        email = "staging-real-inbox@example.com"
        response = self.client.post(
            reverse("account_signup"),
            {
                "first_name": "Asha",
                "last_name": "Mehta",
                "email": email,
                "password1": "A-strong-staging-password-852!",
                "password2": "A-strong-staging-password-852!",
            },
        )

        self.assertTrue(
            User.objects.filter(email__iexact=email).exists(),
            msg=f"Signup failed with HTTP {response.status_code}: {response.content[:1000]!r}",
        )
        user = User.objects.get(email__iexact=email)
        self.assertEqual(user.first_name, "Asha")
        self.assertEqual(user.last_name, "Mehta")
        self.assertEqual(user.full_name, "Asha Mehta")
        self.assertFalse(
            EmailAddress.objects.filter(
                user=user, email__iexact=email, verified=True
            ).exists()
        )
        self.assertEqual(mail.outbox, [])
