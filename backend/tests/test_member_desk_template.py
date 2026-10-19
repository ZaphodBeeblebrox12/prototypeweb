from datetime import datetime, timezone
from types import SimpleNamespace

from django.template.loader import get_template
from django.test import SimpleTestCase


class MemberDeskTemplateContractTests(SimpleTestCase):
    """Guard the real member desk against reverting to demo-only markup."""

    def test_live_member_desk_template_compiles_and_renders(self):
        template = get_template("accounts/member_desk.html")
        user = SimpleNamespace(
            username="test-member",
            first_name="Test",
            email="test@example.com",
            date_joined=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_login=None,
            telegram_username="",
            discord_username="",
            get_full_name=lambda: "Test Member",
        )
        rendered = template.render({"user": user})

        self.assertIn("TradeThesis", rendered)
        self.assertIn('id="page-overview"', rendered)
        self.assertIn('id="page-purchases"', rendered)
        self.assertIn('id="page-connections"', rendered)
        self.assertIn('id="page-billing"', rendered)
        self.assertIn('id="page-learning"', rendered)
        self.assertIn("Your learning, when you are ready.", rendered)
        self.assertIn("Nothing to resume just yet", rendered)
        self.assertIn('class="learning-empty-state"', rendered)
        self.assertIn('id="page-profile"', rendered)
        self.assertIn('id="page-help"', rendered)

    def test_my_learning_uses_access_aware_empty_state_and_return_action(self):
        source = get_template("accounts/member_desk.html").template.source
        self.assertIn("{% if member_course_cards %}", source)
        self.assertIn("Course cards and saved lesson progress will appear here once your account has access.", source)
        self.assertIn("Explore the course catalogue", source)
        self.assertIn('data-goto="overview"', source)
        self.assertIn("Saved progress · no active entitlement", source)

    def test_live_member_desk_contains_no_mock_account_or_payment_records(self):
        template = get_template("accounts/member_desk.html")
        source = template.template.source

        for placeholder in (
            "Alex Morgan",
            "alex@example.com",
            "TT-DEMO-001",
            "TT-DEMO-002",
            "Sample account",
            "sample receipt",
            "simulated",
        ):
            with self.subTest(placeholder=placeholder):
                self.assertNotIn(placeholder.casefold(), source.casefold())

    def test_connection_mutations_are_csrf_protected_post_forms(self):
        template = get_template("accounts/member_desk.html")
        source = template.template.source

        self.assertIn("method=\"post\" action=\"{% url 'bot_integration:telegram_unlink' %}\"", source)
        self.assertIn("method=\"post\" action=\"{% url 'bot_integration:discord_unlink' %}\"", source)
        self.assertGreaterEqual(source.count("{% csrf_token %}"), 3)
