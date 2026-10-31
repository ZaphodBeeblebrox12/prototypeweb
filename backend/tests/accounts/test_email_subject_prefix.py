from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.accounts.adapters import CustomAccountAdapter


class EmailSubjectBrandingTests(SimpleTestCase):
    @override_settings(ACCOUNT_EMAIL_SUBJECT_PREFIX="[example.com] ")
    def test_allauth_email_subject_never_uses_sites_database_placeholder(self):
        subject = CustomAccountAdapter().format_email_subject(
            "Reset your TradeThesis password"
        )

        self.assertEqual(
            subject,
            "[TradeThesis] Reset your TradeThesis password",
        )
        self.assertNotIn("example.com", subject)

    @override_settings(SITE_BASE_URL="https://tradethesis-academy-staging.onrender.com")
    def test_account_email_context_uses_trade_thesis_site_identity(self):
        adapter = CustomAccountAdapter()
        context = {}

        with patch("allauth.account.adapter.DefaultAccountAdapter.send_mail") as send:
            adapter.send_mail(
                "account/email/password_reset_key",
                "learner@example.test",
                context,
            )

        send.assert_called_once()
        self.assertEqual(context["current_site"].name, "TradeThesis")
        self.assertEqual(
            context["current_site"].domain,
            "tradethesis-academy-staging.onrender.com",
        )
        self.assertEqual(
            context["dashboard_url"],
            "https://tradethesis-academy-staging.onrender.com/dashboard/",
        )
