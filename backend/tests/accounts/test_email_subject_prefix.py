from django.test import SimpleTestCase, override_settings

from apps.accounts.adapters import CustomAccountAdapter


class EmailSubjectBrandingTests(SimpleTestCase):
    @override_settings(ACCOUNT_EMAIL_SUBJECT_PREFIX="[TradeThesis] ")
    def test_allauth_email_subject_uses_explicit_brand_prefix(self):
        subject = CustomAccountAdapter().format_email_subject(
            "Reset your TradeThesis password"
        )

        self.assertEqual(
            subject,
            "[TradeThesis] Reset your TradeThesis password",
        )
        self.assertNotIn("example.com", subject)
